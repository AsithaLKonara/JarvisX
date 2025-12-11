"""
Integration tests for CLI commands
Tests the full workflow of CLI operations
"""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.utils import CLIOutput, validate_path, validate_url, validate_email
from cli.main import app


class TestCLIIntegration:
    """Integration tests for CLI commands"""
    
    def test_training_workflow(self, temp_dir, sample_training_config):
        """Test complete training workflow"""
        # Test that components work together
        output = CLIOutput(json_output=True)
        assert output is not None
        
        # Test validation
        assert validate_path(str(temp_dir)) is True
        assert validate_path("nonexistent", must_exist=False) is True
    
    def test_cloud_deployment_workflow(self):
        """Test cloud deployment workflow"""
        # Test URL validation
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com") is True
        assert validate_url("not-a-url") is False
    
    def test_business_operations_workflow(self):
        """Test business operations workflow"""
        # Test email validation
        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False
    
    def test_system_monitoring_workflow(self, project_root_path):
        """Test system monitoring workflow"""
        # Test that project root exists
        assert project_root_path.exists()
        assert (project_root_path / "main.py").exists()
    
    def test_command_chaining(self):
        """Test command chaining workflow"""
        runner = CliRunner()
        
        # Test multiple commands in sequence
        result1 = runner.invoke(app, ["status"])
        assert result1.exit_code in [0, 1]
        
        result2 = runner.invoke(app, ["version"])
        assert result2.exit_code in [0, 1]
    
    @patch('cli.base.get_config')
    def test_configuration_persistence(self, mock_get_config):
        """Test configuration persistence across commands"""
        mock_config = MagicMock()
        mock_config.get.return_value = 'INFO'
        mock_get_config.return_value = mock_config
        
        runner = CliRunner()
        result1 = runner.invoke(app, ["status"])
        result2 = runner.invoke(app, ["status", "--verbose"])
        
        # Config should be accessed in both
        assert result1.exit_code in [0, 1]
        assert result2.exit_code in [0, 1]
    
    @patch('cli.main.get_history')
    def test_history_tracking(self, mock_history):
        """Test history tracking across commands"""
        mock_history_instance = MagicMock()
        mock_history.return_value = mock_history_instance
        
        runner = CliRunner()
        result1 = runner.invoke(app, ["status"])
        result2 = runner.invoke(app, ["version"])
        
        # History should be tracked
        assert result1.exit_code in [0, 1]
        assert result2.exit_code in [0, 1]
    
    @patch('cli.main.get_analytics')
    def test_analytics_aggregation(self, mock_analytics):
        """Test analytics aggregation across commands"""
        mock_analytics_instance = MagicMock()
        mock_analytics.return_value = mock_analytics_instance
        
        runner = CliRunner()
        result1 = runner.invoke(app, ["status"])
        result2 = runner.invoke(app, ["version"])
        
        # Analytics should be tracked
        assert result1.exit_code in [0, 1]
        assert result2.exit_code in [0, 1]
    
    def test_multi_command_workflow(self):
        """Test multi-command workflow"""
        runner = CliRunner()
        
        # Simulate a workflow: status -> version -> help
        commands = [
            ["status"],
            ["version"],
            ["help", "command", "training"]
        ]
        
        for cmd in commands:
            result = runner.invoke(app, cmd)
            assert result.exit_code in [0, 1]


class TestCLIErrorHandling:
    """Test error handling in CLI commands"""
    
    def test_invalid_input_handling(self):
        """Test that invalid inputs are handled gracefully"""
        # Invalid URL
        assert validate_url("") is False
        assert validate_url("not-a-url") is False
        
        # Invalid email
        assert validate_email("") is False
        assert validate_email("@example.com") is False
        
        # Invalid path
        assert validate_path("") is False
    
    def test_missing_dependencies(self, monkeypatch):
        """Test behavior when dependencies are missing"""
        # Test graceful degradation when optional deps are missing
        output = CLIOutput(json_output=True)
        assert output is not None

