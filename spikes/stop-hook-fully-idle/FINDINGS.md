# Findings: Stop Hook Fully Idle Condition

## 1. Hypothesize

### What is unknown?
- The exact behavior of the Antigravity agent's execution loop when a Stop hook returns a `"decision": "block"` or `"decision": "continue"`.
- The exact keys passed to the Stop hook's standard input payload (specifically `fullyIdle` vs `fully_idle`).
- How to configure the hook to conditionally run its logic only when the agent is fully idle, either by exiting early (letting the stop proceed) or returning a continue decision (preventing the stop until fully idle).

### What you expect it to do
- The Stop hook receives a JSON payload on standard input containing `fullyIdle: true` or `fullyIdle: false`.
- If the hook script processes `fullyIdle == false`, it can either:
  - Return `{"decision": "block", "reason": "Wait for background tasks"}` to keep the agent execution loop running.
  - Exit with `sys.exit(0)` (no output) to allow the stop to proceed without performing the hook's main action (prompting the user).
- If the hook script processes `fullyIdle == true`, it executes the main action (prompting the human for review).

### Key questions
- Does the Antigravity system expect `"decision": "block"` or `"decision": "continue"` to prevent termination?
- What is the default behavior if the script exits with `0` but prints no JSON decision? Does the agent stop or block?
- How is the stop hook currently wrapper-invoked in this repository?

### Success criteria
- A working Python script prototype demonstrating how to handle `fullyIdle`.
- A completed knowledge document `.specs/knowledge/stop-hook-fully-idle.md` explaining the recipe and gotchas.

---

## 2. Experiments & Observations

### Experiment 1: Simulating Stop Hook Payload when `fullyIdle` is `false`
- **Hypothesis:** When `fullyIdle` is `false`, the hook script should detect it and print a `"decision": "block"` JSON message to standard output, preventing the agent from terminating, or exit with `0` silently if termination is allowed.
- **Command/Code:** `echo '{"executionNum": 1, "terminationReason": "model_stop", "fullyIdle": false}' | ./spikes/stop-hook-fully-idle/experiment_stop_hook.py`
- **Result:** PASS
- **Observed output:**
  ```
  DEBUG: received fullyIdle=False
  DEBUG: Agent is not fully idle. Skipping stop hook action or returning block.
  {"decision": "block", "reason": "Agent is not fully idle. Waiting for background tasks to complete."}
  ```
- **Gotcha:** None.

### Experiment 2: Simulating Stop Hook Payload when `fullyIdle` is `true`
- **Hypothesis:** When `fullyIdle` is `true`, the hook script should proceed to run the main hook action (prompting user/notifying completion).
- **Command/Code:** `echo '{"executionNum": 1, "terminationReason": "model_stop", "fullyIdle": true}' | ./spikes/stop-hook-fully-idle/experiment_stop_hook.py`
- **Result:** PASS
- **Observed output:**
  ```
  DEBUG: received fullyIdle=True
  DEBUG: Agent is fully idle. Proceeding with stop hook action...
  ```
- **Gotcha:** None.
