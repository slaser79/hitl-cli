#!/usr/bin/env python3
import json
import subprocess
import sys


def get_last_turns(transcript_path: str, num_turns: int = 1, max_search_lines: int = 200) -> str:
    """
    Reads a JSONL transcript file and returns the last assistant message text.

    Args:
        transcript_path: Path to the JSONL transcript file
        num_turns: Number of assistant messages to return (default: 1)
        max_search_lines: Maximum number of lines to search backwards for assistant messages
    """
    try:
        with open(transcript_path) as f:
            lines = f.readlines()

        if not lines:
            return "No recent activity found in transcript."

        # Search through the last max_search_lines to find assistant messages with text
        search_lines = lines[-max_search_lines:] if len(lines) > max_search_lines else lines

        # Iterate in reverse to find the most recent assistant message with text content
        for line in reversed(search_lines):
            try:
                turn_data = json.loads(line)
                if not isinstance(turn_data, dict):
                    continue

                # Check for assistant message - handle both formats:
                # 1. type: "assistant" at top level (test format)
                # 2. message.role: "assistant" (Claude Code transcript format)
                message = turn_data.get("message", {})
                if not isinstance(message, dict):
                    continue

                is_assistant = (
                    turn_data.get("type") == "assistant" or
                    message.get("role") == "assistant"
                )

                if not is_assistant:
                    continue

                content = message.get("content", [])

                # Extract text content (skip thinking, tool_use, etc.)
                assistant_text = ""
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text = safe_get_str(item, "text", "")
                            if text:
                                assistant_text += text
                        elif isinstance(item, str):
                            assistant_text += item

                if assistant_text.strip():
                    return assistant_text.strip()
            except json.JSONDecodeError:
                continue

        return "No recent activity found in transcript."

    except FileNotFoundError:
        return "Error: Transcript file not found."
    except Exception as e:
        return f"An error occurred while reading the transcript: {e}"


def safe_get_str(d, key, default=""):
    """Safely get a string value from dict, handling None values."""
    val = d.get(key, default)
    return val if val is not None else default

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

        # 1. Get the last assistant message as context for the user
        review_payload = get_last_turns(transcript_path)

        prompt_for_human = review_payload

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
        # Assume everything is good if user response contains "all good" or "looks good"
        # or "Great job" and similar phrases (case insensitive)
        # Bit of hack as responses are now in json
        satisfied_phrases = [
            "all good", "looks good", "great job", "thats it for now",
            "thats good", "thats great", "wee are done", "ok great"
        ]
        if any(phrase in user_response.lower() for phrase in satisfied_phrases):
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
