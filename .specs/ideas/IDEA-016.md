# Ideas Batch — hitl-cli (Batch 22)

## IDEA-316: "Human-Presence" Heartbeat for High-Stakes Tasks
- **Category**: Security
- **Problem**: For extremely critical operations (e.g., deleting production databases), a single approval might not be enough if the human's device is compromised or left unattended.
- **Proposed Solution**: Implement a "Presence Heartbeat" requirement. The human must maintain active focus on the HITL app (e.g., holding a button or responding to periodic "Still here?" prompts) for the duration of the high-stakes task. If the heartbeat is lost, the task is immediately paused.
- **Business Value**: Provides an additional layer of safety and non-repudiation for high-risk autonomous actions.
- **Effort Estimate**: M

---

## IDEA-317: "Agent Voice" Audio Prompts
- **Category**: UX
- **Problem**: Busy developers might miss a notification on their phone if it's in their pocket or across the room.
- **Proposed Solution**: Use text-to-speech on the mobile app to read the prompt aloud when it arrives. Users can configure specific "Voices" for different agents to quickly identify which system is requesting attention.
- **Business Value**: Increases responsiveness and reduces latency for human-in-the-loop interactions.
- **Effort Estimate**: S

---

## IDEA-318: "Conflict-Free" Multi-Human Approval (M-of-N)
- **Category**: Integration
- **Problem**: Some organizational policies require multiple people to approve a change, but current HITL requests are typically 1-to-1.
- **Proposed Solution**: Support "Consensus Groups" where a request is sent to N humans, and requires M approvals to proceed. The CLI tracks the consensus state and only returns the final result once the threshold is met.
- **Business Value**: Enables HITL to support enterprise-level compliance and governance workflows.
- **Effort Estimate**: L

---

## IDEA-319: "Smart Redaction" for Log Streams
- **Category**: Security
- **Problem**: Agents often send full log outputs to the human for debugging, which might contain sensitive environment variables or internal paths.
- **Proposed Solution**: An intelligent log filter that automatically identifies and redacts common sensitive patterns (API keys, passwords, IPs) from attached logs before they leave the agent's environment.
- **Business Value**: Enhances security posture by preventing accidental data leakage during remote debugging.
- **Effort Estimate**: M

---

## IDEA-320: "Auto-Resume" on Infrastructure Recovery
- **Category**: Performance
- **Problem**: If the agent's host crashes while waiting for human input, the entire task state is lost, requiring a full restart.
- **Proposed Solution**: Implement local state persistence for pending requests. If the agent process restarts, it can "Reconnect" to existing requests on the relay and resume waiting for the human's response.
- **Business Value**: Increases reliability and efficiency of long-running autonomous workflows.
- **Effort Estimate**: M

---

## IDEA-321: "Human-in-the-Loop" Git Rebase Assistant
- **Category**: Feature
- **Problem**: AI agents often struggle with complex git merge conflicts, leading to broken builds or lost work.
- **Proposed Solution**: A specialized HITL mode for merge conflicts. When a conflict occurs, the agent sends the conflicting hunks to the mobile app's diff editor (IDEA-315). The human resolves the conflict on their phone, and the agent applies the resolution.
- **Business Value**: Significantly improves agent autonomy in collaborative development environments.
- **Effort Estimate**: L

---

## IDEA-322: "Interactive Shell" Snippet Executor
- **Category**: UX
- **Problem**: Sometimes a human needs to run a quick diagnostic command on the agent's host to understand why a request was made, but doesn't want to open a full SSH session.
- **Proposed Solution**: Allow the human to send "Diagnostic Snippets" (e.g., `df -h`, `free -m`) from the mobile app. The agent executes the snippet in a restricted environment and sends the output back to the app.
- **Business Value**: Provides quick situational awareness for human operators without full handover.
- **Effort Estimate**: M

---

