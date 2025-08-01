"""
Tests for the notify command functionality

These tests validate:
1. Command argument parsing and validation
2. MCP tool call integration with notify_human tool
3. Authentication method selection (OAuth 2.1 vs traditional JWT)
4. Error handling scenarios (network failures, authentication errors)
5. CLI output formatting and user feedback
6. Integration with mock MCP server responses
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from hitl_cli.main import app


class TestNotifyCommandArguments:
    """Test notify command argument parsing and validation"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_notify_command_exists(self):
        """Test that notify command is available in CLI"""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "notify" in result.stdout

    def test_notify_command_requires_message_argument(self):
        """Test that notify command requires a message argument"""
        result = self.runner.invoke(app, ["notify"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_notify_command_accepts_message_argument(self):
        """Test that notify command accepts message argument"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Mock the async call_tool method
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            # Mock auth checks
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", "Test notification"])
                    
                    # Should not fail due to missing argument
                    assert "Missing option" not in result.output
                    assert "required" not in result.output.lower()

    def test_notify_command_handles_empty_message(self):
        """Test that notify command handles empty message appropriately"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", ""])
                    
                    # Should accept empty message (server can handle validation)
                    mock_client.call_tool.assert_called_once()

    def test_notify_command_handles_long_message(self):
        """Test that notify command handles long messages"""
        long_message = "A" * 1000  # 1000 character message
        
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", long_message])
                    
                    # Should accept long message
                    mock_client.call_tool.assert_called_once()
                    call_args = mock_client.call_tool.call_args
                    assert call_args[0][1]["message"] == long_message

    def test_notify_command_handles_special_characters(self):
        """Test that notify command handles special characters in message"""
        special_message = "Test with emoji 🎉 and special chars: !@#$%^&*()"
        
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", special_message])
                    
                    # Should accept special characters
                    mock_client.call_tool.assert_called_once()
                    call_args = mock_client.call_tool.call_args
                    assert call_args[0][1]["message"] == special_message


class TestNotifyCommandMCPIntegration:
    """Test MCP tool call integration with notify_human tool"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_notify_calls_correct_mcp_tool(self):
        """Test that notify command calls the notify_human MCP tool"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", "Test message"])
                    
                    # Verify correct MCP tool was called
                    mock_client.call_tool.assert_called_once()
                    call_args = mock_client.call_tool.call_args
                    assert call_args[0][0] == "notify_human"  # tool name
                    assert call_args[0][1]["message"] == "Test message"  # arguments

    def test_notify_passes_correct_arguments_to_mcp_tool(self):
        """Test that notify command passes correct arguments to MCP tool"""
        test_message = "Important notification message"
        
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", test_message])
                    
                    # Verify arguments structure
                    mock_client.call_tool.assert_called_once()
                    call_args = mock_client.call_tool.call_args
                    arguments = call_args[0][1]
                    
                    assert isinstance(arguments, dict)
                    assert "message" in arguments
                    assert arguments["message"] == test_message

    def test_notify_handles_mcp_tool_response(self):
        """Test that notify command handles MCP tool response correctly"""
        expected_response = "Notification sent successfully."
        
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value=expected_response)
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", "Test"])
                    
                    # Verify response is displayed to user
                    assert result.exit_code == 0
                    assert expected_response in result.stdout


class TestNotifyCommandAuthentication:
    """Test authentication method selection (OAuth 2.1 vs traditional JWT)"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_notify_uses_oauth_when_available(self):
        """Test that notify command uses OAuth Bearer authentication when available"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            # Mock OAuth authentication
            with patch('hitl_cli.main.is_using_oauth', return_value=True):
                result = self.runner.invoke(app, ["notify", "--message", "Test"])
                
                # Verify MCP client was called (OAuth method doesn't need agent_id parameter)
                mock_client.call_tool.assert_called_once()
                call_args = mock_client.call_tool.call_args
                
                # For OAuth, agent_id should be None or not passed as third parameter
                assert len(call_args[0]) == 2 or call_args[0][2] is None

    def test_notify_uses_traditional_jwt_when_oauth_not_available(self):
        """Test that notify command uses traditional JWT authentication when OAuth not available"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            # Mock traditional JWT authentication
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.main.get_current_agent_id', return_value="test-agent-id"):
                    result = self.runner.invoke(app, ["notify", "--message", "Test"])
                    
                    # Verify MCP client was called with agent_id for traditional auth
                    mock_client.call_tool.assert_called_once()
                    call_args = mock_client.call_tool.call_args
                    
                    # For traditional JWT, agent_id should be passed as third parameter
                    assert len(call_args[0]) == 3
                    assert call_args[0][2] == "test-agent-id"

    def test_notify_creates_temp_agent_when_no_agent_id_available(self):
        """Test that notify command handles missing agent ID gracefully"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            # Mock traditional JWT authentication with no agent ID
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value=None):
                    result = self.runner.invoke(app, ["notify", "--message", "Test"])
                    
                    # Should still work - MCPClient handles creating temp agent
                    mock_client.call_tool.assert_called_once()


