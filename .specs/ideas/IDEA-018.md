# Ideas Batch — hitl-cli (Batch 24)

## IDEA-346: "Agent-Persona" Customization
- **Category**: UX
- **Problem**: In the mobile app, all agents look identical, making it difficult for the human to quickly distinguish between different types of agents (e.g., a "Security Watchdog" vs. a "Code Refactorer").
- **Proposed Solution**: Allow agents to specify persona metadata including a custom name, emoji icon, and color theme. The mobile app will use this metadata to customize the notification and the request UI.
- **Business Value**: Reduces human cognitive load and speeds up recognition of the requesting agent's purpose.
- **Effort Estimate**: S

---

## IDEA-347: "Just-in-Time" Credential Injection
- **Category**: Security
- **Problem**: Agents often need temporary access to sensitive credentials that should not be stored on the agent's disk or in its environment variables.
- **Proposed Solution**: Implement a specific request flow where the agent can request a secret from the human. The human provides the secret in the mobile app, and it is securely relayed to the agent's memory via the E2EE proxy, never touching the disk.
- **Business Value**: Enables secure, human-gated management of sensitive secrets for autonomous tasks.
- **Effort Estimate**: M

---

## IDEA-348: "Request Priority" with OS-level Critical Alerts
- **Category**: Feature
- **Problem**: Critical security or system failure alerts might be missed if the human's phone is in "Do Not Disturb" or "Silent" mode.
- **Proposed Solution**: Utilize the iOS and Android "Critical Alerts" API for high-priority HITL requests. These requests will bypass the device's mute and DND settings to ensure they are seen immediately.
- **Business Value**: Ensures that mission-critical or life-critical notifications are delivered reliably regardless of device state.
- **Effort Estimate**: M

---

## IDEA-349: "Human-in-the-Loop" Git Hook Integration
- **Category**: Integration
- **Problem**: Developers may accidentally push sensitive data or breaking changes because traditional git hooks are easily bypassed or ignored.
- **Proposed Solution**: Provide a `hitl-git-hook` that can be configured as a `pre-push` or `pre-commit` hook. It requires a mobile app confirmation before the git operation is allowed to complete.
- **Business Value**: Adds a physical human-verification layer to the DevOps pipeline to prevent costly mistakes.
- **Effort Estimate**: S

---

## IDEA-350: "Agent Collaboration" - Human-Mediated Handover
- **Category**: Feature
- **Problem**: Multi-agent workflows often require one agent to hand over its work to another agent, but the transition point needs human validation.
- **Proposed Solution**: A specific "Handover" request type where the human reviews the output of the first agent and then selects which downstream agent should receive the data next from a list of available agents.
- **Business Value**: Enables complex, multi-agent pipelines with human-verified quality gates between stages.
- **Effort Estimate**: M

---

## IDEA-351: "SDK" Support for Python Logging Handler
- **Category**: Tech Debt
- **Problem**: Developers want to route critical errors or specific logs to their HITL app without having to manually integrate the SDK calls throughout their codebase.
- **Proposed Solution**: Implement a `HITLHandler` for the standard Python `logging` module. This allows developers to add HITL as a logging target with a single line of configuration.
- **Business Value**: Lowers the barrier to entry for adding mobile alerting to existing Python applications.
- **Effort Estimate**: S

---

## IDEA-352: "mDNS" Discovery for Local-Only HITL
- **Category**: Integration
- **Problem**: In high-security or air-gapped environments, agents and humans may be on the same local network but cannot reach the public internet to connect via the relay.
- **Proposed Solution**: Implement Multicast DNS (mDNS) discovery in the CLI and SDK to allow local discovery and direct communication between agents and human devices on the same subnet.
- **Business Value**: Extends HITL utility to secure, offline, or remote edge infrastructures where internet access is restricted.
- **Effort Estimate**: L

---

