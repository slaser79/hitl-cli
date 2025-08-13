"""
Tests for CLI proxy mode functionality.

Tests the new `hitl-cli proxy <backend_url>` command that enables transparent
end-to-end encryption by acting as an MCP proxy between Claude and the backend.
"""

import asyncio
import json
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from io import StringIO

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

    def test_proxy_command_accepts_backend_url(self):
        """Test that proxy command accepts backend_url argument."""
        with patch('hitl_cli.proxy_handler_v2.create_fastmcp_proxy_server') as mock_create_server, \
             patch('hitl_cli.crypto.load_agent_keypair') as mock_load_keys:
            
            # Mock the FastMCP server creation
            mock_server = MagicMock()
            mock_server.run_stdio_async = AsyncMock()
            mock_create_server.return_value = mock_server
            mock_load_keys.return_value = ("test_public", "test_private")
            
            result = self.runner.invoke(app, ["proxy", "https://test-backend.com"])
            
            # Command should be recognized and attempt to start proxy
            assert result.exit_code == 0 or "backend_url" in str(result.exception) if result.exception else True

    @patch('hitl_cli.proxy_handler.ProxyHandler')
    def test_proxy_command_help(self, mock_handler):
        """Test proxy command help text."""
        result = self.runner.invoke(app, ["proxy", "--help"])
        assert result.exit_code == 0
        assert "proxy" in result.stdout.lower()
        assert "backend" in result.stdout.lower()

    @patch('hitl_cli.crypto.ensure_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler')
    def test_proxy_command_initializes_keys(self, mock_handler, mock_ensure_keys):
        """Test that proxy command initializes agent keypair before starting."""
        mock_handler.return_value.start_proxy_loop = AsyncMock()
        mock_ensure_keys.return_value = ("public_key", "private_key")
        
        result = self.runner.invoke(app, ["proxy", "https://test-backend.com"])
        
        # Should call key initialization
        mock_ensure_keys.assert_called_once()

    @patch('hitl_cli.crypto.ensure_agent_keypair')
    @patch('hitl_cli.proxy_handler.ProxyHandler')
    def test_proxy_command_starts_handler(self, mock_handler, mock_ensure_keys):
        """Test that proxy command starts the proxy handler."""
        mock_proxy_instance = mock_handler.return_value
        mock_proxy_instance.start_proxy_loop = AsyncMock()
        mock_ensure_keys.return_value = ("public_key", "private_key")
        
        result = self.runner.invoke(app, ["proxy", "https://test-backend.com"])
        
        # Should create handler with correct backend URL
        mock_handler.assert_called_once_with("https://test-backend.com")
        # Should start the proxy loop
        mock_proxy_instance.start_proxy_loop.assert_called_once()


class TestProxyHandler:
    """Test suite for the proxy handler core functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend_url = "https://test-backend.com"

    @patch('hitl_cli.crypto.load_agent_keypair')
    def test_proxy_handler_initialization(self, mock_load_keys):
        """Test proxy handler initialization."""
        from hitl_cli.proxy_handler import ProxyHandler
        
        mock_load_keys.return_value = ("public_key", "private_key")
        
        handler = ProxyHandler(self.backend_url)
        
        assert handler.backend_url == self.backend_url
        assert handler.public_key == "public_key"
        assert handler.private_key == "private_key"

    @pytest.mark.asyncio
    @patch('hitl_cli.crypto.load_agent_keypair')
    @patch('sys.stdin')
    @patch('sys.stdout')
    async def test_proxy_handler_stdio_loop(self, mock_stdout, mock_stdin, mock_load_keys):
        """Test that proxy handler listens for MCP JSON-RPC over stdio."""
        from hitl_cli.proxy_handler import ProxyHandler
        
        mock_load_keys.return_value = ("public_key", "private_key")
        
        # Mock stdin to provide a sample MCP request
        mock_stdin.readline = AsyncMock(side_effect=[
            '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}\n',
            ''  # EOF to end loop
        ])
        
        handler = ProxyHandler(self.backend_url)
        handler.handle_mcp_request = AsyncMock(return_value={
            "jsonrpc": "2.0", 
            "id": 1, 
            "result": {"tools": []}
        })
        
        # Start proxy loop (should terminate when stdin returns empty)
        await handler.start_proxy_loop()
        
        # Should have processed the MCP request
        handler.handle_mcp_request.assert_called_once()

    @pytest.mark.asyncio
    @patch('hitl_cli.crypto.load_agent_keypair')
    async def test_proxy_handler_invalid_json(self, mock_load_keys):
        """Test proxy handler handles invalid JSON gracefully."""
        from hitl_cli.proxy_handler import ProxyHandler
        
        mock_load_keys.return_value = ("public_key", "private_key")
        
        handler = ProxyHandler(self.backend_url)
        
        # Should return error response for invalid JSON
        response = await handler.handle_mcp_request("invalid json")
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        assert response["error"]["code"] == -32700  # Parse error

    @pytest.mark.asyncio
    @patch('hitl_cli.crypto.load_agent_keypair')
    async def test_proxy_handler_missing_method(self, mock_load_keys):
        """Test proxy handler handles missing method gracefully."""
        from hitl_cli.proxy_handler import ProxyHandler
        
        mock_load_keys.return_value = ("public_key", "private_key")
        
        handler = ProxyHandler(self.backend_url)
        
        # Request without method
        request = {"jsonrpc": "2.0", "id": 1, "params": {}}
        
        response = await handler.handle_mcp_request(json.dumps(request))
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        assert response["error"]["code"] == -32600  # Invalid request

    @pytest.mark.asyncio 
    @patch('hitl_cli.crypto.load_agent_keypair')
    async def test_proxy_handler_termination_on_parent_exit(self, mock_load_keys):
        """Test that proxy terminates when parent process ends."""
        from hitl_cli.proxy_handler import ProxyHandler
        
        mock_load_keys.return_value = ("public_key", "private_key")
        
        handler = ProxyHandler(self.backend_url)
        
        # Mock stdin to simulate parent process ending (EOF)
        with patch('sys.stdin') as mock_stdin:
            mock_stdin.readline = AsyncMock(return_value='')  # EOF
            
            # Should exit cleanly when parent terminates
            await handler.start_proxy_loop()
            
            # Should not raise any exceptions