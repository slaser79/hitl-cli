#!/usr/bin/env python3
import json
import sys

def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # In Antigravity Stop hooks, fullyIdle indicates whether all background tasks are done.
    fully_idle = input_data.get("fullyIdle", False)

    print(f"DEBUG: received fullyIdle={fully_idle}", file=sys.stderr)

    if not fully_idle:
        print("DEBUG: Agent is not fully idle. Skipping stop hook action or returning block.", file=sys.stderr)
        # Option A: Exit early and let the agent terminate (do not run hook action)
        # sys.exit(0)
        
        # Option B: Block/continue so the agent stays alive until background tasks complete
        output = {
            "decision": "block",
            "reason": "Agent is not fully idle. Waiting for background tasks to complete."
        }
        print(json.dumps(output))
        sys.exit(0)

    print("DEBUG: Agent is fully idle. Proceeding with stop hook action...", file=sys.stderr)
    # Perform the actual hook action here (e.g. notify user)
    # ...
    sys.exit(0)

if __name__ == "__main__":
    main()
