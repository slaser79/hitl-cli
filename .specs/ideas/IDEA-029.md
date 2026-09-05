# Ideas Batch — hitl-cli (Batch 35)

## IDEA-508: Interactive Terminal Multi-Select Checklist (`hitl-cli select --multi`)
- **Category**: Feature
- **Problem**: Autonomous agents often propose a set of optional tasks, test suites, or files to modify, but current CLI interactions only permit single-choice selection or plain free text.
- **Proposed Solution**: Add an interactive multi-select prompt (`hitl-cli select --multi --min 1 --max 5`) and SDK method (`request_selection()`) rendering an in-terminal interactive checkbox list with spacebar selection and Rich UI styling. On the mobile app, the payload renders as multi-toggle action cards returning the array of selected items to the waiting agent.
- **Business Value**: Cuts multi-turn agent coordination overhead and eliminates redundant round-trips by allowing humans to approve subsets of proposed actions in a single prompt.
- **Effort Estimate**: M

---

## IDEA-509: Persistent HTTP Connection Pooling & Session Reuse in `ApiClient`
- **Category**: Performance
- **Problem**: `ApiClient` instantiates a new ephemeral `httpx.AsyncClient` inside every `get()`, `post()`, `put()`, and `delete()` call, paying full TCP and TLS handshaking costs on every poll and notification.
- **Proposed Solution**: Refactor `ApiClient` to maintain a reusable `httpx.AsyncClient` session with HTTP keepalive, connection pooling, and an async context manager (`async with ApiClient() as client:`). Standalone CLI commands borrow from a shared client instance, eliminating per-request socket teardown.
- **Business Value**: Cuts request latency by over 50% and reduces CPU overhead during high-frequency status polling loops.
- **Effort Estimate**: S

---

## IDEA-510: Structured Exception Hierarchy Decoupling from CLI Exit Codes in SDK
- **Category**: Tech Debt
- **Problem**: Internal helper methods in `ApiClient` directly call `typer.Exit(1)` and write to terminal streams, causing unintended process termination when the client is imported into Python SDK workflows.
- **Proposed Solution**: Create a clean exception hierarchy in `hitl_cli.exceptions` (`HITLError`, `AuthenticationError`, `RelayTimeoutError`, `PayloadValidationError`) and update `ApiClient` and `mcp_client.py` to raise typed exceptions. The top-level Typer CLI commands in `main.py` catch these exceptions and map them cleanly to standard CLI exit codes.
- **Business Value**: Makes the Python SDK safe and resilient for enterprise application embedding without risking unexpected process termination.
- **Effort Estimate**: S

---

