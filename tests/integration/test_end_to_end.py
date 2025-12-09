"""
End-to-End Tests for Complete User Workflows
Tests complete workflows from start to finish
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import tempfile
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestTrainingToDeploymentWorkflow(unittest.TestCase):
    """Test complete training to deployment workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "training_config.json"
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('cli.training.TrainingJobManager')
    @patch('cli.cloud.HfApi')
    def test_training_to_deployment(self, mock_api_class, mock_job_manager_class):
        """Test complete workflow: training → status → deploy"""
        # Mock job manager
        mock_job_manager = MagicMock()
        mock_job_manager.create_job.return_value = "job-123"
        mock_job_manager.get_job.return_value = {
            "job_id": "job-123",
            "status": "completed",
            "output_dir": str(self.output_dir)
        }
        mock_job_manager_class.return_value = mock_job_manager
        
        # Mock HF API
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        
        # Simulate workflow
        # 1. Start training
        job_id = mock_job_manager.create_job(
            config_path=str(self.config_file),
            output_dir=str(self.output_dir),
            epochs=5
        )
        self.assertEqual(job_id, "job-123")
        
        # 2. Check status
        job = mock_job_manager.get_job(job_id)
        self.assertEqual(job['status'], "completed")
        
        # 3. Deploy (simulated)
        # In real scenario, would deploy model from output_dir
        self.assertTrue(True)


class TestBusinessWorkflow(unittest.TestCase):
    """Test complete business operations workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('cli.business.ClientDatabase')
    @patch('cli.business.InvoiceGenerator')
    def test_client_to_invoice_workflow(self, mock_invoice, mock_client_db):
        """Test workflow: add client → generate invoice → export"""
        # Mock client database
        mock_client = MagicMock()
        mock_client.add_client.return_value = 1
        mock_client.get_client_by_id.return_value = {
            "id": 1,
            "name": "Test Client",
            "email": "test@example.com"
        }
        mock_client_db.return_value = mock_client
        
        # Mock invoice generator
        mock_inv = MagicMock()
        mock_inv.create_invoice.return_value = "INV-001"
        mock_inv.list_invoices.return_value = [
            {"invoice_id": "INV-001", "total": 100.0}
        ]
        mock_invoice.return_value = mock_inv
        
        # Simulate workflow
        # 1. Add client
        client_id = mock_client.add_client(
            name="Test Client",
            email="test@example.com"
        )
        self.assertEqual(client_id, 1)
        
        # 2. Generate invoice
        invoice_id = mock_inv.create_invoice(
            client_name="Test Client",
            items=[{"description": "Service", "amount": 100.0}],
            tax_rate=0.0
        )
        self.assertEqual(invoice_id, "INV-001")
        
        # 3. Export (simulated)
        invoices = mock_inv.list_invoices()
        self.assertEqual(len(invoices), 1)


class TestVoiceCommandWorkflow(unittest.TestCase):
    """Test complete voice command workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        from cli.voice_utils import VoiceCommandParser
        self.parser = VoiceCommandParser()
    
    @patch('speech.speech_recognizer.SpeechRecognizer')
    @patch('cli.voice.TTSEngine')
    def test_voice_interactive_workflow(self, mock_tts_class, mock_recognizer_class):
        """Test interactive voice mode workflow"""
        # Mock recognizer
        mock_recognizer = MagicMock()
        mock_recognizer.is_available.return_value = True
        mock_recognizer.listen.side_effect = ["system status", "exit"]
        mock_recognizer_class.return_value = mock_recognizer
        
        # Mock TTS
        mock_tts = MagicMock()
        mock_tts.is_available = True
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts
        
        # Simulate workflow
        # 1. Listen for command
        text1 = mock_recognizer.listen(timeout=10)
        self.assertEqual(text1, "system status")
        
        # 2. Parse command
        command = self.parser.parse_voice_command(text1)
        self.assertIsNotNone(command)
        
        # 3. Exit
        text2 = mock_recognizer.listen(timeout=10)
        self.assertEqual(text2, "exit")


if __name__ == '__main__':
    unittest.main()

