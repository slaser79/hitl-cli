# Ideas Batch — hitl-cli (Batch 28)

## IDEA-403: Security-Hardened SDK Sandbox with Restricted Command Execution
- **Category**: Security
- **Problem**: When an agent executes arbitrary tool commands based on human response input, it may lead to security vulnerabilities if the response payload has been hijacked or spoofed.
- **Proposed Solution**: Introduce a restricted sandbox environment inside the SDK that validates and filters human responses before passing them to CLI subprocesses. Users can define strict regular expression or schema allowlists for executable text values.
- **Business Value**: Mitigates risk of remote code execution (RCE) on systems running autonomous agent hooks.
- **Effort Estimate**: M

---

## IDEA-404: SDK Heartbeat-Driven Liveness Detection for Long-Running Agent Hooks
- **Category**: Performance
- **Problem**: When `review_and_continue` or other CLI hooks run, if the host agent process hangs or dies silently, the relay waits indefinitely for response completion, locking up human queue bandwidth.
- **Proposed Solution**: Implement an active heartbeat mechanism inside the SDK and CLI. The client regularly reports "still alive and polling" to the relay every 30 seconds; if the relay misses multiple heartbeats, it automatically marks the request as "abandoned/stuck" and frees up the human's inbox.
- **Business Value**: Promotes high efficiency and team responsiveness by preventing stuck/dangling approval tasks.
- **Effort Estimate**: S

---

## IDEA-405: CLI `doctor` diagnostic bundle with E2EE payload validation
- **Category**: Tech Debt
- **Problem**: Troubleshooting decryption failures between the CLI, SDK, and the mobile app is incredibly difficult since E2EE keys are locally generated and payloads are fully opaque.
- **Proposed Solution**: Extend the `doctor` subcommand with a `--verify-crypto` flag that runs test-vectors through the local PyNaCl setup and verifies key exchange status with the relay without exposing actual private keys.
- **Business Value**: Enhances developer efficiency by shortening the debugging cycle for complex E2EE errors from days to seconds.
- **Effort Estimate**: S

---

## IDEA-406: Interactive Command-Line Prompt Editor (Interactive TUI Editor)
- **Category**: UX
- **Problem**: Typing long multi-line prompt messages or markdown tables in standard terminal arguments is painful and prone to shell formatting errors.
- **Proposed Solution**: When generating a request, if the user leaves the `--prompt` argument empty or specifies `--edit`, launch the user's preferred command-line text editor (via `$EDITOR` or `$VISUAL`) with a temporary Markdown template. Upon saving and exiting, the CLI validates, parses, and sends the prompt.
- **Business Value**: Improves developer adoption and satisfaction by providing a native terminal-centric editing experience.
- **Effort Estimate**: S

---

## IDEA-407: Real-time Audio Alert Bridge for Urgent Notifications
- **Category**: UX
- **Problem**: When developers are away from their screens or working in full-screen IDEs, standard push notifications are easy to miss, delaying critical deployments.
- **Proposed Solution**: Add an option in the CLI (`--voice` or `--audio`) that uses local text-to-speech engines (e.g., `say` on macOS, `espeak` on Linux) to speak the prompt out loud, or play a distinct audio tone when a request lands.
- **Business Value**: Reduces response latency for critical real-time approvals, keeping automation pipelines moving.
- **Effort Estimate**: S

---

## IDEA-408: Hierarchical Multi-Agent Context Aggregation
- **Category**: Feature
- **Problem**: In complex multi-agent workflows, a parent agent might spawn subagents that also require human approvals, but the human sees each subagent request as isolated without knowing the parent task context.
- **Proposed Solution**: Allow requests to pass a `parent_request_id` or `trace_id`. The CLI and relay aggregate these hierarchical tasks so the human can see a nested tree of approvals, showing exactly which subagent requested what and under which parent goal.
- **Business Value**: Improves human decision accuracy and retention by providing full contextual visibility of nested agent actions.
- **Effort Estimate**: M

---

## IDEA-409: Pre-Registered Mock Response Profiles for Non-Interactive Testing
- **Category**: Feature
- **Problem**: Testing CLI/SDK integrations in CI/CD environments currently requires spinning up a mock server or manually mocking HTTP clients, which is complex and brittle.
- **Proposed Solution**: Introduce a `--mock-profile` CLI flag and SDK parameter. Developers can specify a local JSON profile (e.g., `{"Choose option X": "Option X chosen"}`) that automatically intercepts outgoing requests and returns predefined responses locally without hitting the network.
- **Business Value**: Accelerates developer productivity and reliability of testing pipelines.
- **Effort Estimate**: S

---

