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
| 2026-03-04 | researcher | IDEA-016: Multi-device E2EE graceful degradation | PENDING |
| 2026-03-04 | researcher | IDEA-017: Custom exception hierarchy | PENDING |
| 2026-03-04 | researcher | IDEA-018: Telemetry & observability hooks | PENDING |
| 2026-03-04 | researcher | IDEA-019: Configuration schema validation | PENDING |
| 2026-03-04 | researcher | IDEA-020: Streaming response support | PENDING |
| 2026-03-04 | researcher | IDEA-021: Request deduplication (idempotency keys) | PENDING |
| 2026-03-04 | researcher | IDEA-022: Deprecated auth flow migration command | PENDING |
| 2026-03-04 | researcher | IDEA-023: Proxy tool registration race condition fix | PENDING |
| 2026-03-04 | researcher | IDEA-024: OAuth token expiration warning | PENDING |
| 2026-03-04 | researcher | IDEA-025: Centralize hardcoded timeout constants (DRY) | PENDING |
| 2026-03-04 | researcher | IDEA-026: Hook script error propagation | PENDING |
| 2026-03-04 | researcher | IDEA-027: File permissions validation after write | PENDING |
| 2026-03-04 | researcher | IDEA-028: CLI help text and examples for advanced options | PENDING |
| 2026-03-04 | researcher | IDEA-029: Silent E2EE key registration failure fix | PENDING |
| 2026-03-04 | researcher | IDEA-030: Hook registry & health check commands | PENDING |

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

---

## IDEA-016: Multi-Device E2EE Graceful Degradation

**Category:** Reliability / Security
**Priority Suggestion:** High
**Effort:** Medium (1 day)
**Origin:** Codebase analysis (proxy_handler_v2.py:200-202)

### Problem
`encrypt_arguments()` always selects the first device key when multiple exist: `device_public_key = PublicKey(device_public_keys[0], ...)`. The code comment acknowledges this is incomplete. If the first device is unreachable, encryption silently fails for multi-device users.

### Proposal
Implement multi-recipient encryption or a fallback strategy:
```python
for device_key in device_public_keys:
    encrypted_copies.append(encrypt_for_device(device_key, payload))
```

### Impact
- Enables reliable E2EE for users with multiple devices
- Prevents silent encryption failure
- Required for production multi-device support

---

## IDEA-017: Custom Exception Hierarchy

**Category:** Architecture / Error Handling
**Priority Suggestion:** High
**Effort:** Medium (1 day)
**Origin:** Codebase analysis across all modules

### Problem
Only `NotLoggedInError` exists. All other errors use bare `Exception`, making it impossible for SDK consumers to handle errors precisely:
- Auth failures vs network timeouts vs encryption errors all look the same
- `except Exception` is the only catching strategy

### Proposal
```python
class HITLError(Exception): pass
class AuthenticationError(HITLError): pass
class TokenExpiredError(AuthenticationError): pass
class EncryptionError(HITLError): pass
class NetworkError(HITLError): pass
class TimeoutError(HITLError): pass
```

### Impact
- SDK consumers can handle specific error types
- Better logging and debugging
- Foundation for retry logic (IDEA-014) — only retry `NetworkError`

---

## IDEA-018: Telemetry & Observability Hooks

**Category:** Observability
**Priority Suggestion:** Low
**Effort:** Medium (1-2 days)
**Origin:** Production observability gap

### Problem
No hooks for measuring request latency, auth method usage, error rates, or tool popularity. Invisible in production.

### Proposal
Add an optional telemetry interface:
```python
class HITLTelemetry(Protocol):
    def on_request(self, method: str, latency_ms: float, status: int): ...
    def on_auth(self, method: str, success: bool): ...
```
Users opt-in by setting `HITL.telemetry = MyCollector()`.

### Impact
- Production visibility for operations teams
- Data-driven optimization decisions
- No overhead when disabled

---

## IDEA-019: Configuration Schema Validation

**Category:** Reliability / DX
**Priority Suggestion:** Medium
**Effort:** Small (half day)
**Origin:** config.py is only 13 lines with zero validation

### Problem
No validation on configuration values. `BACKEND_BASE_URL` could be malformed, timeouts could be negative, log levels could be invalid strings. Failures manifest at runtime, not startup.

### Proposal
Add Pydantic or dataclass validation:
```python
class HITLConfig(BaseModel):
    server_url: HttpUrl
    api_timeout: PositiveInt = 30
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
```

### Impact
- Fail fast on misconfiguration
- Self-documenting settings
- Complements IDEA-003 (centralized config)

