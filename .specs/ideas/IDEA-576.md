# Ideas Batch — hitl-cli (Batch 576)

## IDEA-688: MCP `CallToolResult.isError` Propagation & FastMCP `TextContent` Decryption Normalization
- **Category**: Tech Debt
- **Problem**: `MCPClient.call_tool()` in `hitl_cli/mcp_client.py` ignores `result.isError` on FastMCP `CallToolResult` objects, returning server error messages (such as timeouts or agent-lookup failures) as normal human responses with exit code 0—causing stop hooks to feed relay errors back to AI agents as user instructions. Meanwhile, `decrypt_response()` in `hitl_cli/proxy_handler_v2.py` only accepts `dict` or `str` inputs and crashes with `"Unknown encrypted response format"` when `BackendMCPClient.call_tool()` returns a FastMCP `CallToolResult` or `TextContent` object.
- **Proposed Solution**: Extract a shared `extract_mcp_result(result)` helper in `hitl_cli/mcp_client.py` that inspects `getattr(result, "isError", False)` and raises a descriptive exception containing the server's error text, and reuse it in `proxy_handler_v2.decrypt_response()` before PyNaCl decryption. Normalize decrypted payloads so both JSON `{"response": ...}` envelopes and raw UTF-8 strings behave identically across REST and MCP transports.
- **Business Value**: Stops autonomous stop hooks from treating relay error messages as human commands and fixes a breaking type mismatch in live E2EE MCP proxy mode.
- **Effort Estimate**: S

---

## IDEA-689: Path-Filtered Multi-Request Loop in `OAuthCallbackHandler` (`favicon.ico` Resilience)
- **Category**: UX
- **Problem**: `OAuthDynamicClient._start_callback_server()` in `hitl_cli/auth.py` runs `server.handle_request()` once and `OAuthCallbackHandler.do_GET()` does not check `parsed_url.path == "/callback"`. When a browser sends a speculative `/favicon.ico` or preflight request to `localhost:8080` first, the server consumes that request, populates `callback_data` with `code=None, state=None`, and immediately aborts `hitl-cli login` with a spurious CSRF state mismatch.
- **Proposed Solution**: Guard `OAuthCallbackHandler.do_GET()` so requests to paths other than `self.callback_path` (such as `/favicon.ico`) return HTTP `404` without mutating `callback_data`, and run `handle_request()` in a loop until a valid `/callback` request arrives or the login timeout expires. Ignore stray non-OAuth probes lacking both `code` and `error` query parameters so browser preconnects cannot terminate the listener early.
- **Business Value**: Eliminates random browser-induced OAuth login failures during `hitl-cli login`, improving first-run developer onboarding reliability.
- **Effort Estimate**: S

---

## IDEA-690: Server-Origin Scoping & Issuer Verification for Stored OAuth and Keypair Credentials
- **Category**: Security
- **Problem**: `hitl_cli/config.py` stores `oauth_client.json`, `oauth_token.json`, `token.json`, and `agent.key` directly under `~/.config/hitl-cli/` with no record of which `HITL_SERVER_URL` issued them. Switching `HITL_SERVER_URL` between `https://hitlrelay.app` and a local or staging relay silently transmits production bearer tokens and client credentials to the wrong host.
- **Proposed Solution**: Persist an `"issuer_url"` (normalized scheme, host, and port) inside stored credential and keypair files—or scope storage into per-origin subdirectories under `~/.config/hitl-cli/servers/<origin_hash>/`—and verify the active `BACKEND_BASE_URL` matches before attaching `Authorization` headers in `auth.py`, `api_client.py`, and `mcp_client.py`. When a mismatch is detected, abort safely with an actionable message instructing the user to re-authenticate against the active server.
- **Business Value**: Prevents accidental production OAuth bearer-token leakage when developers test against local or staging relay instances.
- **Effort Estimate**: M

---

## IDEA-691: Agent Endpoint Schema Normalization (`id` vs `agent_id`) & OAuth `--agent-id` Honor
- **Category**: Tech Debt
- **Problem**: `hitl_cli/main.py` (`agents create`) reads `result.get("id")` from `POST /api/v1/agents` while `MCPClient.create_agent_for_mcp()` in `hitl_cli/mcp_client.py` indexes `result["agent_id"]`, guaranteeing either a `KeyError` or `"ID: N/A"` output on one code path. Furthermore, `hitl-cli request`, `notify`, and `notify-completion` silently discard `--agent-id` when using OAuth or `HITL_API_KEY` authentication.
- **Proposed Solution**: Add a shared `extract_agent_id(payload)` helper accepting `payload.get("id") or payload.get("agent_id")` across `main.py` and `mcp_client.py`, and forward `agent_id` consistently in OAuth and REST tool/request payloads when explicitly provided. Emit a clear warning if mutually incompatible `--agent-id` and `--agent-name` options are combined so CLI behavior matches `--help` documentation.
- **Business Value**: Fixes a latent crash during automatic agent creation and makes multi-agent attribution flags reliable across all authentication modes.
- **Effort Estimate**: S

