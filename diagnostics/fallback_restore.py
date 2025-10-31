"""
JARVIS AI - Fallback Restore System
Emergency restore and recovery mechanisms for system failures.
"""

import json
import logging
import os
import shutil
import subprocess
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid
from pathlib import Path
import tarfile
import zipfile

class RestoreType(Enum):
    """Types of restore operations."""
    CONFIGURATION = "configuration"
    DATABASE = "database"
    CODE = "code"
    DEPENDENCIES = "dependencies"
    FULL_SYSTEM = "full_system"
    SELECTIVE = "selective"

class RestoreStatus(Enum):
    """Restore operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class BackupInfo:
    """Backup information."""
    backup_id: str
    backup_type: RestoreType
    timestamp: datetime
    size_bytes: int
    file_path: str
    description: str
    checksum: str
    dependencies: List[str]

@dataclass
class RestoreOperation:
    """Restore operation record."""
    operation_id: str
    restore_type: RestoreType
    backup_id: str
    status: RestoreStatus
    start_time: datetime
    end_time: Optional[datetime]
    success: bool
    error_message: str
    restored_files: List[str]
    failed_files: List[str]

class FallbackRestoreSystem:
    """
    Fallback restore system for emergency recovery.
    Provides backup and restore capabilities for system recovery.
    """
    
    def __init__(self, backup_interval_hours: int = 24, max_backups: int = 10):
        """Initialize Fallback Restore System."""
        self.logger = logging.getLogger(__name__)
        self.backup_interval_hours = backup_interval_hours
        self.max_backups = max_backups
        
        # Backup and restore state
        self.backups = []
        self.restore_operations = []
        self.last_backup_time = None
        
        # Critical system components
        self.critical_components = [
            "core/",
            "utils/",
            "memory/",
            "interface/",
            "config/",
            "requirements.txt",
            "main.py",
            ".env"
        ]
        
        # Create backup directories
        self._create_backup_structure()
        
        # Load existing backups
        self._load_backup_registry()
        
        self.logger.info("Fallback Restore System initialized")
    
    def _create_backup_structure(self):
        """Create backup directory structure."""
        try:
            directories = [
                'backups',
                'backups/full',
                'backups/config',
                'backups/database',
                'backups/code',
                'backups/selective',
                'backups/registry'
            ]
            
            for directory in directories:
                dir_path = Path(directory)
                dir_path.mkdir(exist_ok=True)
            
            self.logger.info("Backup structure created")
        
        except Exception as e:
            self.logger.error(f"Error creating backup structure: {e}")
    
    def _load_backup_registry(self):
        """Load existing backup registry."""
        try:
            registry_file = Path("backups/registry/backup_registry.json")
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                    self.backups = [
                        BackupInfo(
                            backup_id=backup['backup_id'],
                            backup_type=RestoreType(backup['backup_type']),
                            timestamp=datetime.fromisoformat(backup['timestamp']),
                            size_bytes=backup['size_bytes'],
                            file_path=backup['file_path'],
                            description=backup['description'],
                            checksum=backup['checksum'],
                            dependencies=backup['dependencies']
                        )
                        for backup in backup_data
                    ]
                
                self.logger.info(f"Loaded {len(self.backups)} backups from registry")
        
        except Exception as e:
            self.logger.error(f"Error loading backup registry: {e}")
            self.backups = []
    
    def _save_backup_registry(self):
        """Save backup registry to file."""
        try:
            registry_file = Path("backups/registry/backup_registry.json")
            
            backup_data = [
                {
                    "backup_id": backup.backup_id,
                    "backup_type": backup.backup_type.value,
                    "timestamp": backup.timestamp.isoformat(),
                    "size_bytes": backup.size_bytes,
                    "file_path": backup.file_path,
                    "description": backup.description,
                    "checksum": backup.checksum,
                    "dependencies": backup.dependencies
                }
                for backup in self.backups
            ]
            
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Backup registry saved")
        
        except Exception as e:
            self.logger.error(f"Error saving backup registry: {e}")
    
    def create_backup(self, backup_type: RestoreType, description: str = None) -> Optional[BackupInfo]:
        """Create a new backup."""
        try:
            backup_id = f"backup_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.now()
            
            # Determine backup path and files
            if backup_type == RestoreType.FULL_SYSTEM:
                backup_path = Path("backups/full") / f"full_backup_{backup_id}.tar.gz"
                files_to_backup = self._get_all_system_files()
            elif backup_type == RestoreType.CONFIGURATION:
                backup_path = Path("backups/config") / f"config_backup_{backup_id}.tar.gz"
                files_to_backup = self._get_config_files()
            elif backup_type == RestoreType.DATABASE:
                backup_path = Path("backups/database") / f"db_backup_{backup_id}.tar.gz"
                files_to_backup = self._get_database_files()
            elif backup_type == RestoreType.CODE:
                backup_path = Path("backups/code") / f"code_backup_{backup_id}.tar.gz"
                files_to_backup = self._get_code_files()
            else:
                backup_path = Path("backups/selective") / f"selective_backup_{backup_id}.tar.gz"
                files_to_backup = self.critical_components
            
            # Create backup
            success, size_bytes, checksum = self._create_tar_backup(backup_path, files_to_backup)
            
            if not success:
                return None
            
            # Create backup info
            backup_info = BackupInfo(
                backup_id=backup_id,
                backup_type=backup_type,
                timestamp=timestamp,
                size_bytes=size_bytes,
                file_path=str(backup_path),
                description=description or f"{backup_type.value} backup",
                checksum=checksum,
                dependencies=[]
            )
            
            # Add to registry
            self.backups.append(backup_info)
            self.last_backup_time = timestamp
            
            # Save registry
            self._save_backup_registry()
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            self.logger.info(f"Backup created: {backup_id} ({backup_type.value})")
            return backup_info
        
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return None
    
    def _get_all_system_files(self) -> List[str]:
        """Get all system files for full backup."""
        try:
            files = []
            for root, dirs, filenames in os.walk('.'):
                # Skip certain directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv', 'backups']]
                
                for filename in filenames:
                    if not filename.startswith('.') and not filename.endswith('.pyc'):
                        file_path = os.path.join(root, filename)
                        files.append(file_path)
            
            return files
        
        except Exception as e:
            self.logger.error(f"Error getting system files: {e}")
            return []
    
    def _get_config_files(self) -> List[str]:
        """Get configuration files."""
        config_files = []
        config_dirs = ['config', 'settings']
        
        for config_dir in config_dirs:
            if os.path.exists(config_dir):
                for root, dirs, filenames in os.walk(config_dir):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        config_files.append(file_path)
        
        # Add individual config files
        config_files.extend(['.env', 'requirements.txt', 'package.json'])
        
        return [f for f in config_files if os.path.exists(f)]
    
    def _get_database_files(self) -> List[str]:
        """Get database files."""
        db_files = []
        db_extensions = ['.db', '.sqlite', '.sqlite3']
        
        for root, dirs, filenames in os.walk('.'):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in db_extensions):
                    file_path = os.path.join(root, filename)
                    db_files.append(file_path)
        
        return db_files
    
    def _get_code_files(self) -> List[str]:
        """Get code files."""
        code_files = []
        code_extensions = ['.py', '.js', '.ts', '.html', '.css', '.json']
        
        for root, dirs, filenames in os.walk('.'):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv', 'backups']]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in code_extensions):
                    file_path = os.path.join(root, filename)
                    code_files.append(file_path)
        
        return code_files
    
    def _create_tar_backup(self, backup_path: Path, files_to_backup: List[str]) -> Tuple[bool, int, str]:
        """Create tar.gz backup file."""
        try:
            total_size = 0
            
            with tarfile.open(backup_path, 'w:gz') as tar:
                for file_path in files_to_backup:
                    if os.path.exists(file_path):
                        try:
                            tar.add(file_path)
                            total_size += os.path.getsize(file_path)
                        except Exception as e:
                            self.logger.warning(f"Could not add {file_path} to backup: {e}")
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)
            
            return True, total_size, checksum
        
        except Exception as e:
            self.logger.error(f"Error creating tar backup: {e}")
            return False, 0, ""
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum."""
        try:
            import hashlib
            
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            
            return hash_md5.hexdigest()
        
        except Exception as e:
            self.logger.error(f"Error calculating checksum: {e}")
            return ""
    
    def _cleanup_old_backups(self):
        """Clean up old backups based on max_backups setting."""
        try:
            if len(self.backups) <= self.max_backups:
                return
            
            # Sort by timestamp (oldest first)
            self.backups.sort(key=lambda x: x.timestamp)
            
            # Remove oldest backups
            while len(self.backups) > self.max_backups:
                old_backup = self.backups.pop(0)
                
                # Delete backup file
                backup_file = Path(old_backup.file_path)
                if backup_file.exists():
                    backup_file.unlink()
                
                self.logger.info(f"Removed old backup: {old_backup.backup_id}")
            
            # Save updated registry
            self._save_backup_registry()
        
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}")
    
    def restore_from_backup(self, backup_id: str, restore_type: RestoreType = None) -> Optional[RestoreOperation]:
        """Restore system from backup."""
        try:
            # Find backup
            backup = next((b for b in self.backups if b.backup_id == backup_id), None)
            if not backup:
                self.logger.error(f"Backup not found: {backup_id}")
                return None
            
            # Create restore operation
            operation_id = f"restore_{uuid.uuid4().hex[:8]}"
            operation = RestoreOperation(
                operation_id=operation_id,
                restore_type=restore_type or backup.backup_type,
                backup_id=backup_id,
                status=RestoreStatus.PENDING,
                start_time=datetime.now(),
                end_time=None,
                success=False,
                error_message="",
                restored_files=[],
                failed_files=[]
            )
            
            self.restore_operations.append(operation)
            
            # Execute restore
            self._execute_restore(operation, backup)
            
            return operation
        
        except Exception as e:
            self.logger.error(f"Error restoring from backup: {e}")
            return None
    
    def _execute_restore(self, operation: RestoreOperation, backup: BackupInfo):
        """Execute restore operation."""
        try:
            operation.status = RestoreStatus.IN_PROGRESS
            
            self.logger.info(f"Starting restore operation: {operation.operation_id}")
            
            # Verify backup file exists
            backup_file = Path(backup.file_path)
            if not backup_file.exists():
                operation.error_message = "Backup file not found"
                operation.status = RestoreStatus.FAILED
                return
            
            # Verify checksum
            current_checksum = self._calculate_checksum(backup_file)
            if current_checksum != backup.checksum:
                operation.error_message = "Backup file checksum mismatch"
                operation.status = RestoreStatus.FAILED
                return
            
            # Create restore directory
            restore_dir = Path("restore_temp") / operation.operation_id
            restore_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract backup
            success, extracted_files = self._extract_backup(backup_file, restore_dir)
            
            if not success:
                operation.error_message = "Failed to extract backup"
                operation.status = RestoreStatus.FAILED
                return
            
            # Restore files
            restored_files, failed_files = self._restore_files(extracted_files, restore_dir)
            
            operation.restored_files = restored_files
            operation.failed_files = failed_files
            operation.success = len(failed_files) == 0
            operation.status = RestoreStatus.COMPLETED if operation.success else RestoreStatus.PARTIAL
            
            # Clean up restore directory
            shutil.rmtree(restore_dir, ignore_errors=True)
            
            self.logger.info(f"Restore operation completed: {operation.operation_id}")
        
        except Exception as e:
            operation.status = RestoreStatus.FAILED
            operation.error_message = str(e)
            self.logger.error(f"Error executing restore: {e}")
        
        finally:
            operation.end_time = datetime.now()
    
    def _extract_backup(self, backup_file: Path, extract_dir: Path) -> Tuple[bool, List[str]]:
        """Extract backup file."""
        try:
            extracted_files = []
            
            with tarfile.open(backup_file, 'r:gz') as tar:
                tar.extractall(extract_dir)
                
                # Get list of extracted files
                for member in tar.getmembers():
                    if member.isfile():
                        extracted_files.append(member.name)
            
            return True, extracted_files
        
        except Exception as e:
            self.logger.error(f"Error extracting backup: {e}")
            return False, []
    
    def _restore_files(self, extracted_files: List[str], extract_dir: Path) -> Tuple[List[str], List[str]]:
        """Restore files from extracted backup."""
        try:
            restored_files = []
            failed_files = []
            
            for file_path in extracted_files:
                try:
                    source_path = extract_dir / file_path
                    target_path = Path(file_path)
                    
                    # Create target directory if needed
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(source_path, target_path)
                    restored_files.append(file_path)
                
                except Exception as e:
                    self.logger.warning(f"Failed to restore {file_path}: {e}")
                    failed_files.append(file_path)
            
            return restored_files, failed_files
        
        except Exception as e:
            self.logger.error(f"Error restoring files: {e}")
            return [], extracted_files
    
    def emergency_restore(self) -> Optional[RestoreOperation]:
        """Perform emergency restore from latest backup."""
        try:
            if not self.backups:
                self.logger.error("No backups available for emergency restore")
                return None
            
            # Find latest backup
            latest_backup = max(self.backups, key=lambda x: x.timestamp)
            
            self.logger.warning(f"Performing emergency restore from backup: {latest_backup.backup_id}")
            
            return self.restore_from_backup(latest_backup.backup_id)
        
        except Exception as e:
            self.logger.error(f"Error in emergency restore: {e}")
            return None
    
    def get_backup_list(self) -> List[Dict[str, Any]]:
        """Get list of available backups."""
        try:
            return [
                {
                    "backup_id": backup.backup_id,
                    "backup_type": backup.backup_type.value,
                    "timestamp": backup.timestamp.isoformat(),
                    "size_mb": backup.size_bytes / 1024 / 1024,
                    "description": backup.description,
                    "file_path": backup.file_path
                }
                for backup in sorted(self.backups, key=lambda x: x.timestamp, reverse=True)
            ]
        
        except Exception as e:
            self.logger.error(f"Error getting backup list: {e}")
            return []
    
    def get_restore_history(self) -> List[Dict[str, Any]]:
        """Get restore operation history."""
        try:
            return [
                {
                    "operation_id": operation.operation_id,
                    "restore_type": operation.restore_type.value,
                    "backup_id": operation.backup_id,
                    "status": operation.status.value,
                    "start_time": operation.start_time.isoformat(),
                    "end_time": operation.end_time.isoformat() if operation.end_time else None,
                    "success": operation.success,
                    "restored_files_count": len(operation.restored_files),
                    "failed_files_count": len(operation.failed_files)
                }
                for operation in sorted(self.restore_operations, key=lambda x: x.start_time, reverse=True)
            ]
        
        except Exception as e:
            self.logger.error(f"Error getting restore history: {e}")
            return []
    
    def schedule_automatic_backup(self):
        """Schedule automatic backup if needed."""
        try:
            if not self.last_backup_time:
                # Create initial backup
                self.create_backup(RestoreType.FULL_SYSTEM, "Initial automatic backup")
                return
            
            # Check if backup is needed
            time_since_backup = datetime.now() - self.last_backup_time
            if time_since_backup.total_seconds() >= self.backup_interval_hours * 3600:
                self.create_backup(RestoreType.FULL_SYSTEM, "Scheduled automatic backup")
        
        except Exception as e:
            self.logger.error(f"Error in automatic backup scheduling: {e}")
    
    def export_restore_report(self, output_file: str = None) -> bool:
        """Export comprehensive restore report."""
        try:
            if not output_file:
                output_file = f"backups/restore_report_{int(datetime.now().timestamp())}.json"
            
            report_data = {
                "report_timestamp": datetime.now().isoformat(),
                "backup_interval_hours": self.backup_interval_hours,
                "max_backups": self.max_backups,
                "total_backups": len(self.backups),
                "total_restore_operations": len(self.restore_operations),
                "last_backup_time": self.last_backup_time.isoformat() if self.last_backup_time else None,
                "backups": self.get_backup_list(),
                "restore_history": self.get_restore_history()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Restore report exported: {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting restore report: {e}")
            return False