## IDEA-323: "Visual Verification" with OCR
- **Category**: Feature
- **Problem**: For UI-testing agents, a screenshot is good, but the human still has to manually verify that the correct text is present.
- **Proposed Solution**: The agent performs local OCR on the screenshot and highlights specific text regions in the HITL app. The human can "Click" on the highlighted text to confirm its presence/correctness.
- **Business Value**: Automates and simplifies the verification of visual tasks for humans.
- **Effort Estimate**: L

---

## IDEA-324: "Agent Reputation" Dashboard
- **Category**: Performance
- **Problem**: In a system with many agents, it's hard to tell which ones are reliable and which ones are "hallucination-prone" or overly chatty.
- **Proposed Solution**: Track "Approval/Rejection" rates for each agent identity. A local dashboard shows the reputation score of each agent, helping the human decide how much to trust a specific request.
- **Business Value**: Provides visibility into agent performance and helps identify buggy or misaligned autonomous systems.
- **Effort Estimate**: S

---

## IDEA-325: "Contextual Documentation" Deep-Links
- **Category**: UX
- **Problem**: A human might receive a request about an obscure internal error code and have no idea what it means or how to handle it.
- **Proposed Solution**: Allow agents to attach "Help Links" to requests. The mobile app renders these as clickable buttons that open the relevant internal documentation or wiki page directly.
- **Business Value**: Reduces human cognitive load and speeds up the decision-making process.
- **Effort Estimate**: S

---

## IDEA-326: "Predictive Human" Response Mocking
- **Category**: Tech Debt
- **Problem**: Testing complex HITL workflows requires a real human to be available, which slows down CI/CD and developer testing.
- **Proposed Solution**: A "Mock Human" mode for the CLI. Developers can provide a JSON file of "Expected Prompts" and "Automated Responses." When the agent makes a matching request, the CLI returns the mock response instantly.
- **Business Value**: Speeds up development and enables reliable automated testing of HITL logic.
- **Effort Estimate**: M

---

## IDEA-327: "Secure Enclave" Key Storage for E2EE
- **Category**: Security
- **Problem**: Storing E2EE private keys in `~/.hitl/` is vulnerable to local file system attacks.
- **Proposed Solution**: Support for hardware-backed key storage (e.g., Apple Secure Enclave, Android StrongBox, or TPM). The E2EE keys are generated and stored in the hardware, ensuring they can never be extracted.
- **Business Value**: Provides world-class security for confidential human-agent interactions.
- **Effort Estimate**: L

---

## IDEA-328: "Agent-Initiated" Screen Sharing
- **Category**: Feature
- **Problem**: Sometimes a text description and a screenshot aren't enough to explain a complex UI bug or interaction sequence.
- **Proposed Solution**: The agent can initiate a temporary "Screen Stream" of its virtual display to the mobile app. The human watches the agent work in real-time to identify where it's going wrong.
- **Business Value**: Dramatically improves the ability to debug complex visual agents.
- **Effort Estimate**: L

---

## IDEA-329: "Smart Notification" Grouping (De-duplication)
- **Category**: UX
- **Problem**: If 10 agents all hit the same error simultaneously, the human receives 10 identical notifications, which is annoying and redundant.
- **Proposed Solution**: The relay (or a local CLI aggregator) groups identical notifications within a short time window. The human sees "10 agents reported error X" instead of 10 individual pings.
- **Business Value**: Reduces "notification fatigue" and keeps the human focused on unique issues.
- **Effort Estimate**: M

---

## IDEA-330: "One-Click" Remediation Actions
- **Category**: UX
- **Problem**: Approving a fix often requires the human to type a response or select a choice, even if the fix is obvious.
- **Proposed Solution**: Support for "Action Buttons" in notifications. An agent can send a request like "Disk space low. [Clean Logs] [Increase Volume] [Ignore]." The human performs the fix with a single tap.
- **Business Value**: Minimizes the time and effort required for human intervention in routine maintenance tasks.
- **Effort Estimate**: S