## IDEA-353: "Interactive-Terminal" via E2EE Proxy
- **Category**: Feature
- **Problem**: A human may need to run a quick diagnostic command (e.g., `ls`, `tail`, `ps`) on the agent's machine to understand context, but SSH access may be restricted or too heavyweight.
- **Proposed Solution**: Provide a "Remote Shell" request type where the mobile app provides a secure terminal interface to execute a set of pre-approved commands on the agent's machine via the E2EE proxy.
- **Business Value**: Provides a safe and lightweight way for humans to inspect the agent's environment without full SSH access.
- **Effort Estimate**: L

---

## IDEA-354: "Shell-Alias" Generator for Common Tasks
- **Category**: UX
- **Problem**: Typing full `hitl-cli` commands with multiple flags is cumbersome for developers who frequently perform the same manual signals.
- **Proposed Solution**: A command `hitl-cli alias` that generates a set of optimized shell aliases for the user's shell (Bash/Zsh) for common notification and request patterns.
- **Business Value**: Encourages frequent use of HITL by reducing the friction of repetitive manual signaling tasks.
- **Effort Estimate**: S

---

## IDEA-355: "Streaming" Human Input for Long Responses
- **Category**: Feature
- **Problem**: Agents must wait for the human to finish typing a long multi-line response and hit "Send" before they can see any of the input.
- **Proposed Solution**: Support for streaming human input via WebSockets or SSE, allowing the agent to receive partial updates as the human types their reasoning or instructions.
- **Business Value**: Reduces overall latency and allows the agent to start processing or ask clarifying questions before the human finishes typing.
- **Effort Estimate**: M

---

## IDEA-356: "Request Dependency" Chaining
- **Category**: Feature
- **Problem**: Humans can be overwhelmed by a large number of concurrent requests that are actually dependent on each other in a specific sequence.
- **Proposed Solution**: Allow agents to specify that a request `depends_on` another request ID. The mobile app will hide dependent requests until their parent requests have been successfully resolved.
- **Business Value**: Reduces human cognitive load and ensures that approvals are handled in the correct logical order.
- **Effort Estimate**: M

---

## IDEA-357: "Local" SQLite Audit Log for Forensic Integrity
- **Category**: Security
- **Problem**: Relying solely on the central relay for audit logs is a risk if the relay is compromised or the data is tampered with.
- **Proposed Solution**: The CLI will maintain a local, append-only SQLite database of every request sent and response received, including cryptographic proofs of the human's signature.
- **Business Value**: Provides an immutable, local record of human decisions for forensic analysis and compliance auditing.
- **Effort Estimate**: S

---

## IDEA-358: "Agent-to-Agent" HITL (Recursive Supervision)
- **Category**: Integration
- **Problem**: In large agent swarms, a "Manager Agent" may need to approve the work of a "Worker Agent" using the same standard protocol used by humans.
- **Proposed Solution**: Allow an agent instance to register as a "Responder" (Human role). This enables recursive HITL where agents can supervise each other using the existing mobile-first protocol.
- **Business Value**: Enables scalable, hierarchical agent organizations with a unified and standardized supervision interface.
- **Effort Estimate**: L

---

## IDEA-359: "Predictive" Choice Suggestion
- **Category**: UX
- **Problem**: Humans often make the same repetitive choices for similar prompts, leading to decision fatigue and "autopilot" behavior.
- **Proposed Solution**: Use local interaction history to highlight or pre-select the choice the human is most likely to make based on previous patterns with that specific agent and prompt type.
- **Business Value**: Speeds up human decision-making and reduces the friction of repetitive manual approvals.
- **Effort Estimate**: M

---

## IDEA-360: "Protocol-Level" Compression for E2EE Payloads
- **Category**: Performance
- **Problem**: Large E2EE payloads (e.g., long log snippets or data snapshots) can be slow to transmit and consume significant data on mobile networks.
- **Proposed Solution**: Implement transparent Zstd or GZIP compression for payloads *before* they are encrypted by the proxy or SDK.
- **Business Value**: Reduces bandwidth usage and improves the responsiveness of data-intensive human interactions.
- **Effort Estimate**: S
