"""
Test suite for CLI input validation
"""

import pytest
from cli.utils import validate_path, validate_url, validate_email, validate_json


class TestPathValidation:
    """Test path validation"""
    
    def test_valid_path(self):
        """Test valid path validation"""
        assert validate_path("/tmp/test") is True
        assert validate_path("./test") is True
        assert validate_path("test") is True
    
    def test_invalid_path(self):
        """Test invalid path validation"""
        # Empty path
        assert validate_path("") is False
        # Path with invalid characters (on Windows)
        # This would need platform-specific testing


class TestURLValidation:
    """Test URL validation"""
    
    def test_valid_url(self):
        """Test valid URL validation"""
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com") is True
        assert validate_url("https://example.com:8080") is True
    
    def test_invalid_url(self):
        """Test invalid URL validation"""
        assert validate_url("not-a-url") is False
        assert validate_url("") is False
        assert validate_url("ftp://example.com") is False  # Only http/https allowed


class TestEmailValidation:
    """Test email validation"""
    
    def test_valid_email(self):
        """Test valid email validation"""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@example.co.uk") is True
    
    def test_invalid_email(self):
        """Test invalid email validation"""
        assert validate_email("not-an-email") is False
        assert validate_email("@example.com") is False
        assert validate_email("test@") is False


class TestJSONValidation:
    """Test JSON validation"""
    
    def test_valid_json(self):
        """Test valid JSON validation"""
        assert validate_json('{"key": "value"}') is True
        assert validate_json('[1, 2, 3]') is True
    
    def test_invalid_json(self):
        """Test invalid JSON validation"""
        assert validate_json("not json") is False
        assert validate_json("{key: value}") is False
        assert validate_json("") is False

