"""
Tests for Status and Version CLI commands
Tests status and version display
"""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.status import status_command, version_command
from cli.main import app


class TestStatusCommand:
    """Test status command"""
    
    @patch('cli.status.get_config')
    @patch('cli.status.get_project_root')
    def test_status_command_basic(self, mock_root, mock_config):
        """Test basic status command"""
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'INFO'
        mock_config.return_value = mock_config_instance
        mock_root.return_value = Path('/test')
        
        runner = CliRunner()
        result = runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
    
    @patch('cli.status.get_config')
    @patch('cli.status.get_project_root')
    def test_status_command_json(self, mock_root, mock_config):
        """Test status command with JSON output"""
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'INFO'
        mock_config.return_value = mock_config_instance
        mock_root.return_value = Path('/test')
        
        runner = CliRunner()
        result = runner.invoke(app, ["status", "--json"])
        
        assert result.exit_code == 0
    
    @patch('cli.status.get_config')
    @patch('cli.status.get_project_root')
    def test_status_command_verbose(self, mock_root, mock_config):
        """Test status command with verbose"""
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = 'INFO'
        mock_config.return_value = mock_config_instance
        mock_root.return_value = Path('/test')
        
        runner = CliRunner()
        result = runner.invoke(app, ["status", "--verbose"])
        
        assert result.exit_code == 0


class TestVersionCommand:
    """Test version command"""
    
    def test_version_command_basic(self):
        """Test basic version command"""
        runner = CliRunner()
        result = runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
    
    def test_version_command_json(self):
        """Test version command with JSON output"""
        runner = CliRunner()
        result = runner.invoke(app, ["version", "--json"])
        
        assert result.exit_code == 0
        # Should contain version info
        assert "version" in result.stdout.lower() or len(result.stdout) > 0

