import pytest
from datetime import datetime, timedelta
from hitl_cli.models import FileAttachment, HumanResponse

def test_file_attachment_model_parses():
    data = {
        "download_url": "https://example.com/file.pdf?token=abc",
        "filename": "file.pdf",
        "content_type": "application/pdf",
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
        "file_size": 123456,
    }
    fa = FileAttachment(**data)
    assert fa.filename == "file.pdf"
    assert fa.content_type == "application/pdf"
    assert isinstance(fa.expires_at, datetime)

def test_human_response_normalizes_single_attachment_dict():
    att = {
        "download_url": "https://example.com/a.png",
        "filename": "a.png",
        "content_type": "image/png",
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
    }
    hr = HumanResponse(text="ok", attachments=att)
    assert len(hr.attachments) == 1
    assert hr.attachments[0].filename == "a.png"

def test_human_response_handles_no_attachments():
    hr = HumanResponse(text="no files")
    assert hr.attachments == []
