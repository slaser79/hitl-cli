
# HITL-CLI: Human-in-the-Loop Command-Line Interface and SDK

**hitl-cli** is the official reference client for the [Human-in-the-Loop (HITL) mobile application](https://hitlrelay.app). It provides a powerful command-line interface (CLI) and Python SDK to programmatically request input from, and send notifications to, a human user via their mobile device.

It features zero-config, secure authentication using OAuth 2.1 and supports end-to-end encryption (E2EE) for confidential interactions.

## Features

- **Command-Line Interface:** Easily send HITL requests from your terminal or shell scripts.
- **Python SDK:** Integrate human-in-the-loop workflows directly into your Python applications.
- **Secure by Default:** Uses modern OAuth 2.1 with PKCE for user authentication. No manual client setup needed.
- **End-to-End Encryption:** A local proxy mode enables E2EE for use with tools like Claude Desktop, ensuring the server only handles encrypted data.
- **Service Authentication:** Supports API key authentication for non-interactive environments (e.g., CI/CD, backend services).

## 1. Installation

Install `hitl-cli` from PyPI using `pip` (or your preferred Python package manager):

```bash
pip install hitl-cli
```

## 2. Authentication

You can authenticate in two ways: OAuth 2.1 (for users) or API Keys (for services).

### Option A: OAuth 2.1 (Recommended for Users)

This is the standard method for interactive use. The `login` command will open your browser to authenticate and securely store your credentials.

1.  **Run the login command:**
    ```bash
    hitl-cli login --name "My Workstation"
    ```
    *This will open a browser window for you to log in or sign up.*

2.  **Authenticate in the browser.**

3.  Upon success, your credentials will be securely stored, and your CLI will be ready to use.

### Option B: API Key (for Services and Automation)

For non-interactive environments, you can authenticate by setting an environment variable.

```bash
export HITL_API_KEY="your_api_key_here"

# Now you can use the CLI without the login step
hitl-cli notify --message "The nightly build has completed."
```

## 3. Usage Patterns

### A. As a Command-Line Tool

Quickly request human input or send notifications directly from your terminal.

**Example: Requesting Input**
```bash
# Request a simple confirmation
hitl-cli request --prompt "Do you approve the deployment to production?"

# Provide multiple choices
hitl-cli request --prompt "Which environment to deploy?" --choice "Staging" --choice "Production"
```

**Example: Sending a Notification**
```bash
hitl-cli notify --message "The data processing job has started."
```

### B. As a Python SDK

Integrate HITL workflows into your Python applications using the `HITL` class.

```python
import asyncio
from hitl_cli import HITL

async def main():
    # The SDK automatically uses your configured credentials (OAuth or API Key)
    hitl = HITL()

    try:
        # Request input and wait for the response
        user_response = await hitl.request_input(
            "Do you want to proceed with the database migration?",
            choices=["Yes", "No", "Postpone"]
        )

        print(f"Human response: {user_response}")

        if user_response == "Yes":
            await hitl.notify("Database migration started.")
            # ... run migration ...
            await hitl.notify_completion("The database migration is complete!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### C. End-to-End Encryption with a Local Proxy

For maximum security, `hitl-cli` can act as a local [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) proxy. This allows tools like Claude Desktop to interact with a human while ensuring that the prompt and response are end-to-end encrypted. The HITL server only relays the encrypted data and never sees the plaintext content.

1.  **Log in first:**
    ```bash
    hitl-cli login --name "My E2EE Agent"
    ```

2.  **Configure your MCP client (e.g., Claude Desktop's `mcp_servers.json`):**
    ```json
    {
      "mcpServers": {
        "human": {
          "command": "hitl-cli",
          "args": ["proxy", "https://hitlrelay.app/mcp-server/mcp/"]
        }
      }
    }
    ```
The proxy will automatically encrypt the request and decrypt the response. The llm will still use the unecrypted enpoints and the hit-cli proxy will use the endpoints ending in e2ee

    ```python
    human.request_human_input(prompt="Please provide the API key for the staging environment.")
    ```

### D. Continuous Interaction Hook for Claude Code

The `hitl-hook-review-and-continue` hook provides a powerful way to create a continuous interaction loop with Claude Code. When Claude finishes a task, this hook intercepts the stop event, asks for your confirmation via the HITL app, and feeds your response back to Claude as new instructions.

**Setup:**

Add the following to your Claude Code settings file:
- `~/.claude/settings.json` (user-level, affects all projects)
- `.claude/settings.local.json` (project-level, gitignored)

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "hitl-hook-review-and-continue"
          }
        ]
      }
    ]
  }
}
```

**How it works:**
- When Claude Code finishes responding, the hook executes
- A prompt appears on your HITL mobile app
- You can review what Claude did and provide feedback
- Your response is fed back to Claude as new instructions
- This creates an interactive review-and-continue workflow

For more details on hooks, see the [Claude Code hooks documentation](https://docs.claude.com/en/docs/claude-code/hooks).

This turns `hitl-cli` into a remote control for your AI assistant.

