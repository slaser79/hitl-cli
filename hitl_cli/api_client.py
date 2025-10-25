import logging
from typing import Any, Dict, List, Optional

import httpx
import typer

from .auth import NotLoggedInError, get_current_token, is_using_api_key, get_api_key
from .config import BACKEND_BASE_URL
from .crypto import decrypt_payload, encrypt_payload, ensure_agent_keypair

logger = logging.getLogger(__name__)


class ApiClient:
    """HTTP client for hitl-shin-relay API with automatic JWT authentication"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or BACKEND_BASE_URL
        self.timeout = 30.0

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        if is_using_api_key():
            api_key = get_api_key()
            return {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
        else:
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
            except Exception:
                error_msg = f"HTTP {response.status_code} - {response.text}"

            logger.error(f"API error: {error_msg}")
            typer.echo(f"API Error: {error_msg}")
            raise typer.Exit(1)

        try:
            return response.json()
        except Exception:
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

    async def request_human_input_e2ee(
        self,
        prompt: str,
        choices: Optional[List[str]] = None,
        placeholder_text: Optional[str] = None,
    ) -> str:
        """Send an E2EE request for human input"""
        # 1. Ensure agent's keypair exists
        agent_public_key, agent_private_key = await ensure_agent_keypair()

        # 2. Fetch user's public key from the server
        user_keys = await self.get("/api/v1/keys/user")
        if not user_keys:
            raise Exception("No user public keys found on the server.")

        # For simplicity, we'll use the first available user key.
        user_public_key_b64 = user_keys[0]['public_key']

        # 3. Construct the payload
        payload = {
            "prompt": prompt,
            "choices": choices or [],
            "placeholder_text": placeholder_text or "",
        }

        # 4. Encrypt the payload
        encrypted_payload_b64 = encrypt_payload(
            payload, user_public_key_b64, agent_private_key
        )

        # 5. Send the encrypted payload to the E2EE endpoint
        e2ee_request_body = {"encrypted_payload": encrypted_payload_b64}
        response = await self.post("/api/v1/hitl/request/e2ee", e2ee_request_body)

        # 6. Decrypt the response
        encrypted_response_b64 = response["encrypted_response"]
        decrypted_response = decrypt_payload(
            encrypted_response_b64, user_public_key_b64, agent_private_key
        )

        return decrypted_response.get("response", "")

    async def notify_human_e2ee(self, message: str) -> str:
        """Send an E2EE notification to the user"""
        # 1. Ensure agent's keypair exists
        agent_public_key, agent_private_key = await ensure_agent_keypair()

        # 2. Fetch user's public key from the server
        user_keys = await self.get("/api/v1/keys/user")
        if not user_keys:
            raise Exception("No user public keys found on the server.")

        # For simplicity, we'll use the first available user key.
        user_public_key_b64 = user_keys[0]["public_key"]

        # 3. Construct the payload
        payload = {"message": message}

        # 4. Encrypt the payload
        encrypted_payload_b64 = encrypt_payload(
            payload, user_public_key_b64, agent_private_key
        )

        # 5. Send the encrypted payload to the E2EE notify endpoint
        e2ee_request_body = {"encrypted_payload": encrypted_payload_b64}
        response = await self.post(
            "/api/v1/hitl/notify/e2ee", e2ee_request_body
        )

        return response.get("status", "Notification sent")

    async def notify_task_completion_e2ee(self, summary: str) -> str:
        """Send an E2EE notification that a task has been completed"""
        # 1. Ensure agent's keypair exists
        agent_public_key, agent_private_key = await ensure_agent_keypair()

        # 2. Fetch user's public key from the server
        user_keys = await self.get("/api/v1/keys/user")
        if not user_keys:
            raise Exception("No user public keys found on the server.")

        # For simplicity, we'll use the first available user key.
        user_public_key_b64 = user_keys[0]["public_key"]

        # 3. Construct the payload
        payload = {"summary": summary}

        # 4. Encrypt the payload
        encrypted_payload_b64 = encrypt_payload(
            payload, user_public_key_b64, agent_private_key
        )

        # 5. Send the encrypted payload to the E2EE completion endpoint
        e2ee_request_body = {"encrypted_payload": encrypted_payload_b64}
        response = await self.post(
            "/api/v1/hitl/complete/e2ee", e2ee_request_body
        )

        # 6. Decrypt the response
        encrypted_response_b64 = response["encrypted_response"]
        decrypted_response = decrypt_payload(
            encrypted_response_b64, user_public_key_b64, agent_private_key
        )

        return decrypted_response.get("response", "")
