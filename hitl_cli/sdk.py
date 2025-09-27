"""
HITL SDK - Python SDK for Human-in-the-Loop CLI

This module provides a high-level Python SDK for integrating HITL (Human-in-the-Loop)
functionality into your applications. It wraps the core MCPClient and ApiClient classes
to provide simple, async methods for common HITL operations.

Example usage:
    import asyncio
    from hitl_cli import HITL

    async def main():
        hitl = HITL()
        response = await hitl.request_input("Do you want to proceed?", ["Yes", "No"])
        print(f"Human response: {response}")

    asyncio.run(main())
"""

import logging
from typing import List, Optional

from .mcp_client import MCPClient

logger = logging.getLogger(__name__)


class HITL:
    """
    High-level SDK for Human-in-the-Loop operations.

    This class provides simplified async methods for common HITL operations like
    requesting human input, sending notifications, and notifying task completion.

    Authentication is handled automatically based on the configured method:
    - API Key (if HITL_API_KEY environment variable is set)
    - OAuth Bearer token (if logged in with --dynamic)
    """

    def __init__(self):
        """
        Initialize the HITL SDK client.

        Authentication will be handled automatically based on the configured method.
        """
        self._mcp_client = MCPClient()

    async def request_input(
        self,
        prompt: str,
        choices: Optional[List[str]] = None,
        placeholder: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> str:
        """
        Request input from a human user.

        Args:
            prompt: The question or prompt to show to the human
            choices: Optional list of predefined choices for the human to select from
            placeholder: Optional placeholder text for free-form input
            agent_name: Optional agent name (for OAuth authentication)

        Returns:
            The human's response as a string

        Raises:
            Exception: If authentication fails or the request times out

        Example:
            response = await hitl.request_input(
                "What is your favorite color?",
                ["Red", "Blue", "Green"]
            )
        """
        try:
            # Determine which authentication method to use
            from .auth import is_using_api_key, is_using_oauth

            if is_using_api_key():
                return await self._mcp_client.request_human_input_api_key(
                    prompt=prompt,
                    choices=choices,
                    placeholder_text=placeholder
                )
            elif is_using_oauth():
                return await self._mcp_client.request_human_input_oauth(
                    prompt=prompt,
                    choices=choices,
                    placeholder_text=placeholder,
                    agent_name=agent_name
                )
            else:
                # Fallback to traditional method (will likely fail with deprecation message)
                return await self._mcp_client.request_human_input(
                    prompt=prompt,
                    choices=choices,
                    placeholder_text=placeholder
                )
        except Exception as e:
            logger.error(f"Failed to request human input: {e}")
            raise

    async def notify_completion(
        self,
        summary: str,
        agent_name: Optional[str] = None
    ) -> str:
        """
        Notify a human that a task has been completed.

        Args:
            summary: Summary of the completed task
            agent_name: Optional agent name (for OAuth authentication)

        Returns:
            The human's response as a string

        Raises:
            Exception: If authentication fails or the request times out

        Example:
            response = await hitl.notify_completion("All tests passed successfully!")
        """
        try:
            # Determine which authentication method to use
            from .auth import is_using_api_key, is_using_oauth

            if is_using_api_key():
                return await self._mcp_client.notify_task_completion_api_key(summary=summary)
            elif is_using_oauth():
                return await self._mcp_client.notify_task_completion_oauth(
                    summary=summary,
                    agent_name=agent_name
                )
            else:
                # Fallback to traditional method
                return await self._mcp_client.notify_task_completion(summary=summary)
        except Exception as e:
            logger.error(f"Failed to notify task completion: {e}")
            raise

    async def notify(
        self,
        message: str,
        agent_name: Optional[str] = None
    ) -> str:
        """
        Send a fire-and-forget notification to a human.

        Unlike request_input and notify_completion, this method does not wait for
        a response from the human.

        Args:
            message: The notification message to send
            agent_name: Optional agent name (for OAuth authentication)

        Returns:
            Success confirmation message

        Raises:
            Exception: If authentication fails

        Example:
            await hitl.notify("Processing started in the background")
        """
        try:
            # Determine which authentication method to use
            from .auth import is_using_api_key, is_using_oauth

            if is_using_api_key():
                return await self._mcp_client.notify_human_api_key(message=message)
            elif is_using_oauth():
                return await self._mcp_client.notify_human_oauth(
                    message=message,
                    agent_name=agent_name
                )
            else:
                # Fallback to traditional method
                return await self._mcp_client.notify_human(message=message)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            raise

    async def create_agent(self, name: str) -> str:
        """
        Create a new agent.

        Args:
            name: Name for the new agent

        Returns:
            The agent ID of the created agent

        Raises:
            Exception: If authentication fails or agent creation fails

        Example:
            agent_id = await hitl.create_agent("My Assistant")
        """
        try:
            return await self._mcp_client.create_agent_for_mcp(name)
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise

    async def list_agents(self) -> List[dict]:
        """
        List all agents belonging to the current user.

        Returns:
            List of agent dictionaries with 'id' and 'name' keys

        Raises:
            Exception: If authentication fails

        Example:
            agents = await hitl.list_agents()
            for agent in agents:
                print(f"Agent: {agent['name']} (ID: {agent['id']})")
        """
        try:
            from .api_client import ApiClient
            client = ApiClient()
            return await client.get("/api/v1/agents")
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            raise
