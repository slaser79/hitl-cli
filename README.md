# HITL CLI - Human-in-the-Loop Command Line Interface

[![Python CI](https://github.com/yourusername/hitl-cli/actions/workflows/python-app.yml/badge.svg)](https://github.com/yourusername/hitl-cli/actions/workflows/python-app.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A reference implementation of a command-line interface for Human-in-the-Loop (HITL) services. This CLI provides seamless integration with HITL backend services, enabling users to manage agents, send requests for human input, and handle authentication through Google OAuth.

## Features

- 🔐 **Dual Authentication**: Traditional Google OAuth + new OAuth 2.1 dynamic client registration
- ⚡ **Zero-Config Auth**: Dynamic client registration eliminates manual OAuth setup
- 🛡️ **Enhanced Security**: PKCE (Proof Key for Code Exchange) support for OAuth 2.1
- 🤖 **Agent Management**: Create, list, and rename AI agents with customizable names
- 💬 **Human-in-the-Loop Requests**: Send requests for human decisions with customizable choices
- 🔄 **MCP Integration**: Built-in support for Model Context Protocol (MCP) clients
- 📊 **Request Tracking**: Monitor request status and receive human responses
- 🔑 **Secure Token Storage**: Platform-specific secure credential storage with automatic refresh

## Installation

### Using Nix (Recommended)

If you have Nix installed, you can use the provided flake for a reproducible development environment:

```bash
# Enter the development shell
nix develop

# The virtual environment will be automatically activated
# Dependencies will be synced automatically
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/hitl-cli.git
cd hitl-cli

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

### Using uv

```bash
# Clone the repository
git clone https://github.com/yourusername/hitl-cli.git
cd hitl-cli

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

## Configuration

### Quick Start (Recommended - OAuth 2.1)

For the easiest setup with zero configuration:

```bash
# Set the backend URL (required)
export HITL_BACKEND_URL="https://your-backend-url.com"

# Login with automatic client registration
hitl-cli login --dynamic --name "My Agent"
```

### Traditional Setup (Google OAuth 2.0)

For traditional OAuth setup:

```bash
# Set the backend URL (required)
export HITL_BACKEND_URL="https://your-backend-url.com"

# Set Google OAuth client ID (required for traditional login)
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"

# Login with traditional flow
hitl-cli login
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

| Feature | OAuth 2.1 Dynamic | Traditional OAuth 2.0 |
|---------|-------------------|------------------------|
| **Setup Required** | None (zero-config) | Manual client ID setup |
| **Security** | PKCE + Dynamic registration | Standard OAuth 2.0 |
| **Agent Management** | Automatic via `--name` | Manual via `agents` commands |
| **Token Type** | Bearer tokens | JWT tokens |
| **RFC Standards** | RFC 7591 + RFC 7636 | RFC 6749 |
| **Recommended For** | New users, agents | Existing integrations |

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

# Notify completion of a task
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

## Troubleshooting

### OAuth 2.1 Issues

**Problem**: Dynamic client registration fails
```bash
# Clear cached client data and retry
rm ~/.hitl/oauth_client.json
hitl-cli login --dynamic --name "My Agent"
```

**Problem**: Bearer token expired
```bash
# Token should refresh automatically, but if not:
hitl-cli logout
hitl-cli login --dynamic --name "My Agent"
```

### Traditional OAuth Issues

**Problem**: Missing GOOGLE_CLIENT_ID
```bash
# Set the environment variable
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
hitl-cli login
```

### General Issues

**Problem**: Connection errors
```bash
# Verify backend URL
echo $HITL_BACKEND_URL
curl -v $HITL_BACKEND_URL/health

# Check authentication status
hitl-cli status
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hitl_cli --cov-report=term-missing

# Run specific test file
pytest tests/test_auth_flow.py
```

### Code Quality

```bash
# Install development dependencies
uv add --dev ruff

# Check code style
ruff check hitl_cli/

# Format code
ruff format hitl_cli/
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