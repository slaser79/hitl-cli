"""
Tests for response decryption functionality.

Tests that the proxy receives encrypted responses from the backend,
decrypts them with the agent's private key, and returns plaintext to Claude.
"""

import json
import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import Base64Encoder

from hitl_cli.proxy_handler import ProxyHandler


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

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler.get_device_public_keys')
    @patch('hitl_cli.proxy_handler.ProxyHandler.forward_to_backend')
    async def test_encrypted_response_decrypted(self, mock_forward, mock_get_keys, mock_load_keys):
        """Test that encrypted responses are decrypted before returning to Claude."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )
        
        mock_get_keys.return_value = [
            self.device_public_key.encode(Base64Encoder).decode()
        ]
        
        # Create encrypted response from device
        plaintext_response = "User clicked Yes"
        
        # Encrypt response (device -> agent)
        box = Box(self.device_private_key, self.agent_public_key)
        encrypted_bytes = box.encrypt(plaintext_response.encode())
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode()
        
        # Mock backend returning encrypted response
        mock_forward.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": encrypted_b64
                    }
                ],
                "isError": False
            }
        }
        
        handler = ProxyHandler(self.backend_url)
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "request_human_input",
                "arguments": {"prompt": "Click Yes or No"}
            }
        }
        
        response = await handler.handle_request_human_input(request)
        
        # Should decrypt and return plaintext
        assert response["result"]["content"][0]["text"] == plaintext_response

    @patch('hitl_cli.crypto.load_agent_keypair')
    def test_decrypt_response_success(self, mock_load_keys):
        """Test successful response decryption."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )
        
        handler = ProxyHandler(self.backend_url)
        
        # Create encrypted data
        plaintext = "Decrypted response text"
        
        # Encrypt (device -> agent)
        box = Box(self.device_private_key, self.agent_public_key)
        encrypted_bytes = box.encrypt(plaintext.encode())
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode()
        
        # Mock device public key
        device_public_key_b64 = self.device_public_key.encode(Base64Encoder).decode()
        
        decrypted = handler.decrypt_response(encrypted_b64, device_public_key_b64)
        
        assert decrypted == plaintext

    @patch('hitl_cli.crypto.load_agent_keypair')
    def test_decrypt_response_invalid_base64(self, mock_load_keys):
        """Test decrypt_response with invalid base64 input."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )
        
        handler = ProxyHandler(self.backend_url)
        
        invalid_b64 = "not_valid_base64!!!"
        device_public_key_b64 = self.device_public_key.encode(Base64Encoder).decode()
        
        with pytest.raises(Exception, match="Failed to decode"):
            handler.decrypt_response(invalid_b64, device_public_key_b64)

    @patch('hitl_cli.crypto.load_agent_keypair')
    def test_decrypt_response_wrong_device_key(self, mock_load_keys):
        """Test decrypt_response with wrong device public key."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )
        
        handler = ProxyHandler(self.backend_url)
        
        # Create encrypted data with device1
        plaintext = "Secret message"
        box = Box(self.device_private_key, self.agent_public_key)
        encrypted_bytes = box.encrypt(plaintext.encode())
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode()
        
        # Try to decrypt with wrong device key
        wrong_device_key = PrivateKey.generate().public_key
        wrong_device_key_b64 = wrong_device_key.encode(Base64Encoder).decode()
        
        with pytest.raises(Exception, match="Failed to decrypt"):
            handler.decrypt_response(encrypted_b64, wrong_device_key_b64)

    @patch('hitl_cli.crypto.load_agent_keypair')
    def test_decrypt_response_corrupted_data(self, mock_load_keys):
        """Test decrypt_response with corrupted encrypted data."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )
        
        handler = ProxyHandler(self.backend_url)
        
        # Create valid encrypted data then corrupt it
        plaintext = "Original message"
        box = Box(self.device_private_key, self.agent_public_key)
        encrypted_bytes = box.encrypt(plaintext.encode())
        
        # Corrupt the data
        corrupted_bytes = encrypted_bytes[:-5] + b"12345"
        corrupted_b64 = base64.b64encode(corrupted_bytes).decode()
        
        device_public_key_b64 = self.device_public_key.encode(Base64Encoder).decode()
        
        with pytest.raises(Exception, match="Failed to decrypt"):
            handler.decrypt_response(corrupted_b64, device_public_key_b64)


class TestResponseProcessing:
    """Test suite for response processing and formatting."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler.decrypt_response')
    def test_process_encrypted_response_text_content(self, mock_decrypt, mock_load_keys):
        """Test processing encrypted response with text content."""
        mock_load_keys.return_value = ("agent_pub", "agent_priv")
        mock_decrypt.return_value = "Decrypted message"
        
        handler = ProxyHandler(self.backend_url)
        
        # Mock encrypted response format
        encrypted_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "encrypted_base64_data"
                    }
                ],
                "isError": False
            }
        }
        
        device_public_key = "device_key_base64"
        
        processed = handler.process_encrypted_response(encrypted_response, device_public_key)
        
        # Should decrypt the text content
        mock_decrypt.assert_called_once_with("encrypted_base64_data", device_public_key)
        
        # Should replace encrypted text with decrypted text
        assert processed["result"]["content"][0]["text"] == "Decrypted message"
        assert processed["jsonrpc"] == "2.0"
        assert processed["id"] == 1

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler.decrypt_response')
    def test_process_encrypted_response_multiple_content(self, mock_decrypt, mock_load_keys):
        """Test processing encrypted response with multiple content items."""
        mock_load_keys.return_value = ("agent_pub", "agent_priv")
        mock_decrypt.side_effect = ["Decrypted 1", "Decrypted 2"]
        
        handler = ProxyHandler(self.backend_url)
        
        encrypted_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {"type": "text", "text": "encrypted_data_1"},
                    {"type": "text", "text": "encrypted_data_2"}
                ],
                "isError": False
            }
        }
        
        device_public_key = "device_key_base64"
        
        processed = handler.process_encrypted_response(encrypted_response, device_public_key)
        
        # Should decrypt both content items
        assert mock_decrypt.call_count == 2
        assert processed["result"]["content"][0]["text"] == "Decrypted 1"
        assert processed["result"]["content"][1]["text"] == "Decrypted 2"

    @patch('hitl_cli.crypto.load_agent_keypair')
    def test_process_encrypted_response_no_content(self, mock_load_keys):
        """Test processing encrypted response with no content."""
        mock_load_keys.return_value = ("agent_pub", "agent_priv")
        
        handler = ProxyHandler(self.backend_url)
        
        encrypted_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [],
                "isError": False
            }
        }
        
        device_public_key = "device_key_base64"
        
        processed = handler.process_encrypted_response(encrypted_response, device_public_key)
        
        # Should return unchanged
        assert processed == encrypted_response

    @patch('hitl_cli.crypto.load_agent_keypair')
    def test_process_encrypted_response_error_response(self, mock_load_keys):
        """Test processing encrypted error response."""
        mock_load_keys.return_value = ("agent_pub", "agent_priv")
        
        handler = ProxyHandler(self.backend_url)
        
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32603,
                "message": "Internal error"
            }
        }
        
        device_public_key = "device_key_base64"
        
        processed = handler.process_encrypted_response(error_response, device_public_key)
        
        # Should return error unchanged
        assert processed == error_response

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler.decrypt_response')
    def test_process_encrypted_response_decryption_failure(self, mock_decrypt, mock_load_keys):
        """Test processing when decryption fails."""
        mock_load_keys.return_value = ("agent_pub", "agent_priv")
        mock_decrypt.side_effect = Exception("Decryption failed")
        
        handler = ProxyHandler(self.backend_url)
        
        encrypted_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {"type": "text", "text": "encrypted_data"}
                ],
                "isError": False
            }
        }
        
        device_public_key = "device_key_base64"
        
        processed = handler.process_encrypted_response(encrypted_response, device_public_key)
        
        # Should return error response
        assert "error" in processed
        assert "Failed to decrypt response" in processed["error"]["message"]

    @patch('hitl_cli.crypto.load_agent_keypair')
    def test_process_encrypted_response_non_text_content(self, mock_load_keys):
        """Test processing encrypted response with non-text content."""
        mock_load_keys.return_value = ("agent_pub", "agent_priv")
        
        handler = ProxyHandler(self.backend_url)
        
        encrypted_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {"type": "image", "url": "https://example.com/image.png"},
                    {"type": "text", "text": "This will not be decrypted"}
                ],
                "isError": False
            }
        }
        
        device_public_key = "device_key_base64"
        
        processed = handler.process_encrypted_response(encrypted_response, device_public_key)
        
        # Should only decrypt text content, leave others unchanged
        assert processed["result"]["content"][0]["type"] == "image"
        assert processed["result"]["content"][0]["url"] == "https://example.com/image.png"
        # In practice, text content would be decrypted, but we're not mocking it here
        assert processed["result"]["content"][1]["type"] == "text"


