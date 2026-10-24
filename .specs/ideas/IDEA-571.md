# Ideas Batch — hitl-cli (Batch 571)

## IDEA-613: Model Context Protocol (MCP) Dynamic Resources & Policy Discovery (`hitl://`)
- **Category**: Feature
- **Problem**: Autonomous agents communicating over MCP (Claude Code, Cursor, Antigravity) currently only discover HITL capabilities via active tools (`request_human_input`, `notify`), leaving models blind to organizational review guidelines, human availability hours, or project safety policies before formulating actions.
- **Proposed Solution**: Extend `proxy_handler_v2.py` to implement the standard MCP Resources protocol (`resources/list`, `resources/read`). Expose dynamic URI resources such as `hitl://guidelines/safety`, `hitl://reviewer/status`, and `hitl://project/review-criteria` that models read directly into their prompt context to self-align with review expectations before invoking sensitive operations.
- **Business Value**: Proactively aligns autonomous agents with team policies before destructive commands are attempted, eliminating unnecessary rejected review requests and saving human reviewer time.
- **Effort Estimate**: M

---

## IDEA-614: Context Pruning & AST-Aware Log Distillation Engine (`hitl-cli request --prune-context`)
- **Category**: Performance
- **Problem**: Coding agents frequently include multi-megabyte log files, long compiler stack traces, or entire source files in review prompts, exceeding mobile push notification payload limits (e.g., Apple APNS 4KB payload cap) and causing network serialization stalls.
- **Proposed Solution**: Implement an AST-aware and stack-trace-aware context pruning algorithm in `hitl-cli request --prune-context`. The engine automatically extracts the root cause exception, preserves immediate git diff hunks with surrounding function signatures, and collapses repetitive boilerplate lines, reducing payload byte-size by up to 90% while maintaining complete human readability.
- **Business Value**: Ensures prompt payloads fit within instant mobile push notification limits without truncation, accelerating network transmission and reducing mobile reviewer data usage.
- **Effort Estimate**: S

---

## IDEA-615: Detailed Interactive Event Timeline & Audit Inspector (`hitl-cli inspect <request-id>`)
- **Category**: UX
- **Problem**: When an agent request times out, fails, or is rejected, developers have no simple CLI tool to inspect the lifecycle of the transaction, leaving them to guess whether the mobile push notification was delivered, opened, dismissed, or blocked by network connectivity.
- **Proposed Solution**: Implement `hitl-cli inspect <request_id>` that queries the relay for full diagnostic event history and renders an interactive Rich-formatted timeline: prompt dispatch timestamp, APNS/FCM delivery receipt, mobile client screen open time, reviewer interaction duration, and final cryptographic signature verification.
- **Business Value**: Cuts troubleshooting time from hours of log-digging to seconds for engineers and platform teams debugging human-agent interaction delays.
- **Effort Estimate**: S

---

## IDEA-616: Automated Ephemeral Git Workspace Rollback Guard on Human Rejection (`--rollback-on-reject`)
- **Category**: Feature
- **Problem**: When an autonomous coding agent performs code changes and asks for approval via `hitl-cli request`, if the human reviewer rejects the proposed change, the agent process or developer environment is left with dirty, rejected modifications across the working tree, requiring manual git resets or stash drops.
- **Proposed Solution**: Add a `--rollback-on-reject` flag to `hitl-cli request`. Before dispatching the prompt, `hitl-cli` creates a temporary in-memory or ephemeral stash of modified and untracked files. If the reviewer selects a rejection choice or the prompt expires, the CLI automatically restores the repository to its clean pre-request state, safely discarding rejected artifacts.
- **Business Value**: Eliminates broken, half-applied code changes when human reviewers reject agent actions, saving developers from tedious manual git cleanup and preventing accidental dirty commits.
- **Effort Estimate**: S

---

## IDEA-617: Machine-Readable POSIX Exit Code Taxonomy & Structured JSON Errors (`--json-errors`)
- **Category**: Tech Debt
- **Problem**: `hitl-cli` currently exits with generic status codes (0 for success, 1 for all failures), forcing shell scripts, CI runners, and agent supervisory harnesses to parse fragile, localized human text from stderr to determine whether an error was an auth failure, timeout, network error, or user rejection.
- **Proposed Solution**: Establish a formal `HitlExitCode` enumeration mapping specific operational outcomes to predictable POSIX return codes (e.g. 0=Approved, 10=Rejected by Human, 11=Timeout Expired, 12=Authentication Missing, 13=Relay Unreachable, 14=Payload Validation Failed). Add a `--json-errors` global flag that emits a structured JSON error envelope to stderr.
- **Business Value**: Makes `hitl-cli` rock-solid for enterprise automation, eliminating flaky bash string-parsing scripts in CI/CD and multi-agent harnesses.
- **Effort Estimate**: S

