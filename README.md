# HITL CLI - Human-in-the-Loop Command Line Interface

[![Python CI](https://github.com/yourusername/hitl-cli/actions/workflows/python-app.yml/badge.svg)](https://github.com/yourusername/hitl-cli/actions/workflows/python-app.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A reference implementation of a command-line interface for Human-in-the-Loop (HITL) services. This CLI provides seamless integration with HITL backend services, enabling users to manage agents, send requests for human input, and handle authentication through Google OAuth.

## Features

- 🔐 **Dual Authentication**: Traditional Google OAuth + new OAuth 2.1 dynamic client registration
- ⚡ **Zero-Config Auth**: Dynamic client registration eliminates manual OAuth setup
- 🛡️ **Enhanced Security**: PKCE (Proof Key for Code Exchange) support for OAuth 2.1
- 🔒 **End-to-End Encryption**: Optional E2EE proxy mode for maximum privacy
- 🛡️ **Cryptographic Guardian**: Transparent encryption between agents and humans
- 🤖 **Agent Management**: Create, list, and rename AI agents with customizable names
- 💬 **Human-in-the-Loop Requests**: Send requests for human decisions with customizable choices
- 🔄 **MCP Integration**: Built-in support for Model Context Protocol (MCP) clients
- 📊 **Request Tracking**: Monitor request status and receive human responses
- 🔑 **Secure Token Storage**: Platform-specific secure credential storage with automatic refresh

## Installation


## Nix 

The project uses Nix for dependency management. Ensure you have Nix installed on your system. Then, you can use the following commands to set up the development environment:

```bash
# The virtual environment will be automatically activated
# Dependencies will be synced automatically
```

### Using pip

```bash
# Clone the repository
nix develop -c git clone https://github.com/yourusername/hitl-cli.git
nix develop -c cd hitl-cli

# Create a virtual environment
nix develop -c python -m venv .venv
nix develop -c source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
nix develop -c pip install -e .
```

### Using uv

```bash
# Clone the repository
nix develop -c git clone https://github.com/yourusername/hitl-cli.git
nix develop -c cd hitl-cli

# Create virtual environment and install
nix develop -c uv venv
nix develop -c source .venv/bin/activate  # On Windows: .venv\Scripts\activate
nix develop -c uv sync
```

## Configuration

### Quick Start (Recommended - OAuth 2.1)

For the easiest setup with zero configuration:

```bash
# Set the backend URL (required)
nix develop -c export HITL_SERVER_URL="https://your-backend-url.com"

# Login with automatic client registration
nix develop -c hitl-cli login --dynamic --name "My Agent"
```

### Traditional Setup (Google OAuth 2.0)

For traditional OAuth setup:

```bash
# Set the backend URL (required)
nix develop -c export HITL_SERVER_URL="https://your-backend-url.com"

# Set Google OAuth client ID (required for traditional login)
nix develop -c export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"

# Login with traditional flow
### API Key Authentication (for non-interactive use)

For non-interactive environments like scripts, background services, or CI/CD pipelines, you can authenticate using an API key. This method bypasses the interactive `hitl-cli login` flow.

```bash
# Set the backend URL (required)
nix develop -c export HITL_SERVER_URL="https://your-backend-url.com"

# Set the API Key (replaces login)
nix develop -c export HITL_API_KEY="your-secret-api-key"

# Now you can use the CLI directly
nix develop -c hitl-cli request --prompt "This is a test from a script."
```
**Note**: When `HITL_API_KEY` is set, it takes precedence over any existing OAuth tokens.
nix develop -c hitl-cli login
```

## Usage

### Authentication

#### OAuth 2.1 Dynamic Registration (Recommended)

Authenticate with zero configuration using dynamic client registration:

```bash
# Login with automatic OAuth client setup
hitl-cli login --dynamic --name "My Development Agent"
```

This will:
1. Automatically register a new OAuth client with the server
2. Open your browser for Google authentication with PKCE security
3. Store the bearer token securely for future requests
4. Set up your agent with the specified name

#### Traditional Google OAuth 2.0

Authenticate using traditional OAuth (requires manual client setup):

```bash
# Traditional login (requires GOOGLE_CLIENT_ID environment variable)
hitl-cli login
```

This will open your browser for Google authentication and exchange tokens with the backend server.

#### Authentication Method Comparison

| Feature | OAuth 2.1 Dynamic | Traditional OAuth 2.0 | API Key |
|---------|-------------------|------------------------|---------|
| **Setup Required** | None (zero-config) | Manual client ID setup | Environment variable (`HITL_API_KEY`) |
| **Security** | PKCE + Dynamic registration | Standard OAuth 2.0 | Bearer token (long-lived) |
| **Agent Management** | Automatic via `--name` | Manual via `agents` commands | N/A (uses user's default agent) |
| **Token Type** | Bearer tokens | JWT tokens | Static API Key |
| **RFC Standards** | RFC 7591 + RFC 7636 | RFC 6749 | N/A |
| **Recommended For** | New users, agents | Existing integrations | Scripts, CI/CD, background services |

**Recommendation**: Use OAuth 2.1 dynamic registration (`--dynamic --name`) for new setups as it provides better security and requires no manual configuration.

### Managing Agents

List all your agents:
```bash
hitl-cli agents list
```

Create a new agent:
```bash
hitl-cli agents create --name "My Assistant"
```

Rename an agent:
```bash
hitl-cli agents rename <agent-id> --name "New Name"
```

### Sending HITL Requests

#### With OAuth 2.1 (Bearer Token Authentication)

```bash
# Send a request with choices
hitl-cli request --prompt "Should I proceed with the deployment?" \
  --choice "Yes" --choice "No" --choice "Ask me later"

# Send a free-form text request
hitl-cli request --prompt "What should I name this file?"

# Send a one-way notification (fire-and-forget)
hitl-cli notify --message "Task started: Processing data files"
hitl-cli notify --message "Step 2 of 5: Analyzing dependencies"

# Notify completion of a task (waits for response)
hitl-cli notify-completion --summary "Task completed successfully. All tests passed."
```

#### With Traditional OAuth (Agent-Based)

```bash
# Send requests with specific agent ID
hitl-cli request --prompt "Should I proceed?" --agent-id "agent-123"

# Create agents first if needed
hitl-cli agents create --name "My Assistant"
hitl-cli agents list  # Get agent ID
```

### One-Way Notifications

The `notify` command sends non-blocking notifications that don't require a response:

```bash
# Basic notification
hitl-cli notify --message "Starting data processing..."

# Progress updates
hitl-cli notify --message "Processing: 50% complete"
hitl-cli notify --message "Processing: 100% complete"

# Status notifications
hitl-cli notify --message "Server health check: All systems operational"
hitl-cli notify --message "Warning: High memory usage detected"
```

**Key Features:**
- Fire-and-forget: Returns immediately without waiting
- No user interaction required
- Appears as toast notification on mobile device
- Ideal for progress updates and status messages

### Other Commands

Check authentication status:
```bash
hitl-cli status
```

Logout:
```bash
hitl-cli logout
```

Get help:
```bash
hitl-cli --help
hitl-cli <command> --help
```

## Interactive `Stop` Hook for Remote Review and Continuation

This feature allows users to review Claude's output on their phone and provide follow-up instructions without interacting with the terminal.

**1. Installation and Login**

Ensure you have the latest version of `hitl-cli` installed and are logged in:

```bash
uv pip install --upgrade hitl-cli
hitl-cli login --dynamic --name "Claude Code Interactive Session"
```

**2. Configure the Claude Code `Stop` Hook**

To enable the interactive review-and-continue workflow, add the following `hooks` configuration to your `.claude/settings.json` file. **This is the only hook needed for this workflow.**

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "hitl-hook-review-and-continue",
            "timeout": 600
          }
        ]
      }
    ]
  }
}
```
> **Note:** The `timeout` is set to 600 seconds (10 minutes) to give you ample time to review the request on your phone and respond without the hook timing out. Adjust as needed.

---

**3. The User Experience in Action**

With this setup, a typical interaction will flow like this:

1.  **You:** (In Claude Code terminal) `Okay, please refactor the auth.py module to use the new UserStore class.`
2.  **Claude:** (Performs a series of `Read`, `Edit`, `Write` actions, which you can see in the terminal). When it believes it's finished, it stops.
3.  **`Stop` Hook Triggers:** Your terminal pauses.
4.  **Your Phone:** You receive a notification from the HITL app. You open it and see a message like:
    ```
    Claude has completed its task. Please review the final actions below.

    Click 'Approve' to finish, or reply with new instructions to continue.

    --- Turn -2 ---
    {
      "type": "tool_code",
      "tool_name": "Read",
      "tool_input": {
        "file_path": "hitl_cli/auth.py"
      }
    }

    --- Turn -1 ---
    {
      "type": "tool_code",
      "tool_name": "Write",
      "tool_input": {
        "file_path": "hitl_cli/auth.py",
        "content": "# ... new, refactored code here ..."
      }
    }
    ```
5.  **You Decide:**
    *   **Scenario A (Approval):** The code looks perfect. You tap the `Approve` button. The `hitl-cli` command in the terminal prints "Approve" and exits. Your Claude Code session cleanly ends its turn and waits for your next typed command.
    *   **Scenario B (Continuation):** You notice Claude forgot to add docstrings. You type a reply directly into the HITL app: `Looks great, but please add docstrings to the new methods.` You hit send. The `hitl-cli` command in the terminal prints that exact string and exits. The hook script tells Claude to block the stop and uses your reply as the new instruction.
6.  **Claude:** The terminal becomes active again, and Claude says something like: `Understood. I will add docstrings to the new methods in auth.py.` and continues working.

This creates a powerful, seamless loop for remote-controlling complex tasks.

## End-to-End Encryption (E2EE) Proxy Mode

For privacy-conscious users who require that the HITL server cannot decipher their messages, the CLI provides a **Cryptographic Guardian** proxy mode that enables transparent end-to-end encryption.

### Quick Setup

1. **Authenticate with E2EE**:
```bash
hitl-cli login --dynamic --name "My Secure Agent"
```

2. **Start the E2EE Proxy**:
```bash
hitl-cli proxy https://hitl-relay.app/mcp-server/mcp/
```

3. **Configure Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "hitl-shin-relay": {
      "command": "hitl-cli",
      "args": ["proxy", "https://hitlrelay.app/mcp-server/mcp/"]
    }
  }
}
```
4. ** Configure for Claude Code**
```bash
claude mcp add human-in-the-loop-e2ee -- /Users/yourUser/lab/hitl/hitl-cli/result/bin/hitl-cli proxy https://hitlrelay.app/mcp-server/mcp/
```


