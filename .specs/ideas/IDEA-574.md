# Ideas Batch — hitl-cli (Batch 574)

## IDEA-658: XDG Base Directory Compliance & Legacy `~/.hitl/` Path Unification (`hitl-cli config migrate`)
- **Category**: Tech Debt
- **Problem**: `hitl_cli/config.py` hardcodes `~/.config/hitl-cli/` while `README.md`, `CLAUDE.md`, and `AGENTS.md` instruct users to inspect `~/.hitl/` for tokens and keys, and environment overrides such as `XDG_CONFIG_HOME` are ignored. This discrepancy creates recurring debugging confusion and breaks XDG-compliant Linux/macOS and containerized workstation setups.
- **Proposed Solution**: Refactor `hitl_cli/config.py` to resolve configuration, state, and cache paths according to the XDG Base Directory specification (`XDG_CONFIG_HOME`, `XDG_STATE_HOME`, `XDG_CACHE_HOME`) with an explicit `HITL_CONFIG_DIR` override. Add startup auto-detection that warns once if legacy `~/.hitl/` credentials are present and provides `hitl-cli config migrate` to safely relocate them with `0600` permissions while syncing all repository documentation.
- **Business Value**: Eliminates a well-known developer support trap and enables clean deployment in read-only containers and XDG-compliant environments.
- **Effort Estimate**: S

---

## IDEA-659: Optional `[legacy-jwt]` Extra & In-Process Hook Dispatch for Sub-50ms Cold Starts
- **Category**: Performance
- **Problem**: `pyproject.toml` declares `google-auth` and `google-auth-oauthlib` as mandatory top-level dependencies even though the Firebase/JWT flow is legacy-only, and both `review_and_continue.py` and `codex_notify.py` spawn `subprocess.run(["hitl-cli", ...])` as a cold child process on every agent turn. Together, these impose hundreds of milliseconds of unnecessary dependency bloat and Python startup latency on every hook invocation.
- **Proposed Solution**: Move `google-auth` and `google-auth-oauthlib` into an optional `[project.optional-dependencies] legacy-jwt` extra with an actionable error message if legacy login is attempted without it, and refactor `review_and_continue.py` and `codex_notify.py` to invoke `hitl_cli.sdk.HITL` directly in-process instead of spawning a subprocess. Defer heavy imports (`fastmcp`, `pynacl`) inside `main.py` to the commands that use them so short-lived commands launch in under 50ms.
- **Business Value**: Cuts turn-hook latency and shrinks package install size and supply-chain exposure for every PyPI and `uvx` user.
- **Effort Estimate**: S

---

## IDEA-660: Event-Driven Transcript Stabilization Watcher in `review_and_continue` Hook
- **Category**: Performance
- **Problem**: `hitl_cli/hooks/review_and_continue.py` starts every execution with an unconditional `time.sleep(0.5)` and polls up to six times at 0.5-second intervals waiting for the JSONL transcript line count to stabilize. This blind polling adds 1.5 to 3.5 seconds of dead wait time to every Claude Code or Antigravity stop event.
- **Proposed Solution**: Replace the fixed sleep-and-poll loop with an OS-adaptive filesystem watcher (`inotify` on Linux via `ctypes`, `kqueue` on macOS, and a tight `st_mtime_ns` fallback) paired with a trailing-newline JSONL parse check on the final line. As soon as the assistant entry flushes cleanly to disk, the hook extracts the message and proceeds immediately in under 50ms.
- **Business Value**: Makes interactive stop-hook reviews feel instantaneous and removes wasted idle latency across thousands of daily autonomous agent turns.
- **Effort Estimate**: S

---

