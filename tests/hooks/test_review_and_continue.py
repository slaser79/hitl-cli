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
    output = review_and_continue.get_last_turns(temp_transcript, num_turns=2)
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
    """Test that we find assistant messages even if they're not in the last 2 lines"""
    output = review_and_continue.get_last_turns(temp_transcript_with_tool_results, num_turns=2)
    # Should find the assistant message even though it's not in the last 2 lines
    assert "recommended next steps" in output
    # Should NOT return the "no activity" message
    assert "No recent activity" not in output


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
