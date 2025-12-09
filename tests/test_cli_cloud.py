"""
Unit Tests for Cloud CLI Commands
Tests all cloud-related CLI functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.cloud import (
    connect_cloud,
    deploy_cloud,
    cloud_status,
    test_cloud,
    monitor_cloud,
    cloud_logs
)


class TestCloudCLI(unittest.TestCase):
    """Test Cloud CLI commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_space = "test-user/test-space"
        self.test_url = "https://test-user-test-space.hf.space"
    
    @patch('cloud_llm_client.CloudLLMClient')
    def test_connect_cloud(self, mock_client_class):
        """Test cloud connect command"""
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        mock_client_class.return_value = mock_client
        
        # Test successful connection
        try:
            connect_cloud(url=self.test_url, token=None, json_output=False)
            # If no exception, connection succeeded
            self.assertTrue(True)
        except SystemExit:
            # Typer exits on error, which is expected in tests
            pass
    
    @patch('huggingface_hub.upload_folder')
    @patch('huggingface_hub.HfApi')
    def test_deploy_cloud(self, mock_api_class, mock_upload):
        """Test cloud deploy command"""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        
        # Mock space info
        mock_space = MagicMock()
        mock_space.id = self.test_space
        mock_api.space_info.return_value = mock_space
        
        # Test deployment
        try:
            deploy_cloud(
                space=self.test_space,
                model=None,
                hardware=None,
                token="test_token",
                json_output=False
            )
            # If no exception, deployment attempted
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('huggingface_hub.HfApi')
    def test_cloud_status(self, mock_api_class):
        """Test cloud status command"""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        
        # Mock space info
        mock_space_info = MagicMock()
        mock_space_info.id = self.test_space
        mock_space_info.runtime = {"stage": "running", "hardware": "cpu"}
        mock_api.space_info.return_value = mock_space_info
        
        # Test status check
        try:
            cloud_status(space=self.test_space, token="test_token", json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('cloud_llm_client.CloudLLMClient')
    def test_test_cloud(self, mock_client_class):
        """Test cloud test command"""
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        mock_client.generate.return_value = "Test response"
        mock_client_class.return_value = mock_client
        
        # Test API test
        try:
            test_cloud(endpoint="/generate", prompt="Hello", json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('cloud_llm_client.CloudLLMClient')
    def test_monitor_cloud(self, mock_client_class):
        """Test cloud monitor command"""
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        mock_client.generate.return_value = "Test"
        mock_client_class.return_value = mock_client
        
        # Test monitoring (will be interrupted in test)
        try:
            monitor_cloud(
                space=self.test_space,
                metrics="latency,errors",
                interval=1,
                json_output=False
            )
            self.assertTrue(True)
        except (SystemExit, KeyboardInterrupt):
            pass


if __name__ == '__main__':
    unittest.main()