## IDEA-661: Stdout Wire-Framing Shield for MCP Stdio Proxy (`sys.stdout` Isolation)
- **Category**: Security
- **Problem**: During `hitl-cli proxy` stdio sessions, shared modules (`api_client.py`, `auth.py`, `crypto.py`) and third-party libraries occasionally call `typer.echo()`, `print()`, or default loggers that write directly to `stdout`. Any non-JSON-RPC bytes emitted on `stdout` corrupt the MCP stdio framing and cause Claude Desktop, Cursor, or Antigravity to drop the proxy connection silently.
- **Proposed Solution**: At `proxy` startup in `proxy_handler_v2.py`, duplicate the raw `stdout` file descriptor exclusively for FastMCP's stdio writer and rebind `sys.stdout`, `typer.echo`, and root logging handlers to `sys.stderr` (or the proxy log stream). Add an automated regression test asserting that `print()` or `typer.echo()` calls inside client helpers cannot pollute the MCP wire stream.
- **Business Value**: Prevents hard-to-diagnose MCP proxy disconnects in desktop IDEs, improving session reliability and developer retention.
- **Effort Estimate**: S

---

## IDEA-662: Native MCP `elicitation/create` Bridge in `hitl-cli proxy`
- **Category**: Integration
- **Problem**: Newer Model Context Protocol servers and IDE clients increasingly use MCP's native `elicitation/create` request capability for structured mid-tool user confirmation, yet `hitl-cli proxy` only relays HITL-specific tools (`request_human_input`) and cannot route standard MCP elicitation prompts to the user's mobile device.
- **Proposed Solution**: Register an MCP client-capability handler in `proxy_handler_v2.py` that advertises `elicitation` support to upstream MCP servers, intercepts incoming `elicitation/create` JSON-Schema requests, translates their prompt message and schema fields into E2EE mobile HITL prompts via `crypto.py`, and returns standard `accept`, `decline`, or `cancel` responses upstream.
- **Business Value**: Turns `hitl-cli` into a universal mobile human-gate for the entire MCP server ecosystem without requiring upstream servers to adopt a custom HITL SDK.
- **Effort Estimate**: M

---

## IDEA-663: Out-of-Band E2EE Key Fingerprint & Short Authentication String (`hitl-cli key verify`)
- **Category**: Security
- **Problem**: `hitl_cli/crypto.py` fetches mobile device public keys from the backend relay (`get_device_public_keys()`) using pure Trust-On-First-Use (TOFU), leaving users with no mechanism to detect whether a compromised relay substituted a rogue public key during device registration.
- **Proposed Solution**: Add a `hitl-cli key verify` command that computes a deterministic SHA-256 Short Authentication String (SAS)—formatted as both a 6-digit numeric code and a 4-emoji sequence—over the canonical sorted pair of the local agent X25519 public key and each registered mobile device key. Users can visually compare the SAS against the matching fingerprint screen in `hitl-app` and mark trusted keys as verified in local config.
- **Business Value**: Closes the MITM key-substitution gap in E2EE mode and strengthens enterprise zero-trust security assurances.
- **Effort Estimate**: S

---

## IDEA-664: MCP Streamable HTTP Sidecar Transport in `hitl-cli proxy` (`--transport streamable-http`)
- **Category**: Integration
- **Problem**: `hitl-cli proxy` currently exposes only a local stdio FastMCP server, making it awkward to deploy `hitl-cli` as an E2EE sidecar container in Kubernetes pods, Docker Compose stacks, or remote devboxes where agent runners connect over HTTP rather than spawning local subprocesses.
- **Proposed Solution**: Extend `hitl-cli proxy` in `proxy_handler_v2.py` with `--transport streamable-http --host 127.0.0.1 --port 8765`, enforcing a local bearer token whenever bound to non-loopback interfaces. Containerized agents connect to the sidecar over MCP Streamable HTTP while `hitl-cli` transparently handles OAuth token refresh and PyNaCl E2EE encryption toward `hitlrelay.app`.
- **Business Value**: Unlocks containerized and cloud-hosted agent architectures where stdio child-process spawning across container boundaries is impractical.
- **Effort Estimate**: M

---

