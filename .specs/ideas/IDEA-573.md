# Ideas Batch — hitl-cli (Batch 573)

## IDEA-643: Terraform & OpenTofu Infrastructure Plan Review and Apply Safety Gate (`hitl-tf-gate` / `hitl-cli tf-plan`)
- **Category**: Integration
- **Problem**: Autonomous DevOps agents running infrastructure-as-code (Terraform or OpenTofu) frequently apply destructive cloud modifications (destroying databases, altering security group CIDRs, deleting VPC gateways) without human verification because native IaC tools lack interactive mobile approval gates.
- **Proposed Solution**: Introduce a dedicated CLI wrapper `hitl-cli tf-plan` (and standalone binary `hitl-tf-gate`). The tool parses `terraform plan -json`, generates an executive blast-radius summary (resources added, modified, destroyed, and critical IAM/network changes), dispatches an interactive review card with diff previews to the mobile app, and releases the execution lock only when explicit human authorization is granted before proceeding to `terraform apply`.
- **Business Value**: Prevents catastrophic production outages, accidental cloud infrastructure deletions, and runaway billing incidents caused by unverified autonomous agent infrastructure actions.
- **Effort Estimate**: S

---

## IDEA-644: Hardware Security Key (FIDO2 / WebAuthn) Step-Up Authentication for High-Risk Actions (`--require-webauthn`)
- **Category**: Security
- **Problem**: When autonomous agents request approval for high-risk operations (e.g. transferring production databases, minting long-lived root credentials, issuing treasury transactions), a compromised mobile device or stolen device PIN could allow unauthorized human approvals.
- **Proposed Solution**: Implement step-up WebAuthn and FIDO2 hardware token verification via `hitl-cli request --risk-level critical --require-webauthn`. The CLI requests that the relay and mobile client enforce a physical NFC or USB hardware security key tap (e.g. YubiKey) before signing the response, incorporating the hardware attestation signature into the decrypted payload verified locally by `crypto.py`.
- **Business Value**: Eliminates physical device compromise and insider threat vectors for enterprise-critical agent operations, satisfying strict zero-trust mandates in banking, healthcare, and defense.
- **Effort Estimate**: M

---

## IDEA-645: Interactive Terminal Context Selector & Git Diff Picker (`hitl-cli request --select-context`)
- **Category**: UX
- **Problem**: When developers or agents compose complex review requests from the command line, manually typing file paths, diff ranges, or commit hashes into `--prompt` arguments is tedious, error-prone, and frequently omits critical uncommitted modifications.
- **Proposed Solution**: Implement a lightweight curses-based interactive context picker in `hitl-cli request --select-context`. The terminal interface presents a live checklist of modified files, staged diffs, recent commit logs, and terminal outputs, allowing the operator to selectively bundle syntax-highlighted context attachments into the prompt payload with simple spacebar toggles.
- **Business Value**: Drastically reduces friction when authoring rich contextual review prompts from developer terminals, increasing reviewer clarity and speeding up approval turnarounds.
- **Effort Estimate**: S

---

## IDEA-646: Kernel-Level Socket Pooling & Zero-Allocation HTTP/3 (QUIC) Transport in `ApiClient` (`--http3`)
- **Category**: Performance
- **Problem**: Autonomous agents operating in mobile, cellular, or multi-cloud network topologies suffer from TCP head-of-line blocking, high connection establishment handshakes, and packet loss delays during continuous long-polling and SSE notification streaming.
- **Proposed Solution**: Equip `ApiClient` with native HTTP/3 (QUIC) transport support leveraging `httpx` with `aioquic`. HTTP/3 enables 0-RTT connection resumption, multiplexed streams without head-of-line blocking, and resilience against client network/IP migration, cutting request latency by up to 40% across lossy and high-latency edge networks.
- **Business Value**: Minimizes mobile-to-relay round-trip latency and eliminates connection drops for globally distributed remote developers and edge agents.
- **Effort Estimate**: M

---

## IDEA-647: Multi-Party Quorum & Dual-Control Approval Policies (`hitl-cli request --quorum N/M`)
- **Category**: Feature
- **Problem**: For sensitive operations such as production database migrations, main branch force-pushes, or cloud IAM policy alterations, relying on a single human approver violates corporate separation-of-duties and dual-control regulatory compliance requirements.
- **Proposed Solution**: Add multi-party approval orchestration in `hitl-cli request --quorum 2/3 --approver-group secops`. The CLI registers a quorum challenge with the relay, dispatches concurrent mobile notifications to all eligible approvers in the group, and blocks the agent until the required threshold ($N$ of $M$) of cryptographically verified unique approvals have been collected.
- **Business Value**: Unlocks enterprise sales in regulated industries by satisfying mandatory SOX, SOC2, and ISO 27001 four-eyes approval controls for autonomous operations.
- **Effort Estimate**: M

