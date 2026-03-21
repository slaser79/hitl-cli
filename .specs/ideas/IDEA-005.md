# Ideas Batch — hitl-cli (Batch 11)

## IDEA-151: Support for Custom Haptic/Audio Cues on Mobile

- **Category**: UX
- **Problem**: All HITL notifications use the same default system alert, making it difficult for users to distinguish between low-priority updates and critical "System Down" blocks without looking at their phone.
- **Proposed Solution**: Allow the `notify` and `request` commands to include a `--cue` or `--alert-id` parameter. The mobile app can then trigger specific vibration patterns or custom sounds to provide eyes-free context.
- **Business Value**: Reduces response time for critical events and improves user focus by allowing them to filter by sound/feel.
- **Effort Estimate**: S

---

## IDEA-152: Web-based Approval Dashboard for Teams

- **Category**: Feature
- **Problem**: Mobile-only interaction is excellent for individuals, but teams often need a shared "Command Center" where anyone on-call can see and resolve pending HITL requests.
- **Proposed Solution**: Develop a lightweight, secure web dashboard that mirrors the mobile app's functionality. It would support team-based login and allow multiple people to view the same agent's queue.
- **Business Value**: Essential for enterprise adoption where shared accountability and auditability are required.
- **Effort Estimate**: L

---

## IDEA-153: Integration with OpenTelemetry (OTel)

- **Category**: Tech Debt
- **Problem**: In complex agentic workflows, tracing a request from the AI agent through the CLI to the Relay and finally the Human is difficult, making it hard to identify latency bottlenecks.
- **Proposed Solution**: Add OpenTelemetry instrumentation to the `ApiClient` and `HITL` SDK. Support standard trace propagation headers to link human interactions to the broader agent execution trace.
- **Business Value**: Improves observability and allows for data-driven optimization of human-in-the-loop latency.
- **Effort Estimate**: M

---

## IDEA-154: "Proof of Knowledge" Approval Challenges

- **Category**: Security
- **Problem**: One-tap approvals on mobile are convenient but can lead to "approval fatigue" where users accidentally authorize high-risk actions (e.g., prod database deletion) without reading.
- **Proposed Solution**: Add a `--challenge` flag to the `request` command. The mobile app will then require the user to answer a simple question (e.g., "What environment are you deploying to?") before the "Approve" button is enabled.
- **Business Value**: Significantly reduces the risk of catastrophic human error in autonomous systems.
- **Effort Estimate**: M

---

## IDEA-155: SDK-level Response Caching (Time-to-Live)

- **Category**: Performance
- **Problem**: Agents often repeat the same high-level question (e.g., "Is the staging environment ready?") multiple times within a short window, causing redundant notifications for the human.
- **Proposed Solution**: Implement an optional `cache_ttl` parameter in the `request_input` SDK method. If a response for the same prompt exists within the TTL, return it immediately without hitting the network.
- **Business Value**: Protects the human user from redundant "noisy" requests and reduces relay overhead.
- **Effort Estimate**: S

---

## IDEA-156: `hitl-cli network-test` Deep Connectivity Diagnostics

- **Category**: UX
- **Problem**: Setting up the CLI in restricted enterprise environments often fails due to proxies, MTU issues, or DNS misconfigurations that the standard `doctor` command doesn't diagnose.
- **Proposed Solution**: A specialized diagnostic command that performs a series of low-level network tests (HTTPS latency, WebSocket stability, SSL certificate chain validation, and MTU discovery) against the relay.
- **Business Value**: Drastically reduces support overhead for "cannot connect" issues in complex network environments.
- **Effort Estimate**: S

---

## IDEA-157: Support for Markdown Tables in Prompts

- **Category**: UX
- **Problem**: Agents often need humans to review tabular data (e.g., a list of changed files or pricing tiers), but current prompts render these as garbled plain text on small mobile screens.
- **Proposed Solution**: Update the relay and mobile app to support rendering Markdown tables. The CLI/SDK would detect table structures and ensure they are formatted for horizontal scrolling on mobile.
- **Business Value**: Enables higher-quality human decision-making by presenting complex data in its natural, readable format.
- **Effort Estimate**: M

---

## IDEA-158: Support for "Ephemeral" Agents (Auto-delete after session)