### How E2EE Proxy Works

1. **Transparent Operation**: Claude Desktop sees only standard plaintext tools
2. **Automatic Encryption**: Proxy intercepts requests and encrypts them
3. **Key Management**: Automatic keypair generation and secure storage
4. **Mobile Integration**: Mobile app seamlessly decrypts and responds
5. **Response Decryption**: Proxy decrypts responses before returning to Claude

### Security Benefits

- ✅ **Zero-Knowledge Server**: Server sees only encrypted blobs
- ✅ **End-to-End Protection**: Only you and your devices can read messages
- ✅ **Forward Secrecy**: Compromise of server doesn't reveal past messages
- ✅ **Transparent to Claude**: No changes required to LLM behavior

### Key Storage

- **Agent Keys**: `~/.config/hitl-shin-relay/agent.key` (600 permissions)
- **OAuth Tokens**: `~/.hitl/oauth_token.json` (600 permissions)
- **Mobile Keys**: Device secure keychain (iOS/Android)

For detailed E2EE setup instructions, see the [E2EE Onboarding Guide](../docs/onboarding_e2ee.md).

## Troubleshooting

### OAuth 2.1 Issues

**Problem**: Dynamic client registration fails
```bash
# Clear cached client data and retry
rm ~/.hitl/oauth_client.json
nix develop -c hitl-cli login --dynamic --name "My Agent"
```

