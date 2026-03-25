# Ideas Batch — hitl-cli (Batch 12)

## IDEA-166: Automated Failure Wrapper (`hitl-cli run`)

- **Category**: Feature / DX
- **Problem**: Developers currently must write custom wrapper scripts or manually check exit codes to trigger human notifications when a long-running shell command (e.g., a build or migration) fails.
- **Proposed Solution**: A `hitl-cli run -- <command>` wrapper that monitors the execution of any shell command. If the command returns a non-zero exit code, it automatically sends a HITL request to the human with the last few lines of stderr and options to "Retry", "Ignore", or "Fix" (via input).
- **Business Value**: Provides a universal, zero-code way to add "Human-in-the-Loop" resilience to any existing automated workflow or script.
- **Effort Estimate**: M

---

## IDEA-167: VS Code & Cursor Extension for HITL Management

- **Category**: UX / DX
- **Problem**: Developers often have to switch context between their IDE, terminal, and mobile phone to monitor their agents, view pending requests, or manage E2EE keys.
- **Proposed Solution**: A dedicated IDE extension (VS Code/Cursor) that provides a sidebar for managing the HITL agent fleet, approving/rejecting requests directly within the editor, and visualizing real-time interaction logs.
- **Business Value**: Dramatically reduces context-switching and improves developer productivity by integrating HITL into their primary workspace.
- **Effort Estimate**: L

---

## IDEA-168: On-Call Escalation Integration (PagerDuty/Opsgenie)

- **Category**: Integration
- **Problem**: Mission-critical agent failures might occur when the primary human user is unavailable or away from their phone, leading to unaddressed "blocking" requests.
- **Proposed Solution**: Integrate `hitl-cli` with PagerDuty or Opsgenie. If a high-priority HITL request is not answered within a configurable window, it automatically triggers a standard on-call escalation to ensure someone responds.
- **Business Value**: Essential for moving HITL from "nice-to-have" development aid to reliable production infrastructure for mission-critical tasks.
- **Effort Estimate**: M

---

## IDEA-169: Collaborative Decision Polls (Consensus Mode)

- **Category**: Feature
- **Problem**: Some high-risk decisions (e.g., "Authorize Production Rollback") require more than a single person's approval to prevent accidental or malicious actions by one individual.
- **Proposed Solution**: Extend the `request` command to support a list of multiple recipient agents and a quorum strategy (e.g., `consensus`, `majority`, `3-of-5`). The relay aggregates the votes and only resolves the request once the quorum is met.
- **Business Value**: Enables secure, team-based governance for high-stakes autonomous operations in enterprise environments.
- **Effort Estimate**: L

---

## IDEA-170: SDK Decorator for Automatic Failure Handling (`@hitl.wrap`)

- **Category**: SDK / DX
- **Problem**: Integrating HITL into Python applications often requires a lot of boilerplate code (try/except blocks, formatting error messages into HITL prompts).
- **Proposed Solution**: Provide a `@hitl.wrap` Python decorator that can be applied to any async function. If the function raises an unhandled exception, the decorator automatically triggers a HITL request for the user to "Fix & Retry", "Provide manual result", or "Fail".
- **Business Value**: Significantly lowers the barrier to entry for adding HITL resilience to existing Python codebases.
- **Effort Estimate**: S

---

## IDEA-171: Cryptographically Signed Human Approvals

- **Category**: Security / Compliance
- **Problem**: While the transport is secure (HTTPS/E2EE), there is no persistent, non-repudiable proof that a specific authorized human actually performed a particular approval.
- **Proposed Solution**: Utilize the mobile device's Secure Enclave/KeyStore to sign the response payload at the moment of approval. The `hitl-cli` then verifies and stores this signature, providing a verifiable "proof of intent."
- **Business Value**: Critical for regulatory compliance (e.g., SOC2, HIPAA) where a clear audit trail of human authorization is required for sensitive operations.
- **Effort Estimate**: L

---

## IDEA-172: Desktop-Native Interaction (Raycast / Alfred Extensions)

- **Category**: UX
- **Problem**: Power users working at their desktops often find it slower to pick up their phone for a simple "Yes/No" approval than to use a keyboard shortcut.
- **Proposed Solution**: Provide official extensions for Raycast (macOS) and Alfred that allow users to view their pending HITL queue and respond to requests using a native, spotlight-style desktop interface.
- **Business Value**: Enhances the "power user" experience and reduces friction for developers who spend most of their time at their machines.
- **Effort Estimate**: M

---

## IDEA-173: "Simulation Mode" for Human Workflow Training

