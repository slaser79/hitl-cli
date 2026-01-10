import os
from unittest.mock import AsyncMock, patch

import pytest
from hitl_cli.mcp_client import MCPClient
from hitl_cli.sdk import HITL


@pytest.mark.asyncio
@patch.dict(os.environ, {"HITL_API_KEY": "test_api_key"})
@patch("hitl_cli.api_client.ApiClient")
@patch("hitl_cli.sdk.MCPClient")
async def test_sdk_uses_rest_with_api_key(mock_mcp_class, mock_api_client_class):
    """Verify that SDK uses ApiClient (REST) and NOT MCPClient when HITL_API_KEY is set."""
    mock_api_client = mock_api_client_class.return_value
    mock_api_client.request_human_input = AsyncMock(return_value="REST response")

    hitl = HITL()
    # We need to manually inject the mocked MCP client because HITL.__init__ creates one
    hitl._mcp_client = mock_mcp_class.return_value

    result = await hitl.request_input("Test prompt")

    assert result == "REST response"
    # Verify ApiClient was called
    mock_api_client.request_human_input.assert_called_once()
    # Verify MCPClient methods were NOT called for the actual request
    assert mock_mcp_class.return_value.request_human_input_api_key.call_count == 0
    assert mock_mcp_class.return_value.call_tool.call_count == 0

@pytest.mark.asyncio
@patch.dict(os.environ, {"HITL_API_KEY": "test_api_key"})
@patch("hitl_cli.mcp_client.ApiClient")
async def test_mcp_client_uses_rest_with_api_key(mock_api_client_class):
    """Verify that MCPClient itself redirects to ApiClient when API key is set."""
    mock_api_client = mock_api_client_class.return_value
    mock_api_client.request_human_input = AsyncMock(return_value="REST response via MCPClient")

    client = MCPClient()
    result = await client.request_human_input_api_key("Test prompt")

    assert result == "REST response via MCPClient"
    mock_api_client.request_human_input.assert_called_once()
