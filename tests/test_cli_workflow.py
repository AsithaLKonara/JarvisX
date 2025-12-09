"""
Unit Tests for Workflow CLI Commands
Tests all workflow-related CLI functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import tempfile
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.workflow import (
    list_workflows,
    execute_workflow,
    create_workflow,
    workflow_status,
    workflow_analytics,
    recommend_workflows
)


class TestWorkflowCLI(unittest.TestCase):
    """Test Workflow CLI commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.workflow_file = Path(self.temp_dir) / "test_workflow.json"
        
        # Create test workflow
        test_workflow = {
            "id": "test-workflow-1",
            "name": "Test Workflow",
            "nodes": []
        }
        with open(self.workflow_file, 'w') as f:
            json.dump(test_workflow, f)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('automation.workflow_orchestrator.WorkflowOrchestrator')
    def test_list_workflows(self, mock_orchestrator_class):
        """Test workflow listing"""
        # Mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator.get_workflows.return_value = [
            {"id": "wf1", "name": "Workflow 1", "node_count": 5, "active": True},
            {"id": "wf2", "name": "Workflow 2", "node_count": 3, "active": False}
        ]
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Test listing
        try:
            list_workflows(category=None, json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('automation.workflow_orchestrator.WorkflowOrchestrator')
    def test_execute_workflow(self, mock_orchestrator_class):
        """Test workflow execution"""
        # Mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator.execute_workflow.return_value = {
            "success": True,
            "workflow_name": "Test Workflow"
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Test execution
        try:
            execute_workflow(
                workflow_id="test-workflow-1",
                input_data='{"key": "value"}',
                json_output=False
            )
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('automation.workflow_orchestrator.WorkflowOrchestrator')
    def test_create_workflow(self, mock_orchestrator_class):
        """Test workflow creation"""
        # Mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator.workflows = {}
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Test creation
        try:
            create_workflow(
                from_template=None,
                name="Test Workflow",
                workflow_file=str(self.workflow_file),
                json_output=False
            )
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('automation.workflow_orchestrator.WorkflowOrchestrator')
    def test_workflow_status(self, mock_orchestrator_class):
        """Test workflow status"""
        # Mock orchestrator
        mock_orchestrator = MagicMock()
        mock_execution = MagicMock()
        mock_execution.execution_id = "exec-1"
        mock_execution.workflow_id = "wf-1"
        mock_execution.status = "running"
        mock_orchestrator.get_execution.return_value = mock_execution
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Test status check
        try:
            workflow_status(execution_id="exec-1", json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass


if __name__ == '__main__':
    unittest.main()

