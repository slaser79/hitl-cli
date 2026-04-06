# Ideas Batch — hitl-cli (Batch 9)

## IDEA-121: Automated "Diagnostic Snapshot" for Support

- **Category**: Tech Debt
- **Problem**: When a user reports a bug, support needs to know the CLI version, OS, config state, and recent error logs. Collecting this manually is slow and prone to error.
- **Proposed Solution**: A `hitl-cli support-bundle` command that generates a redacted ZIP/JSON file containing all relevant non-sensitive diagnostic information (version, OS, connectivity test results, redacted logs).
- **Business Value**: Speeds up issue resolution and reduces support overhead.
- **Effort Estimate**: S

---

## IDEA-122: Automatic E2EE Key Rotation Policy

- **Category**: Security
- **Problem**: E2EE keys are currently stored indefinitely in `~/.hitl/agent_keypair.json`. Long-lived keys increase the window of vulnerability if a machine is compromised.
- **Proposed Solution**: Implement a configurable key rotation policy (e.g., every 30 days). The CLI automatically generates a new keypair and re-registers with the relay during a `login` or a background `refresh` call.
- **Business Value**: Enhances long-term security posture for confidential interactions.
- **Effort Estimate**: M

---

## IDEA-123: SDK Support for Custom HTTP Middleware (Interceptors)

- **Category**: Integration
- **Problem**: Enterprise users may need to inject custom headers (for corporate proxies, tracing, or custom auth) into every SDK request.
- **Proposed Solution**: Allow the `HITL` class constructor to accept a list of `httpx` middlewares or a custom `httpx.AsyncClient` instance to be used for all internal API calls.
- **Business Value**: Enables integration into complex enterprise network environments.
- **Effort Estimate**: S

---

## IDEA-124: Human Response "Reasoning" or "Notes" Field

- **Category**: Feature
- **Problem**: Simple choice selections often lack the context of *why* the human made that choice, which is critical for debugging agent behavior.
- **Proposed Solution**: Extend the `request` payload and mobile app UI to include an optional "Reasoning" text field that the human can fill out alongside their choice.
- **Business Value**: Provides richer feedback for AI agents to learn from human decision-making.
- **Effort Estimate**: M

---

## IDEA-125: Local "Mock Relay" for Hermetic Testing

- **Category**: DX
- **Problem**: Running integration tests currently requires a connection to the real `hitlrelay.app` or a complex manual mock of the API.
- **Proposed Solution**: A lightweight, local FastAPI server bundled with the CLI (`hitl-cli serve-mock`) that implements the HITL API and allows testing the full E2EE flow without any external dependencies.
- **Business Value**: Enables 100% hermetic and fast integration tests in CI/CD pipelines.
- **Effort Estimate**: M

---

## IDEA-126: `hitl-cli log-tail` for Real-time Interaction Monitoring

- **Category**: UX
- **Problem**: Developers have to manually poll or check the mobile app to see the status of their sent requests.
- **Proposed Solution**: A `log-tail` command that uses WebSockets or long-polling to stream real-time updates of sent requests, human responses, and E2EE proxy activity to the terminal.
- **Business Value**: Provides a "live view" of the human-in-the-loop system for easier debugging.
- **Effort Estimate**: M

---

## IDEA-127: Support for Multi-Choice "Checkboxes" (Multiple Selection)

- **Category**: Feature
- **Problem**: Currently, `request` only supports single-choice selection. Users can't select multiple options (e.g., "Which files to delete?").
- **Proposed Solution**: Add a `--multiple` flag to the `request` command that changes the mobile UI to checkboxes and returns a list of selected values.
- **Business Value**: Enables more complex data collection and human-driven batch operations.
- **Effort Estimate**: M

---

## IDEA-128: SDK-level "Circuit Breaker" for Relay Failures

- **Category**: Reliability
- **Problem**: If the HITL relay is down, the SDK might hang or repeatedly retry, potentially slowing down the host application.
- **Proposed Solution**: Implement a circuit breaker pattern in the `HITL` SDK that fast-fails requests if the relay is consistently unreachable, with configurable fallback modes.
- **Business Value**: Prevents a single dependency from cascading failures into the main application.
- **Effort Estimate**: M

---

## IDEA-129: Rich Human-Input Validation (RegEx/Schema)

- **Category**: UX
- **Problem**: Humans might provide invalid free-text input (e.g., a malformed email), forcing the agent to send another request to correct it.
- **Proposed Solution**: Allow the `request` command to specify a RegEx pattern or JSON schema for the free-text input field, with the mobile app providing real-time validation.
- **Business Value**: Reduces interaction round-trips and improves data quality.
- **Effort Estimate**: L

---

## IDEA-130: "Emergency" Priority Bypass for Notifications

- **Category**: UX
- **Problem**: During "Quiet Hours" or "Do Not Disturb," critical alerts (e.g., "Production Down") might be missed.
- **Proposed Solution**: A `--priority emergency` flag that uses platform-specific "Critical Alerts" features to bypass system-level silence settings.
- **Business Value**: Ensures that time-sensitive, high-stakes notifications are always delivered immediately.
- **Effort Estimate**: L

---

## IDEA-131: Integrated "Token Scrubbing" for Logs

- **Category**: Security
- **Problem**: Debug logs might accidentally include OAuth tokens or API keys if not carefully managed.
- **Proposed Solution**: Add a specialized log filter to the internal logging setup that automatically identifies and masks strings matching the pattern of HITL tokens and keys.
- **Business Value**: Reduces the risk of accidental credential leakage through log files.
- **Effort Estimate**: S

---

## IDEA-132: Local SQLite Persistence for Offline Audit Log

- **Category**: Reliability
- **Problem**: If the relay is unavailable or the user clears their terminal, the history of human interactions is lost.
- **Proposed Solution**: Implement a local SQLite database that stores every request and response (encrypted at rest if E2EE), providing a permanent, searchable audit trail.
- **Business Value**: Ensures compliance and accountability for all human-mediated actions.
- **Effort Estimate**: M

---

## IDEA-133: SDK Support for "Fire and Forget" Notifications

- **Category**: Performance
- **Problem**: `hitl.notify()` currently waits for the HTTP response from the relay, which can slow down the main thread for non-critical telemetry.
- **Proposed Solution**: Add a `background=True` parameter to `notify` that schedules the network call in a background task without blocking the caller.
- **Business Value**: Minimizes performance impact on the host application for non-critical notifications.
- **Effort Estimate**: S

---

## IDEA-134: "Time-to-Respond" SLAs for Requests

- **Category**: Feature
- **Problem**: Critical requests might need to be escalated or cancelled if a human doesn't respond within a specific timeframe (SLA).
- **Proposed Solution**: Add an `--sla` flag to `request` that triggers a secondary notification or a webhook call if the primary response hasn't been received by the deadline.
- **Business Value**: Enables operational guarantees for human-in-the-loop business processes.
- **Effort Estimate**: M

---

## IDEA-135: E2EE Support for Binary Attachments

- **Category**: Feature
- **Problem**: Users can't currently send sensitive images or files (e.g., screenshots of errors) through the E2EE proxy securely.
- **Proposed Solution**: Extend the E2EE proxy and `crypto.py` to handle chunked encryption of binary data, allowing agents to send small files alongside prompts securely.
- **Business Value**: Enables high-context, secure troubleshooting and review of visual data.
- **Effort Estimate**: L