## IDEA-665: Mid-Session OAuth 401 Silent Refresh & Persistent Session Reuse in `BackendMCPClient`
- **Category**: Performance
- **Problem**: `BackendMCPClient` in `proxy_handler_v2.py` opens a brand-new `fastmcp.Client` connection for every `list_tools()` and `call_tool()` invocation and reads `get_current_oauth_token()` without triggering an OAuth refresh on expiry or HTTP 401. As a result, every tool call pays full TLS and MCP initialization latency, and multi-hour IDE proxy sessions fail once the short-lived access token expires.
- **Proposed Solution**: Maintain a persistent, health-checked `fastmcp.Client` session inside `BackendMCPClient` with an asyncio lock guarding reconnects, and catch HTTP 401 / auth failures to invoke `OAuthDynamicClient` token refresh and transparently replay the tool call once. Expose connection reuse metrics in debug logs so multi-hour IDE sessions stay uninterrupted.
- **Business Value**: Eliminates mid-session proxy dropouts during long coding marathons and cuts per-tool-call proxy overhead.
- **Effort Estimate**: S

---

## IDEA-666: Synthetic Hook Payload Simulator & Dry-Run Verifier (`hitl-cli hook test`)
- **Category**: UX
- **Problem**: Developers configuring `hitl-hook-review-and-continue` or `hitl-codex-notify` inside `~/.claude/settings.json`, Antigravity hooks, or `~/.codex/config.toml` frequently misconfigure paths, environment variables, or transcript formats, only discovering silent failures hours later when an autonomous run finishes without notifying their phone.
- **Proposed Solution**: Implement a `hitl-cli hook test` subcommand supporting `--target claude|codex|antigravity` and `--dry-run`. The command synthesizes realistic JSON/JSONL fixture payloads (including Antigravity `fullyIdle` states), executes the registered hook pipeline end-to-end, and prints extracted message previews, latency breakdown, and actionable remediation hints for any error.
- **Business Value**: Reduces hook onboarding and troubleshooting time from hours to seconds and prevents silent missed notifications in production agent setups.
- **Effort Estimate**: S

---

## IDEA-667: MCP `roots/list` Workspace & Git Branch Attribution Forwarding in Proxy Mode
- **Category**: Integration
- **Problem**: MCP clients such as Claude Desktop, Cursor, and Antigravity advertise active project directories via the MCP `roots/list` protocol, yet `hitl-cli proxy` ignores these roots, forcing mobile reviewers juggling multiple concurrent repositories to guess which workspace and branch originated an incoming prompt.
- **Proposed Solution**: Query or track MCP client `roots/list` notifications inside `proxy_handler_v2.py`, resolve each workspace root's repository basename and current git branch (without reading file contents), and attach a compact `workspace` attribution badge to outbound E2EE tool metadata. Include a `--no-roots` opt-out flag for privacy-restricted environments.
- **Business Value**: Gives human reviewers immediate workspace context on mobile approval cards, preventing accidental approvals in the wrong repository or branch.
- **Effort Estimate**: S

---

## IDEA-668: Dead Code & Inline `MockResponse` Stub Removal in `api_client.py`
- **Category**: Tech Debt
- **Problem**: `hitl_cli/api_client.py` currently embeds test scaffolding directly inside production code (`post_sync()` returns a hardcoded `class MockResponse` stub instead of issuing an HTTP request) and mixes synchronous test helpers with the live async `ApiClient`, creating a dangerous footgun if invoked by external SDK consumers.
- **Proposed Solution**: Remove the inline `MockResponse` stub from `hitl_cli/api_client.py`, relocate all HTTP test doubles into `tests/conftest.py`, and replace `get_sync`/`post_sync` with a clean, properly implemented `httpx.Client`-backed synchronous helper (or explicit deprecation notice) tested against real `httpx.MockTransport`.
- **Business Value**: Eliminates a silent correctness hazard where calling `post_sync` fakes HTTP success without contacting the relay, improving SDK trustworthiness.
- **Effort Estimate**: S

---

