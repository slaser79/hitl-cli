# Ideas — hitl-cli

## Status Legend
| Status | Meaning |
|--------|---------|
| PENDING | Awaiting CEO review |
| APPROVED | CEO approved for roadmap |
| REJECTED | CEO rejected |
| PROMOTED | Moved to ROADMAP.md |

## Ideas Index
| Date | Source | Title | Status |
|------|--------|-------|--------|
| 2026-03-03 | researcher | IDEA-001: Auth Strategy Pattern (eliminate 6x dispatch duplication) | PENDING |
| 2026-03-03 | researcher | IDEA-002: Native async commands (drop asyncio.run wrappers) | PENDING |
| 2026-03-03 | researcher | IDEA-003: Centralized Config class with validation | PENDING |
| 2026-03-03 | researcher | IDEA-004: Complete E2EE in proxy handler | PENDING |
| 2026-03-03 | researcher | IDEA-005: Token refresh concurrency guard | PENDING |
| 2026-03-03 | researcher | IDEA-006: `hitl-cli status` command | PENDING |
| 2026-03-03 | researcher | IDEA-007: SDK documentation and examples in README | PENDING |
| 2026-03-03 | researcher | IDEA-008: Connection pooling for ApiClient | PENDING |
| 2026-03-03 | researcher | IDEA-009: Configurable timeouts per-command | PENDING |
| 2026-03-03 | researcher | IDEA-010: CI coverage threshold enforcement | PENDING |
| 2026-03-03 | researcher | IDEA-011: Batch notification support | PENDING |
| 2026-03-03 | researcher | IDEA-012: Request history / audit log | PENDING |
| 2026-03-03 | researcher | IDEA-013: Stale branch cleanup | PENDING |
| 2026-03-03 | researcher | IDEA-014: Retry with exponential backoff | PENDING |
| 2026-03-03 | researcher | IDEA-015: Real async integration tests | PENDING |

---

## IDEA-001: Auth Strategy Pattern

**Category:** Architecture / Tech Debt
**Priority Suggestion:** High
**Effort:** Medium (1-2 days)
**Origin:** Closed issue #25 + codebase analysis

### Problem
The 4-branch auth dispatch pattern (`if e2ee → elif api_key → elif oauth → else jwt`) is duplicated **6 times** across `main.py` (3x) and `sdk.py` (3x). Every new auth method or new command multiplies this.

### Proposal
Extract an `AuthStrategy` that resolves the correct transport once:

```python
class AuthDispatcher:
    @staticmethod
    def get_client() -> ApiClient | MCPClient:
        if is_using_api_key(): return ApiClient()
        if is_using_oauth(): return OAuthMCPClient()
        return LegacyMCPClient()
```

Commands become one-liners: `client = AuthDispatcher.get_client(); await client.request(...)`.

### Impact
- Eliminates ~120 lines of duplicated branching
- New auth methods only need one update point
- Simplifies testing (mock one dispatcher, not 6 branches)

---

## IDEA-002: Native Async Commands

**Category:** Architecture / Tech Debt
**Priority Suggestion:** Medium
**Effort:** Small (half day)
**Origin:** Closed issue #24 + codebase analysis

### Problem
Every command wraps async logic in `asyncio.run()`:
```python
@app.command()
def request(...):
    async def _async_request():
        ...
    asyncio.run(_async_request())
```
Typer 0.16+ (already a dependency) supports native async commands.

### Proposal
```python
@app.command()
async def request(...):
    response = await client.request_human_input(...)
```

