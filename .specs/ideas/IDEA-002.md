# Ideas Batch — hitl-cli (Batch 8)

## IDEA-106: HITL-Proxy for Jupyter/IPython Notebooks

- **Category**: Integration
- **Problem**: Data scientists working in Jupyter notebooks often need to pause long-running training or processing jobs for human review (e.g., "Is this loss curve acceptable?"). Currently, they have to manually integrate the SDK.
- **Proposed Solution**: An IPython magic command `%hitl_request` and a background listener that allows seamless human-in-the-loop interaction directly within notebook cells without blocking the kernel.
- **Business Value**: Expands the user base to the data science community and improves the efficiency of high-resource computing tasks.
- **Effort Estimate**: M

---

## IDEA-107: Progressive Web App (PWA) Fallback for Approvals

- **Category**: UX
- **Problem**: New or temporary users might not have the mobile app installed, leading to missed or delayed critical approvals.
- **Proposed Solution**: Generate a unique, short-lived PWA link that can be opened in any mobile browser to provide the same approval interface as the native app.
- **Business Value**: Increases the success rate and speed of approvals by removing the app-installation barrier.
- **Effort Estimate**: L

---

## IDEA-108: Biometric Challenge for High-Risk Requests

- **Category**: Security
- **Problem**: If a user's phone is unlocked, someone else could potentially approve a sensitive request (e.g., a large fund transfer or production deploy).
- **Proposed Solution**: Add a `--biometric` flag to `request` that forces the mobile app to perform a FaceID/Fingerprint check before allowing the human to respond.
- **Business Value**: Provides enterprise-grade security for the most critical operations.
- **Effort Estimate**: M

---

## IDEA-109: Slack & Discord Notification Bridge

- **Category**: Integration
- **Problem**: While HITL is mobile-first, teams often want visibility into what requests are pending or completed within their primary communication channels.
- **Proposed Solution**: A built-in integration that mirrors HITL notifications and request status updates to configured Slack or Discord webhooks.
- **Business Value**: Improves team coordination and transparency around human-in-the-loop processes.
- **Effort Estimate**: S

---

## IDEA-110: Intelligent Notification Bundling

- **Category**: Performance
- **Problem**: High-frequency automated systems can spam the user with dozens of push notifications in a short time, leading to "alert fatigue."
- **Proposed Solution**: Implement server-side or client-side logic to group multiple non-urgent notifications into a single "digest" push if they occur within a specific window.
- **Business Value**: Protects the user from burnout and ensures that truly urgent alerts stand out.
- **Effort Estimate**: M

---

## IDEA-111: Custom Branding & Themes for Requests

- **Category**: UX
- **Problem**: All HITL requests look identical, making it hard for users to quickly distinguish between different projects or urgency levels.
- **Proposed Solution**: Allow agents to specify an accent color, icon, or "brand name" in the `request` payload to customize how the prompt is rendered on the mobile device.
- **Business Value**: Improves user recognition and allows companies to provide a branded experience for internal tools.
- **Effort Estimate**: S

---

## IDEA-112: Geofencing for Sensitive Approvals

- **Category**: Security
- **Problem**: Some corporate policies require that certain actions only be approved from a secure location (e.g., the office).
- **Proposed Solution**: Add a `--require-location` flag that checks the mobile device's GPS against a configured geofence before allowing a response to be sent.
- **Business Value**: Enables compliance with strict physical security requirements for high-stakes environments.
- **Effort Estimate**: L

---

## IDEA-113: Zapier & Make.com (Integromat) Integration

- **Category**: Integration
- **Problem**: Users want to trigger complex secondary workflows (e.g., "Add to spreadsheet", "Update Jira") based on HITL responses without writing custom code.
- **Proposed Solution**: Provide official connectors for Zapier and Make.com that treat HITL responses as "triggers" for downstream automation.
- **Business Value**: Dramatically lowers the technical bar for building complex, multi-service HITL workflows.
- **Effort Estimate**: M

---

## IDEA-114: Voice-to-Text Responses for Mobile

- **Category**: Feature
- **Problem**: Users are often "on the go" and might find it cumbersome to type long, detailed responses to complex prompts on a mobile keyboard.
- **Proposed Solution**: Enable a microphone icon in the mobile app for "Rich Text" prompts, allowing the user to dictate their response, which is then transcribed and sent back to the agent.
- **Business Value**: Improves the quality and speed of human feedback in mobile-only scenarios.
- **Effort Estimate**: M

---

## IDEA-115: Conditional Logic for Multi-Step Requests

- **Category**: Feature
- **Problem**: Complex human interactions often require a "branching" flow (e.g., if 'Yes', ask 'When?'). Currently, this requires multiple round-trips from the agent.
- **Proposed Solution**: Allow the agent to send a "request tree" where subsequent questions are pre-loaded and revealed based on the human's previous choices.
- **Business Value**: Reduces latency and improves the user experience for complex, structured data collection.
- **Effort Estimate**: L

---

## IDEA-116: Emoji-only Quick Reactions

- **Category**: UX
- **Problem**: Sometimes a full text choice is unnecessary for simple feedback (e.g., "LGTM", "Needs work").
- **Proposed Solution**: Allow agents to define a set of emojis as "Quick Reactions" that appear as a single-tap bar at the bottom of the notification/prompt.
- **Business Value**: Makes human interaction feel faster and more modern, similar to popular messaging apps.
- **Effort Estimate**: S

---

## IDEA-117: Automated OpenAPI Specification Generation

- **Category**: Tech Debt
- **Problem**: The `hitl-cli` backend and client interfaces are evolving rapidly, and manual documentation of the API structure is prone to falling behind.
- **Proposed Solution**: Implement a script that inspects the Pydantic models and Typer commands to automatically generate and update a versioned OpenAPI (Swagger) specification.
- **Business Value**: Ensures the API is always well-documented for external developers and future sub-agents.
- **Effort Estimate**: S

---

## IDEA-118: GitHub Issue/PR Comment Integration

- **Category**: Integration
- **Problem**: When a HITL request is triggered from a GitHub Action, there is no persistent record of the interaction within the GitHub UI.
- **Proposed Solution**: An optional feature where the CLI (running in GH Actions) automatically posts a comment to the relevant Issue/PR when a request is sent, and updates it when the response is received.
- **Business Value**: Provides a clear audit trail and visibility for the entire team directly within the PR workflow.
- **Effort Estimate**: S

---

## IDEA-119: Scheduled "Delayed" Requests

- **Category**: Feature
- **Problem**: An agent might identify a problem at 2 AM but doesn't want to wake the human.
- **Proposed Solution**: Add a `--deliver-at` or `--delay` flag to `request` and `notify` that instructs the relay to hold the message until a specific time.
- **Business Value**: Respects user's "Quiet Hours" while allowing agents to schedule non-urgent work without custom queuing logic.
- **Effort Estimate**: M

---

## IDEA-120: Dynamic "Agent Capabilities" Advertisement

- **Category**: Tech Debt
- **Problem**: The relay doesn't know what features (e.g., E2EE, multi-line, attachments) a specific CLI version or SDK integration supports.
- **Proposed Solution**: During the login/registration phase, the client sends a `capabilities` bitmask or JSON object detailing what it can handle, allowing the relay to degrade gracefully.
- **Business Value**: Future-proofs the system and enables seamless rollout of new features across a heterogeneous fleet of agents.
- **Effort Estimate**: M
