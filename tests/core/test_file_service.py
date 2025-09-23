import logging
import warnings
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
import pytest
from hitl_cli.models import FileAttachment
from hitl_cli.services.file_service import (
    FileDownloadError,
    ExpiredURLError,
    FileDownloadHTTPError,
    FileDownloadNetworkError,
    FileContentTypeMismatchWarning,
    download_attachment,
    download_url,
    is_expired,
    safe_join,
)


@pytest.fixture
def mock_pdf_content():
    return b"%PDF-1.4\nSample PDF content for testing."


@pytest.fixture
def sample_attachment(mock_pdf_content):
    now = datetime.now(timezone.utc)
    return FileAttachment(
        download_url="https://example.com/file.pdf",
        filename="test.pdf",
        content_type="application/pdf",
        expires_at=now + timedelta(hours=1),
        file_size=len(mock_pdf_content),
    )


@pytest.fixture
def expired_attachment(mock_pdf_content):
    now = datetime.now(timezone.utc)
    return FileAttachment(
        download_url="https://example.com/file.pdf",
        filename="test.pdf",
        content_type="application/pdf",
        expires_at=now - timedelta(hours=1),
        file_size=len(mock_pdf_content),
    )


@pytest.fixture
def mock_transport_success(mock_pdf_content):
    def handle_request(request):
        if request.method == "GET":
            headers = {
                "content-type": "application/pdf",
                "content-length": str(len(mock_pdf_content)),
            }
            return httpx.Response(200, headers=headers, content=mock_pdf_content)
        return httpx.Response(404)

    return httpx.MockTransport(handle_request)


@pytest.fixture
def mock_transport_http_error():
    def handle_request(request):
        if request.method == "GET":
            return httpx.Response(403, content=b"Access denied")
        return httpx.Response(404)

    return httpx.MockTransport(handle_request)


@pytest.fixture
def mock_transport_network_error():
    def handle_request(request):
        raise httpx.ConnectError("Connection failed")

    return httpx.MockTransport(handle_request)


@pytest.fixture
def mock_transport_mismatch(mock_pdf_content):
    def handle_request(request):
        if request.method == "GET":
            headers = {
                "content-type": "image/jpeg",  # Mismatch
                "content-length": str(len(mock_pdf_content)),
            }
            return httpx.Response(200, headers=headers, content=mock_pdf_content)
        return httpx.Response(404)

    return httpx.MockTransport(handle_request)


class TestUtils:
    def test_is_expired_future(self):
        future = datetime.now(timezone.utc) + timedelta(days=1)
        assert not is_expired(future)

    def test_is_expired_past(self):
        past = datetime.now(timezone.utc) - timedelta(days=1)
        assert is_expired(past)

    def test_is_expired_now(self):
        now = datetime.now(timezone.utc)
        assert not is_expired(now)  # Not expired yet

    def test_safe_join_sanitization(self, tmp_path):
        dest_dir = tmp_path / "downloads"
        malicious = "../../../etc/passwd"
        safe_path = safe_join(dest_dir, malicious)
        assert safe_path.name == "unnamed_file"  # Sanitized
        assert safe_path.parent == dest_dir

        normal = "test file.pdf"
        safe_path = safe_join(dest_dir, normal)
        assert safe_path.name == "test file.pdf"


class TestDownloadFunctions:
    @pytest.mark.asyncio
    async def test_download_url_success(self, tmp_path, mock_pdf_content, mock_transport_success):
        dest_path = tmp_path / "test.pdf"
        client = httpx.AsyncClient(transport=mock_transport_success)

        path = await download_url(
            "https://example.com/file.pdf",
            dest_path,
            expected_content_type="application/pdf",
            client=client,
        )

        assert path.exists()
        assert path.read_bytes() == mock_pdf_content
        assert path.stat().st_size == len(mock_pdf_content)
        await client.aclose()

    @pytest.mark.asyncio
    async def test_download_attachment_success(self, tmp_path, sample_attachment, mock_pdf_content, mock_transport_success):
        dest_dir = tmp_path / "attachments"
        client = httpx.AsyncClient(transport=mock_transport_success)

        path = await download_attachment(
            sample_attachment,
            dest_dir,
            client=client,
        )

        assert path.exists()
        assert path.read_bytes() == mock_pdf_content
        assert path.stat().st_size == sample_attachment.file_size
        assert "test.pdf" in path.name  # Sanitized filename
        await client.aclose()

    @pytest.mark.asyncio
    async def test_download_attachment_expired(self, expired_attachment, tmp_path):
        with pytest.raises(ExpiredURLError):
            await download_attachment(expired_attachment, tmp_path)

    @pytest.mark.asyncio
    async def test_download_url_http_error(self, tmp_path, mock_transport_http_error):
        dest_path = tmp_path / "test.pdf"
        client = httpx.AsyncClient(transport=mock_transport_http_error)

        with pytest.raises(FileDownloadHTTPError) as exc_info:
            await download_url("https://example.com/file.pdf", dest_path, client=client)

        error = exc_info.value
        assert error.status_code == 403
        assert "Access denied" in str(error)
        await client.aclose()

    @pytest.mark.asyncio
    async def test_download_url_network_error(self, tmp_path, mock_transport_network_error):
        dest_path = tmp_path / "test.pdf"
        client = httpx.AsyncClient(transport=mock_transport_network_error)

        with pytest.raises(FileDownloadNetworkError):
            await download_url("https://example.com/file.pdf", dest_path, client=client)

        await client.aclose()

    @pytest.mark.asyncio
    async def test_download_url_content_type_mismatch(self, tmp_path, mock_pdf_content, mock_transport_mismatch):
        dest_path = tmp_path / "test.pdf"
        client = httpx.AsyncClient(transport=mock_transport_mismatch)

        with pytest.warns(FileContentTypeMismatchWarning):
            path = await download_url(
                "https://example.com/file.pdf",
                dest_path,
                expected_content_type="application/pdf",
                client=client,
            )

        assert path.exists()
        assert path.read_bytes() == mock_pdf_content
        await client.aclose()

    @pytest.mark.asyncio
    async def test_download_attachment_size_mismatch_warning(self, tmp_path, sample_attachment, mock_pdf_content, mock_transport_success):
        # Modify size to mismatch
        mismatch_attachment = sample_attachment.copy(update={"file_size": len(mock_pdf_content) + 1})
        dest_dir = tmp_path / "attachments"
        client = httpx.AsyncClient(transport=mock_transport_success)

        with pytest.warns(FileContentTypeMismatchWarning):
            await download_attachment(mismatch_attachment, dest_dir, client=client)

        # File still saved correctly
        files = list(dest_dir.iterdir())
        assert len(files) == 1
        assert files[0].read_bytes() == mock_pdf_content
        await client.aclose()
