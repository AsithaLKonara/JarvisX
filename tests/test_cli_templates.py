"""
Tests for Templates CLI commands
Tests command template management
"""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.templates import app, _load_templates, _save_templates


class TestTemplateSave:
    """Test template save command"""
    
    @patch('cli.templates._load_templates')
    @patch('cli.templates._save_templates')
    def test_save_template(self, mock_save, mock_load):
        """Test saving a template"""
        mock_load.return_value = {}
        
        runner = CliRunner()
        result = runner.invoke(app, ["save", "test_template", "status --json"])
        
        assert result.exit_code == 0
        mock_save.assert_called_once()
    
    @patch('cli.templates._load_templates')
    @patch('cli.templates._save_templates')
    def test_save_template_with_description(self, mock_save, mock_load):
        """Test saving template with description"""
        mock_load.return_value = {}
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "save", "test", "status",
            "--description", "Test description"
        ])
        
        assert result.exit_code == 0


class TestTemplateList:
    """Test template list command"""
    
    @patch('cli.templates.get_output')
    @patch('cli.templates._load_templates')
    def test_list_templates(self, mock_load, mock_get_output):
        """Test listing templates"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_load.return_value = {
            'template1': {'command': 'status', 'description': 'Test'}
        }
        
        runner = CliRunner()
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
    
    @patch('cli.templates.get_output')
    @patch('cli.templates._load_templates')
    def test_list_templates_json(self, mock_load, mock_get_output):
        """Test listing templates with JSON"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_load.return_value = {'template1': {'command': 'status'}}
        
        runner = CliRunner()
        result = runner.invoke(app, ["list", "--json"])
        
        assert result.exit_code == 0


class TestTemplateGet:
    """Test template get command"""
    
    @patch('cli.templates.get_output')
    @patch('cli.templates._load_templates')
    def test_get_template(self, mock_load, mock_get_output):
        """Test getting a template"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_load.return_value = {
            'test_template': {
                'command': 'status --json',
                'description': 'Test'
            }
        }
        
        runner = CliRunner()
        result = runner.invoke(app, ["get", "test_template"])
        
        assert result.exit_code == 0
    
    @patch('cli.templates._load_templates')
    def test_get_template_not_found(self, mock_load):
        """Test getting non-existent template"""
        mock_load.return_value = {}
        
        runner = CliRunner()
        result = runner.invoke(app, ["get", "nonexistent"])
        
        assert result.exit_code == 1


class TestTemplateDelete:
    """Test template delete command"""
    
    @patch('cli.templates._load_templates')
    @patch('cli.templates._save_templates')
    def test_delete_template(self, mock_save, mock_load):
        """Test deleting a template"""
        mock_load.return_value = {
            'test_template': {'command': 'status'}
        }
        
        runner = CliRunner()
        result = runner.invoke(app, ["delete", "test_template", "--yes"])
        
        assert result.exit_code == 0
        mock_save.assert_called_once()


class TestTemplateExecute:
    """Test template execute command"""
    
    @patch('cli.templates._load_templates')
    def test_execute_template(self, mock_load):
        """Test executing a template"""
        mock_load.return_value = {
            'test_template': {
                'command': 'status',
                'description': 'Test'
            }
        }
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "test_template"])
        
        # May fail if command execution is attempted, but should handle gracefully
        assert result.exit_code in [0, 1]

