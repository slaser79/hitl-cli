# Ideas Batch — hitl-cli (Batch 570)

## IDEA-598: Interactive Multi-Step Approval Workflows with Stage Dependencies (`hitl-cli workflow run`)
- **Category**: Feature
- **Problem**: Complex autonomous tasks (such as database migrations, multi-cluster deployments, or security remediations) require staged human reviews at discrete milestones rather than independent, disconnected prompt calls.
- **Proposed Solution**: Introduce a declarative workflow runner (`hitl-cli workflow run <pipeline.yaml>`) supporting ordered stages, branch conditions, and contextual parameter passing between human decisions. Each stage yields structured review data, feeds validated human inputs into subsequent agent execution steps, and executes automated rollback routines if any stage is rejected.
- **Business Value**: Enables autonomous agents to handle multi-million dollar high-stakes deployments safely, expanding HITL's addressable market to complex enterprise DevOps workflows.
- **Effort Estimate**: M

---

## IDEA-599: Terminal Window Title Bar & OSC Escape Live Countdown Indicator (`hitl-cli request --title-status`)
- **Category**: UX
- **Problem**: Developers running autonomous agents in background terminal tabs or tmux panes cannot tell if an agent is executing, blocked waiting on a human response, or completed without switching tabs.
- **Proposed Solution**: Implement OSC 0/2 (`\033]0;...\007`) escape sequences in `hitl-cli request` to dynamically set terminal window and tab titles with live progress (e.g., `[HITL ⏳ 01:24] Waiting for Approval` or `[HITL ✅] Approved`). On resolution, emit an audible and visual terminal bell (`\a`) to alert the developer immediately.
- **Business Value**: Prevents developer context thrashing and reduces turnaround delays by surfacing HITL status directly in IDE and multiplexer tab headers.
- **Effort Estimate**: S

---

## IDEA-600: Adaptive Polling Schedule with Exponential Decay & Server-Sent Conditional State Checks (`ApiClient`)
- **Category**: Performance
- **Problem**: In `api_client.py`, polling for human responses uses a static polling frequency that either floods the server with redundant requests during long idle waits or introduces up to several seconds of latency when a reviewer responds quickly.
- **Proposed Solution**: Implement an adaptive polling schedule in `ApiClient` that polls aggressively (every 250ms) for the first 10 seconds, backs off exponentially to 5s with jitter, and leverages HTTP `Last-Modified` and `ETag` conditional polling headers so the relay can respond with `304 Not Modified` payload-free responses until state changes.
- **Business Value**: Cuts mobile relay request bandwidth and database load by 65% while reducing fast human response pickup latency to sub-second speeds.
- **Effort Estimate**: S

---

## IDEA-601: Time-Locked One-Time Nonces and Replay Attack Prevention in MCP Proxy (`--replay-protection`)
- **Category**: Security
- **Problem**: In FastMCP proxy mode (`proxy_handler_v2.py`), tool call requests forwarded between the agent host and the relay could theoretically be captured and replayed if an attacker intercepts the communication channel, potentially triggering duplicate or unauthorized operations.
- **Proposed Solution**: Implement cryptographically signed, timestamped nonces (using HMAC-SHA256 with microsecond timestamp windows and an in-memory sliding nonce window) on every MCP tool request and response. Requests with expired timestamps or replayed nonces are rejected immediately with an audit security event.
- **Business Value**: Hardens the MCP proxy against replay and man-in-the-middle tampering, securing enterprise agent-to-human control planes.
- **Effort Estimate**: S

---

## IDEA-602: Centralized Asynchronous Context Manager for Safe Resource Teardown & Graceful Signal Cleanup (`HitlContext`)
- **Category**: Tech Debt
- **Problem**: Across `main.py`, `proxy_handler_v2.py`, and hooks, background tasks, open HTTP sessions, and file descriptors are cleaned up ad-hoc, leading to dangling socket warnings or unclosed connection errors (`ResourceWarning: unclosed <ssl.SSLSocket>`) when CLI processes terminate abruptly.
- **Proposed Solution**: Implement a unified asynchronous context manager (`HitlContext`) that registers POSIX signal handlers (SIGINT, SIGTERM, SIGHUP), coordinates orderly cancellation of all pending async tasks, flushes buffered audit telemetry, and ensures clean closure of SSL connections and tempfiles.
- **Business Value**: Eliminates sporadic CLI hang states on shutdown and eliminates unhandled socket leak warnings, improving developer trust and test suite hygiene.
- **Effort Estimate**: S

