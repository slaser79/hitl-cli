"""
Tests for API Client functionality

These tests validate:
1. Exit code handling with typer
2. Error response handling
3. Authentication integration
4. HTTP method implementations
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
import typer
from hitl_cli.api_client import ApiClient
from hitl_cli.auth import save_token


class TestApiClientExitCodeHandling:
    """Test API Client exit code handling"""

    @pytest.fixture
    def mock_config_dir(self, tmp_path):
        """Create a temporary config directory"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                yield config_dir, token_file

    def test_handle_response_401_uses_correct_exit_code(self, mock_config_dir):
        """Test that _handle_response uses correct typer.Exit parameter for 401 errors"""
        config_dir, token_file = mock_config_dir
        save_token("test-token")

        client = ApiClient()

        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Authentication failed"}

        with pytest.raises(typer.Exit) as exc_info:
            client._handle_response(mock_response)

        # Verify correct exit code is used
        assert exc_info.value.exit_code == 1
        assert hasattr(exc_info.value, 'exit_code')  # Should have exit_code attribute, not 'code'

    def test_handle_response_generic_error_uses_correct_exit_code(self, mock_config_dir):
        """Test that _handle_response uses correct typer.Exit parameter for generic errors"""
        config_dir, token_file = mock_config_dir
        save_token("test-token")

        client = ApiClient()

        # Mock 500 response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "Internal server error"}

        with pytest.raises(typer.Exit) as exc_info:
            client._handle_response(mock_response)

        # Verify correct exit code is used
        assert exc_info.value.exit_code == 1
        assert hasattr(exc_info.value, 'exit_code')  # Should have exit_code attribute, not 'code'

    def test_handle_response_success_returns_json(self, mock_config_dir):
        """Test that _handle_response returns JSON for successful responses"""
        config_dir, token_file = mock_config_dir
        save_token("test-token")

        client = ApiClient()

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": "test"}

        result = client._handle_response(mock_response)

        assert result == {"status": "success", "data": "test"}

    def test_handle_response_invalid_json_returns_default(self, mock_config_dir):
        """Test that _handle_response handles invalid JSON gracefully"""
        config_dir, token_file = mock_config_dir
        save_token("test-token")

        client = ApiClient()

        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        result = client._handle_response(mock_response)

        assert result == {"status": "success"}

    def test_get_headers_not_logged_in_uses_correct_exit_code(self, mock_config_dir):
        """Test that _get_headers uses correct typer.Exit parameter when not logged in"""
        config_dir, token_file = mock_config_dir
        # Don't save any token

        client = ApiClient()

        with pytest.raises(typer.Exit) as exc_info:
            client._get_headers()

        # Verify correct exit code is used
        assert exc_info.value.exit_code == 1
        assert hasattr(exc_info.value, 'exit_code')  # Should have exit_code attribute, not 'code'


class TestApiClientSyncWrapperHandling:
    """Test API Client sync wrapper handling"""

    @pytest.fixture
    def mock_config_dir(self, tmp_path):
        """Create a temporary config directory"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                yield config_dir, token_file

    def test_post_sync_handles_typer_exit_correctly(self, mock_config_dir):
        """Test that post_sync handles typer.Exit with correct attribute access"""
        config_dir, token_file = mock_config_dir
        save_token("test-token")

        client = ApiClient()

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            # Mock 401 response to trigger typer.Exit
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"detail": "Auth failed"}

            # Make the post method return a coroutine that yields the mock response
            async def mock_post(*args, **kwargs):
                return mock_response
            mock_client.post = mock_post

            # Call post_sync
            result = client.post_sync("/test", {"data": "test"})

            # Verify it returns MockResponse with correct status code from typer.Exit
            assert hasattr(result, 'status_code')
            assert hasattr(result, 'json')
            assert result.status_code == 1  # Should be 1 from typer.Exit(1), not 500 from missing 'code' attribute
            assert result.json()["error"] == "Request failed"

    def test_post_sync_success_returns_mock_response(self, mock_config_dir):
        """Test that post_sync returns MockResponse for successful requests"""
        config_dir, token_file = mock_config_dir
        save_token("test-token")

        client = ApiClient()

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success", "id": "123"}

            # Make the post method return a coroutine
            async def mock_post(*args, **kwargs):
                return mock_response
            mock_client.post = mock_post

            # Call post_sync
            result = client.post_sync("/test", {"data": "test"})

            # Verify it returns MockResponse with correct data
            assert hasattr(result, 'status_code')
            assert hasattr(result, 'json')
            assert result.status_code == 200
            assert result.json() == {"status": "success", "id": "123"}


class TestApiClientAuthentication:
    """Test API Client authentication handling"""

    @pytest.fixture
    def mock_config_dir(self, tmp_path):
        """Create a temporary config directory"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                yield config_dir, token_file

    def test_get_headers_includes_auth_token(self, mock_config_dir):
        """Test that _get_headers includes correct authorization header"""
        config_dir, token_file = mock_config_dir
        save_token("test-jwt-token")

        client = ApiClient()

        headers = client._get_headers()

        assert headers["Authorization"] == "Bearer test-jwt-token"
        assert headers["Content-Type"] == "application/json"

    def test_all_methods_use_auth_headers(self, mock_config_dir):
        """Test that all HTTP methods use authentication headers"""
        config_dir, token_file = mock_config_dir
        save_token("test-jwt-token")

        client = ApiClient()

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}

            # Make all methods return coroutines
            async def mock_get(*args, **kwargs):
                return mock_response
            async def mock_post(*args, **kwargs):
                return mock_response
            async def mock_put(*args, **kwargs):
                return mock_response
            async def mock_delete(*args, **kwargs):
                return mock_response

            mock_client.get = mock_get
            mock_client.post = mock_post
            mock_client.put = mock_put
            mock_client.delete = mock_delete

            # Test all methods
            import asyncio
            asyncio.run(client.get("/test"))
            asyncio.run(client.post("/test", {"data": "test"}))
            asyncio.run(client.put("/test", {"data": "test"}))
            asyncio.run(client.delete("/test"))

            # Verify all calls used auth headers
            for call in [mock_client.get, mock_client.post, mock_client.put, mock_client.delete]:
                call.assert_called_once()
                call_args = call.call_args
                headers = call_args[1]["headers"]
                assert headers["Authorization"] == "Bearer test-jwt-token"
                assert headers["Content-Type"] == "application/json"
