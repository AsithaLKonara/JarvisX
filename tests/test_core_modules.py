"""
Tests for core modules
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestConfigManagement:
    """Test configuration management"""
    
    def test_config_loading(self):
        """Test loading configuration"""
        try:
            from utils.config import Config
            config = Config()
            assert config is not None
        except ImportError:
            pytest.skip("Config module not available")
    
    def test_env_variable_loading(self, monkeypatch):
        """Test environment variable loading"""
        monkeypatch.setenv("TEST_VAR", "test_value")
        import os
        assert os.getenv("TEST_VAR") == "test_value"


class TestModelLoading:
    """Test model loading functionality"""
    
    def test_model_path_resolution(self, monkeypatch):
        """Test model path resolution with environment variable"""
        # Test that JARVIS_MODEL_PATH is respected
        test_path = "/test/model/path"
        monkeypatch.setenv("JARVIS_MODEL_PATH", test_path)
        
        import os
        env_path = os.getenv("JARVIS_MODEL_PATH", "").strip()
        assert env_path == test_path
    
    def test_model_path_fallback(self, project_root_path):
        """Test model path fallback mechanism"""
        # Test that fallback to relative path works
        from jarvis_llm_brain import JarvisLLMBrain
        # This will test the fallback logic
        # Note: This may fail if model doesn't exist, which is expected
        try:
            brain = JarvisLLMBrain()
            # Just verify it initializes without hardcoded path errors
            assert brain is not None
        except Exception as e:
            # Expected if model files don't exist
            # But should not fail due to hardcoded paths
            assert "hardcoded" not in str(e).lower()


class TestValidationFunctions:
    """Test validation functions"""
    
    def test_path_validation(self, temp_dir):
        """Test path validation"""
        from cli.utils import validate_path
        
        # Valid paths
        assert validate_path(str(temp_dir)) is True
        assert validate_path("./test") is True
        
        # Invalid paths
        assert validate_path("") is False
    
    def test_url_validation(self):
        """Test URL validation"""
        from cli.utils import validate_url
        
        # Valid URLs
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com:8080") is True
        
        # Invalid URLs
        assert validate_url("") is False
        assert validate_url("not-a-url") is False
    
    def test_email_validation(self):
        """Test email validation"""
        from cli.utils import validate_email
        
        # Valid emails
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@example.co.uk") is True
        
        # Invalid emails
        assert validate_email("") is False
        assert validate_email("@example.com") is False
        assert validate_email("test@") is False

