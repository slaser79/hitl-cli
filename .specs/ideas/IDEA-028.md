# Ideas Batch — hitl-cli (Batch 34)

## IDEA-493: Interactive File Patch Applicator with Selective Line-Level Discard (`hitl-cli patch`)
- **Category**: Feature
- **Problem**: When an agent proposes a complex multi-file code diff, human approvers often want to accept the majority of changes while rejecting or tweaking specific lines before letting the agent proceed.
- **Proposed Solution**: Introduce `hitl-cli patch apply <request_id>` and SDK support allowing reviewers to interactively toggle hunk inclusions (or edit inline in `$EDITOR`) before returning the modified patch back to the waiting agent. The agent receives the filtered patch payload and continues execution with the user's modifications applied.
- **Business Value**: Drastically cuts iteration cycles by letting humans refine agent code suggestions in-flight rather than executing full retry prompts.
- **Effort Estimate**: M

---

## IDEA-494: Automated Hardware Security Module (HSM) & PKCS#11 Provider Bridge for E2EE Signing
- **Category**: Security
- **Problem**: Enterprise and sovereign environments require private cryptographic keys to remain inside hardware security modules (HSM) or smartcards (YubiKey/PIV) rather than stored as plaintext software keys on disk.
- **Proposed Solution**: Add PKCS#11 and FIPS 140-2/3 cryptographic provider integration into `crypto.py` (`hitl-cli crypto --provider pkcs11:/usr/lib/libykcs11.so`), enabling `hitl-cli` to perform E2EE payload signing and key derivation directly within hardware modules.
- **Business Value**: Unlocks high-compliance enterprise, banking, and government defense contracts that forbid software-only private key storage on agent host machines.
- **Effort Estimate**: M

---

## IDEA-495: Real-Time Human Reviewer Presence & Typing Indicator in CLI/SDK (`--presence`)
- **Category**: UX
- **Problem**: Autonomous agents and developers waiting on a terminal prompt have no indication whether a human has opened the push notification, is currently reading the prompt, or is actively typing a response on their mobile device.
- **Proposed Solution**: Implement bidirectional presence heartbeats (`viewed`, `typing`, `idle`) through relay WebSockets/SSE into `hitl-cli request` and `HITL.request_input()`. The CLI renders an active animated status indicator showing "Human opened notification..." and "Human is typing...", giving developers immediate visual feedback.
- **Business Value**: Reduces developer anxiety and unnecessary aborts during long wait periods, making human-in-the-loop interactions feel seamless and collaborative.
- **Effort Estimate**: S

---

## IDEA-496: Connection Warm-Up & Background SSL/TLS Pre-Handshaking on CLI Startup
- **Category**: Performance
- **Problem**: High-frequency CLI invocations within tight shell scripts or CI hooks pay full TCP/TLS handshaking latencies (150-300ms) on every single `hitl-cli` command invocation.
- **Proposed Solution**: Add a lightweight persistent background transport worker or TCP Fast Open (TFO) connection pre-warmer in `api_client.py` that keeps authenticated keepalive sockets ready for immediate dispatch.
- **Business Value**: Cuts invocation latency for shell scripts and hooks by over 60%, delivering sub-50ms HITL prompt dispatches.
- **Effort Estimate**: S

---

## IDEA-497: Unified Event-Driven Hook Architecture with Async Lifecycle Middleware
- **Category**: Tech Debt
- **Problem**: Existing hook implementations (`review_and_continue.py`, `codex_notify.py`) contain duplicated subprocess piping, error formatting, and custom CLI invocation logic.
- **Proposed Solution**: Refactor `hitl_cli/hooks/` into an extensible middleware pipeline (`HookPipeline`, `HookEventContext`) with standardized lifecycle hooks for `pre_request`, `post_response`, `on_timeout`, and `on_error`. All agent-specific hooks (Claude Code, Codex, Cursor, Antigravity) inherit from this unified pipeline.
- **Business Value**: Slashes ongoing maintenance burden across agent hook integrations and eliminates subtle regressions when new hook types are added.
- **Effort Estimate**: M

---

## IDEA-498: Native VS Code & Cursor Extension Language Server Protocol (LSP) Bridge
- **Category**: Integration
- **Problem**: Developers writing code in VS Code or Cursor currently have to switch context to their terminal or mobile phone to interact with HITL agent prompts during editing sessions.
- **Proposed Solution**: Build a lightweight LSP/VS Code extension bridge daemon (`hitl-cli lsp`) that intercepts local MCP tool calls and renders native VS Code notification banners, inline diff decorations, and action buttons directly in the editor window.
- **Business Value**: Deepens developer workflow stickiness by embedding HITL approvals directly inside the most popular IDEs.
- **Effort Estimate**: M

---

## IDEA-499: Hierarchical Multi-Party Consensus & Quorum Approvals (`--quorum`)
- **Category**: Feature
- **Problem**: High-stakes production actions (e.g. database schema drops, infrastructure provisioning, financial trades) require approvals from multiple distinct stakeholders (e.g. 2 of 3 tech leads) rather than a single individual.
- **Proposed Solution**: Extend `hitl-cli request` with `--quorum 2/3 --approver-group leads` syntax, routing the request to all designated team members and tracking concurrent approvals. The CLI waits until the threshold is satisfied or rejected by a veto before returning consensus status to the agent.
- **Business Value**: Eliminates single-operator risk on catastrophic autonomous actions and satisfies enterprise SOC2 multi-party authorization requirements.
- **Effort Estimate**: M

---

