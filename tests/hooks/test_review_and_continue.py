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


def test_get_last_assistant_messages_simple(temp_transcript_simple):
    """Test basic extraction of assistant message."""
    output = review_and_continue.get_last_assistant_messages(temp_transcript_simple)
    assert "Task completed successfully" in output


def test_get_last_assistant_messages_with_progress(temp_transcript_with_progress):
    """Test that we skip progress events and find the assistant message."""
    output = review_and_continue.get_last_assistant_messages(temp_transcript_with_progress)
    assert "Committed and PR created" in output
    assert "progress" not in output


def test_get_last_assistant_messages_with_tool_calls(temp_transcript_with_tool_calls):
    """Test that we find multiple assistant messages including the last one."""
    output = review_and_continue.get_last_assistant_messages(temp_transcript_with_tool_calls)
    # Should find the FINAL message
    assert "Final message - should be returned" in output
    # With num_messages=3, we now include earlier messages too for context
    assert "First message" in output


def test_get_last_assistant_messages_claude_code_format(temp_transcript_claude_code_format):
    """Test that we handle Claude Code's transcript format (message.role)."""
    output = review_and_continue.get_last_assistant_messages(temp_transcript_claude_code_format)
    # Should find the LAST assistant message
    assert "Would you like me to merge this PR?" in output
    # With num_messages=3, we now include earlier messages too for context
    assert "All tests pass" in output


def test_get_last_assistant_messages_file_not_found():
    """Test handling of missing transcript file."""
    output = review_and_continue.get_last_assistant_messages("/nonexistent/path.jsonl")
    assert "Error" in output or "not found" in output.lower()