class TestNotifyCommandErrorHandling:
    """Test error handling scenarios (network failures, authentication errors)"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_notify_handles_network_errors(self):
        """Test that notify command handles network errors gracefully"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(side_effect=Exception("Network connection failed"))
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", "Test"])
                    
                    # Should exit with error code
                    assert result.exit_code == 1
                    assert "Network connection failed" in result.output

    def test_notify_handles_authentication_errors(self):
        """Test that notify command handles authentication errors gracefully"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(side_effect=Exception("Authentication required"))
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", "Test"])
                    
                    # Should exit with error code and show helpful message
                    assert result.exit_code == 1
                    assert "Authentication required" in result.output

    def test_notify_handles_mcp_server_errors(self):
        """Test that notify command handles MCP server errors gracefully"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(side_effect=Exception("MCP tool call failed: 500 - Internal Server Error"))
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", "Test"])
                    
                    # Should exit with error code and show server error
                    assert result.exit_code == 1
                    assert "MCP tool call failed" in result.output

    def test_notify_handles_timeout_errors(self):
        """Test that notify command handles timeout errors gracefully"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(side_effect=asyncio.TimeoutError("Request timed out"))
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", "Test"])
                    
                    # Should exit with error code and show timeout message
                    assert result.exit_code == 1
                    assert "timed out" in result.output.lower() or "timeout" in result.output.lower()


class TestNotifyCommandOutput:
    """Test CLI output formatting and user feedback"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_notify_displays_success_message(self):
        """Test that notify command displays success message"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", "Test message"])
                    
                    # Should display success and exit cleanly
                    assert result.exit_code == 0
                    assert "Notification sent." in result.output

    def test_notify_shows_message_being_sent(self):
        """Test that notify command shows the message being sent"""
        test_message = "Important notification"
        
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", test_message])
                    
                    # Should show the message being sent
                    assert result.exit_code == 0
                    assert test_message in result.output

    def test_notify_exits_immediately_after_success(self):
        """Test that notify command exits immediately after successful notification"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent.")
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="test-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", "Test"])
                    
                    # Should exit immediately with success code
                    assert result.exit_code == 0
                    # Should not contain any "waiting" or blocking messages
                    assert "waiting" not in result.output.lower()
                    assert "blocking" not in result.output.lower()


class TestNotifyCommandIntegration:
    """Integration tests with mock MCP server responses"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_notify_end_to_end_oauth_flow(self):
        """Test complete notify flow with OAuth authentication"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent to mobile device.")
            
            # Mock OAuth flow
            with patch('hitl_cli.main.is_using_oauth', return_value=True):
                result = self.runner.invoke(app, ["notify", "--message", "Integration test message"])
                
                # Verify complete flow
                assert result.exit_code == 0
                assert "Integration test message" in result.output
                assert "Notification sent to mobile device." in result.output
                
                # Verify MCP tool call
                mock_client.call_tool.assert_called_once()
                call_args = mock_client.call_tool.call_args
                assert call_args[0][0] == "notify_human"
                assert call_args[0][1]["message"] == "Integration test message"

    def test_notify_end_to_end_jwt_flow(self):
        """Test complete notify flow with JWT authentication"""
        with patch('hitl_cli.main.MCPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.call_tool = AsyncMock(return_value="Notification sent to mobile device.")
            
            # Mock JWT flow
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.main.get_current_agent_id', return_value="jwt-agent-123"):
                    result = self.runner.invoke(app, ["notify", "--message", "JWT integration test"])
                    
                    # Verify complete flow
                    assert result.exit_code == 0
                    assert "JWT integration test" in result.output
                    assert "Notification sent to mobile device." in result.output
                    
                    # Verify MCP tool call with agent ID
                    mock_client.call_tool.assert_called_once()
                    call_args = mock_client.call_tool.call_args
                    assert call_args[0][0] == "notify_human"
                    assert call_args[0][1]["message"] == "JWT integration test"
                    assert call_args[0][2] == "jwt-agent-123"

    def test_notify_with_real_mcp_client_initialization(self):
        """Test notify command with real MCPClient initialization (mocked network calls)"""
        test_message = "Real client test"
        
        # Mock only the network calls, let MCPClient initialize normally
        with patch('hitl_cli.mcp_client.MCPClient.call_tool') as mock_call_tool:
            mock_call_tool.return_value = AsyncMock(return_value="Real notification sent.")()
            
            with patch('hitl_cli.main.is_using_oauth', return_value=False):
                with patch('hitl_cli.auth.get_current_agent_id', return_value="real-agent"):
                    result = self.runner.invoke(app, ["notify", "--message", test_message])
                    
                    # Should work with real client initialization
                    assert result.exit_code == 0
                    assert test_message in result.output