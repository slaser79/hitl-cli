# Ideas Batch — hitl-cli (Batch 26)

## IDEA-373: Dynamic Command-Line Argument Autocomplete based on Remote CLI State
- **Category**: UX
- **Problem**: Users manually typing choices or arguments in `hitl-cli request` might make typos, and they don't know the exact names of active agents or task IDs on the relay.
- **Proposed Solution**: Implement shell completion (Bash/Zsh/Fish) that dynamically fetches available tasks or options from the local cache and/or HITL relay API in the background. Running `hitl-cli status --task <TAB>` or choosing choices would show intelligent tab-completions.
- **Business Value**: Speeds up terminal operations and reduces typing errors, improving overall CLI usability.
- **Effort Estimate**: S

---

## IDEA-374: Cryptographic Audit Log Validation Utility
- **Category**: Security
- **Problem**: Although there is an SQLite audit log or logs on the relay, there is no easy tool to verify the cryptographic signatures and integrity of local or remote history logs to prove no tampering occurred.
- **Proposed Solution**: Add a `hitl-cli history verify` command. It walks the local audit log or fetches transaction history, validates that the HMAC/signatures of responses match the registered agent and human keys, and highlights any tampered or un-signed entries.
- **Business Value**: Guarantees compliance and security auditing for enterprise environments by providing verifiable proof of human decisions.
- **Effort Estimate**: M

---

## IDEA-375: Configurable In-Memory Secret Store for Transient Agents
- **Category**: Security
- **Problem**: When running in ephemeral CI/CD environments (e.g., GitHub Actions, GitLab CI), writing authentication credentials and E2EE keys to the disk (`~/.hitl/`) is risky and often forbidden.
- **Proposed Solution**: Allow passing configuration, OAuth tokens, and keys entirely via environment variables (e.g., `HITL_OAUTH_TOKEN_JSON` and `HITL_PRIVATE_KEY_PEM`) or loading them in-memory from a secure Vault/Secret Manager, bypassing disk writes.
- **Business Value**: Simplifies CI/CD security compliance and allows running in read-only file systems.
- **Effort Estimate**: S

---

## IDEA-376: Automatic Notification Fallback to Email / Slack Webhook
- **Category**: UX
- **Problem**: If the human user does not have the mobile app installed, has their phone turned off, or has uninstalled it, notifications and critical requests fail silently or timeout.
- **Proposed Solution**: Support defining fallback communication channels (like email, Slack webhook, or Discord webhook) in the user's config. If the relay detects the mobile app is unreachable after a short timeout, it triggers a fallback notification to the configured webhook or email.
- **Business Value**: Increases notification delivery success rate and ensures developers are reached even when away from their phones.
- **Effort Estimate**: M

---

## IDEA-377: Incremental Log and Artifact Streaming for Human Context
- **Category**: Performance
- **Problem**: When a developer wants to send context (e.g., build logs) with a request, sending the entire 10MB log as a single E2EE payload is slow and could hit API payload limits.
- **Proposed Solution**: Support sending a referenced log stream. The CLI or SDK uploads chunks incrementally or sets up a temporary WebSocket log viewer, allowing the human to scroll through logs dynamically on their mobile app.
- **Business Value**: Enables providing rich debugging context to the human without hitting payload limits or causing high network latency.
- **Effort Estimate**: L

---

## IDEA-378: Offline Mode with Local SQLite Pending Queue
- **Category**: Feature
- **Problem**: If the developer loses network connectivity, running `hitl-cli notify` or `hitl.notify(...)` throws a connection exception immediately, breaking local scripts that could otherwise continue.
- **Proposed Solution**: Implement an offline request/notification queue. When offline, notifications are queued locally in a SQLite database and automatically flushed to the relay once network connectivity is restored.
- **Business Value**: Increases robustness of automated developer scripts against temporary network outages.
- **Effort Estimate**: M

---

## IDEA-379: Standardized SDK Mocking Framework for Unit Testing
- **Category**: Tech Debt
- **Problem**: Developers integrating the `hitl-cli` SDK into their Python projects have to manually write complex mocks for the `HITL` client class to avoid hitting the live API during unit tests.
- **Proposed Solution**: Provide a first-class `hitl_cli.testing` module containing a `MockHITL` class and a `pytest` fixture (`hitl_mock`). It simulates human inputs, pre-seeds responses, and records all outgoing notifications for assertions.
- **Business Value**: Improves the DX and test coverage of downstream applications integrating with HITL.
- **Effort Estimate**: S

---

