"""
Tests for CLI proxy mode functionality.

Tests the new `hitl-cli proxy <backend_url>` command that enables transparent
end-to-end encryption by acting as an MCP proxy between Claude and the backend.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from hitl_cli.main import app


class TestProxyCommand:
    """Test suite for the proxy command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_proxy_command_exists(self):
        """Test that the proxy command is available in the CLI."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "proxy" in result.stdout

    def test_proxy_command_requires_backend_url(self):
        """Test that proxy command requires backend_url argument."""
        result = self.runner.invoke(app, ["proxy"])
        assert result.exit_code != 0

    @patch('hitl_cli.main.is_logged_in', return_value=True)
    @patch('hitl_cli.main.create_fastmcp_proxy_server')
    @patch('hitl_cli.main.ensure_agent_keypair')
    def test_proxy_command_accepts_backend_url(self, mock_ensure_keys, mock_create_server, mock_is_logged_in):
        """Test that proxy command accepts backend_url argument."""
        with patch('hitl_cli.main.is_logged_in', return_value=True), \
             patch('hitl_cli.main.create_fastmcp_proxy_server') as mock_create_server, \
             patch('hitl_cli.main.ensure_agent_keypair') as mock_ensure_keys:

            # Mock the FastMCP server creation
            mock_server = MagicMock()
            mock_server.run_stdio_async = AsyncMock()
            mock_create_server.return_value = mock_server
            mock_ensure_keys.return_value = ("test_public", "test_private")

            result = self.runner.invoke(app, ["proxy", "https://test-backend.com"])

            # Command should succeed
            assert result.exit_code == 0
            # Verify server was created and run
            mock_create_server.assert_called_once_with("https://test-backend.com")
            mock_server.run_stdio_async.assert_awaited_once()

    def test_proxy_command_help(self):
        """Test proxy command help text."""
        result = self.runner.invoke(app, ["proxy", "--help"])
        assert result.exit_code == 0
        assert "proxy" in result.stdout.lower()
        assert "backend" in result.stdout.lower()

    @patch('hitl_cli.main.is_logged_in', return_value=True)
    @patch('hitl_cli.main.ensure_agent_keypair')
    @patch('hitl_cli.main.create_fastmcp_proxy_server')
    def test_proxy_command_initializes_keys(self, mock_create_server, mock_ensure_keys, mock_is_logged_in):
        """Test that proxy command initializes agent keypair before starting."""
        mock_server = MagicMock()
        mock_server.run_stdio_async = AsyncMock()
        mock_create_server.return_value = mock_server
        mock_ensure_keys.return_value = ("test_public", "test_private")

        result = self.runner.invoke(app, ["proxy", "https://test-backend.com"])

        # Should call key initialization
        mock_ensure_keys.assert_called_once()
        assert result.exit_code == 0

    @patch('hitl_cli.main.is_logged_in', return_value=True)
    @patch('hitl_cli.main.ensure_agent_keypair')
    @patch('hitl_cli.main.create_fastmcp_proxy_server')
    def test_proxy_command_starts_handler(self, mock_create_server, mock_ensure_keys, mock_is_logged_in):
        """Test that proxy command starts the proxy handler."""
        mock_server = MagicMock()
        mock_server.run_stdio_async = AsyncMock()
        mock_create_server.return_value = mock_server
        mock_ensure_keys.return_value = ("public_key", "private_key")

        result = self.runner.invoke(app, ["proxy", "https://test-backend.com"])

        # Should create server with correct backend URL
        mock_create_server.assert_called_once_with("https://test-backend.com")
        # Should start the server
        mock_server.run_stdio_async.assert_awaited_once()
        assert result.exit_code == 0
