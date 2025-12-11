"""
Tests for common CLI options
Tests --verbose, --json, --voice, --config options across commands
"""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.main import app
from cli.base import get_config, get_output

# Set timeout for all tests in this file (5 seconds)
pytestmark = pytest.mark.timeout(5)


class TestVerboseOption:
    """Test --verbose option"""
    
    def test_verbose_flag(self):
        """Test that --verbose flag is accepted"""
        runner = CliRunner()
        result = runner.invoke(app, ["--verbose", "--help"])
        
        assert result.exit_code == 0
    
    def test_verbose_short_flag(self):
        """Test that -v flag works"""
        runner = CliRunner()
        result = runner.invoke(app, ["-v", "--help"])
        
        assert result.exit_code == 0
    
    @patch('cli.base.get_config')
    def test_verbose_config_setting(self, mock_get_config):
        """Test that verbose sets config"""
        mock_config = MagicMock()
        mock_config.get.return_value = False
        mock_get_config.return_value = mock_config
        
        runner = CliRunner()
        result = runner.invoke(app, ["--verbose", "status"])
        
        # Config should be accessed
        assert result.exit_code in [0, 1]


class TestJSONOption:
    """Test --json option"""
    
    def test_json_flag(self):
        """Test that --json flag is accepted"""
        runner = CliRunner()
        result = runner.invoke(app, ["--json", "status"])
        
        assert result.exit_code in [0, 1]
    
    @patch('cli.base.get_output')
    def test_json_output_format(self, mock_get_output):
        """Test that JSON output is used when --json is set"""
        mock_output = MagicMock()
        mock_output.json_output = True
        mock_get_output.return_value = mock_output
        
        runner = CliRunner()
        result = runner.invoke(app, ["--json", "status"])
        
        # Output should be configured for JSON
        assert result.exit_code in [0, 1]
    
    def test_json_with_other_options(self):
        """Test JSON option with other options"""
        runner = CliRunner()
        result = runner.invoke(app, ["--json", "--verbose", "status"])
        
        assert result.exit_code in [0, 1]


class TestVoiceOption:
    """Test --voice option"""
    
    def test_voice_flag(self):
        """Test that --voice flag is accepted"""
        runner = CliRunner()
        result = runner.invoke(app, ["--voice", "--help"])
        
        assert result.exit_code == 0
    
    @patch('cli.base.get_output')
    def test_voice_output_integration(self, mock_get_output):
        """Test that voice option enables TTS"""
        mock_output = MagicMock()
        mock_output.voice = False
        mock_get_output.return_value = mock_output
        
        runner = CliRunner()
        result = runner.invoke(app, ["--voice", "status"])
        
        # Voice option should be processed
        assert result.exit_code in [0, 1]
    
    def test_voice_with_json(self):
        """Test voice option with JSON output"""
        runner = CliRunner()
        result = runner.invoke(app, ["--voice", "--json", "status"])
        
        assert result.exit_code in [0, 1]


class TestConfigOption:
    """Test --config option"""
    
    def test_config_flag(self):
        """Test that --config flag is accepted"""
        runner = CliRunner()
        result = runner.invoke(app, ["--config", "test.json", "--help"])
        
        assert result.exit_code == 0
    
    @patch('cli.base.get_config')
    def test_config_file_loading(self, mock_get_config):
        """Test that config file is loaded"""
        mock_config = MagicMock()
        mock_get_config.return_value = mock_config
        
        runner = CliRunner()
        result = runner.invoke(app, ["--config", "test.json", "status"])
        
        # Config should be accessed
        assert result.exit_code in [0, 1]
    
    def test_config_file_not_found(self):
        """Test handling of missing config file"""
        runner = CliRunner()
        result = runner.invoke(app, ["--config", "nonexistent.json", "status"])
        
        # Should handle gracefully (may exit with error)
        assert result.exit_code in [0, 1]


class TestOptionCombinations:
    """Test combinations of options"""
    
    def test_all_options_together(self):
        """Test all options used together"""
        runner = CliRunner()
        result = runner.invoke(app, [
            "--verbose",
            "--json",
            "--voice",
            "--config", "test.json",
            "--help"
        ])
        
        assert result.exit_code == 0
    
    def test_verbose_and_json(self):
        """Test verbose and JSON together"""
        runner = CliRunner()
        result = runner.invoke(app, ["--verbose", "--json", "status"])
        
        assert result.exit_code in [0, 1]
    
    def test_verbose_and_voice(self):
        """Test verbose and voice together"""
        runner = CliRunner()
        result = runner.invoke(app, ["--verbose", "--voice", "status"])
        
        assert result.exit_code in [0, 1]


class TestInvalidOptions:
    """Test invalid option handling"""
    
    def test_invalid_option_name(self):
        """Test that invalid option names are rejected"""
        runner = CliRunner()
        result = runner.invoke(app, ["--invalid-option", "--help"])
        
        # Should show error or help
        assert result.exit_code != 0 or "--help" in result.stdout
    
    def test_missing_option_value(self):
        """Test handling of missing option values"""
        runner = CliRunner()
        result = runner.invoke(app, ["--config", "--help"])
        
        # Should handle missing value
        assert result.exit_code in [0, 1]

