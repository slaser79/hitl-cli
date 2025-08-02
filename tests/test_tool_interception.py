"""
Tests for MCP tool interception functionality.

Tests that the proxy intercepts tools/list requests and only advertises 
plaintext tools to Claude, hiding the encrypted variants.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hitl_cli.proxy_handler import ProxyHandler


class TestToolListInterception:
    """Test suite for tools/list request interception."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"
        
    @patch('hitl_cli.crypto.load_agent_keypair')
    async def test_tools_list_request_intercepted(self, mock_load_keys):
        """Test that tools/list requests are intercepted by proxy."""
        mock_load_keys.return_value = ("public_key", "private_key")
        
        handler = ProxyHandler(self.backend_url)
        
        # Mock tools/list request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        # Should handle tools/list internally, not forward to backend
        with patch.object(handler, 'handle_tools_list') as mock_handle:
            mock_handle.return_value = {"jsonrpc": "2.0", "id": 1, "result": {"tools": []}}
            
            response = await handler.handle_mcp_request(json.dumps(request))
            
            mock_handle.assert_called_once()
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1

    @patch('hitl_cli.crypto.load_agent_keypair')
    async def test_non_tools_list_forwarded_to_backend(self, mock_load_keys):
        """Test that non-tools/list requests are forwarded to backend."""
        mock_load_keys.return_value = ("public_key", "private_key")
        
        handler = ProxyHandler(self.backend_url)
        
        # Mock non-tools/list request
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "some/other/method",
            "params": {"arg": "value"}
        }
        
        # Should forward to backend
        with patch.object(handler, 'forward_to_backend') as mock_forward:
            mock_forward.return_value = {"jsonrpc": "2.0", "id": 2, "result": {"success": True}}
            
            response = await handler.handle_mcp_request(json.dumps(request))
            
            mock_forward.assert_called_once_with(request)

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler.get_backend_tools')
    async def test_handle_tools_list_filters_encrypted_tools(self, mock_get_tools, mock_load_keys):
        """Test that handle_tools_list filters out encrypted tool variants."""
        mock_load_keys.return_value = ("public_key", "private_key")
        
        # Mock backend tools including both plaintext and encrypted variants
        mock_backend_tools = [
            {
                "name": "request_human_input",
                "description": "Request input from human user",
                "inputSchema": {"type": "object"}
            },
            {
                "name": "request_human_input_e2ee", 
                "description": "Request input with end-to-end encryption",
                "inputSchema": {"type": "object"}
            },
            {
                "name": "notify_human",
                "description": "Send notification to human",
                "inputSchema": {"type": "object"}
            },
            {
                "name": "notify_human_e2ee",
                "description": "Send notification with encryption",
                "inputSchema": {"type": "object"}
            },
            {
                "name": "onboard_agent",
                "description": "Onboard a new agent",
                "inputSchema": {"type": "object"}
            }
        ]
        
        mock_get_tools.return_value = mock_backend_tools
        
        handler = ProxyHandler(self.backend_url)
        
        # Handle tools/list request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = await handler.handle_tools_list(request)
        
        # Should only return plaintext tools
        tools = response["result"]["tools"]
        tool_names = [tool["name"] for tool in tools]
        
        assert "request_human_input" in tool_names
        assert "notify_human" in tool_names
        assert "onboard_agent" in tool_names
        assert "request_human_input_e2ee" not in tool_names
        assert "notify_human_e2ee" not in tool_names

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler.get_backend_tools')
    async def test_handle_tools_list_preserves_tool_metadata(self, mock_get_tools, mock_load_keys):
        """Test that handle_tools_list preserves tool metadata for plaintext tools."""
        mock_load_keys.return_value = ("public_key", "private_key")
        
        mock_backend_tools = [
            {
                "name": "request_human_input",
                "description": "Request input from human user",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "choices": {"type": "array"}
                    },
                    "required": ["prompt"]
                }
            }
        ]
        
        mock_get_tools.return_value = mock_backend_tools
        
        handler = ProxyHandler(self.backend_url)
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = await handler.handle_tools_list(request)
        
        # Should preserve all metadata
        tools = response["result"]["tools"]
        assert len(tools) == 1
        
        tool = tools[0]
        assert tool["name"] == "request_human_input"
        assert tool["description"] == "Request input from human user"
        assert tool["inputSchema"]["type"] == "object"
        assert "prompt" in tool["inputSchema"]["properties"]
        assert "choices" in tool["inputSchema"]["properties"]

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler.get_backend_tools')
    async def test_handle_tools_list_empty_backend_tools(self, mock_get_tools, mock_load_keys):
        """Test handle_tools_list with empty backend tools."""
        mock_load_keys.return_value = ("public_key", "private_key")
        mock_get_tools.return_value = []
        
        handler = ProxyHandler(self.backend_url)
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = await handler.handle_tools_list(request)
        
        assert response["result"]["tools"] == []

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler.get_backend_tools')
    async def test_handle_tools_list_backend_error(self, mock_get_tools, mock_load_keys):
        """Test handle_tools_list when backend tools retrieval fails."""
        mock_load_keys.return_value = ("public_key", "private_key")
        mock_get_tools.side_effect = Exception("Backend error")
        
        handler = ProxyHandler(self.backend_url)
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = await handler.handle_tools_list(request)
        
        # Should return error response
        assert "error" in response
        assert response["error"]["code"] == -32603  # Internal error


