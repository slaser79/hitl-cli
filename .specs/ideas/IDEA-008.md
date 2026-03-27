# Ideas Batch — hitl-cli (Batch 14)

## IDEA-196: Offline Mode with Local Sync
- **Category**: Feature
- **Problem**: Interaction failure and potential state loss when the agent loses internet connectivity during a pending human response.
- **Proposed Solution**: Implement a local SQLite queue to store outgoing requests and incoming responses, syncing automatically once connectivity is restored.
- **Business Value**: Increases reliability for autonomous agents in unstable network environments.
- **Effort Estimate**: M

---

## IDEA-197: Interactive "Dry Run" Mode for Agents
- **Category**: UX / DX
- **Problem**: Notification fatigue and risk of unintended actions during the development and testing phase of agents.
- **Proposed Solution**: Add a `--dry-run` flag to simulate human interaction locally in the terminal instead of sending it to the mobile app.
- **Business Value**: Accelerates development and reduces notification noise for human users.
- **Effort Estimate**: S

---

## IDEA-198: Support for Structured Human Responses (JSON Schema)
- **Category**: Feature / SDK
- **Problem**: Inability for humans to provide complex structured data (forms) that agents can parse reliably beyond simple strings.
- **Proposed Solution**: Allow agents to send a JSON Schema; the mobile app renders a dynamic form, and the response is validated against the schema.
- **Business Value**: Enables complex data entry and decision-making workflows.
- **Effort Estimate**: L

---

## IDEA-199: "On-Call" Team Rotation Integration
- **Category**: Integration / Feature
- **Problem**: Critical agent requests getting blocked if the primary human user is unavailable or off-duty.
- **Proposed Solution**: Integrate with PagerDuty/Opsgenie to route HITL requests to the person currently "on-call" for the relevant team.
- **Business Value**: Ensures high-availability for critical autonomous operations.
- **Effort Estimate**: M

---

## IDEA-200: Biometric Challenge for High-Risk Approvals
- **Category**: Security
- **Problem**: Risk of unauthorized approval of sensitive actions if a phone is lost or left unlocked.
- **Proposed Solution**: Add a `--require-biometric` flag that forces FaceID/TouchID/Fingerprint validation on the mobile app before approval.
- **Business Value**: Provides bank-grade security for high-stakes autonomous operations.
- **Effort Estimate**: M

---

## IDEA-201: Global "Quiet Hours" for Non-Critical Notifications
- **Category**: UX
- **Problem**: User burnout and notification fatigue from non-critical agent updates during sleep or focused work hours.
- **Proposed Solution**: Allow defining "Quiet Hours" where low-priority requests are queued or delivered silently without push notifications.
- **Business Value**: Improves long-term user adoption and well-being.
- **Effort Estimate**: S

---

## IDEA-202: "Agent Heartbeat" — Low-Bandwidth Status Streaming
- **Category**: UX / Observability
- **Problem**: Human uncertainty about agent progress during long-running tasks without frequent, disruptive notifications.
- **Proposed Solution**: A lightweight heartbeat mechanism showing a live progress bar or status line in the mobile app.
- **Business Value**: Provides real-time visibility and peace of mind without interrupting the human.
- **Effort Estimate**: M

---

## IDEA-203: Support for File Attachments in Requests
- **Category**: Feature / Integration
- **Problem**: Lack of context (screenshots, logs, reports) for humans to make informed decisions based solely on text prompts.
- **Proposed Solution**: Enable the `request` and `notify` commands to include file attachments that are displayed in the mobile app.
- **Business Value**: Enables context-aware decision-making by providing actual evidence to the human.
- **Effort Estimate**: L

---

## IDEA-204: "Shadow Concordance" Mode (Trust Building)
- **Category**: Feature / Quality
- **Problem**: Organizational hesitation to grant agents autonomy due to a lack of data on decision-making quality.
- **Proposed Solution**: A mode where the agent records its intended choice and compares it with the human's actual choice to generate a concordance report.
- **Business Value**: Safely builds data-driven confidence in autonomous systems.
- **Effort Estimate**: M

---

## IDEA-205: Integration with Jupyter Notebooks (%hitl magic)
- **Category**: Integration / DX
- **Problem**: No easy way for data scientists to pause long-running notebooks for human review of plots or results.
- **Proposed Solution**: A Jupyter extension with a `%hitl` magic command to send cell outputs (images/tables) to a human for review.
- **Business Value**: Brings HITL to the AI/ML research community, enabling human-in-the-loop evaluation.
- **Effort Estimate**: S

---

## IDEA-206: Multi-User Consensus (Poll Mode)
- **Category**: Feature / Security
- **Problem**: Single-human approval may be insufficient for extremely sensitive or high-impact actions (e.g., "Three-man rule").
- **Proposed Solution**: A `--consensus N` flag requiring N different humans to approve the same choice before proceeding.
- **Business Value**: Implements robust governance and risk management for high-impact operations.
- **Effort Estimate**: L

---

## IDEA-207: `hitl-cli doctor --fix` (Automated Configuration Repair)
- **Category**: UX / Tech Debt
- **Problem**: Manual and tedious repair of common configuration/auth issues identified by the `doctor` command.
- **Proposed Solution**: Add an `--fix` flag to the `doctor` command to automatically repair issues like stale tokens or wrong permissions.
- **Business Value**: Reduces support burden and improves the "Day 2" experience.
- **Effort Estimate**: S

---

## IDEA-208: "Context Injection" from Git / Env
- **Category**: Feature / UX
- **Problem**: Prompts often lack background context (branch, server, env), forcing manual inclusion by developers.
- **Proposed Solution**: Automatically append system metadata (git branch, hostname, env vars) to requests as viewable metadata in the app.
- **Business Value**: Saves time and ensures humans always have the necessary context for safe decisions.
- **Effort Estimate**: S

---

## IDEA-209: SDK support for "Human-Driven Remote Config"
- **Category**: Feature / SDK
- **Problem**: Changing agent parameters at runtime usually requires a code change or manual process restart.
- **Proposed Solution**: An SDK pattern (`get_config(schema)`) that prompts a human to fill out a structured form to live-configure the agent.
- **Business Value**: Turns the mobile app into a remote control dashboard for live autonomous agents.
- **Effort Estimate**: M

---

## IDEA-210: Adaptive Timeouts Based on Human Response History
- **Category**: UX / Performance
- **Problem**: Hardcoded timeouts being either too short (causing failures) or too long (causing idling) for varying task complexities.
- **Proposed Solution**: Track user response times per request type and use "Adaptive Timeouts" to balance speed and reliability.
- **Business Value**: Optimizes agent performance by aligning expectations with actual human behavior.
- **Effort Estimate**: M
