# Ideas Batch — hitl-cli (Batch 21)

## IDEA-301: "Agent-to-Agent" Peer Verification
- **Category**: Architecture
- **Problem**: Some tasks are too routine for a human but too risky for a single agent. A second opinion from a different model or agent instance could prevent common hallucinations.
- **Proposed Solution**: Implement a "Peer Verification" protocol where an agent sends its plan to a second agent via `hitl-cli`. If the second agent approves, the task proceeds; if they disagree, it is escalated to a human with both agents' reasoning.
- **Business Value**: Reduces human workload by delegating low-level verification to secondary agents.
- **Effort Estimate**: M

---

## IDEA-302: "Interactive Debugger" Breakpoint over HITL
- **Category**: Feature
- **Problem**: When an autonomous script fails in a remote environment, developers have to manually recreate the state to debug it, which is time-consuming.
- **Proposed Solution**: A `hitl.breakpoint()` SDK method that, when hit, pauses the script and sends a rich interaction request to the human. The mobile app shows the local variables and stack trace, allowing the human to "Inject" a value or "Skip" the failing line.
- **Business Value**: Enables "Live Debugging" of remote agents, significantly reducing MTTR (Mean Time To Repair).
- **Effort Estimate**: L

---

## IDEA-303: "Proof of Decision" Blockchain Notarization
- **Category**: Security
- **Problem**: In high-compliance industries (finance, healthcare), a simple database log of human approvals isn't sufficient for non-repudiation and immutable auditing.
- **Proposed Solution**: Integrate with a lightweight notarization service (e.g., Tierion or a private ledger). Every human approval generates a cryptographic receipt that is anchored to a blockchain, providing immutable proof of who authorized what.
- **Business Value**: Provides enterprise-grade auditability and regulatory compliance for AI-driven operations.
- **Effort Estimate**: L

---

## IDEA-304: Automatic "Contextual Git" Attachment
- **Category**: UX
- **Problem**: Humans often receive requests like "Can I fix this bug?" without the necessary context of what files were changed or what the current diff looks like.
- **Proposed Solution**: A built-in feature that detects if the agent is running in a git repo. It automatically attaches the `git diff` and the last 3 commit messages to every HITL request as "System Context" without extra code from the developer.
- **Business Value**: Improves decision speed and accuracy by providing relevant context automatically.
- **Effort Estimate**: S

---

## IDEA-305: "Agent Handover" Remote Shell Session
- **Category**: Feature
- **Problem**: Agents can get stuck on interactive prompts or edge cases they aren't programmed to handle (e.g., an unexpected `y/n` prompt from an old tool).
- **Proposed Solution**: A "Remote Shell" capability in the mobile app. When an agent is stuck, the human can initiate a temporary, secure SSH-like session directly through the relay to the agent's environment to fix the immediate blocker.
- **Business Value**: Prevents agent "deadlocks" and allows for quick manual intervention without full context switching.
- **Effort Estimate**: L

---

## IDEA-306: "Agent Quota" Governance Policy
- **Category**: Integration
- **Problem**: Autonomous agents can be "chatty," and a bugged loop could generate thousands of notifications, overwhelming the human and wasting resources.
- **Proposed Solution**: Define a per-agent `quota.yaml` policy (e.g., max 10 requests per hour, max 50 per day). The CLI enforces this locally, returning an error to the script if the quota is exceeded, preventing "notification storms."
- **Business Value**: Provides operational guardrails and prevents "attention exhaustion" for human operators.
- **Effort Estimate**: S

---

## IDEA-307: "Semantic Search" for Local Interaction Memory
- **Category**: Performance
- **Problem**: With hundreds of past interactions, finding "that one time we approved the database migration" using keyword search is slow and inaccurate.
- **Proposed Solution**: Use a local embedding model (like `all-MiniLM-L6-v2`) to index the `history.jsonl` file. The command `hitl-cli history find` then performs a semantic vector search to find conceptually related past decisions.
- **Business Value**: Turns past interactions into a "Knowledge Base" for both humans and future agents.
- **Effort Estimate**: M

---

