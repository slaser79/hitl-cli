# Ideas Batch — hitl-cli (Batch 33)

## IDEA-478: Git Worktree & Dirty State Auto-Detection Snapshot in HITL Prompt Context
- **Category**: Integration
- **Problem**: When an agent running inside a git repository asks for human confirmation on complex code actions, the human approver doesn't know what uncommitted changes or branch the agent is currently operating on without checking manually.
- **Proposed Solution**: Introduce `--git-context` (or automatic git repo inspection) in `hitl-cli request` that captures current branch, HEAD SHA, git status summary, and modified file list into structured prompt metadata. The mobile and terminal clients render this as a collapsible context card for fast inspection.
- **Business Value**: Prevents accidental approvals on wrong git branches or uncommitted working states, boosting developer trust in autonomous repo modifications.
- **Effort Estimate**: S

---

## IDEA-479: Post-Quantum Cryptography (PQC) Kyber/ML-KEM Key Exchange Hybrid Support
- **Category**: Security
- **Problem**: Long-term confidentiality of end-to-end encrypted HITL approval prompts is vulnerable to "harvest now, decrypt later" quantum attacks against classical Curve25519 cryptography.
- **Proposed Solution**: Add hybrid post-quantum key encapsulation (ML-KEM-768 combined with X25519) into `crypto.py`, enabling enterprise teams to generate quantum-resistant E2EE session keys. The CLI automatically negotiates hybrid cipher suites with compatible mobile and relay clients.
- **Business Value**: Future-proofs sensitive organizational and sovereign data against quantum decryption threats, qualifying `hitl-cli` for high-security government and enterprise defense bids.
- **Effort Estimate**: M

---

## IDEA-480: Interactive TUI Fleet Monitor (`hitl-cli top`) for Multi-Agent Task Tracking
- **Category**: UX
- **Problem**: In multi-agent autonomous environments where multiple AI workers run concurrently in parallel containers or processes, developers have no unified live dashboard to monitor queue depths, pending approvals, and agent statuses.
- **Proposed Solution**: Build `hitl-cli top`, an interactive terminal dashboard using Textual and Rich that displays live active requests, pending human approvals, response timers, agent IDs, and connection health in real time. Developers can navigate between active requests and resolve them directly from the TUI.
- **Business Value**: Gives engineering teams complete real-time observability across their entire agent fleet, preventing stalled agents from going unnoticed.
- **Effort Estimate**: M

---

## IDEA-481: Async Zero-Copy Binary IPC Transport for Local MCP Proxy Daemon
- **Category**: Performance
- **Problem**: When running `hitl-cli proxy` with Claude Desktop or local IDEs over stdio, continuous high-frequency JSON-RPC parsing over pipes incurs JSON serialization bottlenecks and sub-optimal process spawning overhead.
- **Proposed Solution**: Introduce an optional local UNIX domain socket (or Windows named pipe) binary transport utilizing msgpack or flatbuffers for the MCP proxy daemon (`hitl-cli proxy --socket /tmp/hitl.sock`), replacing stdio string pipes with persistent zero-copy local IPC. The proxy daemon maintains background persistent connections to the relay while serving local tools with microsecond response times.
- **Business Value**: Reduces local MCP proxy latency and CPU consumption by 45%, providing instantaneous responsiveness during rapid autonomous tool-call loops.
- **Effort Estimate**: M

---

## IDEA-482: Pluggable Transport Layer Architecture with Decoupled Protocol Adapters
- **Category**: Tech Debt
- **Problem**: Transport logic in `api_client.py` and `mcp_client.py` is tightly coupled with HTTP/REST implementation details, making it difficult to introduce new protocols (gRPC, WebSockets, SSE) or mock networking during tests.
- **Proposed Solution**: Refactor internal networking into an abstract `BaseTransport` interface with pluggable adapters (`HttpTransport`, `SseTransport`, `SocketTransport`, `MockTransport`) and centralized request/response interceptor pipelines. Authentication headers and E2EE framing are moved into composable middleware layers.
- **Business Value**: Accelerates future protocol development velocity by 30% and simplifies test isolation across all client components.
- **Effort Estimate**: M

