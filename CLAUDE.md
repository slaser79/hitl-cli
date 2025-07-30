# CLAUDE.md - Project Guidelines for `hitl-cli`

This document provides essential guidelines, conventions, and operational procedures for the `hitl-cli` project. These guidelines ensure consistent development practices and efficient debugging.

## 1. Project Overview

`hitl-cli` is a standalone Python command-line interface that serves as a reference implementation for Human-in-the-Loop (HITL) services. It is designed to be:
- **Open Source**: MIT licensed for community use and contribution
- **Standalone**: No direct dependencies on the private `hitl-shin-relay` backend
- **Extensible**: Clean architecture allowing easy addition of new commands and features
- **Modern Authentication**: Implements OAuth 2.1 with dynamic client registration and PKCE
- **Dual-Mode**: Supports both traditional OAuth 2.0 and modern OAuth 2.1 flows
- **Zero-Config**: Dynamic client registration eliminates manual OAuth setup

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
- **google-auth**: Official Google authentication library (traditional flow)
- **google-auth-oauthlib**: OAuth 2.0 flow implementation (traditional flow)
- **authlib**: RFC-compliant OAuth 2.1 implementation with PKCE support
- **fastmcp**: Model Context Protocol client implementation
- **pyjwt**: JWT token handling for authentication
- **keyring**: Secure cross-platform credential storage

## 5. Development Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints for all function signatures
- Keep functions focused and single-purpose
- Document complex logic with inline comments

### Testing

#### OAuth 2.1 Tests
```bash
# Run OAuth 2.1 specific tests
pytest tests/test_oauth_dynamic_registration.py -v

# Test PKCE implementation
pytest tests/test_oauth_dynamic_registration.py::test_pkce_code_generation -v

# Test dynamic client registration
pytest tests/test_oauth_dynamic_registration.py::test_dynamic_client_registration -v
```

#### General Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hitl_cli --cov-report=term-missing

# Run specific test
pytest tests/test_auth_flow.py -v

# Test both authentication flows
pytest tests/test_auth_flow.py tests/test_oauth_dynamic_registration.py -v
```

#### Manual Testing OAuth 2.1
```bash
# Test complete OAuth 2.1 flow
python test_oauth_implementation.py