## IDEA-308: "Air-Gapped" Local Relay Mode
- **Category**: Architecture
- **Problem**: Defense and high-security sectors cannot use a cloud-based relay due to data sovereignty and physical air-gap requirements.
- **Proposed Solution**: A "Self-Hostable" version of the HITL Relay packaged as a Docker container or NixOS module. The CLI can be configured to point to this local instance via the `HITL_SERVER_URL` env var.
- **Business Value**: Expands the market to high-security, regulated, and industrial air-gapped environments.
- **Effort Estimate**: L

---

## IDEA-309: "Sensitive Data" Local Redaction Filter
- **Category**: Security
- **Problem**: Agents might accidentally include secrets, PII, or internal tokens in their prompts, which then get sent to the relay and the human's mobile device.
- **Proposed Solution**: A local "DLP" (Data Loss Prevention) filter that scans outgoing prompts for patterns like AWS keys, email addresses, or credit card numbers, redacting them before they are encrypted and sent.
- **Business Value**: Reduces security risk and ensures compliance with data protection regulations (GDPR, CCPA).
- **Effort Estimate**: S

---

## IDEA-310: "Time-of-Day" Availability Policies
- **Category**: UX
- **Problem**: Agents run 24/7, but humans need to sleep. Receiving non-critical refactoring requests at 4 AM is a poor user experience.
- **Proposed Solution**: Allow users to configure "Work Hours" in the CLI. Non-emergency requests (marked with a new `--priority` flag) are queued locally and only dispatched when the human enters their active window.
- **Business Value**: Improves developer well-being and long-term engagement with the HITL platform.
- **Effort Estimate**: S

---

## IDEA-311: "Panic Button" Emergency Kill-Switch
- **Category**: Security
- **Problem**: If an agent starts performing destructive actions, the human needs a way to immediately stop it, even if they aren't currently at their computer.
- **Proposed Solution**: A "Panic" button in the mobile app that, when pressed, sends a "SIGKILL" signal to the agent's host process (via the E2EE proxy) and cancels all pending requests.
- **Business Value**: Provides a critical safety mechanism for managing autonomous AI agents.
- **Effort Estimate**: M

---

## IDEA-312: "Interactive Charts" for Data Analysis
- **Category**: UX
- **Problem**: Agents often need human help analyzing performance data or trends, but sending raw numbers is hard to digest on a mobile screen.
- **Proposed Solution**: Support for JSON-based chart definitions (e.g., Vega-Lite) in the HITL payload. The mobile app renders these as interactive, touch-enabled charts, allowing the human to explore data before approving an action.
- **Business Value**: Enables data-driven decision-making for AI-assisted monitoring and analytics.
- **Effort Estimate**: M

---

## IDEA-313: "Custom Prompt Templates" with YAML Context
- **Category**: Feature
- **Problem**: Reusing complex prompt structures across different scripts leads to code duplication and inconsistent human experiences.
- **Proposed Solution**: Support for `.hitl/templates/*.yaml` files. The CLI can invoke a template by name (`hitl-cli request --template deploy_approval --var env=prod`) and automatically fill in the placeholders.
- **Business Value**: Standardizes human-agent interactions across an entire organization.
- **Effort Estimate**: S

---

## IDEA-314: "Live Camera Feed" for Physical Agents
- **Category**: Feature
- **Problem**: For agents controlling physical robots or hardware sensors, text descriptions might not be enough to judge a situation.
- **Proposed Solution**: Establish a low-latency WebRTC stream from the agent's host (e.g., Raspberry Pi) directly to the mobile app when a request is made. The human views the live feed to make an informed decision.
- **Business Value**: Enables safe and effective HITL control for robotics and IoT systems.
- **Effort Estimate**: L

---

## IDEA-315: "Interactive Mobile" Diff Editor
- **Category**: UX
- **Problem**: Approving code changes with a simple "Yes/No" is often too binary. Sometimes a human just wants to tweak one line before allowing the agent to proceed.
- **Proposed Solution**: Send the proposed diff to the mobile app, which renders it in a specialized, mobile-optimized code editor. The human can make minor edits and send the "Corrected" diff back for the agent to apply.
- **Business Value**: Enables collaborative "Human-in-the-Loop" refinement of autonomous output.
- **Effort Estimate**: L
