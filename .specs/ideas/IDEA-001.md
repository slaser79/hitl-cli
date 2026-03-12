# Ideas Batch — hitl-cli

## IDEA-091: GitHub Action for Mobile-First HITL Approvals

- **Category**: Integration
- **Problem**: CI/CD pipelines often need human approval for deployments or sensitive steps, but current solutions (like GitHub environments) are sometimes too rigid or disconnected from the developer's mobile workflow.
- **Proposed Solution**: A dedicated GitHub Action that wraps `hitl-cli notify` and `hitl-cli request`, allowing easy integration into `.github/workflows/`. It could automatically handle API key setup and link the HITL request to the specific workflow run.
- **Business Value**: Improves developer productivity and security by bringing HITL directly into the DevOps pipeline.
- **Effort Estimate**: S

---

## IDEA-092: Multi-User Consensus for Critical Actions

- **Category**: Feature
- **Problem**: Critical actions (e.g., "Delete Production Database") might require more than one human to approve. Current implementation is 1:1.
- **Proposed Solution**: Extend the `request` command to support multiple recipients (e.g., `--recipient user-a --recipient user-b`) and a strategy (e.g., `all`, `any`, `majority`). The CLI waits until the condition is met.
- **Business Value**: Enhances security and reduces risk for high-stakes operations.
- **Effort Estimate**: M

---

## IDEA-093: HITL-Proxy for SSH (Human 2FA)

- **Category**: Security
- **Problem**: SSH keys can be stolen. Traditional 2FA is often cumbersome.
- **Proposed Solution**: A `ForceCommand` or `AuthorizedKeysCommand` script that triggers a `hitl-cli request` on the user's phone before allowing the SSH session to establish.
- **Business Value**: Adds a powerful layer of security to critical infrastructure with a seamless mobile experience.
- **Effort Estimate**: M

---

## IDEA-094: LangChain / LlamaIndex First-Class Tools

- **Category**: Integration
- **Problem**: AI developers using LangChain or LlamaIndex have to manually wrap the `hitl-cli` SDK to use it as a "Tool" or "Toolspec" for their agents.
- **Proposed Solution**: Provide first-class integrations (e.g., `from hitl_cli.integrations.langchain import HITLTool`) that follow the expected interfaces of these popular frameworks.
- **Business Value**: Accelerates adoption among AI engineers and positions `hitl-cli` as the go-to for agentic HITL.
- **Effort Estimate**: S

---

## IDEA-095: "Silent" Background Status Updates (Heartbeats)

- **Category**: Performance
- **Problem**: Monitoring long-running tasks via notifications can be noisy. Sometimes you just want to know "it's still running" without a push notification alert.
- **Proposed Solution**: Add a `--silent` or `--background` flag to `notify` that updates a "status" field in the mobile app's agent view without triggering a high-priority alert.
- **Business Value**: Enables non-intrusive monitoring of background processes, reducing alert fatigue.
- **Effort Estimate**: S

---

## IDEA-096: Web Framework Dependency Injection (FastAPI/Flask)

- **Category**: Integration
- **Problem**: Backend developers using FastAPI or Flask have to manually manage the `HITL` client lifecycle and configuration.
- **Proposed Solution**: Provide a dependency provider for popular web frameworks (e.g., `Depends(get_hitl_client)`) that automatically handles auth, connection pooling, and configuration.
- **Business Value**: Simplifies adoption for backend engineers building HITL-powered web services.
- **Effort Estimate**: S

---

## IDEA-097: "Proxy-as-a-Service" (Daemon Mode)

- **Category**: Feature
- **Problem**: Running `hitl-cli proxy` requires keeping a terminal open. If the terminal closes, the MCP connection drops.
- **Proposed Solution**: Add a `hitl-cli proxy --daemon` or `hitl-cli proxy install-service` command that runs the proxy as a background system service (systemd/launchd).
- **Business Value**: Provides a robust, "always-on" integration for tools like Claude Desktop without manual intervention.
- **Effort Estimate**: M

---

## IDEA-098: Session Persistence & Resumption (Interrupt Protection)

- **Category**: Reliability
- **Problem**: If the CLI is interrupted (e.g., network drop, accidental Ctrl+C) while waiting for a human response, the state is lost.
- **Proposed Solution**: Persist active requests to a local SQLite or JSON file. Add a `hitl-cli resume <request_id>` command to reconnect and wait for the response.
- **Business Value**: Prevents data loss and improves reliability for long-running human interactions.
- **Effort Estimate**: M

---

## IDEA-099: "Wait-for-Agent" (Online Check)

- **Category**: Feature
- **Problem**: A script might want to send a request to a specific agent, but that agent (mobile app) might be offline.
- **Proposed Solution**: Add a `--wait-until-online` flag that makes the CLI poll or wait until the relay reports the target agent is connected before sending the request.
- **Business Value**: Improves the success rate of interactions in intermittent connectivity scenarios.
- **Effort Estimate**: S

---

## IDEA-100: Shell Prompt Integration (`hitl-cli status --pending-count`)

- **Category**: UX
- **Problem**: Developers want to know if they have pending HITL requests without switching apps.
- **Proposed Solution**: A lightweight command `hitl-cli status --pending-count` that can be easily integrated into shell prompts (Zsh/Bash) or status bars (tmux/polybar).
- **Business Value**: Increases responsiveness to HITL requests by making them visible in the developer's primary workspace.
- **Effort Estimate**: S

---

## IDEA-101: "Sandbox Mode" for Risk-Free Development

- **Category**: UX
- **Problem**: Testing HITL integrations might accidentally send real notifications or requests during development/CI.
- **Proposed Solution**: Add a global `--sandbox` flag that prevents any requests from reaching the real relay and instead logs them locally or sends them to a "safe" developer-only agent.
- **Business Value**: Prevents accidental "production" notifications during development, reducing risk.
- **Effort Estimate**: S

---

## IDEA-102: `hitl-sudo` Wrapper for Sensitive Operations

- **Category**: Security
- **Problem**: Elevating privileges on a machine should be strictly controlled.
- **Proposed Solution**: A wrapper script `hitl-sudo <command>` that requires approval via the mobile app before executing the command with `sudo`.
- **Business Value**: Provides a modern, mobile-first alternative to traditional privilege escalation controls.
- **Effort Estimate**: M

---

## IDEA-103: Adaptive Timeouts Based on Historical Response Times

- **Category**: Performance
- **Problem**: Fixed timeouts (e.g., 15 mins) are often too long or too short depending on the user's habits.
- **Proposed Solution**: The CLI tracks how long it takes for a human to respond to different types of prompts and suggests/uses an adaptive timeout based on historical data.
- **Business Value**: Optimizes wait times and resource usage, improving overall system efficiency.
- **Effort Estimate**: L

---

## IDEA-104: Client-Side "Quiet Hours" Support

- **Category**: UX
- **Problem**: Automated scripts might send notifications in the middle of the night, bothering the user.
- **Proposed Solution**: Add a client-side configuration for "quiet hours" where `notify` commands are either suppressed or queued until a "safe" time.
- **Business Value**: Improves user experience and prevents burnout/annoyance from automated systems.
- **Effort Estimate**: S

---

## IDEA-105: SDK Mocking & Null-Client for Testing

- **Category**: Tech Debt
- **Problem**: SDK users want to test their code's logic without actually making network calls.
- **Proposed Solution**: Provide a `MockHITL` or `NullHITL` implementation in the SDK that follows the same interface but returns pre-configured responses or simply logs actions.
- **Business Value**: Drastically simplifies unit and integration testing for applications using the `hitl-cli` SDK.
- **Effort Estimate**: S
