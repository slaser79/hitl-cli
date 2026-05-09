# Ideas Batch — hitl-cli (Batch 19)

## IDEA-271: "Human Presence" Heartbeat Integration
- **Category**: Performance / UX
- **Problem**: Agents often send requests when the human is offline or their device is unreachable, causing the agent to wait indefinitely for a response that won't come soon.
- **Proposed Solution**: The SDK periodically checks a lightweight "Human Presence" status from the relay before initiating a full request. If the human is offline, the agent can choose to defer the task or try an alternative path.
- **Business Value**: Increases agent autonomy and efficiency by avoiding "dead-end" waits for unreachable humans.
- **Effort Estimate**: S

---

## IDEA-272: "Dry-Run" SDK Mocking Engine
- **Category**: DX / Tech Debt
- **Problem**: Testing agent logic that requires human input is difficult and slow, often requiring manual intervention during test runs or complex custom mocks.
- **Proposed Solution**: Add a built-in `MockHITL` transport to the SDK that can be configured with a script of "pre-recorded" human responses. This allows for fully automated, deterministic testing of complex HITL workflows.
- **Business Value**: Accelerates development cycles and improves test coverage for human-in-the-loop applications.
- **Effort Estimate**: S

---

## IDEA-273: Multi-Channel Escalation (Slack/Discord)
- **Category**: Integration / Reliability
- **Problem**: If the human misses a critical mobile notification, a time-sensitive agent workflow might stall or fail.
- **Proposed Solution**: Allow users to configure secondary notification channels (like Slack or Discord webhooks) in their profile. If a request remains unanswered after a timeout, the relay automatically escalates it to the secondary channel.
- **Business Value**: Reduces critical path downtime and ensures important requests aren't missed.
- **Effort Estimate**: M

---

## IDEA-274: "Request Bundling" for CLI Efficiency
- **Category**: Performance / UX
- **Problem**: Running multiple `hitl-cli` commands in a script results in a barrage of individual notifications, leading to "notification fatigue" for the human.
- **Proposed Solution**: Implement a `hitl-cli bundle` context manager or a command-line flag that groups multiple requests into a single, multi-step notification on the mobile app.
- **Business Value**: Improves the human experience by reducing interruption frequency and providing better context for grouped tasks.
- **Effort Estimate**: M

---

## IDEA-275: Mobile-Native Image Markup and Annotation
- **Category**: UX / Feature
- **Problem**: Describing a visual issue (e.g., a UI bug or a misaligned physical part) in text is difficult. Humans often need to point exactly where the problem is.
- **Proposed Solution**: Extend the mobile app to support "Annotation Requests." When an agent sends an image, the human can use native drawing tools to circle, point, or highlight areas before returning the response.
- **Business Value**: Enables high-precision visual feedback, expanding the use cases for HITL in QA and industrial monitoring.
- **Effort Estimate**: L

---

## IDEA-276: "Agent Personality" and Branding
- **Category**: UX
- **Problem**: Users with many agents find it hard to distinguish between them at a glance, as every request looks the same in the notification list.
- **Proposed Solution**: Allow agents to register metadata including a name, avatar URL, and a "bio" or "purpose." This branding is prominently displayed in the mobile app and notification banners.
- **Business Value**: Enhances user familiarity and trust by giving each autonomous agent a distinct, recognizable identity.
- **Effort Estimate**: S

---

## IDEA-277: Encrypted On-Demand Log Tailing
- **Category**: Security / UX
- **Problem**: When a human is asked to approve a fix, they often want to see the most recent logs to verify the context, but sending logs by default is noisy and potentially insecure.
- **Proposed Solution**: Add a "Request Logs" button to the mobile app UI. When tapped, the agent securely tails the last 50-100 lines of its local logs, encrypts them using the session's E2EE key, and sends them to the app.
- **Business Value**: Provides secure, real-time technical context without cluttering the primary notification.
- **Effort Estimate**: M

---

