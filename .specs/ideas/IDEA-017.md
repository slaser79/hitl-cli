# Ideas Batch — hitl-cli (Batch 23)

## IDEA-331: "Time-to-Respond" SLAs for Autonomous Agents
- **Category**: Performance
- **Problem**: Agents can hang indefinitely waiting for a human response, blocking valuable compute resources and delaying downstream tasks.
- **Proposed Solution**: Allow agents to specify a `timeout` and a `default_choice` in the request. If the human doesn't respond within the SLA, the CLI automatically returns the default choice and logs the SLA breach.
- **Business Value**: Prevents deadlocks in autonomous workflows and ensures predictable execution times.
- **Effort Estimate**: M

---

## IDEA-332: "Geofenced" critical Approval Validation
- **Category**: Security
- **Problem**: Compromised mobile devices could be used to approve high-risk operations from anywhere in the world.
- **Proposed Solution**: Integration with mobile GPS to enforce geofencing. Critical requests (e.g., "Delete Production") can be configured to only allow approval if the human is within a verified corporate office location.
- **Business Value**: Mitigates risk of unauthorized remote approvals from stolen or compromised devices.
- **Effort Estimate**: L

---

## IDEA-333: "Dependency-Aware" Contextual Links
- **Category**: Integration
- **Problem**: Humans often have to switch between the HITL app and GitHub/Jira to understand the context of a request (e.g., which PR is this about?).
- **Proposed Solution**: Allow agents to attach `context_urls` to requests. The mobile app renders these as prominent deep-links to PRs, Issues, or CI logs, providing one-tap access to relevant technical context.
- **Business Value**: Reduces context-switching overhead and speeds up human decision making.
- **Effort Estimate**: S

---

## IDEA-334: "SDK-Level" Middleware Interceptors
- **Category**: Tech Debt
- **Problem**: Adding global logic (like logging, custom telemetry, or payload modification) to all HITL requests in a large application is tedious and error-prone.
- **Proposed Solution**: Implement an "Interceptor" pattern in the Python SDK. Developers can register global middlewares that can inspect, modify, or block requests and responses before they are sent to the relay.
- **Business Value**: Improves maintainability and allows for consistent cross-cutting concerns across all HITL interactions.
- **Effort Estimate**: M

---

## IDEA-335: "Zero-Trust" Proxy-to-Relay mTLS
- **Category**: Security
- **Problem**: The current proxy-to-relay connection relies on API keys/OAuth tokens, which can be intercepted or leaked.
- **Proposed Solution**: Support for mutual TLS (mTLS) between the local `hitl-cli proxy` and the backend relay. Each workstation gets a unique client certificate, ensuring that only verified hardware can connect to the proxy surface.
- **Business Value**: Provides defense-in-depth for the proxy mode, ensuring identity verification at the transport layer.
- **Effort Estimate**: L

---

## IDEA-336: "Semantic History" Search for Human Responses
- **Category**: UX
- **Problem**: Developers often forget how they handled a specific edge case in the past and want to see their previous responses to similar prompts.
- **Proposed Solution**: A `hitl-cli history search --semantic "..."` command that uses local embeddings (e.g., via `sentence-transformers`) to find past prompts and responses that are semantically similar to the query.
- **Business Value**: Leverages historical knowledge to improve the consistency and quality of human-in-the-loop decisions.
- **Effort Estimate**: M

---

## IDEA-337: "Interactive-Markdown" with State Sync
- **Category**: UX
- **Problem**: Current prompts are mostly static text. Complex requests might need the human to "check off" a list of manual verification steps.
- **Proposed Solution**: Support interactive Markdown elements (like `[ ]` checkboxes) in prompts. The human can toggle these in the mobile app, and the final "checked" state is returned to the agent in the response payload.
- **Business Value**: Enables structured manual checklists that are verified by the human and recorded by the agent.
- **Effort Estimate**: M

---

