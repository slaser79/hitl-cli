# Ideas Batch — hitl-cli (Batch 18)

## IDEA-256: "Verifiable Agent Origin" (Security)
- **Category**: Security
- **Problem**: Humans can't be sure which specific agent or process is requesting input, risking "Agent Spoofing" where a malicious process mimics a trusted agent.
- **Proposed Solution**: Each agent instance generates a unique session key during login. The mobile app displays a "Verified" badge and agent metadata (PID, host, start time) signed by this key.
- **Business Value**: Protects against malicious agents and increases human trust in the autonomous system.
- **Effort Estimate**: M

---

## IDEA-257: "Streaming Live Logs" to Mobile (UX)
- **Category**: UX
- **Problem**: Notifications often report failure but lack the specific context (e.g., error logs) needed for a human to diagnose and decide on a fix from their phone.
- **Proposed Solution**: A `hitl-cli notify-stream` command that sends a rolling window of logs to the mobile app in real-time or as a follow-up to a failure notification.
- **Business Value**: Reduces "Time-to-Resolution" by providing immediate technical context on the mobile device.
- **Effort Estimate**: M

---

## IDEA-258: "Conditional Hook Execution" (Integration)
- **Category**: Integration
- **Problem**: Current hooks (like `review-and-continue`) execute on every stop, even when no significant changes occurred, leading to unnecessary human interruptions.
- **Proposed Solution**: Add condition flags to hooks (e.g., `--if-modified <glob>`, `--if-exit-code <n>`) to only trigger the HITL request when specific criteria are met.
- **Business Value**: Minimizes human fatigue by filtering out non-critical or redundant interaction points.
- **Effort Estimate**: S

---

## IDEA-259: "Adaptive SDK Wait-Strategy" (Performance)
- **Category**: Performance
- **Problem**: Fixed polling intervals for human responses are either too slow (wasting time) or too aggressive (wasting battery and API quota).
- **Proposed Solution**: Implement an adaptive polling algorithm in the SDK that speeds up when a human is known to be active and slows down during quiet periods (e.g., nighttime).
- **Business Value**: Optimizes the balance between responsiveness and resource consumption.
- **Effort Estimate**: S

---

## IDEA-260: "HITL-CLI" Git Credential Helper (Integration)
- **Category**: Integration
- **Problem**: Managing SSH keys or personal access tokens for Git is a constant friction point for developers and a security risk if stored unencrypted.
- **Proposed Solution**: A Git credential helper that uses `hitl-cli` to request a one-time approval on the human's mobile device for every `git push` or `git pull` operation.
- **Business Value**: Provides a seamless, mobile-first 2FA experience for the most common developer workflow.
- **Effort Estimate**: M

---

## IDEA-261: "Dynamic Choice Refresh" (Feature)
- **Category**: Feature
- **Problem**: Choices provided in a request are static. If the environment changes while waiting, the human might need to pick from an updated set of options.
- **Proposed Solution**: Allow the mobile app to "Request Update" from the agent, triggering a callback in the SDK to provide a fresh list of choices without re-sending the entire notification.
- **Business Value**: Enables more accurate decision-making in fast-moving environments.
- **Effort Estimate**: M

---

## IDEA-262: "Geo-Fenced Approval Constraints" (Security)
- **Category**: Security
- **Problem**: Extremely sensitive actions (e.g., production database wipes) should ideally only be approved when the human is in a secure, known location.
- **Proposed Solution**: Add optional geo-fencing metadata to HITL requests. The mobile app verifies the human's GPS coordinates against the constraint before enabling the "Approve" button.
- **Business Value**: Adds a physical layer of security to high-risk digital operations.
- **Effort Estimate**: M

---

## IDEA-263: "Mobile Visualization" (Vega-Lite support) (UX)
- **Category**: UX
- **Problem**: Humans struggle to interpret raw data or trends sent as text, making it hard to approve scaling or budget changes.
- **Proposed Solution**: Support for rendering simple, interactive charts on the mobile app using the Vega-Lite specification sent via the CLI or SDK.
- **Business Value**: Empowers humans to make data-driven decisions quickly from their mobile device.
- **Effort Estimate**: L

---

## IDEA-264: "Voice-to-JSON" Response Parsing (UX)
- **Category**: UX
- **Problem**: Typing structured data (like a configuration JSON) on a mobile keyboard is error-prone and frustrating.
- **Proposed Solution**: Use the mobile app's voice-to-text combined with a small LLM to parse the human's spoken response into the specific JSON schema requested by the agent.
- **Business Value**: Lowers the barrier for providing complex structured input on the go.
- **Effort Estimate**: M

---

## IDEA-265: "Agent-to-Agent" Review Delegation (Architecture)
- **Category**: Architecture
- **Problem**: A human might be asked for a technical review that they'd rather have another AI agent perform first.
- **Proposed Solution**: A "Delegate to Agent" response type in the mobile app that forwards the request context to another specified MCP server for initial analysis.
- **Business Value**: Enables complex, multi-agent collaborative workflows with humans acting as high-level orchestrators.
- **Effort Estimate**: L

---

## IDEA-266: "HITL-CLI" Docker Extension (UX)
- **Category**: UX
- **Problem**: Monitoring the HITL status of agents running inside Docker containers requires digging through container logs.
- **Proposed Solution**: A Docker Desktop extension that visualizes the "HITL Health" of all local containers and provides a centralized UI for pending requests.
- **Business Value**: Simplifies the local development and debugging experience for containerized agents.
- **Effort Estimate**: M

---

## IDEA-267: "Memory-Resident" E2EE Keys (Security)
- **Category**: Security
- **Problem**: End-to-End Encryption keys stored on disk are vulnerable if the developer's laptop is stolen or compromised.
- **Proposed Solution**: A "Volatile Mode" where E2EE keys are kept only in memory and are derived from a user-provided passphrase entered at the start of each session.
- **Business Value**: Provides a higher security tier for organizations with strict compliance requirements.
- **Effort Estimate**: S

---

## IDEA-268: "Human-Cost" Budgeting SDK (Performance)
- **Category**: Performance
- **Problem**: Autonomous agents may over-rely on human input, leading to high "human cognitive debt" and operational inefficiencies.
- **Proposed Solution**: An SDK feature that tracks the estimated "cost" (in minutes or dollars) of each request and allows setting a "Human Budget" that the agent cannot exceed.
- **Business Value**: Forces agents to prioritize their requests and respect the human's time.
- **Effort Estimate**: M

---

## IDEA-269: "One-Time-Sign" Challenge/Response (Security)
- **Category**: Security
- **Problem**: Long-lived OAuth tokens can be abused if intercepted.
- **Proposed Solution**: For high-value requests, implement a cryptographic challenge-response where the human must sign a unique nonce with their mobile device's secure enclave for each approval.
- **Business Value**: Ensures that critical approvals are cryptographically linked to a specific physical device and a specific point in time.
- **Effort Estimate**: L

---

## IDEA-270: "Interactive-Shell" inside HITL (Feature)
- **Category**: Feature
- **Problem**: Sometimes "Yes/No" isn't enough. You want to tell the agent to "run this command instead".
- **Proposed Solution**: A "Terminal" choice type that opens a mini-terminal in the mobile app, allowing the human to type a single command that is then executed by the agent and its output returned to the mobile app for further review.
- **Business Value**: Enables deep, interactive troubleshooting of remote agents directly from the mobile app.
- **Effort Estimate**: L
