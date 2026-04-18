# Ideas Batch — hitl-cli (Batch 17)

## IDEA-241: "Semantic Prompt Optimization" for Human Clarity
- **Category**: UX
- **Problem**: AI agents often generate prompts that are too technical or verbose for a human to quickly digest on a mobile screen.
- **Proposed Solution**: Use a small local LLM or specialized template to summarize the prompt before sending it. Highlight the core decision needed and move technical details to a collapsible section.
- **Business Value**: Reduces human cognitive load and speeds up decision-making by presenting clearer, more actionable requests.
- **Effort Estimate**: M

---

## IDEA-242: "Predictive Human Availability" for Request Timing
- **Category**: Performance / UX
- **Problem**: Agents send requests when the human is busy or sleeping, leading to long wait times and stalled workflows.
- **Proposed Solution**: The mobile app tracks successful interaction windows and shares an anonymized heatmap with the relay. The SDK queries this to suggest optimal times for non-urgent requests.
- **Business Value**: Optimizes agent workflows by matching task execution with human availability, reducing total turnaround time.
- **Effort Estimate**: L

---

## IDEA-243: "Collaborative Human Review" (Shared Workspace)
- **Category**: Feature / Integration
- **Problem**: For complex tasks like code review, one human might want to see a colleague's opinion before deciding.
- **Proposed Solution**: Allow a "Shared Session" mode where multiple humans can view the same HITL request simultaneously. They can chat or vote in a mini-thread attached to the request.
- **Business Value**: Enables real-time team collaboration on critical AI-driven decisions without leaving the HITL workflow.
- **Effort Estimate**: L

---

## IDEA-244: "E2EE Proof-of-Work" for Spam Prevention
- **Category**: Security / Performance
- **Problem**: A compromised API key could be used to flood a human's phone with encrypted junk, wasting battery on decryption.
- **Proposed Solution**: Require every E2EE request to include a verifiable CPU-bound Proof-of-Work (PoW) token. The relay rejects any request without a valid token.
- **Business Value**: Hardens the system against DoS and battery-drain attacks targeting encrypted channels.
- **Effort Estimate**: M

---

## IDEA-245: "Agent-side" Input Validation (Client-side Schemas)
- **Category**: Tech Debt / Quality
- **Problem**: Humans often provide invalid input that the agent only catches after a network round-trip.
- **Proposed Solution**: Allow requests to specify a JSON Schema or regex for the response. The mobile app uses this to validate input locally before allowing the user to send it.
- **Business Value**: Eliminates invalid data round-trips, improving system robustness and user experience.
- **Effort Estimate**: S

---

## IDEA-246: "Context-Rich" Multi-media Attachments (Video/Audio)
- **Category**: Feature
- **Problem**: Some situations are better explained with a quick screen recording or a voice note than a long wall of text.
- **Proposed Solution**: Extend the SDK to support attaching small video or audio snippets (e.g., 10s MP4/AAC) to a request. The mobile app provides a native player for this context.
- **Business Value**: Provides humans with high-fidelity context for complex failures, leading to better and faster decisions.
- **Effort Estimate**: M

---

## IDEA-247: "Just-in-Time" SDK Telemetry Export
- **Category**: Observability
- **Problem**: When an SDK integration fails in the field, it's hard to retrieve the internal state of the library for debugging.
- **Proposed Solution**: Add an `export_diagnostics()` method that packages sanitized config, recent logs, and connection status into an E2EE payload sent to the human's phone.
- **Business Value**: Simplifies remote troubleshooting of complex SDK deployments without exposing secrets.
- **Effort Estimate**: S

---

## IDEA-248: "Shadow-Request" for Agent Consistency Verification
- **Category**: Quality / Security
- **Problem**: It is difficult to verify if an agent is consistently asking for (or skipping) human approvals correctly.
- **Proposed Solution**: Implement a "Shadow Mode" where the SDK periodically sends duplicate requests to a second audit human to verify the first human's decision.
- **Business Value**: Provides a high-assurance audit path for safety-critical autonomous systems.
- **Effort Estimate**: M

---

## IDEA-249: "Zero-Trust" Agent-to-Human Handshake (QR Pair)
- **Category**: Security
- **Problem**: Initial setup between a CLI and mobile app relies on the relay being honest during the OAuth flow.
- **Proposed Solution**: Add a `hitl-cli link` command that displays a QR code. The mobile app scans this to exchange E2EE keys out-of-band, bypassing the relay.
- **Business Value**: Achieves true "Zero-Trust" security by removing the relay from the initial identity-establishment phase.
- **Effort Estimate**: M

---

## IDEA-250: "Workflow-specific" Mobile Dashboard Widgets
- **Category**: UX
- **Problem**: Users with many agents find them all lumped together in one list, making organization difficult.
- **Proposed Solution**: Allow agents to define tags or workspaces. The mobile app creates specialized dashboard tabs or widgets based on these tags.
- **Business Value**: Improves user organization and task-switching efficiency in high-density HITL environments.
- **Effort Estimate**: S

---

## IDEA-251: "Automatic Proxy Discovery" via mDNS/Bonjour
- **Category**: Integration / UX
- **Problem**: Configuring tools like Claude Desktop to find a local proxy requires manual port and environment setup.
- **Proposed Solution**: The proxy advertises itself via mDNS. A helper command `hitl-cli proxy discover` automatically generates the correct configuration for MCP clients.
- **Business Value**: Reduces setup friction for new users and simplifies complex multi-tool environments.
- **Effort Estimate**: S

---

## IDEA-252: "Human-in-the-Loop" for Large-Scale Data Labeling
- **Category**: Feature / Performance
- **Problem**: Using HITL for thousands of small labeling tasks is too slow with the 1-request-per-notification model.
- **Proposed Solution**: A "Batch Request" mode that sends a set of tasks to the mobile app. The app shows a swipe interface for rapid-fire decisions, returning the whole batch.
- **Business Value**: Enables high-throughput, mobile-first data labeling and human-feedback-reinforcement-learning (RLHF) workflows.
- **Effort Estimate**: M

---

## IDEA-253: "Proxy-side" Request Interception & Rewriting
- **Category**: Security / Tech Debt
- **Problem**: Old or buggy SDKs might send insecure or malformed requests that should be corrected before hitting the network.
- **Proposed Solution**: Allow the local proxy to run interceptors that can sanitize, augment, or block requests from local agents based on local policy.
- **Business Value**: Provides a centralized point for enforcing local security and compliance across all agents on a machine.
- **Effort Estimate**: M

---

## IDEA-254: "Interactive-Wait" Terminal TUI
- **Category**: UX
- **Problem**: When waiting for a request, the terminal is static and provides little feedback to the developer.
- **Proposed Solution**: Replace the static wait with a rich TUI showing a live countdown, agent status, and a chat box for sending additional context to the human.
- **Business Value**: Improves the developer's experience during long wait times and provides better feedback about the interaction.
- **Effort Estimate**: S

---

## IDEA-255: "Agent-as-a-Proxy" (Chained HITL)
- **Category**: Feature / Architecture
- **Problem**: A human might want an AI's opinion *before* responding to another agent's request.
- **Proposed Solution**: Allow the human to "Forward" a request from the mobile app to another agent (MCP server) and see its response before finalizing their own.
- **Business Value**: Enables hierarchical collaboration where humans and AI agents work together in complex decision trees.
- **Effort Estimate**: L
