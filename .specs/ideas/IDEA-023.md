# Ideas Batch — hitl-cli (Batch 29)

## IDEA-418: Zero-Trust Per-Session Approval Delegation Tokens
- **Category**: Security
- **Problem**: When delegating approval tasks to sub-agents or lower-tier human operators, grant scope cannot currently be limited to a single request session or time window.
- **Proposed Solution**: Implement short-lived, cryptographically signed delegation tokens in `hitl-cli` that restrict secondary approvers to specific request IDs and expirations. The SDK will validate token signatures locally before forwarding approvals to the relay.
- **Business Value**: Reduces organizational security risks by enforcing fine-grained least-privilege delegation for high-stakes human approvals.
- **Effort Estimate**: M

---

## IDEA-419: Native OpenTelemetry Tracing Integration for Agent-HITL Interactions
- **Category**: Integration
- **Problem**: AI agent framework operators lack visibility into latency, queue times, and response bottlenecks across the human-in-the-loop lifecycle.
- **Proposed Solution**: Inject W3C Trace Context and OpenTelemetry span exports into `api_client.py` and `mcp_client.py`. Every request sent to the HITL relay will automatically generate spans tracking proxy overhead, relay delay, and human response latency.
- **Business Value**: Enables enterprise customers to monitor and optimize human response SLAs within their existing observability pipelines.
- **Effort Estimate**: M

---

## IDEA-420: Multi-Tenant Vault Integration for Secret-Masked HITL Prompts
- **Category**: Security
- **Problem**: Agents frequently pass sensitive parameters (API keys, database URIs, PII) in prompt payloads, risking exposure on mobile notification screens and log files.
- **Proposed Solution**: Add auto-redaction rules and HashiCorp Vault / AWS Secrets Manager integration in `hitl-cli`. Prompts are scanned before submission, replacing detected secrets with secure vault reference URIs that only authorized human devices can resolve.
- **Business Value**: Prevents catastrophic data leaks and regulatory non-compliance when exposing agent prompts to external notification channels.
- **Effort Estimate**: L

---

## IDEA-421: Interactive Asynchronous Polling Mode with WebSocket Push Fallback
- **Category**: Performance
- **Problem**: Polling the relay REST API for long-running approval requests incurs unnecessary network bandwidth and introduces up to several seconds of response latency.
- **Proposed Solution**: Upgrade `api_client.py` to negotiate a WebSocket connection for real-time push delivery of human approval responses, seamlessly falling back to exponential HTTP polling if WebSocket upgrade fails.
- **Business Value**: Reduces agent waiting latency by up to 90% and cuts server bandwidth costs for high-volume HITL deployments.
- **Effort Estimate**: M

---

## IDEA-422: Automated CLI Crash Diagnostic Dump and Self-Healing Recovery
- **Category**: UX
- **Problem**: Unexpected unhandled exceptions or broken environment configs in CLI execution can crash background agent scripts without structured diagnostic capture.
- **Proposed Solution**: Catch uncaught CLI exceptions in `main.py` top-level handler, automatically dumping a sanitized state snapshot (environment, config hash, last request state) to `.hitl/crash.json` and presenting actionable recovery suggestions.
- **Business Value**: Decreases support overhead and developer frustration by accelerating bug diagnosis and automated agent self-recovery.
- **Effort Estimate**: S

---

## IDEA-423: Agent-Side Multi-Choice Response Timeout and Fallback Actions
- **Category**: Feature
- **Problem**: If a human operator does not respond within a deadline, autonomous agent workflows freeze indefinitely waiting for input.
- **Proposed Solution**: Introduce `--timeout-action` and SDK-level `timeout_policy` configurations (e.g., `default_choice`, `abort`, or `escalate`). When the deadline expires, `hitl-cli` automatically executes the designated fallback action and logs the expiration event.
- **Business Value**: Prevents autonomous agent pipelines from getting stuck indefinitely on un-answered human prompts, ensuring system continuity.
- **Effort Estimate**: S

---

## IDEA-424: Offline Notification Queue Compression and Batch Sync Protocol
- **Category**: Performance
- **Problem**: Intermittent network disconnects cause agents to lose notification events or flood the relay with individual retries upon reconnect.
- **Proposed Solution**: Create an offline SQLite buffer in `hitl-cli` that stores pending notifications locally during network partitions. Upon reconnection, notifications are compressed (gzip/zstd) and delivered in a single HTTP batch payload.
- **Business Value**: Guarantees reliable event delivery in poor connectivity environments while minimizing network resource usage.
- **Effort Estimate**: M

---

