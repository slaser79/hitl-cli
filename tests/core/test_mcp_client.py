"""
Tests for MCP Client functionality

These tests validate:
1. Google ID Token caching and persistence
2. JWT decoding robustness
3. Agent ID validation
4. Error handling and timeout scenarios
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from hitl_cli.mcp_client import MCPClient


class TestMCPClientTokenManagement:
    """Test MCP Client token management and caching"""

    @pytest.fixture
    def mock_config_dir(self, tmp_path):
        """Create a temporary config directory"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                yield config_dir, token_file

    def test_get_mcp_token_deprecated_raises(self, mock_config_dir):
        """Test that get_mcp_token raises exception as it's deprecated"""
        config_dir, token_file = mock_config_dir

        client = MCPClient()

        import pytest
        with pytest.raises(Exception):
            import asyncio
            asyncio.run(client.get_mcp_token("any-agent"))


class TestMCPClientErrorHandling:
    """Test MCP Client error handling"""

    def test_get_mcp_token_handles_auth_failure(self):
        """Test that get_mcp_token handles authentication failures gracefully"""
        client = MCPClient()

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            # Mock authentication failure
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Invalid token"

            # Make the post method return a coroutine
            async def mock_post(*args, **kwargs):
                return mock_response
            mock_client.post = mock_post

            # Call get_mcp_token and expect exception
            import asyncio
            with pytest.raises(Exception) as exc_info:
                asyncio.run(client.get_mcp_token("test-agent-id"))

            assert "Traditional OAuth flow is no longer supported" in str(exc_info.value)

    def test_get_mcp_token_handles_network_errors(self):
        """Test that get_mcp_token handles network errors gracefully"""
        client = MCPClient()

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock network error
            mock_client.post.side_effect = Exception("Network error")

            # Call get_mcp_token and expect exception
            import asyncio
            with pytest.raises(Exception) as exc_info:
                asyncio.run(client.get_mcp_token("test-agent-id"))

            assert "Traditional OAuth flow is no longer supported" in str(exc_info.value)

    def test_request_human_input_validates_agent_id(self):
        """Test that request_human_input validates agent ID exists"""
        client = MCPClient()

        # Mock agent validation - should fail for invalid agent
        with patch.object(client, 'validate_agent_exists', return_value=False):
            import asyncio
            with pytest.raises(Exception) as exc_info:
                asyncio.run(client.request_human_input("Test prompt", agent_id="invalid-agent-id"))

            assert "Agent does not exist" in str(exc_info.value)

    def test_request_human_input_proceeds_with_valid_agent_id(self):
        """Test that request_human_input proceeds when agent ID is valid"""
        client = MCPClient()

        # Mock agent validation - should succeed for valid agent
        with patch.object(client, 'validate_agent_exists', return_value=True):
            with patch.object(client, 'call_tool', return_value="Success") as mock_call:
                import asyncio
                result = asyncio.run(client.request_human_input("Test prompt", agent_id="valid-agent-id"))

                # Verify validation was called
                client.validate_agent_exists.assert_called_once_with("valid-agent-id")

                # Verify tool was called with valid agent
                mock_call.assert_called_once()
                assert mock_call.call_args[0][2] == "valid-agent-id"  # agent_id parameter

                assert result == "Success"

    def test_request_human_input_creates_temp_agent_when_none_specified(self):
        """Test that request_human_input creates temporary agent when none specified"""
        client = MCPClient()

        # Mock get_current_agent_id to return None
        with patch('hitl_cli.mcp_client.get_current_agent_id', return_value=None):
            with patch.object(client, 'create_agent_for_mcp', return_value="temp-agent-id") as mock_create:
                with patch.object(client, 'call_tool', return_value="Success") as mock_call:
                    import asyncio
                    asyncio.run(client.request_human_input("Test prompt"))

                    # Verify temporary agent was created
                    mock_create.assert_called_once()
                    agent_name = mock_create.call_args[0][0]
                    assert agent_name.startswith("hitl-cli-")

                    # Verify tool was called with temp agent
                    mock_call.assert_called_once()
                    assert mock_call.call_args[0][2] == "temp-agent-id"  # agent_id parameter

    def test_validate_agent_exists_returns_true_for_valid_agent(self):
        """Test that validate_agent_exists returns True for valid agent"""
        client = MCPClient()

        # Mock API client to return agent list
        mock_agents = [
            {"id": "agent-1", "name": "Test Agent 1"},
            {"id": "agent-2", "name": "Test Agent 2"}
        ]

        with patch('hitl_cli.mcp_client.ApiClient') as mock_api_client_class:
            mock_api_client = MagicMock()
            mock_api_client_class.return_value = mock_api_client

            # Mock get method to return agents
            async def mock_get(path):
                return mock_agents
            mock_api_client.get = mock_get

            import asyncio
            result = asyncio.run(client.validate_agent_exists("agent-1"))

            assert result is True

    def test_validate_agent_exists_returns_false_for_invalid_agent(self):
        """Test that validate_agent_exists returns False for invalid agent"""
        client = MCPClient()

        # Mock API client to return agent list
        mock_agents = [
            {"id": "agent-1", "name": "Test Agent 1"},
            {"id": "agent-2", "name": "Test Agent 2"}
        ]

        with patch('hitl_cli.mcp_client.ApiClient') as mock_api_client_class:
            mock_api_client = MagicMock()
            mock_api_client_class.return_value = mock_api_client

            # Mock get method to return agents
            async def mock_get(path):
                return mock_agents
            mock_api_client.get = mock_get

            import asyncio
            result = asyncio.run(client.validate_agent_exists("agent-3"))

            assert result is False

    def test_validate_agent_exists_returns_false_on_api_error(self):
        """Test that validate_agent_exists returns False when API call fails"""
        client = MCPClient()

        with patch('hitl_cli.mcp_client.ApiClient') as mock_api_client_class:
            mock_api_client = MagicMock()
            mock_api_client_class.return_value = mock_api_client

            # Mock get method to raise exception
            async def mock_get(path):
                raise Exception("API error")
            mock_api_client.get = mock_get

            import asyncio
            result = asyncio.run(client.validate_agent_exists("agent-1"))

            assert result is False


