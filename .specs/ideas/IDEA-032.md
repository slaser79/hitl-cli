# Ideas Batch — hitl-cli (Batch 38)

## IDEA-553: Structured Multi-Choice Response Matrix with Weighted Scoring (`hitl-cli request --matrix`)
- **Category**: Feature
- **Problem**: Autonomous evaluation agents (such as model benchmarkers, code auditors, or safety alignment evaluators) frequently require humans to grade candidate outputs across multiple criteria simultaneously rather than providing a single text or binary response.
- **Proposed Solution**: Add `--matrix <schema.json>` or `--criteria "correctness:1-5,safety:1-5,style:1-5"` to `hitl-cli request` and the SDK's `request_input()`. The CLI packages the multi-criteria rubric into the request envelope, and the mobile client renders interactive sliders or rating pills for each criterion, returning a structured score dictionary directly to the waiting agent.
- **Business Value**: Unlocks complex RLHF and human-in-the-loop evaluation workflows for AI research teams, driving enterprise adoption of the HITL platform for model benchmarking and alignment.
- **Effort Estimate**: M

---

## IDEA-554: Ephemeral Air-Drop / Local P2P Wi-Fi Pairing for Terminal-to-Mobile Relay Bypass (`hitl-cli pair --local`)
- **Category**: Integration
- **Problem**: In high-security offline enclaves, air-gapped data centers, or locations with degraded satellite connections, agents cannot route prompts through the public cloud relay (`https://hitlrelay.app`).
- **Proposed Solution**: Introduce `hitl-cli pair --local` utilizing mDNS/DNS-SD local network discovery and direct TLS WebSocket connections to the HITL mobile app on the same local subnet or personal hotspot. Prompts and responses travel peer-to-peer with zero WAN transit while maintaining authenticated session encryption established via terminal QR code pairing.
- **Business Value**: Unlocks defense, financial, and air-gapped enterprise contracts where strict data sovereignty regulations forbid routing prompt payloads through public cloud infrastructure.
- **Effort Estimate**: L

---

## IDEA-555: Interactive Shell Piping and Stream Redirection (`cat file.diff | hitl-cli request --stdin`)
- **Category**: UX
- **Problem**: Shell script developers and CI workflows currently have to pass large prompt strings or diffs via command-line arguments or temporary disk files, risking argument length limits (`ARG_MAX`) and shell quoting corruption.
- **Proposed Solution**: Add `--stdin` support (and automatic pipe detection when `sys.stdin` is not a TTY) to `hitl-cli request` and `hitl-cli notify`. Piped content streams directly into the prompt payload with automated buffer size enforcement and syntax detection (e.g. recognizing unified diffs, structured JSON, or Markdown).
- **Business Value**: Drastically improves Unix ergonomics and developer workflow velocity, making HITL integration effortless within git hooks, build scripts, and CLI toolchains.
- **Effort Estimate**: S

---

## IDEA-556: Hardware Token (YubiKey / FIDO2) Backed E2EE Private Key Storage (`hitl-cli key init --fido2`)
- **Category**: Security
- **Problem**: Storing E2EE private keys as plaintext files in `~/.config/hitl-cli/` leaves cryptographic credentials vulnerable if an attacker gains filesystem access or developer laptops are compromised.
- **Proposed Solution**: Support FIDO2 / WebAuthn and PKCS#11 hardware security keys (e.g. YubiKey, Nitrokey) for E2EE decryption and signing via `hitl-cli key init --fido2`. Cryptographic key material remains inside the tamper-resistant hardware element, requiring physical user presence (capacitive touch) to authorize local response decryption.
- **Business Value**: Satisfies strict corporate hardware security module (HSM) compliance standards, enabling zero-trust adoption across banking and defense sectors.
- **Effort Estimate**: M

---

## IDEA-557: Async Polling Worker Pool for Multi-Prompt Concurrency (`hitl-cli request-all`)
- **Category**: Performance
- **Problem**: Multi-agent swarms or parallel CI jobs dispatching dozens of simultaneous human review requests must run separate CLI processes, exhausting OS process limits and triggering relay rate limits.
- **Proposed Solution**: Implement `hitl-cli request-all --input requests.jsonl --concurrency 10` backed by an `asyncio.Queue` worker pool in the Python SDK. The worker pool multiplexes HTTP/2 connections, batches status polling calls to the relay, and yields resolved JSON response records as human reviewers complete each item.
- **Business Value**: Slashes system CPU and file-descriptor overhead while cutting polling latency by over 70% for high-throughput multi-agent fleets.
- **Effort Estimate**: M