---

## IDEA-603: Temporal & AWS Step Functions Durable Activity Worker Bridge (`hitl-cli worker temporal`)
- **Category**: Integration
- **Problem**: Enterprise platform teams orchestrating agentic workflows using durable execution engines like Temporal or AWS Step Functions cannot easily pause workflows for interactive human decisions without building complex polling mechanisms.
- **Proposed Solution**: Provide a native Temporal Activity worker and AWS Step Function task token runner in `hitl-cli` (`hitl-cli worker temporal --task-queue <queue>`). When a workflow reaches a human approval step, the worker receives the activity, dispatches the prompt via HITL, and asynchronously heartbeats and resolves the Temporal activity once human approval is received.
- **Business Value**: Enables enterprise platform engineering teams to seamlessly integrate HITL into production Temporal and Step Functions pipelines, unlocking enterprise contracts.
- **Effort Estimate**: M

---

## IDEA-604: Ephemeral Sandboxed Dry-Run Execution with Worktree Snapshot Verification (`hitl-cli request --dry-run-snapshot`)
- **Category**: Feature
- **Problem**: Reviewers approving risky filesystem or git manipulations cannot verify whether the command will succeed cleanly without dirtying their workspace.
- **Proposed Solution**: Implement a lightweight git worktree snapshot runner (`hitl-cli request --dry-run-snapshot`). Before submitting the approval request, the CLI executes the proposed command inside a temporary isolated branch and worktree, captures stdout/stderr and file diffs, and presents the actual executed outcome to the reviewer.
- **Business Value**: Gives reviewers 100% confidence before signing off on complex refactors or deletions, eliminating the fear of broken developer environments.
- **Effort Estimate**: M

---

## IDEA-605: Interactive Prompt Composing in `$EDITOR` with Markdown Validation (`hitl-cli request --edit`)
- **Category**: UX
- **Problem**: When submitting detailed human review prompts or bug reproduction steps with code blocks, typing long markdown directly into CLI arguments (`--prompt "..."`) is error-prone and leads to escaping bugs in shell scripts.
- **Proposed Solution**: Introduce an interactive prompt composing mode (`hitl-cli request --edit`) that opens the user's preferred `$EDITOR` (or micro-terminal modal) with syntax highlighting, template placeholders, and pre-flight markdown validation before submission to the relay.
- **Business Value**: Prevents malformed prompts and saves developer frustration when framing nuanced instructions for autonomous agents.
- **Effort Estimate**: S

---

## IDEA-606: In-Memory DNS Resolution Caching & Happy Eyeballs (RFC 8305) Dual-Stack Connection Pooling
- **Category**: Performance
- **Problem**: Repeated DNS lookups and IPv6/IPv4 connection timeouts in restrictive corporate environments cause unpredictable network latency during API client invocations.
- **Proposed Solution**: Implement a client-side TTL-aware DNS resolver cache and RFC 8305 "Happy Eyeballs" concurrent IPv4/IPv6 socket racer in `hitl_cli.api_client`. The client caches IP lookups across CLI invocations using an ephemeral memory-mapped cache, eliminating DNS overhead and automatically selecting the fastest transport path.
- **Business Value**: Cuts network latency by up to 200ms per prompt and eliminates connection timeout failures on corporate dual-stack IPv4/IPv6 networks.
- **Effort Estimate**: S

---

## IDEA-607: Cryptographic Artifact Provenance & Release Integrity Attestation via Sigstore (`hitl-cli self-update --verify`)
- **Category**: Security
- **Problem**: Developers running `hitl-cli` updates in CI pipelines or local workstations risk supply-chain compromise if an upstream PyPI package or mirror is hijacked.
- **Proposed Solution**: Integrate Sigstore Cosign verification into the update and installation workflows (`hitl-cli self-update`). Before applying updates or downloading release assets, the CLI checks the Sigstore transparency log (Rekor) to verify the digital signature against the project's official OIDC identity (slaser79/hitl-cli).
- **Business Value**: Mitigates supply chain poisoning attacks, safeguarding enterprise developer environments against malicious package substitutions.
- **Effort Estimate**: S

