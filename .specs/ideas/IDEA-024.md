# Ideas Batch — hitl-cli (Batch 30)

## IDEA-433: Agent-to-Human Dynamic Attachment & File Payload Support
- **Category**: Integration
- **Problem**: When agents request human input for complex code diffs, logs, or screenshots, string prompts alone are often insufficient or exceed payload limits.
- **Proposed Solution**: Extend `hitl-cli request` and the SDK to support `--attachment <path>` (e.g. images, PDFs, or diff files). The CLI and SDK will compress, optionally E2EE encrypt, and upload attachments to the relay for mobile rendering.
- **Business Value**: Expands HITL usage to multimodal agent tasks, increasing task resolution rates for visual or complex code reviews.
- **Effort Estimate**: M

---

## IDEA-434: CLI Session Record & Interactive Replay Terminal
- **Category**: UX
- **Problem**: Debugging complex multi-turn agent-human interaction loops is difficult when CLI output and responses are ephemeral terminal logs.
- **Proposed Solution**: Introduce `hitl-cli session record` and `hitl-cli session replay <session_id>` commands to capture structured event logs (prompts, timings, choices, responses) of CLI/SDK sessions.
- **Business Value**: Accelerates developer onboarding and shortens debugging cycles for AI workflow developers.
- **Effort Estimate**: S

---

## IDEA-435: Automated JWT/OAuth Token Pre-Fetch Daemon for Background CLI Jobs
- **Category**: Feature
- **Problem**: Long-running background processes or CI/CD pipelines fail when cached OAuth access tokens expire during overnight execution without an interactive browser.
- **Proposed Solution**: Add a lightweight background daemon process (`hitl-cli daemon --refresh`) that proactively monitors and refreshes OAuth 2.1 tokens using stored refresh tokens before expiration.
- **Business Value**: Eliminates token expiration job failures in automated environments, improving CI/CD and agent execution reliability.
- **Effort Estimate**: M

---

## IDEA-436: Configurable Webhook & Slack Event Forwarder in E2EE Proxy Mode
- **Category**: Integration
- **Problem**: Teams want team-wide visibility when a critical human approval is requested by an autonomous agent, but current notifications only target the individual mobile device.
- **Proposed Solution**: Allow the local `hitl-cli proxy` mode to emit localized event webhooks or Slack notifications upon prompt dispatch and receipt of human approval.
- **Business Value**: Increases enterprise organizational visibility into high-impact agent operations without exposing plain-text payload secrets to central log servers.
- **Effort Estimate**: M

---

## IDEA-437: Deterministic Response Schema Validation for Structured Choice Outputs
- **Category**: Tech Debt
- **Problem**: When human operators respond via free-form text or custom choices, agents receiving the SDK response must manually parse and validate response format consistency.
- **Proposed Solution**: Add Pydantic and JSON-Schema validation to `hitl.request_input()` in the Python SDK, guaranteeing that the returned human response matches expected structural types or choices before returning to caller.
- **Business Value**: Reduces edge-case crash risks in autonomous agent loops due to unexpected human input formatting.
- **Effort Estimate**: S

---

## IDEA-438: Adaptive Exponential Backoff & Connection Health Probing in Stdio Proxy
- **Category**: Performance
- **Problem**: Temporary network disruptions cause the MCP stdio proxy to fail fast or hang agent processes during model execution.
- **Proposed Solution**: Implement adaptive reconnection logic with ping/pong health probes and state recovery in `proxy_server.py`. If network drops, the proxy buffers outgoing MCP requests locally while attempting background reconnection.
- **Business Value**: Prevents agent task crashes during transient mobile or network disconnects, raising agent operational SLA.
- **Effort Estimate**: M

---

## IDEA-439: Granular CLI Scope & Permissions Policy Profiles
- **Category**: Security
- **Problem**: Different agents or automation scripts running on a machine share a single stored credential profile with unrestricted request privileges.
- **Proposed Solution**: Introduce sub-profile scoping (`hitl-cli profile create --scope notify-only`) that restricts specific CLI keys or sub-tokens to explicit commands (e.g. `notify` only, or restricted prompt tags).
- **Business Value**: Enforces defense-in-depth principles across multi-agent local environments, mitigating malicious or malfunctioning agent actions.
- **Effort Estimate**: M

---

