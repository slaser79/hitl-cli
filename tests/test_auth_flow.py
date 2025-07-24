"""
Comprehensive tests for CLI authentication flow

These tests validate:
1. OAuth flow with Google
2. Token exchange with backend
3. Agent creation and binding
4. MCP request flow
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from hitl_cli.auth import is_logged_in, load_token, save_token
from hitl_cli.main import app
from typer.testing import CliRunner


class TestCLIAuthenticationFlow:
    """Test the complete CLI authentication flow"""

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
        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', config_dir / "token.json"):
                yield config_dir

    @pytest.fixture
    def mock_client_secret(self, tmp_path):
        """Create a mock client_secret_desktop.json file"""
        secret_file = tmp_path / "client_secret_desktop.json"
        secret_data = {
            "installed": {
                "client_id": "test-client-id.apps.googleusercontent.com",
                "client_secret": "test-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        secret_file.write_text(json.dumps(secret_data))

        with patch('hitl_cli.auth.CLIENT_SECRET_FILE', secret_file):
            yield secret_file

    def test_login_flow_success(self, runner, mock_config_dir, mock_client_secret):
        """Test successful login flow"""

        # Mock the OAuth flow
        mock_credentials = Mock()
        mock_credentials.id_token = "fake-google-id-token"

        with patch('hitl_cli.auth.InstalledAppFlow.from_client_secrets_file') as mock_flow_factory:
            mock_flow = Mock()
            mock_flow.run_local_server.return_value = mock_credentials
            mock_flow_factory.return_value = mock_flow

            # Mock the token exchange
            with patch('httpx.AsyncClient.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"access_token": "fake-jwt-token"}
                mock_post.return_value = mock_response

                # Run the login command
                result = runner.invoke(app, ["login"])

                assert result.exit_code == 0
                assert "Login successful!" in result.output

                # Verify OAuth flow was called
                mock_flow.run_local_server.assert_called_once_with(port=0)

                # Verify token exchange was called
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                assert call_args[0][0] == "http://127.0.0.1:8000/api/v1/auth/google"
                assert call_args[1]["json"]["id_token"] == "fake-google-id-token"

    def test_login_already_logged_in(self, runner, mock_config_dir):
        """Test login when already logged in"""

        # Save a token first
        with patch('hitl_cli.auth.CONFIG_DIR', mock_config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', mock_config_dir / "token.json"):
                save_token("existing-token")

                result = runner.invoke(app, ["login"])

                assert result.exit_code == 0
                assert "Already logged in!" in result.output

    def test_logout_flow(self, runner, mock_config_dir):
        """Test logout flow"""

        # Save a token first
        with patch('hitl_cli.auth.CONFIG_DIR', mock_config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', mock_config_dir / "token.json"):
                save_token("test-token")
                assert is_logged_in()

                result = runner.invoke(app, ["logout"])

                assert result.exit_code == 0
                assert "Logged out successfully!" in result.output
                assert not is_logged_in()

    def test_logout_not_logged_in(self, runner, mock_config_dir):
        """Test logout when not logged in"""

        with patch('hitl_cli.auth.CONFIG_DIR', mock_config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', mock_config_dir / "token.json"):
                result = runner.invoke(app, ["logout"])

                assert result.exit_code == 0
                assert "Not logged in." in result.output


class TestAgentManagement:
    """Test agent creation and management"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_auth(self, tmp_path):
        """Mock authentication state"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                with patch('hitl_cli.api_client.CONFIG_DIR', config_dir):
                    with patch('hitl_cli.api_client.TOKEN_FILE', token_file):
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


class TestMCPRequestFlow:
    """Test the MCP request flow"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_auth(self, tmp_path):
        """Mock authentication state"""
        config_dir = tmp_path / ".config" / "hitl-cli"
        config_dir.mkdir(parents=True)
        token_file = config_dir / "token.json"

        with patch('hitl_cli.auth.CONFIG_DIR', config_dir):
            with patch('hitl_cli.auth.TOKEN_FILE', token_file):
                with patch('hitl_cli.api_client.CONFIG_DIR', config_dir):
                    with patch('hitl_cli.api_client.TOKEN_FILE', token_file):
                        with patch('hitl_cli.mcp_client.CONFIG_DIR', config_dir):
                            with patch('hitl_cli.mcp_client.TOKEN_FILE', token_file):
                                save_token("test-jwt-token")
                                yield

    def test_request_with_new_agent(self, runner, mock_auth):
        """Test making a request that creates a new agent"""

        # Mock OAuth flow for MCP token
        mock_credentials = Mock()
        mock_credentials.id_token = "fake-google-id-token"

        with patch('hitl_cli.mcp_client.InstalledAppFlow.from_client_secrets_file') as mock_flow_factory:
            mock_flow = Mock()
            mock_flow.run_local_server.return_value = mock_credentials
            mock_flow_factory.return_value = mock_flow

            # Mock client secret file
            with patch('hitl_cli.mcp_client.CLIENT_SECRET_FILE', Path("fake-secret.json")):
                with patch('hitl_cli.mcp_client.CLIENT_SECRET_FILE.exists', return_value=True):

                    # Mock the async HTTP calls
                    with patch('httpx.AsyncClient') as mock_client_class:
                        mock_client = MagicMock()
                        mock_client_class.return_value.__aenter__.return_value = mock_client

                        # Mock agent creation
                        agent_response = Mock()
                        agent_response.status_code = 200
                        agent_response.json.return_value = {"id": "new-agent-id", "name": "hitl-cli-12345678"}

                        # Mock MCP token exchange
                        mcp_token_response = Mock()
                        mcp_token_response.status_code = 200
                        mcp_token_response.json.return_value = {"access_token": "mcp-jwt-token"}

                        # Mock MCP tool call
                        mcp_call_response = Mock()
                        mcp_call_response.status_code = 200
                        mcp_call_response.json.return_value = {"result": "User approved"}

                        # Set up the mock responses in order
                        mock_client.post.side_effect = [agent_response, mcp_token_response, mcp_call_response]

                        result = runner.invoke(app, ["request", "--prompt", "Approve deployment?"])

                        assert result.exit_code == 0
                        assert "Sending request: Approve deployment?" in result.output
                        assert "Waiting for human response..." in result.output
                        assert "Human response received: User approved" in result.output

    def test_request_with_existing_agent(self, runner, mock_auth):
        """Test making a request with an existing agent ID"""

        # Mock OAuth flow for MCP token
        mock_credentials = Mock()
        mock_credentials.id_token = "fake-google-id-token"

        with patch('hitl_cli.mcp_client.InstalledAppFlow.from_client_secrets_file') as mock_flow_factory:
            mock_flow = Mock()
            mock_flow.run_local_server.return_value = mock_credentials
            mock_flow_factory.return_value = mock_flow

            # Mock client secret file
            with patch('hitl_cli.mcp_client.CLIENT_SECRET_FILE', Path("fake-secret.json")):
                with patch('hitl_cli.mcp_client.CLIENT_SECRET_FILE.exists', return_value=True):

                    # Mock the async HTTP calls
                    with patch('httpx.AsyncClient') as mock_client_class:
                        mock_client = MagicMock()
                        mock_client_class.return_value.__aenter__.return_value = mock_client

                        # Mock MCP token exchange
                        mcp_token_response = Mock()
                        mcp_token_response.status_code = 200
                        mcp_token_response.json.return_value = {"access_token": "mcp-jwt-token"}

                        # Mock MCP tool call
                        mcp_call_response = Mock()
                        mcp_call_response.status_code = 200
                        mcp_call_response.json.return_value = {"result": "User denied"}

                        mock_client.post.side_effect = [mcp_token_response, mcp_call_response]

                        result = runner.invoke(app, [
                            "request",
                            "--prompt", "Approve deployment?",
                            "--agent-id", "existing-agent-id"
                        ])

                        assert result.exit_code == 0
                        assert "Human response received: User denied" in result.output

    def test_request_with_choices(self, runner, mock_auth):
        """Test making a request with multiple choice options"""

        # Mock OAuth flow for MCP token
        mock_credentials = Mock()
        mock_credentials.id_token = "fake-google-id-token"

        with patch('hitl_cli.mcp_client.InstalledAppFlow.from_client_secrets_file') as mock_flow_factory:
            mock_flow = Mock()
            mock_flow.run_local_server.return_value = mock_credentials
            mock_flow_factory.return_value = mock_flow

            # Mock client secret file
            with patch('hitl_cli.mcp_client.CLIENT_SECRET_FILE', Path("fake-secret.json")):
                with patch('hitl_cli.mcp_client.CLIENT_SECRET_FILE.exists', return_value=True):

                    # Mock the async HTTP calls
                    with patch('httpx.AsyncClient') as mock_client_class:
                        mock_client = MagicMock()
                        mock_client_class.return_value.__aenter__.return_value = mock_client

                        # Mock responses
                        agent_response = Mock()
                        agent_response.status_code = 200
                        agent_response.json.return_value = {"id": "new-agent-id"}

                        mcp_token_response = Mock()
                        mcp_token_response.status_code = 200
                        mcp_token_response.json.return_value = {"access_token": "mcp-jwt-token"}

                        mcp_call_response = Mock()
                        mcp_call_response.status_code = 200
                        mcp_call_response.json.return_value = {"result": "Yes"}

                        mock_client.post.side_effect = [agent_response, mcp_token_response, mcp_call_response]

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
