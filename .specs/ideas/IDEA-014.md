# Ideas Batch — hitl-cli (Batch 20)

## IDEA-286: "Prompt-to-Speech" Accessibility Mode
- **Category**: UX
- **Problem**: Visually impaired developers or those in hands-busy environments (e.g., lab work) cannot easily interact with technical prompts on a mobile screen.
- **Proposed Solution**: Implement native screen-reader optimizations in the mobile app and a `--voice` flag in the CLI that adds phonetic hints for complex technical terms (e.g., "G-C-C" instead of "gcc").
- **Business Value**: Ensures inclusivity and enables hands-free operation in industrial/technical environments.
- **Effort Estimate**: M

---

## IDEA-287: "Request-Response" State Diff
- **Category**: Observability
- **Problem**: It's often hard to audit exactly what effect a human's "Approval" had on the system state, leading to "what happened?" debugging sessions.
- **Proposed Solution**: A new command `hitl-cli diff <request_id>` that compares a pre-request system snapshot (files, env, git) with the state after the human responded and the agent acted.
- **Business Value**: Provides high-fidelity auditing and easier debugging of human-driven changes.
- **Effort Estimate**: M

---

## IDEA-288: "Agent Sentiment" Back-off Logic
- **Category**: UX / Reliability
- **Problem**: Agents can be "annoying" if they keep asking questions when a human is clearly frustrated, leading to poor decisions or the human disabling the agent.
- **Proposed Solution**: Use a lightweight local NLP model to detect frustration or urgency in human "Reasoning" fields. The SDK then automatically increases the `wait_between_requests` or suggests the agent "summarize multiple tasks."
- **Business Value**: Improves human-AI harmony and prevents "agent rejection" by end-users.
- **Effort Estimate**: M

---

## IDEA-289: "Zero-Knowledge" Permission Challenges
- **Category**: Security
- **Problem**: Humans shouldn't have to send a secret (like a password) to an agent to prove they have permission to authorize an action.
- **Proposed Solution**: Implement a challenge-response protocol where the agent sends a nonce, and the human signs it with a local hardware key. The agent verifies the signature without ever seeing the human's secret key.
- **Business Value**: Enables "Zero Trust" authorization for high-security infrastructure.
- **Effort Estimate**: L

---

## IDEA-290: "Browser IDE" Sidebar Integration
- **Category**: Integration
- **Problem**: Developers using cloud IDEs (GitHub Codespaces, Gitpod) lose the terminal context when switching to mobile, and want a more integrated experience.
- **Proposed Solution**: A VS Code / Browser extension that uses the `hitl-cli` local HTTP API to show pending requests directly in the IDE sidebar, mirroring the mobile app experience.
- **Business Value**: Keeps developers in their "flow state" and increases response speed.
- **Effort Estimate**: L

---

## IDEA-291: "Automated Regression" from Interaction History
- **Category**: Testing
- **Problem**: As agents evolve, it's hard to ensure their autonomous logic still aligns with how humans decided things in the past.
- **Proposed Solution**: A tool `hitl-cli generate-tests` that parses `history.jsonl` and generates a suite of regression tests that mock human responses based on previous decisions for similar prompts.
- **Business Value**: Ensures "behavioral consistency" and safe agent upgrades over time.
- **Effort Estimate**: M

---

## IDEA-292: "Multi-Language" Prompt Templates
- **Category**: UX
- **Problem**: Global teams need to interact with agents in their native languages, but hardcoding translations in every script is unmaintainable.
- **Proposed Solution**: Support for `.hitl/i18n/*.yaml` files. The agent sends a `template_id` and `context`, and the mobile app renders the prompt in the human's preferred language.
- **Business Value**: Enables global adoption and reduces cognitive load for non-English speaking engineers.
- **Effort Estimate**: M

---

