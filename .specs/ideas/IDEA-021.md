# Ideas Batch — hitl-cli (Batch 27)

## IDEA-388: Structured CLI Output Options for Scripting Automation (JSON, YAML, CSV)
- **Category**: UX
- **Problem**: When developers wrap `hitl-cli` inside shell scripts, parsing the human-readable output (like tables or formatted lines) using `grep` or `awk` is brittle and error-prone.
- **Proposed Solution**: Introduce a global flag `--format` (`json`, `yaml`, `text`) to all CLI query and status commands. For instance, `hitl-cli status --format json` or `hitl-cli agents list --format yaml` would return structured payloads easily parseable by tools like `jq` or `yq`.
- **Business Value**: Promotes seamless automation and scriptability, accelerating developer adoption in custom CI/CD pipelines.
- **Effort Estimate**: S

---

## IDEA-389: Encrypted Local Config Verification and Lockfile
- **Category**: Security
- **Problem**: Storing local OAuth tokens and dynamic client registrations in plaintext JSON files (`~/.hitl/*.json`) on developer machines leaves them vulnerable to local privilege escalation or malicious software.
- **Proposed Solution**: Encrypt sensitive files in `~/.hitl/` (like `oauth_token.json` and `oauth_client.json`) using a local machine-derived key (e.g. using a secure salt combined with user-specific keys from the OS keyring/passphrase) or validate their cryptographic integrity using a SHA-256 lockfile.
- **Business Value**: Mitigates risk of local token theft and credential harvesting on compromised developer machines.
- **Effort Estimate**: M

---

## IDEA-390: Multi-Device OAuth Session Syncing
- **Category**: Feature
- **Problem**: Developers working across multiple machines (e.g. desktop and laptop, or cloud containers) must re-authenticate and perform dynamic client registration on each machine separately, creating cluttered agent lists on the relay.
- **Proposed Solution**: Support a mechanism to export a secure, encrypted setup profile from one authenticated CLI instance to another via a short-lived, single-use authentication PIN or QR code displayed on the console and verified on the mobile app.
- **Business Value**: Enhances cross-device developer experience (DX) and reduces duplicate agent/client records.
- **Effort Estimate**: M

---

## IDEA-391: Automatic Latency Optimization with Nearest Edge Endpoint Selection
- **Category**: Performance
- **Problem**: When a developer is traveling or working globally, sending all requests to a static `HITL_SERVER_URL` in a fixed region causes unnecessary HTTP roundtrip latency.
- **Proposed Solution**: Implement an endpoint resolution step in the `ApiClient` that checks a set of available regional server nodes, benchmarks response latencies using short ping probes, and automatically routes subsequent requests to the lowest latency node.
- **Business Value**: Minimizes latency of developer interactive loops globally, accelerating task completions.
- **Effort Estimate**: M

---

## IDEA-392: Unified CLI Context Attachment for Requests
- **Category**: UX
- **Problem**: When requesting human input using `hitl-cli request`, attaching context files (such as local screenshots, log files, or terminal dumps) is cumbersome and requires manual file ingestion.
- **Proposed Solution**: Introduce a `--file` (`-f`) flag to the `request` command, allowing developers to attach one or more files directly. The CLI automatically reads, validates, hashes, and optionally encrypts these files before sending them to the relay as structured attachment payloads.
- **Business Value**: Streamlines the process of sending rich debugging context to the human.
- **Effort Estimate**: S

---

## IDEA-393: SDK Local-First Fallback Mode with Timeout Guardrails
- **Category**: Feature
- **Problem**: If the SDK is configured to block on human response (`await hitl.request_input(...)`) and the network connection drops or the human is completely unresponsive, the client application hangs indefinitely.
- **Proposed Solution**: Add support for a `fallback_fn` parameter and absolute timeout thresholds in the SDK request methods. If the timeout expires or the network is unreachable, the SDK executes the fallback callback (e.g., executing a default rule or local mock input) to prevent application lockup.
- **Business Value**: Restores autonomy to automated agents when humans are absent, preventing business process stalling.
- **Effort Estimate**: M

---

## IDEA-394: E2EE Payload Compression for Large Payloads
- **Category**: Performance
- **Problem**: Encrypting large payloads (e.g., massive log dumps or database diffs) with PyNaCl and encoding them to base64 increases the data size significantly, consuming unnecessary network bandwidth and memory.
- **Proposed Solution**: Integrate transparent, lightweight compression (like `zlib` or `lz4`) prior to encrypting payload messages in `crypto.py`. The receiver client (mobile app or MCP client) detects compression flags in the header and decompresses the payload upon decryption.
- **Business Value**: Reduces network overhead, reduces costs for mobile data plans, and speeds up E2EE operations.
- **Effort Estimate**: S

---

