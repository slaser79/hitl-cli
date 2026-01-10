import os
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from typer.testing import CliRunner

from hitl_cli.main import app

runner = CliRunner()

@pytest.fixture
def mock_api_key_env():
    with patch.dict(os.environ, {"HITL_API_KEY": "test-api-key"}):
        yield

@pytest.fixture
def mock_api_client():
    with patch("hitl_cli.main.ApiClient") as mock:
        # Setup the mock instance
        instance = mock.return_value
        
        # We expect this method to be called after the fix
        instance.notify_task_completion = AsyncMock(
            return_value="User acknowledged"
        )
        instance.request_human_input = AsyncMock(
            return_value="User input"
        )
        instance.notify_human = AsyncMock(
            return_value="Notification sent"
        )
        yield mock

@pytest.fixture
def mock_mcp_client():
    with patch("hitl_cli.main.MCPClient") as mock:
        instance = mock.return_value
        instance.notify_task_completion_api_key = AsyncMock(
            return_value="MCP response"
        )
        yield mock

def test_notify_completion_uses_rest_api_with_api_key(mock_api_key_env, mock_api_client, mock_mcp_client):
    """
    Test that 'notify-completion' uses ApiClient (REST) instead of MCPClient
    when HITL_API_KEY is set.
    """
    # Act
    result = runner.invoke(
        app,
        [
            "notify-completion",
            "--summary",
            "Task finished",
        ],
    )

    # Assert
    assert result.exit_code == 0
    
    # Verify ApiClient was used (Desired Behavior)
    mock_api_client.return_value.notify_task_completion.assert_called_once_with(
        summary="Task finished"
    )
    
    # Verify MCPClient was NOT used
    mock_mcp_client.return_value.notify_task_completion_api_key.assert_not_called()
