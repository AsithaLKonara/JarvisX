"""
Test Suite for Phase 1: Command Center Hub
Tests all Command Center components
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

# Add command_center to path
sys.path.insert(0, str(Path(__file__).parent.parent / "command_center"))

from hub import CommandCenterHub, SystemStatus
from mode_orchestrator import ModeOrchestrator, ModeStatus
from task_manager import TaskManager, TaskStatus, TaskPriority
from voice_control import VoiceControl
from report_generator import ReportGenerator

class TestCommandCenterHub(unittest.TestCase):
    """Test Command Center Hub functionality"""
    
    def setUp(self):
        self.hub = CommandCenterHub()
    
    def test_initialization(self):
        """Test hub initialization"""
        self.assertEqual(self.hub.status, SystemStatus.INITIALIZING)
        self.assertIsNone(self.hub.active_mode)
        self.assertEqual(len(self.hub.tasks), 0)
    
    def test_initialize(self):
        """Test hub initialization process"""
        result = self.hub.initialize()
        self.assertTrue(result)
        self.assertEqual(self.hub.status, SystemStatus.READY)
    
    def test_create_task(self):
        """Test task creation"""
        task_id = self.hub.create_task("Test Task", "engineer", 2)
        self.assertIsNotNone(task_id)
        self.assertEqual(len(self.hub.tasks), 1)
        self.assertEqual(self.hub.tasks[0].name, "Test Task")
        self.assertEqual(self.hub.tasks[0].mode, "engineer")
    
    def test_switch_mode(self):
        """Test mode switching"""
        self.hub.initialize()
        result = self.hub.switch_mode("engineer")
        self.assertTrue(result)
        self.assertEqual(self.hub.active_mode, "engineer")
        
        # Test invalid mode
        result = self.hub.switch_mode("invalid")
        self.assertFalse(result)
    
    def test_get_status(self):
        """Test status retrieval"""
        self.hub.initialize()
        status = self.hub.get_status()
        self.assertIn('status', status)
        self.assertIn('active_mode', status)
        self.assertIn('uptime', status)
        self.assertIn('tasks_count', status)
        self.assertIn('available_modes', status)

class TestModeOrchestrator(unittest.TestCase):
    """Test Mode Orchestrator functionality"""
    
    def setUp(self):
        self.orchestrator = ModeOrchestrator()
    
    def test_initialization(self):
        """Test orchestrator initialization"""
        self.assertIsNone(self.orchestrator.current_mode)
        self.assertEqual(len(self.orchestrator.modes), 6)
    
    def test_activate_mode(self):
        """Test mode activation"""
        result = self.orchestrator.activate_mode("engineer")
        self.assertTrue(result)
        self.assertEqual(self.orchestrator.current_mode, "engineer")
        self.assertEqual(self.orchestrator.modes["engineer"].status, ModeStatus.ACTIVE)
    
    def test_get_mode_status(self):
        """Test mode status retrieval"""
        self.orchestrator.activate_mode("designer")
        status = self.orchestrator.get_mode_status("designer")
        self.assertEqual(status, ModeStatus.ACTIVE)
        
        # Test invalid mode
        status = self.orchestrator.get_mode_status("invalid")
        self.assertIsNone(status)
    
    def test_is_mode_available(self):
        """Test mode availability check"""
        self.assertTrue(self.orchestrator.is_mode_available("engineer"))
        self.assertFalse(self.orchestrator.is_mode_available("invalid"))

class TestTaskManager(unittest.TestCase):
    """Test Task Manager functionality"""
    
    def setUp(self):
        self.task_manager = TaskManager()
    
    def test_initialization(self):
        """Test task manager initialization"""
        self.assertEqual(len(self.task_manager.tasks), 0)
        self.assertEqual(self.task_manager.task_counter, 0)
    
    def test_create_task(self):
        """Test task creation"""
        task_id = self.task_manager.create_task("Test Task", "engineer", TaskPriority.HIGH)
        self.assertIsNotNone(task_id)
        self.assertEqual(len(self.task_manager.tasks), 1)
        
        task = self.task_manager.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.mode, "engineer")
        self.assertEqual(task.priority, TaskPriority.HIGH)
    
    def test_start_task(self):
        """Test task starting"""
        task_id = self.task_manager.create_task("Test Task", "engineer")
        result = self.task_manager.start_task(task_id)
        self.assertTrue(result)
        
        task = self.task_manager.get_task(task_id)
        self.assertEqual(task.status, TaskStatus.RUNNING)
        self.assertIsNotNone(task.started_at)
    
    def test_complete_task(self):
        """Test task completion"""
        task_id = self.task_manager.create_task("Test Task", "engineer")
        self.task_manager.start_task(task_id)
        result = self.task_manager.complete_task(task_id)
        self.assertTrue(result)
        
        task = self.task_manager.get_task(task_id)
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.completed_at)
    
    def test_fail_task(self):
        """Test task failure"""
        task_id = self.task_manager.create_task("Test Task", "engineer")
        result = self.task_manager.fail_task(task_id, "Test error")
        self.assertTrue(result)
        
        task = self.task_manager.get_task(task_id)
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertEqual(task.error_message, "Test error")
    
    def test_get_tasks_by_mode(self):
        """Test getting tasks by mode"""
        self.task_manager.create_task("Task 1", "engineer")
        self.task_manager.create_task("Task 2", "designer")
        self.task_manager.create_task("Task 3", "engineer")
        
        engineer_tasks = self.task_manager.get_tasks_by_mode("engineer")
        self.assertEqual(len(engineer_tasks), 2)
        
        designer_tasks = self.task_manager.get_tasks_by_mode("designer")
        self.assertEqual(len(designer_tasks), 1)
    
    def test_get_task_stats(self):
        """Test task statistics"""
        self.task_manager.create_task("Task 1", "engineer")
        self.task_manager.create_task("Task 2", "designer")
        
        stats = self.task_manager.get_task_stats()
        self.assertIn('pending', stats)
        self.assertIn('running', stats)
        self.assertIn('completed', stats)
        self.assertIn('failed', stats)
        self.assertIn('cancelled', stats)

class TestVoiceControl(unittest.TestCase):
    """Test Voice Control functionality"""
    
    def setUp(self):
        self.voice_control = VoiceControl()
    
    def test_initialization(self):
        """Test voice control initialization"""
        self.assertFalse(self.voice_control.is_listening)
        self.assertEqual(len(self.voice_control.callbacks), 0)
    
    def test_register_callback(self):
        """Test callback registration"""
        def test_callback(text):
            pass
        
        self.voice_control.register_callback("test", test_callback)
        self.assertIn("test", self.voice_control.callbacks)
    
    def test_process_voice_command(self):
        """Test voice command processing"""
        callback_called = False
        
        def test_callback(text):
            nonlocal callback_called
            callback_called = True
        
        self.voice_control.register_callback("test", test_callback)
        result = self.voice_control.process_voice_command("test command")
        self.assertTrue(result)
        self.assertTrue(callback_called)

class TestReportGenerator(unittest.TestCase):
    """Test Report Generator functionality"""
    
    def setUp(self):
        self.report_generator = ReportGenerator()
    
    def test_initialization(self):
        """Test report generator initialization"""
        self.assertTrue(self.report_generator.log_dir.exists())
    
    def test_generate_system_status_report(self):
        """Test system status report generation"""
        hub_status = {
            'status': 'ready',
            'active_mode': 'engineer',
            'uptime': '0:01:00'
        }
        task_stats = {'pending': 2, 'running': 1, 'completed': 5}
        
        report = self.report_generator.generate_system_status_report(hub_status, task_stats)
        self.assertIn('timestamp', report)
        self.assertIn('system_status', report)
        self.assertIn('task_statistics', report)
        self.assertEqual(report['total_tasks'], 8)
    
    def test_generate_daily_report(self):
        """Test daily report generation"""
        report = self.report_generator.generate_daily_report()
        self.assertIn('date', report)
        self.assertIn('generated_at', report)
        self.assertIn('summary', report)
        self.assertIn('recommendations', report)
    
    def test_generate_performance_report(self):
        """Test performance report generation"""
        metrics = {
            'cpu_usage': 85,
            'memory_usage': 70,
            'disk_usage': 60
        }
        
        report = self.report_generator.generate_performance_report(metrics)
        self.assertIn('timestamp', report)
        self.assertIn('performance_metrics', report)
        self.assertIn('analysis', report)
        self.assertIn('recommendations', report)
    
    def test_save_report(self):
        """Test report saving"""
        report = {'test': 'data', 'timestamp': datetime.now().isoformat()}
        result = self.report_generator.save_report(report, 'test_report.json')
        self.assertTrue(result)
        
        # Clean up
        test_file = self.report_generator.log_dir / 'test_report.json'
        if test_file.exists():
            test_file.unlink()

if __name__ == '__main__':
    unittest.main()



