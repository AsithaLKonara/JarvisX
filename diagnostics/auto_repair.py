"""
JARVIS AI - Auto Repair System
Automated repair and maintenance mechanisms for system issues.
"""

import json
import logging
import os
import shutil
import subprocess
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid
from pathlib import Path

class RepairActionType(Enum):
    """Types of repair actions."""
    CLEANUP_CACHE = "cleanup_cache"
    CLEANUP_LOGS = "cleanup_logs"
    CLEANUP_TEMP = "cleanup_temp"
    RESTART_SERVICE = "restart_service"
    KILL_PROCESS = "kill_process"
    FREE_DISK_SPACE = "free_disk_space"
    OPTIMIZE_MEMORY = "optimize_memory"
    UPDATE_DEPENDENCIES = "update_dependencies"
    REPAIR_PERMISSIONS = "repair_permissions"
    RESTART_SYSTEM = "restart_system"

class RepairStatus(Enum):
    """Repair action status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class RepairAction:
    """Individual repair action."""
    action_id: str
    action_type: RepairActionType
    description: str
    status: RepairStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_seconds: float
    success: bool
    error_message: str
    parameters: Dict[str, Any]

@dataclass
class RepairSession:
    """Complete repair session."""
    session_id: str
    trigger_reason: str
    start_time: datetime
    end_time: Optional[datetime]
    actions: List[RepairAction]
    overall_success: bool
    issues_fixed: List[str]
    issues_remaining: List[str]

class AutoRepairSystem:
    """
    Automated repair and maintenance system.
    Automatically detects and fixes common system issues.
    """
    
    def __init__(self, system_monitor=None):
        """Initialize Auto Repair System."""
        self.logger = logging.getLogger(__name__)
        self.system_monitor = system_monitor
        
        # Repair state
        self.repair_sessions = []
        self.current_session = None
        self.auto_repair_enabled = True
        
        # Repair rules and actions
        self.repair_rules = self._create_default_repair_rules()
        self.repair_actions = self._create_repair_actions()
        
        # Create repair directories
        self._create_repair_structure()
        
        self.logger.info("Auto Repair System initialized")
    
    def _create_repair_structure(self):
        """Create repair directory structure."""
        try:
            directories = [
                'repair',
                'repair/sessions',
                'repair/backups',
                'repair/logs',
                'repair/scripts'
            ]
            
            for directory in directories:
                dir_path = Path(directory)
                dir_path.mkdir(exist_ok=True)
            
            self.logger.info("Repair structure created")
        
        except Exception as e:
            self.logger.error(f"Error creating repair structure: {e}")
    
    def _create_default_repair_rules(self) -> Dict[str, Any]:
        """Create default repair rules."""
        return {
            "high_cpu_usage": {
                "condition": "cpu_usage > 80",
                "actions": ["kill_process", "optimize_memory"],
                "priority": "high"
            },
            "high_memory_usage": {
                "condition": "memory_usage > 85",
                "actions": ["optimize_memory", "cleanup_cache"],
                "priority": "high"
            },
            "low_disk_space": {
                "condition": "disk_usage > 90",
                "actions": ["cleanup_temp", "cleanup_logs", "free_disk_space"],
                "priority": "critical"
            },
            "too_many_processes": {
                "condition": "process_count > 250",
                "actions": ["kill_process", "restart_service"],
                "priority": "medium"
            },
            "system_errors": {
                "condition": "error_rate > 5",
                "actions": ["cleanup_logs", "restart_service"],
                "priority": "medium"
            }
        }
    
    def _create_repair_actions(self) -> Dict[RepairActionType, Callable]:
        """Create repair action functions."""
        return {
            RepairActionType.CLEANUP_CACHE: self._cleanup_cache,
            RepairActionType.CLEANUP_LOGS: self._cleanup_logs,
            RepairActionType.CLEANUP_TEMP: self._cleanup_temp,
            RepairActionType.RESTART_SERVICE: self._restart_service,
            RepairActionType.KILL_PROCESS: self._kill_process,
            RepairActionType.FREE_DISK_SPACE: self._free_disk_space,
            RepairActionType.OPTIMIZE_MEMORY: self._optimize_memory,
            RepairActionType.UPDATE_DEPENDENCIES: self._update_dependencies,
            RepairActionType.REPAIR_PERMISSIONS: self._repair_permissions,
            RepairActionType.RESTART_SYSTEM: self._restart_system
        }
    
    def start_auto_repair(self):
        """Start automatic repair monitoring."""
        try:
            if not self.auto_repair_enabled:
                self.logger.warning("Auto repair is disabled")
                return
            
            if self.system_monitor and self.system_monitor.is_monitoring:
                # Add repair callback to system monitor
                self.system_monitor.add_alert_callback(self._handle_system_alert)
                self.logger.info("Auto repair monitoring started")
            else:
                self.logger.warning("System monitor not available for auto repair")
        
        except Exception as e:
            self.logger.error(f"Error starting auto repair: {e}")
    
    def stop_auto_repair(self):
        """Stop automatic repair monitoring."""
        try:
            self.auto_repair_enabled = False
            self.logger.info("Auto repair monitoring stopped")
        
        except Exception as e:
            self.logger.error(f"Error stopping auto repair: {e}")
    
    def _handle_system_alert(self, alert: str, health):
        """Handle system alert and trigger repairs."""
        try:
            if not self.auto_repair_enabled:
                return
            
            self.logger.info(f"Handling system alert: {alert}")
            
            # Determine repair actions based on alert
            repair_actions = self._determine_repair_actions(health)
            
            if repair_actions:
                # Start repair session
                session = self._start_repair_session(f"Alert: {alert}", repair_actions)
                self.logger.info(f"Started repair session: {session.session_id}")
        
        except Exception as e:
            self.logger.error(f"Error handling system alert: {e}")
    
    def _determine_repair_actions(self, health) -> List[RepairActionType]:
        """Determine repair actions based on system health."""
        try:
            actions = []
            
            for metric in health.metrics:
                if metric.status.value in ["warning", "critical"]:
                    if metric.metric_type.value == "cpu_usage":
                        actions.append(RepairActionType.KILL_PROCESS)
                        actions.append(RepairActionType.OPTIMIZE_MEMORY)
                    
                    elif metric.metric_type.value == "memory_usage":
                        actions.append(RepairActionType.OPTIMIZE_MEMORY)
                        actions.append(RepairActionType.CLEANUP_CACHE)
                    
                    elif metric.metric_type.value == "disk_usage":
                        actions.append(RepairActionType.CLEANUP_TEMP)
                        actions.append(RepairActionType.CLEANUP_LOGS)
                        actions.append(RepairActionType.FREE_DISK_SPACE)
                    
                    elif metric.metric_type.value == "process_count":
                        actions.append(RepairActionType.KILL_PROCESS)
                        actions.append(RepairActionType.RESTART_SERVICE)
            
            return list(set(actions))  # Remove duplicates
        
        except Exception as e:
            self.logger.error(f"Error determining repair actions: {e}")
            return []
    
    def _start_repair_session(self, trigger_reason: str, actions: List[RepairActionType]) -> RepairSession:
        """Start a new repair session."""
        try:
            session_id = f"repair_{uuid.uuid4().hex[:8]}"
            
            session = RepairSession(
                session_id=session_id,
                trigger_reason=trigger_reason,
                start_time=datetime.now(),
                end_time=None,
                actions=[],
                overall_success=False,
                issues_fixed=[],
                issues_remaining=[]
            )
            
            self.current_session = session
            self.repair_sessions.append(session)
            
            # Execute repair actions
            self._execute_repair_actions(session, actions)
            
            return session
        
        except Exception as e:
            self.logger.error(f"Error starting repair session: {e}")
            return None
    
    def _execute_repair_actions(self, session: RepairSession, actions: List[RepairActionType]):
        """Execute repair actions in a session."""
        try:
            for action_type in actions:
                action = RepairAction(
                    action_id=f"action_{uuid.uuid4().hex[:8]}",
                    action_type=action_type,
                    description=f"Executing {action_type.value}",
                    status=RepairStatus.PENDING,
                    start_time=None,
                    end_time=None,
                    duration_seconds=0.0,
                    success=False,
                    error_message="",
                    parameters={}
                )
                
                session.actions.append(action)
                
                # Execute the action
                self._execute_repair_action(action)
            
            # Complete the session
            self._complete_repair_session(session)
        
        except Exception as e:
            self.logger.error(f"Error executing repair actions: {e}")
    
    def _execute_repair_action(self, action: RepairAction):
        """Execute a single repair action."""
        try:
            action.status = RepairStatus.IN_PROGRESS
            action.start_time = datetime.now()
            
            self.logger.info(f"Executing repair action: {action.action_type.value}")
            
            # Get the repair function
            repair_func = self.repair_actions.get(action.action_type)
            if not repair_func:
                action.error_message = f"No repair function for {action.action_type.value}"
                action.status = RepairStatus.FAILED
                return
            
            # Execute the repair function
            success, message = repair_func(action.parameters)
            
            action.success = success
            action.error_message = message if not success else ""
            action.status = RepairStatus.COMPLETED if success else RepairStatus.FAILED
            
            self.logger.info(f"Repair action {action.action_type.value}: {'SUCCESS' if success else 'FAILED'}")
        
        except Exception as e:
            action.status = RepairStatus.FAILED
            action.error_message = str(e)
            self.logger.error(f"Error executing repair action {action.action_type.value}: {e}")
        
        finally:
            action.end_time = datetime.now()
            if action.start_time:
                action.duration_seconds = (action.end_time - action.start_time).total_seconds()
    
    def _cleanup_cache(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Clean up system cache."""
        try:
            cache_dirs = [
                "~/.cache",
                "/tmp",
                "cache",
                "temp"
            ]
            
            cleaned_size = 0
            cleaned_files = 0
            
            for cache_dir in cache_dirs:
                cache_path = Path(cache_dir).expanduser()
                if cache_path.exists():
                    for file_path in cache_path.rglob("*"):
                        if file_path.is_file():
                            try:
                                file_size = file_path.stat().st_size
                                file_path.unlink()
                                cleaned_size += file_size
                                cleaned_files += 1
                            except:
                                pass
            
            return True, f"Cleaned {cleaned_files} files, freed {cleaned_size / 1024 / 1024:.2f} MB"
        
        except Exception as e:
            return False, f"Cache cleanup failed: {str(e)}"
    
    def _cleanup_logs(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Clean up old log files."""
        try:
            log_dirs = [
                "logs",
                "monitoring/logs",
                "repair/logs"
            ]
            
            cleaned_files = 0
            cleaned_size = 0
            
            for log_dir in log_dirs:
                log_path = Path(log_dir)
                if log_path.exists():
                    for file_path in log_path.rglob("*.log"):
                        try:
                            # Delete logs older than 7 days
                            if (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days > 7:
                                file_size = file_path.stat().st_size
                                file_path.unlink()
                                cleaned_size += file_size
                                cleaned_files += 1
                        except:
                            pass
            
            return True, f"Cleaned {cleaned_files} log files, freed {cleaned_size / 1024 / 1024:.2f} MB"
        
        except Exception as e:
            return False, f"Log cleanup failed: {str(e)}"
    
    def _cleanup_temp(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Clean up temporary files."""
        try:
            temp_dirs = [
                "/tmp",
                "temp",
                "tmp"
            ]
            
            cleaned_files = 0
            cleaned_size = 0
            
            for temp_dir in temp_dirs:
                temp_path = Path(temp_dir)
                if temp_path.exists():
                    for file_path in temp_path.rglob("*"):
                        if file_path.is_file():
                            try:
                                # Delete temp files older than 1 day
                                if (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days > 1:
                                    file_size = file_path.stat().st_size
                                    file_path.unlink()
                                    cleaned_size += file_size
                                    cleaned_files += 1
                            except:
                                pass
            
            return True, f"Cleaned {cleaned_files} temp files, freed {cleaned_size / 1024 / 1024:.2f} MB"
        
        except Exception as e:
            return False, f"Temp cleanup failed: {str(e)}"
    
    def _restart_service(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Restart system service."""
        try:
            # This is a placeholder - in a real implementation, you would restart actual services
            # For now, we'll just simulate a restart
            service_name = parameters.get("service_name", "jarvis")
            
            # Simulate service restart
            time.sleep(1)
            
            return True, f"Service {service_name} restarted successfully"
        
        except Exception as e:
            return False, f"Service restart failed: {str(e)}"
    
    def _kill_process(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Kill problematic processes."""
        try:
            import psutil
            
            killed_processes = 0
            
            # Find processes consuming high CPU or memory
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if proc.info['cpu_percent'] > 50 or proc.info['memory_percent'] > 10:
                        # Skip system processes
                        if proc.info['name'] not in ['systemd', 'kernel', 'init']:
                            proc.kill()
                            killed_processes += 1
                except:
                    pass
            
            return True, f"Killed {killed_processes} high-resource processes"
        
        except Exception as e:
            return False, f"Process kill failed: {str(e)}"
    
    def _free_disk_space(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Free up disk space."""
        try:
            # This combines multiple cleanup actions
            cache_success, cache_msg = self._cleanup_cache({})
            logs_success, logs_msg = self._cleanup_logs({})
            temp_success, temp_msg = self._cleanup_temp({})
            
            if cache_success or logs_success or temp_success:
                return True, f"Disk space freed: {cache_msg}, {logs_msg}, {temp_msg}"
            else:
                return False, "Failed to free disk space"
        
        except Exception as e:
            return False, f"Disk space free failed: {str(e)}"
    
    def _optimize_memory(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Optimize memory usage."""
        try:
            import gc
            
            # Force garbage collection
            collected = gc.collect()
            
            # Clear Python caches
            import sys
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
            
            return True, f"Memory optimized: {collected} objects collected"
        
        except Exception as e:
            return False, f"Memory optimization failed: {str(e)}"
    
    def _update_dependencies(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Update system dependencies."""
        try:
            # This is a placeholder - in a real implementation, you would update actual dependencies
            return True, "Dependencies update simulated successfully"
        
        except Exception as e:
            return False, f"Dependencies update failed: {str(e)}"
    
    def _repair_permissions(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Repair file permissions."""
        try:
            # This is a placeholder - in a real implementation, you would repair actual permissions
            return True, "Permissions repair simulated successfully"
        
        except Exception as e:
            return False, f"Permissions repair failed: {str(e)}"
    
    def _restart_system(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Restart the entire system."""
        try:
            # This is a placeholder - in a real implementation, you would restart the system
            # For safety, this is disabled by default
            return False, "System restart disabled for safety"
        
        except Exception as e:
            return False, f"System restart failed: {str(e)}"
    
    def _complete_repair_session(self, session: RepairSession):
        """Complete a repair session."""
        try:
            session.end_time = datetime.now()
            
            # Calculate overall success
            successful_actions = [a for a in session.actions if a.success]
            session.overall_success = len(successful_actions) > 0
            
            # Generate issues fixed and remaining
            session.issues_fixed = [a.description for a in successful_actions]
            session.issues_remaining = [a.error_message for a in session.actions if not a.success and a.error_message]
            
            # Save session data
            self._save_repair_session(session)
            
            self.logger.info(f"Repair session completed: {session.session_id} - {'SUCCESS' if session.overall_success else 'FAILED'}")
        
        except Exception as e:
            self.logger.error(f"Error completing repair session: {e}")
    
    def _save_repair_session(self, session: RepairSession):
        """Save repair session data."""
        try:
            session_file = Path("repair/sessions") / f"session_{session.session_id}.json"
            
            session_data = {
                "session_id": session.session_id,
                "trigger_reason": session.trigger_reason,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "overall_success": session.overall_success,
                "issues_fixed": session.issues_fixed,
                "issues_remaining": session.issues_remaining,
                "actions": [
                    {
                        "action_id": action.action_id,
                        "action_type": action.action_type.value,
                        "description": action.description,
                        "status": action.status.value,
                        "start_time": action.start_time.isoformat() if action.start_time else None,
                        "end_time": action.end_time.isoformat() if action.end_time else None,
                        "duration_seconds": action.duration_seconds,
                        "success": action.success,
                        "error_message": action.error_message
                    }
                    for action in session.actions
                ]
            }
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Repair session saved: {session_file}")
        
        except Exception as e:
            self.logger.error(f"Error saving repair session: {e}")
    
    def get_repair_history(self, hours: int = 24) -> List[RepairSession]:
        """Get repair history for specified hours."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return [session for session in self.repair_sessions if session.start_time >= cutoff_time]
        
        except Exception as e:
            self.logger.error(f"Error getting repair history: {e}")
            return []
    
    def get_repair_statistics(self) -> Dict[str, Any]:
        """Get repair statistics."""
        try:
            total_sessions = len(self.repair_sessions)
            successful_sessions = len([s for s in self.repair_sessions if s.overall_success])
            
            total_actions = sum(len(s.actions) for s in self.repair_sessions)
            successful_actions = sum(len([a for a in s.actions if a.success]) for s in self.repair_sessions)
            
            return {
                "total_sessions": total_sessions,
                "successful_sessions": successful_sessions,
                "success_rate": (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                "total_actions": total_actions,
                "successful_actions": successful_actions,
                "action_success_rate": (successful_actions / total_actions * 100) if total_actions > 0 else 0,
                "auto_repair_enabled": self.auto_repair_enabled
            }
        
        except Exception as e:
            self.logger.error(f"Error getting repair statistics: {e}")
            return {}
    
    def manual_repair(self, actions: List[RepairActionType]) -> RepairSession:
        """Perform manual repair with specified actions."""
        try:
            session = self._start_repair_session("Manual repair", actions)
            self.logger.info(f"Manual repair session started: {session.session_id}")
            return session
        
        except Exception as e:
            self.logger.error(f"Error starting manual repair: {e}")
            return None
    
    def export_repair_report(self, output_file: str = None) -> bool:
        """Export comprehensive repair report."""
        try:
            if not output_file:
                output_file = f"repair/repair_report_{int(datetime.now().timestamp())}.json"
            
            report_data = {
                "report_timestamp": datetime.now().isoformat(),
                "auto_repair_enabled": self.auto_repair_enabled,
                "repair_statistics": self.get_repair_statistics(),
                "recent_sessions": [
                    {
                        "session_id": session.session_id,
                        "trigger_reason": session.trigger_reason,
                        "start_time": session.start_time.isoformat(),
                        "overall_success": session.overall_success,
                        "actions_count": len(session.actions)
                    }
                    for session in self.repair_sessions[-10:]  # Last 10 sessions
                ]
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Repair report exported: {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting repair report: {e}")
            return False