---

## IDEA-692: Encrypted Hook Mode (`HITL_E2EE=1` / `--e2ee`) for `review_and_continue` and `codex_notify`
- **Category**: Security
- **Problem**: Even after a user runs `hitl-cli login` and generates an E2EE keypair, `hitl_cli/hooks/review_and_continue.py` and `hitl_cli/hooks/codex_notify.py` always invoke `hitl-cli notify-completion` and `hitl-cli notify` in plaintext without `--e2ee`, transmitting assistant code summaries and working-directory context unencrypted through the relay.
- **Proposed Solution**: Add a `--e2ee` flag and `HITL_E2EE=1` environment variable support (with optional auto-enable when `agent.key` exists and `e2ee_hooks` is configured) to both `hitl-hook-review-and-continue` and `hitl-codex-notify`, forwarding `--e2ee` to the underlying CLI/SDK calls. Fail closed with an explicit `stderr` diagnostic on key or decryption errors rather than silently falling back to plaintext.
- **Business Value**: Closes a silent privacy gap so coding-agent transcripts and turn summaries remain end-to-end encrypted during autonomous Claude Code, Antigravity, and Codex hook loops.
- **Effort Estimate**: S

---

## IDEA-693: String-Content Message Support & Antigravity JSON Exit Parity in `review_and_continue`
- **Category**: UX
- **Problem**: In `hitl_cli/hooks/review_and_continue.py`, `get_last_assistant_messages()` rejects `entry["message"]["content"]` whenever it is a plain `str` instead of a `list`, silently dropping assistant turns, while Antigravity mode (`--antigravity` / `IS_ANTIGRAVITY=1`) exits `0` with empty stdout on `"YOU ARE DONE"` or missing `transcript_path` instead of emitting `{"decision": "allow", "reason": ""}` as required by Antigravity hooks.
- **Proposed Solution**: Normalize `message["content"]` in `get_last_assistant_messages()` when it is a `str` (wrapping `[content]` just like flat `PLANNER_RESPONSE` entries) and centralize Antigravity allow-exit handling in a helper that emits `{"decision": "allow", "reason": ""}` across every allow-stop branch. Add regression tests in `tests/hooks/test_review_and_continue.py` covering string-content transcripts and Antigravity allow-exit JSON output.
- **Business Value**: Eliminates silently dropped assistant messages and malformed stop-hook stdout errors in Antigravity and Claude Code sessions.
- **Effort Estimate**: S

---

## IDEA-694: `HITL_API_KEY` Precedence & Cross-Account `agent_id` Contamination Guard
- **Category**: Security
- **Problem**: When `HITL_API_KEY` is set on a machine that also has an older `oauth_token.json` on disk, `get_current_agent_id()` in `hitl_cli/auth.py` still decodes the stale OAuth JWT (`verify_signature=False`) and returns the old OAuth user's `agent_id` to `crypto.register_public_key_with_backend()`, while `hitl-cli login` reports `"Already logged in!"` without noting the active `HITL_API_KEY` override.
- **Proposed Solution**: Short-circuit `get_current_agent_id()` to return `HITL_AGENT_ID` (or `None` when unset) whenever `is_using_api_key()` is true so stale OAuth files never leak across authentication modes, and log explicit warnings instead of swallowing `jwt.PyJWTError` when decoding non-JWT tokens. Update `hitl-cli login` to warn clearly when `HITL_API_KEY` is set in the environment and will override interactive OAuth credentials.
- **Business Value**: Prevents cross-account E2EE public-key misregistration and eliminates confusing auth-precedence surprises in mixed interactive/CI environments.
- **Effort Estimate**: S

---