**Problem**: Bearer token expired
```bash
# Token should refresh automatically, but if not:
nix develop -c hitl-cli logout
nix develop -c hitl-cli login --dynamic --name "My Agent"
```

### Traditional OAuth Issues

**Problem**: Missing GOOGLE_CLIENT_ID
```bash
# Set the environment variable
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
nix develop -c hitl-cli login
```

### General Issues

**Problem**: Connection errors
```bash
# Verify backend URL
echo $HITL_SERVER_URL
curl -v $HITL_SERVER_URL/health

# Check authentication status
nix develop -c hitl-cli status
```

### E2EE Proxy Issues

**Problem**: Proxy not responding to Claude Desktop
```bash
# Check if proxy is running
ps aux | grep "hitl-cli proxy"

# Restart proxy
nix develop -c hitl-cli proxy https://hitlrelay.app/mcp-server/mcp/
```

**Problem**: "Encryption failed" errors
```bash
# Verify key generation
ls -la ~/.config/hitl-shin-relay/agent.key

# Regenerate keys if necessary
rm ~/.config/hitl-shin-relay/agent.key
nix develop -c hitl-cli login --dynamic --name "My Agent"
```

**Problem**: Mobile app shows encrypted text instead of decrypted content
```bash
# This indicates mobile app decryption failure
# Check that mobile app is authenticated with same Google account
# Force-close and restart mobile app to regenerate keys
```

