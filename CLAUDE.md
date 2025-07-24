# CLAUDE.md - Project Guidelines for `hitl-cli`

This document provides essential guidelines, conventions, and operational procedures for the `hitl-cli` project. These guidelines ensure consistent development practices and efficient debugging.

## 1. Project Overview

`hitl-cli` is a standalone Python command-line interface that serves as a reference implementation for Human-in-the-Loop (HITL) services. It is designed to be:
- **Open Source**: MIT licensed for community use and contribution
- **Standalone**: No direct dependencies on the private `hitl-shin-relay` backend
- **Extensible**: Clean architecture allowing easy addition of new commands and features

## 2. Development Environment

### Nix Setup
The project uses Nix for reproducible development environments:

```bash
# Enter development shell
nix develop

# This automatically:
# - Activates Python 3.12 environment
# - Creates/activates virtual environment
# - Installs uv package manager
# - Syncs all dependencies
```

### Manual Setup (without Nix)
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
# OR using uv:
uv sync
```

## 3. Project Structure

```
hitl-cli/
├── hitl_cli/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # CLI entry point
│   ├── auth.py              # Google OAuth authentication
│   ├── api_client.py        # Backend API client
│   ├── mcp_client.py        # MCP protocol client
│   ├── commands.py          # CLI command implementations
│   └── config.py            # Configuration management
├── tests/
│   ├── test_auth_flow.py    # Authentication tests
│   ├── test_api_client.py   # API client tests
│   └── test_mcp_client.py   # MCP client tests
├── .github/workflows/       # CI/CD configuration
├── pyproject.toml           # Project metadata and dependencies
├── flake.nix               # Nix development environment
└── README.md               # User documentation
```

## 4. Key Dependencies

- **typer**: Modern CLI framework with automatic help generation
- **httpx**: Async-capable HTTP client for API communication
- **google-auth**: Official Google authentication library
- **google-auth-oauthlib**: OAuth 2.0 flow implementation
- **fastmcp**: Model Context Protocol client implementation
- **pyjwt**: JWT token handling for authentication

## 5. Development Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints for all function signatures
- Keep functions focused and single-purpose
- Document complex logic with inline comments

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hitl_cli --cov-report=term-missing

# Run specific test
pytest tests/test_auth_flow.py -v
```

### Error Handling
- Always handle network errors gracefully
- Provide clear error messages to users
- Use Typer's exception handling for CLI errors
- Log errors appropriately without exposing sensitive data

## 6. Authentication Flow

1. **Google OAuth Login**:
   - User runs `hitl-cli login`
   - Browser opens for Google authentication
   - OAuth callback provides tokens
   - Tokens stored securely in platform keyring

2. **Token Management**:
   - Access tokens are short-lived
   - Refresh tokens used for renewal
   - Secure storage using keyring library
   - Automatic token refresh on API calls

3. **Backend Integration**:
   - Exchange Google token for backend JWT
   - Include JWT in all API requests
   - Handle token expiration gracefully

## 7. Configuration

Environment variables:
- `HITL_BACKEND_URL`: Backend API base URL (required)
- `GOOGLE_CLIENT_ID`: Google OAuth client ID (required)
- `HITL_LOG_LEVEL`: Logging level (optional, default: INFO)

Configuration precedence:
1. Command-line arguments
2. Environment variables
3. Configuration file (~/.hitl/config.json)
4. Default values

## 8. Common Issues and Solutions

### Authentication Issues
**Problem**: "Token has expired" errors
**Solution**: 
- Ensure system time is synchronized
- Check token refresh logic
- Verify backend JWT configuration

### Network Issues
**Problem**: Connection timeouts or failures
**Solution**:
- Check backend URL configuration
- Verify network connectivity
- Implement retry logic with exponential backoff

### MCP Client Issues
**Problem**: MCP requests not being received
**Solution**:
- Verify agent is properly registered
- Check WebSocket connection stability
- Ensure proper JWT token in MCP requests

## 9. Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md (create if needed)
3. Run full test suite
4. Create git tag: `git tag v0.1.0`
5. Push tag: `git push origin v0.1.0`
6. GitHub Actions will build and create release

## 10. Security Considerations

- **Never** commit sensitive data (tokens, secrets)
- Use secure credential storage (keyring)
- Validate all user inputs
- Sanitize data before logging
- Keep dependencies updated for security patches

## 11. Debugging Tips

Enable debug logging:
```bash
export HITL_LOG_LEVEL=DEBUG
hitl-cli --debug <command>
```

Common debug points:
- Authentication flow in `auth.py`
- API requests/responses in `api_client.py`
- Token storage/retrieval
- MCP WebSocket connections

## 12. Contributing

1. Fork the repository
2. Create feature branch from `main`
3. Write tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

### Commit Message Format
```
<type>: <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

## 13. Future Enhancements

Planned features:
- [ ] Offline mode with request queuing
- [ ] Multiple backend support
- [ ] Plugin system for custom commands
- [ ] Interactive mode
- [ ] Request templates
- [ ] Bulk operations

## 14. Maintainer Notes

- Keep README.md user-focused
- Update CLAUDE.md for developer guidelines
- Monitor issue tracker for common problems
- Regular dependency updates (monthly)
- Backward compatibility for at least 2 versions