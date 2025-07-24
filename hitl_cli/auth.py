import json
import os
import stat
from typing import Optional

import httpx
import jwt
import typer
from google_auth_oauthlib.flow import InstalledAppFlow

from .config import (
    BACKEND_BASE_URL,
    CLIENT_SECRET_FILE,
    CONFIG_DIR,
    GOOGLE_OAUTH_SCOPES,
    TOKEN_FILE,
)


class NotLoggedInError(Exception):
    """Raised when user is not logged in"""
    pass


def ensure_secure_storage():
    """Ensure the config directory exists with proper permissions"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Set directory permissions to 700 (owner read/write/execute only)
    os.chmod(CONFIG_DIR, stat.S_IRWXU)


def save_token(token: str, google_id_token: Optional[str] = None):
    """Save JWT token and optionally Google ID token to secure storage"""
    ensure_secure_storage()

    # Load existing data if available
    existing_data = {}
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, "r") as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    token_data = {
        "access_token": token,
        "google_id_token": google_id_token or existing_data.get("google_id_token")
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)

    # Set file permissions to 600 (owner read/write only)
    os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)


def load_token() -> Optional[str]:
    """Load JWT token from secure storage"""
    if not TOKEN_FILE.exists():
        return None

    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
            return token_data.get("access_token")
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        return None


def load_google_id_token() -> Optional[str]:
    """Load Google ID token from secure storage"""
    if not TOKEN_FILE.exists():
        return None

    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
            return token_data.get("google_id_token")
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        return None


def delete_token():
    """Delete the stored token file"""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


async def exchange_google_token_for_jwt(google_id_token: str) -> str:
    """Exchange Google ID token for internal JWT"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_BASE_URL}/api/v1/auth/google",
            json={"id_token": google_id_token},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            raise typer.Exit(f"Token exchange failed: {response.status_code} - {response.text}")

        result = response.json()
        return result["access_token"]


def perform_oauth_flow() -> str:
    """Perform OAuth 2.0 flow and return Google ID token"""
    if not CLIENT_SECRET_FILE.exists():
        typer.echo(f"Error: {CLIENT_SECRET_FILE} not found!")
        typer.echo("Please obtain a client_secret_desktop.json file from Google Cloud Console")
        typer.echo("and place it in the root of the hitl-cli directory.")
        raise typer.Exit(1)

    # Create OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRET_FILE),
        scopes=GOOGLE_OAUTH_SCOPES
    )

    # Run the OAuth flow
    typer.echo("Opening browser for Google Sign-In...")
    try:
        credentials = flow.run_local_server(port=0)
        return credentials.id_token
    except Exception as e:
        typer.echo(f"OAuth flow failed: {e}")
        raise typer.Exit(1)


def is_logged_in() -> bool:
    """Check if user is logged in"""
    return load_token() is not None


def get_current_token() -> str:
    """Get current JWT token or raise error if not logged in"""
    token = load_token()
    if token is None:
        raise NotLoggedInError("Not logged in. Please run 'hitl-cli login' first.")
    return token


def get_current_agent_id() -> Optional[str]:
    """Get current user's agent ID from JWT token"""
    try:
        token = get_current_token()
        # Decode JWT without verification to get the payload
        # Using PyJWT for robust decoding
        payload_data = jwt.decode(token, options={"verify_signature": False})
        return payload_data.get('agent_id')
    except Exception:
        return None


# Aliases for test compatibility
def exchange_token_with_backend(google_id_token: str) -> str:
    """Exchange Google ID token for JWT token (sync wrapper)"""
    import asyncio
    return asyncio.run(exchange_google_token_for_jwt(google_id_token))


def store_jwt_token(token: str):
    """Store JWT token securely (alias for save_token)"""
    return save_token(token)


def get_stored_jwt_token() -> Optional[str]:
    """Get stored JWT token (alias for load_token)"""
    return load_token()
