---
id: SPEC-HITL-AGY-001
title: "Antigravity Channel Plugin"
status: "Draft"
owner: "hitl"
created_by: "cos"
last_updated: 2026-06-11
products: ["hitl-cli", "hitl-channel"]
depends_on:[]
---

# Antigravity Channel Plugin

## 0. Empire foreground tracking (auto, do not skip)

```bash
empire_bookend_start() { :; }
empire_bookend_heartbeat_bg() { :; }
empire_bookend_end() { :; }
source ~/empire-tools/empire-bookend.sh 2>/dev/null || true
empire_bookend_start "empire-spec" "antigravity channel plugin"
trap 'empire_bookend_end failed "interrupted"' EXIT
empire_bookend_heartbeat_bg  # heartbeat (skill may exceed 90 min)
```

## 1. Executive Summary
The CEO requires a two-way, out-of-band communication channel with Google Antigravity agents so that agents can ask clarifying questions, present choices, and receive feedback without stalling the terminal console. We will establish this by extending the existing `hitl-channel` (Claude Code) infrastructure, allowing Antigravity agents to connect as MCP clients and receive `notifications/claude/channel` inbound messages via an explicit SDK Plugin (`HitlChannelPlugin`).

## 2. CEO Business Outcomes
- [ ] The user can respond to Antigravity agent clarifying questions from their phone while away from the keyboard, unblocking long-running autonomous tasks. (Verified by CV1.)
- [ ] The user can review and approve agent tool-execution choices directly from the `hitl-app` via interactive choice menus. (Verified by CV2.)
- [ ] New Antigravity agents automatically inherit the identical communication and privacy constraints currently defined for Claude, accelerating agent-to-production time without rewriting UI flows. (Verified by AV1.)

## 3. User Stories
*No runtime-evaluation surface; sibling-primitive audit not applicable.*

- As a CEO, I want to securely pair my mobile device with the Antigravity agent using a short-lived 6-digit code, so that unauthorized users on the same network cannot hijack the session.
- As a CEO, I want to receive push notifications on my phone when an Antigravity agent needs input, so that I don't have to constantly monitor the terminal.
- As a CEO, I want to tap interactive choices on my phone to answer the agent's questions, so that the agent can resume execution immediately with clear direction.

## 4. Technical Implementation & Architecture
### 4.0 Target State — the end-state picture in one read
The Google Antigravity agent lifecycle is extended via an explicit `HitlChannelPlugin` added to its configuration. When the agent starts, this plugin initializes a local MCP Stdio connection to the existing `hitl-channel` process. The plugin exposes the standard `reply_to_hitl` and `present_choices_to_hitl` tools to the agent's LLM context, making them available as native capabilities without altering the core agent loop.

Simultaneously, the plugin registers a notification handler on the MCP client for `notifications/claude/channel`. When the CEO replies on the `hitl-app`, the message traverses the relay and the channel, which pushes the notification to the agent. The plugin intercepts this notification and asynchronously injects it into the agent's prompt context (or message inbox), waking the agent to process the CEO's input without requiring a new terminal command.

By coupling the existing robust `hitl-channel` transport with a dedicated Antigravity plugin, the architecture achieves bilateral communication while remaining cleanly decoupled. The agent framework remains unaware of the mobile application's existence, and the mobile application continues treating the remote agent as just another Claude instance, ensuring maximum reuse of the existing infrastructure.

### 4.1 Architecture
Data flow matches the existing Claude Code architecture:
`Antigravity Agent` <--(MCP Stdio)--> `hitl-channel` <--(WS)--> `hitl-shin-relay` <--(WS/FCM)--> `hitl-app`.
Inbound messages flow from `hitl-app` → `hitl-shin-relay` → `hitl-channel` → `mcp.notification("notifications/claude/channel")` → `HitlChannelPlugin` notification interceptor → Agent context.

