# Ideas Batch — hitl-cli (Batch 37)

## IDEA-538: Serverless Asynchronous Webhook Callback Dispatch (`hitl-cli request --callback-url`)
- **Category**: Integration
- **Problem**: Cloud-native agent workers running on serverless runtimes (AWS Lambda, Google Cloud Run, Temporal, or LangGraph Cloud) cannot maintain long-lived polling processes without incurring steep idle compute bills and hitting execution timeout limits.
- **Proposed Solution**: Add `--callback-url <url>` and `--callback-secret <token>` to `hitl-cli request` and SDK methods. When specified, the relay accepts the prompt asynchronously, returns an immediate `202 Accepted` with request metadata, and posts the HMAC-SHA256 signed human decision directly to the callback endpoint once the reviewer approves or rejects on their mobile device.
- **Business Value**: Unlocks serverless and event-driven cloud agent architectures, eliminating the prohibitive cost of idle compute hours while waiting for human responses.
- **Effort Estimate**: M

---

## IDEA-539: Live Session Token & Financial Spend Telemetry Card in Review Prompts (`--session-cost`)
- **Category**: UX
- **Problem**: Human reviewers approving high-impact autonomous agent actions on mobile currently have zero visibility into how many model tokens or cloud dollars the agent session has consumed.
- **Proposed Solution**: Introduce `--session-cost <USD>`, `--tokens-used <int>`, and `--model <name>` parameters to `hitl-cli request` and the SDK payload envelope. The mobile app renders an interactive financial telemetry pill above the action buttons, displaying accumulated session spend and warning reviewers if the proposed operation exceeds budget thresholds.
- **Business Value**: Protects organizations from unexpected AI model billing overruns by giving human operators immediate financial visibility before granting execution approvals.
- **Effort Estimate**: S

---

## IDEA-540: Multi-Recipient Team Broadcast with First-Response Resolution (`--broadcast --team`)
- **Category**: Feature
- **Problem**: Directing an urgent agent approval prompt to a single developer causes severe workflow bottlenecks if that individual is away from their desk or phone.
- **Proposed Solution**: Implement multi-recipient request dispatching supporting `--team <team_id>` or `--reviewers <user1,user2,...>` combined with a `--policy first-wins` resolution mode. The relay broadcasts push notifications to all authorized team members simultaneously, unblocks the agent as soon as the first human answers, and instantly dismisses or clears the pending prompt on all other devices.
- **Business Value**: Slashes agent blockage and idle wait times across engineering teams by ensuring prompts are resolved by whoever is available first.
- **Effort Estimate**: M

---

## IDEA-541: Fast Unix Domain Socket (UDS) Transport for MCP Proxy Server (`hitl-cli proxy --socket`)
- **Category**: Performance
- **Problem**: Communicating with the MCP proxy exclusively over stdio pipes risks pipe deadlocks, buffer saturation, and JSON-RPC message corruption when external commands or subagents emit unexpected characters to stdout.
- **Proposed Solution**: Add `--socket <path>` to `hitl-cli proxy` allowing client agents (Claude Code, Google Antigravity, Cursor) to connect via local Unix domain sockets (or Windows named pipes). The socket transport bypasses standard I/O streams entirely, eliminating stdio pollution crashes and boosting message throughput between the local harness and the HITL proxy daemon.
- **Business Value**: Hardens agent integration stability and eliminates frustrating tool-call parsing failures caused by contaminated stdout streams.
- **Effort Estimate**: S

---

## IDEA-542: Interactive Multi-Field Form Schema Prompting (`hitl-cli request --form`)
- **Category**: Feature
- **Problem**: Agents requiring several configuration inputs (such as choosing an AWS region, selecting instance sizes, and entering a cluster name) are forced into tedious multi-turn question loops with human reviewers.
- **Proposed Solution**: Add `--form <schema.json>` support to `hitl-cli request` accepting a declarative JSON schema defining input fields (text inputs, dropdown menus, toggles, and numeric steppers). The mobile application dynamically renders an interactive form card, performs client-side field validation, and returns a structured JSON dictionary to the CLI/SDK in a single atomic turn.
- **Business Value**: Accelerates complex approvals and reduces human context switching by condensing multi-question agent interrogations into a single, cohesive form submission.
- **Effort Estimate**: M

