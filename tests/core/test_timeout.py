from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hitl_cli.api_client import ApiClient


@pytest.mark.asyncio
async def test_request_human_input_timeout():
    """Test that request_human_input uses 900s timeout"""
    client = ApiClient()
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_instance

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "approved"}
        mock_instance.post.return_value = mock_response

        with patch.object(ApiClient, '_get_headers', return_value={}):
            await client.request_human_input("test prompt")

        # Verify httpx.AsyncClient was called with timeout=900.0
        mock_client_class.assert_called_with(timeout=900.0)

@pytest.mark.asyncio
async def test_notify_task_completion_timeout():
    """Test that notify_task_completion uses 900s timeout"""
    client = ApiClient()
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_instance

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "acknowledged"}
        mock_instance.post.return_value = mock_response

        with patch.object(ApiClient, '_get_headers', return_value={}):
            await client.notify_task_completion("task done")

        # Verify httpx.AsyncClient was called with timeout=900.0
        mock_client_class.assert_called_with(timeout=900.0)

@pytest.mark.asyncio
async def test_notify_human_timeout():
    """Test that notify_human uses 900s timeout"""
    client = ApiClient()
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_instance

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "sent"}
        mock_instance.post.return_value = mock_response

        with patch.object(ApiClient, '_get_headers', return_value={}):
            await client.notify_human("hello")

        # Verify httpx.AsyncClient was called with timeout=900.0
        mock_client_class.assert_called_with(timeout=900.0)

@pytest.mark.asyncio
async def test_default_timeout():
    """Test that regular get/post use default timeout (30s)"""
    client = ApiClient()
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_instance.get.return_value = mock_response

        with patch.object(ApiClient, '_get_headers', return_value={}):
            await client.get("/api/v1/agents")

        # Verify httpx.AsyncClient was called with timeout=30.0
        mock_client_class.assert_called_with(timeout=30.0)
