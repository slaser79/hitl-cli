# Ideas Batch — hitl-cli (Batch 568)

## IDEA-568: Human-Delegated Subagent Handoff & Collaborative Session Escalation (`hitl-cli request --delegate-to-human`)
- **Category**: Feature
- **Problem**: When an autonomous agent encounters an unsolvable problem, high ambiguity, or an operational deadlock, it either crashes or enters an unproductive retry loop with no clean mechanism to yield interactive terminal control to a human.
- **Proposed Solution**: Introduce `--delegate-to-human` and SDK `yield_terminal()` support in `hitl-cli request`. When triggered, the CLI pauses the agent runner, dispatches an interactive takeover invitation to the reviewer's mobile app, establishes a secure terminal stream bridge, and cleanly resumes agent execution once the human operator signals completion.
- **Business Value**: Eliminates catastrophic workflow terminations when agents encounter edge-case blockers, boosting autonomous task completion rates and client retention.
- **Effort Estimate**: M

---

## IDEA-569: Rich Terminal Markdown Diff Viewer with Interactive Side-by-Side Split (`hitl-cli request --diff-view side-by-side`)
- **Category**: UX
- **Problem**: Code patches and configuration diffs displayed during terminal confirmations wrap awkwardly on narrow displays or output dense unified diff text that is difficult to review before approving critical actions.
- **Proposed Solution**: Integrate a syntax-highlighted terminal split-pane diff viewer powered by Rich (`--diff-view side-by-side|unified`) that displays line numbers, inline character-level highlights, and collapsible unchanged context. The prompt view supports interactive scrolling and can automatically pipe large diffs into the user's configured terminal pager (such as `delta` or `less`).
- **Business Value**: Accelerates code review speed and prevents costly human approval errors on complex pull requests and refactoring tasks.
- **Effort Estimate**: S

---

## IDEA-570: HTTP/2 Multiplexing & Connection Keep-Alive with Pipelined Polling in `ApiClient`
- **Category**: Performance
- **Problem**: Repetitive short-lived HTTP/1.1 connections during rapid polling cycles and status checks introduce latency spikes from repeated TCP handshakes and TLS renegotiation.
- **Proposed Solution**: Upgrade `httpx.AsyncClient` in `api_client.py` to enable HTTP/2 protocol multiplexing (`http2=True`) with persistent connection pooling and aggressive TCP keep-alive keepalives. Active sessions share persistent network sockets across sequential requests and long-polling relay loops, minimizing round-trip overhead.
- **Business Value**: Slashes network latency by up to 45% and reduces connection load on the HITL relay infrastructure, delivering a snappier user experience.
- **Effort Estimate**: S

---

## IDEA-571: Automated Ephemeral Credential Redaction & In-Flight Payload Sanitization Filter (`hitl-cli --redact-sensitive`)
- **Category**: Security
- **Problem**: Autonomous agents inadvertently include private keys, AWS tokens, database credentials, or secret environment variables in prompt payloads and error logs transmitted to the mobile relay.
- **Proposed Solution**: Implement a client-side regex and entropy-based sanitization engine into `ApiClient` and `mcp_client.py`. Matching sensitive patterns (such as bearer tokens, private keys, and API secrets) are substituted with deterministic masking tokens (`[REDACTED:token_...a4f1]`) before encryption and dispatch, maintaining an ephemeral local lookup table for terminal output reconstruction.
- **Business Value**: Mitigates severe data leakage and compliance violation risks by guaranteeing that proprietary credentials never leave the developer's workstation.
- **Effort Estimate**: M

---

## IDEA-572: Unify Asynchronous Command Runner & Decouple CLI Typer Sync Bridges
- **Category**: Tech Debt
- **Problem**: CLI commands in `main.py` individually instantiate and manage `asyncio.run()` loops, leading to repetitive boilerplate, inconsistent `SIGINT` interrupt handling, and fragmented client teardown.
- **Proposed Solution**: Implement a centralized `@async_command` runner decorator for Typer commands that provides structured event loop lifecycle management, unified signal handling for cancellation, and standardized exception translation. All asynchronous API calls and MCP proxy routines execute under this single lifecycle manager.
- **Business Value**: Eliminates hundreds of lines of brittle boilerplate code and hardens CLI reliability across operating system platforms.
- **Effort Estimate**: S