---

## IDEA-483: Ephemeral "Magic-Link" Web Review Generation for Non-App Stakeholders
- **Category**: Feature
- **Problem**: Requesting input from external stakeholders, clients, or non-technical business partners who do not have the HITL mobile app installed requires manual copying of prompts into emails or chats.
- **Proposed Solution**: Support `--magic-link` on `hitl-cli request`, which generates an encrypted, single-use, time-expiring web approval URL that can be shared via email or Slack for instant browser-based approval without app installation. The link securely transmits the human response back to the waiting CLI via the relay.
- **Business Value**: Expands HITL reach across non-technical team members and external clients, unlocking B2B approval workflows without onboarding friction.
- **Effort Estimate**: M

---

## IDEA-484: In-Memory Secret Zeroization & Automated Terminal Redaction Filter
- **Category**: Security
- **Problem**: Prompts containing temporary tokens, connection strings, or sensitive PII may linger in OS terminal scrollback buffers, bash history, and process memory dumps.
- **Proposed Solution**: Implement an in-memory entropy and pattern detector in `hitl_cli.output` that auto-redacts detected credentials with `***` in terminal renders, while zeroizing in-memory plaintext string buffers using `ctypes.memset` upon task completion. A `--no-redact` override flag allows explicit opt-out when debugging.
- **Business Value**: Mitigates enterprise compliance breaches and accidental credential leaks in recorded screen shares, shared terminal logs, and system crash dumps.
- **Effort Estimate**: S

---

## IDEA-485: Dynamic Payload Delta Compression with Content-Defined Chunking for Multi-Turn Agent Loops
- **Category**: Performance
- **Problem**: Long-running iterative agent loops repeatedly send large code contexts or prompts with only minor diffs between turns, wasting bandwidth and compute.
- **Proposed Solution**: Implement client-side content-defined chunking (CDC) and rolling hash delta compression in the SDK/CLI; if a base context was recently transmitted, the CLI only transmits delta patches and chunk references. The mobile app reconstructs the full prompt using cached chunks.
- **Business Value**: Cuts mobile network data usage by up to 75% for multi-turn workflows and decreases relay transmission latency.
- **Effort Estimate**: M

---

## IDEA-486: Multi-Stage Escalation Ladder with Dynamic Tiered Timeouts (`--escalate`)
- **Category**: Feature
- **Problem**: When an urgent agent request goes unacknowledged by the primary on-call reviewer for several minutes, the agent stalls indefinitely rather than routing the request to a secondary reviewer.
- **Proposed Solution**: Introduce `--escalate "5m:secondary_user,15m:team_lead"` to `hitl-cli request`, allowing the CLI to define time-based escalation policies that dynamically page backup approvers if the primary reviewer does not respond within the tier window. The CLI tracks escalation state and updates local progress indicators.
- **Business Value**: Slashes SLA breach rates and prevents critical automated workflows from blocking when individual reviewers are unavailable.
- **Effort Estimate**: M

---

## IDEA-487: Kubernetes Operator & Custom Resource Definition (CRD) for Declarative Pipeline Approval Gates
- **Category**: Integration
- **Problem**: Cloud-native deployment pipelines running ArgoCD, Tekton, or Kubernetes Jobs require complex custom scripts to pause deployments for human signoff.
- **Proposed Solution**: Provide a lightweight Kubernetes Operator and `HitlRequest` CRD that wraps `hitl-cli`, automatically managing pod lifecycle, status reporting, and cluster-level webhook approval gates. GitOps engines can watch the CRD status to resume deployment syncs upon human approval.
- **Business Value**: Captures the enterprise cloud-native market by standardizing human approval gates directly inside Kubernetes CI/CD workflows.
- **Effort Estimate**: L

