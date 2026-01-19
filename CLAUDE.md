# Project Guidelines: `hitl-cli`

This document outlines the essential guidelines, conventions, and operational procedures for the `hitl-cli` project. Following these standards ensures consistent development practices, efficient collaboration, and a stable codebase.

## 1. Project Overview

`hitl-cli` is a standalone, open-source Python command-line interface that serves as a reference implementation for Human-in-the-Loop (HITL) services.

**Key Features:**
*   **Open Source**: MIT licensed for community use and contribution.
*   **Standalone**: No proprietary dependencies on private backend services.
*   **Extensible**: A clean architecture allows for easy addition of new commands.
*   **Modern Authentication**: Supports OAuth 2.1 with Proof Key for Code Exchange (PKCE) and dynamic client registration.
*   **Dual-Mode Auth**: Compatible with both modern OAuth 2.1 and a traditional Firebase/JWT flow.
*   **Zero-Config**: Dynamic client registration eliminates the need for manual OAuth client setup.

---

## 2. Getting Started: Development Environment

This project supports two development setups: a reproducible environment using **Nix** (recommended) or a **Manual** setup using standard Python tools.

### Option 1: Nix Environment (Recommended)

The `flake.nix` file provides a fully reproducible development environment.

**Setup:**
Simply enter the development shell:

```bash
# This command automatically:
# 1. Enters a shell with Python 3.12 and all required dependencies.
# 2. Creates and activates a virtual environment.
# 3. Installs the 'uv' package manager.
# 4. Installs project dependencies.
nix develop
```
You are now ready to start developing.

### Option 2: Manual Environment (Without Nix)

If you are not using Nix, you can set up the environment with `uv` (or `pip`) and Python 3.12+.

**Setup Steps:**

1.  **Create and activate a virtual environment:**
    ```bash
    uv venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    # Install all project dependencies from pyproject.toml
    uv sync
    ```
    *Alternatively, for an editable install:*
    ```bash
    pip install -e .
    ```

---

## 3. Development Practices

### Code Style
*   Follow **PEP 8** conventions for all Python code.
*   Use **type hints** for all function signatures.
*   Write small, single-purpose functions.
*   Document complex logic with clear, concise inline comments.

### Mandatory Test-Driven Development (TDD) Protocol

**Zero tolerance for regressions.** All code changes, from bug fixes to new features, **must** follow this TDD protocol.

**Step 1: Record Baseline**
Before making changes, establish a baseline of the current test results.
```bash
# In a Nix environment:
nix develop -c pytest tests/ --tb=no -q > baseline_tests.txt

# In a manual environment:
uv run pytest tests/ --tb=no -q > baseline_tests.txt

# Announce the baseline
echo "Baseline recorded: $(grep -E 'failed|passed|error' baseline_tests.txt)"
```

**Step 2: Write a Failing Test**
Create a new test that captures the requirements of your change. **This test must fail initially.**
```bash
# Example for a new feature
pytest tests/test_new_feature.py::test_my_new_functionality -v
```

**Step 3: Implement the Code**
Write the minimum amount of code required to make the new test pass, while ensuring all existing tests continue to pass.

**Step 4: Verify No Regressions**
Run the entire test suite again and compare the output to your baseline. The number of failed tests must not increase.
```bash
# Run final tests
nix develop -c pytest tests/ --tb=no -q > final_tests.txt

# Verify that no new tests are failing
diff baseline_tests.txt final_tests.txt
```
**Success Criteria:** Your new tests pass, and no existing tests have started to fail.

### Running Tests

The following commands can be run inside a `nix develop` shell or using `uv run` in a manual setup.

*   **Run all tests:**
    ```bash
    pytest
    ```

*   **Run tests with a coverage report:**
    ```bash
    pytest --cov=hitl_cli --cov-report=term-missing
    ```

*   **Run a specific test file or function:**
    ```bash
    # Test a specific file
    pytest tests/test_auth_flow.py -v

    # Test a specific function
    pytest tests/test_oauth_dynamic_registration.py::test_pkce_code_generation -v
    ```

---

## 4. Project Internals

### Project Structure
```
hitl-cli/
├── hitl_cli/                # Source code for the CLI tool
│   ├── main.py              # CLI entry point (Typer app)
│   ├── auth.py              # Authentication logic
│   ├── api_client.py        # Backend API interaction
│   ├── mcp_client.py        # Model Context Protocol client
│   ├── commands.py          # CLI command implementations
│   └── config.py            # Configuration management
├── tests/                   # Automated tests
├── .github/                 # CI/CD workflows
├── pyproject.toml           # Project metadata and dependencies
├── flake.nix                # Nix development environment definition
└── README.md                # User-facing documentation
```