## IDEA-395: Typer Command Registry Refactoring to Support CLI Plugins
- **Category**: Tech Debt
- **Problem**: All CLI subcommands are directly imported and registered in `main.py`, making it difficult to write custom extensions or plugins without modifying the core CLI package.
- **Proposed Solution**: Refactor the CLI loading mechanism to use dynamic entry point discovery (via Python's `importlib.metadata`). This allows third-party packages to register subcommands under the `hitl-cli` namespace automatically.
- **Business Value**: Enables modular development and allows teams to build custom internal tooling on top of `hitl-cli` without fork maintenance.
- **Effort Estimate**: M

---

## IDEA-396: Zero-Dependency Verification Script for CI Pipelines
- **Category**: Tech Debt
- **Problem**: Verifying `hitl-cli`'s installation and configuration on remote build servers currently requires importing all heavy packages (like PyNaCl, Typer, httpx), which is slow and heavy for simple health checks.
- **Proposed Solution**: Provide a lightweight, zero-dependency bash/python utility script (`hitl-cli-check`) in the distribution that performs basic sanity tests (e.g., verifying environmental variables, testing TCP connectivity to the relay, checking python version) without loading any optional packages.
- **Business Value**: Streamlines integration checks in CI pipelines and simplifies environment debugging.
- **Effort Estimate**: S

---

## IDEA-397: OAuth Client Credentials Grant Flow for Daemon Integration
- **Category**: Integration
- **Problem**: The current authentication flows (OAuth 2.1 PKCE or Firebase/JWT) require interactive user login, which makes it difficult to run `hitl-cli` as a background system daemon or non-interactive cron job.
- **Proposed Solution**: Support the OAuth 2.1 Client Credentials Grant flow. A machine/daemon can configure a pre-registered `client_id` and `client_secret` via environment variables to retrieve access tokens without browser interaction.
- **Business Value**: Simplifies deployment of autonomous server agents and background workflows in production environments.
- **Effort Estimate**: M

---

## IDEA-398: Real-time CLI Status Bar for Interactive Approvals
- **Category**: UX
- **Problem**: When running interactive commands that block (like `hitl-cli request`), the console simply displays a static "Waiting for response..." message, giving no indication of whether the server is still polling or active.
- **Proposed Solution**: Add an animated terminal progress indicator or status bar (using `rich` or standard ANSI escape codes). It displays a live counter of elapsed time, dynamic heartbeat dots, and the status of the connection to the relay.
- **Business Value**: Improves CLI user experience and assures developers that the command is actively running and waiting, rather than hung.
- **Effort Estimate**: S

---

## IDEA-399: Client-Side Rate Limiter and Traffic Shaping
- **Category**: Performance
- **Problem**: High-velocity agent loops can easily flood the HITL relay with hundreds of notifications or requests in a few seconds, hitting rate limits and causing API errors.
- **Proposed Solution**: Implement a client-side token bucket rate limiter in `ApiClient`. It queues outgoing requests and shapes the traffic to stay within configured limits, returning warnings or executing backoffs locally.
- **Business Value**: Prevents application crashes due to unexpected rate limit rejections and ensures respectful utilization of server resources.
- **Effort Estimate**: M

---

## IDEA-400: Cryptographically Verifiable Session Revocation
- **Category**: Security
- **Problem**: When a user revokes an agent session, there is no cryptographic proof that the relay has acknowledged the revocation, leaving open questions about relay security.
- **Proposed Solution**: Upon receiving a logout or client revocation request, the relay returns a cryptographically signed receipt containing the client ID and timestamps of revocation. The CLI validates this signature and appends the receipt to a local revocation ledger.
- **Business Value**: Strengthens corporate compliance and security posture by providing undeniable proof of credential revocation.
- **Effort Estimate**: M

---

## IDEA-401: SDK Automatic Environment Context Ingestion
- **Category**: Feature
- **Problem**: When developers raise a HITL request in their agents, they must manually write code to collect execution context (such as OS version, Python version, git branch, current command line) to append to the request.
- **Proposed Solution**: Add an option in the SDK (`auto_collect_context=True`) that automatically gathers metadata about the running environment (CPU arch, OS, Git commit SHA, calling script name) and attaches it to the request details.
- **Business Value**: Saves developer time by automatically enriching issues with the diagnostic data needed for resolution.
- **Effort Estimate**: S

---

## IDEA-402: Multi-Channel Interactive Console Fallback
- **Category**: Integration
- **Problem**: If the HITL service or relay is entirely down, developers cannot run their agents at all because all requests fail, forcing them to modify agent code to bypass the HITL checks.
- **Proposed Solution**: Implement a fallback parameter `--local-fallback` in the CLI. When the relay is unreachable, the command falls back to an interactive local terminal prompt where a local operator can type the response directly.
- **Business Value**: Ensures local developmental and testing workflows can continue even during full remote backend outages.
- **Effort Estimate**: M
