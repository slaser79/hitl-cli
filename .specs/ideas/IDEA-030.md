# Ideas Batch — hitl-cli (Batch 36)

## IDEA-523: Visual Attachment Support for UI & Artifact Approval (`hitl-cli request --image`)
- **Category**: Feature
- **Problem**: Autonomous coding agents frequently generate visual outputs such as web UI screenshots, render diffs, and charts that cannot be evaluated effectively through text-only prompts.
- **Proposed Solution**: Add `--image <path>` to `hitl-cli request` (and `image_path` parameter to the Python SDK `HITL.request_input()`) that performs client-side format validation (PNG, JPEG, WebP) and thumbnail compression, sending the payload as an encrypted attachment or base64 data URI to the relay. The mobile app renders the visual artifact inline above the choice buttons with full-screen zoom and inspection tools, while the CLI displays an in-terminal image preview using Kitty/iTerm2 protocols or an ASCII placeholder.
- **Business Value**: Expands HITL into front-end design, data visualization, and QA automation workflows where visual verification is required for task sign-off.
- **Effort Estimate**: M

---

## IDEA-524: Directory-Scoped `.hitl.toml` Workspace Configuration Discovery
- **Category**: Feature
- **Problem**: `hitl-cli` currently only reads configuration from global directories (`~/.config/hitl-cli/`) or global environment variables, causing friction and errors when developers work across repositories with different relay endpoints, timeouts, or project tags.
- **Proposed Solution**: Update `config.py` to traverse parent directories starting from the current working directory to discover `.hitl.toml` or `.hitl/config.toml` files, applying local settings with higher precedence than global defaults. Local project configs can define default prompts, escalation tags, custom timeouts, and relay URLs while maintaining security boundaries by prohibiting local secret token definitions without explicit opt-in.
- **Business Value**: Simplifies multi-repository and enterprise developer workflows while preventing misrouted notifications across project boundaries.
- **Effort Estimate**: S

---

## IDEA-525: Native Headless CI Simulation & Auto-Mock Mode (`HITL_SIMULATION_MODE`)
- **Category**: Integration
- **Problem**: Automated test suites and CI/CD pipelines executing agent code that calls `hitl-cli` block indefinitely until timeout because no mobile reviewer is present in headless test environments.
- **Proposed Solution**: Introduce a simulation engine activated via `--simulate <choice>` or the `HITL_SIMULATION_MODE=approve|reject|canned:<path>` environment variable. When active, `ApiClient` and SDK methods bypass network relay calls, log an explicit warning to stderr, and immediately return predefined mock answers and simulated timestamps.
- **Business Value**: Enables seamless end-to-end testing of agent workflows in automated CI/CD pipelines without blocking or requiring live human intervention.
- **Effort Estimate**: S

---

## IDEA-526: Automated Terminal Shell Completion for Bash, Zsh, and Fish (`hitl-cli completion`)
- **Category**: UX
- **Problem**: Terminal users and script authors frequently look up flag names, subcommands, and choice arguments manually because `hitl-cli` lacks out-of-the-box shell tab completion.
- **Proposed Solution**: Add a `hitl-cli completion` subcommand (`install` and `show [bash|zsh|fish|powershell]`) leveraging Typer's built-in shell completion engine. Provide dynamic completion callbacks for active auth profiles, local attachment paths, and common command options.
- **Business Value**: Accelerates developer adoption and reduces syntax errors for terminal-first developers using the CLI directly.
- **Effort Estimate**: S

---

## IDEA-527: Native Desktop & OSC 777/9 In-Terminal OS Notification Dispatch
- **Category**: UX
- **Problem**: Developers multitasking in other windows while waiting for an agent approval prompt frequently miss incoming requests or responses, causing unnecessary idle delays.
- **Proposed Solution**: Add terminal escape sequence triggers (OSC 777 and OSC 9) supported by modern terminal emulators (iTerm2, WezTerm, Ghostty, Alacritty) alongside OS desktop notification fallbacks (`notify-send` on Linux, `osascript` on macOS). When an agent initiates a blocking prompt or a mobile response resolves, `hitl-cli` fires an unobtrusive desktop notification with sound chime.
- **Business Value**: Recovers developer attention immediately when action is required, eliminating friction and wait time during local agent supervision.
- **Effort Estimate**: S