### Authentication Flows

The CLI supports two distinct authentication methods.
 Dynamic Registration (Recommended)
This modern, secure flow requires no manual setup.

1.  **Dynamic Client Registration**: The CLI registers itself as an OAuth client with the server automatically.
2.  **PKCE Authorization**: A Proof Key for Code Exchange (PKCE) flow prevents authorization code interception attacks.
3.  **Token Management**: The CLI securely stores bearer and refresh tokens in `~/.hitl/oauth_token.json` with restricted file permissions (600). Tokens are refreshed automatically.

#### Flow 2: Traditional Firebase Auth (Legacy)
This flow relies on exchanging a Firebase ID token for a backend-specific JWT.

1.  **Firebase Authentication**: The user authenticates with a provider (e.g., Google) via their browser to obtain a Firebase ID token.
2.  **Backend JWT Exchange**: The Firebase token is exchanged for a custom JWT from the `hitl-cli` backend.
3rage**: Tokens are stored in the system's native keyring.

### Configuration
Configuration is loaded with the following precedence:
1.  Command-line arguments (e.g., `--name "Agent"`)
2.  Environment variables
3.  Configuration files (`~/.hitl/`)
4.  Default values

**Environment Variables:**
*   `HITL_SERVER_URL`: **(Required)** The base URL for the backend API.
*   `GOOGLE_CLIENT_ID`: (Required for traditional flow only) The Google OAuth client ID.
*   `HITL_LOG_LEVEL`: (Optional) Set logging level (e.g., `DEBUG`, `INFO`). Defaults to `INFO`.

**Configuration Files:**
*   `~/.hitl/oauth_client.json`: Stores data from dynamic client registration.
*   `~/.hitl/oauth_token.json`: Stores OAuth 2.1 bearer and refresh tokens.
*   `~/.hitl/config.json`: Stores general CLI configuration.

### Security
*   **PKCE**: Implemented for OAuth 2.1 to mitigate authorization code interception.
*   **No Hardcoded Secrets**: Dynamic client registration avoids committing secrets to source code.
*   **Secure Token Storage**: Uses the system keyring (legacy) or restricted file permissions (OAuth 2.1).
*   **Never commit sensitive data** (tokens, secrets, credentials) to version control.

---

## 5. Troubleshooting and Debugging

### Enable Debug Logging
For more detailed output, set the log level to `DEBUG`:
```bash
export HITL_LOG_LEVEL=DEBUG
hitl-cli --debug <command>
```

### Common Issues & Solutions

*   **Problem: OAuth dynamic registration fails.**
    *   **Solution**: Verify the `HITL_SERVER_URL` is correct and reachable. Ensure the backend implements RFC 7591. Try clearing `~/.hitl/oauth_client.json` and re-authenticating.

*   **Problem: PKCE validation errors.**
    *   **Solution**: Check that your system time is synchronized .  **Secure Sto
#### Flow 1: OAuth 2.1 withwith a reliable time server. This can affect the validity of state parameters.

*   **Problem: "Token has expired" errors.**s automatically. If it fails, re-authenticate using `hitl-cli login`. For the OAuth 2.1 flow, ensure `~/.hitl/oauth_token.json` has `600` permissions.

*   **Problem: Network timeouts or connection failures.**
    *   **Solution**: Verify the `HITL_SERVER_URL` and your network connection. Use `curl -v $HITL_SERVER_URL/health` to test connectivity to the backend.

### Clearing Local Credentials
To perform a fresh login, you can log out and remove stored credentials:
```bash
# This command clears credentials from the sys
    *   **Solution**: The CLI should handle token refreshe

## The Constitution (Non-Negotiable)

This repository is a **Satellite** in the HITL Empire, managed from HQ (`slaser79/agent_workflows`).

### 1. The Spec-First Doctrine
**No code is written without a Spec.**
- You must read the spec linked in your Issue before writing code.
- *Code is liability. Specs are assets.*

### 2. Relentless Improvement (Kaizen)
**We do not repeat mistakes.**
- After every failure, document lessons learned.
- *The system gets smarter with every crash.*

### 3. Chain of Command
1. **The CEO (Human):** Sets high-level intent via HITL.
2. **The Chief of Staff (CoS):** The Architect. Creates Specs and GitHub Issues.
3. **The Workers:** (Gemini/Codex/Qwen). They write code in isolated worktrees.

For full Empire governance, see: [agent_workflows CLAUDE.md](https://github.com/slaser79/agent_workflows/blob/main/CLAUDE.md)