---

## IDEA-020: Streaming Response Support

**Category:** Feature / Performance
**Priority Suggestion:** Low
**Effort:** Large (2-3 days)
**Origin:** Roadmap Phase 2 alignment

### Problem
Current implementation waits for the full HTTP response before returning. For long-running human reviews, the CLI appears frozen with no feedback.

### Proposal
Support streaming responses via SSE or chunked transfer:
```python
async for chunk in client.stream_response(request_id):
    print(chunk, end='', flush=True)
```

### Impact
- Better UX for long wait times
- Foundation for real-time collaboration features
- Aligns with Phase 2 roadmap

---

## IDEA-021: Request Deduplication

**Category:** Reliability / Performance
**Priority Suggestion:** Medium
**Effort:** Small (half day)
**Origin:** Codebase analysis

### Problem
If the same request is sent twice (duplicate CLI invocation, retry misfire), both reach the backend, causing duplicate HITL prompts on the user's phone.

### Proposal
Add `X-Idempotency-Key` headers to requests:
```python
import uuid
headers["X-Idempotency-Key"] = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{prompt}:{choices}:{time_window}"))
```

### Impact
- Prevents duplicate prompts on mobile
- Required for reliable retry logic (IDEA-014)
- Low implementation cost

---

## IDEA-022: Deprecated Auth Flow Migration Command

**Category:** Migration / DX
**Priority Suggestion:** Medium
**Effort:** Small (half day)
**Origin:** mcp_client.py:31-32 blocks traditional flow with bare Exception

### Problem
Traditional JWT auth is blocked with `Exception("Traditional OAuth flow is no longer supported...")` but there's no guided migration path. Users hit a wall with no instructions.

### Proposal
Add `hitl-cli auth-migrate` command:
```bash
hitl-cli auth-migrate
# Output: "Migrating from JWT to OAuth 2.1..."
# 1. Detects existing JWT tokens
# 2. Runs OAuth login flow
# 3. Verifies new tokens work
# 4. Archives old token files
```

### Impact
- Smooth migration from legacy to modern auth
- Reduces support burden
- Clears deprecated code path adoption

---

## IDEA-023: Proxy Tool Registration Race Condition Fix

**Category:** Bug / Reliability
**Priority Suggestion:** High
**Effort:** Small (2 hours)
**Origin:** proxy_handler_v2.py:369-423

### Problem
`register_backend_tools()` is async but may not complete before the first tool list request. The proxy server could list zero tools on initial connection.

### Proposal
Either:
1. Register tools synchronously during server init
2. Or add a readiness gate that blocks tool listing until registration completes

### Impact
- Prevents empty tool list on first MCP connection
- Eliminates intermittent "no tools available" errors
- Critical for reliable Claude Desktop integration

---

## IDEA-024: OAuth Token Expiration Warning

**Category:** UX / Reliability
**Priority Suggestion:** Medium
**Effort:** Small (2 hours)
**Origin:** auth.py:427-429, mcp_client.py:55-93

### Problem
Tokens expire silently during long operations. Users discover expiration only when a request fails.

### Proposal
```python
if expires_at and (expires_at - time.time()) < 300:
    logger.warning(f"OAuth token expires in {int((expires_at - time.time()) / 60)}m — consider refreshing")
```
Also add `hitl-cli auth check` to show token status.

### Impact
- Proactive rather than reactive auth management
- Fewer mid-operation auth failures
- Better CI/CD pipeline reliability

---

## IDEA-025: Centralize Hardcoded Timeout Constants (DRY)

**Category:** Architecture / Maintainability
**Priority Suggestion:** Medium
**Effort:** Tiny (1 hour)
**Origin:** 6+ hardcoded timeout values across modules

### Problem
The value `900.0` (human response timeout) appears in:
- `api_client.py` lines 142, 149, 156
- `mcp_client.py` line 27
- `auth.py` line 395

And `30.0` (API timeout) appears in:
- `api_client.py` line 19
- Multiple other locations

Different from IDEA-009 (user-configurable timeouts) — this is about code DRY principle.

### Proposal
Move to `config.py`:
```python
DEFAULT_API_TIMEOUT = 30.0
DEFAULT_HUMAN_TIMEOUT = 900.0
```
Replace all hardcoded values with these constants.

### Impact
- Single place to adjust defaults
- Prerequisite for IDEA-009
- Prevents drift between modules

---

## IDEA-026: Hook Script Error Propagation

**Category:** Reliability / Debugging
**Priority Suggestion:** Medium
**Effort:** Small (2 hours)
**Origin:** hooks/review_and_continue.py:156-166, hooks/codex_notify.py:92-97

