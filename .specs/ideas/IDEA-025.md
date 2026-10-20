# Ideas Batch — hitl-cli (Batch 31)

## IDEA-448: Client-Side SHA-256 Idempotency Engine for Fault-Tolerant Agent Retries
- **Category**: Security
- **Problem**: When agent workflows crash or retry network requests, duplicate human approval prompts are dispatched to mobile devices for the exact same action.
- **Proposed Solution**: Implement deterministic SHA-256 payload hashing and local key caching in `hitl-cli` and SDK to inject `Idempotency-Key` headers on outgoing requests, short-circuiting duplicate prompts.
- **Business Value**: Prevents accidental duplicate execution of high-risk actions (e.g., financial transactions or server drops), protecting enterprise operational integrity.
- **Effort Estimate**: S

---

## IDEA-449: Single-Key Interactive Hotkey Binds in Terminal Approval Mode
- **Category**: UX
- **Problem**: Developers responding to interactive `hitl-cli ask` prompts in the terminal must type out complete text strings or navigate complex options.
- **Proposed Solution**: Enable numeric and single-character hotkeys (`[1]` Approve, `[2]` Reject, `[y/n]`) in interactive terminal prompts for instant single-keystroke input submission.
- **Business Value**: Accelerates developer response velocity and reduces friction during local multi-step agent debugging.
- **Effort Estimate**: S

---

## IDEA-450: Automatic Multi-Part Envelope Chunking for Large Context Diffs
- **Category**: Performance
- **Problem**: Large code diffs or diagnostic log outputs attached to HITL requests frequently exceed HTTP payload caps or push notification payload limits.
- **Proposed Solution**: Add client-side payload chunking to `hitl-cli` and SDK that splits large attachments into indexed envelope chunks with a master summary header before uploading to the relay.
- **Business Value**: Guarantees reliable delivery of heavy code diffs and detailed diagnostic contexts without payload truncation errors.
- **Effort Estimate**: M

---

## IDEA-451: Zero-Config Docker & Kubernetes Secret Mount Auto-Discovery
- **Category**: Integration
- **Problem**: Containerized AI agents running in cloud or Kubernetes environments lack access to host keyrings or desktop login sessions, causing auth failures without manual config boilerplate.
- **Proposed Solution**: Implement automatic environment sniffing in `hitl-cli` that auto-discovers mounted service account tokens or key secrets at `/var/run/secrets/hitl/` without explicit CLI flags.
- **Business Value**: Streamlines enterprise container deployment of HITL agents, lowering onboarding time for DevOps teams.
- **Effort Estimate**: M

---

## IDEA-452: Cryptographic Payload Signature Verification for Non-Repudiable Approvals
- **Category**: Security
- **Problem**: In high-security environments, agents receiving human responses must verify that responses were genuinely signed by an authorized key, preventing man-in-the-middle spoofing.
- **Proposed Solution**: Integrate asymmetric signature validation (Ed25519) into SDK response handlers, verifying that human approval digests match registered public keys before returning data to agents.
- **Business Value**: Guarantees cryptographic non-repudiation for high-stakes enterprise decisions like production releases or access grants.
- **Effort Estimate**: M

---

## IDEA-453: Local Shell Hook Plugin Framework for Post-Response Actions
- **Category**: Feature
- **Problem**: Developers want local tools (e.g., build systems or database syncs) to run immediately after a human approves or rejects a prompt, without coupling logic into the agent core.
- **Proposed Solution**: Support post-response lifecycle hooks in `.hitl/hooks.toml` (`on_approval`, `on_rejection`) that `hitl-cli` executes locally with response payload environment variables.
- **Business Value**: Enables seamless integration of HITL prompt outcomes into existing developer toolchains and local automation pipelines.
- **Effort Estimate**: S

---

## IDEA-454: Adaptive Priority Tagging & Emergency Push Escalation
- **Category**: Feature
- **Problem**: Urgent infrastructure alerts (e.g., database connection exhaustion) are queued equally with routine agent status notifications.
- **Proposed Solution**: Add `--priority [low|normal|urgent|critical]` flags to `hitl-cli request` and SDK methods, marking high-priority prompts to bypass batching and activate urgent push headers on the relay.
- **Business Value**: Reduces mean time to resolution (MTTR) for critical production incidents by prioritizing time-sensitive human intervention.
- **Effort Estimate**: S

---