## IDEA-410: Adaptive Rate Limiting with Backpressure Negotiation
- **Category**: Performance
- **Problem**: The HITL relay can become overloaded during massive batch jobs, but client-side rate limiters are static and don't dynamically adjust to relay load.
- **Proposed Solution**: Implement a dynamic window rate limiter in `ApiClient` that reads custom response headers (e.g., `X-RateLimit-Current-Load`) from the relay and dynamically shrinks or expands its request sending window to prevent service outages.
- **Business Value**: Enhances system reliability and reduces server infrastructure costs under high load.
- **Effort Estimate**: M

---

## IDEA-411: Local Audit Log Deduplication and Compaction
- **Category**: Performance
- **Problem**: Long-running CLI daemons or SDK servers accumulate massive local SQLite or JSONL audit logs over months, leading to high disk usage and slow search lookups.
- **Proposed Solution**: Add a background compaction task or command `hitl-cli history compact` that deduplicates redundant entries, archives older entries, and compresses transaction history to keep the database size minimal.
- **Business Value**: Saves disk space and improves log retrieval speed on developer workstations.
- **Effort Estimate**: S

---

## IDEA-412: Declarative Command Routing via Config Policies
- **Category**: Integration
- **Problem**: Developers want different request types (e.g., security alerts vs. budget approvals) to route to different human supervisors, but hardcoding these routes in the agent logic is inflexible.
- **Proposed Solution**: Implement a config-based routing engine. Developers define routing rules in `~/.hitl/config.json` mapping specific tags/priorities to target relay channels or user groups, decoupling routing decisions from the agent code.
- **Business Value**: Increases administrative control and organizational efficiency by streamlining request workflows.
- **Effort Estimate**: M

---

## IDEA-413: Automated SDK Dependency Lazy Loading
- **Category**: Tech Debt
- **Problem**: Importing `hitl-cli` in Python projects is slow because it immediately loads heavy modules like `cryptography`, `PyNaCl`, and `FastMCP`, even if the user only wants to use basic, unencrypted REST functions.
- **Proposed Solution**: Refactor the SDK imports to lazy-load optional dependencies. The heavy cryptographic and MCP modules are only imported at runtime when a feature requiring E2EE or FastMCP is actually invoked.
- **Business Value**: Significantly speeds up startup times for lightweight python agents, improving developer experience.
- **Effort Estimate**: S

---

## IDEA-414: Native Integration with System Keychains for E2EE Private Keys
- **Category**: Security
- **Problem**: Storing E2EE private keys in plaintext or simple configuration files on disk is a major security risk if the developer machine is compromised.
- **Proposed Solution**: Integrate the Python `keyring` library into `crypto.py`. The private key generated during registration is securely stored in the OS-native credential manager (macOS Keychain, Windows Credential Manager, or Linux Secret Service).
- **Business Value**: Maximizes security compliance and minimizes the risk of E2EE key theft on local developer systems.
- **Effort Estimate**: M

---

## IDEA-415: Human Presence-Aware Intelligent Polling Intervals
- **Category**: Performance
- **Problem**: The SDK/CLI keeps polling the relay for human input at a constant rate, which wastes bandwidth and API calls when the human is offline or during non-working hours.
- **Proposed Solution**: Implement adaptive polling. The relay returns metadata about the human's last active timestamp or online state, allowing the CLI to back off its poll interval to 10-15 seconds when the human is offline, and speed up to 1-2 seconds when the human is actively viewing the prompt.
- **Business Value**: Drastically reduces network traffic, API costs, and server load.
- **Effort Estimate**: S

---

## IDEA-416: CLI Shell Alias Generator for Common HITL Tasks
- **Category**: UX
- **Problem**: Running common actions like checking notifications or listing active agents requires typing long command flags repeatedly.
- **Proposed Solution**: Provide a CLI helper command `hitl-cli alias-gen` that generates short, intuitive shell aliases (e.g., `hask`, `hnotify`, `hstatus`) compatible with Bash, Zsh, or Fish, saving keystrokes.
- **Business Value**: Boosts developer productivity and makes everyday CLI interaction frictionless.
- **Effort Estimate**: S

---

## IDEA-417: Federated Multi-Relay Fallback Support
- **Category**: Integration
- **Problem**: Relying on a single `HITL_SERVER_URL` relay creates a single point of failure; if the primary relay is down, the entire hitl-cli ecosystem stops working.
- **Proposed Solution**: Allow configuring a list of fallback relay URLs. If connection to the primary relay fails, `ApiClient` automatically rolls over to secondary/private backup relays to submit the notification/request.
- **Business Value**: Guarantees high availability and business continuity for mission-critical enterprise workflows.
- **Effort Estimate**: M
