from typing import Any, Dict, List, Optional

import httpx
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from .api_client import ApiClient
from .auth import (
    get_current_agent_id,
    get_current_oauth_token,
    is_oauth_token_expired,
    is_using_api_key,
    is_using_oauth,
    load_oauth_client,
    load_oauth_token,
    refresh_oauth_token,
    save_oauth_token,
    get_api_key
)
from .config import BACKEND_BASE_URL


class MCPClient:
    """Client for making MCP calls using FastMCP streamable HTTP transport"""

    def __init__(self):
        self.base_url = BACKEND_BASE_URL
        self.timeout = 900.0  # 15 minutes for human responses
        self._mcp_token_cache = {}  # Cache MCP tokens to avoid repeated OAuth

    async def get_mcp_token(self, agent_id: str) -> str:
        """Get MCP-specific JWT token for the agent - DEPRECATED: Use OAuth instead"""
        raise Exception("Traditional OAuth flow is no longer supported. Please use OAuth dynamic registration.")

    async def create_agent_for_mcp(self, agent_name: str) -> str:
        """Create an agent and return its ID"""
        client = ApiClient()
        agent_data = {"name": agent_name}
        result = await client.post("/api/v1/agents", agent_data)
        return result["agent_id"]

    async def validate_agent_exists(self, agent_id: str) -> bool:
        """Validate that an agent exists and belongs to the current user"""
        try:
            client = ApiClient()
            agents = await client.get("/api/v1/agents")

            # Check if agent_id exists in the list of user's agents
            for agent in agents:
                if agent.get("id") == agent_id:
                    return True
            return False
        except Exception:
            return False

    async def _get_oauth_token(self) -> str:
        """Get valid OAuth access token, refreshing if necessary"""
        token_data = load_oauth_token()
        if not token_data:
            raise Exception("No OAuth token found - please login with --dynamic")

        # Check if token is expired
        if is_oauth_token_expired(token_data):
            # Try to refresh the token
            refresh_token = token_data.get('refresh_token')
            if not refresh_token:
                # Fallback: use current token as-is
                return token_data['access_token']

            client_data = load_oauth_client()
            if not client_data:
                raise Exception("OAuth client data not found - please login again")

            try:
                # Refresh the token
                new_token_data = await refresh_oauth_token(
                    refresh_token,
                    client_data['client_id'],
                    client_data.get('client_secret')
                )

                # Preserve refresh token if not provided in response
                if 'refresh_token' not in new_token_data:
                    new_token_data['refresh_token'] = refresh_token

                # Save updated token
                save_oauth_token(new_token_data)

                return new_token_data['access_token']

            except Exception as e:
                raise Exception(f"Failed to refresh OAuth token: {e}")

        return token_data['access_token']

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any], agent_id: Optional[str] = None) -> str:
        """Make an MCP tool call using FastMCP Client with streamable HTTP transport"""

        # Check if using API key authentication
        if is_using_api_key():
            api_key = get_api_key()
            mcp_url = f"{self.base_url}/mcp-server/mcp/"
            headers = {"X-API-Key": api_key}
            transport = StreamableHttpTransport(mcp_url, headers=headers)

            try:
                async with Client(transport=transport, timeout=self.timeout) as client:
                    result = await client.call_tool(tool_name, arguments)

                # Extract text content from the result
                if hasattr(result, 'content'):
                    # Handle MCP content format
                    if isinstance(result.content, list) and len(result.content) > 0:
                        content_item = result.content[0]
                        if hasattr(content_item, 'text'):
                            return content_item.text
                        elif isinstance(content_item, dict) and 'text' in content_item:
                            return content_item['text']
                    elif hasattr(result.content, 'text'):
                        return result.content.text

                # Fallback: try to get text directly from result
                if hasattr(result, 'text'):
                    return result.text
                elif isinstance(result, str):
                    return result
                else:
                    return str(result)

            except Exception as e:
                raise Exception(f"MCP tool call failed: {e}")

        # Determine authentication method and token (OAuth or traditional)
        if is_using_oauth():
            # Use OAuth Bearer authentication
            oauth_token = await self._get_oauth_token()
            auth_token = oauth_token
        else:
            # Use traditional MCP token authentication
            if not agent_id:
                agent_id = get_current_agent_id()
                if not agent_id:
                    raise Exception("No agent_id provided and none found in JWT token")

            auth_token = await self.get_mcp_token(agent_id)

        # Create MCP client URL (streamable HTTP endpoint)
        mcp_url = f"{self.base_url}/mcp-server/mcp/"

        # Create custom auth handler for Bearer token
        import httpx

        class BearerAuth(httpx.Auth):
            """Custom auth handler for Bearer token"""
            def __init__(self, token: str):
                self.token = token

            def auth_flow(self, request):
                request.headers["Authorization"] = f"Bearer {self.token}"
                yield request

        auth = BearerAuth(auth_token)

        try:
            # Use FastMCP Client with streamable HTTP transport and auth
            async with Client(mcp_url, auth=auth, timeout=self.timeout) as client:
                result = await client.call_tool(tool_name, arguments)

            # Extract text content from the result
            if hasattr(result, 'content'):
                # Handle MCP content format
                if isinstance(result.content, list) and len(result.content) > 0:
                    content_item = result.content[0]
                    if hasattr(content_item, 'text'):
                        return content_item.text
                    elif isinstance(content_item, dict) and 'text' in content_item:
                        return content_item['text']
                elif hasattr(result.content, 'text'):
                    return result.content.text

            # Fallback: try to get text directly from result
            if hasattr(result, 'text'):
                return result.text
            elif isinstance(result, str):
                return result
            else:
                return str(result)

        except Exception as e:
            raise Exception(f"MCP tool call failed: {e}")

    async def request_human_input(
        self,
        prompt: str,
        choices: Optional[List[str]] = None,
        placeholder_text: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> str:
        """Make a request for human input via the MCP server"""

        # If no agent_id provided, use the current user's agent from JWT token
        if agent_id is None:
            agent_id = get_current_agent_id()
            if agent_id is None:
                # Fallback: create a temporary agent for this request
                import uuid
                agent_id = await self.create_agent_for_mcp(f"hitl-cli-{uuid.uuid4().hex[:8]}")
        else:
            # Validate that the provided agent_id exists and belongs to the user
            if not await self.validate_agent_exists(agent_id):
                raise Exception(f"Agent does not exist or does not belong to the current user: {agent_id}")

        # Build arguments for the tool call
        arguments = {"prompt": prompt}
        if choices:
            arguments["choices"] = choices
        if placeholder_text:
            arguments["placeholder_text"] = placeholder_text

        # Make the MCP tool call using FastMCP Client
        result = await self.call_tool("request_human_input", arguments, agent_id)
        return result

    async def notify_task_completion(
        self,
        summary: str,
        agent_id: Optional[str] = None
    ) -> str:
        """Notify human that a task has been completed and get their response"""

        # If no agent_id provided, use the current user's agent from JWT token
        if agent_id is None:
            agent_id = get_current_agent_id()
            if agent_id is None:
                # Fallback: create a temporary agent for this request
                import uuid
                agent_id = await self.create_agent_for_mcp(f"hitl-cli-{uuid.uuid4().hex[:8]}")
        else:
            # Validate that the provided agent_id exists and belongs to the user
            if not await self.validate_agent_exists(agent_id):
                raise Exception(f"Agent does not exist or does not belong to the current user: {agent_id}")

        # Build arguments for the tool call
        arguments = {"summary": summary}

        # Make the MCP tool call using FastMCP Client
        result = await self.call_tool("notify_human_completion", arguments, agent_id)
        return result

    async def request_human_input_oauth(
        self,
        prompt: str,
        choices: Optional[List[str]] = None,
        placeholder_text: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> str:
        """Make a request for human input via the MCP server using OAuth Bearer authentication"""
        
        if not is_using_oauth():
            raise Exception("OAuth authentication required - please login with --dynamic")

        # Build arguments for the tool call
        arguments = {"prompt": prompt}
        if choices:
            arguments["choices"] = choices
        if placeholder_text:
            arguments["placeholder_text"] = placeholder_text
        if agent_name:
            arguments["agent_name"] = agent_name

        # Make the MCP tool call using OAuth Bearer auth
        result = await self.call_tool("request_human_input", arguments)
        return result

    async def notify_task_completion_oauth(
        self,
        summary: str,
        agent_name: Optional[str] = None
    ) -> str:
        """Notify human that a task has been completed using OAuth Bearer authentication"""
        
        if not is_using_oauth():
            raise Exception("OAuth authentication required - please login with --dynamic")

        # Build arguments for the tool call
        arguments = {"summary": summary}
        if agent_name:
            arguments["agent_name"] = agent_name

        # Make the MCP tool call using OAuth Bearer auth
        result = await self.call_tool("notify_human_completion", arguments)
        return result
