#!/usr/bin/env python3

import asyncio
import logging
from typing import List, Optional

import httpx
import typer

from .api_client import ApiClient
from .auth import (
    delete_oauth_tokens,
    delete_token,
    get_current_oauth_token,
    is_logged_in,
    is_using_api_key,
    is_using_oauth,
    OAuthDynamicClient,
)
from .config import BACKEND_BASE_URL
from .crypto import ensure_agent_keypair
from .mcp_client import MCPClient
from .proxy_handler_v2 import create_fastmcp_proxy_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = typer.Typer(help="HITL CLI - Command-line interface for hitl-shin-relay service")


def main():
    """Main entry point for the CLI application"""
    # Typer handles async commands automatically when they're defined
    app()

agents_app = typer.Typer(help="Manage agents")
app.add_typer(agents_app, name="agents")

admin_app = typer.Typer(help="Administrative commands")
app.add_typer(admin_app, name="admin")

@app.command()
def login(
    name: Optional[str] = typer.Option(None, "--name", help="Agent name for dynamic registration")
):
    """Login to the HITL service using OAuth 2.1 dynamic registration"""
    
    async def _login():
        # Check if already logged in
        if is_logged_in() or is_using_oauth():
            typer.echo("✅ Already logged in!")
            return

        # Use OAuth 2.1 dynamic client registration
        try:
            default_name = name or "HITL CLI Agent"
            oauth_client = OAuthDynamicClient()
            access_token, agent_name = await oauth_client.perform_dynamic_oauth_flow(default_name)

            typer.echo("✅ OAuth 2.1 dynamic authentication successful!")

            # Generate E2EE keys and register with server during login
            typer.echo("🔐 Generating end-to-end encryption keys...")
            public_key, private_key = await ensure_agent_keypair()
            typer.echo("✅ E2EE keys generated and registered with server")

            typer.echo()
            typer.echo(f"🤖 Agent '{agent_name}' is ready for secure E2EE communication.")
            typer.echo("💡 Use Claude Desktop with MCP configuration to interact securely.")
            typer.echo()
            typer.echo("📋 Claude Desktop MCP Configuration:")
            typer.echo('   {')
            typer.echo('     "mcpServers": {')
            typer.echo('       "hitl": {')
            typer.echo('         "command": "hitl-cli",')
            typer.echo('         "args": ["proxy", "https://hitlrelay.app/mcp-server/mcp/"]')
            typer.echo('       }')
            typer.echo('     }')
            typer.echo('   }')

        except Exception as e:
            logger.error(f"OAuth 2.1 login failed: {e}")
            typer.echo(f"❌ OAuth 2.1 login failed: {e}")
            raise typer.Exit(1)

    asyncio.run(_login())

@app.command()
def logout():
    """Logout from the HITL service"""
    if not is_logged_in() and not is_using_oauth():
        typer.echo("Not logged in.")
        return

    # Delete both traditional and OAuth tokens
    delete_token()
    delete_oauth_tokens()
    typer.echo("Logged out successfully!")

@agents_app.command("list")
def agents_list():
    """List all agents for the current user"""
    client = ApiClient()

    try:
        agents = asyncio.run(client.get("/api/v1/agents"))

        if not agents:
            typer.echo("No agents found.")
            return

        # Display agents in a formatted table
        typer.echo("\nAgents:")
        typer.echo("-" * 60)
        typer.echo(f"{'ID':<36} {'Name':<20}")
        typer.echo("-" * 60)

        for agent in agents:
            agent_id = agent.get("id", "N/A")
            agent_name = agent.get("name", "N/A")
            typer.echo(f"{agent_id:<36} {agent_name:<20}")

    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        typer.echo(f"Failed to list agents: {e}")
        raise typer.Exit(1)

@agents_app.command("create")
def agents_create(
    name: str = typer.Option(..., "--name", help="Name of the agent to create")
):
    """Create a new agent"""
    client = ApiClient()

    try:
        agent_data = {"name": name}
        result = asyncio.run(client.post("/api/v1/agents", agent_data))

        agent_id = result.get("id", "N/A")
        agent_name = result.get("name", "N/A")

        typer.echo("Agent created successfully!")
        typer.echo(f"ID: {agent_id}")
        typer.echo(f"Name: {agent_name}")

    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        typer.echo(f"Failed to create agent: {e}")
        raise typer.Exit(1)