## Development

### Running Tests

```bash
# Run all tests
nix develop -c pytest

# Run with coverage
nix develop -c pytest --cov=hitl_cli --cov-report=term-missing

# Run specific test file
nix develop -c pytest tests/test_auth_flow.py
```

### Code Quality

```bash
# Install development dependencies
nix develop -c uv add --dev ruff

# Check code style
nix develop -c ruff check hitl_cli/

# Format code
nix develop -c ruff format hitl_cli/
```

### Building

```bash
# Build distribution packages
python -m build

# This creates wheel and source distributions in dist/
```

## Architecture

The HITL CLI is structured as follows:

- `hitl_cli/auth.py` - Dual authentication system (OAuth 2.1 + traditional Google OAuth)
- `hitl_cli/api_client.py` - HTTP client for backend API communication
- `hitl_cli/mcp_client.py` - MCP client with Bearer token and JWT authentication
- `hitl_cli/commands.py` - CLI command implementations
- `hitl_cli/config.py` - Configuration management and secure token storage
- `hitl_cli/main.py` - Entry point and CLI setup

### Authentication Flows

#### OAuth 2.1 Dynamic Registration Flow
1. **Dynamic Registration**: CLI registers a new OAuth client automatically (RFC 7591)
2. **PKCE Authorization**: Secure authorization with Proof Key for Code Exchange (RFC 7636)
3. **Bearer Token**: Direct OAuth bearer token for MCP operations
4. **Agent Context**: Agent name embedded in authentication headers

#### Traditional OAuth 2.0 Flow
1. **Google OAuth**: Standard Google OAuth 2.0 authentication
2. **JWT Exchange**: Backend exchanges Google token for internal JWT
3. **Agent Management**: Manual agent creation and management
4. **API Authentication**: JWT-based API authentication

## Security

### OAuth 2.1 Security Features
- **PKCE (Proof Key for Code Exchange)**: Prevents authorization code interception attacks
- **Dynamic Client Registration**: No hardcoded client credentials in source code
- **State Parameter**: CSRF protection during OAuth flow
- **Bearer Token Storage**: Secure file permissions (600) for token files
- **Automatic Token Refresh**: Seamless token renewal without re-authentication

### Platform Security
- Tokens are stored securely using platform-specific credential storage:
  - macOS: Keychain
  - Linux: Secret Service API (e.g., GNOME Keyring)
  - Windows: Windows Credential Locker
- All API communications use HTTPS
- OAuth 2.1 tokens expire after a configurable period
- Google OAuth tokens are never stored directly in traditional flow

### RFC Compliance
- **RFC 7591**: OAuth 2.0 Dynamic Client Registration Protocol
- **RFC 7636**: Proof Key for Code Exchange by OAuth Public Clients
- **RFC 6749**: OAuth 2.0 Authorization Framework (traditional flow)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI interface
- Uses [FastMCP](https://github.com/jlowin/fastmcp) for MCP protocol support
- Dual authentication: Google OAuth 2.0 (traditional) + OAuth 2.1 with PKCE (modern)
- OAuth 2.1 implementation uses [Authlib](https://authlib.org/) for RFC compliance
- Dynamic client registration following RFC 7591 standards

## Related Projects

- [hitl-shin-relay](https://github.com/yourusername/hitl-shin-relay) - The backend service for HITL (private repository)
