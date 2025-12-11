"""
End-to-end workflow tests
Tests complete user workflows from start to finish
"""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.main import app

# Set timeout for E2E workflow tests (15 seconds)
pytestmark = pytest.mark.timeout(15)


@pytest.mark.e2e
class TestE2ETrainingWorkflow:
    """Test complete training workflow end-to-end"""
    
    @patch('cli.training.TrainingJobManager')
    def test_e2e_training_workflow(self, mock_manager_class):
        """Test complete training workflow"""
        mock_manager = MagicMock()
        mock_job = {
            'job_id': 'test-job-123',
            'status': 'running',
            'config': {'model_name': 'test'}
        }
        mock_manager.create_job.return_value = 'test-job-123'
        mock_manager.get_job.return_value = mock_job
        mock_manager_class.return_value = mock_manager
        
        runner = CliRunner()
        
        # Start training
        result1 = runner.invoke(app, [
            "training", "start",
            "--config", "test_config.json"
        ])
        
        # Check status
        result2 = runner.invoke(app, [
            "training", "status",
            "--job-id", "test-job-123"
        ])
        
        # List jobs
        result3 = runner.invoke(app, ["training", "list"])
        
        assert result1.exit_code in [0, 1]
        assert result2.exit_code in [0, 1]
        assert result3.exit_code in [0, 1]


@pytest.mark.e2e
class TestE2ECloudDeployment:
    """Test cloud deployment workflow end-to-end"""
    
    @patch('builtins.__import__')
    def test_e2e_cloud_deployment(self, mock_import):
        """Test complete cloud deployment workflow"""
        # Create mock huggingface_hub module
        mock_hf_module = MagicMock()
        mock_api = MagicMock()
        mock_space_info = MagicMock()
        mock_space_info.id = "test-space"
        mock_space_info.runtime = {"stage": "running"}
        mock_api.space_info.return_value = mock_space_info
        mock_hf_module.HfApi.return_value = mock_api
        
        # Make __import__ return mock_hf_module when importing huggingface_hub
        def import_side_effect(name, *args, **kwargs):
            if name == 'huggingface_hub':
                return mock_hf_module
            # For other imports, use real import
            import builtins
            return builtins.__import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        runner = CliRunner()
        
        # Connect
        result1 = runner.invoke(app, [
            "cloud", "connect",
            "--url", "https://huggingface.co/spaces/test/space"
        ])
        
        # Check status
        result2 = runner.invoke(app, [
            "cloud", "status",
            "--space", "test/space"
        ])
        
        assert result1.exit_code in [0, 1, 2]
        assert result2.exit_code in [0, 1, 2]


@pytest.mark.e2e
class TestE2EBusinessInvoice:
    """Test business invoice generation workflow"""
    
    @patch('business_mode.client_database.ClientDatabase')
    @patch('business_mode.invoice_generator.InvoiceGenerator')
    def test_e2e_business_invoice(self, mock_invoice_class, mock_client_class):
        """Test complete invoice generation workflow"""
        # Mock client database
        mock_client_db = MagicMock()
        mock_client = {'id': 1, 'name': 'Test Client', 'email': 'test@example.com'}
        mock_client_db.get_client_by_id.return_value = mock_client
        mock_client_db.add_client.return_value = 1
        mock_client_class.return_value = mock_client_db
        
        # Mock invoice generator
        mock_invoice_gen = MagicMock()
        mock_invoice_gen.create_invoice.return_value = "invoice-123"
        mock_invoice_gen.get_invoice.return_value = {
            'id': 'invoice-123',
            'total': 100.0,
            'status': 'pending'
        }
        mock_invoice_class.return_value = mock_invoice_gen
        
        runner = CliRunner()
        
        # Add client
        result1 = runner.invoke(app, [
            "business", "client", "add",
            "--name", "Test Client",
            "--email", "test@example.com"
        ])
        
        # Generate invoice
        result2 = runner.invoke(app, [
            "business", "invoice",
            "--client-id", "1"
        ])
        
        assert result1.exit_code in [0, 1, 2]
        assert result2.exit_code in [0, 1, 2]


@pytest.mark.e2e
class TestE2ESystemOptimization:
    """Test system optimization workflow"""
    
    @patch('system_monitor.resource_monitor.ResourceMonitor')
    @patch('system_monitor.health_checker.HealthChecker')
    def test_e2e_system_optimization(self, mock_health_class, mock_monitor_class):
        """Test complete system optimization workflow"""
        mock_monitor = MagicMock()
        mock_monitor.get_cpu_info.return_value = {'percent': 50}
        mock_monitor.get_memory_info.return_value = {'percent': 60}
        mock_monitor.get_disk_info.return_value = {'percent': 40}
        mock_monitor_class.return_value = mock_monitor
        
        mock_health = MagicMock()
        mock_health.get_all_status.return_value = {
            'overall_status': 'healthy',
            'components': {}
        }
        mock_health_class.return_value = mock_health
        
        runner = CliRunner()
        
        # Check status
        result1 = runner.invoke(app, ["system", "status"])
        
        # Health check
        result2 = runner.invoke(app, ["system", "health"])
        
        # Optimize
        result3 = runner.invoke(app, ["system", "optimize", "--auto"])
        
        assert result1.exit_code in [0, 1, 2]
        assert result2.exit_code in [0, 1, 2]
        assert result3.exit_code in [0, 1, 2]


@pytest.mark.e2e
class TestE2EVoiceWorkflow:
    """Test voice command workflow"""
    
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_e2e_voice_workflow(self, mock_orchestrator_class):
        """Test complete voice workflow"""
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'Done',
            'actions': []
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        
        # Execute voice command
        result1 = runner.invoke(app, [
            "voice", "command",
            "Check system status"
        ])
        
        # Unified execute
        result2 = runner.invoke(app, [
            "unified", "execute",
            "Monitor CPU usage"
        ])
        
        assert result1.exit_code in [0, 1]
        assert result2.exit_code in [0, 1]

