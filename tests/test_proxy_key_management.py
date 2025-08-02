"""
Tests for proxy key management functionality.

Tests agent keypair generation, storage, and retrieval for end-to-end encryption.
Uses PyNaCl for cryptographic operations.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from nacl.public import PrivateKey, PublicKey
from nacl.encoding import Base64Encoder

from hitl_cli.crypto import (
    generate_agent_keypair,
    save_agent_keypair, 
    load_agent_keypair,
    ensure_agent_keypair,
    get_agent_keys_path,
    register_public_key_with_backend
)


class TestKeyGeneration:
    """Test suite for cryptographic key generation."""

    def test_generate_agent_keypair_returns_valid_keys(self):
        """Test that key generation returns valid PyNaCl key pair."""
        public_key_b64, private_key_b64 = generate_agent_keypair()
        
        # Should return base64-encoded strings
        assert isinstance(public_key_b64, str)
        assert isinstance(private_key_b64, str)
        
        # Should be valid base64 encoding
        public_key_bytes = Base64Encoder.decode(public_key_b64)
        private_key_bytes = Base64Encoder.decode(private_key_b64)
        
        # Should be valid PyNaCl keys
        public_key = PublicKey(public_key_bytes)
        private_key = PrivateKey(private_key_bytes)
        
        # Public key from private key should match
        assert private_key.public_key.encode() == public_key.encode()

    def test_generate_agent_keypair_unique_keys(self):
        """Test that each key generation produces unique keys."""
        pub1, priv1 = generate_agent_keypair()
        pub2, priv2 = generate_agent_keypair()
        
        # Keys should be different each time
        assert pub1 != pub2
        assert priv1 != priv2

    def test_generate_agent_keypair_correct_length(self):
        """Test that generated keys have correct byte length."""
        public_key_b64, private_key_b64 = generate_agent_keypair()
        
        public_key_bytes = Base64Encoder.decode(public_key_b64)
        private_key_bytes = Base64Encoder.decode(private_key_b64)
        
        # PyNaCl key lengths
        assert len(public_key_bytes) == 32  # 32 bytes for Curve25519 public key
        assert len(private_key_bytes) == 32  # 32 bytes for Curve25519 private key


class TestKeyStorage:
    """Test suite for key storage and retrieval."""

    def setup_method(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.keys_path = Path(self.temp_dir) / "agent.key"

    def teardown_method(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_agent_keys_path_default(self):
        """Test default agent keys path location."""
        expected_path = Path.home() / ".config" / "hitl-shin-relay" / "agent.key"
        assert get_agent_keys_path() == expected_path

    def test_get_agent_keys_path_creates_directory(self):
        """Test that get_agent_keys_path creates parent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "new_dir" / "agent.key"
            
            with patch('hitl_cli.crypto.Path.home') as mock_home:
                mock_home.return_value = Path(temp_dir)
                
                result_path = get_agent_keys_path()
                
                # Directory should be created
                assert result_path.parent.exists()

    def test_save_agent_keypair(self):
        """Test saving agent keypair to file."""
        public_key, private_key = generate_agent_keypair()
        
        save_agent_keypair(public_key, private_key, self.keys_path)
        
        # File should exist
        assert self.keys_path.exists()
        
        # File should have restricted permissions (600)
        file_stat = self.keys_path.stat()
        assert oct(file_stat.st_mode)[-3:] == "600"

    def test_save_agent_keypair_overwrites_existing(self):
        """Test that saving overwrites existing keys."""
        # Create initial keys
        pub1, priv1 = generate_agent_keypair()
        save_agent_keypair(pub1, priv1, self.keys_path)
        
        # Save different keys
        pub2, priv2 = generate_agent_keypair()
        save_agent_keypair(pub2, priv2, self.keys_path)
        
        # Should load the new keys
        loaded_pub, loaded_priv = load_agent_keypair(self.keys_path)
        assert loaded_pub == pub2
        assert loaded_priv == priv2

    def test_load_agent_keypair_success(self):
        """Test loading valid agent keypair from file."""
        public_key, private_key = generate_agent_keypair()
        save_agent_keypair(public_key, private_key, self.keys_path)
        
        loaded_public, loaded_private = load_agent_keypair(self.keys_path)
        
        assert loaded_public == public_key
        assert loaded_private == private_key

    def test_load_agent_keypair_file_not_found(self):
        """Test loading keypair when file doesn't exist."""
        non_existent_path = Path(self.temp_dir) / "nonexistent.key"
        
        with pytest.raises(FileNotFoundError):
            load_agent_keypair(non_existent_path)

    def test_load_agent_keypair_invalid_format(self):
        """Test loading keypair from corrupted file."""
        # Write invalid content to key file
        self.keys_path.write_text("invalid json content")
        
        with pytest.raises((ValueError, KeyError)):
            load_agent_keypair(self.keys_path)

    def test_load_agent_keypair_missing_keys(self):
        """Test loading keypair with missing key fields."""
        # Write JSON without required keys
        import json
        self.keys_path.write_text(json.dumps({"invalid": "data"}))
        
        with pytest.raises(KeyError):
            load_agent_keypair(self.keys_path)


