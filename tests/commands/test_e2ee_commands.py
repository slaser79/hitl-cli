import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from hitl_cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_mcp_client():
    with patch("hitl_cli.main.MCPClient") as mock:
        mock.return_value.request_human_input_e2ee = AsyncMock(
            return_value="decrypted_response"
        )
        mock.return_value.notify_human_e2ee = AsyncMock(
            return_value="Notification sent"
        )
        mock.return_value.notify_task_completion_e2ee = AsyncMock(
            return_value="decrypted_response"
        )
        yield mock


def test_request_e2ee(mock_mcp_client):
    """Test the 'request' command with the --e2ee flag."""
    # Act
    result = runner.invoke(
        app,
        [
            "request",
            "--prompt",
            "Test prompt",
            "--e2ee",
        ],
    )

    # Assert
    assert result.exit_code == 0
    assert "decrypted_response" in result.stdout
    mock_mcp_client.return_value.request_human_input_e2ee.assert_called_once_with(
        prompt="Test prompt",
        choices=None,
        placeholder_text=None,
    )


def test_notify_e2ee(mock_mcp_client):
    """Test the 'notify' command with the --e2ee flag."""
    # Act
    result = runner.invoke(
        app,
        [
            "notify",
            "--message",
            "Test message",
            "--e2ee",
        ],
    )

    # Assert
    assert result.exit_code == 0
    assert "Notification sent" in result.stdout
    mock_mcp_client.return_value.notify_human_e2ee.assert_called_once_with(
        message="Test message"
    )


def test_notify_completion_e2ee(mock_mcp_client):
    """Test the 'notify-completion' command with the --e2ee flag."""
    # Act
    result = runner.invoke(
        app,
        [
            "notify-completion",
            "--summary",
            "Test summary",
            "--e2ee",
        ],
    )

    # Assert
    assert result.exit_code == 0
    assert "decrypted_response" in result.stdout
    mock_mcp_client.return_value.notify_task_completion_e2ee.assert_called_once_with(
        summary="Test summary"
    )