---

## IDEA-488: Syntax-Highlighted Split-Diff Visualizer for Code Review Approvals (`--diff`)
- **Category**: UX
- **Problem**: When coding agents propose code or configuration edits, plain text prompts scramble indentation and make multi-file code diffs unreadable in both terminal and mobile views.
- **Proposed Solution**: Implement a native syntax-highlighted side-by-side diff renderer in the CLI (`hitl-cli diff-preview` / rich diff styling) and generate structured split-diff payload metadata for mobile rendering. Agents can pass `--diff <file_or_patch>` so reviewers see clear green/red line changes with syntax highlighting.
- **Business Value**: Dramatically reduces developer cognitive fatigue and error rates when approving automated code modifications, boosting review speed and user trust.
- **Effort Estimate**: S

---

## IDEA-489: Standardized OpenTelemetry Semantic Convention Tracing Exporter
- **Category**: Tech Debt
- **Problem**: Internal tracing and diagnostics in `hitl-cli` lack standardization with OpenTelemetry semantic conventions for GenAI and human-in-the-loop workflows, preventing unified observability across enterprise APM dashboards.
- **Proposed Solution**: Implement full W3C Trace Context propagation and OTel GenAI semantic attributes (`gen_ai.system`, `gen_ai.request.hitl_type`, `hitl.human_latency_seconds`) in the Python SDK and CLI networking stack. Traces can be exported via OTLP gRPC/HTTP directly to configured collectors.
- **Business Value**: Enables DevOps teams to monitor human response latencies and agent interaction bottlenecks alongside overall application traces in Datadog, New Relic, and Honeycomb.
- **Effort Estimate**: S

---

## IDEA-490: Smart Audio-Visual Terminal Alerts & Configurable Desktop Bell (`--alert`)
- **Category**: UX
- **Problem**: Developers running agent tasks in background terminal windows or minimized tabs frequently miss when an agent is waiting for input, wasting minutes before realizing the agent is blocked.
- **Proposed Solution**: Add `--alert [bell|visual|modal]` flag to `hitl-cli request` that rings the terminal bell (`\a`), flashes the terminal tab title, or renders a native system toast notification when an input prompt is dispatched. An optional repeat interval keeps pinging until answered.
- **Business Value**: Eliminates developer idle time waiting on blocked agents, increasing overall developer productivity by up to 20%.
- **Effort Estimate**: S

---

## IDEA-491: Agent Execution Replay Sandbox with Interactive Time-Travel Debugging
- **Category**: Feature
- **Problem**: When an agent behaves unexpectedly after receiving human input, engineers cannot easily step backward to inspect the exact prompt, choices, and environment state that produced the behavior.
- **Proposed Solution**: Introduce `hitl-cli replay --snapshot <file>` to record and replay deterministic session trees, allowing engineers to simulate alternative human choices at any decision node without re-executing costly agent steps. The SDK saves execution trace DAGs with all intermediate inputs.
- **Business Value**: Slashes AI workflow debugging time by 50% and allows safe regression testing of complex agent interaction trees.
- **Effort Estimate**: M

---

## IDEA-492: Automated OAuth Scope Downgrade & Read-Only CI Token Provisioning (`hitl-cli token mint`)
- **Category**: Security
- **Problem**: Developers frequently reuse high-privilege interactive OAuth tokens in unattended CI/CD test runners, creating unnecessary credential exposure if logs or runners are compromised.
- **Proposed Solution**: Add `hitl-cli token mint --scope notify:only --ttl 1h` to generate cryptographically restricted, short-lived, least-privilege child tokens for CI jobs and sub-agent processes. The minted token includes embedded cryptographic caveats and expiry timestamps.
- **Business Value**: Enforces the principle of least privilege across automated pipelines, reducing security breach impact radius in enterprise environments.
- **Effort Estimate**: S
