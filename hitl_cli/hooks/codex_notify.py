#!/usr/bin/env python3
"""
Codex CLI notify hook for Human-in-the-Loop notifications.

This hook receives agent-turn-complete notifications from Codex CLI
and sends them to the user via the HITL mobile app.

Configuration in ~/.codex/config.toml:
    notify = ["hitl-codex-notify"]

or with full path:
    notify = ["python3", "/path/to/codex_notify.py"]
"""

import json
import subprocess
import sys


def format_notification_message(notification: dict) -> str:
    """
    Format a Codex notification into a human-readable message.

    Args:
        notification: Codex notification dictionary with fields:
            - type: notification type (e.g., "agent-turn-complete")
            - thread-id: unique identifier for the Codex session
            - turn-id: identifier for this specific turn
            - cwd: working directory where Codex is running
            - input-messages: list of user input messages
            - last-assistant-message: Codex's final response

    Returns:
        Formatted notification message string
    """
    notification_type = notification.get("type", "unknown")

    if notification_type == "agent-turn-complete":
        # Extract key fields
        last_message = notification.get("last-assistant-message", "")
        input_messages = notification.get("input-messages", [])
        cwd = notification.get("cwd", "")
        thread_id = notification.get("thread-id", "")

        # Format user input
        user_input = " ".join(input_messages) if input_messages else "No input"

        # Build message
        message_parts = [
            "🤖 Codex Turn Complete",
            "",
            f"📝 Task: {user_input}",
            "",
            f"✅ Result: {last_message}",
            "",
            f"📁 Directory: {cwd}",
            f"🔗 Session: {thread_id[:8]}...",
        ]

        return "\n".join(message_parts)
    else:
        # Fallback for unknown notification types
        return f"Codex notification ({notification_type}): {json.dumps(notification)}"


def main() -> int:
    """
    Main entry point for the Codex notify hook.

    Expects a single command-line argument containing JSON notification data.

    Returns:
        0 on success, 1 on error
    """
    try:
        # Validate arguments
        if len(sys.argv) != 2:
            print("Usage: codex_notify.py <NOTIFICATION_JSON>", file=sys.stderr)
            return 1

        # Parse JSON argument
        try:
            notification = json.loads(sys.argv[1])
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            return 1

        # Format notification message
        message = format_notification_message(notification)

        # Send notification via HITL CLI
        subprocess.run(
            ["hitl-cli", "notify", "--message", message],
            check=True,
            capture_output=True,
            text=True
        )

        return 0

    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to send HITL notification: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: Unexpected error in codex notify hook: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