### 4.2 Components
- `hitl_channel_plugin.py`: A new Python module located within the `hitl-cli` package. It implements the `HitlChannelPlugin` class. The class is responsible for spawning the `bun src/server.ts` process via the Antigravity `McpStdioServer` transport.
- The plugin must register a hook to intercept `notifications/claude/channel`. 
- **Pairing Flow Support**: The plugin must explicitly handle notifications with `type: "pairing_request"`. When `hitl-channel` emits a pairing code, the plugin must intercept it and log the 6-digit code securely to the terminal (e.g., via `sys.stderr` or standard agent logging). This guarantees that only a user with access to the agent's terminal can see the code and pair their device, matching Claude's existing security model. Standard conversational notifications will be synthesized into user-turn or system messages for the LLM.

### 4.3 UI/UX & Design System Adherence
Zero UI changes. `hitl-app` and `hitl-channel` process the payloads exactly as they do for Claude. The Antigravity agent must adhere to the exact JSON schema required by `present_choices_to_hitl` and `reply_to_hitl`.

### 4.4 DRY & KISS Principles
We leverage the existing `hitl-channel` server intact, rather than rewriting a dedicated Antigravity relay server. The explicit SDK plugin keeps the Antigravity agent configuration declarative and isolated from the core execution engine, adhering to the SDK's composability design.

## 5. Delivery Plan
### Phase 1: MV Spec
- **Scope:** Provide a functional `HitlChannelPlugin` in `hitl-cli` that connects an Antigravity agent to `hitl-channel`. It must successfully intercept a `pairing_request` notification to print the code, and intercept an inbound text message to print to the console.
- **CEO Outcome:** Verifies that Antigravity agents can receive phone push notifications and can be securely paired without structural blockers.

### Phase 2: Fully Integrated Agent Inbox
- **Scope:** Implement the context-injection so the inbound message is actually consumed by the LLM, and the agent responds via `reply_to_hitl`.
- **CEO Outcome:** True bilateral conversation between the CEO on mobile and the Antigravity agent on the desktop.

## 6. Regression Analysis & Testing Strategy
### 6.1 Regression Risks
Since `hitl-channel` is unmodified, risk to Claude Code workflows is zero. The main risk is the Antigravity agent's event loop blocking on the MCP connection or failing to cleanly shut down the Stdio process when the agent terminates. Mitigation: strictly test the Stdio process cleanup lifecycle in the plugin's `__del__` or `on_session_end` hook.

### 6.2 Testing Strategy
- **Unit:** Mock the `McpStdioServer` and verify the plugin correctly registers the notification handler and formats the injected prompt.
- **E2E:** Spawn a trivial "Echo" Antigravity agent via the CLI, connect from `hitl-app`, send a message, and verify the agent echoes it back via `reply_to_hitl`.

## 7. Acceptance Criteria
### Agent-verifiable
- [ ] **AV1** `HitlChannelPlugin` parses configuration and correctly attaches the `hitl-channel` MCP server without crashing.
- [ ] **AV2** The plugin registers a valid notification handler for `notifications/claude/channel` that correctly extracts the `content` and `meta.sender_id`.

### CEO device-verify (work-with-CEO on device)
- [ ] **CV1** The CEO initiates a pairing request from the `hitl-app`, observes the 6-digit code printed in the Antigravity terminal, and successfully completes the pairing flow.
- [ ] **CV2** The CEO receives a push notification on their physical iPhone when the Antigravity agent invokes `reply_to_hitl`.
- [ ] **CV3** The CEO taps a choice in the `hitl-app`, and the Antigravity agent's log shows it processed the choice and advanced to the next step.

## 7a. User-Story → AC Traceability

| User story phrase | AC # | Notes |
|---|---|---|
| "securely pair my device" | CV1 | Ensure no unauthorized access |
| "receive push notifications on my phone" | CV2 | Basic outbound comms |
| "tap interactive choices on my phone" | CV3 | Interactive input |
| "agent can resume execution" | AV2, CV3 | Agent consumes the input and acts |

## 7b. Doctrine stability
No volatile PRs cited. The strict adherence to `notifications/claude/channel` is defined by the fixed contract established by `hitl-channel`.
