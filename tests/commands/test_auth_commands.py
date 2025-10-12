"""
Tests for CLI authentication commands (login, logout, agents)

These tests validate the CLI command behavior and user interactions.
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from hitl_cli.auth import save_token
from hitl_cli.main import app
from typer.testing import CliRunner


class TestLoginCommand:
    """Test the login CLI command"""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing"""
        return CliRunner()

    @pytest.fixture
    def mock_config_dir(self, tmp_path):
        """Create a temporary config directory"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)

        # Patch the config module to use temp directory
        with patch('hitl_cli.auth.CONFIG_DIR', config_dir), \
             patch('hitl_cli.auth.TOKEN_FILE', config_dir / "token.json"), \
             patch('hitl_cli.auth.OAUTH_TOKEN_FILE', config_dir / "oauth_token.json"):
            from hitl_cli.auth import delete_token, delete_oauth_tokens
            delete_token()
            delete_oauth_tokens()
            yield config_dir


    def test_login_flow_success(self, runner, mock_config_dir):
        """Test successful login flow"""

        with patch('hitl_cli.main.OAuthDynamicClient') as mock_oauth_client_cls, \
             patch('hitl_cli.main.ensure_agent_keypair', new_callable=AsyncMock) as mock_ensure_keys:
            inst = mock_oauth_client_cls.return_value
            inst.perform_dynamic_oauth_flow = AsyncMock(return_value=("fake-access-token", "HITL CLI Agent"))
            mock_ensure_keys.return_value = ("public_key", "private_key")

            # Run the login command
            result = runner.invoke(app, ["login", "--name", "Test Agent"])

            assert result.exit_code == 0
            assert "OAuth 2.1 dynamic authentication successful!" in result.output

            # Verify OAuth client was created and flow was called
            inst.perform_dynamic_oauth_flow.assert_awaited_once_with("Test Agent")

            # Verify keys were ensured
            mock_ensure_keys.assert_awaited_once()

    def test_login_already_logged_in(self, runner, mock_config_dir):
        """Test login when already logged in"""

        # Save a token first
        with patch('hitl_cli.auth.CONFIG_DIR', mock_config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', mock_config_dir / "token.json"):
                save_token("existing-token")

                result = runner.invoke(app, ["login"])

                assert result.exit_code == 0
                assert "Already logged in!" in result.output


class TestLogoutCommand:
    """Test the logout CLI command"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_logout_flow(self, runner, tmp_path):
        """Test logout flow"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)

        # Save a token first
        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', config_dir / "token.json"):
                save_token("test-token")

                result = runner.invoke(app, ["logout"])

                assert result.exit_code == 0
                assert "Logged out successfully!" in result.output

    def test_logout_not_logged_in(self, runner, tmp_path):
        """Test logout when not logged in"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', config_dir / "token.json"):
                result = runner.invoke(app, ["logout"])

                assert result.exit_code == 0
                assert "Not logged in." in result.output


class TestAgentCommands:
    """Test agent management CLI commands"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_auth(self, tmp_path):
        """Mock authentication state"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir), \
             patch('hitl_cli.auth.TOKEN_FILE', token_file):
            save_token("test-jwt-token")
            yield

    def test_agents_list_success(self, runner, mock_auth):
        """Test listing agents"""

        mock_agents = [
            {"id": "agent-1", "name": "Test Agent 1"},
            {"id": "agent-2", "name": "Test Agent 2"}
        ]

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_agents
            mock_get.return_value = mock_response

            result = runner.invoke(app, ["agents", "list"])

            assert result.exit_code == 0
            assert "Test Agent 1" in result.output
            assert "Test Agent 2" in result.output
            assert "agent-1" in result.output
            assert "agent-2" in result.output

    def test_agents_list_not_logged_in(self, runner):
        """Test listing agents when not logged in"""

        with patch('hitl_cli.auth.load_token', return_value=None):
            result = runner.invoke(app, ["agents", "list"])

            assert result.exit_code == 1
            assert "Not logged in" in result.output

    def test_agents_create_success(self, runner, mock_auth):
        """Test creating an agent"""

        new_agent = {"id": "new-agent-id", "name": "My New Agent"}

        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = new_agent
            mock_post.return_value = mock_response

            result = runner.invoke(app, ["agents", "create", "--name", "My New Agent"])

            assert result.exit_code == 0
            assert "Agent created successfully!" in result.output
            assert "ID: new-agent-id" in result.output
            assert "Name: My New Agent" in result.output


class TestRequestCommand:
    """Test the request CLI command"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_auth(self, tmp_path):
        """Mock authentication state"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir), \
             patch('hitl_cli.auth.TOKEN_FILE', token_file):
            save_token("test-jwt-token")
            yield

    def test_request_with_new_agent(self, runner, mock_auth):
        """Test making a request that creates a new agent"""

        with patch('hitl_cli.mcp_client.MCPClient.request_human_input', new_callable=AsyncMock) as mock_request_human_input:
            mock_request_human_input.return_value = "User approved"

            with patch('hitl_cli.auth.get_current_agent_id', return_value=None):
                result = runner.invoke(app, ["request", "--prompt", "Approve deployment?"])

                assert result.exit_code == 0
                assert "Sending request: Approve deployment?" in result.output
                assert "Waiting for human response..." in result.output
                assert "Human response received: User approved" in result.output

                mock_request_human_input.assert_awaited_once_with(
                    prompt='Approve deployment?',
                    choices=None,
                    placeholder_text=None,
                    agent_id=None
                )

    def test_request_with_existing_agent(self, runner, mock_auth):
        """Test making a request with an existing agent ID"""

        with patch('hitl_cli.mcp_client.MCPClient.request_human_input', new_callable=AsyncMock) as mock_request_human_input:
            mock_request_human_input.return_value = "User denied"

            with patch('hitl_cli.auth.get_current_agent_id', return_value="existing-agent-id"):
                result = runner.invoke(app, [
                    "request",
                    "--prompt", "Approve deployment?",
                    "--agent-id", "existing-agent-id"
                ])

                assert result.exit_code == 0
                assert "Human response received: User denied" in result.output

                mock_request_human_input.assert_awaited_once_with(
                    prompt='Approve deployment?',
                    choices=None,
                    placeholder_text=None,
                    agent_id='existing-agent-id'
                )

    def test_request_with_choices(self, runner, mock_auth):
        """Test making a request with multiple choice options"""

        with patch('hitl_cli.mcp_client.MCPClient.request_human_input', new_callable=AsyncMock) as mock_request_human_input:
            mock_request_human_input.return_value = "Yes"

            with patch('hitl_cli.auth.get_current_agent_id', return_value=None):
                result = runner.invoke(app, [
                    "request",
                    "--prompt", "Continue with operation?",
                    "--choice", "Yes",
                    "--choice", "No",
                    "--choice", "Maybe"
                ])

                assert result.exit_code == 0
                assert "Choices: ['Yes', 'No', 'Maybe']" in result.output
                assert "Human response received: Yes" in result.output

                mock_request_human_input.assert_awaited_once_with(
                    prompt='Continue with operation?',
                    choices=['Yes', 'No', 'Maybe'],
                    placeholder_text=None,
                    agent_id=None
                )