---

## IDEA-648: Protocol Buffers Schema Generation & Contract Testing for Relay Transports
- **Category**: Tech Debt
- **Problem**: Communication schemas between `hitl-cli`, the mobile application, and `hitl-shin-relay` are currently maintained as loosely typed Python dictionaries and JSON strings, leading to subtle cross-repo contract drift and runtime errors when schema fields change.
- **Proposed Solution**: Establish a canonical Protocol Buffers (Protobuf) schema repository with automated code generation for Pydantic v2 data models used across `api_client.py` and `mcp_client.py`. Integrate automated schema contract validation tests into CI that assert exact backward compatibility for all serialized JSON and SSE wire formats against historical release schemas.
- **Business Value**: Eliminates breaking changes and silent payload corruption between CLI releases and backend services, reducing cross-repository debugging overhead.
- **Effort Estimate**: S

---

## IDEA-649: Kubernetes Validating Admission Controller & Helm Deployment Safety Gate (`hitl-k8s-gate`)
- **Category**: Integration
- **Problem**: Autonomous platform agents managing Kubernetes clusters via Helm or `kubectl` can accidentally apply manifests with invalid container images, dangerous privilege escalations, or misconfigured resource quotas directly into production namespaces.
- **Proposed Solution**: Build a lightweight Kubernetes Validating Admission Webhook (`hitl-k8s-gate`). When an agent or automated pipeline applies manifests in protected namespaces, the webhook intercepts the API request, extracts the declarative diff, dispatches a mobile HITL approval prompt with structured container and RBAC details, and admits or rejects the Kubernetes resource based on the human's response.
- **Business Value**: Provides an unbypassable, cluster-enforced safety barrier protecting enterprise Kubernetes infrastructure against runaway or rogue AI agent deployments.
- **Effort Estimate**: L

---

## IDEA-650: Local Terminal Voice Synthesis & Whisper Speech-to-Text Response Capture (`hitl-cli request --speak`)
- **Category**: UX
- **Problem**: Software engineers on call, working while commuting, or wearing audio headsets cannot stop to read long textual diffs on terminal screens or type detailed terminal feedback, leading to prolonged response delays during incidents.
- **Proposed Solution**: Integrate local text-to-speech (TTS) synthesis and speech-to-text (STT) input into `hitl-cli request --speak`. The CLI speaks a concise auditory summary of the prompt using OS speech engines (macOS `say`, Linux `speech-dispatcher`, or Piper) and records the reviewer's vocal response via a local Whisper.cpp or system microphone model, translating spoken instructions directly into choice selections or clarifying text.
- **Business Value**: Dramatically accelerates on-call engineer reaction speed during critical outages and provides an accessible, eyes-free interaction option for multitasking developers.
- **Effort Estimate**: M

---

## IDEA-651: Adaptive RFC 3229 Delta Compression for Multi-Step Agent Sessions (`--delta-compression`)
- **Category**: Performance
- **Problem**: Multi-turn agent tasks that issue sequential prompts every few minutes frequently re-transmit full code files, logs, or workspace context, consuming excessive network bandwidth and exhausting mobile data caps on repetitive identical content.
- **Proposed Solution**: Implement RFC 3229 HTTP delta compression in `ApiClient` using efficient VCDIFF/Xdelta algorithms. When an agent prompts multiple times within a persistent session, the CLI computes differences relative to previous prompt payloads and transmits only the byte delta, allowing the relay and mobile app to reconstruct the full context while slashing wire transfer volume by over 80%.
- **Business Value**: Reduces relay infrastructure egress costs and significantly speeds up mobile push delivery on cellular connections during intensive multi-prompt coding sessions.
- **Effort Estimate**: S

---

## IDEA-652: Post-Quantum Hybrid Key Exchange (ML-KEM-768 / Kyber + X25519) for E2EE (`--pqc-hybrid`)
- **Category**: Security
- **Problem**: Existing PyNaCl Box (X25519) encryption is vulnerable to future "harvest now, decrypt later" adversary attacks where captured encrypted network traffic is retained until cryptographically relevant quantum computers can break elliptic-curve cryptography.
- **Proposed Solution**: Introduce a post-quantum hybrid key encapsulation mechanism in `hitl_cli/crypto.py` that pairs classical X25519 with NIST-standardized ML-KEM-768 (formerly CRYSTALS-Kyber) via `liboqs-python` or pure-Python ML-KEM. The shared secrets are combined via HKDF-SHA256 to derive the session encryption key, ensuring forward secrecy against both classical and quantum adversaries.
- **Business Value**: Future-proofs confidential AI agent interactions and protects proprietary code against quantum decryption, ensuring compliance with NSA Commercial National Security Algorithm (CNSA 2.0) guidelines.
- **Effort Estimate**: M