## IDEA-380: HTTP Proxy Authentication Tunneling
- **Category**: Integration
- **Problem**: Many corporate networks force all outbound traffic through authenticated HTTP/HTTPS proxies, which blocks `hitl-cli` from connecting to the public relay.
- **Proposed Solution**: Add config options and environment variable support (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`) to the `ApiClient` and `mcp_client.py`, utilizing `httpx`'s built-in proxy tunneling with basic/digest auth.
- **Business Value**: Enables adoption of hitl-cli inside restricted enterprise networks.
- **Effort Estimate**: S

---

## IDEA-381: Local Dev Dashboard with Live Web Interface
- **Category**: UX
- **Problem**: Debugging the interactive HITL loop locally (especially with E2EE and MCP) is hard to trace, as standard output only shows raw logs or CLI text.
- **Proposed Solution**: Add a `hitl-cli dashboard` command that spins up a local web server (e.g., on localhost:8000) showing a visual dashboard of all active, pending, and completed requests, including their unencrypted payload details for easy debugging.
- **Business Value**: Drastically reduces local development cycle times for developers building complex agentic loops.
- **Effort Estimate**: M

---

## IDEA-382: Graceful JWT/OAuth Token Revocation Command
- **Category**: Security
- **Problem**: Users logging out only delete local credential files, leaving registered dynamic clients and active tokens valid on the relay server until they expire.
- **Proposed Solution**: Implement a `hitl-cli logout` command that explicitly sends a revocation request (RFC 7009) to the relay's `/oauth/revoke` endpoint to invalidate both refresh and access tokens before deleting the local config.
- **Business Value**: Adheres to security best practices and minimizes dangling authorization credentials.
- **Effort Estimate**: S

---

## IDEA-383: SDK Multi-Tenant Client Connection Pool
- **Category**: Performance
- **Problem**: Long-running Python agent servers handling requests for multiple users currently instantiate a new `HITL` client per user, leading to high connection setup overhead and resource leaks.
- **Proposed Solution**: Refactor the SDK to support a multi-tenant client pool (`HITLClientPool`) that manages shared `httpx.AsyncClient` connections and routes requests for different user profiles efficiently.
- **Business Value**: Reduces server memory consumption and latency for SaaS integrations.
- **Effort Estimate**: M

---

## IDEA-384: Dynamic E2EE Key Rotation Protocol
- **Category**: Security
- **Problem**: If an E2EE private key stored locally is compromised, past and future messages remain vulnerable unless a manual key generation is performed.
- **Proposed Solution**: Implement an automated key rotation protocol where the CLI and relay negotiate a new E2EE key pair periodically (e.g., every 30 days or after 100 requests) without requiring user intervention.
- **Business Value**: Provides forward secrecy and enhances protection of highly sensitive data.
- **Effort Estimate**: L

---

## IDEA-385: Interactive Prompt Configuration Generator
- **Category**: Tech Debt
- **Problem**: Creating structured prompts with complex choices and markdown formatting requires typing lengthy CLI commands, which developers find tedious.
- **Proposed Solution**: Add an interactive prompt builder wizard: `hitl-cli request wizard`. It guides the user step-by-step through setting the prompt title, body, choice list, priority, and outputs the equivalent CLI command or SDK python code.
- **Business Value**: Improves developer adoption and onboarding speed by making it easy to generate valid commands.
- **Effort Estimate**: S

---

## IDEA-386: Agent-to-Human Dynamic Screen Overlay Sharing
- **Category**: Feature
- **Problem**: When an agent requests approval for a UI action (e.g. clicking a button), screenshots don't show the exact coordinates or target elements clearly.
- **Proposed Solution**: Allow attaching coordinates or HTML selectors to requests. The mobile app overlays a red bounding box or highlighter on the attached screenshot to show exactly where the agent proposes to interact.
- **Business Value**: Minimizes human error during visual verification tasks by pointing out the exact region of interest.
- **Effort Estimate**: M

---

## IDEA-387: SDK Event-Driven Callback Handlers
- **Category**: Feature
- **Problem**: The SDK relies on waiting for a coroutine (`await hitl.request_input(...)`) which blocks the current task execution thread. There is no simple way to handle responses asynchronously using event handlers.
- **Proposed Solution**: Add support for registering async callback handlers: `hitl.on_response(request_id, callback_coro)`. When the human responds, the SDK automatically invokes the registered callback in the background.
- **Business Value**: Enables building non-blocking event-driven agent architectures using the Python SDK.
- **Effort Estimate**: M
