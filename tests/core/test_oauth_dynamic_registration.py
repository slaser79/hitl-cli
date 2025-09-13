"""
Comprehensive tests for OAuth 2.1 dynamic client registration

This test module validates:
1. RFC 7591 dynamic client registration
2. OAuth 2.1 + PKCE authorization flow
3. Bearer token authentication
4. Integration with FastMCP OAuth client
5. MCP client updates for OAuth Bearer auth
"""

import json
import secrets
import base64
import hashlib
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, AsyncMock
from urllib.parse import parse_qs, urlparse

import pytest
import httpx
from typer.testing import CliRunner

from hitl_cli.main import app


class TestOAuthDynamicRegistration:
    """Test OAuth 2.1 dynamic client registration"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_config_dir(self, tmp_path):
        """Create a temporary config directory with fully isolated auth files"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)

        token_file = config_dir / "token.json"
        oauth_token_file = config_dir / "oauth_token.json"
        oauth_client_file = config_dir / "oauth_client.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir), \
             patch('hitl_cli.auth.TOKEN_FILE', token_file), \
             patch('hitl_cli.auth.OAUTH_TOKEN_FILE', oauth_token_file), \
             patch('hitl_cli.auth.OAUTH_CLIENT_FILE', oauth_client_file):
            from hitl_cli.auth import delete_token, delete_oauth_tokens
            delete_token()
            delete_oauth_tokens()
            yield config_dir

    def test_oauth_dynamic_registration_success(self, runner, mock_config_dir):
        """Test successful dynamic client registration"""

        with patch('hitl_cli.main.is_logged_in', return_value=False):
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.main.OAuthDynamicClient') as mock_oauth_client_class:
                    mock_oauth_client = Mock()
                    mock_oauth_client.perform_dynamic_oauth_flow = AsyncMock(return_value=("fake-access-token", "Test Agent"))
                    mock_oauth_client_class.return_value = mock_oauth_client

                    with patch('hitl_cli.main.ensure_agent_keypair') as mock_ensure_keys:
                        mock_ensure_keys.return_value = ("public_key", "private_key")

                        result = runner.invoke(app, [
                            "login",
                            "--name", "Test Agent"
                        ])

                        assert result.exit_code == 0
                        assert "OAuth 2.1 dynamic authentication successful!" in result.output

                        # Verify OAuth client was created and flow was called
                        mock_oauth_client_class.assert_called_once()
                        mock_oauth_client.perform_dynamic_oauth_flow.assert_called_once_with("Test Agent")

                        # Verify keys were ensured
                        mock_ensure_keys.assert_called_once()

    def test_oauth_pkce_flow(self, runner, mock_config_dir):
        """Test OAuth 2.1 + PKCE authorization flow"""

        # Mock registered client
        client_data = {
            "client_id": "dynamic-client-123",
            "client_secret": "secret-456"
        }

        with patch('hitl_cli.auth.load_oauth_client', return_value=client_data):
            with patch('webbrowser.open') as mock_browser:
                with patch('http.server.HTTPServer') as mock_server:
                    # Mock the authorization code callback
                    mock_handler = Mock()
                    mock_handler.path = "/callback?code=auth-code-123&state=test-state"

                    mock_server_instance = Mock()
                    mock_server_instance.handle_request.return_value = None
                    mock_server.return_value = mock_server_instance

                    # Mock token exchange
                    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
                        token_response = {
                            "access_token": "oauth-bearer-token",
                            "token_type": "Bearer",
                            "expires_in": 3600,
                            "refresh_token": "refresh-token-123"
                        }

                        mock_response = Mock()
                        mock_response.status_code = 200
                        mock_response.json.return_value = token_response
                        mock_post.return_value = mock_response

                        from hitl_cli.auth import OAuthDynamicClient
                        client = OAuthDynamicClient()

                        # Test PKCE parameters generation
                        code_verifier = client._generate_code_verifier()
                        code_challenge = client._generate_code_challenge(code_verifier)

                        assert len(code_verifier) >= 43
                        assert len(code_verifier) <= 128
                        assert code_challenge != code_verifier

                        # Verify code challenge generation
                        expected_challenge = base64.urlsafe_b64encode(
                            hashlib.sha256(code_verifier.encode()).digest()
                        ).decode().rstrip('=')
                        assert code_challenge == expected_challenge

                        # Test token exchange (async)
                        import asyncio
                        asyncio.run(client._exchange_authorization_code(
                            client_id="dynamic-client-123",
                            client_secret="secret-456",
                            authorization_code="auth-code-123",
                            code_verifier="code-verifier-123",
                            agent_name="Test Agent"
                        ))

                        # Verify token exchange was called with correct headers
                        mock_post.assert_awaited_once()
                        call_args = mock_post.await_args
                        headers = call_args[1]["headers"]
                        assert headers["X-MCP-Agent-Name"] == "Test Agent"

    def test_oauth_bearer_token_storage(self, runner, mock_config_dir):
        """Test OAuth Bearer token storage and retrieval"""
        
        from hitl_cli.auth import save_oauth_token, load_oauth_token
        
        token_data = {
            "access_token": "oauth-bearer-token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "refresh-token-123",
            "expires_at": 1234567890 + 3600
        }
        
        # Test saving OAuth token
        save_oauth_token(token_data)
        
        # Test loading OAuth token
        loaded_token = load_oauth_token()
        assert loaded_token["access_token"] == "oauth-bearer-token"
        assert loaded_token["token_type"] == "Bearer"
        assert loaded_token["refresh_token"] == "refresh-token-123"

    def test_x_mcp_agent_name_header(self, runner, mock_config_dir):
        """Test X-MCP-Agent-Name header during token exchange"""

        agent_name = "My Custom Agent"

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "oauth-bearer-token",
                "token_type": "Bearer"
            }
            mock_post.return_value = mock_response

            from hitl_cli.auth import OAuthDynamicClient
            client = OAuthDynamicClient()

            # Mock the token exchange call (async)
            import asyncio
            asyncio.run(client._exchange_authorization_code(
                client_id="test-client-id",
                client_secret=None,
                authorization_code="auth-code-123",
                code_verifier="code-verifier-123",
                agent_name=agent_name
            ))

            # Verify X-MCP-Agent-Name header was included
            mock_post.assert_awaited_once()
            call_args = mock_post.await_args
            headers = call_args[1]["headers"]
            assert headers["X-MCP-Agent-Name"] == agent_name



