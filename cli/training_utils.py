"""
Training Utilities
Helper functions for training operations
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from enum import Enum

from cli.utils import get_project_root


class TrainingJobStatus(Enum):
    """Training job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainingJobManager:
    """Manages training jobs and their status"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = get_project_root() / "training_jobs.db"
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize training jobs database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                config_path TEXT,
                output_dir TEXT,
                epochs INTEGER,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                error_message TEXT,
                progress REAL DEFAULT 0.0,
                log_file TEXT,
                process_id INTEGER
            )
        """)
        # Add new columns if they don't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE training_jobs ADD COLUMN log_file TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            cursor.execute("ALTER TABLE training_jobs ADD COLUMN process_id INTEGER")
        except sqlite3.OperationalError:
            pass  # Column already exists
        conn.commit()
        conn.close()
    
    def get_log_file(self, job_id: str) -> Optional[Path]:
        """Get log file path for a job"""
        job = self.get_job(job_id)
        if not job:
            return None
        
        # Check if log_file is stored in database
        if job.get('log_file'):
            log_path = Path(job['log_file'])
            if log_path.exists():
                return log_path
        
        # Fallback: check output_dir for logs
        if job.get('output_dir'):
            output_dir = Path(job['output_dir'])
            log_path = output_dir / f"training_{job_id}.log"
            if log_path.exists():
                return log_path
        
        # Fallback: check logs directory
        project_root = get_project_root()
        log_path = project_root / "logs" / f"training_{job_id}.log"
        if log_path.exists():
            return log_path
        
        return None
    
    def set_log_file(self, job_id: str, log_file: str):
        """Set log file path for a job"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE training_jobs SET log_file = ? WHERE job_id = ?",
            (log_file, job_id)
        )
        conn.commit()
        conn.close()
    
    def set_process_id(self, job_id: str, process_id: int):
        """Set process ID for a job"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE training_jobs SET process_id = ? WHERE job_id = ?",
            (process_id, job_id)
        )
        conn.commit()
        conn.close()
    
    def get_process_id(self, job_id: str) -> Optional[int]:
        """Get process ID for a job"""
        job = self.get_job(job_id)
        if job:
            return job.get('process_id')
        return None
    
    def create_job(
        self,
        config_path: str,
        output_dir: Optional[str] = None,
        epochs: Optional[int] = None
    ) -> str:
        """Create a new training job"""
        job_id = str(uuid.uuid4())
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO training_jobs 
            (job_id, status, config_path, output_dir, epochs, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            TrainingJobStatus.PENDING.value,
            config_path,
            output_dir,
            epochs,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job information"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM training_jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_job_status(
        self,
        job_id: str,
        status: TrainingJobStatus,
        error_message: Optional[str] = None
    ):
        """Update job status"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        update_fields = ["status = ?"]
        values = [status.value]
        
        if status == TrainingJobStatus.RUNNING:
            update_fields.append("started_at = ?")
            values.append(datetime.now().isoformat())
        elif status in [TrainingJobStatus.COMPLETED, TrainingJobStatus.FAILED, TrainingJobStatus.CANCELLED]:
            update_fields.append("completed_at = ?")
            values.append(datetime.now().isoformat())
        
        if error_message:
            update_fields.append("error_message = ?")
            values.append(error_message)
        
        values.append(job_id)
        
        cursor.execute(
            f"UPDATE training_jobs SET {', '.join(update_fields)} WHERE job_id = ?",
            values
        )
        conn.commit()
        conn.close()
    
    def update_progress(self, job_id: str, progress: float):
        """Update training progress (0.0 to 1.0)"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE training_jobs SET progress = ? WHERE job_id = ?",
            (progress, job_id)
        )
        conn.commit()
        conn.close()
    
    def list_jobs(self, status: Optional[TrainingJobStatus] = None) -> List[Dict]:
        """List all jobs, optionally filtered by status"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT * FROM training_jobs WHERE status = ? ORDER BY created_at DESC", (status.value,))
        else:
            cursor.execute("SELECT * FROM training_jobs ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_job(self, job_id: str):
        """Delete a job record"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM training_jobs WHERE job_id = ?", (job_id,))
        conn.commit()
        conn.close()


def load_training_config(config_path: str) -> Dict:
    """Load training configuration from file"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, 'r') as f:
        return json.load(f)


def validate_training_config(config: Dict) -> bool:
    """Validate training configuration"""
    required_keys = ['model_name', 'dataset_path', 'output_dir', 'training_config']
    return all(key in config for key in required_keys)