---

## IDEA-543: Automated Cross-Platform Hook Installer and Diagnostic CLI (`hitl-cli hook install`)
- **Category**: UX
- **Problem**: Installing the stop hook (`review_and_continue.py`) currently demands tedious manual JSON editing of hidden agent configuration files (`~/.claude/config.json`, `.gemini/settings.json`, `.cursor/`), frequently resulting in invalid path errors and broken hooks.
- **Proposed Solution**: Implement `hitl-cli hook install [claude|antigravity|cursor|copilot]` to auto-detect installed agent environments, write executable wrapper scripts with absolute paths, validate shell permissions, and perform an automated dry-run round-trip test. A complementary `hitl-cli hook status` and `uninstall` command provides full lifecycle management.
- **Business Value**: Eliminates the highest-friction onboarding hurdle for developers, reducing hook setup time from 20 minutes to under 5 seconds.
- **Effort Estimate**: S

---

## IDEA-544: Zero-Trust Ephemeral E2EE Sessions with Automatic Key Shredding (`--ephemeral-keypair`)
- **Category**: Security
- **Problem**: Encrypting sensitive review prompts with static long-term workstation keys leaves past interactions vulnerable to retrospective decryption if a developer's workstation disk is compromised or imaged.
- **Proposed Solution**: Implement true Perfect Forward Secrecy (PFS) in `crypto.py` by generating an ephemeral, single-turn X25519 keypair for each request transaction. The CLI exchanges ephemeral public keys with the mobile client, completes symmetric payload encryption/decryption, and immediately zeroes the memory buffer holding the private key using `sodium_memzero` upon response completion.
- **Business Value**: Guarantees enterprise-grade forward secrecy for high-stakes credentials and proprietary code, preventing retrospective decryption even if physical workstation storage is leaked.
- **Effort Estimate**: M

---

## IDEA-545: SDK Asynchronous Batch Notification Dispatcher (`HITL.notify_many`)
- **Category**: Performance
- **Problem**: Agent workflows generating multiple progress notifications or log events issue sequential HTTP requests that block the main agent event loop and introduce cumulative network latency.
- **Proposed Solution**: Add `await hitl.notify_many([...])` and background queue auto-flushing to the Python SDK. Notifications are packed into a single compressed JSON batch request sent to the relay in one network round-trip, with non-blocking background workers ensuring zero delay to agent reasoning loops.
- **Business Value**: Cuts network overhead by up to 80% when agents stream progress events, boosting end-to-end task execution speed.
- **Effort Estimate**: S

---

## IDEA-546: Machine-Readable Structured Output Formats across CLI Commands (`--format json|quiet`)
- **Category**: UX
- **Problem**: `hitl-cli` commands print colored ANSI strings intended solely for human eyes, making deterministic output parsing in bash automation, Makefile recipes, and jq pipelines brittle and prone to breakage.
- **Proposed Solution**: Add universal `--format [json|ndjson|plain|quiet]` and `--output-file <path>` flags across all Typer commands (`request`, `notify`, `status`, `history`). In `--format json` mode, all standard logs and color codes are redirected to stderr, leaving stdout strictly reserved for clean, schema-validated JSON responses.
- **Business Value**: Simplifies embedding `hitl-cli` into devops automation, CI/CD pipelines, and shell scripts without brittle regex string scraping.
- **Effort Estimate**: S

---

## IDEA-547: FastMCP Request Lifecycle Middleware Pipeline Architecture
- **Category**: Tech Debt
- **Problem**: The MCP proxy (`proxy_handler_v2.py`) tightly couples protocol message parsing with tool execution, lacking standard lifecycle interceptor points for security inspection, request timing, or payload transformation.
- **Proposed Solution**: Refactor `proxy_handler_v2.py` to implement an ASGI-style middleware pipeline with standard `process_request` and `process_response` lifecycle hooks. Core cross-cutting features—such as PII scrubbing, request latency metrics, custom audit logging, and payload size guards—can be cleanly implemented as pluggable middleware layers.
- **Business Value**: Drastically reduces proxy maintenance complexity and enables clean extension points for enterprise compliance and observability policies.
- **Effort Estimate**: M

