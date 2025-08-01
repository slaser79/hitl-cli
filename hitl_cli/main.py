#!/usr/bin/env python3

import asyncio
import logging
from typing import List, Optional

import typer

from .api_client import ApiClient
from .auth import (
    delete_oauth_tokens,
    delete_token,
    exchange_token_with_backend,
    get_current_agent_id,
    is_logged_in,
    is_using_oauth,
    OAuthDynamicClient,
    perform_oauth_flow,
    save_token,
)
from .mcp_client import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = typer.Typer(help="HITL CLI - Command-line interface for hitl-shin-relay service")


def perform_oauth_and_token_exchange(purpose: str = "authentication") -> tuple[str, str]:
    """Perform OAuth flow and token exchange - reusable helper function"""
    typer.echo(f"🔐 {purpose.title()} Required")
    typer.echo(f"Please sign in to complete {purpose}...")

    try:
        # Perform OAuth flow
        typer.echo("🌐 Starting Google OAuth flow...")
        google_id_token = perform_oauth_flow()
        typer.echo("✅ Google authentication successful!")

        # Exchange for JWT
        typer.echo("🔄 Exchanging token with backend...")
        jwt_token = exchange_token_with_backend(google_id_token)
        typer.echo("✅ Token exchange successful!")

        return jwt_token, google_id_token
    except Exception as e:
        logger.error(f"{purpose.title()} failed: {e}")
        typer.echo(f"❌ {purpose.title()} failed: {e}")
        raise typer.Exit(1)

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
    dynamic: bool = typer.Option(False, "--dynamic", help="Use OAuth 2.1 dynamic client registration"),
    name: Optional[str] = typer.Option(None, "--name", help="Agent name for dynamic client registration")
):
    """Login to the HITL service using Google OAuth 2.0 or OAuth 2.1 dynamic registration"""
    
    # Check if already logged in (either method)
    if is_logged_in() or is_using_oauth():
        typer.echo("✅ Already logged in!")
        return

    # Validate flags
    if dynamic and not name:
        typer.echo("❌ --name is required when using --dynamic")
        raise typer.Exit(1)

    if dynamic:
        # Use OAuth 2.1 dynamic client registration
        try:
            oauth_client = OAuthDynamicClient()
            access_token, agent_name = asyncio.run(oauth_client.perform_dynamic_oauth_flow(name))
            
            typer.echo("✅ OAuth 2.1 dynamic authentication successful!")
            typer.echo()
            typer.echo(f"🤖 Agent '{agent_name}' is ready for use.")
            typer.echo("💡 Use 'hitl-cli request --prompt \"<your prompt>\"' to interact.")
            
        except Exception as e:
            logger.error(f"OAuth 2.1 login failed: {e}")
            typer.echo(f"❌ OAuth 2.1 login failed: {e}")
            raise typer.Exit(1)
    else:
        # Use traditional Google OAuth + JWT flow
        typer.echo("🔐 HITL CLI Login")
        typer.echo("=" * 30)

        try:
            # Use the helper function to perform OAuth and token exchange
            jwt_token, google_id_token = perform_oauth_and_token_exchange("login")

            # Save both JWT and Google ID tokens
            save_token(jwt_token, google_id_token)

            typer.echo("✅ Login successful!")
            typer.echo()
            typer.echo("🤖 Your agent has been automatically created/updated.")
            typer.echo("💡 Use 'hitl-cli agents list' to see your agents.")

        except Exception as e:
            logger.error(f"Login failed: {e}")
            typer.echo(f"❌ Login failed: {e}")
            typer.echo()
            if "Unknown or inactive client" in str(e):
                typer.echo("💡 This is unexpected - the CLI client should be auto-registered.")
                typer.echo("   Please check that the backend server is running properly.")
            raise typer.Exit(1)

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

    # Perform OAuth flow to get admin credentials
    try:
        jwt_token, google_token = perform_oauth_and_token_exchange("admin authentication")
    except Exception as e:
        logger.error(f"Admin authentication failed: {e}")
        typer.echo(f"❌ Admin authentication failed: {e}")
        raise typer.Exit(1)

    # Register the client
    typer.echo()
    typer.echo("📝 Registering OAuth Client...")

    # Create API client with admin token
    api_client = ApiClient()

    # Store the admin token temporarily
    save_token(jwt_token)

    try:
        registration_data = {
            "client_id": client_id,
            "client_name": client_name,
            "client_type": client_type,
            "agent_name": agent_name
        }

        result = asyncio.run(api_client.post("/api/v1/oauth/clients/register", registration_data))

        typer.echo("✅ OAuth client registered successfully!")
        typer.echo(f"   Client ID: {result['client_id']}")
        typer.echo(f"   Client Type: {result['client_type']}")
        typer.echo(f"   Agent Template: {result['agent_name']}")
        typer.echo(f"   Status: {'Active' if result['is_active'] else 'Inactive'}")
        typer.echo()
        typer.echo("🎉 Registration complete!")
        typer.echo("The client application can now authenticate users.")

    except Exception as e:
        logger.error(f"OAuth client registration failed: {e}")
        typer.echo(f"❌ OAuth client registration failed: {e}")
        typer.echo()
        typer.echo("💡 Make sure you have admin privileges and the backend is running.")
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
            if is_using_oauth():
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
            if is_using_oauth():
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
    message: str = typer.Option(..., "--message", help="The notification message to send to the human")
):
    """Send a notification message to the human (fire-and-forget, non-blocking)"""
    async def _async_notify():
        client = MCPClient()

        try:
            typer.echo(f"Sending notification: {message}")

            # Choose authentication method
            if is_using_oauth():
                # Use OAuth Bearer authentication - call tool without agent_id
                response = await client.call_tool("notify_human", {"message": message})
            else:
                # Use traditional JWT authentication - call tool with agent_id from token
                agent_id = get_current_agent_id()
                response = await client.call_tool("notify_human", {"message": message}, agent_id)

            typer.echo(f"{response}")

        except Exception as e:
            logger.error(f"Notification failed: {e}")
            typer.echo(f"Notification failed: {e}")
            raise typer.Exit(1)

    # Run the async function using asyncio.run
    asyncio.run(_async_notify())

if __name__ == "__main__":
    app()