## IDEA-511: Official Google Antigravity Channel Plugin (`HitlChannelPlugin`)
- **Category**: Integration
- **Problem**: While hitl-cli provides hooks for Claude Code and Codex, Google Antigravity agents currently lack a first-class channel plugin, forcing users to write bespoke shell glue (Issue #74).
- **Proposed Solution**: Implement `HitlChannelPlugin` in `hitl_cli/hooks/antigravity_channel.py` conforming to the Antigravity SDK plugin interface, spawning the `hitl-channel` stdio transport, registering tool definitions (`reply_to_hitl`, `present_choices_to_hitl`), and handling inbound channel notifications. The plugin automatically tears down child processes on session termination.
- **Business Value**: Unlocks native HITL workflows for Google Antigravity developers, cementing hitl-cli as the universal bridge across major AI coding agents.
- **Effort Estimate**: M

---

## IDEA-512: Resilient Stop-Hook Review Preservation on Secondary Lint Failures
- **Category**: Tech Debt
- **Problem**: In `review_and_continue.py`, when a reviewer provides feedback but a subsequent automated lint or formatting hook fails, the human's actual approval decision and comments are discarded (Issues #70, #75).
- **Proposed Solution**: Restructure hook execution into an isolated two-phase workflow where the human review payload is committed to disk immediately upon receipt before secondary hooks run. If a subsequent lint check fails, the hook reports the lint failure while preserving the reviewer's structured notes in the agent feedback loop.
- **Business Value**: Prevents loss of human review decisions, eliminating redundant developer re-reviews and wasted token spend.
- **Effort Estimate**: S

---

## IDEA-513: Real-Time ANSI Terminal Status Dashboard for Blocking Requests (`--watch`)
- **Category**: UX
- **Problem**: When `hitl-cli request` waits for human feedback over long timeouts, developers see only static text or noisy periodic log messages with no visibility into mobile delivery or elapsed time.
- **Proposed Solution**: Introduce an optional `--watch` mode utilizing Rich Live display that renders an in-place updating terminal dashboard displaying elapsed time, timeout progress bar, relay connectivity health, and interactive hotkeys (`c` to cancel, `p` to re-ping reviewer).
- **Business Value**: Enhances developer situational awareness during extended review intervals, preventing premature task cancellations.
- **Effort Estimate**: S

---

## IDEA-514: Client-Side Automated Secret & PII Masking Filter (`--sanitize`)
- **Category**: Security
- **Problem**: Autonomous agents formulating prompt descriptions often inadvertently include raw API keys, bearer tokens, or database connection strings scraped from error traces and diffs into outbound requests.
- **Proposed Solution**: Integrate a client-side regex and entropy-based sanitization filter in `hitl_cli` that scans prompt text, choice labels, and attachments to automatically redact sensitive credentials (AWS, GitHub, OpenAI, private keys) before network transmission. An explicit `--no-sanitize` flag allows overriding when sharing test fixtures is intended.
- **Business Value**: Protects organizations against catastrophic credential leaks and compliance violations caused by over-sharing AI agents.
- **Effort Estimate**: M

---

## IDEA-515: Multi-File Unified Context Diff Bundler with Syntactic Chunk Pruning (`--diff-context`)
- **Category**: Feature
- **Problem**: Passing large raw git diffs spanning dozens of files into HITL requests results in overwhelming mobile screens and truncated notifications.
- **Proposed Solution**: Introduce `--diff-context <git-ref>` to `hitl-cli request`, which analyzes git patches, prunes non-essential context lines, extracts enclosing AST class/function breadcrumbs, and bundles the changes into a structured multi-file payload. Mobile and CLI reviewers can expand individual file cards with change metrics.
- **Business Value**: Accelerates mobile code review turnaround times by presenting concise, context-aware diffs optimized for mobile viewports.
- **Effort Estimate**: M

---

## IDEA-516: Interactive Terminal Prompt Preview & Dry-Run Mode (`hitl-cli request --dry-run`)
- **Category**: UX
- **Problem**: Developers writing automated agent workflows cannot easily verify how their prompts, choice buttons, and markdown styling will render on mobile without sending real push notifications to reviewers.
- **Proposed Solution**: Add `--dry-run` and `--preview` options to `hitl-cli request` and `hitl-cli notify` that validate payload schema constraints, calculate token size, and render an accurate ASCII/Rich simulation of the mobile prompt card in the terminal.
- **Business Value**: Speeds up prompt engineering and test iteration for agent developers while preventing unnecessary mobile alert spam.
- **Effort Estimate**: S

---

## IDEA-517: Cryptographic Nonce & Anti-Replay Guard for Mobile E2EE Approvals
- **Category**: Security
- **Problem**: If an encrypted approval payload from a prior operation is intercepted by a malicious local process, it could theoretically be replayed against the CLI proxy to authorize unauthorized actions.
- **Proposed Solution**: Generate a cryptographically secure 128-bit random nonce and UTC validity timestamp within every outbound request envelope. Upon decrypting the response in `crypto.py`, the CLI verifies that the returned nonce matches the active request and rejects any expired or duplicate tokens.
- **Business Value**: Eliminates replay attack vectors in automated execution loops, ensuring non-repudiation for high-privilege agent actions.
- **Effort Estimate**: S

---

## IDEA-518: Centralized Auth Strategy Factory & Unified Dispatch Engine
- **Category**: Tech Debt
- **Problem**: The four-way authentication dispatch logic (`E2EE` -> `API_KEY` -> `OAUTH` -> `JWT`) is duplicated across 6 distinct entry points in `main.py` and `sdk.py`, causing code bloat and risk of divergent behavior.
- **Proposed Solution**: Extract authentication resolution into a centralized `AuthStrategy` factory in `hitl_cli/auth_strategy.py` that evaluates credentials, tokens, and CLI flags once to construct a unified transport client. All CLI commands and SDK entry points delegate auth dispatch to this factory.
- **Business Value**: Eliminates critical duplicated logic in the authentication boundary, reducing security regressions when modifying auth mechanisms.
- **Effort Estimate**: M

---

## IDEA-519: Slack & Discord Webhook Escalation Gateway (`hitl-cli gateway`)
- **Category**: Integration
- **Problem**: Distributed teams working in Slack or Discord often miss individual mobile push notifications during work hours, blocking automated CI/CD and agent workflows.
- **Proposed Solution**: Provide a background gateway service (`hitl-cli gateway --slack-webhook <url>`) that mirrors pending human prompts into dedicated team channels with interactive action buttons, routing team member approvals back to the active CLI session.
- **Business Value**: Prevents workflow deadlocks by meeting developer teams in their primary communication tool, shortening decision turnaround times.
- **Effort Estimate**: M

---

## IDEA-520: Adaptive Polling with Exponential Jitter & Long-Polling Relay Handshake
- **Category**: Performance
- **Problem**: Both the CLI and Python SDK poll the relay server at a static 1-second interval while awaiting human input, generating heavy relay traffic and battery drain during long review waits.
- **Proposed Solution**: Implement an adaptive polling loop featuring randomized exponential backoff (scaling from 1s to 10s) combined with an HTTP Long-Polling handshake that holds connections open on the relay until an answer arrives or a keepalive timer expires.
- **Business Value**: Cuts relay API traffic by more than 75% during extended human wait times, significantly lowering cloud infrastructure costs.
- **Effort Estimate**: S

---

## IDEA-521: Fuzzy-Search Interactive Terminal History & Audit Log Browser (`hitl-cli history search`)
- **Category**: UX
- **Problem**: Developers managing multi-agent tasks have no simple terminal interface to review earlier decisions, inspect prompt timestamps, or look up previous responses without manually parsing raw JSON files.
- **Proposed Solution**: Build `hitl-cli history search` using an interactive terminal fuzzy-finder (Rich/prompt_toolkit) allowing users to filter past requests by status (`approved`, `rejected`, `timeout`), view prompt diffs, and export interaction transcripts to markdown or JSON.
- **Business Value**: Speeds up debugging and post-incident reviews by giving developers instant visibility into past human-agent interactions.
- **Effort Estimate**: S

---

## IDEA-522: Air-Gapped Local Subnet Relay Daemon for Offline Enclaves (`hitl-cli daemon --offline`)
- **Category**: Feature
- **Problem**: Autonomous agents deployed in air-gapped lab networks, defense environments, or secure enclaves cannot communicate with the public `hitlrelay.app` cloud service.
- **Proposed Solution**: Add an embedded local relay daemon to `hitl-cli` (`hitl-cli daemon --offline --port 8443`) that binds to the local network over TLS and serves the HITL REST and web interface, allowing local mobile devices or browser clients on the same intranet to review and approve prompts without internet connectivity.
- **Business Value**: Opens lucrative enterprise sales in defense, healthcare, and air-gapped environments where outbound cloud relay traffic is strictly prohibited.
- **Effort Estimate**: L
