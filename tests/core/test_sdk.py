"""
Tests for HITL SDK functionality

These tests validate:
1. SDK initialization
2. Authentication method detection
3. Request input functionality
4. Notification functionality
5. Task completion notifications
6. Agent management
7. Error handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from hitl_cli.sdk import HITL


class TestHITLSDK:
    """Test HITL SDK functionality"""

    @pytest.fixture
    def hitl_client(self):
        """Create a HITL SDK client for testing"""
        return HITL()

    def test_initialization(self, hitl_client):
        """Test that HITL client initializes correctly"""
        assert hitl_client is not None
        assert hasattr(hitl_client, '_mcp_client')
        assert hitl_client._mcp_client is not None

    @patch('hitl_cli.auth.is_using_api_key')
    @patch('hitl_cli.auth.is_using_oauth')
    def test_request_input_api_key_auth(self, mock_oauth, mock_api_key, hitl_client):
        """Test request_input with API key authentication"""
        mock_api_key.return_value = True
        mock_oauth.return_value = False

        with patch.object(hitl_client._mcp_client, 'request_human_input_api_key', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = "User response"

            import asyncio
            result = asyncio.run(hitl_client.request_input("Test prompt", ["Yes", "No"]))

            assert result == "User response"
            mock_request.assert_called_once_with(
                prompt="Test prompt",
                choices=["Yes", "No"],
                placeholder_text=None
            )

    @patch('hitl_cli.auth.is_using_api_key')
    @patch('hitl_cli.auth.is_using_oauth')
    def test_request_input_oauth_auth(self, mock_oauth, mock_api_key, hitl_client):
        """Test request_input with OAuth authentication"""
        mock_api_key.return_value = False
        mock_oauth.return_value = True

        with patch.object(hitl_client._mcp_client, 'request_human_input_oauth', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = "OAuth response"

            import asyncio
            result = asyncio.run(hitl_client.request_input("Test prompt", agent_name="Test Agent"))

            assert result == "OAuth response"
            mock_request.assert_called_once_with(
                prompt="Test prompt",
                choices=None,
                placeholder_text=None,
                agent_name="Test Agent"
            )

    @patch('hitl_cli.auth.is_using_api_key')
    @patch('hitl_cli.auth.is_using_oauth')
    def test_request_input_fallback_auth(self, mock_oauth, mock_api_key, hitl_client):
        """Test request_input with fallback authentication"""
        mock_api_key.return_value = False
        mock_oauth.return_value = False

        with patch.object(hitl_client._mcp_client, 'request_human_input', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = "Fallback response"

            import asyncio
            result = asyncio.run(hitl_client.request_input("Test prompt"))

            assert result == "Fallback response"
            mock_request.assert_called_once_with(
                prompt="Test prompt",
                choices=None,
                placeholder_text=None
            )

    @patch('hitl_cli.auth.is_using_api_key')
    def test_notify_completion_api_key_auth(self, mock_api_key, hitl_client):
        """Test notify_completion with API key authentication"""
        mock_api_key.return_value = True

        with patch.object(hitl_client._mcp_client, 'notify_task_completion_api_key', new_callable=AsyncMock) as mock_notify:
            mock_notify.return_value = "Task completed feedback"

            import asyncio
            result = asyncio.run(hitl_client.notify_completion("Task done"))

            assert result == "Task completed feedback"
            mock_notify.assert_called_once_with(summary="Task done")

    @patch('hitl_cli.auth.is_using_api_key')
    @patch('hitl_cli.auth.is_using_oauth')
    def test_notify_completion_oauth_auth(self, mock_oauth, mock_api_key, hitl_client):
        """Test notify_completion with OAuth authentication"""
        mock_api_key.return_value = False
        mock_oauth.return_value = True

        with patch.object(hitl_client._mcp_client, 'notify_task_completion_oauth', new_callable=AsyncMock) as mock_notify:
            mock_notify.return_value = "OAuth feedback"

            import asyncio
            result = asyncio.run(hitl_client.notify_completion("Task done", agent_name="Test Agent"))

            assert result == "OAuth feedback"
            mock_notify.assert_called_once_with(
                summary="Task done",
                agent_name="Test Agent"
            )

    @patch('hitl_cli.auth.is_using_api_key')
    def test_notify_api_key_auth(self, mock_api_key, hitl_client):
        """Test notify with API key authentication"""
        mock_api_key.return_value = True

        with patch.object(hitl_client._mcp_client, 'notify_human_api_key', new_callable=AsyncMock) as mock_notify:
            mock_notify.return_value = "Notification sent"

            import asyncio
            result = asyncio.run(hitl_client.notify("Hello world"))

            assert result == "Notification sent"
            mock_notify.assert_called_once_with(message="Hello world")

    @patch('hitl_cli.auth.is_using_oauth')
    @patch('hitl_cli.auth.is_using_api_key')
    def test_notify_oauth_auth(self, mock_api_key, mock_oauth, hitl_client):
        """Test notify with OAuth authentication"""
        mock_api_key.return_value = False
        mock_oauth.return_value = True

        with patch.object(hitl_client._mcp_client, 'notify_human_oauth', new_callable=AsyncMock) as mock_notify:
            mock_notify.return_value = "OAuth notification sent"

            import asyncio
            result = asyncio.run(hitl_client.notify("Hello world", agent_name="Test Agent"))

            assert result == "OAuth notification sent"
            mock_notify.assert_called_once_with(
                message="Hello world",
                agent_name="Test Agent"
            )

    def test_create_agent(self, hitl_client):
        """Test agent creation"""
        with patch.object(hitl_client._mcp_client, 'create_agent_for_mcp', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = "agent-123"

            import asyncio
            result = asyncio.run(hitl_client.create_agent("Test Agent"))

            assert result == "agent-123"
            mock_create.assert_called_once_with("Test Agent")

    def test_list_agents(self, hitl_client):
        """Test listing agents"""
        mock_agents = [
            {"id": "agent-1", "name": "Agent One"},
            {"id": "agent-2", "name": "Agent Two"}
        ]

        with patch('hitl_cli.api_client.ApiClient') as mock_api_client_class:
            mock_api_client = MagicMock()
            mock_api_client_class.return_value = mock_api_client
            mock_api_client.get = AsyncMock(return_value=mock_agents)

            import asyncio
            result = asyncio.run(hitl_client.list_agents())

            assert result == mock_agents
            mock_api_client.get.assert_called_once_with("/api/v1/agents")

    def test_request_input_error_handling(self, hitl_client):
        """Test error handling in request_input"""
        with patch('hitl_cli.auth.is_using_api_key', return_value=True):
            with patch.object(hitl_client._mcp_client, 'request_human_input_api_key', new_callable=AsyncMock) as mock_request:
                mock_request.side_effect = Exception("Network error")

                import asyncio
                with pytest.raises(Exception, match="Network error"):
                    asyncio.run(hitl_client.request_input("Test prompt"))

    def test_notify_completion_error_handling(self, hitl_client):
        """Test error handling in notify_completion"""
        with patch('hitl_cli.auth.is_using_api_key', return_value=True):
            with patch.object(hitl_client._mcp_client, 'notify_task_completion_api_key', new_callable=AsyncMock) as mock_notify:
                mock_notify.side_effect = Exception("Authentication failed")

                import asyncio
                with pytest.raises(Exception, match="Authentication failed"):
                    asyncio.run(hitl_client.notify_completion("Task done"))

    def test_notify_error_handling(self, hitl_client):
        """Test error handling in notify"""
        with patch('hitl_cli.auth.is_using_api_key', return_value=True):
            with patch.object(hitl_client._mcp_client, 'notify_human_api_key', new_callable=AsyncMock) as mock_notify:
                mock_notify.side_effect = Exception("Send failed")

                import asyncio
                with pytest.raises(Exception, match="Send failed"):
                    asyncio.run(hitl_client.notify("Hello world"))