---

## IDEA-528: Relay HTTP Transient Error Auto-Retry with Truncated Exponential Backoff
- **Category**: Performance
- **Problem**: Temporary relay restarts, gateway 502/503/504 errors, or dropped socket connections instantly crash the CLI, aborting long-running autonomous agent sessions.
- **Proposed Solution**: Implement a robust HTTP transport retry middleware in `ApiClient` using `httpx.HTTPTransport(retries=...)` or an asynchronous retry decorator targeting transient HTTP status codes (408, 429, 502, 503, 504) and connection resets. The retry loop applies truncated exponential backoff with full jitter and emits subtle diagnostic logs to stderr without corrupting stdout JSON outputs.
- **Business Value**: Protects long-running agent workflows from transient network and server blips, reducing workflow abort rates.
- **Effort Estimate**: S

---

## IDEA-529: Automated Key Rotation and Rekeying Command (`hitl-cli key rotate`)
- **Category**: Security
- **Problem**: E2EE Curve25519 keypairs stored in `~/.config/hitl-cli/` remain static indefinitely after initial setup, failing enterprise cryptographic hygiene and key retirement standards.
- **Proposed Solution**: Implement `hitl-cli key rotate` which generates a new keypair, cryptographically signs a rekeying attestation with the existing private key, publishes the public key update to the relay server, and atomically replaces local key files. In-flight requests include key epoch markers to allow seamless decryption during key migration periods.
- **Business Value**: Meets SOC2, ISO-27001, and corporate security requirements for regular cryptographic key rotation without requiring full account re-authentication.
- **Effort Estimate**: M

---

## IDEA-530: Subagent Lineage and Task Hierarchy Tracking in Prompts (`--parent-task-id`)
- **Category**: Feature
- **Problem**: Multi-agent workflows (like Antigravity or OpenHands) spawn hierarchical subagents whose questions appear flat and disconnected on the mobile app, leaving human reviewers without necessary context.
- **Proposed Solution**: Extend request payloads and CLI options with `--parent-task-id`, `--subagent-role`, and `--task-name`, automatically discovering them from standard environment variables (`AGENT_TASK_ID`, `PARENT_TASK_ID`). The mobile app displays breadcrumb lineage headers (e.g., `Parent Mission > Security Scanner > Subagent #3`), allowing the reviewer to immediately identify who is asking and why.
- **Business Value**: Eliminates reviewer confusion in multi-agent fleet deployments, preventing mistaken approvals caused by missing context.
- **Effort Estimate**: M

---

