from typing import Any, Dict, List, Optional

import httpx
from fastmcp import Client

from .api_client import ApiClient
from .auth import get_current_agent_id, load_google_id_token, perform_oauth_flow
from .config import BACKEND_BASE_URL


class MCPClient:
    """Client for making MCP calls using FastMCP streamable HTTP transport"""

    def __init__(self):
        self.base_url = BACKEND_BASE_URL
        self.timeout = 300.0  # 5 minutes for human responses
        self._mcp_token_cache = {}  # Cache MCP tokens to avoid repeated OAuth

    async def get_mcp_token(self, agent_id: str) -> str:
        """Get MCP-specific JWT token for the agent"""
        # Check cache first
        if agent_id in self._mcp_token_cache:
            return self._mcp_token_cache[agent_id]

        # Try to use stored Google ID token first
        google_id_token = load_google_id_token()
        if not google_id_token:
            # Fallback to OAuth flow if no stored token
            google_id_token = perform_oauth_flow()
            # Save the newly obtained Google ID token
            from .auth import load_token, save_token
            current_jwt = load_token()
            save_token(current_jwt, google_id_token)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/mcp",
                json={"id_token": google_id_token, "agent_id": agent_id},
                headers={"Content-Type": "application/json"}
            )

            if response.status_code != 200:
                raise Exception(f"MCP token exchange failed: {response.status_code} - {response.text}")

            result = response.json()
            mcp_token = result["access_token"]

            # Cache the token
            self._mcp_token_cache[agent_id] = mcp_token
            return mcp_token

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

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any], agent_id: str) -> str:
        """Make an MCP tool call using FastMCP Client with streamable HTTP transport"""
        # Get MCP token for authentication
        mcp_token = await self.get_mcp_token(agent_id)

        # Create MCP client URL (streamable HTTP endpoint)
        mcp_url = f"{self.base_url}/mcp-server/mcp/"

        # Create custom auth handler for JWT Bearer token
        import httpx

        class JWTAuth(httpx.Auth):
            """Custom auth handler for JWT Bearer token"""
            def __init__(self, token: str):
                self.token = token

            def auth_flow(self, request):
                request.headers["Authorization"] = f"Bearer {self.token}"
                yield request

        auth = JWTAuth(mcp_token)

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