---

## IDEA-573: Native OpenTelemetry Tracing & Distributed Context Propagation (`--otel-trace-parent`)
- **Category**: Integration
- **Problem**: In enterprise microservices and multi-agent orchestrations, human-in-the-loop steps appear as disconnected blind spots in APM tools such as Datadog, Jaeger, and Honeycomb.
- **Proposed Solution**: Add W3C Trace Context (`traceparent`, `tracestate`) header injection and extraction across `hitl-cli request`, `notify`, and the Python SDK. Spans are automatically emitted for request dispatch, mobile notification delivery, human reviewer response delay, and decision recording, linking the human review directly into the parent distributed trace.
- **Business Value**: Gives enterprise engineering teams end-to-end visibility into human decision latency across complex autonomous pipelines, identifying operational bottlenecks.
- **Effort Estimate**: M

---

## IDEA-574: Multi-Tier Escalation Policy with Automatic Reviewer Reassignment (`hitl-cli request --escalate-after`)
- **Category**: Feature
- **Problem**: When a designated human reviewer is away from their device, urgent autonomous deployment gates or security prompts stall indefinitely until timeout expiration.
- **Proposed Solution**: Add `--escalate-after <duration>` and `--escalate-to <recipient/team>` options to `hitl-cli request`. If the primary reviewer does not acknowledge or resolve the prompt within the specified duration, the relay re-routes the pending prompt to a fallback team queue or secondary on-call engineer without terminating the agent workflow.
- **Business Value**: Eliminates critical pipeline stalls and prevents expensive agent downtime caused by single-point-of-failure reviewer unavailability.
- **Effort Estimate**: M

---

## IDEA-575: Zero-Install Shell Wrapper & Portable Binary Distribution via PyInstaller/Shiv
- **Category**: UX
- **Problem**: Executing `hitl-cli` in minimal Docker containers, CI build environments, or locked-down corporate developer machines often requires installing Python 3.12, UV, and virtual environments.
- **Proposed Solution**: Build and distribute self-contained, statically linked standalone executables for Linux (x86_64, aarch64) and macOS (Apple Silicon, Intel) using PyInstaller or Shiv via GitHub Releases. A simple `curl -fsSL https://hitlrelay.app/install.sh | sh` installer script places the precompiled binary directly into the user's path without external Python dependencies.
- **Business Value**: Drastically lowers barrier to entry and setup friction for enterprise CI/CD pipelines, driving wider adoption among non-Python developer ecosystems.
- **Effort Estimate**: M

---

## IDEA-576: Cryptographic Request Integrity Checksum & Tamper-Proof Payload Digest
- **Category**: Security
- **Problem**: In relay hops and transit environments where end-to-end encryption is not enabled, there is no cryptographic guarantee that prompt payloads or reviewer responses have not been intercepted and modified.
- **Proposed Solution**: Implement HMAC-SHA256 payload integrity signing in `api_client.py` using a local device signing secret or shared session key. The sender attaches an `X-HITL-Signature` header computed over the timestamp and raw JSON payload body, allowing both client and relay to reject tampered or replayed payloads immediately.
- **Business Value**: Ensures non-repudiation and tamper resistance for critical infrastructure approvals, fulfilling stringent SOC2 and ISO 27001 data integrity audits.
- **Effort Estimate**: S

---

## IDEA-577: Audio Voice-Prompt Synthesis & Speech-to-Text Transcription Bridge
- **Category**: Feature
- **Problem**: Reviewers on the move or in transit cannot easily read dense technical diffs or type lengthy responses on small mobile keyboards.
- **Proposed Solution**: Add `--audio` support to `hitl-cli request` that generates a concise text-to-speech audio brief for the mobile client and enables voice dictation. The mobile app captures the reviewer's spoken instructions, performs on-device transcription via Whisper, and returns the structured text response back to the waiting CLI agent.
- **Business Value**: Enables effortless hands-free approvals and reviews for mobile engineers, cutting response turnaround times and boosting user satisfaction.
- **Effort Estimate**: L