class TestKeyEnsurance:
    """Test suite for key ensurance functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.keys_path = Path(self.temp_dir) / "agent.key"

    def teardown_method(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('hitl_cli.crypto.get_agent_keys_path')
    def test_ensure_agent_keypair_creates_new_keys(self, mock_get_path):
        """Test that ensure_agent_keypair creates new keys when none exist."""
        mock_get_path.return_value = self.keys_path
        
        public_key, private_key = ensure_agent_keypair()
        
        # Should return valid keys
        assert isinstance(public_key, str)
        assert isinstance(private_key, str)
        
        # Should create the key file
        assert self.keys_path.exists()
        
        # Should be able to load the same keys
        loaded_pub, loaded_priv = load_agent_keypair(self.keys_path)
        assert loaded_pub == public_key
        assert loaded_priv == private_key

    @patch('hitl_cli.crypto.get_agent_keys_path')
    def test_ensure_agent_keypair_loads_existing_keys(self, mock_get_path):
        """Test that ensure_agent_keypair loads existing keys."""
        mock_get_path.return_value = self.keys_path
        
        # Create existing keys
        existing_pub, existing_priv = generate_agent_keypair()
        save_agent_keypair(existing_pub, existing_priv, self.keys_path)
        
        # Should load existing keys, not create new ones
        public_key, private_key = ensure_agent_keypair()
        
        assert public_key == existing_pub
        assert private_key == existing_priv

    @patch('hitl_cli.crypto.get_agent_keys_path')
    @patch('hitl_cli.crypto.register_public_key_with_backend')
    def test_ensure_agent_keypair_registers_new_keys(self, mock_register, mock_get_path):
        """Test that ensure_agent_keypair registers new keys with backend."""
        mock_get_path.return_value = self.keys_path
        mock_register.return_value = True
        
        public_key, private_key = ensure_agent_keypair()
        
        # Should register the public key with backend
        mock_register.assert_called_once_with(public_key)

    @patch('hitl_cli.crypto.get_agent_keys_path')
    @patch('hitl_cli.crypto.register_public_key_with_backend')
    def test_ensure_agent_keypair_skips_registration_for_existing(self, mock_register, mock_get_path):
        """Test that ensure_agent_keypair doesn't re-register existing keys."""
        mock_get_path.return_value = self.keys_path
        
        # Create existing keys
        existing_pub, existing_priv = generate_agent_keypair()
        save_agent_keypair(existing_pub, existing_priv, self.keys_path)
        
        public_key, private_key = ensure_agent_keypair()
        
        # Should not register existing keys
        mock_register.assert_not_called()


class TestBackendRegistration:
    """Test suite for backend public key registration."""

    @pytest.mark.asyncio
    @patch('hitl_cli.api_client.ApiClient')
    async def test_register_public_key_with_backend_success(self, mock_api_client):
        """Test successful public key registration with backend."""
        # Mock successful API response
        mock_client_instance = mock_api_client.return_value
        mock_client_instance.post = MagicMock(return_value={"status": "registered"})
        
        public_key = "test_public_key_base64"
        result = await register_public_key_with_backend(public_key)
        
        assert result is True
        
        # Should call the correct API endpoint
        mock_client_instance.post.assert_called_once_with(
            "/api/v1/agents/public-key",
            {"public_key": public_key}
        )

    @pytest.mark.asyncio
    @patch('hitl_cli.api_client.ApiClient')
    async def test_register_public_key_with_backend_failure(self, mock_api_client):
        """Test public key registration failure handling."""
        # Mock API failure
        mock_client_instance = mock_api_client.return_value
        mock_client_instance.post = MagicMock(side_effect=Exception("API Error"))
        
        public_key = "test_public_key_base64"
        result = await register_public_key_with_backend(public_key)
        
        assert result is False

    @pytest.mark.asyncio
    @patch('hitl_cli.api_client.ApiClient')
    async def test_register_public_key_with_backend_http_error(self, mock_api_client):
        """Test public key registration with HTTP error response."""
        # Mock HTTP error response
        mock_client_instance = mock_api_client.return_value
        mock_client_instance.post = MagicMock(side_effect=Exception("400 Bad Request"))
        
        public_key = "test_public_key_base64"
        result = await register_public_key_with_backend(public_key)
        
        assert result is False