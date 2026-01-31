#!/usr/bin/env python3
"""Tests for the review_and_continue stop hook."""
import json
from unittest.mock import MagicMock, patch

import pytest

from hitl_cli.hooks import review_and_continue


@pytest.fixture
def temp_transcript_simple(tmp_path):
    """Simple transcript with one assistant message."""
    transcript_file = tmp_path / "transcript.jsonl"
    turns = [
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Task completed successfully."}
                ]
            }
        }
    ]
    with open(transcript_file, "w") as f:
        for turn in turns:
            f.write(json.dumps(turn) + "\n")
    return str(transcript_file)


@pytest.fixture
def temp_transcript_with_progress(tmp_path):
    """Transcript with assistant message followed by progress events."""
    transcript_file = tmp_path / "transcript.jsonl"
    turns = [
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Committed and PR created."}
                ]
            }
        },
        {
            "type": "progress",
            "data": {"type": "hook_progress", "hookEvent": "Stop"}
        }
    ]
    with open(transcript_file, "w") as f:
        for turn in turns:
            f.write(json.dumps(turn) + "\n")
    return str(transcript_file)


@pytest.fixture
def temp_transcript_with_tool_calls(tmp_path):
    """Transcript where last assistant message is followed by tool calls."""
    transcript_file = tmp_path / "transcript.jsonl"
    turns = [
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "First message - should NOT be returned."}
                ]
            }
        },
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {}}
                ]
            }
        },
        {
            "type": "user",
            "message": {
                "role": "user",
                "content": [{"type": "tool_result", "content": "success"}]
            }
        },
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Final message - should be returned."}
                ]
            }
        },
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "thinking", "thinking": "..."}]
            }
        },
        {
            "type": "progress",
            "data": {"type": "hook_progress"}
        }
    ]
    with open(transcript_file, "w") as f:
        for turn in turns:
            f.write(json.dumps(turn) + "\n")
    return str(transcript_file)


@pytest.fixture
def temp_transcript_claude_code_format(tmp_path):
    """Transcript in Claude Code's actual format (message.role instead of type)."""
    transcript_file = tmp_path / "transcript.jsonl"
    turns = [
        {
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "All tests pass. Creating PR:"},
                    {"type": "tool_use", "name": "Bash", "input": {}}
                ]
            }
        },
        {
            "type": "user",
            "message": {
                "role": "user",
                "content": [{"type": "tool_result", "content": "success"}]
            }
        },
        {
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Done! PR created. Would you like me to merge this PR?"}
                ]
            }
        },
        {
            "type": "progress",
            "data": {"type": "hook_progress", "hookEvent": "Stop"}
        }
    ]
    with open(transcript_file, "w") as f:
        for turn in turns:
            f.write(json.dumps(turn) + "\n")
    return str(transcript_file)


def test_get_last_assistant_message_simple(temp_transcript_simple):
    """Test basic extraction of assistant message."""
    output = review_and_continue.get_last_assistant_message(temp_transcript_simple)
    assert "Task completed successfully" in output


def test_get_last_assistant_message_with_progress(temp_transcript_with_progress):
    """Test that we skip progress events and find the assistant message."""
    output = review_and_continue.get_last_assistant_message(temp_transcript_with_progress)
    assert "Committed and PR created" in output
    assert "progress" not in output


def test_get_last_assistant_message_with_tool_calls(temp_transcript_with_tool_calls):
    """Test that we find the LAST assistant message, not earlier ones."""
    output = review_and_continue.get_last_assistant_message(temp_transcript_with_tool_calls)
    # Should find the FINAL message
    assert "Final message - should be returned" in output
    # Should NOT return the first message
    assert "First message" not in output


def test_get_last_assistant_message_claude_code_format(temp_transcript_claude_code_format):
    """Test that we handle Claude Code's transcript format (message.role)."""
    output = review_and_continue.get_last_assistant_message(temp_transcript_claude_code_format)
    # Should find the LAST assistant message, not the first one
    assert "Would you like me to merge this PR?" in output
    # Should NOT contain the earlier message
    assert "All tests pass" not in output


def test_get_last_assistant_message_file_not_found():
    """Test handling of missing transcript file."""
    output = review_and_continue.get_last_assistant_message("/nonexistent/path.jsonl")
    assert "Error" in output or "not found" in output.lower()


def test_main_hook_allows_stop_on_satisfied_response(temp_transcript_simple):
    """Test that satisfied phrases allow Claude to stop."""
    input_data = {"transcript_path": temp_transcript_simple}

    with patch("hitl_cli.hooks.review_and_continue.json.load", return_value=input_data):
        with patch("hitl_cli.hooks.review_and_continue.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="All good, thanks!", returncode=0)

            with patch("hitl_cli.hooks.review_and_continue.sys.exit") as mock_exit:
                mock_exit.side_effect = SystemExit(0)
                try:
                    review_and_continue.main()
                except SystemExit:
                    pass

                # Should exit with 0 (allow stop)
                mock_exit.assert_called_with(0)


def test_main_hook_blocks_on_new_instructions(temp_transcript_simple):
    """Test that new instructions block the stop."""
    input_data = {"transcript_path": temp_transcript_simple}

    with patch("hitl_cli.hooks.review_and_continue.json.load", return_value=input_data):
        with patch("hitl_cli.hooks.review_and_continue.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="Please also update the README", returncode=0)

            with patch("hitl_cli.hooks.review_and_continue.sys.exit") as mock_exit:
                mock_exit.side_effect = SystemExit(0)
                with patch("builtins.print") as mock_print:
                    try:
                        review_and_continue.main()
                    except SystemExit:
                        pass

                    # Should print a block decision
                    mock_print.assert_called()
                    call_args = mock_print.call_args[0][0]
                    output = json.loads(call_args)
                    assert output["decision"] == "block"
                    assert "README" in output["reason"]


def test_main_hook_respects_stop_hook_active():
    """Test that we don't block when stop_hook_active is true (prevents loops)."""
    input_data = {
        "transcript_path": "/some/path.jsonl",
        "stop_hook_active": True
    }

    with patch("hitl_cli.hooks.review_and_continue.json.load", return_value=input_data):
        with patch("hitl_cli.hooks.review_and_continue.sys.exit") as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            try:
                review_and_continue.main()
            except SystemExit:
                pass

            # Should exit immediately with 0 (allow stop)
            mock_exit.assert_called_once_with(0)


def test_main_hook_blocks_when_response_contains_but_isnt_satisfied_phrase(temp_transcript_simple):
    """Test that 'done but please continue' blocks, not stops (strict matching)."""
    input_data = {"transcript_path": temp_transcript_simple}

    with patch("hitl_cli.hooks.review_and_continue.json.load", return_value=input_data):
        with patch("hitl_cli.hooks.review_and_continue.subprocess.run") as mock_run:
            # Response CONTAINS "done" but has more instructions
            mock_run.return_value = MagicMock(stdout="Done, but please also add tests", returncode=0)

            with patch("hitl_cli.hooks.review_and_continue.sys.exit") as mock_exit:
                mock_exit.side_effect = SystemExit(0)
                with patch("builtins.print") as mock_print:
                    try:
                        review_and_continue.main()
                    except SystemExit:
                        pass

                    # Should print a block decision, NOT allow stop
                    mock_print.assert_called()
                    call_args = mock_print.call_args[0][0]
                    output = json.loads(call_args)
                    assert output["decision"] == "block"
                    assert "add tests" in output["reason"]
