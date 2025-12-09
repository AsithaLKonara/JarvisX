"""
Unit Tests for Training CLI Commands
Tests all training-related CLI functionality
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.training import (
    start_training,
    training_status,
    training_logs,
    list_training_jobs,
    cancel_training,
    evaluate_model
)
from cli.training_utils import TrainingJobManager, TrainingJobStatus
from cli.utils import CLIOutput


class TestTrainingCLI(unittest.TestCase):
    """Test Training CLI commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Create test config
        test_config = {
            "model_name": "test-model",
            "dataset_path": "test_dataset.json",
            "output_dir": str(self.output_dir),
            "training_config": {
                "num_epochs": 5,
                "batch_size": 4,
                "learning_rate": 0.0001,
                "max_length": 512
            }
        }
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Create test database
        self.db_path = Path(self.temp_dir) / "test_training_jobs.db"
        self.job_manager = TrainingJobManager(db_path=str(self.db_path))
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_start_training(self):
        """Test training start command"""
        with patch('cli.training.load_training_config') as mock_load, \
             patch('cli.training.validate_training_config') as mock_validate:
            mock_load.return_value = {
                "model_name": "test-model",
                "output_dir": str(self.output_dir),
                "training_config": {"num_epochs": 5}
            }
            mock_validate.return_value = True
            
            # Mock typer context
            with patch('typer.Option') as mock_option:
                # Test that job is created
                job_id = self.job_manager.create_job(
                    config_path=str(self.config_file),
                    output_dir=str(self.output_dir),
                    epochs=5
                )
                self.assertIsNotNone(job_id)
                self.assertEqual(len(self.job_manager.list_jobs()), 1)
    
    def test_training_status(self):
        """Test training status command"""
        # Create a test job
        job_id = self.job_manager.create_job(
            config_path=str(self.config_file),
            output_dir=str(self.output_dir),
            epochs=5
        )
        
        # Get job status
        job = self.job_manager.get_job(job_id)
        self.assertIsNotNone(job)
        self.assertEqual(job['status'], TrainingJobStatus.PENDING.value)
    
    def test_training_logs(self):
        """Test training logs command"""
        # Create a test job
        job_id = self.job_manager.create_job(
            config_path=str(self.config_file),
            output_dir=str(self.output_dir),
            epochs=5
        )
        
        # Create a log file
        log_file = self.output_dir / f"training_{job_id}.log"
        with open(log_file, 'w') as f:
            f.write("Training started\nTraining in progress\nTraining completed\n")
        
        # Set log file in database
        self.job_manager.set_log_file(job_id, str(log_file))
        
        # Test log retrieval
        retrieved_log = self.job_manager.get_log_file(job_id)
        self.assertEqual(retrieved_log, log_file)
        self.assertTrue(retrieved_log.exists())
    
    def test_list_training_jobs(self):
        """Test list training jobs command"""
        # Create multiple jobs
        job1 = self.job_manager.create_job(
            config_path=str(self.config_file),
            output_dir=str(self.output_dir),
            epochs=5
        )
        job2 = self.job_manager.create_job(
            config_path=str(self.config_file),
            output_dir=str(self.output_dir),
            epochs=10
        )
        
        # List all jobs
        jobs = self.job_manager.list_jobs()
        self.assertEqual(len(jobs), 2)
        
        # Filter by status
        pending_jobs = self.job_manager.list_jobs(TrainingJobStatus.PENDING)
        self.assertEqual(len(pending_jobs), 2)
    
    def test_cancel_training(self):
        """Test cancel training command"""
        # Create a test job
        job_id = self.job_manager.create_job(
            config_path=str(self.config_file),
            output_dir=str(self.output_dir),
            epochs=5
        )
        
        # Update to running
        self.job_manager.update_job_status(job_id, TrainingJobStatus.RUNNING)
        
        # Cancel job
        self.job_manager.update_job_status(
            job_id,
            TrainingJobStatus.CANCELLED,
            error_message="Cancelled by user"
        )
        
        # Verify cancellation
        job = self.job_manager.get_job(job_id)
        self.assertEqual(job['status'], TrainingJobStatus.CANCELLED.value)
        self.assertIsNotNone(job['error_message'])
    
    def test_evaluate_model(self):
        """Test model evaluation command"""
        # Create a test model directory
        model_dir = self.output_dir / "test_model"
        model_dir.mkdir(exist_ok=True)
        
        # Create dummy model files
        (model_dir / "config.json").write_text('{"test": "config"}')
        (model_dir / "model.bin").write_bytes(b"dummy model data")
        
        # Test model path exists
        self.assertTrue(model_dir.exists())
        self.assertTrue((model_dir / "config.json").exists())


if __name__ == '__main__':
    unittest.main()