## IDEA-293: "In-Progress" Heartbeat Ticker
- **Category**: Reliability / UX
- **Problem**: After a human approves a long-running task (e.g., "Deploy Cluster"), they often feel "blind" to whether the agent is actually working or has crashed.
- **Proposed Solution**: The SDK sends periodic "Heartbeat" notifications (e.g., every 60s) with a status message. The mobile app shows this as a "Live Activity" or a pulsing status icon.
- **Business Value**: Reduces human anxiety and prevents unnecessary "did it work?" manual checks.
- **Effort Estimate**: S

---

## IDEA-294: "Local Agent Discovery" & Coordination
- **Category**: Architecture
- **Problem**: Multiple agents running on the same machine/network might bombard the same human with overlapping or conflicting requests.
- **Proposed Solution**: Agents use mDNS/DNS-SD to find each other locally and negotiate a "Shared Queue" or "Priority Lock" before sending a push notification.
- **Business Value**: Prevents "notification storms" and ensures a coherent interaction experience for the human.
- **Effort Estimate**: L

---

## IDEA-295: "Proof of Personhood" Liveness Check
- **Category**: Security
- **Problem**: Malicious software could potentially compromise a device and "auto-tap" approvals on the human's behalf.
- **Proposed Solution**: For "Level 3" sensitive actions, require a "liveness" check in the mobile app (e.g., "Blink your eyes" or a simple CAPTCHA) before the response is accepted.
- **Business Value**: Protects against advanced "device takeover" attacks for critical infrastructure.
- **Effort Estimate**: M

---

## IDEA-296: "Custom Mobile CSS" for Brandable Prompts
- **Category**: UX
- **Problem**: Some requests are more important than others, but they all look identical on the mobile app, making it hard to prioritize at a glance.
- **Proposed Solution**: Allow the agent to send a small, safe CSS-in-JSON snippet (e.g., `{"headerColor": "#ff0000", "icon": "warning"}`) that the mobile app uses to theme the request UI.
- **Business Value**: Increases "situational awareness" and allows for corporate/team branding of agent interactions.
- **Effort Estimate**: S

---

## IDEA-297: "Human Response" Ephemeral Encryption
- **Category**: Security
- **Problem**: If the agent's process is dumped or logs are stolen, the human's past responses (which might contain sensitive reasoning) are exposed.
- **Proposed Solution**: Every human response is encrypted with a unique, one-time key that is purged from the agent's memory as soon as the specific task finishes.
- **Business Value**: Minimizes the blast radius of a compromised agent process.
- **Effort Estimate**: M

---

## IDEA-298: "Agent Identity" Attestation (TPM/Secure Enclave)
- **Category**: Security
- **Problem**: A relay could be tricked into thinking a malicious script is a "Trusted Agent."
- **Proposed Solution**: Use hardware attestation (like TPM or Apple Secure Enclave) to sign a "Manifest of Integrity" for the agent process. The human's app verifies this attestation before showing the request.
- **Business Value**: Provides hardware-level assurance that the agent hasn't been tampered with.
- **Effort Estimate**: L

---

## IDEA-299: "Predictive Conflict" Detection (Semantic)
- **Category**: Reliability
- **Problem**: Two agents might be working on different files that have a semantic dependency (e.g., API definition vs API client), leading to broken builds if both are approved independently.
- **Proposed Solution**: Use an LLM on the relay to analyze the "Intent" of all pending requests across an organization and flag those that have a high semantic overlap or potential conflict.
- **Business Value**: Prevents "silent" regressions caused by uncoordinated autonomous agents.
- **Effort Estimate**: L

---

## IDEA-300: "Human-in-the-Loop" Git Merge Driver
- **Category**: Integration
- **Problem**: Automatic git merges often fail on "semantic" conflicts that `git` can't understand, requiring manual developer intervention at their desk.
- **Proposed Solution**: A custom git merge driver that, when it hits a conflict, triggers a `hitl-cli request` showing the conflicting lines. The human picks the winner or types a resolution on their phone.
- **Business Value**: Enables "hands-free" CI/CD even when complex merges occur.
- **Effort Estimate**: M