class TestOAuthTokenRefresh:
    """Test OAuth token refresh functionality"""

    @pytest.mark.asyncio
    async def test_get_oauth_token_raises_when_expired_without_refresh_token(self):
        """Test that _get_oauth_token raises exception when token expired and no refresh token"""
        client = MCPClient()

        # Mock expired token without refresh token
        mock_token_data = {
            'access_token': 'expired_token',
            'expires_at': 0  # Expired timestamp
            # No refresh_token field
        }

        with patch('hitl_cli.mcp_client.load_oauth_token', return_value=mock_token_data):
            with patch('hitl_cli.mcp_client.is_oauth_token_expired', return_value=True):
                with pytest.raises(Exception) as exc_info:
                    await client._get_oauth_token()

                assert "expired and no refresh token is available" in str(exc_info.value)
                assert "hitl-cli login" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_oauth_token_refreshes_expired_token_successfully(self):
        """Test that _get_oauth_token successfully refreshes an expired token"""
        client = MCPClient()

        # Mock expired token with refresh token
        mock_token_data = {
            'access_token': 'old_expired_token',
            'refresh_token': 'valid_refresh_token',
            'expires_at': 0  # Expired timestamp
        }

        mock_client_data = {
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret'
        }

        mock_new_token_data = {
            'access_token': 'new_fresh_token',
            'expires_in': 3600,
            'expires_at': 9999999999
        }

        with patch('hitl_cli.mcp_client.load_oauth_token', return_value=mock_token_data):
            with patch('hitl_cli.mcp_client.is_oauth_token_expired', return_value=True):
                with patch('hitl_cli.mcp_client.load_oauth_client', return_value=mock_client_data):
                    with patch('hitl_cli.mcp_client.refresh_oauth_token', return_value=mock_new_token_data) as mock_refresh:
                        with patch('hitl_cli.mcp_client.save_oauth_token') as mock_save:
                            result = await client._get_oauth_token()

                            # Verify refresh was called
                            mock_refresh.assert_awaited_once_with(
                                'valid_refresh_token',
                                'test_client_id',
                                'test_client_secret'
                            )

                            # Verify new token was saved
                            mock_save.assert_called_once()

                            # Verify new token was returned
                            assert result == 'new_fresh_token'

    @pytest.mark.asyncio
    async def test_get_oauth_token_raises_when_refresh_fails(self):
        """Test that _get_oauth_token raises exception when token refresh fails"""
        client = MCPClient()

        # Mock expired token with refresh token
        mock_token_data = {
            'access_token': 'old_expired_token',
            'refresh_token': 'invalid_refresh_token',
            'expires_at': 0
        }

        mock_client_data = {
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret'
        }

        with patch('hitl_cli.mcp_client.load_oauth_token', return_value=mock_token_data):
            with patch('hitl_cli.mcp_client.is_oauth_token_expired', return_value=True):
                with patch('hitl_cli.mcp_client.load_oauth_client', return_value=mock_client_data):
                    with patch('hitl_cli.mcp_client.refresh_oauth_token', side_effect=Exception("Invalid refresh token")):
                        with pytest.raises(Exception) as exc_info:
                            await client._get_oauth_token()

                        assert "Failed to refresh OAuth token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_oauth_token_raises_when_client_data_missing(self):
        """Test that _get_oauth_token raises exception when OAuth client data not found"""
        client = MCPClient()

        # Mock expired token with refresh token
        mock_token_data = {
            'access_token': 'old_expired_token',
            'refresh_token': 'valid_refresh_token',
            'expires_at': 0
        }

        with patch('hitl_cli.mcp_client.load_oauth_token', return_value=mock_token_data):
            with patch('hitl_cli.mcp_client.is_oauth_token_expired', return_value=True):
                with patch('hitl_cli.mcp_client.load_oauth_client', return_value=None):
                    with pytest.raises(Exception) as exc_info:
                        await client._get_oauth_token()

                    assert "OAuth client data not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_oauth_token_returns_valid_token_without_refresh(self):
        """Test that _get_oauth_token returns valid token without refresh attempt"""
        client = MCPClient()

        # Mock valid token (not expired)
        mock_token_data = {
            'access_token': 'valid_token',
            'refresh_token': 'refresh_token',
            'expires_at': 9999999999  # Far future
        }

        with patch('hitl_cli.mcp_client.load_oauth_token', return_value=mock_token_data):
            with patch('hitl_cli.mcp_client.is_oauth_token_expired', return_value=False):
                result = await client._get_oauth_token()

                # Should return existing token without refresh
                assert result == 'valid_token'

    @pytest.mark.asyncio
    async def test_get_oauth_token_preserves_refresh_token_when_not_returned(self):
        """Test that _get_oauth_token preserves refresh token if backend doesn't return it"""
        client = MCPClient()

        # Mock expired token with refresh token
        mock_token_data = {
            'access_token': 'old_expired_token',
            'refresh_token': 'original_refresh_token',
            'expires_at': 0
        }

        mock_client_data = {
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret'
        }

        # New token data WITHOUT refresh_token
        mock_new_token_data = {
            'access_token': 'new_fresh_token',
            'expires_in': 3600,
            'expires_at': 9999999999
            # No refresh_token
        }

        with patch('hitl_cli.mcp_client.load_oauth_token', return_value=mock_token_data):
            with patch('hitl_cli.mcp_client.is_oauth_token_expired', return_value=True):
                with patch('hitl_cli.mcp_client.load_oauth_client', return_value=mock_client_data):
                    with patch('hitl_cli.mcp_client.refresh_oauth_token', return_value=mock_new_token_data):
                        with patch('hitl_cli.mcp_client.save_oauth_token') as mock_save:
                            await client._get_oauth_token()

                            # Verify saved token includes preserved refresh token
                            saved_token = mock_save.call_args[0][0]
                            assert saved_token['refresh_token'] == 'original_refresh_token'