## IDEA-669: Git Commit & Markdown Release Checklist Gate (`hitl-cli request --from-commit`)
- **Category**: Feature
- **Problem**: Engineers using `hitl-cli` in release scripts or local pre-push hooks frequently need a human to sign off on a specific git commit, tag, or `RELEASE_CHECKLIST.md`, forcing them to cobble together custom shell scripts that format `git show` summaries and checklist items manually.
- **Proposed Solution**: Add `--from-commit <ref>` and `--checklist <path>` flags to `hitl-cli request`. The CLI extracts commit metadata (hash, author, subject, `--stat` file summary) and parses unchecked Markdown `- [ ]` items into a structured mobile review prompt with pre-populated `Approve`, `Request Changes`, and `Hold` choices, returning a clean exit status based on the verdict.
- **Business Value**: Delivers a zero-boilerplate release and pre-push approval gate for solo builders and engineering teams.
- **Effort Estimate**: S

---

## IDEA-670: Markdown-Safe Transcript Budgeter & Code-Fence Preserving Truncation in Agent Hooks
- **Category**: UX
- **Problem**: `hitl_cli/hooks/review_and_continue.py` extracts the last three assistant messages verbatim and `hitl_cli/hooks/codex_notify.py` passes full `last-assistant-message` strings straight to `hitl-cli notify`. Long agent responses with large stack traces or code blocks overflow mobile push limits, hit OS `ARG_MAX` limits on `subprocess.run`, or break Markdown rendering when sliced mid-fence.
- **Proposed Solution**: Introduce a shared `format_hook_excerpt(text, max_chars)` helper in `hitl_cli/hooks/` that preserves the opening task header and final conclusion while middle-eliding oversized blocks, automatically closing any unclosed triple-backtick Markdown fences and switching hook dispatch to pass payloads via SDK/stdin rather than CLI arguments.
- **Business Value**: Ensures mobile review cards remain crisp, readable, and crash-free even after verbose multi-file coding turns.
- **Effort Estimate**: S

---

## IDEA-671: Automated PyPI & Nix Flake Version/Dependency Parity Gate in CI
- **Category**: Tech Debt
- **Problem**: As reflected in `CHANGELOG.md` (`v1.2.1` version mismatch) and `.specs/knowledge/hitl-cli-architecture.md` (`ruff` missing from `pyproject.toml` / Nix vs `uv` drift), `pyproject.toml`, `uv.lock`, and `flake.nix` can silently drift across PRs, causing `nix develop` environments and PyPI builds to behave differently.
- **Proposed Solution**: Add a lightweight parity check script and GitHub Actions CI step that parses `pyproject.toml` and `flake.nix` to verify identical package versions, checks that all runtime/dev dependencies (including `ruff`) are declared consistently across both manifests, and runs `uv lock --check` alongside `nix flake check` where available.
- **Business Value**: Prevents broken PyPI releases and eliminates "works in Nix, fails in `uv`" surprises for contributors and autonomous workers.
- **Effort Estimate**: S

---

## IDEA-672: Multi-Repo `hitl-daily-report` Portfolio Aggregator with Stale-PR Alerts
- **Category**: Feature
- **Problem**: `hitl_cli/main.py`'s `daily-report` (`hitl-daily-report`) command currently queries only a single `--repo` (`slaser79/hitl-cli`) via sequential `gh` CLI calls and omits visibility into stale open pull requests or failing CI checks waiting on human review.
- **Proposed Solution**: Extend `daily-report` to accept repeatable `--repo` flags or a `~/.config/hitl-cli/repos.toml` portfolio manifest, execute `gh` queries concurrently using `asyncio.gather`, flag open PRs older than 48 hours or with failing status checks under a dedicated `Needs Attention` section, and support `--format markdown|json` output for automated downstream digests.
- **Business Value**: Gives engineering leads and Chief-of-Staff workflows a single consolidated morning status digest across an entire repository portfolio.
- **Effort Estimate**: S
