"""
Cryptographic functions for agent key management and end-to-end encryption.

This module provides PyNaCl-based encryption for secure communication
between CLI agents and mobile devices.
"""

import json
import logging
from pathlib import Path
from typing import Tuple, Optional

from nacl.public import PrivateKey, PublicKey
from nacl.encoding import Base64Encoder

from .auth import get_current_oauth_token, is_using_oauth, get_current_token, get_current_agent_id


logger = logging.getLogger(__name__)


def generate_agent_keypair() -> Tuple[str, str]:
    """
    Generate a new PyNaCl keypair for the agent.
    
    Returns:
        Tuple of (public_key_base64, private_key_base64)
    """
    private_key = PrivateKey.generate()
    public_key = private_key.public_key
    
    # Encode keys as base64 strings
    public_key_b64 = public_key.encode(Base64Encoder).decode()
    private_key_b64 = private_key.encode(Base64Encoder).decode()
    
    return public_key_b64, private_key_b64


def get_agent_keys_path() -> Path:
    """
    Get the path where agent keys should be stored.
    
    Returns:
        Path to agent.key file in ~/.config/hitl-shin-relay/
    """
    config_dir = Path.home() / ".config" / "hitl-shin-relay"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "agent.key"


def save_agent_keypair(public_key: str, private_key: str, keys_path: Optional[Path] = None) -> None:
    """
    Save agent keypair to secure file storage.
    
    Args:
        public_key: Base64-encoded public key
        private_key: Base64-encoded private key  
        keys_path: Optional custom path (defaults to get_agent_keys_path())
    """
    if keys_path is None:
        keys_path = get_agent_keys_path()
    
    # Create key data structure
    key_data = {
        "public_key": public_key,
        "private_key": private_key
    }
    
    # Write to file with restricted permissions
    keys_path.write_text(json.dumps(key_data, indent=2))
    keys_path.chmod(0o600)  # Owner read/write only
    
    logger.info(f"Agent keypair saved to {keys_path}")


def load_agent_keypair(keys_path: Optional[Path] = None) -> Tuple[str, str]:
    """
    Load agent keypair from file storage.
    
    Args:
        keys_path: Optional custom path (defaults to get_agent_keys_path())
        
    Returns:
        Tuple of (public_key_base64, private_key_base64)
        
    Raises:
        FileNotFoundError: If key file doesn't exist
        ValueError: If key file is invalid
        KeyError: If required keys are missing
    """
    if keys_path is None:
        keys_path = get_agent_keys_path()
    
    if not keys_path.exists():
        raise FileNotFoundError(f"Agent key file not found: {keys_path}")
    
    try:
        key_data = json.loads(keys_path.read_text())
        
        public_key = key_data["public_key"]
        private_key = key_data["private_key"]
        
        # Validate keys by attempting to parse them
        PublicKey(public_key, encoder=Base64Encoder)
        PrivateKey(private_key, encoder=Base64Encoder)
        
        return public_key, private_key
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in key file: {e}")
    except KeyError as e:
        raise KeyError(f"Missing key in file: {e}")
    except Exception as e:
        raise ValueError(f"Invalid key data: {e}")


async def ensure_agent_keypair() -> Tuple[str, str]:
    """
    Ensure agent keypair exists, creating and registering if necessary.
    
    Returns:
        Tuple of (public_key_base64, private_key_base64)
    """
    keys_path = get_agent_keys_path()
    
    try:
        # Try to load existing keys
        public_key, private_key = load_agent_keypair(keys_path)
        logger.info("Loaded existing agent keypair")
        return public_key, private_key
        
    except FileNotFoundError:
        # Generate new keys
        logger.info("Generating new agent keypair")
        public_key, private_key = generate_agent_keypair()
        save_agent_keypair(public_key, private_key, keys_path)
        
        # Attempt to register the public key with the backend
        try:
            await register_public_key_with_backend(public_key)
        except Exception as e:
            logger.error(f"Failed to register public key with backend: {e}")
            
        return public_key, private_key


async def register_public_key_with_backend(public_key: str) -> bool:
    """
    Register agent's public key with the backend server.

    Args:
        public_key: Base64-encoded public key

    Returns:
        True if registration successful, False otherwise
    """
    try:
        import httpx
        from .config import BACKEND_BASE_URL

        # Get agent ID for registration
        agent_id = get_current_agent_id()
        if not agent_id:
            logger.error("No agent ID available for key registration")
            return False

        # Determine authentication method
        headers = {"Content-Type": "application/json"}

        if is_using_oauth():
            # Use OAuth Bearer authentication
            oauth_token = get_current_oauth_token()
            if oauth_token:
                headers["Authorization"] = f"Bearer {oauth_token}"
            else:
                logger.error("OAuth token not available for key registration")
                return False
        else:
            # Use traditional JWT authentication
            try:
                jwt_token = get_current_token()
                headers["Authorization"] = f"Bearer {jwt_token}"
            except Exception:
                logger.error("No authentication token available for key registration")
                return False

        # Use correct endpoint and request format
        registration_data = {
            "entity_type": "agent",
            "entity_id": agent_id,
            "public_key": public_key
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BACKEND_BASE_URL}/api/v1/keys/register",
                json=registration_data,
                headers=headers
            )

            if response.status_code == 200:
                logger.info("Successfully registered public key with backend")
                return True
            else:
                logger.error(f"Failed to register public key: HTTP {response.status_code} - {response.text}")
                return False

    except Exception as e:
        logger.error(f"Failed to register public key with backend: {e}")
        return False
