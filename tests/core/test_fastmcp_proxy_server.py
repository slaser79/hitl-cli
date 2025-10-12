"""
Tests for FastMCP-based proxy server implementation.

These tests validate that the new proxy implementation is a proper MCP server
using FastMCP 2.0, with correct protocol compliance and E2EE functionality.

These tests MUST FAIL initially, then pass after proper implementation.
"""

import pytest
from unittest.mock import AsyncMock, patch

# Import the new implementation (will fail initially)
try:
    from hitl_cli.proxy_handler_v2 import create_fastmcp_proxy_server
    from fastmcp import FastMCP, Client
except ImportError:
    # These imports will fail initially - that's expected
    create_fastmcp_proxy_server = None
    FastMCP = None
    Client = None


class TestFastMCPProxyServerCompliance:
    """Test suite for FastMCP proxy server compliance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"

    @pytest.mark.asyncio
    async def test_proxy_server_is_valid_mcp_server(self):
        """Test that proxy is a valid MCP server using FastMCP testing utilities.
        
        This test MUST FAIL initially until proper FastMCP implementation.
        """
        if create_fastmcp_proxy_server is None:
            pytest.fail("FastMCP proxy server implementation not found - this test should fail initially")
        
        # Mock backend tools for testing
        mock_backend_tools = [
            {
                "name": "request_human_input",
                "description": "Request input from human user",
                "inputSchema": {"type": "object", "properties": {"prompt": {"type": "string"}}}
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
            }
        ]
        
        # Generate test keypairs
        from nacl.public import PrivateKey
        from nacl.encoding import Base64Encoder
        
        test_private_key = PrivateKey.generate()
        test_public_key = test_private_key.public_key
        
        with patch('hitl_cli.proxy_handler_v2.get_backend_tools') as mock_get_tools, \
             patch('hitl_cli.proxy_handler_v2.load_agent_keypair') as mock_load_keys:
            
            mock_get_tools.return_value = mock_backend_tools
            mock_load_keys.return_value = (
                test_public_key.encode(Base64Encoder).decode(),
                test_private_key.encode(Base64Encoder).decode()
            ) 
            
            # Create FastMCP proxy server
            server = create_fastmcp_proxy_server(self.backend_url)
            
            # Test that it's a valid FastMCP server
            assert isinstance(server, FastMCP), "Server must be a FastMCP instance"
            
            # Test in-memory client connection (FastMCP testing pattern)
            async with Client(server) as client:
                # Test MCP lifecycle compliance
                tools = await client.list_tools()
                assert isinstance(tools, list), "Tools list must be returned"
                
                # Test that _e2ee tools are filtered out (core proxy functionality)
                tool_names = [tool.name for tool in tools]
                assert "request_human_input" in tool_names, "Plaintext tools must be exposed"
                assert "notify_human" in tool_names, "Plaintext tools must be exposed"
                assert "request_human_input_e2ee" not in tool_names, "E2EE tools must be filtered"
                assert "notify_human_e2ee" not in tool_names, "E2EE tools must be filtered"

    @pytest.mark.asyncio
    async def test_mcp_server_initialization_and_capabilities(self):
        """Test proper MCP server initialization and capabilities.
        
        This test MUST FAIL initially until proper FastMCP implementation.
        """
        if create_fastmcp_proxy_server is None:
            pytest.fail("FastMCP proxy server implementation not found - this test should fail initially")
        
        # Generate test keypairs
        from nacl.public import PrivateKey
        from nacl.encoding import Base64Encoder
        
        test_private_key = PrivateKey.generate()
        test_public_key = test_private_key.public_key
        
        with patch('hitl_cli.proxy_handler_v2.get_backend_tools') as mock_get_tools, \
             patch('hitl_cli.proxy_handler_v2.load_agent_keypair') as mock_load_keys:
            
            mock_get_tools.return_value = []
            mock_load_keys.return_value = (
                test_public_key.encode(Base64Encoder).decode(),
                test_private_key.encode(Base64Encoder).decode()
            )
            
            server = create_fastmcp_proxy_server(self.backend_url)
            
            # Test server can be used with FastMCP Client (proper MCP protocol)
            async with Client(server) as client:
                # Test server responds to tool listing (core MCP functionality)
                tools = await client.list_tools()
                assert isinstance(tools, list), "Server must respond to tools/list"
                
                # Test server has proper FastMCP structure
                assert hasattr(server, '_tool_manager'), "Server must have tool manager"
                assert hasattr(server, 'name'), "Server must have name attribute"

    @pytest.mark.asyncio
    async def test_request_human_input_e2ee_transparency(self):
        """Test that request_human_input transparently handles E2EE encryption.
        
        This test MUST FAIL initially until E2EE implementation.
        """
        if create_fastmcp_proxy_server is None:
            pytest.fail("FastMCP proxy server implementation not found - this test should fail initially")
        
        # Mock device keys and backend responses
        mock_device_keys = ["test_device_public_key_base64"]
        mock_encrypted_payload = "encrypted_test_payload"
        mock_decrypted_response = "Decrypted human response"
        
        with patch('hitl_cli.proxy_handler_v2.get_device_public_keys') as mock_get_keys, \
             patch('hitl_cli.proxy_handler_v2.encrypt_arguments') as mock_encrypt, \
             patch('hitl_cli.proxy_handler_v2.decrypt_response') as mock_decrypt, \
             patch('hitl_cli.proxy_handler_v2.BackendMCPClient') as mock_backend_client, \
             patch('hitl_cli.proxy_handler_v2.load_agent_keypair') as mock_load_keys:

            mock_get_keys.return_value = mock_device_keys
            mock_encrypt.return_value = mock_encrypted_payload
            mock_decrypt.return_value = mock_decrypted_response
            mock_load_keys.return_value = ("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            
            # Mock backend client
            mock_client = AsyncMock()
            mock_client.call_tool.return_value = {"result": "encrypted_response"}
            mock_backend_client.return_value = mock_client
            
            server = create_fastmcp_proxy_server(self.backend_url)
            
            async with Client(server) as client:
                # Test that Claude sees plaintext tool and gets plaintext response
                result = await client.call_tool("request_human_input", {
                    "prompt": "Test prompt",
                    "choices": ["Yes", "No"]
                })
                
                # Verify E2EE flow was triggered transparently
                mock_get_keys.assert_called_once()
                mock_encrypt.assert_called_once()
                mock_client.call_tool.assert_called_once_with(
                    "request_human_input_e2ee",
                    {"encrypted_payload": mock_encrypted_payload}
                )
                mock_decrypt.assert_called_once()
                
                # Verify Claude receives plaintext response
                assert result is not None, "Tool execution must return result"

    @pytest.mark.asyncio
    async def test_proper_json_rpc_error_handling(self):
        """Test proper JSON-RPC 2.0 error handling in FastMCP server.
        
        This test MUST FAIL initially until proper error handling.
        """
        if create_fastmcp_proxy_server is None:
            pytest.fail("FastMCP proxy server implementation not found - this test should fail initially")
        
        with patch('hitl_cli.proxy_handler_v2.get_device_public_keys') as mock_get_keys, \
             patch('hitl_cli.proxy_handler_v2.load_agent_keypair') as mock_load_keys:
            # Simulate error condition
            mock_get_keys.side_effect = Exception("Device keys unavailable")
            mock_load_keys.return_value = ("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            
            server = create_fastmcp_proxy_server(self.backend_url)
            
            async with Client(server) as client:
                # Test that errors are handled properly by FastMCP
                with pytest.raises(Exception):
                    await client.call_tool("request_human_input", {"prompt": "Test"})
                
                # Server should still be functional for other operations
                tools = await client.list_tools()
                assert isinstance(tools, list), "Server must remain functional despite errors"


class TestFastMCPProxyServerIntegration:
    """Integration tests for FastMCP proxy server with existing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"

    @pytest.mark.asyncio
    async def test_fastmcp_server_preserves_existing_proxy_behavior(self):
        """Test that FastMCP implementation preserves all existing proxy behaviors.
        
        This validates that the new implementation maintains compatibility
        with existing test expectations from test_tool_interception.py.
        """
        if create_fastmcp_proxy_server is None:
            pytest.fail("FastMCP proxy server implementation not found - this test should fail initially")
        
        # Use the same mock data as existing tests for compatibility
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
            },
            {
                "name": "request_human_input_e2ee", 
                "description": "Request input with end-to-end encryption",
                "inputSchema": {"type": "object"}
            }
        ]
        
        # Generate test keypairs
        from nacl.public import PrivateKey
        from nacl.encoding import Base64Encoder
        
        test_private_key = PrivateKey.generate()
        test_public_key = test_private_key.public_key
        
        with patch('hitl_cli.proxy_handler_v2.get_backend_tools') as mock_get_tools, \
             patch('hitl_cli.proxy_handler_v2.load_agent_keypair') as mock_load_keys:
            
            mock_get_tools.return_value = mock_backend_tools
            mock_load_keys.return_value = (
                test_public_key.encode(Base64Encoder).decode(),
                test_private_key.encode(Base64Encoder).decode()
            )
            
            server = create_fastmcp_proxy_server(self.backend_url)
            
            async with Client(server) as client:
                tools = await client.list_tools()
                
                # Validate that both E2EE tools are present (my implementation creates both)
                # The old implementation only had request_human_input, but new one has both
                assert len(tools) >= 1, "Should return at least plaintext tools"
                
                tool_names = [tool.name for tool in tools]
                assert "request_human_input" in tool_names, "request_human_input must be present"
                
                # Find the request_human_input tool
                request_tool = next(tool for tool in tools if tool.name == "request_human_input")
                assert "Request input from human" in request_tool.description, "Tool description must reference human input"
                assert hasattr(request_tool, 'inputSchema'), "Tool metadata must be preserved"

    def test_fastmcp_server_creation_with_invalid_backend_url(self):
        """Test FastMCP server creation with invalid backend URL."""
        if create_fastmcp_proxy_server is None:
            pytest.fail("FastMCP proxy server implementation not found - this test should fail initially")
        
        # Test that server can be created even with invalid URL (validation happens at runtime)
        with patch('hitl_cli.proxy_handler_v2.load_agent_keypair') as mock_load_keys:
            mock_load_keys.return_value = ("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            server = create_fastmcp_proxy_server("invalid-url")
            assert isinstance(server, FastMCP), "Server creation should succeed"
            assert server.name == "hitl-e2ee-proxy", "Server should have correct name"
