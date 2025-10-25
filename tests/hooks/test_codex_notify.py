#!/usr/bin/env python3
"""Tests for the Codex notify hook."""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def sample_codex_notification():
    """Sample Codex agent-turn-complete notification."""
    return {
        "type": "agent-turn-complete",
        "thread-id": "b5f6c1c2-1111-2222-3333-444455556666",
        "turn-id": "12345",
        "cwd": "/Users/alice/projects/example",
        "input-messages": ["Rename `foo` to `bar` and update the callsites."],
        "last-assistant-message": "Rename complete and verified `cargo build` succeeds."
    }


def test_codex_notify_parses_json_argument(sample_codex_notification):
    """Test that codex_notify correctly parses JSON from command line argument."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Import and run the hook
        from hitl_cli.hooks import codex_notify

        # Simulate command line execution
        json_arg = json.dumps(sample_codex_notification)
        with patch('sys.argv', ['codex_notify.py', json_arg]):
            exit_code = codex_notify.main()

        # Should exit successfully
        assert exit_code == 0

        # Should have called hitl-cli notify
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "hitl-cli"
        assert call_args[1] == "notify"
        assert "--message" in call_args


def test_codex_notify_formats_message_correctly(sample_codex_notification):
    """Test that the notification message is formatted correctly."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        from hitl_cli.hooks import codex_notify

        json_arg = json.dumps(sample_codex_notification)
        with patch('sys.argv', ['codex_notify.py', json_arg]):
            codex_notify.main()

        # Extract the message argument
        call_args = mock_run.call_args[0][0]
        message_index = call_args.index("--message") + 1
        message = call_args[message_index]

        # Verify message contains key information
        assert "Codex Turn Complete" in message
        assert "Rename complete and verified `cargo build` succeeds." in message
        assert "Rename `foo` to `bar`" in message
        assert "/Users/alice/projects/example" in message


def test_codex_notify_handles_invalid_json():
    """Test that invalid JSON is handled gracefully."""
    with patch('subprocess.run') as mock_run:
        from hitl_cli.hooks import codex_notify

        invalid_json = "not valid json"
        with patch('sys.argv', ['codex_notify.py', invalid_json]):
            exit_code = codex_notify.main()

        # Should exit with error code
        assert exit_code == 1

        # Should not call hitl-cli
        mock_run.assert_not_called()


def test_codex_notify_handles_missing_argument():
    """Test that missing argument is handled gracefully."""
    with patch('subprocess.run') as mock_run:
        from hitl_cli.hooks import codex_notify

        with patch('sys.argv', ['codex_notify.py']):  # No JSON argument
            exit_code = codex_notify.main()

        # Should exit with error code
        assert exit_code == 1

        # Should not call hitl-cli
        mock_run.assert_not_called()


def test_codex_notify_handles_subprocess_failure(sample_codex_notification):
    """Test that subprocess failures are handled gracefully."""
    with patch('subprocess.run') as mock_run:
        # Simulate subprocess failure
        mock_run.side_effect = subprocess.CalledProcessError(1, "hitl-cli")

        from hitl_cli.hooks import codex_notify

        json_arg = json.dumps(sample_codex_notification)
        with patch('sys.argv', ['codex_notify.py', json_arg]):
            exit_code = codex_notify.main()

        # Should exit with error code but not crash
        assert exit_code == 1
