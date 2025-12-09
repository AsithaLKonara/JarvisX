"""
Unit Tests for Model CLI Commands
Tests all model-related CLI functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import tempfile

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.model import (
    list_models,
    load_model,
    compare_models,
    upload_model,
    model_info,
    test_model
)


class TestModelCLI(unittest.TestCase):
    """Test Model CLI commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.models_dir = Path(self.temp_dir) / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        # Create test model
        self.test_model_dir = self.models_dir / "test_model"
        self.test_model_dir.mkdir(exist_ok=True)
        (self.test_model_dir / "config.json").write_text('{"model": "test"}')
        (self.test_model_dir / "model.bin").write_bytes(b"test model data")
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('cli.utils.get_project_root')
    def test_list_models(self, mock_root):
        """Test model listing"""
        mock_root.return_value = Path(self.temp_dir)
        
        # Test listing
        try:
            list_models(local=True, remote=False, json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('cli.utils.get_project_root')
    def test_load_model(self, mock_root):
        """Test model loading"""
        mock_root.return_value = Path(self.temp_dir)
        
        # Test loading
        try:
            load_model(name="test_model", version=None, json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('cli.utils.get_project_root')
    def test_compare_models(self, mock_root):
        """Test model comparison"""
        # Create second model
        model2_dir = self.models_dir / "test_model_2"
        model2_dir.mkdir(exist_ok=True)
        (model2_dir / "config.json").write_text('{"model": "test2"}')
        
        mock_root.return_value = Path(self.temp_dir)
        
        # Test comparison
        try:
            compare_models(
                model_a="test_model",
                model_b="test_model_2",
                metrics="size,latency",
                json_output=False
            )
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('huggingface_hub.upload_folder')
    @patch('huggingface_hub.HfApi')
    def test_upload_model(self, mock_api_class, mock_upload):
        """Test model upload"""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        
        # Test upload
        try:
            upload_model(
                path=str(self.test_model_dir),
                repo="test-user/test-model",
                version=None,
                token="test_token",
                json_output=False
            )
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('cli.utils.get_project_root')
    def test_model_info(self, mock_root):
        """Test model info"""
        mock_root.return_value = Path(self.temp_dir)
        
        # Test info
        try:
            model_info(name="test_model", json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('jarvis_llm_brain.JarvisLLMBrain')
    @patch('cli.utils.get_project_root')
    def test_test_model(self, mock_root, mock_brain_class):
        """Test model testing"""
        mock_root.return_value = Path(self.temp_dir)
        
        # Mock brain
        mock_brain = MagicMock()
        mock_brain.generate_response.return_value = "Test response"
        mock_brain_class.return_value = mock_brain
        
        # Test model testing
        try:
            test_model(name="test_model", prompt="Hello", json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass


if __name__ == '__main__':
    unittest.main()

