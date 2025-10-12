"""
Tests for proxy handler core logic

This file consolidates tests for:
- Tool list interception
- Request encryption
- Response decryption

These tests validate the proxy's core E2EE functionality.
"""

import json
from unittest.mock import AsyncMock, patch

import pytest
pytest.importorskip("nacl")
from nacl.public import PrivateKey, Box
from nacl.encoding import Base64Encoder

from hitl_cli.proxy_handler import ProxyHandler


class TestToolListInterception:
    """Test suite for tools/list request interception."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_tools_list_request_intercepted(self, mock_load_keys):
        """Test that tools/list requests are intercepted by proxy."""
        agent_private_key = PrivateKey.generate()
        agent_public_key = agent_private_key.public_key
        mock_load_keys.return_value = (
            agent_public_key.encode(Base64Encoder).decode(),
            agent_private_key.encode(Base64Encoder).decode()
        )

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

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_non_tools_list_forwarded_to_backend(self, mock_load_keys):
        """Test that non-tools/list requests are forwarded to backend."""
        agent_private_key = PrivateKey.generate()
        agent_public_key = agent_private_key.public_key
        mock_load_keys.return_value = (
            agent_public_key.encode(Base64Encoder).decode(),
            agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Mock non-tools/list request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "other/method",
            "params": {}
        }

        # Should forward to backend
        with patch.object(handler, 'forward_to_backend') as mock_forward:
            mock_forward.return_value = {"jsonrpc": "2.0", "id": 1, "result": {}}

            response = await handler.handle_mcp_request(json.dumps(request))

            mock_forward.assert_called_once()
            assert response["jsonrpc"] == "2.0"

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_tools_list_only_shows_plaintext_tools(self, mock_load_keys):
        """Test that tools/list only advertises plaintext tools to Claude."""
        agent_private_key = PrivateKey.generate()
        agent_public_key = agent_private_key.public_key
        mock_load_keys.return_value = (
            agent_public_key.encode(Base64Encoder).decode(),
            agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Mock backend tools
        mock_backend_tools = [
            {"name": "request_human_input", "description": "Request human input"},
            {"name": "request_human_input_e2ee", "description": "E2EE human input"},
            {"name": "notify_human", "description": "Notify human"},
            {"name": "notify_human_e2ee", "description": "E2EE notify human"},
            {"name": "other_tool", "description": "Other tool"}
        ]

        with patch.object(handler, 'get_backend_tools', new_callable=AsyncMock) as mock_get_tools:
            mock_get_tools.return_value = mock_backend_tools

            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }

            response = await handler.handle_mcp_request(json.dumps(request))

            # Should only include plaintext tools
            tools = response["result"]["tools"]
            tool_names = [tool["name"] for tool in tools]

            assert "request_human_input" in tool_names
            assert "notify_human" in tool_names
            assert "other_tool" in tool_names
            assert "request_human_input_e2ee" not in tool_names
            assert "notify_human_e2ee" not in tool_names


class TestRequestInterception:
    """Test suite for request_human_input interception."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"

        # Generate test keypairs
        self.agent_private_key = PrivateKey.generate()
        self.agent_public_key = self.agent_private_key.public_key

        self.device_private_key = PrivateKey.generate()
        self.device_public_key = self.device_private_key.public_key

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_request_human_input_intercepted(self, mock_load_keys):
        """Test that request_human_input calls are intercepted."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Mock request_human_input call
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "request_human_input",
                "arguments": {
                    "prompt": "Test prompt",
                    "choices": ["Yes", "No"]
                }
            }
        }

        # Should intercept and encrypt
        with patch.object(handler, 'handle_request_human_input') as mock_handle:
            mock_handle.return_value = {"jsonrpc": "2.0", "id": 1, "result": "Intercepted"}

            response = await handler.handle_mcp_request(json.dumps(request))

            mock_handle.assert_called_once()
            assert response["result"] == "Intercepted"

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_request_encryption_with_device_keys(self, mock_load_keys):
        """Test that requests are encrypted for each device public key."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Mock device public keys
        with patch.object(handler, 'get_device_public_keys') as mock_get_keys:
            mock_get_keys.return_value = [
                self.device_public_key.encode(Base64Encoder).decode()
            ]

            # Mock backend call
            with patch.object(handler, 'forward_to_backend') as mock_forward:
                mock_forward.return_value = {"jsonrpc": "2.0", "id": 1, "result": "Success"}

                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "request_human_input",
                        "arguments": {
                            "prompt": "Test prompt",
                            "choices": ["Yes", "No"]
                        }
                    }
                }

                await handler.handle_mcp_request(json.dumps(request))

                # Verify backend was called with E2EE tool
                mock_forward.assert_called_once()
                forwarded_request = mock_forward.call_args[0][0]

                assert forwarded_request["params"]["name"] == "request_human_input_e2ee"
                assert "encrypted_payload" in forwarded_request["params"]["arguments"]

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_request_falls_back_to_plaintext_if_no_device_keys(self, mock_load_keys):
        """Test that requests fall back to plaintext if no device keys available."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Mock no device public keys
        with patch.object(handler, 'get_device_public_keys') as mock_get_keys:
            mock_get_keys.return_value = []

            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "request_human_input",
                    "arguments": {
                        "prompt": "Test prompt"
                    }
                }
            }

            response = await handler.handle_mcp_request(json.dumps(request))

            # Should return error when no device keys available
            assert "error" in response
            assert "No device public keys available" in response["error"]["message"]

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_non_request_human_input_not_intercepted(self, mock_load_keys):
        """Test that non-request_human_input calls are not intercepted."""
        agent_private_key = PrivateKey.generate()
        agent_public_key = agent_private_key.public_key
        mock_load_keys.return_value = (
            agent_public_key.encode(Base64Encoder).decode(),
            agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Mock other tool call
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "other_tool",
                "arguments": {"param": "value"}
            }
        }

        # Should forward directly to backend
        with patch.object(handler, 'forward_to_backend') as mock_forward:
            mock_forward.return_value = {"jsonrpc": "2.0", "id": 1, "result": "Success"}

            await handler.handle_mcp_request(json.dumps(request))

            mock_forward.assert_called_once()
            forwarded_request = mock_forward.call_args[0][0]

            # Should be unchanged
            assert forwarded_request["params"]["name"] == "other_tool"
            assert forwarded_request["params"]["arguments"]["param"] == "value"


class TestResponseDecryption:
    """Test suite for encrypted response decryption."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"

        # Generate test keypairs
        self.agent_private_key = PrivateKey.generate()
        self.agent_public_key = self.agent_private_key.public_key

        self.device_private_key = PrivateKey.generate()
        self.device_public_key = self.device_private_key.public_key

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_encrypted_response_decrypted(self, mock_load_keys):
        """Test that encrypted responses are decrypted before returning to Claude."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Create encrypted response payload in newer structure
        plaintext_response = "User clicked Yes"

        # Encrypt response (device -> agent)
        device_to_agent_box = Box(self.device_private_key, self.agent_public_key)
        encrypted_response = device_to_agent_box.encrypt(
            plaintext_response.encode(),
            encoder=Base64Encoder
        )

        encrypted_response_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {"type": "text", "text": encrypted_response.decode()}
                ]
            }
        }

        device_public_key_b64 = self.device_public_key.encode(Base64Encoder).decode()
        decrypted = handler.process_encrypted_response(encrypted_response_payload, device_public_key_b64)
        decrypted_text = decrypted["result"]["content"][0]["text"]

        assert decrypted_text == plaintext_response

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_plaintext_response_returned_unchanged(self, mock_load_keys):
        """Test that plaintext responses are returned unchanged."""
        agent_private_key = PrivateKey.generate()
        agent_public_key = agent_private_key.public_key
        mock_load_keys.return_value = (
            agent_public_key.encode(Base64Encoder).decode(),
            agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Mock backend returning plaintext response
        plaintext_response = "User clicked No"

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "other_tool",
                "arguments": {"param": "value"}
            }
        }

        # Mock forward_to_backend to return plaintext
        with patch.object(handler, 'forward_to_backend') as mock_forward:
            mock_forward.return_value = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": plaintext_response
            }

            response = await handler.handle_mcp_request(json.dumps(request))

            # Should return plaintext unchanged
            assert response["result"] == plaintext_response

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_decryption_error_handling(self, mock_load_keys):
        """Test handling of decryption errors."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Create invalid encrypted response payload
        response_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {"type": "text", "text": "invalid_encrypted_data"}
                ]
            }
        }

        device_public_key_b64 = self.device_public_key.encode(Base64Encoder).decode()
        response = handler.process_encrypted_response(response_payload, device_public_key_b64)

        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Failed to decrypt response" in response["error"]["message"]


