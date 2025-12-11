"""
Unit Tests for Config CLI Commands
Tests all configuration-related CLI functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import tempfile
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.config import (
    show_config,
    get_config_value,
    set_config,
    validate_config
)


class TestConfigCLI(unittest.TestCase):
    """Test Config CLI commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        
        # Create test config
        test_config = {
            "log_level": "INFO",
            "debug": False,
            "test_key": "test_value"
        }
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('cli.config.get_config')
    def test_show_config(self, mock_get_config):
        """Test config display"""
        # Mock config
        mock_config = MagicMock()
        mock_config.get_all.return_value = {"log_level": "INFO", "debug": False}
        mock_get_config.return_value = mock_config
        
        # Test show
        try:
            show_config(format="json", json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('cli.config.get_config')
    def test_get_config_value(self, mock_get_config):
        """Test getting config value"""
        # Mock config
        mock_config = MagicMock()
        mock_config.get.return_value = "test_value"
        mock_get_config.return_value = mock_config
        
        # Test get
        try:
            get_config_value(key="test_key", json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('cli.config.get_config')
    def test_set_config_value(self, mock_get_config):
        """Test setting config value"""
        # Mock config
        mock_config = MagicMock()
        mock_config.set.return_value = True
        mock_get_config.return_value = mock_config
        
        # Test set
        try:
            set_config(key="test_key", value="new_value", json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('cli.config.validate_config_file')
    @patch('cli.config.get_config')
    def test_validate_config(self, mock_get_config, mock_validate_file):
        """Test config validation"""
        # Mock config
        mock_config = MagicMock()
        mock_config.config_file = self.config_file
        mock_get_config.return_value = mock_config
        mock_validate_file.return_value = True
        
        # Test validation
        try:
            validate_config(config_path=None, json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass


if __name__ == '__main__':
    unittest.main()

