# System Context & Architecture

## Tech Stack
- **Language:** Python 3.12
- **CLI Framework:** Click
- **Authentication:** OAuth 2.1 with PKCE, Dynamic Client Registration
- **Security:** E2EE support for confidential interactions
- **Infrastructure:** Nix dev environment, uv package manager

## Development Constraints
- **Build Command:** `nix develop` then `uv sync`
- **Test Command:** `nix develop -c pytest`
- **Lint Command:** `nix develop -c ruff check`

## Repository Structure
- `hitl_cli/` - Main package source
- `docs/` - Documentation
- `tests/` - Test suite
- `.specs/` - Source of Truth (Docs-as-Code)

## Architecture
The CLI operates in multiple modes:
1. **Direct CLI:** User invokes commands directly (`hitl-cli ask "question"`)
2. **MCP Proxy:** Runs as stdio server for Claude/Gemini integration
3. **SDK:** Importable Python package for programmatic use