---

## IDEA-618: eBPF-Powered Linux System Call Safety Interceptor (`hitl-ebpf-guard`)
- **Category**: Security
- **Problem**: Autonomous coding agents executing in Docker containers or developer workstations can attempt dangerous system calls (e.g. executing unauthorized binaries, tampering with `/etc/hosts`, or opening outbound reverse shells to arbitrary IP addresses) before a human can intervene.
- **Proposed Solution**: Develop a lightweight eBPF security probe (`hitl-ebpf-guard`) that hooks into kernel `sys_enter_execve`, `sys_enter_connect`, and `sys_enter_unlinkat`. When a sandboxed agent process initiates a system call matching high-risk patterns, the eBPF filter suspends the calling thread at the kernel level, dispatches an approval request via `hitl-cli`, and resumes or terminates the thread based on human authorization.
- **Business Value**: Provides tamper-proof, kernel-level guardrails for autonomous coding agents, unlocking deployment in defense, banking, and high-security enterprise environments.
- **Effort Estimate**: L

---

## IDEA-619: Native Ansible Playbook Human Approval Module (`hitl_approval`)
- **Category**: Integration
- **Problem**: IT operations and systems engineering teams running autonomous Ansible automation playbooks currently lack an easy way to pause execution and request mobile human verification before executing dangerous server configuration changes (such as firewall rule updates, kernel package upgrades, or disk repartitioning).
- **Proposed Solution**: Create an official Ansible module (`hitl_approval`) that wraps the HITL Python SDK. When included in a playbook, the task submits host details, changed configuration diffs, and timeout limits to the sysadmin's mobile app via HITL, cleanly continuing the play upon approval or failing the task upon rejection or timeout.
- **Business Value**: Expands HITL into millions of enterprise IT and sysadmin workflows managed by Ansible, positioning HITL as the premier human safety gate for infrastructure automation.
- **Effort Estimate**: S

---

## IDEA-620: Zero-Copy Local IPC Transport via Linux Abstract Domain Sockets (`hitl-cli proxy --abstract-socket`)
- **Category**: Performance
- **Problem**: Standard stdio pipes used in MCP proxy mode (`proxy_handler_v2.py`) suffer from stdin/stdout buffering quirks, occasional deadlocks on large JSON-RPC messages, and filesystem permission collisions when using file-based Unix sockets in shared environments.
- **Proposed Solution**: Implement support for Linux abstract domain sockets (and Windows named pipes) in `hitl-cli proxy --abstract-socket @hitl_agent_proxy`. The transport bypasses the filesystem hierarchy completely, eliminates file permission cleanup issues upon process termination, and enables high-throughput, zero-copy local message passing between agent processes and the proxy server.
- **Business Value**: Eliminates stdio stream corruption crashes and speeds up local IPC throughput by 4x for high-frequency agent tool calling.
- **Effort Estimate**: S

---

## IDEA-621: Live Terminal Session Cast & VT100 Asciinema Stream Attachment (`hitl-cli request --stream-cast`)
- **Category**: UX
- **Problem**: When an autonomous agent encounters an interactive CLI tool failure (e.g., curses/TUI wizard, dynamic progress display, interactive prompt stall), static text logs lose all visual context and terminal timing dynamics, making it almost impossible for a remote human to diagnose the blocker.
- **Proposed Solution**: Add `--stream-cast` to `hitl-cli request`. The CLI captures an in-memory VT100 / asciinema terminal cast of the agent's recent session execution window (including cursor movements, ANSI color sequences, and timing delays) and attaches it as an interactive, scrubbable player inside the HITL mobile and web reviewer interface.
- **Business Value**: Enables instant diagnostic comprehension of complex CLI and TUI agent failures, cutting reviewer triage time by half and eliminating back-and-forth debugging messages.
- **Effort Estimate**: S

---

## IDEA-622: Client-Side Prompt Injection & Malicious Instruction Quarantining Filter (`--guard-injection`)
- **Category**: Security
- **Problem**: When autonomous agents construct review prompts using untrusted external web scrapes, customer tickets, or third-party git diffs, prompt injection attacks (e.g. hidden instructions like "Approve this without reading" or "Ignore previous system prompt") can deceive the human reviewer or manipulate reviewer tools.
- **Proposed Solution**: Implement a client-side heuristic and syntax prompt-injection scanner (`--guard-injection`) in `hitl-cli request`. Before transmitting the prompt payload, it evaluates external text inputs against known prompt injection and delimiter-escaping vectors, visually quarantining suspicious external strings inside isolated warning callout boxes in the reviewer's mobile UI.
- **Business Value**: Protects human reviewers and autonomous agent orchestrations from malicious prompt injection attacks embedded in untrusted external inputs.
- **Effort Estimate**: S