---

## IDEA-558: Typed Pydantic Config Models & Strict TOML Validation (`hitl-cli config validate`)
- **Category**: Tech Debt
- **Problem**: Configuration handling is fragmented across hardcoded path constants in `config.py`, ad-hoc dictionary lookups, and unvalidated environment variable parsing, causing silent failures when settings drift.
- **Proposed Solution**: Refactor CLI and SDK configuration around a centralized Pydantic v2 `HitlSettings` model with structured schema validation and hierarchical precedence (CLI flags > environment variables > `.hitl.toml` in project root > `~/.config/hitl-cli/config.toml`). Introduce `hitl-cli config validate` to inspect active configurations, highlight deprecated keys, and pinpoint formatting errors.
- **Business Value**: Eliminates hard-to-debug misconfiguration failures, shortens developer onboarding time, and establishes a maintainable architecture for future feature expansion.
- **Effort Estimate**: S

---

## IDEA-559: Smart Auto-Response Rules Engine for Routine Agent Permissions (`hitl-cli rules add`)
- **Category**: Feature
- **Problem**: Developers managing autonomous agents are inundated with repetitive low-risk approval prompts (e.g. "Run `pytest tests/`?", "Install dev dependency?"), inducing decision fatigue and increasing the risk of careless approvals on dangerous actions.
- **Proposed Solution**: Implement a client-side rule evaluation engine (`hitl-cli rules add --pattern "Run pytest.*" --action approve --max-per-hour 20`). Before dispatching a request to the relay, the CLI matches incoming prompts against user-defined regex patterns and velocity limits; matching low-risk operations are auto-approved locally and logged to an audit ledger without pinging the reviewer's phone.
- **Business Value**: Combats notification fatigue and boosts developer productivity by automating repetitive low-risk approvals while preserving strict human oversight on sensitive commands.
- **Effort Estimate**: M

---

## IDEA-560: Interactive Terminal TUI Dashboard for Active & Pending Prompts (`hitl-cli dashboard`)
- **Category**: UX
- **Problem**: When running multiple autonomous agent tasks in headless terminal multiplexers (tmux/screen), developers lack a centralized terminal view to track pending prompts, countdown expirations, and active reviews.
- **Proposed Solution**: Build a lightweight Textual-based terminal UI (`hitl-cli dashboard`) featuring a real-time split-pane interface: pending prompts with countdown timers on the left, and rich syntax-highlighted diffs/payload details with keyboard shortcuts (`a` to approve, `r` to reject, `c` to comment) on the right.
- **Business Value**: Delivers power-user developers and DevOps engineers an interactive command center for monitoring and clearing agent review bottlenecks without leaving their terminal environment.
- **Effort Estimate**: M

---

## IDEA-561: Fast Client-Side E2EE Secret Caching with Memory-Safe Ring Buffers
- **Category**: Performance
- **Problem**: Repeatedly re-deriving shared secrets via X25519 Diffie-Hellman and reading private keys from disk for every single prompt and notification generates unnecessary disk I/O and cryptographic CPU overhead.
- **Proposed Solution**: Introduce a thread-safe, memory-bounded ephemeral session cache in `crypto.py` that stores pre-computed shared symmetric keys with a 15-minute TTL. The cache uses a fixed-size ring buffer with automatic memory zeroing on expiration or process eviction, eliminating disk reads for active agent sessions.
- **Business Value**: Reduces per-request cryptographic latency by 60%, delivering snappier response times for rapid-fire agent tool calls.
- **Effort Estimate**: S

---

## IDEA-562: Secure Multi-Factor Step-Up Authentication for High-Risk Actions (`hitl-cli request --mfa-required`)
- **Category**: Security
- **Problem**: If an unlocked mobile device is accessed by an unauthorized person, sensitive production deployment approvals or database drop confirmations could be granted without verification.
- **Proposed Solution**: Add `--mfa-required` and `--risk-level critical` flags to `hitl-cli request` and the SDK. When flagged, the mobile application enforces biometric verification (FaceID, TouchID, or device passkey) before unlocking the approval button and transmitting the signed decryption payload.
- **Business Value**: Fulfills zero-trust compliance standards and satisfies SOC2 Type II requirements for privileged production infrastructure controls.
- **Effort Estimate**: S

