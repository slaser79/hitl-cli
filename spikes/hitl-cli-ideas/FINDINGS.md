# Research Findings: hitl-cli Ideas Generation

**Date:** 2026-03-03
**Researcher:** Claude (The Researcher)
**Task:** Analyze codebase, commits, and issues to identify improvements

## Methodology

1. Full source code review of all 10 modules (~2,600 LOC)
2. Test suite analysis (94 tests across 16 files)
3. Git history analysis (26 commits, 12 PRs)
4. Closed issue review (Issues #19-#27 — deferred refactoring ideas)
5. Dependency and CI pipeline review
6. Architecture pattern analysis

## Raw Observations

### Code Duplication (Quantified)

**Auth routing pattern** — repeated 3x in `main.py` (lines 240-273, 306-331, 365-390):
```
if e2ee: ... elif is_using_api_key(): ... elif is_using_oauth(): ... else: ...
```
Same 4-branch pattern in `sdk.py` (lines 75-100, 126-142, 170-185).
**Total:** 6 repetitions of the same auth dispatch logic.

**MCP result extraction** — duplicated in `mcp_client.py` (lines ~100-127 and ~166-184).
Identical content extraction from MCP tool call results.

### Configuration Gaps

`config.py` is 13 lines — just 4 path constants and 1 env var. No validation, no defaults system, no user-facing config command.

Configuration is spread across:
- `config.py` (paths, base URL)
- `auth.py` (token file locations, OAuth endpoints)
- `main.py` (logging config)
- `mcp_client.py` (timeouts)
- `api_client.py` (timeouts)

### Async Anti-Pattern

Every CLI command uses `asyncio.run()` wrapper:
```python
@app.command()
def request(...):
    async def _async_request():
        ...
    asyncio.run(_async_request())
```
Typer 0.16+ supports native async commands. This pattern is unnecessary and prevents proper async cleanup.

### Security Observations

1. **E2EE incomplete in proxy**: `proxy_handler_v2.py` has `encrypt_arguments()` function but it's NOT called in `create_fastmcp_proxy_server()`. The E2EE proxy claims are partially undelivered.
2. **Token refresh race**: `mcp_client.py` has no lock around token refresh — concurrent calls can double-refresh.
3. **Silent crypto failures**: `register_public_key_with_backend()` catches all exceptions silently — user doesn't know if E2EE registration succeeded.

### Test Gaps

Well-tested: Auth flows, hooks, CLI commands, crypto operations
Not tested:
- Real async behavior (everything is mocked)
- `proxy_handler_v2.py` E2EE encryption path
- Concurrent request handling
- Network failure/retry behavior
- `sdk.py` auth routing (duplicated from main.py)
- Admin commands end-to-end

### Dormant Features

- `sdk.py` — not documented in README, no integration examples
- File attachment handling (Issue #4) — PR closed, never landed
- Batch notifications — mentioned in roadmap Phase 2, no progress
- Response streaming — mentioned in roadmap Phase 2, no progress

### CI/CD Gaps

- No minimum coverage threshold enforced
- No changelog validation on release
- No version consistency check between pyproject.toml and flake.nix
- ruff not listed in dev dependencies (only in CI workflow)

### Stale Branches

10+ remote branches that are either merged or abandoned:
- `feat/cli-file-attachments-4` (abandoned)
- `public-release-prep` (merged)
- Multiple `feature/issue-28-*` variants
