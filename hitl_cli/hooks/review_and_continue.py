#!/usr/bin/env python3
import json
import subprocess
import sys

def get_last_turns(transcript_path: str, num_turns: int = 2) -> str:
    """
    Reads a JSONL transcript file and returns a human-readable formatted string of the
    last few turns for review.
    """
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()

        # Get the last N lines, ensuring we don't go out of bounds
        last_lines = lines[-num_turns:]

        formatted_turns = []
        for i, line in enumerate(last_lines):
            try:
                turn_data = json.loads(line)
                if not isinstance(turn_data, dict):
                    formatted_turns.append(f"--- Turn {-len(last_lines) + i} (invalid data) ---\n{line.strip()}")
                    continue
                turn_number = -len(last_lines) + i
                formatted_turn = format_turn_for_human(turn_data, turn_number)
                formatted_turns.append(formatted_turn)
            except json.JSONDecodeError:
                # If a line isn't valid JSON, just include it as is.
                formatted_turns.append(f"--- Turn {-len(last_lines) + i} (raw) ---\n{line.strip()}")

        if not formatted_turns:
            return "No recent activity found in transcript."

        return "\n\n".join(formatted_turns)

    except FileNotFoundError:
        return "Error: Transcript file not found."
    except Exception as e:
        return f"An error occurred while reading the transcript: {e}"


def safe_get_str(d, key, default=""):
    """Safely get a string value from dict, handling None values."""
    val = d.get(key, default)
    return val if val is not None else default

def format_turn_for_human(turn_data: dict, turn_number: int) -> str:
    """
    Formats a single turn into a human-readable summary.
    """
    turn_type = turn_data.get("type", "unknown")
    timestamp = turn_data.get("timestamp", "N/A")

    # Format timestamp for readability
    if timestamp is not None and timestamp != "N/A":
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            pass  # Keep original timestamp if parsing fails

    if turn_type == "user":
        # Handle user messages
        message = turn_data.get("message", {})
        if not isinstance(message, dict):
            return f"--- Turn {turn_number} (User - Invalid Message Format) ---\n" \
                   f"⏰ Time: {timestamp}\n" \
                   f"💬 Message: Invalid format (expected dict, got {type(message)})"

        content = message.get("content", [])

        # Check if it's a tool result
        if content and isinstance(content, list) and len(content) > 0:
            first_content = content[0]
            if isinstance(first_content, dict) and first_content.get("type") == "tool_result":
                tool_result = safe_get_str(first_content, "content", "")
                safe_get_str(first_content, "tool_use_id", "")

                # Extract todo information if available
                tool_use_result = turn_data.get("toolUseResult", {})
                if isinstance(tool_use_result, dict):
                    tool_use_result.get("oldTodos", [])
                    new_todos = tool_use_result.get("newTodos", [])

                    todo_summary = []
                    for todo in new_todos:
                        if isinstance(todo, dict):
                            status = safe_get_str(todo, "status", "unknown")
                            content_text = safe_get_str(todo, "content", "")
                            todo_summary.append(f"  • {content_text} [{status}]")

                    return f"--- Turn {turn_number} (User - Tool Result) ---\n" \
                           f"⏰ Time: {timestamp}\n" \
                           f"🔧 Tool Result: {tool_result}\n" \
                           f"📋 Todo Progress:\n" + "\n".join(todo_summary)
                else:
                    return f"--- Turn {turn_number} (User - Tool Result) ---\n" \
                           f"⏰ Time: {timestamp}\n" \
                           f"🔧 Tool Result: {tool_result[:200]}..."
            else:
                # Regular user message
                user_text = ""
                if isinstance(content, list):
                    user_text_parts = []
                    for c in content:
                        if isinstance(c, dict):
                            text = safe_get_str(c, "text", "")
                            user_text_parts.append(text)
                        elif isinstance(c, str):
                            user_text_parts.append(c)
                        else:
                            user_text_parts.append(str(c) if c is not None else "")
                    user_text = " ".join(user_text_parts)
                elif isinstance(content, str):
                    user_text = content
                else:
                    user_text = str(content) if content is not None else ""

                return f"--- Turn {turn_number} (User) ---\n" \
                       f"⏰ Time: {timestamp}\n" \
                       f"💬 Message: {user_text[:20000]}..."

    elif turn_type == "assistant":
        # Handle assistant messages
        message = turn_data.get("message", {})
        if not isinstance(message, dict):
            return f"--- Turn {turn_number} (Assistant - Invalid Message Format) ---\n" \
                   f"⏰ Time: {timestamp}\n" \
                   f"📝 Message: Invalid format (expected dict, got {type(message)})"

        content = message.get("content", [])
        model = safe_get_str(message, "model", "unknown")

        # Extract text content
        assistant_text = ""
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = safe_get_str(item, "text", "")
                    assistant_text += text
                elif isinstance(item, str):
                    assistant_text += item

        # Truncate long responses
        if len(assistant_text) > 2000:
            assistant_text = assistant_text[:2000] + "..."

        # Get usage info if available
        usage = message.get("usage", {})
        if isinstance(usage, dict):
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
        else:
            input_tokens = 0
            output_tokens = 0

        return f"--- Turn {turn_number} (Assistant) ---\n" \
               f"⏰ Time: {timestamp}\n" \
               f"🤖 Model: {model}\n" \
               f"📝 Response: {assistant_text}\n" \
               f"📊 Tokens: {input_tokens} in / {output_tokens} out"

    else:
        # Fallback for unknown turn types
        return f"--- Turn {turn_number} ({turn_type}) ---\n" \
               f"⏰ Time: {timestamp}\n" \
               f"📄 Raw data: {str(turn_data)[:2000]}..."

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
            f"{review_payload}"
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
        # assume everything is good if user reponse cotains "all good" or "looks good" or "Great job" and similar phrases (case insensitive)
        # Bit of hack as responses are now in json
        if any(phrase in user_response.lower() for phrase in ["all good", "looks good", "great job", "thats it for now", "thats good", "thats great", "wee are done", "ok great"]):
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