class TestEndToEndEncryption:
    """Test suite for complete end-to-end encryption flow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"
        
        # Generate test keypairs
        self.agent_private_key = PrivateKey.generate()
        self.agent_public_key = self.agent_private_key.public_key
        
        self.device_private_key = PrivateKey.generate()
        self.device_public_key = self.device_private_key.public_key

    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler.get_device_public_keys')
    @patch('hitl_cli.proxy_handler.ProxyHandler.forward_to_backend')
    async def test_full_encryption_decryption_cycle(self, mock_forward, mock_get_keys, mock_load_keys):
        """Test complete encryption/decryption cycle for request_human_input."""
        mock_load_keys.return_value = (
            self.agent_public_key.encode(Base64Encoder).decode(),
            self.agent_private_key.encode(Base64Encoder).decode()
        )
        
        mock_get_keys.return_value = [
            self.device_public_key.encode(Base64Encoder).decode()
        ]
        
        # Simulate user response
        user_response = "The user selected Option A"
        
        # Encrypt user response (device -> agent)
        box = Box(self.device_private_key, self.agent_public_key)
        encrypted_bytes = box.encrypt(user_response.encode())
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode()
        
        # Mock backend response with encrypted data
        mock_forward.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": encrypted_b64
                    }
                ],
                "isError": False
            }
        }
        
        handler = ProxyHandler(self.backend_url)
        
        # Simulate Claude's request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "request_human_input",
                "arguments": {
                    "prompt": "Please select an option:",
                    "choices": ["Option A", "Option B"]
                }
            }
        }
        
        response = await handler.handle_request_human_input(request)
        
        # Should receive decrypted plaintext response
        assert response["result"]["content"][0]["text"] == user_response
        assert "error" not in response
        
        # Verify encryption was used by checking backend call
        forwarded_request = mock_forward.call_args[0][0]
        assert forwarded_request["params"]["name"] == "request_human_input_e2ee"
        assert "encrypted_payload" in forwarded_request["params"]["arguments"]