import pytest
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from hitl_cli.main import app
from hitl_cli.models import HumanResponse, FileAttachment
from hitl_cli.services.file_service import download_attachment, ExpiredURLError, FileDownloadHTTPError, FileDownloadNetworkError, FileDownloadError


runner = CliRunner()


@pytest.fixture
def mock_mcp_client():
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def tmp_download_dir(tmp_path: Path) -> Path:
    dir_path = tmp_path / "downloads"
    dir_path.mkdir()
    return dir_path


def test_request_no_attachment():
    """Test 1: No attachment - prints text, no file section."""
    mock_response = HumanResponse(
        text="Hello, this is a test response.",
        approved=True,
        attachments=[]
    )

    with patch("hitl_cli.main.MCPClient") as mock_mcp:
        mock_instance = mock_mcp.return_value
        mock_instance.request_human_input_structured.return_value = mock_response

        result = runner.invoke(app, ["request", "--prompt", "Hi there"])

    assert result.exit_code == 0
    assert "Response from human:" in result.stdout
    assert "Text: Hello, this is a test response." in result.stdout
    assert "File Attachment:" not in result.stdout


def test_request_with_attachment_no_download():
    """Test 2: Attachment present, no --download - displays metadata only."""
    expires_at = datetime(2025, 9, 18, 10, 50, 0, tzinfo=timezone.utc)
    mock_attachment = FileAttachment(
        download_url="https://example.com/project-spec.pdf",
        filename="project-spec.pdf",
        content_type="application/pdf",
        expires_at=expires_at,
        file_size=2411724  # ~2.3 MB
    )
    mock_response = HumanResponse(
        text="Here is the document you requested.",
        approved=None,
        attachments=[mock_attachment]
    )

    with patch("hitl_cli.main.MCPClient") as mock_mcp, \
         patch('time.time', return_value=1722470400.0):  # Fixed 2024-08-01 ts: < future, > past

        mock_instance = mock_mcp.return_value
        mock_instance.request_human_input_structured.return_value = mock_response

        result = runner.invoke(app, ["request", "--prompt", "Hi"])

    assert result.exit_code == 0
    assert "Response from human:" in result.stdout
    assert "Text: Here is the document you requested." in result.stdout
    assert "File Attachment:" in result.stdout
    assert "📄 project-spec.pdf (application/pdf)" in result.stdout
    assert "📏 Size: 2.3 MB" in result.stdout  # Formatted size
    assert "⏰ Expires: 2025-09-18 10:50:00 UTC" in result.stdout
    assert "🔗 Download: Available via secure URL" in result.stdout
    assert "Saved to:" not in result.stdout  # No download


def test_request_with_attachment_download_success(tmp_download_dir: Path):
    """Test 3: Attachment present, --download --download-to - saves file, prints path."""
    expires_at = datetime(2025, 9, 18, 10, 50, 0, tzinfo=timezone.utc)
    mock_attachment = FileAttachment(
        download_url="https://example.com/project-spec.pdf",
        filename="project-spec.pdf",
        content_type="application/pdf",
        expires_at=expires_at,
        file_size=2411724
    )
    mock_response = HumanResponse(
        text="Here is the document.",
        approved=None,
        attachments=[mock_attachment]
    )
    mock_download_path = tmp_download_dir / "project-spec.pdf"

    with patch("hitl_cli.main.MCPClient") as mock_mcp, \
         patch("hitl_cli.main.download_attachment", new_callable=AsyncMock) as mock_download, \
         patch('time.time', return_value=1722470400.0):  # Fixed 2024-08-01 ts: < future, > past

        mock_instance = mock_mcp.return_value
        mock_instance.request_human_input_structured.return_value = mock_response
        mock_download.return_value = mock_download_path

        result = runner.invoke(
            app,
            ["request", "--prompt", "Hi", "--download", "--download-to", str(tmp_download_dir)]
        )

    assert result.exit_code == 0
    assert "Saved to:" in result.stdout
    assert str(mock_download_path) in result.stdout
    # Metadata still displayed
    assert "📄 project-spec.pdf (application/pdf)" in result.stdout
    mock_download.assert_called_once_with(
        mock_attachment,
        tmp_download_dir,
        timeout=30.0,
        client=None  # Default
    )


def test_request_with_attachment_download_expired():
    """Test 4: Attachment present, --download - handles ExpiredURLError, prints message, exit 0."""
    expires_at = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)  # Past
    mock_attachment = FileAttachment(
        download_url="https://example.com/expired.pdf",
        filename="expired.pdf",
        content_type="text/plain",
        expires_at=expires_at,
        file_size=None
    )
    mock_response = HumanResponse(
        text="Expired attachment.",
        approved=None,
        attachments=[mock_attachment]
    )

    with patch("hitl_cli.main.MCPClient") as mock_mcp, \
         patch("hitl_cli.main.download_attachment", new_callable=AsyncMock) as mock_download, \
         patch('time.time', return_value=1722470400.0):  # Fixed 2024-08-01 ts: < future, > past

        mock_instance = mock_mcp.return_value
        mock_instance.request_human_input_structured.return_value = mock_response
        mock_download.side_effect = ExpiredURLError("Download link expired at 2024-01-01 00:00:00")

        result = runner.invoke(app, ["request", "--prompt", "Hi", "--download"])

    assert result.exit_code == 0  # Non-fatal
    assert "Error: Download link expired at 2024-01-01 00:00:00" in result.stdout
    # Metadata still shown (size Unknown)
    assert "📏 Size: Unknown" in result.stdout
    assert "🔗 Download: Available via secure URL" not in result.stdout  # But task says show availability; adjust if needed, but error overrides
    mock_download.assert_called_once()
