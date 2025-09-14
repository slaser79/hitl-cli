import os
import unittest.mock
from unittest.mock import patch, MagicMock, AsyncMock

from hitl_cli.api_client import ApiClient
from hitl_cli.mcp_client import MCPClient


class TestApiKeyAuth(unittest.TestCase):
    """Unit tests for API key authentication in ApiClient and MCPClient."""

    @patch.dict(os.environ, {"HITL_API_KEY": "test_api_key"})
    def test_api_client_get_headers_with_api_key(self):
        """Test that ApiClient._get_headers returns X-API-Key when HITL_API_KEY is set."""
        client = ApiClient()
        headers = client._get_headers()
        self.assertEqual(headers, {"X-API-Key": "test_api_key", "Content-Type": "application/json"})
        self.assertNotIn("Authorization", headers)

    @patch.dict(os.environ, {"HITL_API_KEY": "test_api_key"})
    @patch("hitl_cli.mcp_client.StreamableHttpTransport")
    @patch("hitl_cli.mcp_client.Client")
    def test_mcp_client_call_tool_with_api_key(self, mock_client, mock_transport):
        """Test that MCPClient.call_tool uses StreamableHttpTransport with X-API-Key when HITL_API_KEY is set."""
        mock_client_instance = MagicMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        mock_client.return_value.__aexit__.return_value = None
        mock_client_instance.call_tool = AsyncMock(return_value=MagicMock(content=[MagicMock(text="mock response")]))

        client = MCPClient()
        # Mock the async call to avoid real MCP interactions
        import asyncio
        result = asyncio.run(client.call_tool("test_tool", {"arg": "value"}))

        # Verify that StreamableHttpTransport was called with correct URL and headers
        mock_transport.assert_called_once_with(
            f"{client.base_url}/mcp-server/mcp/",
            headers={"X-API-Key": "test_api_key"}
        )

        # Verify that fastmcp.Client was called with the mocked transport
        mock_client.assert_called_once_with(transport=mock_transport.return_value, timeout=client.timeout)

        self.assertEqual(result, "mock response")
