#!/usr/bin/env python3
"""
Claude Code Stop Hook for Human-in-the-Loop review.

This hook intercepts Claude's stop events, extracts the last assistant message,
and sends it to a human for review via the HITL notification system.
"""
import json
import subprocess
import sys
import time


def get_last_assistant_message(transcript_path: str, retries: int = 3, delay: float = 0.2) -> str:
    """
    Reads a JSONL transcript file and returns the last assistant message with text content.

    Iterates from the END of the file backwards to find the most recent assistant
    message that contains actual text (not just thinking or tool_use blocks).

    Note: There's a known race condition where the Stop hook can fire before the
    transcript is fully written. We retry with a small delay to handle this.

    Args:
        transcript_path: Path to the JSONL transcript file
        retries: Number of retry attempts if no message found (default: 3)
        delay: Delay in seconds between retries (default: 0.2)

    Returns:
        The text content of the last assistant message, or an error message if not found.
    """
    for attempt in range(retries):
        if attempt > 0:
            # Wait before retry to allow file to be fully written
            time.sleep(delay)

        try:
            with open(transcript_path) as f:
                lines = f.readlines()
        except FileNotFoundError:
            return "Error: Transcript file not found."
        except Exception as e:
            return f"Error reading transcript: {e}"

        if not lines:
            continue  # Retry if empty

        # Iterate from the END of the file to find the most recent assistant message with text
        for line in reversed(lines):
            try:
                entry = json.loads(line.strip())
            except json.JSONDecodeError:
                continue

            if not isinstance(entry, dict):
                continue

            # Get the message object
            message = entry.get("message", {})
            if not isinstance(message, dict):
                continue

            # Check if this is an assistant message (handle both formats)
            is_assistant = (
                entry.get("type") == "assistant" or
                message.get("role") == "assistant"
            )

            if not is_assistant:
                continue

            # Extract text content from the message
            content = message.get("content", [])
            if not isinstance(content, list):
                continue

            # Collect all text blocks (skip thinking, tool_use, etc.)
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text")
                    if text and isinstance(text, str) and text.strip():
                        text_parts.append(text)
                elif isinstance(item, str) and item.strip():
                    text_parts.append(item)

            # If we found text, return it
            if text_parts:
                return "".join(text_parts).strip()

    return "No recent assistant message found in transcript."


def main():
    """
    Main hook logic to intercept a Stop event, request human input with context,
    and either allow the stop or continue with new instructions.
    """
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"HITL Stop Hook: Failed to parse input: {e}", file=sys.stderr)
        sys.exit(1)

    # Check if we're already in a stop hook loop - prevent infinite loops
    if input_data.get("stop_hook_active", False):
        # Already continuing from a previous stop hook, don't block again
        sys.exit(0)

    transcript_path = input_data.get("transcript_path")
    if not transcript_path:
        # Cannot proceed without the transcript; allow stop
        sys.exit(0)

    # Get the last assistant message
    last_message = get_last_assistant_message(transcript_path)

    # Send the notification to human and wait for response
    try:
        result = subprocess.run(
            ["hitl-cli", "notify-completion", "--summary", last_message],
            check=True,
            capture_output=True,
            text=True,
            timeout=900  # 15 minute timeout
        )
        user_response = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"HITL Stop Hook: notify-completion failed: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("HITL Stop Hook: Timed out waiting for human response", file=sys.stderr)
        sys.exit(1)

    # Interpret the user's response
    satisfied_phrases = [
        "all good", "looks good", "great job", "thats it for now",
        "thats good", "thats great", "we are done", "ok great",
        "done", "thanks", "thank you", "perfect", "awesome"
    ]

    response_lower = user_response.lower()
    if any(phrase in response_lower for phrase in satisfied_phrases):
        # User is satisfied - allow Claude to stop
        sys.exit(0)
    else:
        # User provided new instructions - block the stop and continue
        output = {
            "decision": "block",
            "reason": user_response
        }
        print(json.dumps(output))
        sys.exit(0)


if __name__ == "__main__":
    main()
