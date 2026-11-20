# Ideas Batch — hitl-cli (Batch 575)

## IDEA-673: OAuth 2.1 Bearer & Auto-Refresh Support in `ApiClient` for REST and E2EE Commands
- **Category**: Tech Debt
- **Problem**: `ApiClient._get_headers()` in `hitl_cli/api_client.py` only checks `is_using_api_key()` and legacy `get_current_token()` (`token.json`), completely ignoring OAuth 2.1 tokens in `oauth_token.json`. Consequently, users authenticated via `hitl-cli login` fail immediately with `"Not logged in"` whenever they run `agents list`, `agents create`, or any `--e2ee` command (`request --e2ee`, `notify --e2ee`, `notify-completion --e2ee`).
- **Proposed Solution**: Extend `ApiClient` with an async header resolver that checks `is_using_oauth()`, reads `oauth_token.json`, automatically calls `refresh_oauth_token()` when `is_oauth_token_expired()` is true, and retries once on HTTP 401 before exiting. Extract the token-refresh routine shared with `MCPClient._get_oauth_token()` into `hitl_cli/auth.py` so REST, E2EE, and MCP paths behave identically.
- **Business Value**: Fixes a critical out-of-the-box authentication failure where OAuth-authenticated users cannot manage agents or send E2EE requests without falling back to manual API keys.
- **Effort Estimate**: S

---

## IDEA-674: Hardened OAuth Callback Server with XSS Escaping, Socket Reuse, and Refresh-Grant Negotiation
- **Category**: Security
- **Problem**: `OAuthCallbackHandler.do_GET()` in `hitl_cli/auth.py` interpolates the raw `error` query parameter unescaped into its HTML response (creating a reflected XSS vector on `localhost:8080/callback`), while `OAuthDynamicClient` requests only `["authorization_code"]` without `"refresh_token"`, binds `TCPServer` without `allow_reuse_address = True`, and stalls the `asyncio` event loop with `time.sleep(0.5)`.
- **Proposed Solution**: Escape all callback query parameters (`error`, `error_description`) with `html.escape()` and return a strict `Content-Security-Policy: default-src 'none'` header on callback HTML pages. Subclass `TCPServer` with `allow_reuse_address = True`, replace the blocking `time.sleep` loop with an `asyncio.Event` signaled via `loop.call_soon_threadsafe()`, and include `"refresh_token"` in dynamic client `grant_types` alongside `offline_access` scope.
- **Business Value**: Eliminates a local browser XSS vulnerability and prevents `Address already in use` and missing-refresh-token failures during OAuth onboarding.
- **Effort Estimate**: S

---

