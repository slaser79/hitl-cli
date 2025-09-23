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
uv venv
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
│   ├── auth.py              # Firebase/OAuth authentication
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
uv run pytest tests/test_oauth_dynamic_registration.py -v  # or nix develop -c pytest tests/test_oauth_dynamic_registration.py -v

# Test PKCE implementation
uv run pytest tests/test_oauth_dynamic_registration.py::test_pkce_code_generation -v

# Test dynamic client registration
uv run pytest tests/test_oauth_dynamic_registration.py::test_dynamic_client_registration -v
```

#### General Tests
```bash
# Run all tests
uv run pytest   # or nix develop -c pytest

# Run with coverage
uv run pytest --cov=hitl_cli --cov-report=term-missing

# Run specific test
uv run pytest tests/test_auth_flow.py -v

# Test both authentication flows
uv run pytest tests/test_auth_flow.py tests/test_oauth_dynamic_registration.py -v
```

#### Manual Testing OAuth 2.1
```bash
# Test complete OAuth 2.1 flow
uv run python test_oauth_implementation.py

# Test integration with backend
uv run python oauth_integration_demo.py
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

### Traditional Firebase Auth Flow (Legacy)

1. **Firebase Authentication**:
   - User runs `hitl-cli login`
   - Supports multiple providers: Google, Apple, Email
   - Browser opens for authentication
   - Firebase ID token obtained
   - Tokens stored securely in platform keyring

2. **Backend JWT Exchange**:
   - Exchange Firebase ID token for backend JWT
   - JWT contains user and agent context
   - Include JWT in all API requests
   - Handle token expiration gracefully

3. **Agent Management**:
   - Manual agent creation via API
   - Agent ID required for requests
   - Separate agent management commands

## 7. Configuration

### Environment Variables
- `HITL_SERVER_URL`: Backend API base URL (required for both flows)
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
- Test with curl: `curl -v $HITL_SERVER_URL/health`

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
uv run hitl-cli login --dynamic --name "Debug Agent" --debug

# Test traditional flow
uv run hitl-cli login --debug

# Check authentication status
uv run hitl-cli status --debug

# Test MCP request with debug
uv run hitl-cli request --prompt "Debug test" --debug

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

## 15. Human-in-the-Loop MCP Tool Usage

### When Working on This Project
When the human-in-the-loop MCP tool is available during development, **ALWAYS** use the MCP tool for human confirmations instead of asking directly in conversation:

**✅ CORRECT - Use MCP tool for confirmations:**
```python
# Use mcp__human-in-the-loop__request_human_input for confirmations
result = mcp__human-in-the-loop__request_human_input({
    "prompt": "Should I proceed with updating the authentication flow to OAuth 2.1?",
    "choices": ["Yes, proceed", "No, keep current", "Ask for more details"]
})
```

**❌ INCORRECT - Don't ask directly in conversation:**
```
"Should I proceed with updating the authentication flow? Please confirm."
```

### Confirmation Scenarios
Use the MCP tool for:
- Code changes that might affect authentication flows
- Breaking changes to the CLI interface
- Major refactoring decisions
- Security-related modifications
- Production deployment confirmations
- Test execution approvals that might affect external systems

### Integration with CLI Development
- The CLI itself implements MCP client functionality
- Test MCP interactions during CLI development
- Use the same authentication patterns for development confirmations
- Validate MCP tool responses in CLI testing workflows

## 16. Mandatory TDD Protocol

### **🚨 CRITICAL: All CLI Development MUST Follow TDD**

**Zero tolerance for regressions**. Every code change must follow this protocol:

#### **Step 1: Baseline Assessment (MANDATORY)**
```bash
cd hitl-cli/
nix develop -c pytest tests/ --tb=no -q > baseline_tests.txt
echo "Baseline recorded: $(grep -E 'failed|passed|error' baseline_tests.txt)"
```
**Record exact numbers**: "X passed, Y failed, Z errors"

#### **Step 2: Test-First Development (MANDATORY)**
```bash
# Write failing test first
nix develop -c python -m pytest tests/test_new_feature.py::test_my_new_functionality -v
# Should FAIL initially (proves test works)
```

**Test Requirements**:
- **Independent unit tests** - no external dependencies
- **Outcome-focused** - test what should happen, not how
- **Descriptive names** - test should read like documentation
- **Arrange-Act-Assert pattern**

#### **Step 3: Implementation (MANDATORY)**
- Write **minimal code** to make tests pass
- **No feature creep** beyond test requirements
- Keep all existing tests passing

#### **Step 4: Regression Prevention (MANDATORY)**
```bash
nix develop -c pytest tests/ --tb=no -q > final_tests.txt
# Compare results - MUST have same failure count as baseline
diff baseline_tests.txt final_tests.txt
```

**Success Criteria**:
- ✅ Baseline failure count unchanged
- ✅ New tests pass  
- ✅ No new failures introduced

### **CLI-Specific Testing Guidelines**

#### **OAuth 2.1 Testing**
```python
def test_oauth_dynamic_registration_should_create_client():
    # Test the outcome: client created successfully
    result = oauth_client.register("Test Agent")
    assert result.status == "success"
    assert result.client_id is not None
```

#### **E2EE Proxy Testing**
```python  
def test_proxy_should_encrypt_human_input_requests():
    # Test the outcome: requests are encrypted
    proxy = ProxyHandler()
    encrypted_request = proxy.handle_request_human_input(plaintext_request)
    assert encrypted_request.contains_encrypted_payload()
    assert not encrypted_request.contains_plaintext()
```

#### **MCP Client Testing**
```python
def test_mcp_client_should_handle_authentication_errors():
    # Test the behavior: proper error handling
    client = MCPClient()
    with pytest.raises(AuthenticationError):
        client.call_tool_with_invalid_token("request_human_input", {})
```

### **Common CLI Test Patterns**

#### **Mock External Services**
```python
@patch('hitl_cli.api_client.httpx.post')
def test_api_call_should_retry_on_network_error(mock_post):
    # Arrange
    mock_post.side_effect = [ConnectionError(), MockResponse(200, {"status": "ok"})]
    
    # Act  
    result = api_client.make_request("/test")
    
    # Assert
    assert result.status_code == 200
    assert mock_post.call_count == 2  # Verify retry happened
```

#### **Test CLI Commands**
```python
def test_login_command_should_show_success_message():
    runner = CliRunner()
    result = runner.invoke(login, ['--dynamic', '--name', 'Test'])
    assert result.exit_code == 0
    assert "✅ Login successful" in result.output
```

## 17. Maintainer Notes

- Keep README.md user-focused
- Update CLAUDE.md for developer guidelines
- Monitor issue tracker for common problems
- Regular dependency updates (monthly)
- Backward compatibility for at least 2 versions
- **Always use human-in-the-loop MCP tool for confirmations** when available during development
- **MANDATORY: Follow TDD protocol for ALL code changes**