## IDEA-695: `HITL` Python SDK Parity for `timeout`, `agent_id`, `delete_agent`, and Config Injection
- **Category**: Feature
- **Problem**: The `HITL` class in `hitl_cli/sdk.py` supports `request_input()`, `notify_completion()`, `notify()`, `create_agent()`, and `list_agents()`, but omits per-call `timeout` and `agent_id` parameters, lacks `get_agent()` and `delete_agent()` lifecycle methods, and cannot accept explicit `base_url` or `api_key` credentials without mutating process-wide environment variables.
- **Proposed Solution**: Add optional `base_url: str | None = None` and `api_key: str | None = None` constructor arguments to `HITL`, expose `timeout: float | None = None` and `agent_id: str | None = None` on `request_input()`, `notify_completion()`, and `notify()`, and implement `get_agent(agent_id)` and `delete_agent(agent_id)` wrappers. Thread constructor-scoped config down to `ApiClient` and `MCPClient` so multiple isolated SDK instances can coexist safely in one Python process.
- **Business Value**: Makes the `HITL` Python SDK viable for multi-tenant services and concurrent agent orchestrators without fragile `os.environ` hacks.
- **Effort Estimate**: M

---

## IDEA-696: Async `admin register-client` with Timeout Guard & Automatic OAuth Token Refresh
- **Category**: Tech Debt
- **Problem**: `admin_register_client()` in `hitl_cli/main.py` calls synchronous `httpx.post()` directly with no explicit timeout (defaulting to httpx's 5-second limit instead of 30 seconds) and reads `oauth_token.json` directly without checking expiration or invoking `refresh_oauth_token()`, causing avoidable 401 and timeout errors for admins.
- **Proposed Solution**: Refactor `admin register-client` to dispatch asynchronously via `ApiClient` (or a shared OAuth-aware request helper) with a 30-second timeout, automatic OAuth token refresh prior to the request, and consistent status/error formatting. Add unit tests mocking `POST /api/v1/oauth/clients/register` for expired-token refresh and non-201 error handling.
- **Business Value**: Eliminates flaky admin client-registration failures and removes an inconsistent synchronous `httpx.post` bypass from `main.py`.
- **Effort Estimate**: S

---

## IDEA-697: Remote-First `daily-report` Commit Query Fallback & `--output` Markdown Export
- **Category**: UX
- **Problem**: `_generate_report()` in `hitl_cli/main.py` runs `git log ... origin/main` in the current working directory regardless of `--repo`, failing with a warning whenever `hitl-daily-report --repo <owner/name>` runs outside a local clone of that repository, and prints only to stdout instead of writing dated report files cleanly.
- **Proposed Solution**: Inspect the local `origin` remote URL first and fall back to `gh api repos/{repo}/commits?since=...` whenever the working directory is not a clone of `--repo` (or outside a git repo), and add `--output <path>` / `--format markdown|text` options to write reports directly to files such as `docs/reports/daily/YYYY-MM-DD.md`. Include the clickable GitHub PR/issue numbers and commit SHAs consistently in exported Markdown.
- **Business Value**: Makes `hitl-daily-report` work reliably from any directory or automated CI runner without requiring a local checkout of every target repository.
- **Effort Estimate**: S

---

## IDEA-698: Keypair-Aware `hitl-cli logout --purge-keys` & Malformed E2EE Envelope Guard in `ApiClient`
- **Category**: Security
- **Problem**: `hitl-cli logout` deletes `token.json`, `oauth_client.json`, and `oauth_token.json` but leaves `agent.key` intact on disk, while `ApiClient.request_human_input_e2ee()` and `notify_task_completion_e2ee()` in `hitl_cli/api_client.py` index `response["encrypted_response"]` and `user_keys[0]["public_key"]` without checking structure—raising raw `KeyError`/`TypeError` tracebacks on timeout or malformed relay responses.
- **Proposed Solution**: Add a `--purge-keys` flag to `hitl-cli logout` (and print a reminder if `agent.key` remains on disk) to securely remove local E2EE keypairs during workstation offboarding, and validate both `/api/v1/keys/user` entries and `"encrypted_response"` fields in `api_client.py` with descriptive error messages. Log a clear diagnostic when the relay returns a non-encrypted timeout or status payload instead of ciphertext.
- **Business Value**: Supports clean cryptographic offboarding on shared workstations and replaces opaque E2EE `KeyError` crashes with actionable troubleshooting errors.
- **Effort Estimate**: S

---

## IDEA-699: Shared `BearerAuth` & Pooled FastMCP Transport Factory across `mcp_client.py` and `proxy_handler_v2.py`
- **Category**: Performance
- **Problem**: `hitl_cli/mcp_client.py` and `hitl_cli/proxy_handler_v2.py` redefine an identical nested `class BearerAuth(httpx.Auth)` inside three separate methods (`MCPClient.call_tool`, `BackendMCPClient.list_tools`, `BackendMCPClient.call_tool`) and allocate fresh `fastmcp.Client` transports on every tool invocation.
- **Proposed Solution**: Extract a single `BearerAuth` implementation and a `build_mcp_transport(mcp_url, headers_or_auth)` factory in `hitl_cli/mcp_client.py`, reusing a shared `httpx.AsyncClient` connection pool for HTTP keep-alive across consecutive tool calls in `BackendMCPClient` and `MCPClient`. Expose explicit `aclose()` lifecycle hooks so CLI commands and proxy shutdown release pooled sockets cleanly.
- **Business Value**: Eliminates duplicated auth transport code and removes redundant TLS handshakes across multi-turn MCP proxy and CLI sessions.
- **Effort Estimate**: S

---

## IDEA-700: Portable `hitl-cli` Binary Discovery (`HITL_CLI_BIN` / `sys.executable`) in Agent Hooks
- **Category**: Integration
- **Problem**: `hitl_cli/hooks/review_and_continue.py` and `hitl_cli/hooks/codex_notify.py` invoke bare `["hitl-cli", ...]` via `PATH`, which fails in GUI-launched desktop apps (Claude Desktop, Antigravity IDE, Codex) whose minimal `PATH` omits `~/.local/bin`, Nix profiles, or virtualenvs—prompting brittle hardcoded paths like `/Users/slaser79/...` in `review_and_continue_wrapper.sh`.
- **Proposed Solution**: Introduce a shared `resolve_hitl_cli_command()` helper in `hitl_cli/hooks/__init__.py` that resolves the executable in order: `HITL_CLI_BIN` environment override, sibling `Path(sys.executable).parent / "hitl-cli"`, `shutil.which("hitl-cli")`, and `[sys.executable, "-m", "hitl_cli"]` fallback. Emit an immediate `stderr` diagnostic if no binary or auth credential (`HITL_API_KEY` or stored token) is reachable before attempting dispatch.
- **Business Value**: Eliminates `"FileNotFoundError: 'hitl-cli'"` hook failures in GUI-spawned IDE sessions across macOS and Linux without hardcoded user paths.
- **Effort Estimate**: S

---

## IDEA-701: `hitl-cli --version` Flag & Relay Compatibility Check Command (`hitl-cli version`)
- **Category**: UX
- **Problem**: `hitl-cli` lacks both a `--version` / `-V` CLI option and a `version` subcommand (`hitl-cli --version` fails with `No such option`), preventing users, support tickets, and orchestrators like `hitl-channel` from checking the installed `hitl-cli` version and dependency versions programmatically.
- **Proposed Solution**: Register an eager `--version` / `-V` Typer callback on the root `app` in `hitl_cli/main.py` backed by `importlib.metadata.version("hitl-cli")`, and add a `hitl-cli version [--check-server]` command that prints Python, `fastmcp`, `pynacl`, and `httpx` versions alongside optional `/health` compatibility metadata from `BACKEND_BASE_URL`. Support `--json` output for automated pre-flight checks in CI and wrapper scripts.
- **Business Value**: Accelerates issue triage and allows companion tools (`hitl-channel`, `agent_workflows`) to verify compatible `hitl-cli` installations in one command.
- **Effort Estimate**: S

---

## IDEA-702: Shared `HITL_DAEMON_SESSION` Helper & Schema-Based Antigravity Auto-Detection in Hooks
- **Category**: Integration
- **Problem**: `hitl_cli/hooks/review_and_continue.py` and `hitl_cli/hooks/codex_notify.py` duplicate the `HITL_DAEMON_SESSION=1` / `HITL_HOOK_DEBUG=1` early-exit logic and `/tmp/hitl_hook_daemon_skip.log` path handling across modules, while `review_and_continue.py` requires explicit `--antigravity` or `IS_ANTIGRAVITY=1` flags even when Antigravity's distinctive camelCase `fullyIdle` / `transcriptPath` fields are already present in stdin JSON.
- **Proposed Solution**: Extract a shared `check_daemon_session_skip(hook_name, is_antigravity)` helper in `hitl_cli/hooks/__init__.py` reused by both hooks, including `cwd` and `pid` in debug lines when `HITL_HOOK_DEBUG=1`. Enhance `review_and_continue.py` to auto-detect Antigravity payloads when `"fullyIdle" in input_data or "transcriptPath" in input_data` in addition to `--antigravity` and `IS_ANTIGRAVITY=1`.
- **Business Value**: Reduces hook wrapper configuration friction for `hitl-channel` daemon isolation and eliminates duplicated early-exit logic across hook entry points.
- **Effort Estimate**: S
