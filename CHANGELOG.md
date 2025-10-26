# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-10-25

### Added
- Initial PyPI publication at https://pypi.org/project/hitl-cli/
- OAuth 2.1 authentication with PKCE and dynamic client registration
- End-to-end encryption (E2EE) proxy for Model Context Protocol (MCP)
- Claude Code hooks support via `hitl-hook-review-and-continue`
- Python SDK (`HITL` class) for programmatic access
- CLI commands:
  - `hitl-cli login` - OAuth 2.1 authentication
  - `hitl-cli logout` - Clear credentials
  - `hitl-cli request` - Request human input
  - `hitl-cli notify` - Send fire-and-forget notification
  - `hitl-cli notify-completion` - Notify task completion and wait for response
  - `hitl-cli proxy` - Start E2EE MCP proxy server
- Comprehensive test suite with 94 tests
- MIT License
- Documentation in README.md

### Changed
- Standardized configuration directory from "hitl-shin-relay" to "hitl-cli"
- Replaced manual JSON-RPC proxy implementation with FastMCP 2.0 framework
- Updated README with correct Claude Code hooks configuration

### Fixed
- Async refactoring bugs in login function (PR #13)
- Missing `__init__.py` in hooks package for proper package distribution
- Claude Code hooks JSON structure and file path documentation

### Security
- Implemented PKCE (Proof Key for Code Exchange) for OAuth 2.1
- Token storage with secure file permissions (600)
- End-to-end encryption for human-in-the-loop communications

[1.2.0]: https://github.com/slaser79/hitl-cli/releases/tag/v1.2.0