class TestProxyHandlerIntegration:
    """Integration tests for the proxy handler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"

        # Generate test keypairs
        self.agent_private_key = PrivateKey.generate()
        self.agent_public_key = self.agent_private_key.public_key

        self.device_private_key = PrivateKey.generate()
        self.device_public_key = self.device_private_key.public_key

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_end_to_end_encryption_flow(self, mock_load_keys):
        """Test complete E2EE flow from request to response."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Mock device keys and backend responses
        with patch.object(handler, 'get_device_public_keys') as mock_get_keys:
            mock_get_keys.return_value = [
                self.device_public_key.encode(Base64Encoder).decode()
            ]

            with patch.object(handler, 'forward_to_backend') as mock_forward:
                # Simulate encrypted response from backend
                plaintext_response = "User approved the request"
                device_to_agent_box = Box(self.device_private_key, self.agent_public_key)
                encrypted_response = device_to_agent_box.encrypt(
                    plaintext_response.encode(),
                    encoder=Base64Encoder
                )

                mock_forward.return_value = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {"content": [{"type": "text", "text": encrypted_response.decode()}]}
                }

                # Make request
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "request_human_input",
                        "arguments": {
                            "prompt": "Do you approve this action?",
                            "choices": ["Yes", "No"]
                        }
                    }
                }

                response = await handler.handle_mcp_request(json.dumps(request))

                # Verify encryption was applied to request
                mock_forward.assert_called_once()
                forwarded_request = mock_forward.call_args[0][0]
                assert forwarded_request["params"]["name"] == "request_human_input_e2ee"

                # Verify response was decrypted
                assert response["result"] == plaintext_response

    @pytest.mark.asyncio
    @patch('hitl_cli.proxy_handler.load_agent_keypair')
    async def test_proxy_handler_error_handling(self, mock_load_keys):
        """Test proxy handler error handling in various scenarios."""
        agent_private_key = PrivateKey.generate()
        agent_public_key = agent_private_key.public_key
        mock_load_keys.return_value = (
            agent_public_key.encode(Base64Encoder).decode(),
            agent_private_key.encode(Base64Encoder).decode()
        )

        handler = ProxyHandler(self.backend_url)

        # Test invalid JSON request
        invalid_request = "invalid json"
        response = await handler.handle_mcp_request(invalid_request)

        assert "error" in response
        assert "Invalid JSON" in response["error"]["message"]

        # Test malformed MCP request
        malformed_request = {
            "invalid": "request",
            "missing_required_fields": True
        }

        response = await handler.handle_mcp_request(json.dumps(malformed_request))

        # Should handle gracefully
        assert "error" in response or "jsonrpc" in response
