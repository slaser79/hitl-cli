import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "hitl-cli"
TOKEN_FILE = CONFIG_DIR / "token.json"
OAUTH_CLIENT_FILE = CONFIG_DIR / "oauth_client.json"
OAUTH_TOKEN_FILE = CONFIG_DIR / "oauth_token.json"

# Support environment variable override, default to cloud service
BACKEND_BASE_URL = os.environ.get(
    "HITL_SERVER_URL", 
    "https://hitl-relay.app"
)
