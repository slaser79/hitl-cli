# Ideas Batch — hitl-cli (Batch 16)

## IDEA-226: "Confidence-Threshold" Auto-Approval
- **Category**: Feature
- **Problem**: Humans are often asked for trivial approvals that an AI is 99.9% sure about, leading to notification fatigue and slower overall automation.
- **Proposed Solution**: Add a `confidence` parameter to `request_input`. If confidence exceeds a user-defined threshold in `config.json`, the SDK logs an "Auto-Approval" and proceeds without notifying the mobile app.
- **Business Value**: Dramatically reduces human interruptions for routine, high-confidence AI actions, increasing efficiency.
- **Effort Estimate**: M

---

## IDEA-227: "Interactive Debugger" Session Attachment
- **Category**: Feature
- **Problem**: When an agent fails, a static log snippet is often insufficient for a human to diagnose the root cause of the failure.
- **Proposed Solution**: Add a `debug_port` option to requests. If selected by the human on mobile, the CLI spawns a TUI debugger (like `pudb` or `web-pdb`) and provides a secure tunnel for the human to interact with the live process.
- **Business Value**: Accelerates incident resolution by giving humans direct, interactive access to failing agent processes.
- **Effort Estimate**: L

---

## IDEA-228: "Network-Agnostic" Sidecar Transport (Serial/Bluetooth)
- **Category**: Security
- **Problem**: Air-gapped or industrial systems may forbid any TCP/IP traffic, even to a local localhost proxy.
- **Proposed Solution**: Implement a transport layer for the `hitl-cli proxy` that can communicate over Serial (RS-232) or Bluetooth LE to a "bridge" device that has internet access.
- **Business Value**: Extends HITL capabilities to high-security or industrial environments where standard networking is prohibited.
- **Effort Estimate**: L

---

## IDEA-229: "Plug-and-Play" Enterprise Auth Providers (OIDC/SAML)
- **Category**: Integration
- **Problem**: Large organizations prefer using their own Identity Providers (IDP) rather than a third-party relay's built-in OAuth.
- **Proposed Solution**: Allow `hitl-cli login` to accept an `--idp-url` and `--client-id` to perform authentication against an internal corporate OIDC or SAML gateway.
- **Business Value**: Simplifies enterprise adoption by aligning with existing corporate security and identity policies.
- **Effort Estimate**: M

---

## IDEA-230: "Semantic Conflict" Detection across Agents
- **Category**: UX
- **Problem**: Multiple agents might independently ask for contradictory approvals (e.g., "Scale up" vs "Scale down") within a short window, leading to human confusion.
- **Proposed Solution**: Use local embedding-based semantic analysis to detect conflicting requests. The CLI flags these conflicts to the human: "Warning: Agent B is asking to Scale Down, but you just approved Agent A's Scale Up."
- **Business Value**: Prevents human errors in complex, multi-agent environments by providing cross-agent context.
- **Effort Estimate**: M

---

## IDEA-231: "Response-Consistency" Audit & Warning
- **Category**: Quality
- **Problem**: Humans are inconsistent; a user might approve a risk on Monday but reject the same risk on Tuesday, confusing the AI agent's long-term learning.
- **Proposed Solution**: The CLI maintains a local model of the user's "Response Policy." If a new response deviates significantly from historical patterns for similar prompts, the CLI asks for confirmation: "This is different from your usual response. Are you sure?"
- **Business Value**: Improves agent training and system reliability by encouraging consistent human decision-making.
- **Effort Estimate**: M

---

## IDEA-232: "Relay-Bypassing" Secure Tunnel for Large Assets
- **Category**: Feature
- **Problem**: Attaching large log files or database dumps to a HITL request can exceed relay payload limits or raise privacy concerns by putting sensitive data on a third-party server.
- **Proposed Solution**: The CLI can serve a one-time-use, E2EE-protected local HTTPS link for the human to download large assets directly from the agent's machine, bypassing the relay's storage entirely.
- **Business Value**: Enables sharing of massive context (gigabytes of logs) securely and efficiently during a HITL session without relay costs or risks.
- **Effort Estimate**: M

---