class TestBackendToolsRetrieval:
    """Test suite for backend tools retrieval."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('httpx.AsyncClient')
    async def test_get_backend_tools_success(self, mock_client, mock_load_keys):
        """Test successful retrieval of tools from backend."""
        mock_load_keys.return_value = ("public_key", "private_key")
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "tools": [
                    {"name": "test_tool", "description": "Test tool"}
                ]
            }
        }
        
        mock_client_instance = mock_client.return_value.__aenter__.return_value
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        
        handler = ProxyHandler(self.backend_url)
        
        tools = await handler.get_backend_tools()
        
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('httpx.AsyncClient')
    async def test_get_backend_tools_http_error(self, mock_client, mock_load_keys):
        """Test get_backend_tools with HTTP error."""
        mock_load_keys.return_value = ("public_key", "private_key")
        
        # Mock HTTP error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_client_instance = mock_client.return_value.__aenter__.return_value
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        
        handler = ProxyHandler(self.backend_url)
        
        with pytest.raises(Exception, match="Failed to get tools from backend"):
            await handler.get_backend_tools()

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('httpx.AsyncClient')
    async def test_get_backend_tools_network_error(self, mock_client, mock_load_keys):
        """Test get_backend_tools with network error."""
        mock_load_keys.return_value = ("public_key", "private_key")
        
        # Mock network error
        mock_client_instance = mock_client.return_value.__aenter__.return_value
        mock_client_instance.post = AsyncMock(side_effect=Exception("Network error"))
        
        handler = ProxyHandler(self.backend_url)
        
        with pytest.raises(Exception, match="Failed to get tools from backend"):
            await handler.get_backend_tools()

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('hitl_cli.auth.get_current_oauth_token')
    @patch('httpx.AsyncClient')
    async def test_get_backend_tools_with_oauth_auth(self, mock_client, mock_get_token, mock_load_keys):
        """Test get_backend_tools uses OAuth authentication when available."""
        mock_load_keys.return_value = ("public_key", "private_key")
        mock_get_token.return_value = "oauth_token"
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": {"tools": []}}
        
        mock_client_instance = mock_client.return_value.__aenter__.return_value
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        
        handler = ProxyHandler(self.backend_url)
        
        with patch('hitl_cli.auth.is_using_oauth', return_value=True):
            await handler.get_backend_tools()
        
        # Should use Bearer token in Authorization header
        call_args = mock_client_instance.post.call_args
        headers = call_args[1]['headers']
        assert headers['Authorization'] == 'Bearer oauth_token'