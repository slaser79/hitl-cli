#!/usr/bin/env python3
import json
import subprocess
import sys

def get_last_turns(transcript_path: str, num_turns: int = 2) -> str:
    """
    Reads a JSONL transcript file and returns a formatted string of the
    last few JSON objects for human review.
    """
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()
        
        # Get the last N lines, ensuring we don't go out of bounds
        last_lines = lines[-num_turns:]
        
        formatted_turns = []
        for i, line in enumerate(last_lines):
            try:
                # Parse and then pretty-print the JSON for readability
                turn_data = json.loads(line)
                pretty_json = json.dumps(turn_data, indent=2)
                formatted_turns.append(f"--- Turn {-len(last_lines) + i} ---\n{pretty_json}")
            except json.JSONDecodeError:
                # If a line isn't valid JSON, just include it as is.
                formatted_turns.append(f"--- Turn {-len(last_lines) + i} (raw) ---\n{line}")
                
        if not formatted_turns:
            return "No recent activity found in transcript."
            
        return "\n\n".join(formatted_turns)
        
    except FileNotFoundError:
        return "Error: Transcript file not found."
    except Exception as e:
        return f"An error occurred while reading the transcript: {e}"

def main():
    """
    Main hook logic to intercept a Stop event, request human input with context,
    and either allow the stop or continue with new instructions.
    """
    try:
        input_data = json.load(sys.stdin)
        
        
        transcript_path = input_data.get("transcript_path")
        if not transcript_path:
            # Cannot proceed without the transcript; allow stop.
            sys.exit(0)
            
        # 1. Get the context for the user
        review_payload = get_last_turns(transcript_path, num_turns=2)
        
        prompt_for_human = (
            "Claude has completed its task. Please review the final actions below.\n\n"
            f"```json{review_payload}```"
        )
        
        # 2. Send the blocking request to the user
        completed_process = subprocess.run(
            [
                "hitl-cli", "notify-completion",
                "--summary", prompt_for_human,
            ],
            check=True,
            capture_output=True,
            text=True
        )
        
        user_response = completed_process.stdout.strip()
        
        # 3. Interpret the user's response
        if user_response == "Approve":
            # User is satisfied. Allow Claude to stop by exiting cleanly.
            sys.exit(0)
        else:
            # User provided new instructions. Block the stop and feed them back to Claude.
            # This is the core of the remote control loop.
            output_for_claude = {
                "decision": "block",
                "reason": user_response
            }
            print(json.dumps(output_for_claude))
            sys.exit(0)

    except (json.JSONDecodeError, subprocess.CalledProcessError) as e:
        # If the hook fails for any reason, we don't want to hang the session.
        # Log the error and allow Claude to stop by default.
        print(f"HITL Stop Hook Error: {e}", file=sys.stderr)
        # We exit with 1 to indicate an error, but don't output a "block" command.
        sys.exit(1)

if __name__ == "__main__":
    main()