## IDEA-440: Interactive Shell Mode with Tab Auto-Execution (`hitl-cli shell`)
- **Category**: UX
- **Problem**: Developers repeatedly testing or managing HITL requests from the terminal must continuously type multi-flag `hitl-cli` commands.
- **Proposed Solution**: Create a REPL shell (`hitl-cli shell`) with persistent session context, prompt history, auto-completion, and shortcuts for quick approvals and notification sends.
- **Business Value**: Improves developer productivity and interactive testing velocity for engineers building HITL-powered workflows.
- **Effort Estimate**: S

---

## IDEA-441: Zero-Overhead Ephemeral SDK Memory Caching for Request Statuses
- **Category**: Performance
- **Problem**: High-frequency SDK calls polling for request status generate redundant HTTP network roundtrips to the relay.
- **Proposed Solution**: Integrate an in-memory TTL cache into `api_client.py` for request status and metadata checks, short-circuiting duplicate HTTP GET calls within microsecond intervals.
- **Business Value**: Reduces network bandwidth, API rate-limit utilization, and response latency for rapid-polling agent implementations.
- **Effort Estimate**: S

---

## IDEA-442: Hierarchical Multi-User Escalation Policy in Python SDK
- **Category**: Feature
- **Problem**: If the primary human user does not respond to an urgent HITL request within a timeout, agent execution stalls indefinitely.
- **Proposed Solution**: Add escalation chain support to `hitl.request_input(..., timeout=300, escalate_to=["backup_user_id"])`, automatically routing unanswered prompts to backup users or designated secondary channels upon primary timeout.
- **Business Value**: Protects time-critical business processes from blocking when key decision-makers are unavailable.
- **Effort Estimate**: L

---

## IDEA-443: Automated Security Audit Log & Redaction Filter for CLI Operations
- **Category**: Security
- **Problem**: Agent prompts containing sensitive access tokens or private credentials might be saved into unencrypted local log files or shell histories.
- **Proposed Solution**: Add an automatic secret scanning and redaction middleware to `hitl-cli` logging that masks common API keys, JWTs, and passwords before writing to disk or stdout.
- **Business Value**: Prevents accidental credential leaks in client logs, fulfilling compliance and security auditing requirements.
- **Effort Estimate**: S

---

## IDEA-444: Native Python Async Context Managers for Managed HITL Sessions
- **Category**: Tech Debt
- **Problem**: Managing cleanup, error handling, and completion notifications across complex SDK call sequences requires repetitive try/finally blocks.
- **Proposed Solution**: Implement async context managers in the Python SDK (e.g., `async with hitl.session("Database Backup") as sess:`) that automatically handle start notifications, heartbeats, and error reporting.
- **Business Value**: Streamlines SDK adoption for Python agent developers with cleaner, less error-prone code patterns.
- **Effort Estimate**: S

---

## IDEA-445: Multi-Environment Relay Profile Switching (`hitl-cli env switch`)
- **Category**: UX
- **Problem**: Engineers testing across local, staging, and production HITL relay servers must manually overwrite environment variables or edit config files.
- **Proposed Solution**: Add environment management commands (`hitl-cli env list`, `hitl-cli env switch staging`) to switch server URLs, OAuth client IDs, and keys seamlessly.
- **Business Value**: Simplifies multi-environment developer workflows, reducing deployment misconfiguration risks.
- **Effort Estimate**: S

---

## IDEA-446: Cross-Platform System Tray Status Indicator for MCP Proxy
- **Category**: UX
- **Problem**: When running `hitl-cli proxy` in background developer setups, users cannot easily check proxy health, active requests, or connected agent status without inspecting process lists.
- **Proposed Solution**: Provide an optional desktop system tray applet (`hitl-cli proxy --tray`) showing real-time proxy status, pending human approval badges, and quick toggles.
- **Business Value**: Enhances developer awareness and convenience during multi-agent interactive coding sessions.
- **Effort Estimate**: M

---

## IDEA-447: Standardized Pre-Commit Hook for CLI Secrets & Schema Validation
- **Category**: Tech Debt
- **Problem**: Developer projects using `hitl-cli` configuration files or embedded keys occasionally commit plaintext credentials or invalid JSON settings to git repos.
- **Proposed Solution**: Ship a pre-commit hook (`hitl-cli install-hook`) that automatically validates local `.hitl/config.toml` files and scans for exposed API keys prior to git commits.
- **Business Value**: Safeguards enterprise repos from committing sensitive credentials, maintaining repository security hygiene.
- **Effort Estimate**: S
