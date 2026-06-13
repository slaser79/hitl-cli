#!/usr/bin/env python3
"""
Claude Code Stop Hook for Human-in-the-Loop review.

This hook intercepts Claude's stop events, extracts the last assistant message,
and sends it to a human for review via the HITL notification system.
"""
import json
import os
import subprocess
import sys
import time


def _extract_human_response(stdout: str) -> str:
    """
    Extract the human response from notify-completion stdout.

    The notify-completion command outputs multiple lines including headers.
    The actual response is in the line: "✅ Human response received: {response}"

    Args:
        stdout: The full stdout from the notify-completion command

    Returns:
        The extracted human response, or the stripped stdout if parsing fails
    """
    prefix = "✅ Human response received:"
    if prefix in stdout:
        # Extract everything after the first occurrence of the prefix
        # This handles multi-line responses correctly
        return stdout.split(prefix, 1)[1].strip()

    # Fallback: return stripped stdout if we can't parse it
    return stdout.strip()


def get_last_assistant_messages(
    transcript_path: str,
    num_messages: int = 3,
    retries: int = 3,
    delay: float = 0.5
) -> str:
    """
    Reads a JSONL transcript file and returns the last N assistant messages with text content.

    Iterates from the END of the file backwards to find the most recent assistant
    messages that contain actual text (not just thinking or tool_use blocks).

    Note: There's a known race condition where the Stop hook can fire before the
    transcript is fully written. We use a "stabilization" approach - reading multiple
    times to ensure the file has stopped changing.

    Args:
        transcript_path: Path to the JSONL transcript file
        num_messages: Number of recent assistant messages to return (default: 3)
        retries: Number of stabilization reads (default: 3)
        delay: Delay in seconds between reads (default: 0.5)

    Returns:
        The text content of the last N assistant messages, or an error message if not found.
    """
    # Initial delay to let the transcript file be fully written
    # This handles the race condition where the hook fires before the last message is flushed
    time.sleep(0.5)

    last_line_count = 0
    stable_count = 0
    final_messages = []

    # Keep reading until the file stabilizes (same line count for consecutive reads)
    for attempt in range(retries + 3):  # Extra attempts to allow for stabilization
        if attempt > 0:
            time.sleep(delay)

        try:
            with open(transcript_path) as f:
                lines = f.readlines()
        except FileNotFoundError:
            return "Error: Transcript file not found."
        except Exception as e:
            return f"Error reading transcript: {e}"

        current_line_count = len(lines)

        # Check if file has stabilized
        if current_line_count == last_line_count and current_line_count > 0:
            stable_count += 1
            if stable_count >= 2:
                # File is stable, process what we have
                break
        else:
            stable_count = 0
            last_line_count = current_line_count

        if not lines:
            continue  # Retry if empty

        # Collect the last N assistant messages with text
        messages = []

        # Iterate from the END of the file to find recent assistant messages with text
        for line in reversed(lines):
            if len(messages) >= num_messages:
                break

            try:
                entry = json.loads(line.strip())
            except json.JSONDecodeError:
                continue

            if not isinstance(entry, dict):
                continue

            # Get the message object (Claude schema)
            message = entry.get("message")

            # Check if this is an assistant message (handle both formats)
            is_assistant = (
                entry.get("type") == "assistant" or
                (message and isinstance(message, dict) and message.get("role") == "assistant") or
                (entry.get("source") == "MODEL" and entry.get("type") == "PLANNER_RESPONSE")
            )

            if not is_assistant:
                continue

            # Extract text content from the message
            content = []
            if message and isinstance(message, dict):
                content = message.get("content", [])
            elif "content" in entry:
                flat_content = entry.get("content")
                if isinstance(flat_content, str):
                    content = [flat_content]

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

            # If we found text, add to messages
            if text_parts:
                messages.append("".join(text_parts).strip())

        # Store the result for this read
        if messages:
            final_messages = messages

    # Return messages in chronological order (oldest first)
    if final_messages:
        final_messages.reverse()
        return "\n\n---\n\n".join(final_messages)

    return "No recent assistant messages found in transcript."


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

    # Detect if we are in Antigravity scope
    is_antigravity = ("--antigravity" in sys.argv) or (os.environ.get("IS_ANTIGRAVITY") == "1")

    # In Antigravity Stop hooks, 'fullyIdle' indicates whether background/async tasks are done
    if is_antigravity and not input_data.get("fullyIdle", False):
        output = {
            "decision": "block",
            "reason": "Agent is not fully idle. Waiting for background tasks to complete."
        }
        print(json.dumps(output))
        sys.exit(0)

    # NOTE: We intentionally do NOT check stop_hook_active here.
    # We want the hook to ALWAYS prompt the user until they say "YOU ARE DONE",
    # even if we're in a recursive stop hook situation.

    transcript_path = input_data.get("transcript_path") or input_data.get("transcriptPath")
    if not transcript_path:
        # Cannot proceed without the transcript; allow stop
        sys.exit(0)

    # Get the last few assistant messages for context
    last_messages = get_last_assistant_messages(transcript_path, num_messages=1)

    # Send the notification to human and wait for response
    try:
        result = subprocess.run(
            ["hitl-cli", "notify-completion", "--summary", last_messages],
            check=True,
            capture_output=True,
            text=True,
            timeout=900  # 15 minute timeout
        )
        # Extract just the human response from the stdout
        # The notify-completion command outputs: "✅ Human response received: {response}"
        # We need to parse this line to get just the response value
        user_response = _extract_human_response(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"HITL Stop Hook: notify-completion failed: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("HITL Stop Hook: Timed out waiting for human response", file=sys.stderr)
        sys.exit(1)

    # Interpret the user's response
    # Only allow stop if the response is exactly "YOU ARE DONE" (case-sensitive)
    # Any other response means continue with the user's instructions
    if user_response == "YOU ARE DONE":
        # User explicitly confirms done - allow Claude to stop
        sys.exit(0)
    else:
        # User provided instructions - block the stop and continue
        output = {
            "decision": "block",
            "reason": user_response
        }
        print(json.dumps(output))
        sys.exit(0)


if __name__ == "__main__":
    main()