### Problem
Hook scripts catch errors but don't log the full context:
- No logging of the command being executed
- No stderr capture from subprocess
- Users see only "CalledProcessError" with no actionable info

### Proposal
```python
try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    logger.debug(f"Hook output: {result.stdout}")
except subprocess.CalledProcessError as e:
    logger.error(f"Hook failed: {' '.join(e.cmd)}")
    logger.error(f"stderr: {e.stderr}")
    logger.error(f"stdout: {e.stdout}")
```

### Impact
- Faster hook debugging
- Self-service troubleshooting
- Reduces "hook doesn't work" support tickets

---

## IDEA-027: File Permissions Validation After Write

**Category:** Security
**Priority Suggestion:** High
**Effort:** Small (2 hours)
**Origin:** auth.py:61,449,472 and crypto.py:72

### Problem
Token and key files are chmod'd to 0o600, but:
1. No verification that permissions were actually set (could fail silently on some filesystems)
2. No warning if file already exists with wrong permissions
3. No secure deletion when tokens are cleared

### Proposal
```python
def save_secure_file(path: Path, data: str) -> None:
    path.write_text(data)
    path.chmod(0o600)
    actual = oct(path.stat().st_mode & 0o777)
    if actual != '0o600':
        logger.warning(f"Could not set permissions on {path}: got {actual}")
```

### Impact
- Validates security posture at runtime
- Catches filesystem permission issues early
- Audit-friendly security logging

---

## IDEA-028: CLI Help Text and Examples for Advanced Options

**Category:** UX / Documentation
**Priority Suggestion:** Low
**Effort:** Small (2 hours)
**Origin:** main.py:220-290

### Problem
Advanced CLI options lack descriptions:
- `--placeholder-text` — no explanation of what it does
- `--choice` — unclear if radio buttons or checkboxes
- `--e2ee` — no guidance on when to use vs automatic detection
- No usage examples in help output

### Proposal
Add rich help text with examples:
```python
@app.command()
def request(
    prompt: str = typer.Option(..., help="Question to present to the human"),
    choice: list[str] = typer.Option(None, "--choice", help="Predefined response options (e.g., --choice Yes --choice No)"),
    placeholder_text: str = typer.Option(None, help="Placeholder text shown in the free-text input field"),
    e2ee: bool = typer.Option(False, help="Force end-to-end encryption (auto-detected when keys exist)"),
):
    """Request human input via HITL relay.

    Examples:
        hitl-cli request --prompt "Deploy to prod?" --choice Yes --choice No
        hitl-cli request --prompt "Enter API key" --e2ee
    """
```

### Impact
- Better discoverability of CLI features
- Reduces learning curve for new users
- Self-documenting interface

---

## IDEA-029: Silent E2EE Key Registration Failure Fix

**Category:** Bug / Security
**Priority Suggestion:** High
**Effort:** Small (2 hours)
**Origin:** crypto.py:148-221

### Problem
`ensure_agent_keypair()` catches all exceptions during key registration:
```python
except Exception as e:
    logger.error(f"Failed to register public key: {e}")
    return public_key, private_key  # Returns keys anyway!
```
The agent continues with unregistered keys. The backend will reject encrypted messages later, but the user gets no warning at registration time.

### Proposal
Either:
1. Propagate the error (fail fast)
2. Or set a flag and warn on first HITL request: "E2EE keys not registered — encrypted requests will fail"
3. Or retry registration with backoff

### Impact
- Prevents mysterious E2EE failures minutes/hours after login
- Clear error signal for debugging
- Critical for users relying on E2EE

---

## IDEA-030: Hook Registry & Health Check Commands

**Category:** Feature / Architecture
**Priority Suggestion:** Medium
**Effort:** Medium (1 day)
**Origin:** Codebase analysis — hooks installed as entry points but invisible

### Problem
Hooks are installed as separate CLI entry points (`hitl-hook-review-and-continue`, `hitl-codex-notify`) but there's no:
1. Central registry to discover installed hooks
2. Health check to validate hooks are executable
3. Testing framework for hooks
4. Documentation linking CLI commands to available hooks

### Proposal
Add hook management commands:
```bash
hitl-cli hooks list          # Show installed hooks and their entry points
hitl-cli hooks check         # Validate all hooks are executable and configured
hitl-cli hooks test <name>   # Dry-run a hook with mock data
```

### Impact
- Makes hook ecosystem discoverable
- Validates hook installation (common source of issues)
- Enables future hook marketplace/registry