class TestJWTDecoding:
    """Test JWT token decoding functionality"""

    def test_get_current_agent_id_handles_malformed_jwt(self):
        """Test that get_current_agent_id handles malformed JWT tokens gracefully"""
        from hitl_cli.auth import get_current_agent_id

        # Test with malformed JWT (not 3 parts)
        with patch('hitl_cli.auth.get_current_token', return_value="malformed.jwt"):
            result = get_current_agent_id()
            assert result is None

    def test_get_current_agent_id_handles_invalid_base64(self):
        """Test that get_current_agent_id handles invalid base64 encoding"""
        from hitl_cli.auth import get_current_agent_id

        # Test with invalid base64 in payload
        with patch('hitl_cli.auth.get_current_token', return_value="header.invalid_base64.signature"):
            result = get_current_agent_id()
            assert result is None

    def test_get_current_agent_id_handles_invalid_json(self):
        """Test that get_current_agent_id handles invalid JSON in payload"""
        # Create a JWT with invalid JSON payload
        import base64

        from hitl_cli.auth import get_current_agent_id
        invalid_json = "not_json_data"
        encoded_payload = base64.b64encode(invalid_json.encode()).decode()
        jwt_token = f"header.{encoded_payload}.signature"

        with patch('hitl_cli.auth.get_current_token', return_value=jwt_token):
            result = get_current_agent_id()
            assert result is None

    def test_get_current_agent_id_returns_agent_id_when_valid(self):
        """Test that get_current_agent_id returns agent ID for valid JWT"""
        # Create a valid JWT token using PyJWT library
        import jwt
        from hitl_cli.auth import get_current_agent_id
        payload = {"agent_id": "test-agent-123", "sub": "user@example.com", "exp": 9999999999}
        jwt_token = jwt.encode(payload, "secret", algorithm="HS256")

        with patch('hitl_cli.auth.get_current_oauth_token', return_value=None):
            with patch('hitl_cli.auth.get_current_token', return_value=jwt_token):
                result = get_current_agent_id()
                assert result == "test-agent-123"

    def test_get_current_agent_id_uses_jwt_library(self):
        """Test that get_current_agent_id uses PyJWT library for robust decoding"""
        # Create a real JWT token with PyJWT
        import jwt
        from hitl_cli.auth import get_current_agent_id
        payload = {"agent_id": "test-agent-456", "sub": "user@example.com", "exp": 9999999999}
        jwt_token = jwt.encode(payload, "secret", algorithm="HS256")

        with patch('hitl_cli.auth.get_current_token', return_value=jwt_token):
            # Mock jwt.decode to return our payload
            with patch('hitl_cli.auth.jwt.decode', return_value=payload) as mock_decode:
                result = get_current_agent_id()

                # Verify PyJWT was used for decoding
                mock_decode.assert_called_once()

                # Verify correct agent ID was returned
                assert result == "test-agent-456"
