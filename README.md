# HITL CLI - Human-in-the-Loop Command Line Interface

[![Python CI](https://github.com/yourusername/hitl-cli/actions/workflows/python-app.yml/badge.svg)](https://github.com/yourusername/hitl-cli/actions/workflows/python-app.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A reference implementation of a command-line interface for Human-in-the-Loop (HITL) services. This CLI provides seamless integration with HITL backend services, enabling users to manage agents, send requests for human input, and handle authentication through Google OAuth.

## Features

- 🔐 **Secure Authentication**: Google OAuth integration with JWT token management
- 🤖 **Agent Management**: Create, list, and rename AI agents
- 💬 **Human-in-the-Loop Requests**: Send requests for human decisions with customizable choices
- 🔄 **MCP Integration**: Built-in support for Model Context Protocol (MCP) clients
- 📊 **Request Tracking**: Monitor request status and receive human responses
- 🛡️ **Secure Token Storage**: Platform-specific secure credential storage

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

Before using the CLI, you need to configure the backend URL and Google OAuth client ID:

```bash
# Set the backend URL (required)
export HITL_BACKEND_URL="https://your-backend-url.com"

# Set Google OAuth client ID (required for login)
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
```

## Usage

### Authentication

First, authenticate with your Google account:

```bash
hitl-cli login
```

This will open your browser for Google authentication and securely store the access token.

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

Send a request for human input with choices:
```bash
hitl-cli request --prompt "Should I proceed with the deployment?" \
  --choice "Yes" --choice "No" --choice "Ask me later"
```

Send a free-form text request:
```bash
hitl-cli request --prompt "What should I name this file?"
```

Notify completion of a task:
```bash
hitl-cli notify-completion --summary "Task completed successfully. All tests passed."
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

- `hitl_cli/auth.py` - Google OAuth authentication and token management
- `hitl_cli/api_client.py` - HTTP client for backend API communication
- `hitl_cli/mcp_client.py` - MCP client for human-in-the-loop requests
- `hitl_cli/commands.py` - CLI command implementations
- `hitl_cli/config.py` - Configuration management
- `hitl_cli/main.py` - Entry point and CLI setup

## Security

- Tokens are stored securely using platform-specific credential storage:
  - macOS: Keychain
  - Linux: Secret Service API (e.g., GNOME Keyring)
  - Windows: Windows Credential Locker
- All API communications use HTTPS
- JWT tokens expire after a configurable period
- Google OAuth tokens are never stored directly

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
- Authentication powered by Google OAuth 2.0

## Related Projects

- [hitl-shin-relay](https://github.com/yourusername/hitl-shin-relay) - The backend service for HITL (private repository)