from pathlib import Path

CLIENT_SECRET_FILE = Path(__file__).parent.parent / "client_secret_desktop.json"

CONFIG_DIR = Path.home() / ".config" / "hitl-cli"
TOKEN_FILE = CONFIG_DIR / "token.json"
OAUTH_CLIENT_FILE = CONFIG_DIR / "oauth_client.json"
OAUTH_TOKEN_FILE = CONFIG_DIR / "oauth_token.json"

BACKEND_BASE_URL = "https://hitl-relay-193514263276.europe-west2.run.app"

# Default registered client ID (auto-registered on server startup)
DEFAULT_CLIENT_ID = "193514263276-6hhmbgh7j9jiv3kg006kgo35ene47jdl.apps.googleusercontent.com"

GOOGLE_OAUTH_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]
