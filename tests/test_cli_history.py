"""
Tests for CLI History Commands
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from typer.testing import CliRunner

from cli.history_commands import app
from cli.history import CommandHistory, get_history


class TestHistoryCommands:
    """Test history CLI commands"""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner"""
        return CliRunner()
    
    @pytest.fixture
    def mock_history(self):
        """Create mock history with sample data"""
        history = MagicMock(spec=CommandHistory)
        history.history = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "command": "training start",
                "args": {"model": "test"},
                "result": None
            },
            {
                "timestamp": "2024-01-01T11:00:00",
                "command": "model list",
                "args": {},
                "result": None
            },
            {
                "timestamp": "2024-01-01T12:00:00",
                "command": "training start",
                "args": {"model": "test2"},
                "result": None
            }
        ]
        history.get_recent.return_value = history.history[-2:]
        history.search.return_value = [history.history[0], history.history[2]]
        history.max_history = 1000
        history.history_file = Path("/test/history.json")
        return history
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    def test_list_history(self, mock_output, mock_get_history, runner, mock_history):
        """Test listing command history"""
        mock_get_history.return_value = mock_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["list", "--limit", "5"])
        
        assert result.exit_code == 0
        mock_history.get_recent.assert_called_once_with(5)
        output_obj.print.assert_called()
        output_obj.success.assert_called()
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    def test_list_history_json(self, mock_output, mock_get_history, runner, mock_history):
        """Test listing history in JSON format"""
        mock_get_history.return_value = mock_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["list", "--json", "--limit", "2"])
        
        assert result.exit_code == 0
        mock_history.get_recent.assert_called_once_with(2)
        # Check that JSON was printed
        assert output_obj.print.called
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    def test_list_history_empty(self, mock_output, mock_get_history, runner):
        """Test listing empty history"""
        empty_history = MagicMock(spec=CommandHistory)
        empty_history.history = []
        empty_history.get_recent.return_value = []
        mock_get_history.return_value = empty_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        output_obj.info.assert_called_with("No command history found.")
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    def test_search_history(self, mock_output, mock_get_history, runner, mock_history):
        """Test searching command history"""
        mock_get_history.return_value = mock_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["search", "training", "--limit", "5"])
        
        assert result.exit_code == 0
        mock_history.search.assert_called_once_with("training", 5)
        output_obj.print.assert_called()
        output_obj.success.assert_called()
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    def test_search_history_no_results(self, mock_output, mock_get_history, runner):
        """Test searching with no results"""
        empty_history = MagicMock(spec=CommandHistory)
        empty_history.search.return_value = []
        mock_get_history.return_value = empty_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["search", "nonexistent"])
        
        assert result.exit_code == 0
        output_obj.info.assert_called()
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    @patch('cli.history_commands.typer.confirm')
    def test_clear_history_confirmed(self, mock_confirm, mock_output, mock_get_history, runner, mock_history):
        """Test clearing history with confirmation"""
        mock_confirm.return_value = True
        mock_get_history.return_value = mock_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["clear"])
        
        assert result.exit_code == 0
        mock_history.clear.assert_called_once()
        output_obj.success.assert_called()
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    @patch('cli.history_commands.typer.confirm')
    def test_clear_history_cancelled(self, mock_confirm, mock_output, mock_get_history, runner, mock_history):
        """Test clearing history cancelled"""
        mock_confirm.return_value = False
        mock_get_history.return_value = mock_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["clear"])
        
        assert result.exit_code == 0
        mock_history.clear.assert_not_called()
        output_obj.info.assert_called_with("Operation cancelled.")
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    def test_clear_history_yes_flag(self, mock_output, mock_get_history, runner, mock_history):
        """Test clearing history with --yes flag"""
        mock_get_history.return_value = mock_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["clear", "--yes"])
        
        assert result.exit_code == 0
        mock_history.clear.assert_called_once()
        output_obj.success.assert_called()
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    def test_history_stats(self, mock_output, mock_get_history, runner, mock_history):
        """Test history statistics"""
        mock_get_history.return_value = mock_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["stats"])
        
        assert result.exit_code == 0
        output_obj.print.assert_called()
        output_obj.success.assert_called()
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    def test_history_stats_empty(self, mock_output, mock_get_history, runner):
        """Test history stats with empty history"""
        empty_history = MagicMock(spec=CommandHistory)
        empty_history.history = []
        mock_get_history.return_value = empty_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["stats"])
        
        assert result.exit_code == 0
        output_obj.info.assert_called_with("No command history available.")
    
    @patch('cli.history_commands.get_history')
    @patch('cli.history_commands.get_output')
    def test_history_stats_json(self, mock_output, mock_get_history, runner, mock_history):
        """Test history stats in JSON format"""
        mock_get_history.return_value = mock_history
        output_obj = MagicMock()
        mock_output.return_value = output_obj
        
        result = runner.invoke(app, ["stats", "--json"])
        
        assert result.exit_code == 0
        # Check that JSON was printed
        assert output_obj.print.called


class TestCommandHistoryIntegration:
    """Test CommandHistory class integration"""
    
    @pytest.fixture
    def temp_history_file(self, tmp_path):
        """Create temporary history file"""
        history_file = tmp_path / "test_history.json"
        return history_file
    
    def test_add_command(self, temp_history_file):
        """Test adding commands to history"""
        history = CommandHistory(history_file=temp_history_file, max_history=10)
        
        history.add("test command", args={"key": "value"})
        
        assert len(history.history) == 1
        assert history.history[0]["command"] == "test command"
        assert history.history[0]["args"]["key"] == "value"
        assert "timestamp" in history.history[0]
    
    def test_get_recent(self, temp_history_file):
        """Test getting recent commands"""
        history = CommandHistory(history_file=temp_history_file, max_history=10)
        
        for i in range(5):
            history.add(f"command {i}")
        
        recent = history.get_recent(3)
        assert len(recent) == 3
        assert recent[-1]["command"] == "command 4"
    
    def test_search(self, temp_history_file):
        """Test searching history"""
        history = CommandHistory(history_file=temp_history_file, max_history=10)
        
        history.add("training start")
        history.add("model list")
        history.add("training stop")
        
        results = history.search("training")
        assert len(results) == 2
        assert all("training" in r["command"].lower() for r in results)
    
    def test_clear(self, temp_history_file):
        """Test clearing history"""
        history = CommandHistory(history_file=temp_history_file, max_history=10)
        
        history.add("test command")
        assert len(history.history) == 1
        
        history.clear()
        assert len(history.history) == 0
    
    def test_max_history_limit(self, temp_history_file):
        """Test max history limit"""
        history = CommandHistory(history_file=temp_history_file, max_history=3)
        
        for i in range(5):
            history.add(f"command {i}")
        
        assert len(history.history) == 3
        assert history.history[0]["command"] == "command 2"
        assert history.history[-1]["command"] == "command 4"
    
    def test_save_and_load(self, temp_history_file):
        """Test saving and loading history"""
        history1 = CommandHistory(history_file=temp_history_file, max_history=10)
        history1.add("test command", args={"key": "value"})
        
        # Create new instance to test loading
        history2 = CommandHistory(history_file=temp_history_file, max_history=10)
        assert len(history2.history) == 1
        assert history2.history[0]["command"] == "test command"
        assert history2.history[0]["args"]["key"] == "value"

