"""
Tests for Plugin CLI commands
Tests plugin management functionality
"""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.plugin import app


class TestPluginList:
    """Test plugin list command"""
    
    @patch('cli.plugin.get_output')
    @patch('cli.plugin.get_plugin_manager')
    def test_list_plugins_basic(self, mock_get_manager, mock_get_output):
        """Test basic plugin list"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_manager = MagicMock()
        mock_manager.get_all_plugins_info.return_value = {
            'plugins': {
                'test_plugin': {
                    'version': '1.0.0',
                    'enabled': True,
                    'metadata': {
                        'category': 'test',
                        'description': 'Test plugin'
                    }
                }
            }
        }
        mock_manager.enabled_plugins = {'test_plugin': MagicMock()}
        mock_get_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
    
    @patch('cli.plugin.get_output')
    @patch('cli.plugin.get_plugin_manager')
    def test_list_plugins_enabled_only(self, mock_get_manager, mock_get_output):
        """Test listing only enabled plugins"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_manager = MagicMock()
        mock_manager.get_all_plugins_info.return_value = {
            'plugins': {
                'enabled_plugin': {'enabled': True},
                'disabled_plugin': {'enabled': False}
            }
        }
        mock_manager.enabled_plugins = {'enabled_plugin': MagicMock()}
        mock_get_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(app, ["list", "--enabled"])
        
        assert result.exit_code == 0
    
    @patch('cli.plugin.get_output')
    @patch('cli.plugin.get_plugin_manager')
    def test_list_plugins_json(self, mock_get_manager, mock_get_output):
        """Test plugin list with JSON output"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_manager = MagicMock()
        mock_manager.get_all_plugins_info.return_value = {
            'plugins': {'test': {'version': '1.0'}}
        }
        mock_manager.enabled_plugins = {}
        mock_get_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(app, ["list", "--json"])
        
        assert result.exit_code == 0


class TestPluginEnable:
    """Test plugin enable command"""
    
    @patch('cli.plugin.get_output')
    @patch('cli.plugin.get_plugin_manager')
    def test_enable_plugin(self, mock_get_manager, mock_get_output):
        """Test enabling a plugin"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_manager = MagicMock()
        mock_manager.enable_plugin.return_value = True
        mock_get_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(app, ["enable", "test_plugin"])
        
        assert result.exit_code == 0
        mock_manager.enable_plugin.assert_called_once_with("test_plugin")
    
    @patch('cli.plugin.get_output')
    @patch('cli.plugin.get_plugin_manager')
    def test_enable_plugin_json(self, mock_get_manager, mock_get_output):
        """Test enabling plugin with JSON output"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_manager = MagicMock()
        mock_manager.enable_plugin.return_value = True
        mock_get_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(app, ["enable", "test_plugin", "--json"])
        
        assert result.exit_code == 0


class TestPluginDisable:
    """Test plugin disable command"""
    
    @patch('cli.plugin.get_output')
    @patch('cli.plugin.get_plugin_manager')
    def test_disable_plugin(self, mock_get_manager, mock_get_output):
        """Test disabling a plugin"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_manager = MagicMock()
        mock_manager.disable_plugin.return_value = True
        mock_get_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(app, ["disable", "test_plugin"])
        
        assert result.exit_code == 0
        mock_manager.disable_plugin.assert_called_once_with("test_plugin")


class TestPluginInfo:
    """Test plugin info command"""
    
    @patch('cli.plugin.get_output')
    @patch('cli.plugin.get_plugin_manager')
    def test_plugin_info(self, mock_get_manager, mock_get_output):
        """Test getting plugin information"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_manager = MagicMock()
        mock_manager.get_plugin_info.return_value = {
            'name': 'test_plugin',
            'version': '1.0.0',
            'enabled': True,
            'metadata': {'description': 'Test'}
        }
        mock_get_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(app, ["info", "test_plugin"])
        
        assert result.exit_code == 0
        mock_manager.get_plugin_info.assert_called_once_with("test_plugin")


class TestPluginCreate:
    """Test plugin create command"""
    
    @patch('cli.plugin.get_output')
    @patch('cli.plugin.get_plugin_manager')
    def test_create_plugin(self, mock_get_manager, mock_get_output):
        """Test creating a new plugin"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_manager = MagicMock()
        mock_manager.create_plugin_template.return_value = True
        mock_get_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(app, ["create", "new_plugin", "--category", "general"])
        
        assert result.exit_code == 0


class TestPluginReload:
    """Test plugin reload command"""
    
    @patch('cli.plugin.get_output')
    @patch('cli.plugin.get_plugin_manager')
    def test_reload_plugins(self, mock_get_manager, mock_get_output):
        """Test reloading plugins"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_manager = MagicMock()
        mock_manager.load_plugins.return_value = {
            'successfully_loaded': 5,
            'failed_to_load': 0
        }
        mock_get_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(app, ["reload"])
        
        assert result.exit_code == 0
        mock_manager.load_plugins.assert_called_once()