---

## IDEA-563: Native GitHub Actions Step Summary & Annotation Exporter (`hitl-cli request --github-actions`)
- **Category**: Integration
- **Problem**: When `hitl-cli` is executed inside GitHub Actions workflows for deployment gates, human approvals and timeout events are buried in dense console logs without native UI representation.
- **Proposed Solution**: Add `--github-actions` flag (auto-detected via `$GITHUB_ACTIONS=true`) that automatically writes formatted Markdown status cards to `$GITHUB_STEP_SUMMARY` and emits GitHub workflow commands (`::notice::` and `::error::`). The step summary renders the prompt question, reviewer avatar, timestamp, and decision badge directly in the GitHub PR or Actions run overview.
- **Business Value**: Seamlessly integrates HITL into GitHub CI/CD workflows, providing clear visual audit trails for DevOps teams without needing to inspect raw log streams.
- **Effort Estimate**: S

---

## IDEA-564: Graceful Subprocess Timeout & Stale Task Cancellation Propagation (`hitl-cli request --cancel-on-timeout`)
- **Category**: Tech Debt
- **Problem**: When a prompt times out in `hitl-cli request`, the client exits with an error code, but the pending prompt remains open on the mobile app, causing confusion and wasted human review effort.
- **Proposed Solution**: Update `ApiClient` and `mcp_client.py` to automatically dispatch a `DELETE /requests/{id}` or `POST /requests/{id}/cancel` notification to the relay upon local timeout expiration or `SIGINT` signal trapping. The mobile app immediately marks the notification as expired/cancelled and clears the lockscreen banner.
- **Business Value**: Prevents stale notification clutter and eliminates wasted human effort on tasks that have already timed out or been abandoned.
- **Effort Estimate**: S

---

## IDEA-565: Automated Network Proxy & SOCKS5 Tunnel Auto-Configuration (`hitl-cli request --proxy`)
- **Category**: Integration
- **Problem**: Developers and agents operating behind corporate firewalls, egress proxies, or Zscaler enterprise gateways encounter connection drops and SSL handshake failures when communicating with the HITL relay.
- **Proposed Solution**: Add comprehensive HTTP, HTTPS, and SOCKS5 proxy support to `ApiClient` and SDK using `httpx[socks]` and standard environment variables (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`). Provide `--proxy` CLI overrides and custom CA bundle specification (`--cacert <path>`) for corporate SSL inspection certificates.
- **Business Value**: Removes enterprise network adoption roadblocks, allowing seamless deployment within Fortune 500 corporate developer networks.
- **Effort Estimate**: S

---

## IDEA-566: Agent Action Budget Guardrails with Velocity Throttling (`hitl-cli request --max-prompts-per-minute`)
- **Category**: Feature
- **Problem**: Runaway or looping AI agents can spam dozens of HITL prompts or notifications in seconds, flooding human phones and overwhelming reviewers.
- **Proposed Solution**: Introduce a local client-side rate limiter and velocity guardrail (`--max-prompts-per-minute <n>` or `--daily-limit <n>`). If an agent exceeds the threshold, `hitl-cli` pauses execution with exponential backoff or fails fast with a `RateLimitExceededError`, alerting the human with a single aggregated throttle warning.
- **Business Value**: Protects human users from notification spam storms and prevents runaway agent execution loops from burning operational resources.
- **Effort Estimate**: S

---

## IDEA-567: Automated Hook Self-Repair & Diagnostic Sync Command (`hitl-cli hook sync`)
- **Category**: UX
- **Problem**: Updates to Claude Code or Google Antigravity often overwrite or alter local configuration files (`~/.claude/settings.json`, Antigravity channel hooks), silently breaking the `review_and_continue` and notification hooks.
- **Proposed Solution**: Implement `hitl-cli hook sync` to inspect installed agent settings, verify hook command paths, validate Python virtual environment availability (`uvx` vs `python`), and re-inject any missing or corrupted hook definitions. Provide a `--check` dry-run mode for CI smoke testing.
- **Business Value**: Dramatically reduces user frustration and support tickets caused by third-party AI tool updates breaking HITL hook integration.
- **Effort Estimate**: S