- **Category**: DX / UX
- **Problem**: Humans in the loop need to be prepared for the specific requests an agent might send during a high-stress production incident, but they shouldn't "practice" on live systems.
- **Proposed Solution**: A `hitl-cli simulate` command that allows developers to replay recorded sequences of HITL requests to a human. This allows the human to practice the workflow and refine their "response muscle memory" in a safe environment.
- **Business Value**: Reduces human error rates and improves response speed during real-world incidents.
- **Effort Estimate**: M

---

## IDEA-174: E2EE Key Recovery via Shamir's Secret Sharing

- **Category**: Security
- **Problem**: If a user loses their mobile device, their E2EE private key is gone forever, and they lose access to their entire encrypted history.
- **Proposed Solution**: Implement a secure key recovery mechanism using Shamir's Secret Sharing. The master E2EE key is split into "shards" distributed among multiple trusted devices or printed as QR codes. Recovery requires a quorum (e.g., 2 of 3 shards).
- **Business Value**: Prevents catastrophic data loss for high-security users while maintaining the "Zero-Knowledge" principle.
- **Effort Estimate**: L

---

## IDEA-175: Response Option Time-to-Live (TTL)

- **Category**: UX / Feature
- **Problem**: Some response choices (e.g., "Re-run Build #42") are only valid for a short window. If the human responds hours later, the agent might perform an invalid or dangerous action.
- **Proposed Solution**: Allow individual choices in a `request` to have an associated TTL. The mobile app UI shows a countdown timer next to the choice and disables it (while leaving others active) once it expires.
- **Business Value**: Improves system safety by preventing humans from providing stale, contextually irrelevant responses to fast-moving agents.
- **Effort Estimate**: M

---

## IDEA-176: Agent Handover and Persistence Protocol

- **Category**: Feature
- **Problem**: If an agent instance restarts or crashes while waiting for a HITL response, the incoming response from the human may be lost or rejected by the new instance because it doesn't recognize the request ID.
- **Proposed Solution**: A protocol that allows an agent to register "persistent" request IDs with the relay. Upon restart, the agent can query the relay for any outstanding responses associated with its identity.
- **Business Value**: Enables building truly robust, long-lived autonomous systems that can survive hardware or software restarts without losing human context.
- **Effort Estimate**: M

---

## IDEA-177: SDK Response Interceptors (Local Pre-Processing)

- **Category**: SDK / Architecture
- **Problem**: Developers often need to perform global pre-processing (e.g., logging, sanitizing, or augmenting) on every response received from a human before it reaches the core application logic.
- **Proposed Solution**: Support "Response Interceptors" in the `HITL` SDK class. These are user-defined functions that are automatically called with the raw human response, allowing for centralized, reusable processing logic.
- **Business Value**: Promotes cleaner, more maintainable code for complex agent integrations and improves code reusability.
- **Effort Estimate**: S

---

## IDEA-178: Contextual Deep Linking from Notifications

- **Category**: UX
- **Problem**: A notification often tells a human *what* happened, but not *why*. The human then has to manually navigate to GitHub, the AWS console, or a log aggregator to find the context they need to make a decision.
- **Proposed Solution**: Add a `--deep-link` flag to all HITL commands. The mobile app renders this as a primary action button that opens the relevant external app or web page directly to the correct context.
- **Business Value**: Drastically reduces "time-to-context" for the human, leading to faster and more accurate decision-making.
- **Effort Estimate**: S

---

## IDEA-179: Automated "Agent Capabilities" Onboarding

- **Category**: DX / Security
- **Problem**: New users are often overwhelmed by the setup required for advanced features like E2EE or specific hooks. They might not realize an agent needs certain permissions until it fails.
- **Proposed Solution**: A `hitl.onboard()` SDK method that performs a comprehensive check of the agent's environment and configuration. It triggers a special HITL "onboarding" request on the human's phone to verify connectivity and grant necessary permissions.
- **Business Value**: Ensures a smooth, secure "Day 1" experience for new users and prevents mysterious setup-related failures.
- **Effort Estimate**: M

---

## IDEA-180: Battery and Connection-Aware SDK Polling

- **Category**: Performance / Reliability
- **Problem**: In long-running processes on mobile or edge devices, aggressive polling for HITL responses can drain battery or consume expensive metered data.
- **Proposed Solution**: Implement adaptive polling in the SDK that detects the device's power state (battery vs plugged in) and network type (WiFi vs Cellular). It automatically throttles polling frequency when resources are constrained.
- **Business Value**: Extends device life and reduces operational costs for edge-deployed autonomous agents.
- **Effort Estimate**: M