## IDEA-455: Unified Workspace Profile Management & Auto-Switching (`hitl-cli profile`)
- **Category**: UX
- **Problem**: Developers working across multiple projects or clients must repeatedly overwrite environment variables or re-authenticate to change relay targets and API keys.
- **Proposed Solution**: Add profile commands (`hitl-cli profile create`, `hitl-cli profile switch`) with directory-level `.hitl-profile` auto-detection to isolate credentials per workspace.
- **Business Value**: Enhances developer productivity and eliminates cross-project credential leaks when managing multiple HITL environments.
- **Effort Estimate**: S

---

## IDEA-456: Microsecond-Precision Latency Telemetry for MCP Proxy Tracing
- **Category**: Performance
- **Problem**: Bottlenecks in agent execution loops are difficult to diagnose when transport latency between stdio serialization, relay roundtrips, and human response is unmeasured.
- **Proposed Solution**: Inject high-resolution timing markers (`x-hitl-latency-ms`) across proxy request cycles and add a `hitl-cli proxy stats` command to display real-time latency breakdowns.
- **Business Value**: Empowers agent developers to benchmark latency metrics and optimize agent-human interaction speed.
- **Effort Estimate**: S

---

## IDEA-457: Embedded Standalone Mock Relay Harness for Zero-Dependency CI Testing
- **Category**: Integration
- **Problem**: Integration tests for HITL-enabled AI agents require complex HTTP mocks or external network connections to real relay servers.
- **Proposed Solution**: Provide an embedded mock server (`hitl-cli mock-relay --port 8999 --auto-respond "Approved"`) that serves as a local HTTP/WebSocket endpoint returning scripted human responses in unit/CI tests.
- **Business Value**: Eliminates external service dependencies in CI test suites, increasing test reliability and build speeds.
- **Effort Estimate**: M

---

## IDEA-458: Automatic Pre-Flight PII and Secret Redaction Scanner for Attachments
- **Category**: Security
- **Problem**: AI agents sending log attachments or context snippets may accidentally leak sensitive configuration files (e.g., API keys, passwords, SSH private keys) to external mobile devices.
- **Proposed Solution**: Build a pre-flight regex redaction filter into `hitl-cli` attachment processing that scans for common API key signatures and automatically masks them before payload dispatch.
- **Business Value**: Prevents security breaches and compliance violations caused by unintended secret exposure in human notifications.
- **Effort Estimate**: S

---

## IDEA-459: Typer Standardization & Type-Annotated Subcommand Refactoring
- **Category**: Tech Debt
- **Problem**: Legacy subcommands in `hitl_cli` use raw Click decorators, leading to fragmented argument parsing logic and inconsistent type checking compared to modern Typer modules.
- **Proposed Solution**: Migrate all remaining Click CLI definitions to Typer with Pydantic validation, unifying parameter constraints and removing legacy Click wrapper code.
- **Business Value**: Improves codebase maintainability, reduces static analysis errors, and accelerates new feature development.
- **Effort Estimate**: S

---

## IDEA-460: Real-Time Server-Sent Events (SSE) Proxy Transport Listener
- **Category**: Performance
- **Problem**: Long-polling HTTP polling in `hitl-cli proxy` consumes extra network sockets and introduces latency when awaiting human approvals.
- **Proposed Solution**: Add a Server-Sent Events (SSE) transport listener to `proxy_server.py` to establish a persistent streaming connection with the relay for instant response pushes.
- **Business Value**: Reduces notification delivery latency from seconds to milliseconds while lowering connection overhead.
- **Effort Estimate**: M

---

## IDEA-461: Interactive Terminal Preview Generator for Markdown & Attachment Payloads
- **Category**: UX
- **Problem**: Developers cannot easily inspect how complex markdown diffs or attached files will look to the human reviewer before dispatching the request.
- **Proposed Solution**: Add a preview command (`hitl-cli preview <payload.json>`) that renders formatted terminal markdown or opens a quick local browser preview of the human mobile notification UI.
- **Business Value**: Boosts developer confidence and payload quality before sending requests to human decision-makers.
- **Effort Estimate**: S

---

## IDEA-462: Proactive OAuth Token Expiration Warning and Auto-Refresh Banner
- **Category**: UX
- **Problem**: CLI commands executed near access token expiration fail abruptly mid-operation without clear diagnostic feedback.
- **Proposed Solution**: Calculate OAuth token TTL before command execution; if expiration is within 5 minutes, emit a non-intrusive warning header and trigger silent background token refresh.
- **Business Value**: Prevents sudden CLI command failures due to expired credentials, providing a seamless user experience.
- **Effort Estimate**: S
