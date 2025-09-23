from __future__ import annotations

import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

import httpx
from hitl_cli.models import FileAttachment


class FileDownloadError(Exception):
    """Base exception for file download errors."""


class ExpiredURLError(FileDownloadError):
    """Raised when the attachment URL has expired."""


class FileDownloadHTTPError(FileDownloadError):
    """Raised for HTTP errors during download (non-2xx status)."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")


class FileDownloadNetworkError(FileDownloadError):
    """Raised for network-related errors (connect, timeout, etc.)."""


class FileContentTypeMismatchWarning(Warning):
    """Warning for content-type mismatch (non-blocking)."""


def is_expired(expires_at: datetime) -> bool:
    """Check if the expiration datetime is in the past (UTC)."""
    return expires_at < datetime.now(timezone.utc)


def safe_join(dest_dir: Path, filename: str) -> Path:
    """Safely join filename to dest_dir, sanitizing to prevent path traversal."""
    # Basic sanitization: keep alphanumeric, spaces, -, _, .
    safe_filename = "".join(c for c in filename if c.isalnum() or c in (" ", "-", "_", ".")).rstrip()
    if not safe_filename:
        safe_filename = "unnamed_file"
    return dest_dir / safe_filename


async def download_attachment(
    attachment: FileAttachment,
    dest_dir: Union[str, Path],
    timeout: float = 30.0,
    client: Optional[httpx.AsyncClient] = None,
) -> Path:
    """Download a FileAttachment to the destination directory."""
    if is_expired(attachment.expires_at):
        raise ExpiredURLError(f"Attachment expired at {attachment.expires_at}")

    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = safe_join(dest_dir, attachment.filename)

    downloaded_path = await download_url(
        str(attachment.download_url),
        dest_path,
        attachment.content_type,
        timeout,
        client,
    )

    if attachment.file_size:
        actual_size = downloaded_path.stat().st_size
        if actual_size != attachment.file_size:
            warnings.warn(
                f"Downloaded size {actual_size} != expected {attachment.file_size}",
                FileContentTypeMismatchWarning,  # Reuse warning class for size mismatch too
            )

    return downloaded_path


async def download_url(
    url: str,
    dest_path: Union[str, Path],
    expected_content_type: Optional[str] = None,
    timeout: float = 30.0,
    client: Optional[httpx.AsyncClient] = None,
) -> Path:
    """Download from URL to dest_path, with optional content-type check."""
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    own_client = client is None
    if own_client:
        client = httpx.AsyncClient()

    try:
        async with client.stream("GET", url, timeout=httpx.Timeout(timeout)) as response:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                snippet = (await exc.response.aread())[:100].decode("utf-8", errors="ignore")
                raise FileDownloadHTTPError(exc.response.status_code, snippet) from exc

            content_type = response.headers.get("content-type", "")
            if expected_content_type and expected_content_type not in content_type:
                warnings.warn(
                    f"Expected content-type '{expected_content_type}', got '{content_type}'",
                    FileContentTypeMismatchWarning,
                )

            bytes_written = 0
            with open(dest_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
                    bytes_written += len(chunk)

        return dest_path

    except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout) as exc:
        raise FileDownloadNetworkError(f"Network error: {exc}") from exc
    except httpx.RequestError as exc:
        raise FileDownloadNetworkError(f"Request error: {exc}") from exc
    finally:
        if own_client:
            await client.aclose()