### Impact
- Removes boilerplate wrappers from all 5 commands
- Enables proper async resource cleanup
- Prevents nested `asyncio.run()` issues (Issue #19)

---

## IDEA-003: Centralized Config Class

**Category:** Architecture / DX
**Priority Suggestion:** Medium
**Effort:** Medium (1 day)
**Origin:** Closed issue #27 + codebase analysis

### Problem
`config.py` is 13 lines — just path constants. Configuration is scattered:
- Timeouts in `api_client.py` and `mcp_client.py` (hardcoded)
- Logging in `main.py` (hardcoded)
- Auth endpoints in `auth.py` (hardcoded)

No `hitl-cli config` command exists to view/edit settings.

### Proposal
```python
@dataclass
class HITLConfig:
    server_url: str = "https://hitlrelay.app"
    api_timeout: int = 30
    human_timeout: int = 900
    log_level: str = "INFO"
    e2ee_enabled: bool = True
```
Load from: CLI args > env vars > `~/.hitl/config.json` > defaults.

Add `hitl-cli config show` and `hitl-cli config set <key> <value>` commands.

### Impact
- Single source of truth for all settings
- User-visible configuration without editing env vars
- Easier testing (inject config, not mock env)

---

## IDEA-004: Complete E2EE in Proxy Handler

**Category:** Security / Bug
**Priority Suggestion:** High
**Effort:** Medium (1 day)
**Origin:** Codebase analysis

### Problem
`proxy_handler_v2.py` has an `encrypt_arguments()` function (line ~178) that encrypts tool call arguments using the device's public key. However, this function is **never called** in `create_fastmcp_proxy_server()`. The proxy passes arguments through unencrypted.

### Proposal
Wire `encrypt_arguments()` into the proxy's tool call handler, or explicitly document that E2EE in proxy mode only covers the transport layer (HTTPS), not argument encryption.

### Impact
- Closes a gap between documented E2EE claims and actual behavior
- Critical for users who rely on proxy E2EE for sensitive data

---

## IDEA-005: Token Refresh Concurrency Guard

**Category:** Security / Reliability
**Priority Suggestion:** High
**Effort:** Small (2 hours)
**Origin:** Codebase analysis

### Problem
`mcp_client.py` refreshes tokens without any concurrency guard. If two requests fire simultaneously and both detect an expired token, they both attempt refresh — potentially invalidating each other's new token.

### Proposal
Add an `asyncio.Lock` around token refresh:
```python
_refresh_lock = asyncio.Lock()

async def _ensure_valid_token(self):
    async with self._refresh_lock:
        if self._token_expired():
            await self._refresh_token()
```

### Impact
- Prevents double-refresh race condition
- Prevents spurious auth failures under concurrent load

---

## IDEA-006: `hitl-cli status` Command

**Category:** Feature / DX
**Priority Suggestion:** Medium
**Effort:** Small (half day)
**Origin:** Codebase analysis + user experience gap

### Problem
No way to check current auth state, server connectivity, or E2EE status without attempting an operation.

### Proposal
Add `hitl-cli status` that shows:
```
Auth Method:  OAuth 2.1 (Bearer)
Server:       https://hitlrelay.app ✅ (healthy)
Token:        Valid (expires in 47m)
E2EE:         Active (key registered)
Agent:        "My Agent" (id: abc-123)
```

### Impact
- Faster debugging of auth/connectivity issues
- Self-service troubleshooting (reduces support burden)
- Useful for CI/CD health checks

---

## IDEA-007: SDK Documentation in README

**Category:** Documentation
**Priority Suggestion:** Medium
**Effort:** Small (2 hours)
**Origin:** Codebase analysis

### Problem
`sdk.py` provides a clean `HITL` class with `request_input()`, `notify()`, `notify_completion()`, `create_agent()`, and `list_agents()`. But the README only documents CLI usage — the SDK is invisible to users.

### Proposal
Add a "Python SDK" section to README with:
```python
from hitl_cli import HITL

hitl = HITL()
response = await hitl.request_input("Approve deploy?", ["Yes", "No"])
```

### Impact
- Makes the SDK discoverable
- Enables programmatic integration (the core value prop for agents)
- Low effort, high visibility improvement

---

## IDEA-008: Connection Pooling for ApiClient

**Category:** Performance
**Priority Suggestion:** Low
**Effort:** Small (2 hours)
**Origin:** Codebase analysis

### Problem
`ApiClient` creates a new `httpx.AsyncClient` for every request. Under high-throughput usage (batch notifications, agent fleets), this wastes TCP connections.

### Proposal
Use a shared `httpx.AsyncClient` with connection pooling:
```python
class ApiClient:
    _client: httpx.AsyncClient | None = None

    @classmethod
    def _get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            cls._client = httpx.AsyncClient(timeout=30)
        return cls._client
```

### Impact
- Better performance for burst operations
- Required foundation for batch notification support (IDEA-011)

---

## IDEA-009: Configurable Timeouts Per-Command

**Category:** Feature / DX
**Priority Suggestion:** Low
**Effort:** Small (half day)
**Origin:** Issue #7 history + codebase analysis

### Problem
Timeouts are hardcoded: 30s for API calls, 900s for human response. The 900s timeout was already increased once (Issue #7). Different use cases need different timeouts — a quick approval vs. a detailed review.

### Proposal
Add `--timeout` option to `request` and `notify-completion` commands:
```bash
hitl-cli request --prompt "Quick approval?" --timeout 120
hitl-cli request --prompt "Detailed review needed" --timeout 3600
```

### Impact
- Users control wait times per-request
- Prevents timeout-related task failures
- Complements IDEA-003 (default in config, override per-call)

---

## IDEA-010: CI Coverage Threshold Enforcement

**Category:** Quality / CI
**Priority Suggestion:** Medium
**Effort:** Small (1 hour)
**Origin:** CI pipeline analysis

### Problem
CI runs tests and generates coverage reports but does not enforce a minimum threshold. Coverage can silently regress.

### Proposal
Add `--cov-fail-under=80` to pytest in CI:
```yaml
- run: pytest --cov=hitl_cli --cov-fail-under=80
```
Also add ruff to `[project.optional-dependencies]` (currently only in CI workflow, not in pyproject.toml).

### Impact
- Prevents silent coverage regression
- Ensures dev environment matches CI

---

## IDEA-011: Batch Notification Support

**Category:** Feature (Roadmap Phase 2)
**Priority Suggestion:** Medium
**Effort:** Large (2-3 days)
**Origin:** Roadmap Phase 2

### Problem
Currently, each notification is a separate HTTP request. Agent fleets sending many notifications create unnecessary overhead.

### Proposal
Add `hitl-cli notify-batch` that accepts multiple messages:
```bash
hitl-cli notify-batch --file notifications.json
```
Or via SDK:
```python
await hitl.notify_batch(["Deploy started", "Tests passed", "Deploy complete"])
```

### Impact
- Required for agent fleet scaling
- Reduces API call overhead
- Prerequisite: IDEA-008 (connection pooling)

---

## IDEA-012: Request History / Audit Log

**Category:** Feature / Observability
**Priority Suggestion:** Low
**Effort:** Medium (1 day)
**Origin:** Codebase analysis

### Problem
No local record of requests sent or responses received. Debugging requires checking server-side logs.

### Proposal
Append to `~/.hitl/history.jsonl` on every request/response:
```json
{"ts": "2026-03-03T10:00:00Z", "type": "request", "prompt": "...", "response": "Yes", "latency_ms": 4200}
```
Add `hitl-cli history` command to view recent entries.

### Impact
- Local debugging without server access
- Audit trail for compliance-sensitive environments
- Usage analytics for optimization

---

## IDEA-013: Stale Branch Cleanup

**Category:** Housekeeping
**Priority Suggestion:** Low
**Effort:** Tiny (30 min)
**Origin:** Git history analysis

### Problem
10+ stale remote branches exist from merged/abandoned PRs:
- `feat/cli-file-attachments-4` (abandoned)
- `public-release-prep` (merged)
- Multiple `feature/issue-28-*` variants (superseded)

### Proposal
One-time cleanup: delete merged/abandoned remote branches.
Add branch auto-delete on PR merge in GitHub settings.

### Impact
- Cleaner repo, less confusion for contributors
- Prevents accidental work on stale branches

---

## IDEA-014: Retry with Exponential Backoff

**Category:** Reliability
**Priority Suggestion:** Medium
**Effort:** Small (half day)
**Origin:** Codebase analysis

### Problem
No retry logic for transient failures. Network blips, server restarts, or rate limiting cause immediate failures.

### Proposal
Add retry with exponential backoff to `ApiClient`:
```python
@retry(max_attempts=3, backoff_factor=2, retryable_statuses=[429, 502, 503])
async def _request(self, method, url, **kwargs):
    ...
```

### Impact
- Resilience against transient failures
- Required for production agent fleet reliability
- Rate limit awareness (429 handling)

---

## IDEA-015: Real Async Integration Tests

**Category:** Testing
**Priority Suggestion:** Medium
**Effort:** Medium (1-2 days)
**Origin:** Test suite analysis + closed issue #19

### Problem
All tests mock async behavior. No tests exercise real async flows — token refresh timing, concurrent requests, or actual HTTP calls (even against a test server).

### Proposal
Add `tests/integration/` with:
- A lightweight `httpx`-based mock server
- Tests for concurrent token refresh (validates IDEA-005)
- Tests for timeout behavior under real async conditions
- Tests for E2EE round-trip (encrypt → decrypt)

### Impact
- Catches race conditions that mocks hide
- Validates async cleanup and resource management
- Higher confidence for production deployments
