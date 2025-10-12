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