- **Category**: Feature
- **Problem**: CI/CD jobs and transient scripts often create "disposable" agents that clutter the user's agent list forever because they are never manually deleted.
- **Proposed Solution**: Add an `--ephemeral` or `--ttl` flag to `login` or agent creation. The relay will automatically prune these agents and their history after the specified duration or once the session ends.
- **Business Value**: Keeps the user's "Agent List" clean and manageable without manual maintenance.
- **Effort Estimate**: S

---

## IDEA-159: "Maintenance Mode" for Agents

- **Category**: Feature
- **Problem**: When an agent's host system is undergoing maintenance, it might continue to receive or trigger HITL requests that it cannot properly process, leading to inconsistent state.
- **Proposed Solution**: A `hitl-cli agent maintenance --on/--off` command that tells the relay to auto-defer or "busy-wait" any incoming requests for this agent, showing a "Under Maintenance" status to the human.
- **Business Value**: Improves system reliability and prevents confusing interactions during scheduled downtime.
- **Effort Estimate**: S

---

## IDEA-160: Integration with Microsoft Teams via Incoming Webhooks

- **Category**: Integration
- **Problem**: While Slack and Discord are popular, many corporate users live exclusively in Microsoft Teams and want to see HITL activity there alongside their other work.
- **Proposed Solution**: Provide a first-class integration for Teams Incoming Webhooks, allowing notifications to be mirrored to a specific Teams channel with actionable adaptive card buttons.
- **Business Value**: Expands the product's reach into the large Microsoft 365 enterprise ecosystem.
- **Effort Estimate**: S

---

## IDEA-161: Support for "Shadow" Mode (Read-only)

- **Category**: Feature
- **Problem**: Testing complex new agent logic is risky if every test run sends a real notification to the human's phone.
- **Proposed Solution**: A global `--shadow` mode where all HITL commands are executed and logged locally, but the actual push notification is suppressed at the relay level. The relay can optionally simulate a "default" success response.
- **Business Value**: Enables safe, high-velocity development and testing of HITL workflows without bothering the user.
- **Effort Estimate**: M

---

## IDEA-162: Automatic "Slow-down" Feedback from Human

- **Category**: UX
- **Problem**: AI agents can move faster than humans, sometimes flooding the user with more requests than they can process, leading to frustration and poor decision-making.
- **Proposed Solution**: Add a "Slow Down" button to the mobile app UI. When tapped, the relay includes a `backoff_hint` in the next API response, which the SDK/CLI respects by increasing its polling or sleep intervals.
- **Business Value**: Prevents user burnout and ensures a sustainable, healthy human-AI collaboration loop.
- **Effort Estimate**: M

---

## IDEA-163: Encrypted "Sensitive Data" Redaction in SDK

- **Category**: Security
- **Problem**: Agents might accidentally include secrets (API keys, passwords) in prompt text. Even with E2EE, this data persists in the human's notification history.
- **Proposed Solution**: Implement a client-side redaction utility in the SDK that scans prompt text for common sensitive patterns (regex-based) and masks them before the data is even encrypted or sent.
- **Business Value**: Provides a critical "last line of defense" against accidental credential leakage.
- **Effort Estimate**: S

---

## IDEA-164: "Race-to-Respond" Group Requests (First Winner Wins)

- **Category**: Feature
- **Problem**: For urgent tasks (e.g., "Acknowledge Incident"), waiting for one specific person is too slow. You want to blast the request to a group and have the first person's response lock the task.
- **Proposed Solution**: A new request strategy where the CLI sends a single prompt to multiple agent IDs. The relay tracks who responds first, fulfills the request, and notifies the other recipients that the task is "Claimed."
- **Business Value**: Minimizes mean-time-to-respond (MTTR) for critical operations in team environments.
- **Effort Estimate**: M

---

## IDEA-165: Exportable "HITL Session" Playbacks

- **Category**: UX/DX
- **Problem**: It is difficult to document or share how an interactive HITL workflow actually *looks* and *feels* for stakeholders without doing a live demo.
- **Proposed Solution**: A `hitl-cli history export-playback` command that converts a sequence of requests and responses into a standalone, interactive HTML file or a high-quality terminal GIF "walkthrough."
- **Business Value**: Dramatically improves the ability to "sell" HITL workflows internally and document them for non-technical users.
- **Effort Estimate**: M
