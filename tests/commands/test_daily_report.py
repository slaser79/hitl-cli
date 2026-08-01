"""
Tests for the daily-report CLI command.

These tests validate the daily activity report generation functionality.
"""

import subprocess
from datetime import date
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from hitl_cli.main import app


class TestDailyReportCommand:
    """Test the daily-report CLI command"""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing"""
        return CliRunner()

    @pytest.fixture
    def mock_date(self):
        """Mock today's date for consistent testing"""
        with patch('hitl_cli.main.date') as mock_date:
            mock_date.today.return_value = date(2026, 3, 6)
            mock_date.side_effect = date  # Allow date() constructor to work
            yield mock_date

    def test_daily_report_basic(self, runner, mock_date):
        """Test basic daily report generation with no activity"""

        # Mock all subprocess calls to return empty results
        with patch('subprocess.run') as mock_run:
            # Set up mock to return empty results for all calls
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = ""
            mock_run.return_value.returncode = 0

            result = runner.invoke(app, ["daily-report"])

            assert result.exit_code == 0
            assert "📊 Generating Daily Activity Report" in result.output
            assert "📅 Period: 2026-03-05 to 2026-03-06" in result.output
            assert "## Highlights" in result.output
            assert "## PRs Merged" in result.output
            assert "## Issues Closed" in result.output
            assert "## Blockers" in result.output
            assert "## Stats" in result.output

    def test_daily_report_with_merged_prs(self, runner, mock_date):
        """Test daily report with merged PRs"""
        import json

        merged_prs = [
            {"number": 123, "title": "Fix bug in auth module", "mergedAt": "2026-03-06T10:00:00Z"},
            {"number": 124, "title": "Add new feature X", "mergedAt": "2026-03-06T11:00:00Z"},
        ]

        with patch('subprocess.run') as mock_run:
            # First call is for PRs
            mock_pr_result = type('MockResult', (), {})()
            mock_pr_result.stdout = json.dumps(merged_prs)
            mock_pr_result.stderr = ""
            mock_pr_result.returncode = 0

            # Other calls return empty
            mock_empty_result = type('MockResult', (), {})()
            mock_empty_result.stdout = ""
            mock_empty_result.stderr = ""
            mock_empty_result.returncode = 0

            mock_run.side_effect = [
                mock_pr_result, mock_empty_result,
                mock_empty_result, mock_empty_result
            ]

            result = runner.invoke(app, ["daily-report"])

            assert result.exit_code == 0
            assert "#123: Fix bug in auth module" in result.output
            assert "#124: Add new feature X" in result.output
            assert "2 PR(s) merged" in result.output

    def test_daily_report_with_closed_issues(self, runner, mock_date):
        """Test daily report with closed issues"""
        import json

        closed_issues = [
            {"number": 456, "title": "Update documentation", "closedAt": "2026-03-06T09:00:00Z"},
        ]

        with patch('subprocess.run') as mock_run:
            # First two calls return empty (PRs, issues - but we want issues to have data)
            mock_empty_result = type('MockResult', (), {})()
            mock_empty_result.stdout = ""
            mock_empty_result.stderr = ""
            mock_empty_result.returncode = 0

            mock_issue_result = type('MockResult', (), {})()
            mock_issue_result.stdout = json.dumps(closed_issues)
            mock_issue_result.stderr = ""
            mock_issue_result.returncode = 0

            mock_run.side_effect = [
                mock_empty_result, mock_issue_result,
                mock_empty_result, mock_empty_result
            ]

            result = runner.invoke(app, ["daily-report"])

            assert result.exit_code == 0
            assert "#456: Update documentation" in result.output
            assert "1 issue(s) closed" in result.output

    def test_daily_report_with_blockers(self, runner, mock_date):
        """Test daily report with open blockers"""
        import json

        blockers = [
            {"number": 789, "title": "Critical performance issue"},
        ]

        with patch('subprocess.run') as mock_run:
            mock_empty_result = type('MockResult', (), {})()
            mock_empty_result.stdout = ""
            mock_empty_result.stderr = ""
            mock_empty_result.returncode = 0

            mock_blocker_result = type('MockResult', (), {})()
            mock_blocker_result.stdout = json.dumps(blockers)
            mock_blocker_result.stderr = ""
            mock_blocker_result.returncode = 0

            # PRs, issues, commits empty, blockers have data
            mock_run.side_effect = [
                mock_empty_result,  # PRs
                mock_empty_result,  # Issues
                mock_empty_result,  # Commits
                mock_blocker_result,  # Blockers
            ]

            result = runner.invoke(app, ["daily-report"])

            assert result.exit_code == 0
            assert "#789: Critical performance issue" in result.output
            assert "Open blockers: 1" in result.output

    def test_daily_report_with_commits(self, runner, mock_date):
        """Test daily report with commits to main"""
        commits_output = """abc123 Fix typo in README
def456 Add new feature
789ghi Update dependencies"""

        with patch('subprocess.run') as mock_run:
            mock_empty_result = type('MockResult', (), {})()
            mock_empty_result.stdout = ""
            mock_empty_result.stderr = ""
            mock_empty_result.returncode = 0

            mock_commit_result = type('MockResult', (), {})()
            mock_commit_result.stdout = commits_output
            mock_commit_result.stderr = ""
            mock_commit_result.returncode = 0

            # PRs, issues empty, commits have data, blockers empty
            mock_run.side_effect = [
                mock_empty_result,  # PRs
                mock_empty_result,  # Issues
                mock_commit_result,  # Commits
                mock_empty_result,  # Blockers
            ]

            result = runner.invoke(app, ["daily-report"])

            assert result.exit_code == 0
            assert "Commits to main: 3" in result.output
            assert "3 commit(s) to main" in result.output

    def test_daily_report_custom_repo(self, runner, mock_date):
        """Test daily report with custom repository"""

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = ""
            mock_run.return_value.returncode = 0

            result = runner.invoke(app, ["daily-report", "--repo", "myorg/myrepo"])

            assert result.exit_code == 0
            # Verify the command was called with the custom repo
            calls = [call[0][0] for call in mock_run.call_args_list]
            # Check that gh commands used the custom repo
            gh_calls = [c for c in calls if isinstance(c, list) and len(c) > 0 and c[0] == "gh"]
            for call in gh_calls:
                assert "-R" in call
                repo_idx = call.index("-R")
                assert call[repo_idx + 1] == "myorg/myrepo"

    def test_daily_report_custom_days(self, runner, mock_date):
        """Test daily report with custom days parameter"""

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = ""
            mock_run.return_value.returncode = 0

            result = runner.invoke(app, ["daily-report", "--days", "7"])

            assert result.exit_code == 0
            # Should show 7 day period
            assert "📅 Period: 2026-02-27 to 2026-03-06" in result.output

    def test_daily_report_gh_error_handling(self, runner, mock_date):
        """Test daily report handles gh CLI errors gracefully"""

        with patch('subprocess.run') as mock_run:
            # Simulate gh CLI error
            mock_error_result = type('MockResult', (), {})()
            mock_error_result.stdout = ""
            mock_error_result.stderr = "Error: not logged in to gh"
            mock_error_result.returncode = 1

            mock_run.side_effect = subprocess.CalledProcessError(
                1, ["gh"], stderr="Error: not logged in to gh"
            )

            # Should not crash, but show warnings
            result = runner.invoke(app, ["daily-report"])

            # The command should handle errors gracefully
            # It may exit with error or show warnings depending on implementation
            assert "Warning" in result.output or result.exit_code != 0

    def test_daily_report_full_activity(self, runner, mock_date):
        """Test daily report with all types of activity"""
        import json

        merged_prs = [{"number": 1, "title": "PR 1", "mergedAt": "2026-03-06T10:00:00Z"}]
        closed_issues = [{"number": 2, "title": "Issue 2", "closedAt": "2026-03-06T11:00:00Z"}]
        commits_output = "abc123 Commit message"
        blockers = [{"number": 3, "title": "Blocker 3"}]

        with patch('subprocess.run') as mock_run:
            mock_pr_result = type('MockResult', (), {})()
            mock_pr_result.stdout = json.dumps(merged_prs)
            mock_pr_result.stderr = ""
            mock_pr_result.returncode = 0

            mock_issue_result = type('MockResult', (), {})()
            mock_issue_result.stdout = json.dumps(closed_issues)
            mock_issue_result.stderr = ""
            mock_issue_result.returncode = 0

            mock_commit_result = type('MockResult', (), {})()
            mock_commit_result.stdout = commits_output
            mock_commit_result.stderr = ""
            mock_commit_result.returncode = 0

            mock_blocker_result = type('MockResult', (), {})()
            mock_blocker_result.stdout = json.dumps(blockers)
            mock_blocker_result.stderr = ""
            mock_blocker_result.returncode = 0

            mock_run.side_effect = [
                mock_pr_result,
                mock_issue_result,
                mock_commit_result,
                mock_blocker_result,
            ]

            result = runner.invoke(app, ["daily-report"])

            assert result.exit_code == 0
            assert "#1: PR 1" in result.output
            assert "#2: Issue 2" in result.output
            assert "#3: Blocker 3" in result.output
            assert "Commits to main: 1" in result.output
            assert "Open blockers: 1" in result.output
            assert "PRs merged: 1" in result.output
            assert "Issues closed: 1" in result.output