@admin_app.command("register-client")
def admin_register_client(
    client_id: str = typer.Option(..., "--client-id", help="OAuth client ID to register"),
    client_name: str = typer.Option(..., "--client-name", help="Display name for the client"),
    client_type: str = typer.Option(..., "--client-type", help="Client type (desktop, mobile, web)"),
    agent_name: str = typer.Option(..., "--agent-name", help="Template name for auto-created agents")
):
    """Register a new OAuth client (admin only - for third-party applications)"""

    typer.echo("🔧 OAuth Client Registration")
    typer.echo("=" * 40)
    typer.echo(f"📋 Client ID: {client_id}")
    typer.echo(f"📋 Client Name: {client_name}")
    typer.echo(f"📋 Client Type: {client_type}")
    typer.echo(f"📋 Agent Template: {agent_name}")
    typer.echo()

    if is_using_oauth():
        token = get_current_oauth_token()
        if not token:
            typer.echo("No OAuth token available. Please log in again.")
            raise typer.Exit(1)

        # Register the client
        typer.echo()
        typer.echo("📝 Registering OAuth Client...")

        try:
            registration_data = {
                "client_id": client_id,
                "client_name": client_name,
                "client_type": client_type,
                "agent_name": agent_name
            }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = httpx.post(f"{BACKEND_BASE_URL}/api/v1/oauth/clients/register", json=registration_data, headers=headers)

            if response.status_code not in (200, 201):
                typer.echo(f"❌ Registration failed: {response.status_code} - {response.text}")
                raise typer.Exit(1)

            result = response.json()

            typer.echo("✅ OAuth client registered successfully!")
            typer.echo(f"   Client ID: {result['client_id']}")
            typer.echo(f"   Client Type: {result['client_type']}")
            typer.echo(f"   Agent Template: {result['agent_name']}")
            typer.echo(f"   Status: {'Active' if result.get('is_active', True) else 'Inactive'}")
            typer.echo()
            typer.echo("🎉 Registration complete!")
            typer.echo("The client application can now authenticate users.")

        except Exception as e:
            logger.error(f"OAuth client registration failed: {e}")
            typer.echo(f"❌ OAuth client registration failed: {e}")
            typer.echo()
            typer.echo("💡 Make sure you have admin privileges and the backend is running.")
            raise typer.Exit(1)
    else:
        typer.echo('Please run "hitl-cli login --name \'<Agent Name>\'" to log in.')
        raise typer.Exit(1)


@app.command()
def request(
    prompt: str = typer.Option(..., "--prompt", help="The prompt to send to the human"),
    choice: Optional[List[str]] = typer.Option(None, "--choice", help="Available choices for the human (can be specified multiple times)"),
    placeholder_text: Optional[str] = typer.Option(None, "--placeholder-text", help="Placeholder text for the input field"),
    agent_id: Optional[str] = typer.Option(None, "--agent-id", help="Agent ID to use for the request (optional - not used with OAuth)"),
    agent_name: Optional[str] = typer.Option(None, "--agent-name", help="Agent name for OAuth requests")
):
    """Send a request for human input"""
    async def _async_request():
        client = MCPClient()

        try:
            typer.echo(f"Sending request: {prompt}")
            if choice:
                typer.echo(f"Choices: {choice}")
            if placeholder_text:
                typer.echo(f"Placeholder: {placeholder_text}")

            typer.echo("\nWaiting for human response...")

            # Choose authentication method
            if is_using_api_key():
                # Use API key authentication
                response = await client.request_human_input_api_key(
                    prompt=prompt,
                    choices=choice,
                    placeholder_text=placeholder_text
                )
            elif is_using_oauth():
                # Use OAuth Bearer authentication
                response = await client.request_human_input_oauth(
                    prompt=prompt,
                    choices=choice,
                    placeholder_text=placeholder_text,
                    agent_name=agent_name
                )
            else:
                # Use traditional JWT authentication
                response = await client.request_human_input(
                    prompt=prompt,
                    choices=choice,
                    placeholder_text=placeholder_text,
                    agent_id=agent_id
                )

            typer.echo(f"\nHuman response received: {response}")

        except Exception as e:
            logger.error(f"Request failed: {e}")
            typer.echo(f"Request failed: {e}")
            raise typer.Exit(1)

    # Run the async function using asyncio.run
    asyncio.run(_async_request())

