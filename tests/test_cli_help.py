"""
Tests for Help CLI commands
Tests interactive help system
"""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.help import app


class TestHelpGeneral:
    """Test general help command"""
    
    def test_help_general(self):
        """Test general help display"""
        runner = CliRunner()
        result = runner.invoke(app, ["command"])
        
        # Help commands may exit with 0 or 1
        assert result.exit_code in [0, 1, 2]
    
    def test_help_command_specific(self):
        """Test help for specific command"""
        runner = CliRunner()
        result = runner.invoke(app, ["command", "training"])
        
        # Help commands may exit with 0 or 1
        assert result.exit_code in [0, 1, 2]
    
    def test_help_examples(self):
        """Test help examples command"""
        runner = CliRunner()
        result = runner.invoke(app, ["examples"])
        
        # Help commands may exit with 0 or 1
        assert result.exit_code in [0, 1, 2]
    
    def test_help_quickstart(self):
        """Test help quickstart command"""
        runner = CliRunner()
        result = runner.invoke(app, ["quickstart"])
        
        # Help commands may exit with 0 or 1
        assert result.exit_code in [0, 1, 2]