---

## IDEA-608: Strict Type Checking Enforcement & Zero-Error Mypy Strict Configuration
- **Category**: Tech Debt
- **Problem**: The codebase currently has no formal `mypy --strict` CI gate, allowing hidden type inconsistencies (e.g. `Optional` mismatches, implicit `Any` returns in Typer callbacks, and loose dictionary typing) to linger in critical paths like `api_client.py` and `crypto.py`.
- **Proposed Solution**: Configure `mypy` with `--strict` mode in `pyproject.toml`, annotate all untyped internal functions and generator yields, and add typed overloads for `ApiClient.request()` and `HITL.ask()` returning discriminated union response types. Integrate mypy enforcement into pre-commit and GitHub Actions CI.
- **Business Value**: Prevents regression bugs in production releases, speeds up external contributor onboarding, and ensures the Python SDK provides flawless autocomplete and type safety for IDEs.
- **Effort Estimate**: S

---

## IDEA-609: Database Migration Safety Interceptor (`hitl-cli db-gate`)
- **Category**: Integration
- **Problem**: Autonomous backend agents running database migrations (Alembic, Prisma, Flyway, Django) can easily apply destructive schema mutations (dropping columns, truncating tables, lock contention) that cause downtime.
- **Proposed Solution**: Implement a database migration interceptor (`hitl-cli db-gate -- <migration-command>`). It parses pending SQL DDL statements from the migration tool, classifies table locking and destructive operations, sends an impact summary to the DBA/lead's mobile device, and permits migration execution only after explicit confirmation.
- **Business Value**: Prevents catastrophic data loss and unscheduled database outages caused by unsupervised autonomous schema migrations.
- **Effort Estimate**: M

---

## IDEA-610: Interactive Terminal Fuzzy Choice Selector with Search-as-You-Type (`hitl-cli request --fuzzy`)
- **Category**: UX
- **Problem**: When a human-in-the-loop prompt presents a long list of choices (such as 10+ deployment environments, test suites, or branch names), standard numbered terminal prompts force cumbersome manual typing and scrolling.
- **Proposed Solution**: Implement an interactive fuzzy-search choice selector powered by `prompt_toolkit` in `hitl-cli request --fuzzy`. Reviewers can immediately type keywords to filter the option list in real time, navigate with arrow keys, and hit Enter to select, with instant fallback to standard numbering for non-interactive shells.
- **Business Value**: Streamlines developer terminal ergonomics and saves review time on multi-option prompt selections.
- **Effort Estimate**: S

---

## IDEA-611: High-Throughput Notification Micro-Batching with Client-Side Buffering in `hitl-cli notify` (`--flush-interval`)
- **Category**: Performance
- **Problem**: CI/CD jobs and agent batch runners invoking `hitl-cli notify` for each log event incur significant HTTP connection latency, slowing down pipeline execution when emitting dozens of status milestones.
- **Proposed Solution**: Implement a background notification daemon/worker with client-side micro-batching (`--batch-window 500ms`). Notifications dispatched within the micro-batch window are aggregated into a single HTTP array payload, cutting HTTP round-trips from dozens to one while preserving chronological order.
- **Business Value**: Accelerates CI/CD agent execution times by up to 40% and reduces mobile relay ingress load during rapid status updates.
- **Effort Estimate**: S

---

## IDEA-612: GitHub Copilot CLI Pre-Execution Approval Hook (`hitl-hook-copilot`)
- **Category**: Integration
- **Problem**: Developers using GitHub Copilot CLI (`gh copilot`) or Copilot Workspace agents currently have no unified way to route dangerous shell command suggestions to their mobile device for confirmation before execution.
- **Proposed Solution**: Implement a native wrapper and hook (`hitl-hook-copilot`) for the GitHub CLI copilot extension. When copilot suggests executing a high-impact command (like `rm -rf`, schema drops, or cloud deployments), the hook intercepts execution, transmits command context to the reviewer's mobile app, and blocks local execution until approved.
- **Business Value**: Expands HITL into millions of developer terminals utilizing GitHub Copilot, positioning HITL as the default enterprise safety gate for Copilot CLI workflows.
- **Effort Estimate**: S