---

## IDEA-653: Multi-Channel Fallback Cascade with Automated Voice Call & SMS Escalation (`--escalate-call`)
- **Category**: Feature
- **Problem**: When an urgent agent prompt arrives while an engineer is away from their desk, asleep, or in an area with silenced push notifications, the agent blocks indefinitely, causing severe operational delays and missed SLAs.
- **Proposed Solution**: Add an automated escalation cascade policy in `hitl-cli request --escalate-call 10m --escalate-sms 5m`. If a high-priority prompt remains unacknowledged after the specified duration, the relay triggers an automated SMS and interactive Twilio voice phone call, reading the alert via text-to-speech and allowing the responder to approve or reject directly via phone keypad DTMF tones.
- **Business Value**: Guarantees rapid human intervention for critical production blockers, reducing mean time to acknowledge (MTTA) from hours to minutes during after-hours outages.
- **Effort Estimate**: M

---

## IDEA-654: Modular Hook Middleware Pipeline & Decorator Architecture for CLI Extensibility
- **Category**: Tech Debt
- **Problem**: Current hook implementations (`review_and_continue.py`, `codex_notify.py`) suffer from duplicated argument parsing, error logging, and subprocess handling logic that makes writing new agent integrations brittle and redundant.
- **Proposed Solution**: Refactor `hitl_cli.hooks` into a unified composable middleware architecture with a `@hook_stage` decorator. Shared behaviors such as telemetry recording, payload sanitization, notification dispatch, and signal trapping are decoupled into standalone reusable pipeline stages, enabling new AI agent hooks (e.g., Goose, Devin, Antigravity) to be implemented in under 50 lines of clean, testable code.
- **Business Value**: Eliminates code duplication and lowers maintenance friction, enabling the engineering team to ship new AI agent integration hooks rapidly as new agent platforms emerge.
- **Effort Estimate**: S

---

## IDEA-655: Official GitHub Actions & GitLab CI Native Step Approval Actions (`hitl-action`)
- **Category**: Integration
- **Problem**: DevOps teams integrating HITL approvals into automated CI/CD pipelines currently have to write boilerplate shell scripts with raw curl loops, error handling, and manual exit status checking.
- **Proposed Solution**: Publish an official pre-packaged GitHub Action (`slaser79/hitl-action@v1`) and GitLab CI Component. The action encapsulates `hitl-cli`, automatically injects git commit details, PR URLs, and workflow run metadata into the prompt, formats markdown diff summaries in GitHub Job Summaries, and pauses the CI pipeline until the human approves or rejects from their mobile device.
- **Business Value**: Dramatically lowers adoption barriers for enterprise DevOps teams, turning `hitl-cli` into the standard human-gate solution for thousands of GitHub Actions and GitLab CI deployments.
- **Effort Estimate**: S

---

## IDEA-656: Local Real-Time Web Dashboard for Headless & Remote Dev Environments (`hitl-cli serve-web`)
- **Category**: UX
- **Problem**: Developers running agents on headless remote hosts (e.g. remote SSH servers, GitHub Codespaces, AWS EC2 devboxes, Docker containers) cannot view native desktop notifications or terminal window title updates when a prompt is pending.
- **Proposed Solution**: Add an embedded lightweight local web server in `hitl-cli serve-web --port 8080`. It serves a responsive real-time single-page dashboard over WebSockets that displays pending prompts, rich git diff previews, and active session history, allowing developers to review and approve agent requests through forwarded browser ports without needing a mobile device.
- **Business Value**: Broadens `hitl-cli` usability across cloud-based remote development environments and web-first development teams, removing mobile phone dependency during intense coding sessions.
- **Effort Estimate**: M

---

## IDEA-657: Conditional Auto-Approval Rules Engine with Local Policy Evaluation (`hitl-cli policy evaluate`)
- **Category**: Feature
- **Problem**: Autonomous agents frequently pause for human approval on trivial, repetitive, or low-risk tasks (e.g. formatting markdown docs, updating patch-level test dependencies, generating mock test data), creating alert fatigue that causes reviewers to rubber-stamp dangerous requests.
- **Proposed Solution**: Implement a declarative local policy engine in `hitl-cli policy evaluate` configured via `~/.config/hitl-cli/policy.yaml`. Prompts matching user-defined rule criteria (e.g., diff only modifies `*.md` files, changes pass pre-commit linters, risk score is low) are automatically approved and cryptographically logged with an audit receipt, reserving human intervention exclusively for meaningful or high-risk decisions.
- **Business Value**: Eliminates reviewer cognitive fatigue and accelerates agent productivity on benign tasks while strictly guaranteeing that risky actions are never bypassed.
- **Effort Estimate**: M