class TestMCPOAuthIntegration:
    """Test MCP client integration with OAuth Bearer authentication"""

    @pytest.fixture
    def mock_oauth_token(self, tmp_path):
        """Mock OAuth token storage"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "oauth_token.json"
        
        token_data = {
            "access_token": "oauth-bearer-token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "expires_at": 1234567890 + 3600
        }
        
        token_file.write_text(json.dumps(token_data))
        
        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.OAUTH_TOKEN_FILE', token_file):
                yield token_data

    def test_mcp_client_oauth_auth(self, mock_oauth_token):
        """Test MCP client uses OAuth Bearer authentication"""

        from hitl_cli.mcp_client import MCPClient

        client = MCPClient()

        # Mock FastMCP Client with OAuth support
        with patch('hitl_cli.mcp_client.Client') as mock_fastmcp_client:
            mock_client_instance = AsyncMock()
            mock_fastmcp_client.return_value.__aenter__.return_value = mock_client_instance

            # Mock tool call result
            mock_result = Mock()
            mock_result.content = [Mock(text="Human response")]
            mock_client_instance.call_tool.return_value = mock_result

            # Test OAuth Bearer authentication
            import asyncio
            result = asyncio.run(client.request_human_input_oauth(
                "Test prompt",
                agent_name="Test Agent"
            ))

            assert result == "Human response"

            # Verify FastMCP Client was called with OAuth auth
            mock_fastmcp_client.assert_called_once()
            call_args = mock_fastmcp_client.call_args

            # Verify OAuth Bearer token was used
            auth_handler = call_args[1]['auth']
            assert hasattr(auth_handler, 'token')
            assert auth_handler.token == "oauth-bearer-token"

    def test_mcp_client_oauth_token_refresh(self):
        """Test MCP client handles OAuth token refresh"""

        # Mock expired token
        expired_token_data = {
            "access_token": "expired-oauth-token",
            "token_type": "Bearer",
            "expires_at": 1234567890 - 3600,  # Expired
            "refresh_token": "refresh-token-123"
        }

        with patch('hitl_cli.mcp_client.load_oauth_token', return_value=expired_token_data):
            with patch('hitl_cli.mcp_client.load_oauth_client', return_value={'client_id': 'test-client', 'client_secret': 'test-secret'}):
                with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
                    # Mock refresh token response
                    refresh_response = {
                        "access_token": "new-oauth-token",
                        "token_type": "Bearer",
                        "expires_in": 3600
                    }

                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = refresh_response
                    mock_post.return_value = mock_response

                    from hitl_cli.mcp_client import MCPClient
                    client = MCPClient()

                    # Test token refresh
                    import asyncio
                    token = asyncio.run(client._get_oauth_token())

                    assert token == "new-oauth-token"

                    # Verify refresh token was used
                    mock_post.assert_awaited_once()
                    call_args = mock_post.await_args
                    request_data = call_args[1]["data"]
                    assert request_data["grant_type"] == "refresh_token"
                    assert request_data["refresh_token"] == "refresh-token-123"


class TestOAuthSecurityFeatures:
    """Test OAuth security features and token management"""

    def test_pkce_code_challenge_generation(self):
        """Test PKCE code challenge generation follows RFC 7636"""
        
        from hitl_cli.auth import OAuthDynamicClient
        client = OAuthDynamicClient()
        
        # Test code verifier generation
        code_verifier = client._generate_code_verifier()
        
        # Verify length requirements (43-128 characters)
        assert 43 <= len(code_verifier) <= 128
        
        # Verify character set (unreserved characters)
        import re
        pattern = re.compile(r'^[A-Za-z0-9\-\._~]+$')
        assert pattern.match(code_verifier)
        
        # Test code challenge generation
        code_challenge = client._generate_code_challenge(code_verifier)
        
        # Verify SHA256 + base64url encoding
        expected = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        assert code_challenge == expected

    def test_state_parameter_validation(self):
        """Test OAuth state parameter generation and validation"""
        
        from hitl_cli.auth import OAuthDynamicClient
        client = OAuthDynamicClient()
        
        # Test state generation
        state = client._generate_state()
        
        # Verify length and randomness
        assert len(state) >= 32
        
        # Test multiple generations are different
        state2 = client._generate_state()
        assert state != state2

    def test_token_storage_security(self, tmp_path):
        """Test OAuth token storage security"""
        
        config_dir = tmp_path / ".config" / "hitl-cli"
        token_file = config_dir / "oauth_token.json"
        
        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.OAUTH_TOKEN_FILE', token_file):
                from hitl_cli.auth import save_oauth_token
                
                token_data = {
                    "access_token": "sensitive-oauth-token",
                    "refresh_token": "sensitive-refresh-token"
                }
                
                save_oauth_token(token_data)
                
                # Verify directory permissions (700)
                assert oct(config_dir.stat().st_mode)[-3:] == '700'
                
                # Verify file permissions (600)
                assert oct(token_file.stat().st_mode)[-3:] == '600'

    def test_token_expiry_handling(self):
        """Test OAuth token expiry detection and handling"""
        
        from hitl_cli.auth import is_oauth_token_expired
        import time
        
        # Test non-expired token
        valid_token = {
            "expires_at": int(time.time()) + 3600  # Expires in 1 hour
        }
        assert not is_oauth_token_expired(valid_token)
        
        # Test expired token
        expired_token = {
            "expires_at": int(time.time()) - 3600  # Expired 1 hour ago
        }
        assert is_oauth_token_expired(expired_token)
        
        # Test token without expiry (treat as expired for safety)
        no_expiry_token = {}
        assert is_oauth_token_expired(no_expiry_token)


class TestCLIFlags:
    """Test new CLI flags for dynamic OAuth"""

    @pytest.fixture
    def runner(self):
        return CliRunner()