## IDEA-531: Rolling Hook Telemetry and Audit Log File (`~/.hitl/hooks.log`)
- **Category**: Tech Debt
- **Problem**: Hook scripts (`review_and_continue.py`, `codex_notify.py`) currently drop subprocess stdout/stderr upon failure and provide no persistent execution logs, making hook failures difficult to diagnose (Issue #70).
- **Proposed Solution**: Create a dedicated hook logging module in `hitl_cli.hooks.logger` that appends structured JSONL events to `~/.hitl/hooks.log` with automatic file rotation (max 5MB, 3 rotations). Each log entry records timestamp, calling agent harness (Claude Code or Antigravity), command arguments, duration, exit code, and full captured stderr upon failure.
- **Business Value**: Cuts triage and debugging time for broken hook integrations from hours to seconds, enhancing fleet operational visibility.
- **Effort Estimate**: S

---

## IDEA-532: Zero-Leak Memory Scrubbing and Key Scrambling on Process Exit
- **Category**: Security
- **Problem**: Decrypted private keys, bearer tokens, and confidential prompt payloads linger in Python process memory and can be extracted from core dumps, swap files, or memory inspection tools.
- **Proposed Solution**: Integrate `sodium_memzero` via PyNaCl or `ctypes.memset` to explicitly zero out bytearrays holding private keys and decrypted secrets immediately after use and upon process termination via `atexit`. Enable `PR_SET_DUMPABLE=0` on supported Linux systems to prevent ptrace memory attachment by unauthorized local processes.
- **Business Value**: Hardens the CLI against memory-scraping attacks in shared, multi-tenant developer environments and secure corporate laptops.
- **Effort Estimate**: S

---

## IDEA-533: Bidirectional WebSocket Streaming Transport for Real-Time Human Response
- **Category**: Performance
- **Problem**: The CLI and Python SDK poll the relay server via repeated HTTP GET requests, introducing 1-3 seconds of artificial polling delay before an agent detects that a human has responded.
- **Proposed Solution**: Implement an optional WebSocket transport layer in `ApiClient` and `mcp_client.py` that establishes a persistent streaming socket connection (`wss://hitlrelay.app/ws/requests/{id}`) for active prompts. Mobile response events are pushed instantly down the socket with sub-50ms latency, automatically falling back to HTTP polling if WebSocket handshakes are blocked by network proxies.
- **Business Value**: Eliminates human approval latency in agent loops and decreases relay server HTTP request volume by over 80%.
- **Effort Estimate**: M

---

## IDEA-534: Exportable Audit Ledger and Compliance Log (`hitl-cli audit export`)
- **Category**: Integration
- **Problem**: Regulated enterprises require complete, verifiable records of every autonomous agent action approved or rejected by human operators for compliance audits.
- **Proposed Solution**: Add an append-only local SQLite/JSONL audit ledger in `hitl_cli` that records every prompt, timestamp, responding user ID, decision latency, and cryptographic signature. Provide `hitl-cli audit export --format [json|csv|html] --since <date>` to produce standardized audit reports ready for compliance and security review.
- **Business Value**: Satisfies enterprise governance, compliance, and legal audit requirements, unblocking enterprise procurement of the HITL platform.
- **Effort Estimate**: M

---

## IDEA-535: Dynamic Markdown & Syntax-Highlighted Terminal Confirmation Diff
- **Category**: UX
- **Problem**: When agents prompt the user in terminal interactive mode with multi-line code diffs or structured text, raw uncolored output makes it difficult to quickly spot subtle code changes.
- **Proposed Solution**: Use `rich.syntax.Syntax` and `rich.markdown.Markdown` to render syntax-highlighted diffs, colored Markdown formatting, and formatted choice boxes inside terminal confirmation prompts. The formatter detects TTY capabilities and gracefully downgrades to clean plain text when running in non-interactive pipes or CI logs.
- **Business Value**: Reduces human cognitive fatigue and error rates when reviewing code changes directly in terminal sessions.
- **Effort Estimate**: S

---

## IDEA-536: Unified CLI Diagnostics and Environment Doctor (`hitl-cli doctor`)
- **Category**: UX
- **Problem**: When users experience network issues, expired tokens, missing keys, or misconfigured hooks, troubleshooting requires checking multiple files and guessing error causes.
- **Proposed Solution**: Implement `hitl-cli doctor` to run an automated diagnostic suite checking Python version, config file existence, token expiry, relay connectivity and latency, E2EE key integrity, and hook execution permissions. The command prints an ANSI status report with clear checkmarks and actionable remediation suggestions for any failed checks.
- **Business Value**: Reduces customer support requests by enabling developers to diagnose and fix configuration and network issues self-serve in seconds.
- **Effort Estimate**: S

---

## IDEA-537: Antigravity Background Task Readiness Guard in Stop Hook
- **Category**: Tech Debt
- **Problem**: The `review_and_continue` stop hook prompts for mobile review immediately when an agent stop event occurs, even when long-running background tasks or child jobs are still running (Issue #75).
- **Proposed Solution**: Update `hitl_cli/hooks/review_and_continue.py` to inspect the Antigravity `fullyIdle` property in `sys.stdin` and check for active background subagents. If the agent is not fully idle, the hook outputs `{"decision": "block", "reason": "Background tasks still running"}` and exits 0, suppressing premature mobile notifications until all background execution is complete.
- **Business Value**: Eliminates false mobile notification spam, ensuring humans are only alerted when all background tasks are complete and verified.
- **Effort Estimate**: S