## IDEA-278: "Human-in-the-Loop" Cron Wrapper
- **Category**: Integration / Reliability
- **Problem**: Traditional cron jobs often fail silently or send cryptic emails that are ignored, leading to long-standing production issues.
- **Proposed Solution**: A `hitl-cli cron-wrap` tool that executes any shell command and automatically triggers a HITL request if the command fails, allows the human to "Retry", "Ignore", or "Investigate".
- **Business Value**: Transforms passive alerting into active, mobile-first incident management for legacy systems.
- **Effort Estimate**: S

---

## IDEA-279: Global "Do Not Disturb" SDK Compliance
- **Category**: UX
- **Problem**: Agents might interrupt humans during sleep or meetings, leading to frustration and poorly considered "quick" responses.
- **Proposed Solution**: The SDK queries the human's "DND" status from the relay (configured in the mobile app) before sending requests. If DND is active, non-urgent requests are automatically queued until the window ends.
- **Business Value**: Respects human boundaries and improves decision quality by ensuring humans are attentive when responding.
- **Effort Estimate**: S

---

## IDEA-280: Local "Auto-Approve" Policy Engine
- **Category**: Feature / Security
- **Problem**: Many routine approvals (e.g., "Allow read-only access to staging") are redundant but still consume human time and attention.
- **Proposed Solution**: Implement a local policy engine in `hitl-cli` that allows users to define rules for automatic responses based on agent identity, prompt content, or request type.
- **Business Value**: Saves significant human time by automating low-risk, high-frequency approvals while maintaining an audit trail.
- **Effort Estimate**: M

---

## IDEA-281: Browser Extension for Desktop HITL
- **Category**: Integration / UX
- **Problem**: Developers who are already working in their browser (e.g., in a cloud IDE or monitoring dashboard) find it disruptive to switch to their mobile device for every approval.
- **Proposed Solution**: An official Chrome/Firefox extension that mirrors the HITL queue and allows humans to respond to requests directly from their browser's toolbar.
- **Business Value**: Improves developer productivity by providing a more integrated, cross-platform interaction experience.
- **Effort Estimate**: L

---

## IDEA-282: "Session Recording" and Playback for Auditing
- **Category**: Observability / Security
- **Problem**: For sensitive operations, simply knowing *that* a human approved isn't enough; auditors need to see the exact context the human was shown at the moment of approval.
- **Proposed Solution**: The CLI can optionally record the full state of every HITL interaction (prompt, choices, attachments, time-to-respond) into a signed, tamper-evident audit file.
- **Business Value**: Provides a high-fidelity audit trail for compliance-heavy environments.
- **Effort Estimate**: M

---

## IDEA-283: Local HTTP Control API for `hitl-cli`
- **Category**: Integration
- **Problem**: Integrating other local tools (e.g., a Go service or a Rust CLI) with HITL currently requires spawning a shell process for `hitl-cli`, which is inefficient and hard to manage.
- **Proposed Solution**: A `hitl-cli daemon` mode that exposes a local-only, authenticated HTTP API. Other local applications can then send requests to the mobile app via simple HTTP calls.
- **Business Value**: Simplifies the development of multi-language HITL systems and improves performance for high-frequency local integrations.
- **Effort Estimate**: M

---

## IDEA-284: "Hardware Security Key" Biometric MFA
- **Category**: Security
- **Problem**: For extremely sensitive actions (like moving funds or deleting production databases), a mobile tap might not be considered "strong" enough authentication.
- **Proposed Solution**: Add support for FIDO2/WebAuthn. The mobile app requires the human to tap a physical security key (like a YubiKey) or provide a biometric scan (FaceID/TouchID) before the response is signed and sent.
- **Business Value**: Enables HITL for high-stakes financial and infrastructure operations that require the highest level of assurance.
- **Effort Estimate**: L

---

## IDEA-285: Contextual "Help Me Decide" LLM Assistant
- **Category**: UX
- **Problem**: Agents sometimes send complex technical prompts that a human on a mobile device might not fully understand without more background.
- **Proposed Solution**: A "Help" button in the mobile app that forwards the request context to a designated LLM (e.g., Claude) to provide a plain-English explanation of why the agent is asking and what the implications of each choice are.
- **Business Value**: Democratizes complex agent orchestration by allowing non-technical humans to make informed decisions.
- **Effort Estimate**: M
