# Ideas Batch — hitl-cli (Batch 15)

## IDEA-211: Automated "Agent Reputation" Scoring
- **Category**: Performance
- **Problem**: Some agents may become "noisy" by sending low-quality or redundant prompts, leading to human notification fatigue and slower response times for critical tasks.
- **Proposed Solution**: The relay tracks interaction patterns (e.g., dismissal vs. response, response latency) per agent ID. Agents with poor "reputation" scores are flagged in the mobile app, and the SDK can be configured to automatically rate-limit or downgrade their priority.
- **Business Value**: Protects the human user's most valuable asset—attention—and ensures high-quality interactions across the ecosystem.
- **Effort Estimate**: L

---

## IDEA-212: "Scripted Response Injection" for Automated Testing
- **Category**: UX
- **Problem**: Testing complex agent logic that requires human input is currently difficult to automate in CI/CD because it requires a real human response from a mobile device.
- **Proposed Solution**: Add a `--mock-response <choice>` flag to the `request` command. If present, the CLI skips the relay and immediately returns the provided choice as the result, allowing developers to script the "human" part of the interaction.
- **Business Value**: Dramatically accelerates development and enables reliable automated testing of human-in-the-loop workflows.
- **Effort Estimate**: S

---

## IDEA-213: "Smart-Collapse" for Duplicate Notifications
- **Category**: UX
- **Problem**: A broken agent loop or a flapping monitor can flood a human's phone with dozens of identical notifications in seconds.
- **Proposed Solution**: Implement a client-side or relay-side deduplication window. If multiple identical notifications are sent within a short timeframe (e.g., 60s), they are collapsed into a single alert with a counter (e.g., "Disk 90% full (x15)").
- **Business Value**: Prevents "notification storms" and reduces user annoyance during system failures.
- **Effort Estimate**: M

---

## IDEA-214: HITL SDK Middleware Support
- **Category**: Tech Debt
- **Problem**: Developers want to add cross-cutting concerns (e.g., custom logging, metrics, or data scrubbing) to all HITL interactions without duplicating code or subclassing the main client.
- **Proposed Solution**: Implement a middleware architecture in the `HITL` Python client. Users can register middleware functions that intercept and modify requests before they are sent and responses after they are received.
- **Business Value**: Improves SDK extensibility and allows organizations to easily enforce global interaction policies.
- **Effort Estimate**: M

---

## IDEA-215: Interactive "History Search" in CLI
- **Category**: UX
- **Problem**: Even with a local audit log, finding a specific past interaction (e.g., "What did I approve for the staging migration last Tuesday?") requires manual file grepping.
- **Proposed Solution**: Add a `hitl-cli history search --query "..."` command that provides a searchable, paginated terminal view of past requests and responses, with filtering by agent and tag.
- **Business Value**: Enhances observability and provides a quick "audit trail" for developers directly in their terminal.
- **Effort Estimate**: S

---

## IDEA-216: "Proxy-only" Mode for SDK (E2EE Hardening)
- **Category**: Security / Integration
- **Problem**: In high-security environments, outbound traffic to the public HITL relay from application servers might be blocked or strictly audited.
- **Proposed Solution**: A configuration flag for the SDK to force it to communicate *only* with a local `hitl-cli proxy` instance (e.g., via a Unix socket or localhost). The proxy then handles the E2EE and relay communication.
- **Business Value**: Enables HITL usage in air-gapped or high-security VPCs where direct internet access is forbidden.
- **Effort Estimate**: M

---

## IDEA-217: Support for "Custom Emojis" and Project Icons
- **Category**: UX
- **Problem**: Standard system emojis are often too generic to represent specific internal projects or specialized agent personas.
- **Proposed Solution**: Allow the `notify` and `request` commands to specify a URL or local path for a custom icon. The mobile app renders this icon in the notification and the agent list.
- **Business Value**: Improves visual recognition and "branding" for different automated systems within a large organization.
- **Effort Estimate**: S

---

