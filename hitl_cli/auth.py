import asyncio
import base64
import hashlib
import http.server
import json
import os
import secrets
import socketserver
import stat
import threading
import time
import webbrowser
from typing import Dict, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
import jwt
import typer
from authlib.oauth2 import OAuth2Error

from .config import (
    BACKEND_BASE_URL,
    CONFIG_DIR,
    OAUTH_CLIENT_FILE,
    OAUTH_TOKEN_FILE,
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


def delete_token():
    """Delete the stored token file"""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


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
    """Get current user's agent ID from OAuth token"""
    try:
        token = get_current_oauth_token() or get_current_token()
        if not token:
            return None

        # Decode JWT without verification to get the payload
        # Using PyJWT for robust decoding
        payload_data = jwt.decode(token, options={"verify_signature": False})
        return payload_data.get('agent_id')
    except Exception:
        return None


# OAuth 2.1 Dynamic Client Registration Implementation


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """HTTP server handler for OAuth callback"""
    
    def __init__(self, callback_data: Dict, *args, **kwargs):
        self.callback_data = callback_data
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle OAuth callback GET request"""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Extract authorization code and state
        code = query_params.get('code', [None])[0]
        state = query_params.get('state', [None])[0]
        error = query_params.get('error', [None])[0]
        
        if error:
            self.callback_data['error'] = error
            self.callback_data['error_description'] = query_params.get('error_description', [''])[0]
        else:
            self.callback_data['code'] = code
            self.callback_data['state'] = state
        
        # Send response to browser
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if error:
            html = f"""
            <html><body>
            <h1>Authentication Failed</h1>
            <p>Error: {error}</p>
            <p>You can close this window.</p>
            </body></html>
            """
        else:
            html = """
            <html><body>
            <h1>Authentication Successful</h1>
            <p>You can close this window and return to the CLI.</p>
            </body></html>
            """
        
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Suppress server logs"""
        pass


class OAuthDynamicClient:
    """OAuth 2.1 dynamic client with PKCE support"""
    
    def __init__(self):
        self.base_url = BACKEND_BASE_URL
        self.callback_port = 8080
        self.callback_path = "/callback"
        self.redirect_uri = f"http://localhost:{self.callback_port}{self.callback_path}"
    
    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier (RFC 7636)"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
    
    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge from verifier (RFC 7636)"""
        digest = hashlib.sha256(code_verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip('=')
    
    def _generate_state(self) -> str:
        """Generate OAuth state parameter"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
    
    async def _register_client(self, agent_name: str) -> Dict[str, str]:
        """Register dynamic OAuth client (RFC 7591)"""
        registration_data = {
            "client_name": f"HITL CLI - {agent_name}",
            "redirect_uris": [self.redirect_uri],
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid profile email"
        }

        typer.echo(f"📤 Sending registration request to: {self.base_url}/api/v1/oauth/register")
        typer.echo(f"📋 Registration data: {json.dumps(registration_data, indent=2)}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/oauth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )

            typer.echo(f"📥 Registration response status: {response.status_code}")
            try:
                hdrs = dict(response.headers)
            except Exception:
                hdrs = {}
            typer.echo(f"📥 Registration response headers: {hdrs}")

            if response.status_code != 201:
                typer.echo(f"❌ Registration failed with status: {response.status_code}")
                typer.echo(f"❌ Response body: {response.text}")
                raise Exception(f"Client registration failed: {response.status_code} - {response.text}")

            response_data = response.json()
            typer.echo(f"✅ Registration successful! Response: {json.dumps(response_data, indent=2)}")

            # Validate required fields in response
            required_fields = ["client_id"]
            for field in required_fields:
                if field not in response_data:
                    raise Exception(f"Missing required field '{field}' in registration response")

            typer.echo(f"🔑 Generated client_id: {response_data['client_id']}")

            # Handle both confidential and public clients
            if "client_secret" in response_data:
                typer.echo(f"🔒 Generated client_secret: {'*' * len(response_data.get('client_secret', ''))}")
                typer.echo("📋 Registered as confidential client")
            else:
                typer.echo("📋 Registered as public client (no secret required)")

            return response_data
    
    def _start_callback_server(self, callback_data: Dict) -> socketserver.TCPServer:
        """Start local HTTP server for OAuth callback"""
        handler = lambda *args, **kwargs: OAuthCallbackHandler(callback_data, *args, **kwargs)
        
        server = socketserver.TCPServer(("localhost", self.callback_port), handler)
        server_thread = threading.Thread(target=server.handle_request)
        server_thread.daemon = True
        server_thread.start()
        
        return server
    
    def _build_authorization_url(self, client_id: str, code_challenge: str, state: str) -> str:
        """Build OAuth 2.1 authorization URL with PKCE"""
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile email",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        authorization_url = f"{self.base_url}/api/v1/oauth/authorize?" + urlencode(params)
        
        typer.echo(f"🔗 Authorization URL parameters:")
        typer.echo(f"   - client_id: {client_id}")
        typer.echo(f"   - redirect_uri: {self.redirect_uri}")
        typer.echo(f"   - state: {state}")
        typer.echo(f"   - code_challenge: {code_challenge[:20]}...")
        typer.echo(f"🌐 Full authorization URL: {authorization_url}")
        
        return authorization_url
    
    async def _exchange_authorization_code(
        self,
        client_id: str,
        client_secret: Optional[str],
        authorization_code: str,
        code_verifier: str,
        agent_name: str
    ) -> Dict[str, str]:
        """Exchange authorization code for OAuth tokens"""
        token_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": client_id,
            "code_verifier": code_verifier
        }

        # Only add client_secret if provided (for confidential clients)
        if client_secret:
            token_data["client_secret"] = client_secret

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-MCP-Agent-Name": agent_name
        }

        typer.echo(f"🔄 Token exchange request:")
        typer.echo(f"   - URL: {self.base_url}/api/v1/oauth/token")
        typer.echo(f"   - client_id: {client_id}")
        typer.echo(f"   - code: {authorization_code[:20]}...")
        typer.echo(f"   - agent_name: {agent_name}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/oauth/token",
                data=token_data,
                headers=headers
            )

            typer.echo(f"📥 Token exchange response status: {response.status_code}")
            try:
                hdrs = dict(response.headers)
            except Exception:
                hdrs = {}
            typer.echo(f"📥 Token exchange response headers: {hdrs}")

            if response.status_code != 200:
                typer.echo(f"❌ Token exchange failed with status: {response.status_code}")
                typer.echo(f"❌ Response body: {response.text}")
                raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")

            response_data = response.json()
            typer.echo("✅ Token exchange successful!")
            typer.echo(f"📋 Response keys: {list(response_data.keys())}")

            return response_data
    
    async def perform_dynamic_oauth_flow(self, agent_name: str) -> Tuple[str, str]:
        """Perform complete OAuth 2.1 dynamic registration and authorization flow"""
        typer.echo("🔐 Starting OAuth 2.1 Dynamic Client Registration")
        typer.echo("=" * 50)
        
        # Step 1: Register client dynamically
        typer.echo("📝 Registering dynamic OAuth client...")
        try:
            client_info = await self._register_client(agent_name)
            typer.echo("✅ Client registration successful!")
            
            # Validate critical fields before proceeding
            if not client_info.get("client_id"):
                raise Exception("Registration response missing client_id")
            
            # Save client info
            save_oauth_client(client_info)
            
            # Add a small delay to ensure backend has processed the registration
            typer.echo("⏱️  Waiting for registration to propagate...")
            await asyncio.sleep(2)
            
        except Exception as e:
            typer.echo(f"❌ Client registration failed: {e}")
            raise typer.Exit(1)
        
        # Step 2: Generate PKCE parameters
        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)
        state = self._generate_state()
        
        # Step 3: Start callback server
        callback_data = {}
        server = self._start_callback_server(callback_data)
        
        try:
            # Step 4: Build authorization URL and open browser
            auth_url = self._build_authorization_url(
                client_info["client_id"], 
                code_challenge, 
                state
            )
            
            typer.echo(f"🌐 Opening browser for OAuth authorization...")
            typer.echo(f"   If browser doesn't open, visit: {auth_url}")
            
            webbrowser.open(auth_url)
            
            # Step 5: Wait for callback
            typer.echo("⏳ Waiting for authorization callback...")
            
            # Wait for callback with timeout
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while not callback_data and (time.time() - start_time) < timeout:
                time.sleep(0.5)
            
            if not callback_data:
                raise Exception("Authorization timeout - no callback received")
            
            if 'error' in callback_data:
                error_msg = callback_data.get('error_description', callback_data['error'])
                raise Exception(f"Authorization failed: {error_msg}")
            
            # Verify state parameter
            if callback_data.get('state') != state:
                raise Exception("Invalid state parameter - possible CSRF attack")
            
            authorization_code = callback_data['code']
            typer.echo("✅ Authorization code received!")
            
            # Step 6: Exchange code for tokens
            typer.echo("🔄 Exchanging authorization code for tokens...")
            
            token_response = await self._exchange_authorization_code(
                client_info["client_id"],
                client_info.get("client_secret"),  # May be None for public clients
                authorization_code,
                code_verifier,
                agent_name
            )
            
            # Add expiry timestamp
            if 'expires_in' in token_response:
                token_response['expires_at'] = int(time.time()) + int(token_response['expires_in'])
            
            # Save OAuth tokens
            save_oauth_token(token_response)
            
            typer.echo("✅ OAuth 2.1 authentication successful!")
            
            return token_response['access_token'], agent_name
            
        finally:
            server.server_close()