## IDEA-338: "Device Authorization Grant" (RFC 8628) Support
- **Category**: UX
- **Problem**: Logging in on a remote server via SSH is difficult because the `login` command tries to open a local browser.
- **Proposed Solution**: Implement the OAuth 2.0 Device Authorization Grant. The CLI displays a short code and a URL; the human enters the code on their mobile app or laptop to authorize the remote CLI session.
- **Business Value**: Dramatically improves the developer experience for hitl-cli usage in remote and headless environments.
- **Effort Estimate**: M

---

## IDEA-339: "Agent-Identity" Cryptographic Signing
- **Category**: Security
- **Problem**: It's difficult for a human to be certain that a request actually came from the agent they think it did, rather than a malicious script.
- **Proposed Solution**: Allow the CLI to sign requests using a local private key unique to that workstation/agent. The mobile app verifies the signature and displays a "Verified Agent" badge.
- **Business Value**: Prevents "agent impersonation" attacks and ensures non-repudiation of requests.
- **Effort Estimate**: M

---

## IDEA-340: "Batch-Action" CLI for Mass Approvals
- **Category**: UX
- **Problem**: During large-scale refactorings, an agent might spawn dozens of identical "Confirm change" requests that clutter the human's queue.
- **Proposed Solution**: A `hitl-cli batch approve --pattern "..."` command that allows the human to approve or reject all pending requests matching a specific regex or agent name in a single operation.
- **Business Value**: Significantly reduces the "approval bottleneck" for high-volume autonomous operations.
- **Effort Estimate**: S

---

## IDEA-341: "Smart-Retry" with Rate-Limit Awareness
- **Category**: Performance
- **Problem**: Current retry logic is often too aggressive or doesn't respect the `Retry-After` headers from the relay, leading to further throttling.
- **Proposed Solution**: Refactor `api_client.py` to use jittered exponential backoff that is explicitly aware of HTTP 429 (Too Many Requests) and respects the server's suggested wait time.
- **Business Value**: Improves system reliability and prevents self-inflicted DDoS on the relay infrastructure.
- **Effort Estimate**: S

---

## IDEA-342: "OS-Native" Desktop Notification Bridge
- **Category**: UX
- **Problem**: A developer at their desk might have their phone in another room and miss a critical HITL request.
- **Proposed Solution**: When the `proxy` is running, it can optionally trigger local OS notifications (via `notify-send` or `plyer`) in addition to the mobile ping, ensuring the developer sees it immediately.
- **Business Value**: Minimizes latency for developers who are actively working at their workstations.
- **Effort Estimate**: S

---

## IDEA-343: "SDK-Integrated" Circuit Breaker Pattern
- **Category**: Performance
- **Problem**: If the HITL relay is down, the SDK might block the entire agent application indefinitely or keep retrying uselessly.
- **Proposed Solution**: Build a circuit breaker into the `HITL` Python SDK. If a threshold of failures is met, the SDK "opens the circuit," immediately failing subsequent requests locally for a grace period.
- **Business Value**: Increases the resilience of agent-based applications by preventing them from being dragged down by a third-party service outage.
- **Effort Estimate**: M

---

## IDEA-344: "Custom-UI" JSON Schema Extensions
- **Category**: Integration
- **Problem**: Some HITL tasks need specialized UI (like a chart or a map) that a text-based prompt cannot provide.
- **Proposed Solution**: Allow agents to send a `ui_extension` payload containing structured JSON data. The mobile app can use "UI Plugins" to render this data as rich components (e.g., `vega-lite` charts).
- **Business Value**: Enables HITL to support complex data-driven decision making beyond simple text and choices.
- **Effort Estimate**: L

---

## IDEA-345: "Auto-Diagnostic" Support Bundle
- **Category**: UX
- **Problem**: When a CLI command fails due to network or config issues, the user has to manually gather logs and system info for support.
- **Proposed Solution**: If a command fails, the CLI offers to generate a "Support Bundle" (`hitl-cli doctor --bundle`) that captures redacted logs, config (minus tokens), and system info into a single ZIP for easy sharing.
- **Business Value**: Reduces support turnaround time and helps maintainers debug environment-specific issues more effectively.
- **Effort Estimate**: S
