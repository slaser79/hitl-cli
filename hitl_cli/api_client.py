import logging
from typing import Any, Dict, Optional

import httpx
import typer

from .auth import NotLoggedInError, get_current_token
from .config import BACKEND_BASE_URL

logger = logging.getLogger(__name__)


class ApiClient:
    """HTTP client for hitl-shin-relay API with automatic JWT authentication"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or BACKEND_BASE_URL
        self.timeout = 30.0

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        try:
            token = get_current_token()
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        except NotLoggedInError:
            logger.error("Not logged in - authentication token missing")
            typer.echo("Error: Not logged in. Please run 'hitl-cli login' first.")
            raise typer.Exit(1)

    async def get(self, path: str) -> Dict[str, Any]:
        """Make GET request to API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                headers=self._get_headers()
            )
            return self._handle_response(response)

    async def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request to API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                json=data,
                headers=self._get_headers()
            )
            return self._handle_response(response)

    async def put(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request to API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                f"{self.base_url}{path}",
                json=data,
                headers=self._get_headers()
            )
            return self._handle_response(response)

    async def delete(self, path: str) -> Dict[str, Any]:
        """Make DELETE request to API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}{path}",
                headers=self._get_headers()
            )
            return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        if response.status_code == 401:
            logger.error("Authentication failed - token may be expired or invalid")
            typer.echo("Error: Authentication failed. Please run 'hitl-cli login' again.")
            raise typer.Exit(1)

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", f"HTTP {response.status_code}")
            except:
                error_msg = f"HTTP {response.status_code} - {response.text}"

            logger.error(f"API error: {error_msg}")
            typer.echo(f"API Error: {error_msg}")
            raise typer.Exit(1)

        try:
            return response.json()
        except:
            return {"status": "success"}

    # Sync wrappers for testing
    def get_sync(self, path: str):
        """Sync wrapper for GET request"""
        import asyncio
        return asyncio.run(self.get(path))

    def post_sync(self, path: str, data: Optional[Dict[str, Any]] = None):
        """Sync wrapper for POST request - returns response object for testing"""
        import asyncio


        # For testing, we want to return a response-like object
        class MockResponse:
            def __init__(self, status_code, json_data):
                self.status_code = status_code
                self._json_data = json_data

            def json(self):
                return self._json_data

        try:
            result = asyncio.run(self.post(path, data))
            return MockResponse(200, result)
        except typer.Exit as e:
            # In case of error, still return a response object
            return MockResponse(getattr(e, 'exit_code', 500), {"error": "Request failed"})
