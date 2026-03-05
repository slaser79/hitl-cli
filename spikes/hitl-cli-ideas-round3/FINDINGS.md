# Spike Findings: hitl-cli Ideas Round 3

**Date:** 2026-03-05
**Researcher:** Claude (Opus 4.6)
**Method:** Deep source code analysis, dependency audit, ecosystem gap analysis

## Research Focus

This round focuses on areas NOT covered by IDEA-001 through IDEA-030:
- **Dependency hygiene** (dead dependencies, missing dev tools)
- **SDK/API surface design** (context managers, typing, ergonomics)
- **Hook ecosystem expansion** (new agent integrations)
- **Testing infrastructure** (fixtures, factory patterns)
- **Security hardening** (supply chain, credential hygiene)
- **Packaging & distribution** (PyPI metadata, entry points)
- **Developer experience** (debug tooling, local dev server)

## Key Observations

### 1. Dead Dependencies (google-auth, google-auth-oauthlib)

`google-auth>=2.40.3` and `google-auth-oauthlib>=1.2.2` are in `[project.dependencies]`
but are ONLY used in the deprecated JWT/Firebase flow. The traditional flow in
`mcp_client.py:31-32` raises `Exception("Traditional OAuth flow is no longer supported...")`.

These dependencies add ~15MB to the install and pull in transitive deps (protobuf,
cachetools, pyasn1, rsa, requests). They serve no purpose for new users.

**Evidence:**
```
$ grep -rn "google" hitl_cli/ --include="*.py"
hitl_cli/auth.py:5:from google.auth.transport.requests import Request as GoogleAuthRequest
hitl_cli/auth.py:6:from google.oauth2 import id_token
```
Both imports are only used in `perform_traditional_login()` which is no longer called
from any CLI command.

### 2. E2EE Boilerplate Duplication in api_client.py

Three methods (`request_human_input_e2ee`, `notify_human_e2ee`, `notify_task_completion_e2ee`)
share identical patterns:
1. `ensure_agent_keypair()`
2. `get("/api/v1/keys/user")`
3. Extract first key
4. Construct payload
5. `encrypt_payload()`
6. `post()` to E2EE endpoint
7. `decrypt_payload()` (for request/completion)

This is ~100 lines of near-identical code. A generic `_e2ee_request()` helper would
reduce this to ~30 lines.

### 3. MCP Result Extraction Duplication

`mcp_client.py:call_tool()` has the MCP result content extraction logic duplicated
**verbatim** twice (lines 109-127 and 166-184). This 19-line block handles
`result.content[0].text`, `result.content.text`, `result.text`, `str(result)`.

### 4. No Context Manager for SDK

The `HITL` class has no `__aenter__`/`__aexit__`. Users can't do:
```python
async with HITL() as hitl:
    await hitl.request_input(...)
```
This prevents proper resource cleanup (httpx clients, MCP connections).

### 5. Missing `py.typed` Marker

The package exports type-annotated classes but has no `py.typed` marker file.
PEP 561 requires this for type checkers (mypy, pyright) to recognize the package
as typed. Without it, downstream users get "module is not typed" warnings.

### 6. No `--version` Flag

`hitl-cli --version` doesn't work. Typer supports this trivially with
`app = typer.Typer(... callback=version_callback)` or `typer.Option("--version")`.

### 7. Sync Wrapper Anti-Pattern in api_client.py

`post_sync()` (lines 108-127) creates an ad-hoc `MockResponse` class inside the method
body for testing purposes. This is a testing concern bleeding into production code.

### 8. No `ruff` in Dev Dependencies

CI runs `ruff check .` but `ruff` is not in `[tool.uv.dev-dependencies]`. Developers
must install ruff globally or it silently passes (skips linting).

### 9. Hardcoded Emoji in Output

All CLI output uses hardcoded emoji (`typer.echo("✅ ...")`, `typer.echo("❌ ...")`).
No `--no-emoji` or `--plain` flag exists. This breaks in terminals that don't support
Unicode (some CI runners, Windows cmd.exe, piped output).

### 10. No Gemini/Aider/Windsurf Hook

Hooks exist for Claude Code (stop hook) and Codex (notify), but not for other
popular AI coding agents: Gemini CLI, Aider, Windsurf, Cursor. Each has different
hook/plugin mechanisms.

### 11. ApiClient Tight Coupling to Typer

`ApiClient._handle_response()` calls `typer.echo()` and `raise typer.Exit(1)`.
This makes `ApiClient` unusable as a standalone library — importing it in a non-CLI
context (e.g., a web server, SDK consumer) would need `typer` installed and would
call `sys.exit()` on errors.

### 12. No Request Cancellation

Once a HITL request is sent, there's no way to cancel it. If the agent crashes or
the user wants to abort, the request sits pending on the phone forever.

### 13. No Health Check Command

No `hitl-cli health` or `hitl-cli ping` to verify server connectivity without
sending actual requests. Different from IDEA-006 (`status`) which shows auth state.

### 14. BearerAuth Class Defined Inside Method

`mcp_client.py:150-157` defines `BearerAuth(httpx.Auth)` inside `call_tool()`.
This class is recreated on every call and can't be reused or tested independently.

### 15. No Shell Completion Setup

Typer supports shell completion out of the box, but `hitl-cli` doesn't expose
`hitl-cli --install-completion` or document it. This is a free DX win.