## IDEA-425: Dynamic Rich-Text & Media Markdown Rendering for CLI Approvals
- **Category**: UX
- **Problem**: Terminal-based HITL approval prompts render plain text markdown poorly, making complex tables, diffs, and formatted text difficult for developers to inspect locally.
- **Proposed Solution**: Integrate `rich` library formatting into `hitl-cli` terminal prompts for colorful inline diffs, tables, and syntax-highlighted code snippets. Include terminal image preview rendering for supported terminals (Kitty, iTerm2, WezTerm).
- **Business Value**: Improves developer experience and decision speed when reviewing complex agent proposals directly from the terminal.
- **Effort Estimate**: M

---

## IDEA-426: Granular Config Schema Migration Engine
- **Category**: Tech Debt
- **Problem**: Upgrading `hitl-cli` across major versions with config file schema changes currently requires manual user config file edits or causes startup parsing errors.
- **Proposed Solution**: Implement a versioned schema migration framework in `config.py`. On startup, `hitl-cli` automatically detects legacy configuration schemas (`~/.hitl/config.json`) and migrates them safely with backup creation.
- **Business Value**: Eliminates breaking change friction for existing CLI users during version upgrades.
- **Effort Estimate**: S

---

## IDEA-427: FastMCP Proxy Dynamic Tool Registration & Discovery
- **Category**: Integration
- **Problem**: High-level AI agents (Claude Desktop, Gemini, Codex) cannot dynamically query available HITL approval templates or notification channels supported by the CLI.
- **Proposed Solution**: Extend `proxy_handler_v2.py` / `mcp_client.py` to dynamically register FastMCP tools based on workspace configuration policies (e.g., `hitl_ask_security`, `hitl_notify_slack`).
- **Business Value**: Unlocks contextual tool selection for LLM agents, ensuring agents invoke the exact HITL workflow required for the domain.
- **Effort Estimate**: M

---

## IDEA-428: Local Replay Debugger for Offline SDK Testing
- **Category**: UX
- **Problem**: Testing agent code that depends on `hitl-cli` human responses requires manual mobile interactions or complex mock setups for every test run.
- **Proposed Solution**: Build a `--record-session` and `hitl-cli replay <session.json>` tool. Developers can record real human responses once and replay them deterministically in automated unit/integration tests without hitting the live relay.
- **Business Value**: Accelerates agent developer iteration speed and enables robust offline test automation for HITL workflows.
- **Effort Estimate**: M

---

## IDEA-429: Hardware-Backed YubiKey/WebAuthn Approval Signature Verification
- **Category**: Security
- **Problem**: High-value production operations (e.g. database drops, financial transfers) require cryptographic proof of physical human presence, which standard password/JWT auth does not provide.
- **Proposed Solution**: Support WebAuthn / FIDO2 public key assertion verification in `hitl-cli crypto.py`. The CLI will verify that approval payloads carry a valid hardware-bound WebAuthn signature from an authorized YubiKey before returning success to the agent.
- **Business Value**: Meets stringent enterprise compliance requirements (SOC 2, ISO 27001) for critical infrastructure control by AI agents.
- **Effort Estimate**: L

---

## IDEA-430: Asynchronous PyNaCl Key Generation and Caching Worker
- **Category**: Performance
- **Problem**: Generating new PyNaCl asymmetric key pairs for E2EE sessions synchronously during request initialization adds up to 100-200ms latency to CLI invocations.
- **Proposed Solution**: Implement a background key pre-generation worker in `crypto.py` that maintains a secure local pool of pre-computed keypairs in memory. When an E2EE session starts, a keypair is consumed instantly without on-demand computation.
- **Business Value**: Reduces CLI request creation overhead for latency-sensitive real-time agent loops.
- **Effort Estimate**: S

---

## IDEA-431: Typer CLI Auto-Completion for Dynamic Configuration Options
- **Category**: UX
- **Problem**: Users must look up or copy-paste long command flags, profile names, and relay environment URLs when using `hitl-cli`.
- **Proposed Solution**: Add native shell auto-completion support (`bash`, `zsh`, `fish`) to `main.py` via Typer, dynamically completing profile names, notification tags, and active request IDs.
- **Business Value**: Elevates CLI polish to modern developer tooling standards, increasing terminal productivity and adoption.
- **Effort Estimate**: S

---

## IDEA-432: Standardized Cross-Language SDK Interoperability Test Suite
- **Category**: Tech Debt
- **Problem**: As non-Python SDK implementations (TypeScript/Go) are created, behavior discrepancies in E2EE encryption, payload serialization, and auth retry logic can cause cross-platform bugs.
- **Proposed Solution**: Create a language-agnostic conformance test suite (`tests/conformance/`) in JSON/YAML containing standard test vectors for E2EE encryption, OAuth PKCE flows, and JSON-RPC proxy payloads that all SDK implementations must pass.
- **Business Value**: Prevents fragmentation across multi-language SDK ecosystems and guarantees consistent security guarantees across platforms.
- **Effort Estimate**: M