## IDEA-500: Ephemeral Sandboxed Token Scoping with Dynamic Time-to-Live (`--token-ttl`)
- **Category**: Security
- **Problem**: Sub-agents and spawned worker processes often inherit long-lived credentials, risking credential compromise if an agent execution environment is leaked or compromised.
- **Proposed Solution**: Introduce `hitl-cli auth mint-ephemeral --ttl 15m --max-requests 5` to dynamically generate temporary, scope-constrained JWT tokens derived from the main session. Ephemeral tokens automatically self-destruct once their TTL expires or request quota is exhausted.
- **Business Value**: Minimizes the blast radius of sub-agent security breaches in untrusted execution environments.
- **Effort Estimate**: S

---

## IDEA-501: Rich Markdown & ANSI Code Syntax Highlighting in Terminal Interactive Mode
- **Category**: UX
- **Problem**: When agents send long structured markdown, code snippets, or error traces to the terminal via `hitl-cli`, standard terminal output lacks syntax formatting, making complex decisions hard to read.
- **Proposed Solution**: Integrate Rich's markdown, code lexer, and panel rendering into `hitl-cli request` and `hitl-cli notify`, rendering prompts with syntax-highlighted code blocks, tables, and collapsible metadata blocks.
- **Business Value**: Increases human reviewer comprehension speed and accuracy when reviewing technical code prompts in the terminal.
- **Effort Estimate**: S

---

## IDEA-502: Client-Side Streaming Response Aggregator & Token De-duplication Cache
- **Category**: Performance
- **Problem**: Multi-turn agent loops asking repetitive structured clarifications frequently send nearly identical system context and prompt headers, wasting relay bandwidth and memory.
- **Proposed Solution**: Implement an in-memory token trie and LZ4 payload dictionary in `ApiClient` that caches common prompt headers and context templates across requests within the same process session.
- **Business Value**: Cuts payload transfer sizes by up to 70% in high-frequency multi-turn agent loops, lowering relay infrastructure costs.
- **Effort Estimate**: M

---

## IDEA-503: Terraform & OpenTofu Provider Plugin for Infrastructure Approval Gates (`terraform-provider-hitl`)
- **Category**: Integration
- **Problem**: Infrastructure-as-Code (IaC) pipelines in Terraform and OpenTofu lack an official, cryptographic human approval resource, forcing teams to rely on fragile external bash wrappers.
- **Proposed Solution**: Create a dedicated Go-based Terraform/OpenTofu provider powered by the `hitl-cli` protocol (`resource "hitl_approval" "prod_deploy"`), pausing `terraform apply` executions until an authorized human signs off on the plan diff via the HITL mobile app.
- **Business Value**: Positions HITL as the standard human-gate solution for cloud infrastructure automation, driving enterprise DevOps adoption.
- **Effort Estimate**: L

---

## IDEA-504: Comprehensive Mock Relay Server & Deterministic Async Fixtures for Pytest
- **Category**: Tech Debt
- **Problem**: Integration tests currently rely on patched HTTP responses or external network calls, causing intermittent test flakiness and slowing down CI execution.
- **Proposed Solution**: Build an in-process `MockRelayServer` fixture using `pytest-httpx` and `starlette` that simulates all relay endpoints, OAuth token exchanges, WebSocket presence, and E2EE ciphertext routing without network IO.
- **Business Value**: Delivers 10x faster local test execution and 100% deterministic CI passes, accelerating worker velocity.
- **Effort Estimate**: S

---

## IDEA-505: Voice-to-Text Audio Note Attachment Dispatch (`--audio-note`)
- **Category**: Feature
- **Problem**: Mobile approvers on the move often find typing detailed code feedback or complex rejection explanations on a mobile keyboard tedious, leading to terse or unhelpful rejections.
- **Proposed Solution**: Allow mobile responders to attach short audio notes or voice transcriptions to their HITL response, which `hitl-cli` downloads and presents to the agent/developer (with optional local Whisper transcription if audio-only).
- **Business Value**: Boosts human response depth and speed when reviewing agent tasks away from a keyboard, improving mobile user satisfaction.
- **Effort Estimate**: S

---

## IDEA-506: Cryptographic Audit Receipt Verification & Local Ledger Export (`hitl-cli receipt verify`)
- **Category**: Security
- **Problem**: Regulated enterprises require verifiable, tamper-evident proof that a human explicitly authorized a given agent action for compliance audits (SOC2, HIPAA, ISO 27001).
- **Proposed Solution**: Have `hitl-cli` store Ed25519-signed cryptographic approval receipts returned by the mobile client in a local append-only SQLite/JSON-LD audit ledger (`~/.hitl/audit_ledger.db`), with a CLI command `hitl-cli receipt verify <receipt_id>` that cryptographically proves timestamp, public key, and approved payload hash.
- **Business Value**: Provides legally defensible compliance evidence for automated AI agent operations, winning enterprise security audits.
- **Effort Estimate**: M

---

## IDEA-507: Configurable Interactive Prompt Timeout Countdown & Audible Warning Chime
- **Category**: UX
- **Problem**: When a CLI command has a strict timeout (`--timeout 60`), the user or terminal observer might not realize how much time remains before an automatic abort or default action occurs.
- **Proposed Solution**: Add an interactive terminal countdown progress bar with color-coded urgency (green > yellow > flashing red) and optional terminal bell chime (`\a`) at 10 seconds remaining to alert nearby developers.
- **Business Value**: Prevents accidental timeouts and abandoned requests when developers step away from their desks briefly.
- **Effort Estimate**: S