def save_oauth_client(client_data: Dict[str, str]):
    """Save OAuth client registration data"""
    ensure_secure_storage()
    
    with open(OAUTH_CLIENT_FILE, "w") as f:
        json.dump(client_data, f)
    
    # Set file permissions to 600 (owner read/write only)
    os.chmod(OAUTH_CLIENT_FILE, stat.S_IRUSR | stat.S_IWUSR)


def load_oauth_client() -> Optional[Dict[str, str]]:
    """Load OAuth client registration data"""
    if not OAUTH_CLIENT_FILE.exists():
        return None
    
    try:
        with open(OAUTH_CLIENT_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def save_oauth_token(token_data: Dict[str, str]):
    """Save OAuth token data"""
    ensure_secure_storage()
    
    with open(OAUTH_TOKEN_FILE, "w") as f:
        json.dump(token_data, f)
    
    # Set file permissions to 600 (owner read/write only)  
    os.chmod(OAUTH_TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)


def load_oauth_token() -> Optional[Dict[str, str]]:
    """Load OAuth token data"""
    if not OAUTH_TOKEN_FILE.exists():
        return None
    
    try:
        with open(OAUTH_TOKEN_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def delete_oauth_tokens():
    """Delete OAuth client and token files"""
    if OAUTH_CLIENT_FILE.exists():
        OAUTH_CLIENT_FILE.unlink()
    if OAUTH_TOKEN_FILE.exists():
        OAUTH_TOKEN_FILE.unlink()


def is_oauth_token_expired(token_data: Dict[str, str]) -> bool:
    """Check if OAuth token is expired"""
    if not token_data.get('expires_at'):
        return True  # Treat as expired if no expiry info
    
    return int(time.time()) >= int(token_data['expires_at'])


async def refresh_oauth_token(refresh_token: str, client_id: str, client_secret: Optional[str] = None) -> Dict[str, str]:
    """Refresh OAuth access token"""
    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    
    # Only add client_secret if provided (for confidential clients)
    if client_secret:
        token_data["client_secret"] = client_secret
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_BASE_URL}/api/v1/oauth/token",
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.status_code} - {response.text}")
        
        token_response = response.json()
        
        # Add expiry timestamp  
        if 'expires_in' in token_response:
            token_response['expires_at'] = int(time.time()) + int(token_response['expires_in'])
        
        return token_response


def is_using_oauth() -> bool:
    """Check if user is using OAuth authentication"""
    return load_oauth_token() is not None


def get_current_oauth_token() -> Optional[str]:
    """Get current OAuth access token"""
    token_data = load_oauth_token()
    if not token_data:
        return None
    
    return token_data.get('access_token')
