#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch
import pytest
from hitl_cli.hooks import review_and_continue

@pytest.fixture
def temp_transcript(tmp_path):
    transcript_file = tmp_path / "transcript.jsonl"
    turns = [
        {
            "type": "assistant",
            "timestamp": "2026-01-27T18:29:51.754Z",
            "message": {
                "model": "claude-opus-4-5-20251101",
                "content": [
                    {
                        "type": "text",
                        "text": "Committed and PR created.Commit: bdfc023 on branch feature/maestro-screenshot-automation"
                    }
                ],
                "usage": {
                    "input_tokens": 7,
                    "output_tokens": 1
                }
            }
        },
        {
            "type": "progress",
            "timestamp": "2026-01-27T18:29:51.754Z",
            "data": {
                "type": "hook_progress",
                "hookEvent": "Stop",
                "hookName": "Stop",
                "uuid": "1c70c44a-a92f-470c-8066-b03706169ccf"
            }
        }
    ]
    with open(transcript_file, "w") as f:
        for turn in turns:
            f.write(json.dumps(turn) + "\n")
    return str(transcript_file)

def test_get_last_turns_only_assistant(temp_transcript):
    output = review_and_continue.get_last_turns(temp_transcript)
    # Should ONLY contain the assistant message text
    assert "Committed and PR created" in output
    # Should NOT contain metadata or other turn types
    assert "--- Turn" not in output
    assert "Model:" not in output
    assert "progress" not in output

@pytest.fixture
def temp_transcript_with_tool_results(tmp_path):
    """Transcript where assistant message is not in the last 2 lines"""
    transcript_file = tmp_path / "transcript.jsonl"
    turns = [
        {
            "type": "assistant",
            "timestamp": "2026-01-27T18:29:50.000Z",
            "message": {
                "model": "claude-opus-4-5-20251101",
                "content": [
                    {
                        "type": "text",
                        "text": "Here are the recommended next steps for your project."
                    }
                ]
            }
        },
        {
            "type": "tool_result",
            "timestamp": "2026-01-27T18:29:51.000Z",
            "data": {"tool": "some_tool", "result": "success"}
        },
        {
            "type": "progress",
            "timestamp": "2026-01-27T18:29:52.000Z",
            "data": {"type": "hook_progress", "hookEvent": "Stop"}
        },
        {
            "type": "user",
            "timestamp": "2026-01-27T18:29:53.000Z",
            "message": {"content": "Thanks"}
        }
    ]
    with open(transcript_file, "w") as f:
        for turn in turns:
            f.write(json.dumps(turn) + "\n")
    return str(transcript_file)


def test_get_last_turns_searches_beyond_last_two_lines(temp_transcript_with_tool_results):
    """Test that we find assistant message even if it's not in the last 2 lines"""
    output = review_and_continue.get_last_turns(temp_transcript_with_tool_results)
    # Should find the assistant message even though it's not in the last 2 lines
    assert "recommended next steps" in output
    # Should NOT return the "no activity" message
    assert "No recent activity" not in output


@pytest.fixture
def temp_transcript_claude_code_format(tmp_path):
    """Transcript in Claude Code's actual format (message.role instead of type)"""
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


def test_get_last_turns_claude_code_format(temp_transcript_claude_code_format):
    """Test that we handle Claude Code's transcript format (message.role)"""
    output = review_and_continue.get_last_turns(temp_transcript_claude_code_format)
    # Should find the LAST assistant message, not the first one
    assert "Would you like me to merge this PR?" in output
    # Should NOT contain the earlier message
    assert "All tests pass" not in output


def test_main_hook_logic_no_header(temp_transcript):
    input_data = {
        "transcript_path": temp_transcript
    }
    
    with patch("json.load", return_value=input_data):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="All good", returncode=0)
            
            with patch("sys.exit") as mock_exit:
                review_and_continue.main()
                
                # Check what was sent to hitl-cli
                mock_run.assert_called_once()
                args, kwargs = mock_run.call_args
                summary = ""
                for i, arg in enumerate(args[0]):
                    if arg == "--summary":
                        summary = args[0][i+1]
                
                # Header should be gone
                assert "Claude has completed its task" not in summary
                # Metadata should be gone
                assert "--- Turn" not in summary
                # Only the assistant message should remain
                assert "Committed and PR created" in summary