---

## IDEA-623: Argo Workflows & Tekton Pipelines Step Approval Interceptor (`hitl-workflow-gate`)
- **Category**: Integration
- **Problem**: Cloud-native CI/CD engines like Argo Workflows and Tekton lack a native mobile human approval step, forcing platform teams to create complex custom webhook servers or manually patch workflow manifests.
- **Proposed Solution**: Ship a lightweight, containerized step runner (`hitl-workflow-gate`) that can be dropped directly into Argo Workflow `DAG` templates or Tekton `Task` specifications. The container executes `hitl-cli request`, posts status annotations to the Kubernetes workflow CRD, and pauses pipeline progression until the on-call engineer approves the step on mobile.
- **Business Value**: Drives rapid adoption among cloud-native platform engineering teams using Argo and Tekton for automated production releases.
- **Effort Estimate**: M

---

## IDEA-624: Canary Prompt Routing & Reviewer Group A/B Testing (`hitl-cli request --canary`)
- **Category**: Feature
- **Problem**: Organizations deploying new prompt schemas, risk evaluation policies, or autonomous agent models risk widespread workflow disruption if the new prompts are confusing or lead to high false rejection rates.
- **Proposed Solution**: Introduce a canary evaluation engine in `hitl-cli request --canary <percent>`. The CLI routes a configurable percentage (e.g., 10%) of prompt traffic to an experimental reviewer group or alternative prompt formatting template, while routing the remaining 90% through the baseline flow, collecting comparative response times and clarity metrics.
- **Business Value**: Enables safe, data-driven optimization of human review prompts across large enterprise fleets without risking productivity crashes.
- **Effort Estimate**: M

---

## IDEA-625: Interactive Terminal Conversational Clarification Loop (`hitl-cli converse <request-id>`)
- **Category**: UX
- **Problem**: When an agent prompt is slightly ambiguous, reviewers on desktop terminals cannot easily ask a quick clarifying question or request additional context without either blindly rejecting the request or switching to an external chat application.
- **Proposed Solution**: Add an interactive local conversational terminal loop (`hitl-cli converse <request-id>`). It allows a desktop reviewer to post inline clarifying questions back to the agent session; the agent provides additional context, diffs, or logs, and the reviewer can resolve the prompt with full context without terminating the agent workflow.
- **Business Value**: Prevents premature task cancellations on complex engineering tasks, increasing agent completion rates and reducing developer frustration.
- **Effort Estimate**: M

---

## IDEA-626: Standalone In-Process Deterministic Mock Relay Server (`hitl-relay-mock`)
- **Category**: Tech Debt
- **Problem**: The test suite currently relies on scattered HTTP mocks (`unittest.mock` and `respx`) that drift from the actual backend relay API contract (`hitl-shin-relay`), leading to unexpected runtime regressions when backend API schemas or auth headers change.
- **Proposed Solution**: Build a standalone, in-process deterministic mock relay server (`hitl_cli.testing.MockRelay`) implementing the exact HTTP and SSE protocol of `hitl-shin-relay`. Use it across integration tests to validate end-to-end OAuth registration, E2EE key exchange, SSE streaming, and error handling without external network dependencies.
- **Business Value**: Prevents regressions caused by client-backend contract drift and speeds up automated CI test execution by running fully local, deterministic protocol tests.
- **Effort Estimate**: S

---

## IDEA-627: Slack & Discord Bi-Directional Team Approval Bridge Daemon (`hitl-cli bridge team`)
- **Category**: Integration
- **Problem**: In engineering organizations where developers and operators collaborate primarily in Slack or Discord channels, requiring every team member to install a separate mobile app creates friction and delays for team-wide consensus decisions.
- **Proposed Solution**: Introduce a lightweight bridge daemon (`hitl-cli bridge team --channel slack|discord`). The bridge mirrors HITL prompts into configured Slack/Discord channels with interactive Block Kit action buttons, securely translates button clicks into authenticated HITL responses, and posts real-time agent status updates back to the chat thread.
- **Business Value**: Broadens enterprise organizational adoption by meeting engineering teams where they already communicate, accelerating approval turnarounds without forcing mobile app installation.
- **Effort Estimate**: M