## IDEA-675: Purge Tracked API Key & Consolidate Root Ad-Hoc Antigravity Hook Scripts
- **Category**: Security
- **Problem**: Repository-root scripts `review_and_continue_wrapper.sh` and `review_and_continue_antigravity.py` embed a literal `HITL_API_KEY`, hardcode machine-specific `/Users/slaser79/...` paths, write raw transcripts to `debug_stdin.json`, and duplicate `hitl_cli/hooks/review_and_continue.py` while diverging on `fullyIdle=False` handling (issue #75).
- **Proposed Solution**: Rotate the exposed key and delete the root-level ad-hoc scripts, folding Antigravity `fullyIdle` and `PLANNER_RESPONSE` transcript parsing cleanly into `hitl_cli/hooks/review_and_continue.py` so `fullyIdle=False` returns `{"decision": "allow", "reason": ""}` without token-burning loops. Resolve the CLI binary portably via `shutil.which("hitl-cli")` with `sys.executable` fallback and add CI secret scanning (`gitleaks`) to block future credential commits.
- **Business Value**: Eliminates an active API key exposure in a public MIT-licensed repository and removes divergent hook maintenance across Antigravity and Claude Code.
- **Effort Estimate**: S

---

## IDEA-676: E2EE Proxy Parity for `notify_human_completion`, `placeholder_text`, and Closure-Safe Tool Forwarding
- **Category**: Tech Debt
- **Problem**: In `hitl_cli/proxy_handler_v2.py`, `create_fastmcp_proxy_server()` omits an E2EE wrapper for `notify_human_completion`, drops `placeholder_text` and `agent_name` from `request_human_input`, never awaits `register_backend_tools()`, and suffers from a late-binding Python closure bug (`actual_tool_name = tool_name` inside a `for` loop) that routes every dynamic pass-through tool to the last item while discarding `inputSchema`.
- **Proposed Solution**: Implement an E2EE-wrapped `notify_human_completion` tool and align `request_human_input` parameters (`placeholder_text`, `agent_name`) with `MCPClient`. Fix the loop closure via a factory helper capturing `tool_name` by value, preserve upstream `inputSchema` schemas, and invoke `register_backend_tools()` inside FastMCP's async startup lifespan hook.
- **Business Value**: Prevents silent plaintext fallbacks and broken dynamic tool routing when AI agents run end-to-end encrypted sessions through `hitl-cli proxy`.
- **Effort Estimate**: S

---

## IDEA-677: `O(1)` Reverse-Seek JSONL Tail Reader for Long-Session Agent Stop Hooks
- **Category**: Performance
- **Problem**: `get_last_assistant_messages()` in `hitl_cli/hooks/review_and_continue.py` calls `f.readlines()` inside a multi-attempt stabilization loop, loading and iterating entire multi-megabyte JSONL session transcripts into memory up to six times per turn just to extract the final assistant message.
- **Proposed Solution**: Replace `f.readlines()` with a bounded reverse-seek tail reader (`os.SEEK_END` scanning backwards in 64 KB chunks) that parses lines from EOF until `num_messages` valid assistant entries are collected, falling back cleanly for small files. This keeps transcript extraction constant-memory and sub-millisecond even in 100+ MB coding sessions.
- **Business Value**: Eliminates hook memory spikes and multi-second stop-hook stalls during long autonomous agent sessions.
- **Effort Estimate**: S

---

## IDEA-678: Device Public-Key TTL Cache & Versioned Ciphertext Envelope in E2EE Mode
- **Category**: Performance
- **Problem**: Every E2EE call in `hitl_cli/api_client.py` (`request_human_input_e2ee`, `notify_human_e2ee`, `notify_task_completion_e2ee`) and `hitl_cli/proxy_handler_v2.py` issues a fresh uncached `GET /api/v1/keys/user` or `/api/v1/devices/public-keys` request before encrypting, and emits bare base64 blobs with no envelope version or recipient key identifier.
- **Proposed Solution**: Add an in-memory TTL cache (default 5 minutes, invalidated automatically on decryption or key-mismatch errors) for fetched device public keys in `hitl_cli/crypto.py`, and optionally wrap ciphertext in a versioned JSON envelope (`{"v": 1, "alg": "x25519-xsalsa20-poly1305", "kid": "<fingerprint>", "ct": "..."}`) with backward-compatible fallback for raw base64 payloads.
- **Business Value**: Cuts E2EE pre-request network overhead by 50% per prompt while enabling seamless future cipher upgrades and clearer key-mismatch diagnostics.
- **Effort Estimate**: S

---

## IDEA-679: `HITL_API_KEY` Support in MCP Proxy Mode & README Quickstart Alignment
- **Category**: Feature
- **Problem**: `README.md` instructs users to configure `hitl-cli proxy` with `"HITL_API_KEY": "your_api_key_here"` in `mcp_servers.json`, yet `proxy()` in `hitl_cli/main.py`, `BackendMCPClient`, and `get_device_public_keys()` in `hitl_cli/proxy_handler_v2.py` hard-require OAuth tokens, and `crypto.register_public_key_with_backend()` fails because `get_current_agent_id()` returns `None` under API-key auth.
- **Proposed Solution**: Support `X-API-Key` authentication in `main.py:proxy`, `BackendMCPClient`, and `get_device_public_keys()`, and resolve the target `agent_id` from `--agent-id`, `HITL_AGENT_ID`, or `GET /api/v1/agents` when registering E2EE keys with an API key. Add unit tests covering API-key proxy startup and key registration so the documented quickstart works out of the box.
- **Business Value**: Makes the primary `README.md` MCP proxy installation recipe actually work for CI, headless workstations, and service-account users.
- **Effort Estimate**: S

---

## IDEA-680: Atomic `0o600` Credential & Keypair Persistence (Eliminating Write-Then-Chmod TOCTOU)
- **Category**: Security
- **Problem**: `save_token()`, `save_oauth_client()`, and `save_oauth_token()` in `hitl_cli/auth.py` and `save_agent_keypair()` in `hitl_cli/crypto.py` create or truncate secret files via `open(..., "w")` / `Path.write_text()` under the process default umask (`0o644`) before calling `os.chmod(..., 0o600)` afterward, exposing a TOCTOU read window and risking truncated JSON on crash.
- **Proposed Solution**: Introduce a shared `atomic_write_secret(path, content)` helper that opens a sibling temporary file with `os.open(..., os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)`, writes and `fsync`s the payload, and atomically swaps it into place via `os.replace()`. Refactor all token, client-registration, and `agent.key` writers to use it.
- **Business Value**: Eliminates secret-file permission race conditions on shared hosts and prevents corrupted credential files after sudden process termination.
- **Effort Estimate**: S

---

## IDEA-681: Local Pre-Flight Argument & Byte-Budget Validation Before Encryption or Relay Dispatch
- **Category**: Performance
- **Problem**: `hitl_cli/mcp_client.py` and `hitl_cli/proxy_handler_v2.py` encrypt payloads and open remote connections even when an agent passes an empty prompt, duplicate or blank choices, or multi-megabyte strings, wasting relay round-trips and returning opaque server HTTP 422/500 errors to the caller.
- **Proposed Solution**: Add a lightweight pre-flight validator shared by CLI commands, `HITL` SDK methods, and the MCP proxy that checks non-empty `prompt`/`message`/`summary`, deduplicates and bounds choice lists, enforces configurable UTF-8 payload byte limits, and raises structured validation messages locally before encryption or HTTP transport.
- **Business Value**: Eliminates wasted relay traffic on malformed LLM tool calls and enables autonomous agents to self-correct invalid arguments on the first retry.
- **Effort Estimate**: S

---

## IDEA-682: Persistent Default Agent Binding & Cleanup Subcommands (`hitl-cli agents set-default / prune`)
- **Category**: Feature
- **Problem**: Whenever JWT claims omit `agent_id`, `hitl_cli/mcp_client.py` silently creates a brand-new throwaway agent named `hitl-cli-<8-hex>` via `POST /api/v1/agents` on every `request`, `notify`, or `notify-completion` call, flooding the mobile app with orphaned agents while `hitl-cli agents` provides only `list` and `create`.
- **Proposed Solution**: Persist the active `default_agent_id` in `~/.config/hitl-cli/config.json` during `hitl-cli login` and `agents create` rather than minting ephemeral agents per call. Add `hitl-cli agents set-default <agent-id>`, `hitl-cli agents delete <agent-id>`, and `hitl-cli agents prune --prefix hitl-cli-` commands to inspect and clean up stale agents.
- **Business Value**: Prevents mobile agent-list sprawl and guarantees consistent agent identity, notification threading, and E2EE key binding across CLI sessions.
- **Effort Estimate**: S

---

## IDEA-683: Live-Check CLI Documentation & Help-Flag Parity Test Suite
- **Category**: Tech Debt
- **Problem**: Multiple project documents have drifted from the live code—`.specs/01_system_context.md` references Click instead of Typer, `.specs/02_roadmap.md` lists `ask` instead of `request`, `CLAUDE.md` specifies `~/.hitl/` while `config.py` uses `~/.config/hitl-cli/`, and `README.md` documents unsupported flag combinations—causing both human contributors and AI workers to misconfigure commands.
- **Proposed Solution**: Add an automated pytest suite using `typer.testing.CliRunner` and AST/Markdown parsing that extracts every `hitl-cli ...` invocation from `README.md` and `CLAUDE.md`, verifies the subcommand and options actually exist in `hitl_cli.main:app` (`--help` / dry-parse check), and fails CI whenever documentation and CLI signatures diverge.
- **Business Value**: Keeps onboarding docs and agent instructions permanently synchronized with the live CLI surface with zero manual maintenance.
- **Effort Estimate**: S

---

## IDEA-684: Zero-Touch IDE & Agent MCP Config Generator (`hitl-cli setup`)
- **Category**: UX
- **Problem**: `hitl-cli login` prints only a single hardcoded Claude Desktop JSON snippet (`main.py:76-84`) that omits custom `HITL_SERVER_URL` settings and leaves users to manually craft configs for Cursor, Windsurf, Claude Code (`Stop` hook), Codex CLI (`~/.codex/config.toml`), and Antigravity.
- **Proposed Solution**: Implement a `hitl-cli setup [claude-desktop|claude-code|cursor|windsurf|codex|antigravity]` command that resolves the active `hitl-cli` binary path, outputs tailored MCP/hook configuration snippets carrying configured `HITL_SERVER_URL` overrides, and supports `--apply` for atomic, backup-preserving merges into target JSON/TOML config files.
- **Business Value**: Compresses multi-tool onboarding from 15 minutes of fragile manual file editing to one deterministic command, boosting developer activation.
- **Effort Estimate**: S

---

## IDEA-685: Headless SSH / Container Login Detection & `--no-browser` Port-Forwarding Guide
- **Category**: UX
- **Problem**: Running `hitl-cli login` over SSH, inside Docker containers, or on headless cloud devboxes calls `webbrowser.open(auth_url)` (`hitl_cli/auth.py:389`) and blocks silently for 15 minutes waiting on `localhost:8080/callback` with no guidance on forwarding the OAuth callback port or switching to `HITL_API_KEY`.
- **Proposed Solution**: Detect headless environments (`SSH_CONNECTION`, missing `DISPLAY`/`WAYLAND_DISPLAY` on Linux, `CI=true`) before opening a browser, print clear `ssh -L 8080:localhost:8080` port-forwarding and `HITL_API_KEY` instructions, and add a `--no-browser` flag that skips `webbrowser.open()` while printing a clean copy-pasteable authorization URL.
- **Business Value**: Eliminates confusing 15-minute CLI hangs for remote SSH and cloud-IDE developers during initial setup.
- **Effort Estimate**: S

---

## IDEA-686: MCP Progress Notification Heartbeats (`notifications/progress`) During Long Human Waits
- **Category**: Integration
- **Problem**: During `hitl-cli proxy` sessions, `request_human_input` blocks silently for up to 900 seconds waiting for a mobile reply while emitting zero MCP protocol traffic, causing IDE MCP hosts (Claude Desktop, Cursor, Antigravity) with 60-second tool-call inactivity timeouts to cancel the request prematurely.
- **Proposed Solution**: Accept FastMCP's `Context` in `proxy_handler_v2.py` tools (`request_human_input`, `notify_human_completion`) and run a background asyncio ticker that calls `await ctx.report_progress(...)` every 15 seconds with elapsed wait status while `backend_client.call_tool()` is pending, cleanly canceling the ticker once the human responds.
- **Business Value**: Prevents IDE MCP clients from timing out mid-approval during realistic human review cycles that exceed 60 seconds.
- **Effort Estimate**: S

---

## IDEA-687: Claude Code `Notification` & `PermissionRequest` Real-Time Hook Adapters
- **Category**: Integration
- **Problem**: `hitl_cli/hooks/` currently covers only end-of-turn `Stop` (`review_and_continue.py`) and Codex `notify` (`codex_notify.py`), leaving autonomous Claude Code users without mobile alerts on mid-turn `Notification` events or remote approval for interactive `PermissionRequest` tool prompts.
- **Proposed Solution**: Add `hitl_cli/hooks/claude_permission.py` and `hitl_cli/hooks/claude_notification.py` entry points (`hitl-hook-permission`, `hitl-hook-notification`) that parse Claude Code hook stdin JSON, dispatch concise tool-name/command prompts via `HITL` (with E2EE support), and emit structured `hookSpecificOutput.decision` JSON back to Claude Code.
- **Business Value**: Upgrades `hitl-cli` from a post-turn review loop into a real-time mobile permission controller for unattended autonomous coding runs.
- **Effort Estimate**: M
