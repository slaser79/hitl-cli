"""
Tests for core authentication logic

These tests validate the authentication helper functions and token management.
"""

from unittest.mock import patch

from hitl_cli.auth import is_logged_in, load_token, save_token


class TestTokenManagement:
    """Test token storage and retrieval logic"""

    def test_save_and_load_token(self, tmp_path):
        """Test saving and loading tokens"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                # Test saving token
                save_token("test-token-123")

                # Test loading token
                loaded_token = load_token()
                assert loaded_token == "test-token-123"

    def test_is_logged_in_with_token(self, tmp_path):
        """Test is_logged_in returns True when token exists"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                save_token("valid-token")
                assert is_logged_in() is True

    def test_is_logged_in_without_token(self, tmp_path):
        """Test is_logged_in returns False when no token exists"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                assert is_logged_in() is False

    def test_load_token_no_file(self, tmp_path):
        """Test load_token returns None when no token file exists"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                loaded_token = load_token()
                assert loaded_token is None


class TestTokenSecurity:
    """Test token storage security"""

    def test_token_file_permissions(self, tmp_path):
        """Test that token file is created with correct permissions"""

        config_dir = tmp_path / ".config" / "hitl-cli"
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                save_token("test-token")

                # Check directory permissions (700)
                assert oct(config_dir.stat().st_mode)[-3:] == '700'

                # Check file permissions (600)
                assert oct(token_file.stat().st_mode)[-3:] == '600'

                # Verify token content
                assert load_token() == "test-token"

    def test_config_directory_creation(self, tmp_path):
        """Test that config directory is created with proper permissions"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                # Directory should not exist initially
                assert not config_dir.exists()

                # Save token should create directory
                save_token("test-token")

                # Directory should now exist with correct permissions
                assert config_dir.exists()
                assert oct(config_dir.stat().st_mode)[-3:] == '700'