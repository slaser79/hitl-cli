# Ideas Batch — hitl-cli (Batch 32)

## IDEA-463: Interactive Multi-Turn Dialog Threading in CLI & SDK (`--thread-id`)
- **Category**: Feature
- **Problem**: When an autonomous agent requires iterative clarifications or follow-up feedback from the human user, separate requests generate disconnected prompt cards in the mobile app without shared context.
- **Proposed Solution**: Introduce first-class `thread_id` and `parent_request_id` parameters in `hitl-cli request` and the SDK's `request_input()`, enabling the relay and mobile UI to group chained prompts into a unified conversational thread.
- **Business Value**: Drastically improves user review speed and resolution accuracy for complex multi-step agent negotiations, reducing agent abandonment.
- **Effort Estimate**: M

---

## IDEA-464: Automated Keyring & 1Password/Bitwarden Secret Provider Integration for Headless CI
- **Category**: Security
- **Problem**: Developers running agentic CI/CD pipelines and headless worker environments frequently risk committing or leaking raw `HITL_API_KEY` tokens in plain-text environment files.
- **Proposed Solution**: Add native credential provider integration (`hitl-cli config credential-helper`) supporting 1Password CLI (`op`), Bitwarden CLI (`bw`), and OS secret keyrings to fetch API keys dynamically at runtime without disk persistence.
- **Business Value**: Eliminates plaintext credential storage in repositories and automated pipelines, ensuring compliance with strict enterprise security mandates.
- **Effort Estimate**: S

---

## IDEA-465: Intelligent Rich Terminal Progress Bar and Human-Waiting Activity Indicator
- **Category**: UX
- **Problem**: When an agent or script blocks waiting for human approval over several minutes, the terminal output appears completely frozen, leading developers to assume the process hung and press Ctrl+C prematurely.
- **Proposed Solution**: Implement an interactive Rich terminal display showing an animated spinner, live elapsed timer, countdown until timeout, and real-time status transitions (e.g., "Notification dispatched", "Human viewing request").
- **Business Value**: Prevents accidental workflow aborts during human review delays, improving developer confidence and reducing redundant restart attempts.
- **Effort Estimate**: S

---

## IDEA-466: Configurable Default Fallback Action on Timeout (`--on-timeout approve|reject|default`)
- **Category**: Feature
- **Problem**: Unattended automated pipelines fail abruptly with unhandled exceptions when a human reviewer is away and does not respond within the timeout window.
- **Proposed Solution**: Add an `--on-timeout` parameter (`approve`, `reject`, `choice:<val>`, or `abort`) to CLI commands and the SDK `HITL` class, allowing scripts to execute deterministic fallback policies while marking the decision source in audit logs.
- **Business Value**: Enables resilient, continuous overnight CI/CD pipelines while preserving verifiable auditability between human-approved and timeout-defaulted actions.
- **Effort Estimate**: S

---

## IDEA-467: Local Response Polling Interval Exponential Decay & Push Wakeup Optimization
- **Category**: Performance
- **Problem**: Polling the relay at fixed high frequencies during long human review intervals wastes network bandwidth, increases mobile battery consumption, and exhausts API rate limits.
- **Proposed Solution**: Implement adaptive polling backoff with random jitter in `mcp_client.py` and `api_client.py`, starting with rapid 1-second intervals for immediate responses and decaying to 10-second intervals with instant wakeup on long-poll or push triggers.
- **Business Value**: Reduces client and relay network traffic by up to 60% during extended human pauses while preserving sub-second response times for fast mobile approvals.
- **Effort Estimate**: S

---

## IDEA-468: Native OpenHands, CrewAI, and LangChain Agent Framework Adapter Middleware
- **Category**: Integration
- **Problem**: Integrating `hitl-cli` into prevailing multi-agent frameworks (LangChain, CrewAI, AutoGen, OpenHands) currently requires writing bespoke wrapper classes and tool signatures from scratch.
- **Proposed Solution**: Provide standardized adapter modules (`hitl_cli.adapters.langchain`, `hitl_cli.adapters.crewai`) exposing ready-to-use tool abstractions and callback handlers for seamless human review injection.
- **Business Value**: Lowers developer onboarding friction and establishes `hitl-cli` as the default drop-in human-in-the-loop toolchain across major Python agent ecosystems.
- **Effort Estimate**: M

---

## IDEA-469: Unified Async HTTP Client Session Lifecycle Management across SDK & CLI
- **Category**: Tech Debt
- **Problem**: Disjointed instances of `httpx.AsyncClient` are spawned per request across various CLI subcommands and SDK entry points, causing connection churn and unclosed socket warnings.
- **Proposed Solution**: Implement a centralized, thread-safe async HTTP client session manager with connection pooling, keep-alive reuse, and graceful async cleanup handlers across all SDK calls and CLI commands.
- **Business Value**: Reduces request latency overhead by 30-50ms per call and eliminates intermittent socket leak warnings during high-throughput agent runs.
- **Effort Estimate**: M

---

