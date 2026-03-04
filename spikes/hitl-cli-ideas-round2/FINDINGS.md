# Research Findings: hitl-cli Ideas Round 2

**Date:** 2026-03-04
**Researcher:** Claude (The Researcher)
**Scope:** Deep code analysis for NEW improvement opportunities beyond IDEA-001–015

## Methodology

1. Read every source file in `hitl_cli/` (9 modules, ~2,900 LOC)
2. Read all test files (124 passing tests across 11 files)
3. Analyzed CI/CD workflows, pyproject.toml, and project metadata
4. Cross-referenced closed issues (#1–#34) for recurring themes
5. Filtered out ideas already captured in IDEA-001–015

## Key Observations

### Security Gaps
- **E2EE key registration silently fails** (`crypto.py:148-221`): If backend registration fails, the agent continues with unregistered keys. Backend will reject encrypted messages later — user has no warning.
- **File permissions never verified** (`auth.py:61,449,472`, `crypto.py:72`): Files are chmod'd to 0o600 but there's no assertion that permissions were actually set.
- **Multi-device E2EE picks first device only** (`proxy_handler_v2.py:200-202`): Comment acknowledges this is incomplete.

### Architecture Issues
- **No exception hierarchy**: Only `NotLoggedInError` exists. Everything else is bare `Exception`. Makes SDK error handling imprecise.
- **Proxy tool registration may race** (`proxy_handler_v2.py:369-423`): `register_backend_tools()` is async but may not complete before first tool list request.
- **Hardcoded timeouts in 6+ locations**: Same value (900s) repeated across api_client.py, mcp_client.py — not the same as IDEA-009 which is about user-facing configurability. This is about code-level DRY.

### UX/DX Gaps
- **No deprecation migration path**: Traditional JWT auth is blocked (`mcp_client.py:31-32` throws Exception) but no `auth-migrate` command exists to guide users.
- **CLI help text is sparse**: `--placeholder-text`, `--choice`, `--e2ee` options lack descriptions and examples.
- **Hook management is invisible**: Hooks are installed as entry points but there's no `hitl-cli hooks list/check` to discover or validate them.

### Reliability Concerns
- **No request deduplication**: Duplicate CLI invocations send duplicate requests to backend. Could cause duplicate HITL prompts on mobile.
- **Token expiry is silent**: No warning when token is about to expire during long operations.
- **Hook errors are opaque**: Hooks catch CalledProcessError without logging stderr.

### Feature Opportunities
- **Streaming responses**: Long reviews could benefit from chunked output.
- **Telemetry hooks**: No way to measure latency, track auth method usage, or monitor error rates in production.

## Evidence Summary

| Finding | Files | Lines | Severity |
|---------|-------|-------|----------|
| Silent E2EE key registration failure | crypto.py | 148-221 | HIGH |
| File permissions unverified | auth.py, crypto.py | 61,449,472,72 | HIGH |
| No exception hierarchy | all modules | throughout | HIGH |
| Proxy tool registration race | proxy_handler_v2.py | 369-423 | HIGH |
| Multi-device E2EE incomplete | proxy_handler_v2.py | 200-202 | HIGH |
| No deprecation migration | mcp_client.py | 31-32 | MEDIUM |
| Sparse CLI help text | main.py | 220-290 | MEDIUM |
| Hook management invisible | main.py, hooks/ | — | MEDIUM |
| No request deduplication | api_client.py, mcp_client.py | — | MEDIUM |
| Silent token expiry | auth.py, mcp_client.py | 427-429 | MEDIUM |
| Opaque hook errors | hooks/*.py | 156-166, 92-97 | MEDIUM |
| No streaming support | api_client.py, mcp_client.py | — | LOW |
| No telemetry hooks | main.py, api_client.py | — | LOW |
| Config schema validation | config.py | all 13 lines | MEDIUM |
| Hardcoded timeouts (DRY) | api_client.py, mcp_client.py | 19,142,149,156,192,226 | MEDIUM |
