# Ideas Batch — hitl-cli (Batch 10)

## IDEA-136: Multi-Relay Configuration (Federation Support)

- **Category**: Feature
- **Problem**: Users are currently locked to a single `HITL_SERVER_URL`. Power users may want to use a private self-hosted relay for sensitive internal work and a public relay for open-source contributions.
- **Proposed Solution**: Update the config schema to support a list of "remotes". Commands like `hitl-cli login --remote private` or `hitl-cli request --remote public` would target specific servers.
- **Business Value**: Enables hybrid cloud/on-premise HITL strategies, increasing adoption in enterprise.
- **Effort Estimate**: M

---

## IDEA-137: Human Presence "Availability" API

- **Category**: Feature
- **Problem**: Agents send requests blindly, often waiting for a human who is asleep or away from their phone.
- **Proposed Solution**: Add a `hitl-cli agent check-presence` command and SDK method. The relay tracks the human's last "active" timestamp (e.g., app opened) and returns a status like `online`, `away`, or `offline`.
- **Business Value**: Allows agents to intelligently skip or reroute tasks if no human is available, improving workflow efficiency.
- **Effort Estimate**: M

---

## IDEA-138: Interactive "Dry Run" Preview Mode

- **Category**: UX
- **Problem**: Developers can't easily see how their complex prompts or choices will look on the mobile app without actually triggering a notification.
- **Proposed Solution**: Add a `--preview` flag to the `request` command. Instead of sending the request, the CLI renders a mock mobile screen in the terminal using `rich` or opens a local browser tab with a simulator.
- **Business Value**: Speeds up development and improves the quality of human-facing prompts.
- **Effort Estimate**: S

---

## IDEA-139: Local "HITL Gateway" HTTP Server

- **Category**: Integration
- **Problem**: Invoking the `hitl-cli` process for every notification in a high-frequency system (like a log watcher) adds significant process-spawn overhead.
- **Proposed Solution**: Add `hitl-cli serve` which starts a lightweight local HTTP server. Other local scripts can send JSON payloads to `localhost:8485` to trigger HITL actions via the already-authenticated CLI session.
- **Business Value**: Enables high-performance local integrations with zero process-spawn latency.
- **Effort Estimate**: M

---

## IDEA-140: Support for `NO_COLOR` and `CLICOLOR` Standard Env Vars

- **Category**: UX
- **Problem**: The CLI uses rich formatting and emojis which can break in some legacy terminals, CI logs, or text-only environments.
- **Proposed Solution**: Implement support for industry-standard environment variables like `NO_COLOR` (to disable all ANSI colors) and `CLICOLOR` (to control color output).
- **Business Value**: Ensures a professional and readable experience across all terminal types and logging systems.
- **Effort Estimate**: S

---

## IDEA-141: Automatic "Agent Persona" Randomizer

- **Category**: UX
- **Problem**: Managing multiple test agents can be confusing if they all have generic names like "Agent 1", "Agent 2".
- **Proposed Solution**: If no `--name` is provided during `login` or `create-agent`, the CLI generates a fun, unique persona (e.g., "Rusty Robot", "Silver Surfer") with a corresponding emoji.
- **Business Value**: Makes the HITL experience more engaging and helps developers distinguish between their various agent instances.
- **Effort Estimate**: S

---

## IDEA-142: Batch Request Cancellation and Expiry

- **Category**: Feature
- **Problem**: If a developer's script loops and sends 100 requests by accident, they have to manually dismiss them on their phone.
- **Proposed Solution**: Add `hitl-cli requests cancel-all` and a `--expires-in <seconds>` flag for the `request` command. The relay automatically expires and hides requests after the specified time.
- **Business Value**: Improves user experience by preventing "notification storms" from broken automation.
- **Effort Estimate**: S

---

## IDEA-143: Human Response "Certainty" Level

- **Category**: UX
- **Problem**: Agents treat all human responses as absolute truths. A human might want to say "Yes, but I'm not 100% sure, check the logs too."
- **Proposed Solution**: Add a `--with-certainty` flag to `request`. The mobile app adds a slider (0-100%) to the response. The CLI returns both the choice and the certainty score.
- **Business Value**: Allows agents to implement sophisticated "confidence-based" logic in their workflows.
- **Effort Estimate**: M

---

## IDEA-144: Request "Tagging" and Metadata

- **Category**: Performance
- **Problem**: It's hard to filter interaction history by project, environment, or task type.
- **Proposed Solution**: Add a `--tag` or `--meta` flag to all HITL commands (e.g., `--tag project:apollo --tag env:prod`). This metadata is stored in the local audit log and sent to the relay for better dashboarding.
- **Business Value**: Enables advanced analytics and compliance reporting for HITL-intensive organizations.
- **Effort Estimate**: S

---

## IDEA-145: Integration with System Notification Centers (Desktop)

- **Category**: UX
- **Problem**: If the human is at their desk, they might prefer a desktop notification (macOS/Windows/Linux) instead of or in addition to a mobile push.
- **Proposed Solution**: When `hitl-cli` is waiting for a response, it can optionally trigger a native desktop notification via `plyer` or similar.
- **Business Value**: Improves response times for developers working at their machines.
- **Effort Estimate**: S

---

## IDEA-146: Request "Style" (Visual)

- **Category**: UX
- **Problem**: All requests look the same in the mobile app. A human can't quickly distinguish between a "Warning" and a "Success".
- **Proposed Solution**: Add `--style [info|warning|error|success]` to the `request` and `notify` commands. The mobile app uses different background colors or icons based on the style.
- **Business Value**: Improves human cognitive processing speed for large volumes of notifications.
- **Effort Estimate**: S

---

## IDEA-147: Support for HTTP/2 and HTTP/3

- **Category**: Performance
- **Problem**: HTTP/1.1 latency can be a bottleneck for agents sending many small notifications or heartbeats.
- **Proposed Solution**: Enable HTTP/2 and HTTP/3 support in `httpx.AsyncClient` (already a dependency). This allows for better multiplexing and reduced header overhead.
- **Business Value**: Improves responsiveness and reduces network overhead for global agent fleets.
- **Effort Estimate**: S

---

## IDEA-148: Support for Time-Limited "Burn-on-Read" Requests

- **Category**: Security
- **Problem**: Some requests contain highly sensitive temporary credentials that should be deleted from the human's phone immediately after being read or used.
- **Proposed Solution**: Add a `--burn-on-read` flag. The mobile app wipes the request data from local storage and the server as soon as the response is sent or the view is closed.
- **Business Value**: Minimizes the window of exposure for extremely sensitive data.
- **Effort Estimate**: M

---

## IDEA-149: Integrated "Shell Execution" Request Type

- **Category**: Feature
- **Problem**: Sometimes an agent needs a human to run a command locally and provide the output (e.g., "Run `ls -l` and paste result").
- **Proposed Solution**: Add a specialized request type that provides a "Copy Command" button in the mobile app and a "Paste Result" field. The CLI formats the output cleanly for the agent.
- **Business Value**: Simplifies complex interactive troubleshooting where the human acts as an extension of the agent's environment.
- **Effort Estimate**: M

---

## IDEA-150: Automated "System Health" Dashboard in Mobile App

- **Category**: Observability
- **Problem**: Humans can't see the overall health of their agent fleet (latency, error rates, uptime) from the mobile app.
- **Proposed Solution**: Add a background telemetry reporter to the CLI that sends anonymized aggregate health metrics (if opted-in) to a new "Dashboard" view in the mobile app.
- **Business Value**: Provides humans with high-level oversight of their autonomous systems from anywhere.
- **Effort Estimate**: L
