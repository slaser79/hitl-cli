# Research Findings: hitl-cli Ideas Round 3

**Date:** 2026-03-07
**Researcher:** Claude (The Researcher)
**Scope:** Identifying fresh opportunities for UX, reliability, and security improvements.

## Methodology

1. Analysis of recent additions (e.g., `daily-report` command).
2. Review of existing 60 ideas to ensure zero duplication.
3. Deep dive into `auth.py`, `api_client.py`, and `mcp_client.py` for edge cases.
4. Investigation of hook implementations (`review_and_continue.py`) for usability gaps.
5. Evaluation of terminal UX and developer friction points.

## New Observations

### Terminal UX Gaps
- **Plain Output**: The CLI currently uses basic string formatting for everything. Tables are drawn with dashes, and there are no colors or progress indicators.
- **Verbose Commands**: Frequently used commands like `notify-completion` are long to type.
- **Single-use Login**: OAuth login assumes port 8080 is always free, which is a common point of failure for developers.

### Developer Friction (DX)
- **Environment Switching**: No easy way to override the backend server for a single command without changing global config.
- **Opaque Errors**: API errors are returned as raw status codes or short strings without guidance on how to resolve them.
- **Searchability**: Listing agents or history entries becomes unmanageable as the volume grows.

### Security and Privacy
- **Credential Storage**: Credentials are on disk (protected by permissions) but not in a system keyring.
- **Telemetry Transparency**: As the system grows, users will need clear ways to opt-out of any data collection.
- **Attachment Support**: There is no way to send visual context (images) or logs as files for human review.

### Architecture and Integration
- **REPL Mode**: High-frequency testing is slowed down by CLI startup time.
- **Webhook Integration**: Asynchronous HITL responses are currently limited by the CLI's blocking nature.
- **Cross-Platform Consistency**: The config path is Linux-centric and doesn't follow macOS/Windows conventions.

## Summary of Proposed Ideas (IDEA-061 to IDEA-075)

| ID | Title | Category | Priority |
|----|-------|----------|----------|
| 061 | Command Aliases | UX | Low |
| 062 | Rich Terminal UI | UX | Medium |
| 063 | Agent Search/Filtering | DX | Low |
| 064 | Export/Import Config | DX | Low |
| 065 | --server Flag | DX | Medium |
| 066 | Dynamic OAuth Port | Reliability | Medium |
| 067 | Doc Links in Errors | DX | Low |
| 068 | Update Checker | UX | Low |
| 069 | Keyring Integration | Security | High |
| 070 | Extended User-Agent | Observability | Low |
| 071 | File Attachments | Feature | Medium |
| 072 | Global Debug System | Architecture | Medium |
| 073 | Interactive REPL | UX | Low |
| 074 | Telemetry Opt-out | Compliance | Medium |
| 075 | Local Webhooks | Architecture | Low |