@app.command("notify-completion")
def notify_completion(
    summary: str = typer.Option(..., "--summary", help="Summary of what was completed"),
    agent_id: Optional[str] = typer.Option(None, "--agent-id", help="Agent ID to use for the notification (optional - not used with OAuth)"),
    agent_name: Optional[str] = typer.Option(None, "--agent-name", help="Agent name for OAuth requests")
):
    """Notify human that a task has been completed and wait for their response"""
    async def _async_notify():
        client = MCPClient()

        try:
            typer.echo("📋 Task Completion Notification")
            typer.echo("=" * 40)
            typer.echo(f"Summary: {summary}")
            if agent_id:
                typer.echo(f"Agent ID: {agent_id}")
            if agent_name:
                typer.echo(f"Agent Name: {agent_name}")

            typer.echo("\n⏳ Waiting for human response...")

            # Choose authentication method
            if is_using_api_key():
                # Use API key authentication
                response = await client.notify_task_completion_api_key(
                    summary=summary
                )
            elif is_using_oauth():
                # Use OAuth Bearer authentication
                response = await client.notify_task_completion_oauth(
                    summary=summary,
                    agent_name=agent_name
                )
            else:
                # Use traditional JWT authentication
                response = await client.notify_task_completion(
                    summary=summary,
                    agent_id=agent_id
                )

            typer.echo(f"\n✅ Human response received: {response}")

        except Exception as e:
            logger.error(f"Notification failed: {e}")
            typer.echo(f"❌ Notification failed: {e}")
            raise typer.Exit(1)

    # Run the async function using asyncio.run
    asyncio.run(_async_notify())


@app.command()
def notify(
    message: str = typer.Option(..., "--message", help="The notification message to send"),
    agent_id: Optional[str] = typer.Option(None, "--agent-id", help="Agent ID to use for the notification (optional - not used with OAuth)"),
    agent_name: Optional[str] = typer.Option(None, "--agent-name", help="Agent name for OAuth requests")
):
    """Send a fire-forget notification to human"""
    async def _async_notify():
        client = MCPClient()

        try:
            typer.echo("📢 Sending Notification")
            typer.echo("=" * 40)
            typer.echo(f"Message: {message}")
            if agent_id:
                typer.echo(f"Agent ID: {agent_id}")
            if agent_name:
                typer.echo(f"Agent Name: {agent_name}")

            typer.echo("\n📤 Sending notification...")

            # Choose authentication method
            if is_using_api_key():
                # Use API key authentication
                response = await client.notify_human_api_key(
                    message=message
                )
            elif is_using_oauth():
                # Use OAuth Bearer authentication
                response = await client.notify_human_oauth(
                    message=message,
                    agent_name=agent_name
                )
            else:
                # Use traditional JWT authentication
                response = await client.notify_human(
                    message=message,
                    agent_id=agent_id
                )

            typer.echo(f"\n✅ {response}")

        except Exception as e:
            logger.error(f"Notification failed: {e}")
            typer.echo(f"❌ Notification failed: {e}")
            raise typer.Exit(1)

    # Run the async function using asyncio.run
    asyncio.run(_async_notify())


@app.command()
def proxy(
    backend_url: str = typer.Argument(..., help="Backend MCP server URL")
):
    """Start MCP proxy with transparent end-to-end encryption"""
    async def _async_proxy():
        try:
            # Verify authentication and keys exist (should be created during login)
            if not is_logged_in() and not is_using_oauth():
                typer.echo("❌ Not logged in. Please run 'hitl-cli login --name \"Agent Name\"' first.")
                raise typer.Exit(1)
            
            # Ensure agent keypair exists (generate if needed)
            # typer.echo("🔐 Ensuring agent cryptographic keys...")
            try:
                public_key, private_key = await ensure_agent_keypair()
                # typer.echo("✅ Agent keys ready")
            except Exception:
                typer.echo("❌ E2EE keys not available. Please run 'hitl-cli login --name \"Agent Name\"' to generate keys.")
                raise typer.Exit(1)
            
            # Create and start FastMCP proxy server
            # typer.echo(f"🚀 Starting FastMCP proxy for backend: {backend_url}")
            # typer.echo("📡 Listening for MCP requests on stdin...")
            # typer.echo("🔐 End-to-end encryption active - server will only see encrypted data")
            
            # Use new FastMCP-based proxy server
            server = create_fastmcp_proxy_server(backend_url)
            await server.run_stdio_async()
            
        except Exception as e:
            logger.error(f"Proxy failed: {e}")
            typer.echo(f"❌ Proxy failed: {e}")
            raise typer.Exit(1)
    
    # Run the async function using asyncio.run
    asyncio.run(_async_proxy())

if __name__ == "__main__":
    app()
