"""
Tests for Analytics CLI commands
Tests analytics and metrics functionality
"""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.analytics import app


class TestAnalyticsSummary:
    """Test analytics summary command"""
    
    @patch('cli.analytics.get_analytics')
    @patch('cli.analytics.get_output')
    def test_analytics_summary_basic(self, mock_get_output, mock_get_analytics):
        """Test basic analytics summary"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_analytics = MagicMock()
        mock_analytics.get_summary.return_value = {
            'command_stats': {
                'total_commands': 100,
                'unique_commands': 20,
                'success_rate': 95.0,
                'avg_duration': 1.5,
                'top_commands': [
                    {'command': 'status', 'count': 50}
                ]
            },
            'performance_stats': {
                'total_operations': 100,
                'avg_duration': 1.5
            },
            'error_stats': {
                'total_errors': 5,
                'most_common_errors': []
            }
        }
        mock_get_analytics.return_value = mock_analytics
        
        runner = CliRunner()
        result = runner.invoke(app, ["summary"])
        
        assert result.exit_code == 0
    
    @patch('cli.analytics.get_analytics')
    @patch('cli.analytics.get_output')
    def test_analytics_summary_days(self, mock_get_output, mock_get_analytics):
        """Test analytics summary with custom days"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_analytics = MagicMock()
        mock_analytics.get_summary.return_value = {
            'command_stats': {'total_commands': 50, 'unique_commands': 10, 'success_rate': 95.0, 'avg_duration': 1.0, 'top_commands': []},
            'performance_stats': {'total_operations': 50, 'avg_duration': 1.0},
            'error_stats': {'total_errors': 0, 'most_common_errors': []}
        }
        mock_get_analytics.return_value = mock_analytics
        
        runner = CliRunner()
        result = runner.invoke(app, ["summary", "--days", "30"])
        
        assert result.exit_code == 0
        mock_analytics.get_summary.assert_called_with(30)
    
    @patch('cli.analytics.get_analytics')
    @patch('cli.analytics.get_output')
    def test_analytics_summary_json(self, mock_get_output, mock_get_analytics):
        """Test analytics summary with JSON output"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_analytics = MagicMock()
        mock_analytics.get_summary.return_value = {
            'command_stats': {'total_commands': 100, 'unique_commands': 20, 'success_rate': 95.0, 'avg_duration': 1.0, 'top_commands': []},
            'performance_stats': {'total_operations': 100, 'avg_duration': 1.0},
            'error_stats': {'total_errors': 0, 'most_common_errors': []}
        }
        mock_get_analytics.return_value = mock_analytics
        
        runner = CliRunner()
        result = runner.invoke(app, ["summary", "--json"])
        
        assert result.exit_code == 0


class TestAnalyticsCommands:
    """Test analytics commands command"""
    
    @patch('cli.analytics.get_analytics')
    @patch('cli.analytics.get_output')
    def test_command_stats(self, mock_get_output, mock_get_analytics):
        """Test command statistics"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_analytics = MagicMock()
        mock_analytics.get_command_stats.return_value = {
            'total_commands': 100,
            'top_commands': [{'command': 'status', 'count': 50}],
            'command_durations': {'status': 1.5},
            'success_rate': 95.0
        }
        mock_get_analytics.return_value = mock_analytics
        
        runner = CliRunner()
        result = runner.invoke(app, ["commands"])
        
        assert result.exit_code == 0


class TestAnalyticsPerformance:
    """Test analytics performance command"""
    
    @patch('cli.analytics.get_analytics')
    @patch('cli.analytics.get_output')
    def test_performance_stats(self, mock_get_output, mock_get_analytics):
        """Test performance statistics"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_analytics = MagicMock()
        mock_analytics.get_performance_stats.return_value = {
            'total_operations': 100,
            'avg_duration': 1.5,
            'min_duration': 0.1,
            'max_duration': 5.0,
            'p95_duration': 3.0,
            'p99_duration': 4.5,
            'slowest_operations': [
                {'operation': 'status', 'avg_duration': 2.0}
            ]
        }
        mock_get_analytics.return_value = mock_analytics
        
        runner = CliRunner()
        result = runner.invoke(app, ["performance"])
        
        assert result.exit_code == 0


class TestAnalyticsErrors:
    """Test analytics errors command"""
    
    @patch('cli.analytics.get_analytics')
    @patch('cli.analytics.get_output')
    def test_error_stats(self, mock_get_output, mock_get_analytics):
        """Test error statistics"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_analytics = MagicMock()
        mock_analytics.get_error_stats.return_value = {
            'total_errors': 5,
            'most_common_errors': [{'type': 'ValueError', 'count': 3}],
            'error_rate': 5.0
        }
        mock_get_analytics.return_value = mock_analytics
        
        runner = CliRunner()
        result = runner.invoke(app, ["errors"])
        
        assert result.exit_code == 0


class TestAnalyticsClear:
    """Test analytics clear command"""
    
    @patch('cli.analytics.get_analytics')
    @patch('cli.analytics.get_output')
    def test_clear_analytics(self, mock_get_output, mock_get_analytics):
        """Test clearing analytics"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_analytics = MagicMock()
        mock_analytics.clear_analytics.return_value = True
        mock_get_analytics.return_value = mock_analytics
        
        runner = CliRunner()
        result = runner.invoke(app, ["clear", "--yes"])
        
        assert result.exit_code == 0
        mock_analytics.clear_analytics.assert_called_once()