---

## IDEA-578: Fast Memory-Mapped IPC Cache for Local Multi-Process Agent Worktrees
- **Category**: Performance
- **Problem**: Concurrent agent swarms running in parallel worktrees on the same workstation repeatedly read OAuth tokens, registration credentials, and relay metadata from disk, causing filesystem lock contention and disk I/O churn.
- **Proposed Solution**: Implement a POSIX shared-memory (`shm_open`) or memory-mapped file cache (`mmap`) in `config.py` for local token validation and cached relay session state. A lightweight shared reader-writer lock ensures atomic reads and instant memory invalidation whenever tokens refresh.
- **Business Value**: Reduces process initialization and auth validation latency by 80% on high-density multi-agent developer workstations.
- **Effort Estimate**: S

---

## IDEA-579: Comprehensive CLI Command Snapshot & Regression Testing Suite
- **Category**: Tech Debt
- **Problem**: Visual formatting of CLI output, ANSI styling, and terminal table layouts can silently regress across dependency upgrades or Typer releases without triggering standard unit test assertions.
- **Proposed Solution**: Integrate `syrupy` or `pytest-regressions` snapshot testing across all CLI command modules (`hitl-cli --help`, `status`, `request`, `notify`). Test fixtures capture normalized terminal output, styling tags, and error outputs, asserting exact character-level regression parity in CI.
- **Business Value**: Prevents UI formatting regressions and broken shell output from reaching end users, safeguarding developer experience quality.
- **Effort Estimate**: S

---

## IDEA-580: Native JetBrains IDE & VS Code Extension Companion Protocol (`hitl-cli ide-bridge`)
- **Category**: Integration
- **Problem**: Developers actively coding inside IDEs must constantly switch contexts to a mobile app or browser tab to review and approve actions requested by local AI coding assistants.
- **Proposed Solution**: Introduce a local WebSocket/IPC bridge (`hitl-cli ide-bridge`) that communicates directly with VS Code and JetBrains extension companions. When an agent dispatches a request, an in-editor modal appears with syntax-highlighted diffs, one-click approve/reject actions, and quick-reply feedback fields.
- **Business Value**: Keeps developers in their primary coding flow state, reducing human-in-the-loop review latency from minutes to seconds.
- **Effort Estimate**: M

---

## IDEA-581: Role-Based Access Control (RBAC) & Scoped API Token Delegation (`hitl-cli token mint --scope`)
- **Category**: Security
- **Problem**: Service accounts currently rely on monolithic API keys with global permissions, meaning a compromised CI key can approve arbitrary actions or impersonate any agent.
- **Proposed Solution**: Add a scoped credential minting command (`hitl-cli token mint --role "readonly|approver|notifier" --expires-in 24h --allowed-environments "staging"`). The CLI issues cryptographically signed, short-lived macaroon tokens that enforce least-privilege constraints on allowed commands and environments.
- **Business Value**: Enforces defense-in-depth and the principle of least privilege, preventing catastrophic security breaches from compromised CI/CD secrets.
- **Effort Estimate**: M

---

## IDEA-582: Interactive Terminal Debug Replay & Mock Response Simulator (`hitl-cli replay`)
- **Category**: UX
- **Problem**: Testing agent recovery flows, rejection branches, and complex error handling requires developers to manually trigger and respond to prompts on physical mobile devices during every test iteration.
- **Proposed Solution**: Implement `hitl-cli replay <audit_log.json>` and an interactive mock simulator (`hitl-cli mock --respond "Approved" --delay 2s`). Developers can record real human interaction sessions and replay them deterministically in local dev or integration tests without interacting with mobile devices or cloud relays.
- **Business Value**: Accelerates developer debugging and agent test iteration cycles by 10x, drastically shortening time-to-market for new HITL agent workflows.
- **Effort Estimate**: S