# Test integration with backend
python oauth_integration_demo.py
```

### Error Handling
- Always handle network errors gracefully
- Provide clear error messages to users
- Use Typer's exception handling for CLI errors
- Log errors appropriately without exposing sensitive data

## 6. Authentication Flows

### OAuth 2.1 Dynamic Registration Flow (Recommended)

1. **Dynamic Client Registration** (RFC 7591):
   - User runs `hitl-cli login --dynamic --name "Agent Name"`
   - CLI automatically registers OAuth client with server
   - No hardcoded client credentials required
   - Client credentials stored securely locally

2. **PKCE Authorization** (RFC 7636):
   - Generate cryptographically secure code verifier
   - Create SHA256 code challenge
   - Include PKCE parameters in authorization URL
   - Prevent authorization code interception attacks

3. **OAuth 2.1 Flow**:
   - Browser opens for Google authentication
   - Authorization code exchanged for bearer token
   - X-MCP-Agent-Name header identifies agent context
   - Direct bearer token authentication for MCP operations

4. **Token Management**:
   - Bearer tokens stored with 600 file permissions
   - Automatic token refresh using refresh tokens
   - Token expiry validation before requests
   - Secure deletion on logout

### Traditional OAuth 2.0 Flow (Legacy)

1. **Google OAuth Login**:
   - User runs `hitl-cli login`
   - Requires GOOGLE_CLIENT_ID environment variable
   - Browser opens for Google authentication
   - OAuth callback provides tokens
   - Tokens stored securely in platform keyring

2. **Backend JWT Exchange**:
   - Exchange Google token for backend JWT
   - JWT contains user and agent context
   - Include JWT in all API requests
   - Handle token expiration gracefully

3. **Agent Management**:
   - Manual agent creation via API
   - Agent ID required for requests
   - Separate agent management commands

## 7. Configuration

### Environment Variables
- `HITL_BACKEND_URL`: Backend API base URL (required for both flows)
- `GOOGLE_CLIENT_ID`: Google OAuth client ID (required for traditional flow only)
- `HITL_LOG_LEVEL`: Logging level (optional, default: INFO)

### OAuth 2.1 Configuration Files
- `~/.hitl/oauth_client.json`: Dynamic client registration data
- `~/.hitl/oauth_token.json`: Bearer tokens (600 permissions)
- `~/.hitl/config.json`: General CLI configuration

### Configuration Precedence
1. Command-line arguments (`--dynamic`, `--name`)
2. Environment variables
3. Configuration files
4. Default values

### OAuth 2.1 Endpoints
The implementation expects these backend endpoints:
- `POST /api/v1/oauth/register`: RFC 7591 dynamic client registration
- `GET /api/v1/oauth/authorize`: OAuth 2.1 + PKCE authorization
- `POST /api/v1/oauth/token`: Token exchange and refresh
- `POST /mcp-server/mcp`: MCP requests with Bearer authentication

## 8. Common Issues and Solutions

### OAuth 2.1 Authentication Issues
**Problem**: Dynamic client registration fails
**Solution**: 
- Verify backend URL is correct and accessible
- Check network connectivity to OAuth endpoints
- Ensure backend implements RFC 7591 dynamic registration
- Clear `~/.hitl/oauth_client.json` and retry

**Problem**: PKCE validation errors
**Solution**:
- Ensure code verifier is properly generated (43-128 characters)
- Verify SHA256 challenge calculation
- Check base64url encoding (no padding)
- System time synchronization for state parameter

**Problem**: Bearer token expired
**Solution**:
- Automatic refresh should handle this
- If refresh fails, re-authenticate with `hitl-cli login --dynamic --name "Agent"`
- Check `~/.hitl/oauth_token.json` permissions (should be 600)

### Traditional Authentication Issues
**Problem**: "Token has expired" errors
**Solution**: 
- Ensure system time is synchronized
- Check token refresh logic
- Verify backend JWT configuration
- Re-authenticate with `hitl-cli login`

### Network Issues
**Problem**: Connection timeouts or failures
**Solution**:
- Check backend URL configuration
- Verify network connectivity
- Implement retry logic with exponential backoff
- Test with curl: `curl -v $HITL_BACKEND_URL/health`

### MCP Client Issues
**Problem**: MCP requests not being received
**Solution**:
- For OAuth 2.1: Verify bearer token is valid
- For traditional: Verify agent is properly registered
- Check WebSocket connection stability
- Ensure proper authentication headers in MCP requests
- Test with `hitl-cli status` to verify authentication

## 9. Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md (create if needed)
3. Run full test suite
4. Create git tag: `git tag v0.1.0`
5. Push tag: `git push origin v0.1.0`
6. GitHub Actions will build and create release

## 10. Security Considerations

### OAuth 2.1 Security
- **PKCE Implementation**: Prevents authorization code interception
- **Dynamic Registration**: No hardcoded client secrets in source code
- **State Parameter**: CSRF protection with cryptographically secure random values
- **Token Storage**: File permissions set to 600 (owner read/write only)
- **Code Verifier**: 43-128 character cryptographically random string
- **Challenge Calculation**: SHA256 hash with base64url encoding

### General Security
- **Never** commit sensitive data (tokens, secrets, client credentials)
- Use secure credential storage (keyring for traditional, file permissions for OAuth 2.1)
- Validate all user inputs (agent names, prompts)
- Sanitize data before logging (never log tokens or secrets)
- Keep dependencies updated for security patches
- Regular security audits of authentication flows

### RFC Compliance
- **RFC 7591**: Dynamic Client Registration Protocol implementation
- **RFC 7636**: PKCE implementation with S256 challenge method
- **RFC 6749**: OAuth 2.0 Authorization Framework (traditional flow)
- **RFC 6750**: Bearer Token Usage for OAuth 2.1 flow

## 11. Debugging Tips

### Enable Debug Logging
```bash
export HITL_LOG_LEVEL=DEBUG
hitl-cli --debug <command>
```

### OAuth 2.1 Debug Points
- **Dynamic Registration**: Check `OAuthDynamicClient._register_client()` logs
- **PKCE Generation**: Verify code verifier and challenge in `_generate_code_*()` methods
- **Authorization Flow**: Monitor browser redirect and callback handling
- **Token Exchange**: Debug `_exchange_authorization_code()` with X-MCP-Agent-Name header
- **Token Storage**: Verify file permissions and JSON structure in `~/.hitl/oauth_*.json`
- **Automatic Refresh**: Check `refresh_oauth_token()` functionality

### Traditional Flow Debug Points
- Authentication flow in `auth.py`
- API requests/responses in `api_client.py`
- Token storage/retrieval from keyring
- JWT token validation and expiration

### MCP Debug Points
- WebSocket connections and message exchange
- Bearer token vs JWT authentication method selection
- Agent context in request headers
- Request/response correlation

### Common Debug Commands
```bash
# Test OAuth 2.1 flow
hitl-cli login --dynamic --name "Debug Agent" --debug

# Test traditional flow
hitl-cli login --debug

# Check authentication status
hitl-cli status --debug

# Test MCP request with debug
hitl-cli request --prompt "Debug test" --debug

# Clear all tokens for fresh start
hitl-cli logout
rm -f ~/.hitl/oauth_*.json
```

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

## 13. OAuth 2.1 Implementation Details

### PKCE Implementation
```python
# Code verifier generation (43-128 chars)
code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

# Code challenge calculation
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode('utf-8')).digest()
).decode('utf-8').rstrip('=')
```

### Dynamic Client Registration
```python
# RFC 7591 compliant registration
registration_data = {
    "client_name": agent_name,
    "redirect_uris": [redirect_uri],
    "token_endpoint_auth_method": "client_secret_post",
    "grant_types": ["authorization_code", "refresh_token"],
    "response_types": ["code"],
    "scope": "openid email profile"
}
```

### Bearer Token Authentication
```python
# MCP requests with Bearer tokens
headers = {
    "Authorization": f"Bearer {access_token}",
    "X-MCP-Agent-Name": agent_name,
    "Content-Type": "application/json"
}
```

## 14. Future Enhancements

Planned features:
- [ ] Offline mode with request queuing
- [ ] Multiple backend support
- [ ] Plugin system for custom commands
- [ ] Interactive mode
- [ ] Request templates
- [ ] Bulk operations
- [ ] OAuth 2.1 device flow for headless environments
- [ ] Client credential rotation
- [ ] Token introspection endpoint support

## 14. Maintainer Notes

- Keep README.md user-focused
- Update CLAUDE.md for developer guidelines
- Monitor issue tracker for common problems
- Regular dependency updates (monthly)
- Backward compatibility for at least 2 versions