## IDEA-233: "Shell-Command" Interactive Diff Preview
- **Category**: Feature
- **Problem**: Humans are often asked to approve a shell command but can't see what it will *do* without running it themselves or reading complex script logic.
- **Proposed Solution**: For `request` calls involving commands, the CLI can generate a "diff" or "dry-run" output and attach it to the request. The mobile app renders this in a specialized "Code Diff" view for easier review.
- **Business Value**: Increases human confidence and safety when approving autonomous system commands.
- **Effort Estimate**: S

---

## IDEA-234: "Agent Identity" Request Signing
- **Category**: Security
- **Problem**: A malicious actor with access to the relay could potentially "spoof" a request from a trusted agent to a human, leading to unauthorized actions.
- **Proposed Solution**: The SDK automatically signs every request with a local Agent Private Key. The mobile app verifies this signature against the Agent's Public Key (shared during initial handshake) to guarantee authenticity.
- **Business Value**: Provides non-repudiation and prevents "Man-in-the-Middle" prompt injection at the relay level.
- **Effort Estimate**: M

---

## IDEA-235: "Environment-Aware" Priority Escalation
- **Category**: Feature
- **Problem**: A "Low" priority notification in Production is often more important than a "High" priority one in Staging, but agents don't always know the context.
- **Proposed Solution**: Allow the CLI to capture the `$NODE_ENV` or similar environment variable. The relay can be configured to automatically "boost" the priority of any request coming from a "Production" tagged environment.
- **Business Value**: Ensures that critical infrastructure issues always get the fastest human response, regardless of agent-assigned priority.
- **Effort Estimate**: S

---

## IDEA-236: "Global-Search" across Multi-Agent Audit Logs
- **Category**: Observability
- **Problem**: In an organization with dozens of agents, finding where a specific decision was made (e.g., "Who approved the firewall change?") is difficult and time-consuming.
- **Proposed Solution**: A `hitl-cli audit search --all-agents` command that aggregates and searches the local audit logs from all agents registered on the current machine or server.
- **Business Value**: Provides a centralized "Black Box" recorder for all autonomous actions across an entire workstation or server.
- **Effort Estimate**: M

---

## IDEA-237: "Just-in-Time" (JIT) Credential Injection
- **Category**: Security
- **Problem**: Agents often need temporary credentials (e.g., a one-time password or temporary AWS key) that should never be stored in environment variables or configuration files.
- **Proposed Solution**: A specialized `request_credential` SDK method that prompts the human to securely paste a secret on their mobile device. The secret is sent via E2EE and held only in the agent's memory for the duration of the task.
- **Business Value**: Improves security posture by eliminating the need for long-lived secrets in agent environments.
- **Effort Estimate**: M

---

## IDEA-238: "Recursive" HITL (Human-to-Human Handover)
- **Category**: Feature
- **Problem**: A human might receive a request they are not qualified to approve, requiring them to manually coordinate with another team member.
- **Proposed Solution**: Add a "Delegate" option to the mobile app. The human can select another registered user or team. The relay then routes the request to the new human, maintaining the agent's context and session.
- **Business Value**: Streamlines complex approvals by allowing humans to route tasks within their organization directly from the mobile app.
- **Effort Estimate**: L

---

## IDEA-239: "Low-Bandwidth" Mode for Edge/Satellite Links
- **Category**: Performance
- **Problem**: Using the HITL CLI over low-bandwidth or high-latency links (e.g., satellite, 2G) can be slow and expensive due to metadata overhead.
- **Proposed Solution**: Implement an optional "Low-Bandwidth" flag that aggressively compresses payloads, strips non-essential metadata, and uses a more compact serialization format (e.g., Protobuf) for relay communication.
- **Business Value**: Enables HITL usage in remote or field locations where connectivity is a premium resource.
- **Effort Estimate**: S

---

## IDEA-240: "Carbon-Aware" HITL Throttling
- **Category**: Performance / Sustainability
- **Problem**: Frequent non-critical HITL requests consume energy at both the client and relay level regardless of the current grid carbon intensity.
- **Proposed Solution**: Integrate with a carbon-intensity API (e.g., CarbonSDK). The CLI can be configured to delay or batch non-critical requests until the local energy grid has a high percentage of renewable energy.
- **Business Value**: Promotes corporate social responsibility (CSR) and reduces the carbon footprint of large-scale agent deployments.
- **Effort Estimate**: S