## IDEA-470: Granular Request Authorization Scopes & Action Budget Guardrails
- **Category**: Security
- **Problem**: Autonomous agents running with a valid API key can dispatch unlimited high-cost, disruptive, or malicious approval requests without local policy boundaries.
- **Proposed Solution**: Add local policy configuration (`hitl-policy.yaml`) enabling developers to define rate limits, allowed prompt templates, maximum daily requests per agent, and mandatory choice restrictions.
- **Business Value**: Prevents rogue or malfunctioning autonomous agents from spamming stakeholders or initiating unauthorized destructive operations.
- **Effort Estimate**: M

---

## IDEA-471: Automated QR Code Pairing Terminal Display for Instant Mobile App Login
- **Category**: UX
- **Problem**: Authenticating `hitl-cli` on headless remote servers or cloud dev containers requires copying complex OAuth URLs back and forth between terminal and desktop browsers.
- **Proposed Solution**: Render an interactive ASCII/Unicode QR code directly inside the terminal during `hitl-cli login --qr`, allowing developers to instantly pair their mobile HITL app with a single camera scan.
- **Business Value**: Eliminates authentication friction in cloud developer environments, accelerating developer activation and onboarding velocity.
- **Effort Estimate**: S

---

## IDEA-472: Local Webhook Ingestion Server for Instant Low-Latency Human Response Dispatch
- **Category**: Feature
- **Problem**: Polling-based response retrieval introduces artificial latency and continuous relay load when agents run on server environments capable of receiving incoming HTTP webhooks.
- **Proposed Solution**: Introduce `hitl-cli listen --port <port>` which runs an embedded lightweight ASGI webhook server to receive push notifications and encrypted human responses directly from the relay.
- **Business Value**: Delivers instantaneous sub-100ms response delivery to waiting agents, maximizing throughput in latency-sensitive automation pipelines.
- **Effort Estimate**: M

---

## IDEA-473: E2EE Key Generation Benchmarking and Pre-Computed Ephemeral Key Pool
- **Category**: Performance
- **Problem**: Generating PyNaCl Curve25519 keypairs synchronously during cold CLI invocation introduces measurable latency to short-lived shell commands.
- **Proposed Solution**: Implement a secure background pre-generation worker and local keypool cache in `crypto.py` that pre-computes ephemeral keypairs during idle time for immediate zero-latency dispatch.
- **Business Value**: Cuts 40-70ms off CLI invocation startup time, making `hitl-cli` feel instantaneous in shell scripts and automated agent hooks.
- **Effort Estimate**: S

---

## IDEA-474: Interactive Schema Builder & Dry-Run Prompt Tester (`hitl-cli prompt test`)
- **Category**: UX
- **Problem**: Engineers designing multi-choice prompts, custom timeouts, and attachment payloads cannot verify how their prompt will render visually on mobile without dispatching live push notifications.
- **Proposed Solution**: Add `hitl-cli prompt test` with an interactive terminal preview and a local browser mockup server that accurately renders the prompt layout, Markdown formatting, and interactive choice buttons.
- **Business Value**: Speeds up prompt engineering turnaround and eliminates embarrassing or unreadable prompt bugs in production workflows.
- **Effort Estimate**: S

---

## IDEA-475: Full Pydantic v2 Settings and Payload Validation Engine Integration
- **Category**: Tech Debt
- **Problem**: Configuration loading, token storage, and API payload definitions rely on untyped Python dictionaries and ad-hoc validation functions scattered across `auth.py`, `config.py`, and `api_client.py`.
- **Proposed Solution**: Migrate all configuration, token storage schemas, and API request/response structures to Pydantic v2 `BaseModel` and `BaseSettings` classes with strict validation and automated serialization.
- **Business Value**: Improves code maintainability, eliminates subtle type coercion bugs, and provides instant runtime validation for user configurations.
- **Effort Estimate**: M

---

## IDEA-476: GitHub Actions and GitLab CI Human Gate Step Action (`hitl-cli/action`)
- **Category**: Integration
- **Problem**: DevOps teams integrating human approval gates into CI/CD deployment pipelines must write and maintain brittle bash wrapper scripts around CLI commands.
- **Proposed Solution**: Release an official, packaged GitHub Action (`slaser79/hitl-action`) and GitLab CI component wrapping `hitl-cli` with native step outputs, PR summaries, and automated pipeline pausing.
- **Business Value**: Unlocks thousands of enterprise DevOps and CI/CD pipelines by making human-in-the-loop deployment gating a one-line YAML configuration.
- **Effort Estimate**: S

---

## IDEA-477: Client-Side Ephemeral Session Encryption with Auto-Expiring One-Time Keys
- **Category**: Security
- **Problem**: Persistent storage of device private keys on shared machines risks exposing historical audit logs if an attacker ever accesses the local file system.
- **Proposed Solution**: Support ephemeral, per-request one-time encryption keypairs (ECDH ephemeral-static / forward secrecy) where session decryption keys are cryptographically shredded immediately upon response processing.
- **Business Value**: Delivers forward secrecy for sensitive organizational data, satisfying stringent compliance and security requirements in regulated sectors.
- **Effort Estimate**: M
