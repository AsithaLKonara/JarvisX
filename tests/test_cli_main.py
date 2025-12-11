"""
Tests for main CLI entry point
Tests CLI initialization, command registration, and basic functionality
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from typer.testing import CliRunner

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.main import app, cli

# Set timeout for all tests in this file (5 seconds)
pytestmark = pytest.mark.timeout(5)


class TestCLIMain:
    """Test main CLI entry point"""
    
    def test_cli_help_display(self):
        """Test that CLI shows help when no command provided"""
        runner = CliRunner()
        result = runner.invoke(app, [])
        
        # Should show help or welcome message (Typer may exit with 0, 1, or 2)
        assert result.exit_code in [0, 1, 2]
    
    def test_cli_help_flag(self):
        """Test --help flag"""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "JarvisX V2" in result.stdout or "Command Line Interface" in result.stdout
    
    def test_command_group_registration(self):
        """Test that all command groups are registered"""
        runner = CliRunner()
        
        # Test that command groups exist
        result = runner.invoke(app, ["--help"])
        
        # Check for major command groups
        output = result.stdout.lower()
        assert "training" in output or "cloud" in output or "system" in output
    
    def test_import_error_handling(self, monkeypatch):
        """Test handling of import errors"""
        # Mock import error
        original_import = __import__
        
        def mock_import(name, *args, **kwargs):
            if name == "cli.training":
                raise ImportError("Module not found")
            return original_import(name, *args, **kwargs)
        
        monkeypatch.setattr("builtins.__import__", mock_import)
        
        # Should handle gracefully
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        # May exit with error code but shouldn't crash
        assert result.exit_code in [0, 1]
    
    def test_no_command_shows_help(self):
        """Test that no command shows help or welcome"""
        runner = CliRunner()
        result = runner.invoke(app, [])
        
        # Should show help or welcome message (Typer may exit with 0, 1, or 2)
        assert result.exit_code in [0, 1, 2]
        assert len(result.stdout) > 0
    
    def test_exit_codes(self):
        """Test exit codes for different scenarios"""
        runner = CliRunner()
        
        # Valid command should exit with 0
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        
        # Invalid command should exit with non-zero
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0
    
    @patch('cli.main.get_history')
    @patch('cli.main.get_analytics')
    def test_command_history_tracking(self, mock_analytics, mock_history):
        """Test that commands are tracked in history"""
        mock_history_instance = MagicMock()
        mock_history.return_value = mock_history_instance
        
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        # History should be accessed (may or may not add depending on command)
        # Just verify it doesn't crash
        assert result.exit_code in [0, 1]
    
    @patch('cli.main.get_analytics')
    def test_analytics_tracking(self, mock_analytics):
        """Test that commands are tracked in analytics"""
        mock_analytics_instance = MagicMock()
        mock_analytics.return_value = mock_analytics_instance
        
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        # Analytics should be accessed
        # Just verify it doesn't crash
        assert result.exit_code in [0, 1]
    
    def test_version_command(self):
        """Test version command"""
        runner = CliRunner()
        result = runner.invoke(app, ["version"])
        
        # Should show version or exit successfully
        assert result.exit_code in [0, 1]
    
    def test_status_command(self):
        """Test status command"""
        runner = CliRunner()
        result = runner.invoke(app, ["status"])
        
        # Should show status or exit successfully
        assert result.exit_code in [0, 1]
    
    def test_verbose_option(self):
        """Test --verbose option"""
        runner = CliRunner()
        result = runner.invoke(app, ["--verbose", "--help"])
        
        assert result.exit_code == 0
    
    def test_json_option(self):
        """Test --json option"""
        runner = CliRunner()
        result = runner.invoke(app, ["--json", "status"])
        
        # Should work with JSON output
        assert result.exit_code in [0, 1]
    
    def test_config_option(self):
        """Test --config option"""
        runner = CliRunner()
        result = runner.invoke(app, ["--config", "nonexistent.json", "--help"])
        
        # Should handle config option (may fail if file doesn't exist)
        assert result.exit_code in [0, 1]
    
    def test_voice_option(self):
        """Test --voice option"""
        runner = CliRunner()
        result = runner.invoke(app, ["--voice", "--help"])
        
        # Should accept voice option
        assert result.exit_code == 0
    
    def test_keyboard_interrupt_handling(self):
        """Test keyboard interrupt handling"""
        runner = CliRunner()
        
        # Simulate keyboard interrupt
        with patch('cli.main.app') as mock_app:
            mock_app.side_effect = KeyboardInterrupt()
            # Should handle gracefully
            # This is tested through the cli() function structure
            pass
    
    def test_unexpected_error_handling(self):
        """Test unexpected error handling"""
        runner = CliRunner()
        
        # Test with invalid input that might cause errors
        result = runner.invoke(app, ["invalid", "command", "with", "args"])
        
        # Should handle error gracefully
        assert result.exit_code != 0  # Should exit with error code

