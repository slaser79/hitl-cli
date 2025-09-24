"""
MCP proxy handler for transparent end-to-end encryption.

This module implements an MCP proxy that sits between Claude and the backend,
providing transparent encryption/decryption of human-in-the-loop communications.
"""

import asyncio
import base64
import json
import logging
import sys
from typing import Dict, List, Any, Optional

import httpx
from fastmcp import Client
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import Base64Encoder

from .auth import get_current_oauth_token, is_using_oauth
from .crypto import load_agent_keypair

logger = logging.getLogger(__name__)


class ProxyHandler:
    """
    MCP proxy handler that provides transparent end-to-end encryption.
    
    Intercepts MCP requests from Claude, encrypts sensitive data, forwards
    to backend, decrypts responses, and returns plaintext to Claude.
    """
    
    def __init__(self, backend_url: str):
        """
        Initialize proxy handler.
        
        Args:
            backend_url: URL of the backend MCP server
        """
        self.backend_url = backend_url.rstrip('/')
        
        # Use the provided URL directly if it's already the full MCP endpoint
        if backend_url.endswith('/mcp-server/mcp') or backend_url.endswith('/mcp-server/mcp/'):
            self.mcp_url = backend_url if backend_url.endswith('/') else backend_url + '/'
        else:
            self.mcp_url = f"{self.backend_url}/mcp-server/mcp/"
        
        # Load agent keypair
        self.public_key, self.private_key = load_agent_keypair()
        self.agent_private_key = PrivateKey(self.private_key, encoder=Base64Encoder)
        self.agent_public_key = PublicKey(self.public_key, encoder=Base64Encoder)
        
        logger.info(f"Proxy handler initialized for backend: {backend_url}")

    async def start_proxy_loop(self) -> None:
        """
        Start the main proxy loop, listening for MCP requests on stdin.
        
        Reads JSON-RPC requests from stdin, processes them, and writes
        responses to stdout. Terminates when stdin is closed.
        """
        logger.info("Starting MCP proxy loop")
        
        try:
            while True:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    # EOF - parent process terminated
                    logger.info("Parent process terminated, exiting proxy")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Process MCP request
                try:
                    response = await self.handle_mcp_request(line)
                    
                    # Write response to stdout
                    response_json = json.dumps(response)
                    print(response_json, flush=True)
                    
                except Exception as e:
                    logger.error(f"Error processing MCP request: {e}")
                    
                    # Send error response
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except Exception as e:
            logger.error(f"Proxy loop error: {e}")
            raise

    async def handle_mcp_request(self, request_line: str) -> Dict[str, Any]:
        """
        Handle an MCP JSON-RPC request.
        
        Args:
            request_line: JSON string containing the MCP request
            
        Returns:
            MCP response dictionary
        """
        try:
            request = json.loads(request_line)
        except json.JSONDecodeError:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error - Invalid JSON"
                }
            }
        
        # Validate basic JSON-RPC structure
        if not isinstance(request, dict) or "method" not in request:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32600,
                    "message": "Invalid Request - Missing method"
                }
            }
        
        method = request["method"]
        
        # Handle different MCP methods
        if method == "tools/list":
            return await self.handle_tools_list(request)
        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            if tool_name == "request_human_input":
                return await self.handle_request_human_input(request)
            else:
                # Forward other tool calls to backend
                return await self.forward_to_backend(request)
        else:
            # Forward other methods to backend
            return await self.forward_to_backend(request)

    async def handle_tools_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/list request by filtering out encrypted tool variants.
        
        Args:
            request: MCP tools/list request
            
        Returns:
            Filtered tools list response
        """
        try:
            # Get tools from backend
            backend_tools = await self.get_backend_tools()
            
            # Filter out encrypted variants (tools ending with _e2ee)
            plaintext_tools = [
                tool for tool in backend_tools
                if not tool.get("name", "").endswith("_e2ee")
            ]
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": plaintext_tools
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling tools/list: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Failed to get tools: {str(e)}"
                }
            }

    async def get_backend_tools(self) -> List[Dict[str, Any]]:
        """
        Fetch tools from the backend using forward_to_backend.
        
        Returns:
            List of tool definitions
        """
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        resp = await self.forward_to_backend(req)
        # resp expected format: {"jsonrpc":"2.0","id":...,"result":{"tools":[...]}}
        tools = []
        try:
            result = resp.get("result") or resp
            if isinstance(result, dict) and "tools" in result:
                tools = result["tools"]
            elif isinstance(resp, dict) and "tools" in resp:
                tools = resp["tools"]
        except Exception:
            tools = []
        return tools

    async def handle_request_human_input(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle request_human_input by encrypting arguments and calling _e2ee variant.

        Args:
            request: MCP request_human_input call

        Returns:
            Decrypted response from backend
        """
        try:
            # Get arguments from request
            arguments = request.get("params", {}).get("arguments", {})

            # Get device public keys
            device_public_keys = await self.get_device_public_keys()

            if not device_public_keys:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "No device public keys available"
                    }
                }

            # Encrypt arguments
            encrypted_payload = self.encrypt_arguments(arguments, device_public_keys)

            # Create _e2ee request
            e2ee_request = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "method": "tools/call",
                "params": {
                    "name": "request_human_input_e2ee",
                    "arguments": {
                        "encrypted_payload": encrypted_payload
                    }
                }
            }

            # Forward to backend
            encrypted_response = await self.forward_to_backend(e2ee_request)

            # Decrypt response
            if "result" in encrypted_response:
                # Assume first device key was used for response encryption
                device_public_key = device_public_keys[0]
                decrypted = self.process_encrypted_response(
                    encrypted_response, device_public_key
                )
                if isinstance(decrypted.get("result"), dict):
                    content = decrypted["result"].get("content")
                    if isinstance(content, list) and content and isinstance(content[0], dict) and "text" in content[0]:
                        return {"jsonrpc": decrypted.get("jsonrpc","2.0"), "id": decrypted.get("id"), "result": content[0]["text"]}
                return decrypted
            else:
                # Return error response unchanged
                return encrypted_response

        except Exception as e:
            logger.error(f"Error handling request_human_input: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Failed to process encrypted request: {str(e)}"
                }
            }

    async def get_device_public_keys(self) -> List[str]:
        """
        Retrieve public keys of user's mobile devices from backend.
        
        Returns:
            List of base64-encoded device public keys
            
        Raises:
            Exception: If backend request fails
        """
        # Get authentication headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        if is_using_oauth():
            oauth_token = get_current_oauth_token()
            headers["Authorization"] = f"Bearer {oauth_token}"
        else:
            raise Exception("MCP proxy requires OAuth authentication")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.backend_url}/api/v1/devices/public-keys",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get device public keys: {response.status_code} - {response.text}")
            
            result = response.json()
            return result.get("public_keys", [])

    def encrypt_arguments(self, arguments: Dict[str, Any], device_public_keys: List[str]) -> str:
        """
        Encrypt arguments for multiple device recipients.
        
        Args:
            arguments: Dictionary of arguments to encrypt
            device_public_keys: List of base64-encoded device public keys
            
        Returns:
            Base64-encoded encrypted payload
            
        Raises:
            ValueError: If no device keys provided
        """
        if not device_public_keys:
            raise ValueError("No device public keys provided for encryption")
        
        # Serialize arguments to JSON
        arguments_json = json.dumps(arguments)
        arguments_bytes = arguments_json.encode('utf-8')
        
        # For simplicity, encrypt for first device key
        # In production, would implement multi-recipient encryption
        device_public_key = PublicKey(device_public_keys[0], encoder=Base64Encoder)
        
        # Create encryption box (agent -> device)
        box = Box(self.agent_private_key, device_public_key)
        
        # Encrypt the arguments
        encrypted_bytes = box.encrypt(arguments_bytes)
        
        # Return base64-encoded result
        return base64.b64encode(encrypted_bytes).decode()

    def decrypt_response(self, encrypted_data: str, device_public_key: str) -> str:
        """
        Decrypt response from device.
        
        Args:
            encrypted_data: Base64-encoded encrypted response
            device_public_key: Base64-encoded device public key
            
        Returns:
            Decrypted plaintext string
            
        Raises:
            Exception: If decryption fails
        """
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Get device public key
            device_pub_key = PublicKey(device_public_key, encoder=Base64Encoder)
            
            # Create decryption box (device -> agent)
            box = Box(self.agent_private_key, device_pub_key)
            
            # Decrypt
            decrypted_bytes = box.decrypt(encrypted_bytes)
            
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Failed to decrypt response: {e}")

    def process_encrypted_response(self, response_payload, device_public_key_b64):
        try:
            # Load agent keys
            agent_pub_b64, agent_priv_b64 = load_agent_keypair()
            agent_private = PrivateKey(agent_priv_b64, encoder=Base64Encoder)
            device_public = PublicKey(device_public_key_b64, encoder=Base64Encoder)
            # Extract encrypted text
            result = response_payload.get("result") or {}
            content = result.get("content", [])
            if isinstance(content, dict):  # be tolerant if dict provided
                texts = [content.get("text")]
            else:
                texts = [b.get("text") for b in content if isinstance(b, dict)]
            if not texts or not texts[0]:
                raise Exception("No encrypted content")
            enc_text = texts[0]
            # Handle base64 decoding
            try:
                ciphertext = base64.b64decode(enc_text)
            except Exception:
                # Some code may have Base64Encoder output already decoded; try direct bytes
                try:
                    ciphertext = enc_text.encode()
                except Exception:
                    raise
            box = Box(agent_private, device_public)
            plaintext_bytes = box.decrypt(ciphertext)
            plaintext = plaintext_bytes.decode("utf-8")
            # Return normalized JSON-RPC result with plaintext content (list form)
            return {
                "jsonrpc": response_payload.get("jsonrpc","2.0"),
                "id": response_payload.get("id"),
                "result": {
                    "content": [{"type": "text", "text": plaintext}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": response_payload.get("jsonrpc","2.0"),
                "id": response_payload.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Failed to decrypt response: {e}"
                }
            }

    async def forward_to_backend(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forward MCP request to backend server.
        
        Args:
            request: MCP request to forward
            
        Returns:
            Backend response
        """
        # Get authentication headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        if is_using_oauth():
            oauth_token = get_current_oauth_token()
            headers["Authorization"] = f"Bearer {oauth_token}"
        else:
            raise Exception("MCP proxy requires OAuth authentication")
        
        async with httpx.AsyncClient(timeout=900.0) as client:  # 15 minute timeout for human responses
            response = await client.post(
                self.mcp_url,
                json=request,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Backend request failed: {response.status_code} - {response.text}")
            
            return response.json()