## IDEA-218: "One-Click Remediation Buttons" in SDK
- **Category**: Feature
- **Problem**: When an agent reports an error, the human often knows exactly how to fix it but has to manually type instructions or run a separate command.
- **Proposed Solution**: Add a `remediations` parameter to `request_input` that takes a list of labels and actions. The mobile app renders these as distinct, high-contrast buttons that return structured "fix" intent to the agent.
- **Business Value**: Reduces human cognitive load and speeds up incident resolution.
- **Effort Estimate**: M

---

## IDEA-219: Native "Health-Check" Endpoint in `hitl-cli serve`
- **Category**: Reliability
- **Problem**: Other local services (e.g., monitoring agents) need to verify that the `hitl-cli serve` gateway is running and authenticated before sending tasks.
- **Proposed Solution**: Add a `/health` REST endpoint to the local serve daemon that returns a JSON status including connectivity to the relay, token expiration time, and registered agent identity.
- **Business Value**: Enables more robust local integrations that can "fail fast" or alert if the HITL service itself is unhealthy.
- **Effort Estimate**: S

---

## IDEA-220: Support for `GIT_EDITOR` as Fallback for Complex Input
- **Category**: UX
- **Problem**: Entering long, multi-line, or structured text as a response to a CLI prompt is frustrating and error-prone in a standard terminal.
- **Proposed Solution**: If a request requires a large text response, the CLI can optionally open the user's configured `$EDITOR` (e.g., Vim, Nano, VS Code) to allow for comfortable editing, then send the saved content as the response.
- **Business Value**: Significantly improves the developer experience for providing detailed feedback or code snippets.
- **Effort Estimate**: S

---

## IDEA-221: "Time-of-Day" Adaptive Priority Shifting
- **Category**: UX
- **Problem**: A notification that is appropriate during work hours (Medium priority) can be intrusive and annoying if delivered at 3 AM.
- **Proposed Solution**: Allow users to define "Priority Shifting" rules based on their local time (e.g., "Downgrade all non-Critical notifications by one level between 8 PM and 8 AM").
- **Business Value**: Promotes a healthy work-life balance and reduces the risk of users disabling notifications entirely.
- **Effort Estimate**: M

---

## IDEA-222: SDK Support for `contextvars` (Async Scoping)
- **Category**: Tech Debt
- **Problem**: In complex async Python applications, it is difficult to automatically link a HITL request to the specific web request or trace ID that triggered it.
- **Proposed Solution**: Utilize Python's `contextvars` module within the SDK to automatically capture and propagate task-scoped metadata into every HITL request.
- **Business Value**: Simplifies cross-system tracing and makes debugging interactive flows in large-scale async systems much easier.
- **Effort Estimate**: S

---

## IDEA-223: "Encrypted-at-Rest" for Local Auth Tokens
- **Category**: Security
- **Problem**: While `~/.hitl/` tokens are protected by 600 permissions, they are still stored as plaintext on the disk, making them vulnerable to local file system access or accidental leakage via backups.
- **Proposed Solution**: Provide an option to encrypt the local `oauth_token.json` using a key derived from a system unique identifier (like machine-id) or an optional user passphrase.
- **Business Value**: Provides defense-in-depth for user credentials on shared or less-secure workstations.
- **Effort Estimate**: M

---

## IDEA-224: Support for "Conditional Choices" (Local Branching)
- **Category**: Feature
- **Problem**: Complex human decisions often involve a follow-up question (e.g., "Deploy?" -> "Yes" -> "To which region?"), which currently requires two separate network round-trips.
- **Proposed Solution**: Allow the `request` command to define a simple decision tree in the prompt. The mobile app handles the branching UI locally and only returns the final "leaf" selection to the agent.
- **Business Value**: Reduces network latency and creates a much smoother, app-like experience for multi-step decisions.
- **Effort Estimate**: L

---

## IDEA-225: "Agent-to-Agent" HITL Handover
- **Category**: Feature
- **Problem**: A human might want to "delegate" a task from one agent to another (e.g., "I've reviewed this with the Dev Agent, now hand it over to the Prod Agent for deployment").
- **Proposed Solution**: A specialized request type that allows the human to select a different registered agent from their list to receive a subsequent notification or payload.
- **Business Value**: Enables complex, multi-stage workflows where the human acts as the secure bridge between different autonomous systems.
- **Effort Estimate**: L
