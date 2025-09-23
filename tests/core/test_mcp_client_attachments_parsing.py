import types
import json
from datetime import datetime, timedelta

from hitl_cli.mcp_client import MCPClient
from hitl_cli.models import HumanResponse

def _dummy_content_text(txt):
    o = types.SimpleNamespace()
    o.text = txt
    return o

def test_parse_result_with_text_and_json_attachment():
    client = MCPClient()
    expires = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
    attachment_obj = {
        "file_attachment": {
            "download_url": "https://example.com/doc.pdf",
            "filename": "doc.pdf",
            "content_type": "application/pdf",
            "expires_at": expires,
            "file_size": 2048,
        },
        "approved": True,
        "text": "Here is the document you requested."
    }
    # Simulate FastMCP-like result with list content
    result = types.SimpleNamespace()
    result.content = [
        _dummy_content_text("Acknowledged."),
        {"type": "json", "json": attachment_obj},
    ]
    hr: HumanResponse = client.parse_result_to_human_response(result)
    assert "Acknowledged." in hr.text or "document" in hr.text
    assert hr.approved is True
    assert len(hr.attachments) == 1
    fa = hr.attachments[0]
    assert fa.filename == "doc.pdf"
    assert fa.content_type == "application/pdf"

def test_parse_result_from_string_json():
    client = MCPClient()
    expires = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
    payload = {
        "text": "Please review.",
        "attachments": [
            {
                "download_url": "https://example.com/x.txt",
                "filename": "x.txt",
                "content_type": "text/plain",
                "expires_at": expires,
            }
        ]
    }
    result = json.dumps(payload)
    hr = client.parse_result_to_human_response(result)
    assert "Please review." in hr.text
    assert len(hr.attachments) == 1
    assert hr.attachments[0].filename == "x.txt"
