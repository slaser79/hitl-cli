---
topic: stop-hook-fully-idle
status: SUCCESS
last_updated: 2026-06-13
source_branch: research/stop-hook-fully-idle
---

# Golden Path: Stop Hook Fully Idle Condition

## What This Is For
A Builder should consult this document when modifying or designing an Antigravity `Stop` hook that should only execute its main action (e.g., prompting the human, running post-session commands, publishing notifications) when the agent is completely done and all background tasks have completed (`fullyIdle: true`).

## Working Recipe

To make the stop hook run only when `fullyIdle` is `true`, update the Python hook entrypoint script to parse `sys.stdin` and check the `fullyIdle` attribute.

### Python implementation (`review_and_continue.py` pattern)

```python
import json
import sys

def main():
    try:
        # Read the lifecycle hook input payload from standard input
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Hook Error: Failed to parse input: {e}", file=sys.stderr)
        sys.exit(1)

    # In Antigravity Stop hooks, 'fullyIdle' indicates whether background/async tasks are done
    fully_idle = input_data.get("fullyIdle", False)

    if not fully_idle:
        # Option A: Prevent the stop and continue execution loop until background tasks finish
        output = {
            "decision": "block",
            "reason": "Agent is not fully idle. Waiting for background tasks to complete."
        }
        print(json.dumps(output))
        sys.exit(0)

    # --- Actual Hook Action (Executed only when fullyIdle is true) ---
    # e.g., prompt for human review, send notifications, run linters/tests, save state
    print("Agent is fully idle. Running final hook actions...", file=sys.stderr)
    
    # Allow the stop to proceed as normal (by exiting 0 with no stdout block decision)
    sys.exit(0)
```

## Configuration & Prerequisites

No changes to the hook configuration (`hooks.json`) are required. The standard configuration works:

```json
{
  "hitl-cli-stop-hook": {
    "enabled": true,
    "Stop": [
      {
        "type": "command",
        "command": "/Users/slaser79/lab/hitl/hitl-cli/review_and_continue_wrapper.sh",
        "timeout": 900
      }
    ]
  }
}
```

## Gotchas

- **`fullyIdle` case sensitivity:** The field name passed in the JSON payload is `"fullyIdle"` (camelCase). Do not use `"fully_idle"` (snake_case) or `"FullyIdle"`.
- **Exit codes:** The hook should always exit with code `0`. If it fails (exits non-zero), the agent might report a hook execution error.
- **Output buffering:** Standard print outputs that are meant for JSON decisions should go to stdout, while debugging and status logs should be directed to `sys.stderr` to avoid corrupting the JSON response expected by the Antigravity agent runner.

## What Does NOT Work

- **Ignoring standard input:** If the script ignores standard input, it cannot read the state of the agent, and the hook will run prematurely (on first stop trigger) even if background tasks are still executing.
- **Using `"decision": "continue"` instead of `"block"` in this workspace:** The CLI code and its test suite specifically inspect `"decision": "block"`. Make sure to align the returned decision key with what the caller expects (here, `"decision": "block"`).

## Open Questions

- Does the Antigravity agent runtime support a configuration option directly inside `hooks.json` to filter hook triggers (e.g. `when: "fullyIdle"`) without modifying the script? (No evidence of this was found in the public docs, meaning checking within the script itself is the recommended approach).

## References

- [Antigravity Lifecycle Hook Documentation](https://antigravity.google)
- Existing hook code: [review_and_continue.py](file:///nix/slaser79_offload/lab/hitl/hitl-cli/hitl_cli/hooks/review_and_continue.py)
- Hook tests: [test_review_and_continue.py](file:///nix/slaser79_offload/lab/hitl/hitl-cli/tests/hooks/test_review_and_continue.py)