def test_main_hook_allows_stop_on_explicit_done(temp_transcript_simple):
    """Test that 'YOU ARE DONE' allows Claude to stop."""
    input_data = {"transcript_path": temp_transcript_simple}

    with patch("hitl_cli.hooks.review_and_continue.json.load", return_value=input_data):
        with patch("hitl_cli.hooks.review_and_continue.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="📋 Task Completion Notification\n✅ Human response received: YOU ARE DONE", returncode=0)

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
            mock_run.return_value = MagicMock(stdout="📋 Task Completion Notification\n✅ Human response received: Please also update the README", returncode=0)

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


def test_main_hook_always_prompts_even_when_stop_hook_active(temp_transcript_simple):
    """Test that we ALWAYS prompt user, even when stop_hook_active is true (recursive)."""
    input_data = {
        "transcript_path": temp_transcript_simple,
        "stop_hook_active": True  # Even when active, we should still prompt
    }

    with patch("hitl_cli.hooks.review_and_continue.json.load", return_value=input_data):
        with patch("hitl_cli.hooks.review_and_continue.subprocess.run") as mock_run:
            # User says to continue
            mock_run.return_value = MagicMock(stdout="📋 Task Completion Notification\n✅ Human response received: keep going", returncode=0)

            with patch("hitl_cli.hooks.review_and_continue.sys.exit") as mock_exit:
                mock_exit.side_effect = SystemExit(0)
                with patch("builtins.print") as mock_print:
                    try:
                        review_and_continue.main()
                    except SystemExit:
                        pass

                    # Should still prompt and block (not exit early)
                    mock_run.assert_called_once()  # notify-completion was called
                    mock_print.assert_called()  # block decision was printed


def test_extract_human_response_multi_line():
    """Test that multi-line responses are correctly extracted."""
    stdout = "📋 Task Completion Notification\n========================================\nSummary: Test\n\n✅ Human response received: YOU ARE DONE\nPlease also update the README"
    response = review_and_continue._extract_human_response(stdout)
    assert response == "YOU ARE DONE\nPlease also update the README"


def test_main_hook_blocks_on_multi_line_with_instructions(temp_transcript_simple):
    """Test that multi-line response containing 'YOU ARE DONE' but with extra instructions blocks."""
    input_data = {"transcript_path": temp_transcript_simple}

    with patch("hitl_cli.hooks.review_and_continue.json.load", return_value=input_data):
        with patch("hitl_cli.hooks.review_and_continue.subprocess.run") as mock_run:
            # Multi-line response: first line says DONE, but second line has instructions
            stdout = "✅ Human response received: YOU ARE DONE\nBut wait, please also update the README"
            mock_run.return_value = MagicMock(stdout=stdout, returncode=0)

            with patch("hitl_cli.hooks.review_and_continue.sys.exit") as mock_exit:
                mock_exit.side_effect = SystemExit(0)
                with patch("builtins.print") as mock_print:
                    try:
                        review_and_continue.main()
                    except SystemExit:
                        pass

                    # Should print a block decision because it's NOT EXACTLY "YOU ARE DONE"
                    mock_print.assert_called()
                    call_args = mock_print.call_args[0][0]
                    output = json.loads(call_args)
                    assert output["decision"] == "block"
                    assert "README" in output["reason"]
                    assert "YOU ARE DONE" in output["reason"]


def test_main_hook_blocks_when_not_fully_idle_under_antigravity(temp_transcript_simple):
    """Test that under Antigravity, if the agent is not fully idle, the stop is blocked."""
    input_data = {
        "transcript_path": temp_transcript_simple,
        "fullyIdle": False
    }

    with patch("hitl_cli.hooks.review_and_continue.json.load", return_value=input_data):
        with patch("hitl_cli.hooks.review_and_continue.sys.argv", ["review_and_continue.py", "--antigravity"]):
            with patch("hitl_cli.hooks.review_and_continue.subprocess.run") as mock_run:
                with patch("hitl_cli.hooks.review_and_continue.sys.exit") as mock_exit:
                    mock_exit.side_effect = SystemExit(0)
                    with patch("builtins.print") as mock_print:
                        try:
                            review_and_continue.main()
                        except SystemExit:
                            pass

                        # Should not call notify-completion (subprocess.run)
                        mock_run.assert_not_called()

                        # Should print a block decision
                        mock_print.assert_called()
                        call_args = mock_print.call_args[0][0]
                        output = json.loads(call_args)
                        assert output["decision"] == "block"
                        assert "not fully idle" in output["reason"]
                        mock_exit.assert_called_with(0)


def test_main_hook_prompts_when_not_fully_idle_without_antigravity(temp_transcript_simple):
    """Test that without Antigravity scope, fullyIdle=False is ignored and human prompt occurs."""
    input_data = {
        "transcript_path": temp_transcript_simple,
        "fullyIdle": False
    }

    with patch("hitl_cli.hooks.review_and_continue.json.load", return_value=input_data):
        with patch("hitl_cli.hooks.review_and_continue.sys.argv", ["review_and_continue.py"]):
            with patch.dict("os.environ", {}):
                with patch("hitl_cli.hooks.review_and_continue.subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(stdout="✅ Human response received: YOU ARE DONE", returncode=0)
                    with patch("hitl_cli.hooks.review_and_continue.sys.exit") as mock_exit:
                        mock_exit.side_effect = SystemExit(0)
                        try:
                            review_and_continue.main()
                        except SystemExit:
                            pass

                        # Should call notify-completion (subprocess.run)
                        mock_run.assert_called_once()
                        mock_exit.assert_called_with(0)


def test_main_hook_prompts_when_fully_idle_under_antigravity(temp_transcript_simple):
    """Test that under Antigravity, if the agent is fully idle, human prompt occurs."""
    input_data = {
        "transcript_path": temp_transcript_simple,
        "fullyIdle": True
    }

    with patch("hitl_cli.hooks.review_and_continue.json.load", return_value=input_data):
        with patch("hitl_cli.hooks.review_and_continue.sys.argv", ["review_and_continue.py", "--antigravity"]):
            with patch("hitl_cli.hooks.review_and_continue.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="✅ Human response received: YOU ARE DONE", returncode=0)
                with patch("hitl_cli.hooks.review_and_continue.sys.exit") as mock_exit:
                    mock_exit.side_effect = SystemExit(0)
                    try:
                        review_and_continue.main()
                    except SystemExit:
                        pass

                    # Should call notify-completion (subprocess.run)
                    mock_run.assert_called_once()
                    mock_exit.assert_called_with(0)
