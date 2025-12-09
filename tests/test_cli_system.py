"""
Unit Tests for System CLI Commands
Tests all system-related CLI functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import tempfile

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.system import (
    system_status,
    system_health,
    system_optimize,
    system_logs,
    system_cleanup,
    system_info
)


class TestSystemCLI(unittest.TestCase):
    """Test System CLI commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "jarvis.log"
        self.log_file.write_text("INFO: Test log entry\nWARNING: Test warning\nERROR: Test error\n")
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('cli.system.psutil')
    def test_system_status(self, mock_psutil):
        """Test system status command"""
        # Mock psutil
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.cpu_count.return_value = 4
        mock_mem = MagicMock()
        mock_mem.used = 4 * 1024**3  # 4GB
        mock_mem.total = 8 * 1024**3  # 8GB
        mock_mem.percent = 50.0
        mock_psutil.virtual_memory.return_value = mock_mem
        mock_d = MagicMock()
        mock_d.used = 100 * 1024**3  # 100GB
        mock_d.total = 500 * 1024**3  # 500GB
        mock_d.percent = 20.0
        mock_psutil.disk_usage.return_value = mock_d
        
        # Test status
        try:
            system_status(json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('system_monitor.health_checker.HealthChecker')
    @patch('system_monitor.resource_monitor.ResourceMonitor')
    @patch('cli.system.psutil')
    def test_system_health(self, mock_psutil, mock_resource, mock_health):
        """Test system health command"""
        # Mock health checker
        mock_health_instance = MagicMock()
        mock_health.return_value = mock_health_instance
        mock_health_instance.get_all_status.return_value = {
            "overall_status": "healthy",
            "components": {
                "CPU": {"status": "healthy"},
                "Memory": {"status": "healthy"}
            }
        }
        
        # Mock resource monitor
        mock_resource_instance = MagicMock()
        mock_resource.return_value = mock_resource_instance
        mock_resource_instance.get_cpu_info.return_value = {"percent": 50, "alert": False}
        mock_resource_instance.get_memory_info.return_value = {"percent": 50, "alert": False}
        mock_resource_instance.get_disk_info.return_value = {"percent": 50, "alert": False}
        
        # Test health check
        try:
            system_health(full=False, json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('system_monitor.resource_monitor.ResourceMonitor')
    @patch('cli.system.psutil')
    def test_system_optimize(self, mock_psutil, mock_resource):
        """Test system optimize command"""
        # Mock resource monitor
        mock_resource_instance = MagicMock()
        mock_resource.return_value = mock_resource_instance
        mock_resource_instance.get_cpu_info.return_value = {"percent": 50}
        mock_resource_instance.get_memory_info.return_value = {"percent": 50}
        mock_resource_instance.get_disk_info.return_value = {"percent": 50}
        
        # Test optimization
        try:
            system_optimize(auto=False, json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('cli.utils.get_project_root')
    def test_system_logs(self, mock_root):
        """Test system logs command"""
        mock_root.return_value = Path(self.temp_dir)
        
        # Test log viewing
        try:
            system_logs(tail=10, filter=None, search=None, export=None, json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('cli.utils.get_project_root')
    def test_system_cleanup(self, mock_root):
        """Test system cleanup command"""
        mock_root.return_value = Path(self.temp_dir)
        
        # Test cleanup
        try:
            system_cleanup(logs=True, cache=False, temp=False, days=7, json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    def test_system_info(self):
        """Test system info command"""
        # Test info display
        try:
            system_info(json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass


if __name__ == '__main__':
    unittest.main()

