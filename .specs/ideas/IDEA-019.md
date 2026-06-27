# Ideas Batch — hitl-cli (Batch 25)

## IDEA-361: "Ephemeral" Dynamic Clients
- **Category**: Security
- **Problem**: Currently, dynamic client registration creates persistent client definitions on the server and in the client's file system, which clutter storage when agents are short-lived/transient (e.g. CI/CD runners or one-off tasks).
- **Proposed Solution**: Support an `--ephemeral` flag during dynamic client registration. Ephemeral clients are registered with a short Time-To-Live (TTL) (e.g. 1 hour) on the relay and automatically deleted/purged when expired, eliminating manual clean-up.
- **Business Value**: Enhances security by reducing the attack surface of dangling OAuth credentials and eliminates server database bloat.
- **Effort Estimate**: S

---

## IDEA-362: "Auto-Fallback" to Non-E2EE with Security Guardrails
- **Category**: Security
- **Problem**: When E2EE key exchange fails or is not supported by the relay/mobile client, the operation immediately errors out. In non-critical environments, users might prefer falling back to non-E2EE instead of hard failing.
- **Proposed Solution**: Implement a configuration option and flag `--allow-unencrypted-fallback`. If E2EE setup fails, it will attempt a non-E2EE request, but ONLY if the payload contains no pre-defined sensitive patterns (e.g., regex matching passwords/API keys) to prevent accidental data leaks.
- **Business Value**: Improves developer experience and reliability in non-production environments while preventing security accidents.
- **Effort Estimate**: M

---

## IDEA-363: "Progress-Bar" / "Heartbeat" updates for long-running HITL Requests
- **Category**: UX
- **Problem**: If a human takes a long time to respond to a request, the CLI or SDK just hangs silently, giving no indication if the connection is still active or timed out.
- **Proposed Solution**: Introduce an active heartbeat ping mechanism while waiting for a response. The CLI can show a visual progress spinner and a "Connection active (last check: Ns ago)" message, keeping the session alive and informing the developer of the health of the websocket/HTTP polling.
- **Business Value**: Prevents developers from prematurely canceling active requests due to lack of visibility, saving developer time.
- **Effort Estimate**: S

---

## IDEA-364: "Dry-Run" Mode for HITL CLI/SDK
- **Category**: Tech Debt
- **Problem**: Testing scripts that integrate `hitl-cli` requires actually sending notifications and requests, which either requires a real device or a mocked relay.
- **Proposed Solution**: Add a `--dry-run` flag to the CLI and a `dry_run=True` initialization parameter to the Python SDK. When enabled, requests and notifications are validated locally and log their payloads, returning a mock "Approve" response immediately without reaching out to the network.
- **Business Value**: Speeds up local script development and testing pipelines without requiring live network calls or setup.
- **Effort Estimate**: S

---

## IDEA-365: "Interactive Multi-Choice" with Default Timeouts
- **Category**: Feature
- **Problem**: When requesting input with choices, if the human does not respond within a timeout, the operation fails. In automated scripts, a default choice fallback would be preferred over a hard failure.
- **Proposed Solution**: Support a `--default-choice` option combined with a `--timeout` option. If the human fails to respond before the timeout, the CLI automatically selects the default choice and exits with success.
- **Business Value**: Enables robust automated scripting where human input is preferred but non-blocking if the human is away.
- **Effort Estimate**: S

---

## IDEA-366: "Structured Output" Validation using Pydantic in SDK
- **Category**: Integration
- **Problem**: The SDK allows requesting free-form input or simple choices, but cannot easily validate structured JSON responses from the human.
- **Proposed Solution**: Allow SDK users to pass a Pydantic model to `request_input`. The SDK will serialize the model schema, send it as a validation constraint to the mobile client (which prompts the human to fill in the schema), and automatically parse/validate the response back into the Pydantic model.
- **Business Value**: Allows complex inputs (like configuration settings or structured forms) to be collected from humans with guaranteed type safety.
- **Effort Estimate**: M

---

## IDEA-367: "Local Mock Relay" Dev Server Mode
- **Category**: UX
- **Problem**: Working offline or in closed networks prevents testing the HITL loop since the CLI must reach out to the public `hitlrelay.app`.
- **Proposed Solution**: Add a `hitl-cli dev-server` command that starts a lightweight, local web server mimicking the relay APIs. It displays a simple web interface in the browser representing the mobile app, allowing developers to approve/reject requests locally without internet.
- **Business Value**: Accelerates SDK development and offline testing, making the system highly reliable and decoupled from third-party outages during development.
- **Effort Estimate**: M

---

## IDEA-368: "Diagnostic Self-Test" Command (`hitl-cli doctor`)
- **Category**: UX
- **Problem**: When the CLI fails to connect, users don't know if the issue is local network proxy settings, server outage, invalid token, or expired cryptographic keys.
- **Proposed Solution**: Create a `doctor` command that runs a diagnostic suite: checks internet connectivity, checks DNS resolution of the relay, verifies token validity, validates file permissions of token files, verifies E2EE keys, and sends a test ping to the relay.
- **Business Value**: Drastically reduces user support requests by enabling self-diagnosis of common configuration and networking issues.
- **Effort Estimate**: S

---

## IDEA-369: "Configurable Storage Directory Override via Env Var"
- **Category**: Tech Debt
- **Problem**: The config and token paths are hardcoded to standard user configuration directories. This prevents multiple independent setups on the same machine, or isolated containers where home directories might be read-only or shared.
- **Proposed Solution**: Support a `HITL_CONFIG_DIR` environment variable to override the configuration root path. If set, all credentials, config, and encryption keys will be stored in and loaded from this directory instead of the default user config path.
- **Business Value**: Crucial for advanced CI/CD pipelines, containerized agents, and testing multiple agents concurrently on a single machine.
- **Effort Estimate**: S

---

## IDEA-370: "Configurable Log Redaction" for E2EE Payloads
- **Category**: Security
- **Problem**: When E2EE is enabled, the CLI logs debug info or exceptions which might accidentally write the unencrypted plaintext request details to the local system log.
- **Proposed Solution**: Implement a strict log redaction filter in the logging setup. Any log message containing request payloads, prompts, or options will be automatically sanitized/redacted when the log level is not explicitly set to a highly verbose debugging flag.
- **Business Value**: Ensures compliance with strict security audits where plaintext sensitive data must never touch log files.
- **Effort Estimate**: S

---

## IDEA-371: "Pre-Auth Hook" for Custom Corporate SSO
- **Category**: Security
- **Problem**: Enterprise customers want to restrict access to the HITL CLI so only authenticated corporate users can run it, but the standard login only supports generic OAuth/Firebase.
- **Proposed Solution**: Allow configuring a custom authentication helper script (pre-auth hook) that is run before `hitl-cli login`. The helper script completes the enterprise single sign-on (SSO) and returns the token to `hitl-cli`.
- **Business Value**: Increases appeal to enterprise customers who require SSO compliance for developer tools.
- **Effort Estimate**: M

---

## IDEA-372: "SDK Connection Heartbeat" for Persistent Daemon Modes
- **Category**: Performance
- **Problem**: Long-lived Python daemons utilizing the SDK experience connection dropouts or socket timeouts on their HTTP/WebSocket connections after long periods of inactivity.
- **Proposed Solution**: Implement an optional async background task in the SDK that periodically sends light heartbeat pings to the relay to keep TCP/WebSocket connections warm and alive.
- **Business Value**: Minimizes request latency and socket failure overhead for long-running server daemons using the SDK.
- **Effort Estimate**: S