---

## IDEA-548: Graceful Prompt Revocation on Agent Interruption & Signal Trapping (`--on-interrupt`)
- **Category**: UX
- **Problem**: When a developer aborts a CLI run with Ctrl+C or an orchestrator sends SIGTERM to an agent process, active prompts linger on the mobile app until natural timeout, leading to confusion and invalid human approvals on aborted tasks.
- **Proposed Solution**: Equip `hitl-cli` with a POSIX signal trap (`SIGINT`, `SIGTERM`, `SIGHUP`) that intercepts abrupt termination while waiting on a human response. The signal handler dispatches an immediate revocation request (`DELETE /requests/{id}`) to the relay and cleanly tears down local sockets before exiting with code 130.
- **Business Value**: Eliminates phantom notifications on mobile devices, ensuring human operators never waste effort reviewing work that has already been terminated.
- **Effort Estimate**: S

---

## IDEA-549: Configurable Network Partition Fallback Policy (`--on-disconnect approve|reject|abort`)
- **Category**: Feature
- **Problem**: When automated nighttime builds or CI runs encounter transient relay unavailability, agent jobs hang indefinitely or crash unexpectedly without deterministic fallback paths.
- **Proposed Solution**: Introduce `--on-disconnect [fail|approve|reject|default:<val>]` and `--fallback-timeout <seconds>` options in `ApiClient` and CLI commands. If relay connectivity cannot be established within the fallback timeout, the CLI logs a structured fallback warning and returns the configured fallback response with an audit trail note.
- **Business Value**: Safeguards automated continuous integration pipelines from deadlocking during third-party network outages or maintenance windows.
- **Effort Estimate**: S

---

## IDEA-550: Local Keychain Integration for Service Credentials (`hitl-cli secret store`)
- **Category**: Security
- **Problem**: Developers frequently leave raw `HITL_API_KEY` credentials in unencrypted dotfiles (`.env`, `.bashrc`) or shell history, creating credential exposure risks on shared or backed-up machines.
- **Proposed Solution**: Introduce `hitl-cli secret [store|get|delete]` leveraging the OS native keyring (macOS Keychain, Windows Credential Manager, and Linux SecretService / libsecret). The CLI and SDK prioritize credentials stored in the OS keyring over plaintext files, encrypting service keys at rest using system-level access controls.
- **Business Value**: Eradicates plaintext credential storage on developer workstations, satisfying stringent enterprise data security and compliance requirements.
- **Effort Estimate**: M

---

## IDEA-551: Pytest Test Fixture & Mock Relay Harness (`pytest-hitl`)
- **Category**: Integration
- **Problem**: Third-party developers and agent framework maintainers building on top of the `hitl-cli` SDK currently lack official test fixtures, forcing them to write complex monkeypatches or skip testing human-in-the-loop paths entirely.
- **Proposed Solution**: Publish a standalone test kit module `hitl_cli.testing` providing a `hitl_mock` pytest fixture and in-memory mock relay server. Tests can declare scripted human responses (e.g. `hitl_mock.expect_prompt("Approve PR?").respond("Yes")`) and assert notification delivery without any network calls or relay dependencies.
- **Business Value**: Removes the largest friction point for third-party SDK adoption by enabling agent developers to write reliable, deterministic automated tests for their HITL logic.
- **Effort Estimate**: S

---

## IDEA-552: Mobile Push Notification Priority & Custom Alert Sound Profiles (`--priority urgent|high|low`)
- **Category**: UX
- **Problem**: All mobile approval notifications currently trigger the exact same notification chime on reviewer phones, causing urgent production blockers to be overlooked among routine informational updates.
- **Proposed Solution**: Add `--priority [critical|high|normal|low]` and `--sound [alarm|ping|subtle]` options to `hitl-cli request` and notifications. On supported iOS and Android devices, the relay routes high-priority prompts to dedicated critical alert notification channels with custom sound profiles and persistent banners that bypass system Do Not Disturb when authorized.
- **Business Value**: Drastically reduces Mean Time to Respond (MTTR) for critical production incidents and deployment blocks by alerting human operators with appropriate urgency.
- **Effort Estimate**: S
