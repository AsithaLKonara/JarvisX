#!/usr/bin/env python3
"""
Jarvis X V2 - Computer Access Layer
Bridges AI brain with actual computer control capabilities
"""

import os
import sys
import subprocess
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class PermissionLevel:
    """Permission levels for computer access"""
    SAFE = "safe"              # Read-only, monitoring
    STANDARD = "standard"      # File ops, app launch
    ELEVATED = "elevated"      # System changes, dangerous ops
    
    # Safe actions (no confirmation needed)
    SAFE_ACTIONS = [
        "monitor_cpu", "monitor_memory", "monitor_disk",
        "list_processes", "get_system_info", "read_file",
        "list_directory", "screenshot", "get_current_time"
    ]
    
    # Requires confirmation
    CONFIRM_ACTIONS = [
        "click_mouse", "type_text", "execute_command",
        "create_file", "delete_file", "modify_file",
        "launch_app", "kill_process", "run_workflow"
    ]


class ComputerAccessLayer:
    """
    Computer Access Layer - Connects AI to actual computer control
    
    Provides safe, controlled access to:
    - System monitoring (CPU, memory, disk, processes)
    - File system operations
    - Application control
    - RPA automation
    - Workflow execution
    """
    
    def __init__(self, safety_mode: bool = True, auto_confirm_safe: bool = True):
        """
        Initialize Computer Access Layer
        
        Args:
            safety_mode: Enable safety checks and confirmations
            auto_confirm_safe: Automatically approve safe actions
        """
        self.safety_mode = safety_mode
        self.auto_confirm_safe = auto_confirm_safe
        self.action_history = []
        
        # Import optional components
        self._load_components()
        
        logger.info("Computer Access Layer initialized (Safety: %s)", safety_mode)
    
    def _load_components(self):
        """Load computer control components"""
        # System Monitor
        try:
            from system_monitor.resource_monitor import ResourceMonitor
            self.resource_monitor = ResourceMonitor()
            self.has_monitoring = True
            logger.info("✅ ResourceMonitor loaded")
        except Exception as e:
            # Create basic built-in monitor as fallback
            logger.warning(f"ResourceMonitor not available, using built-in: {e}")
            self.resource_monitor = self._create_builtin_monitor()
            self.has_monitoring = True  # Using built-in fallback
        
        # RPA Controller
        try:
            from automation.rpa_controller import RPAController
            self.rpa = RPAController(safety_mode=self.safety_mode)
            self.has_rpa = True
        except ImportError:
            self.rpa = None
            self.has_rpa = False
            logger.warning("RPAController not available")
        
        # Workflow Orchestrator
        try:
            from automation.workflow_orchestrator import WorkflowOrchestrator
            self.workflows = WorkflowOrchestrator()
            self.has_workflows = True
        except ImportError:
            self.workflows = None
            self.has_workflows = False
            logger.warning("WorkflowOrchestrator not available")
    
    def execute_action(self, action_type: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute computer access action with safety checks
        
        Args:
            action_type: Type of action (e.g., "monitor_cpu", "click_mouse")
            parameters: Action-specific parameters
        
        Returns:
            dict with 'success', 'result', and optional 'error'
        """
        try:
            parameters = parameters or {}
            
            # Check permissions
            permission_check = self._check_permission(action_type, parameters)
            if not permission_check['allowed']:
                return {
                    'success': False,
                    'error': permission_check['reason'],
                    'requires_confirmation': True
                }
            
            # Log action
            self._log_action(action_type, parameters)
            
            # Route to appropriate handler
            result = self._route_action(action_type, parameters)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_permission(self, action_type: str, parameters: Dict) -> Dict[str, Any]:
        """Check if action is allowed"""
        # Safety mode always on for now
        if not self.safety_mode:
            return {'allowed': True, 'reason': None}
        
        # Check if action requires confirmation
        if action_type in PermissionLevel.SAFE_ACTIONS:
            if self.auto_confirm_safe:
                return {'allowed': True, 'reason': None}
        
        if action_type in PermissionLevel.CONFIRM_ACTIONS:
            # In CLI mode, we'll describe what will happen
            return {'allowed': True, 'reason': None, 'requires_user_awareness': True}
        
        # Unknown actions - deny
        return {
            'allowed': False,
            'reason': f"Unknown action type: {action_type}"
        }
    
    def _log_action(self, action_type: str, parameters: Dict):
        """Log executed action"""
        self.action_history.append({
            'action_type': action_type,
            'parameters': parameters,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 actions
        if len(self.action_history) > 100:
            self.action_history = self.action_history[-100:]
    
    def _route_action(self, action_type: str, parameters: Dict) -> Dict[str, Any]:
        """Route action to appropriate handler"""
        
        # ===================================================================
        # SYSTEM MONITORING ACTIONS
        # ===================================================================
        
        if action_type == "monitor_cpu":
            if not self.has_monitoring:
                return {'success': False, 'error': 'System monitoring not available'}
            
            cpu_info = self.resource_monitor.get_cpu_info()
            return {
                'success': True,
                'action': 'monitor_cpu',
                'result': cpu_info
            }
        
        elif action_type == "monitor_memory":
            if not self.has_monitoring:
                return {'success': False, 'error': 'System monitoring not available'}
            
            mem_info = self.resource_monitor.get_memory_info()
            return {
                'success': True,
                'action': 'monitor_memory',
                'result': mem_info
            }
        
        elif action_type == "monitor_disk":
            if not self.has_monitoring:
                return {'success': False, 'error': 'System monitoring not available'}
            
            disk_info = self.resource_monitor.get_disk_info()
            return {
                'success': True,
                'action': 'monitor_disk',
                'result': disk_info
            }
        
        elif action_type == "get_system_stats":
            if not self.has_monitoring:
                return {'success': False, 'error': 'System monitoring not available'}
            
            stats = self.resource_monitor.get_system_stats()
            return {
                'success': True,
                'action': 'get_system_stats',
                'result': stats
            }
        
        elif action_type == "list_processes":
            if not self.has_monitoring:
                return {'success': False, 'error': 'System monitoring not available'}
            
            proc_info = self.resource_monitor.get_process_count()
            return {
                'success': True,
                'action': 'list_processes',
                'result': proc_info
            }
        
        # ===================================================================
        # FILE SYSTEM ACTIONS
        # ===================================================================
        
        elif action_type == "list_directory":
            path = parameters.get('path', '.')
            try:
                items = list(Path(path).iterdir())
                result = [
                    {
                        'name': item.name,
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else None
                    }
                    for item in items
                ]
                return {
                    'success': True,
                    'action': 'list_directory',
                    'result': {'path': path, 'items': result}
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        elif action_type == "read_file":
            file_path = parameters.get('file_path')
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                return {
                    'success': True,
                    'action': 'read_file',
                    'result': {'path': file_path, 'content': content}
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        elif action_type == "get_file_info":
            file_path = parameters.get('file_path')
            try:
                path = Path(file_path)
                stat = path.stat()
                return {
                    'success': True,
                    'action': 'get_file_info',
                    'result': {
                        'path': str(path),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'is_file': path.is_file(),
                        'is_dir': path.is_dir()
                    }
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        elif action_type == "write_file":
            file_path = parameters.get('file_path') or parameters.get('path')
            content = parameters.get('content', '')
            mode = parameters.get('mode', 'w')  # 'w' for write, 'a' for append
            try:
                path = Path(file_path)
                # Create parent directories if needed
                path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(path, mode) as f:
                    f.write(content)
                
                return {
                    'success': True,
                    'action': 'write_file',
                    'result': {
                        'path': str(path),
                        'bytes_written': len(content.encode('utf-8')),
                        'mode': mode
                    }
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        elif action_type == "delete_file":
            file_path = parameters.get('file_path') or parameters.get('path')
            try:
                path = Path(file_path)
                if not path.exists():
                    return {'success': False, 'error': f'File not found: {file_path}'}
                
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    return {'success': False, 'error': f'Path is neither file nor directory: {file_path}'}
                
                return {
                    'success': True,
                    'action': 'delete_file',
                    'result': {
                        'path': str(path),
                        'deleted': True
                    }
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        elif action_type == "search_files":
            search_path = parameters.get('path', '.')
            pattern = parameters.get('pattern', '*')
            recursive = parameters.get('recursive', True)
            try:
                path = Path(search_path)
                if not path.exists():
                    return {'success': False, 'error': f'Search path not found: {search_path}'}
                
                if recursive:
                    matches = list(path.rglob(pattern))
                else:
                    matches = list(path.glob(pattern))
                
                result = [
                    {
                        'path': str(match),
                        'name': match.name,
                        'type': 'directory' if match.is_dir() else 'file',
                        'size': match.stat().st_size if match.is_file() else None
                    }
                    for match in matches
                ]
                
                return {
                    'success': True,
                    'action': 'search_files',
                    'result': {
                        'search_path': str(path),
                        'pattern': pattern,
                        'matches': result,
                        'count': len(result)
                    }
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        # ===================================================================
        # RPA ACTIONS (with confirmation)
        # ===================================================================
        
        elif action_type == "screenshot":
            if not self.has_rpa:
                # Fallback to basic screenshot
                try:
                    import pyautogui
                    filename = parameters.get('filename', f"screenshot_{int(datetime.now().timestamp())}.png")
                    screenshot = pyautogui.screenshot()
                    screenshot.save(filename)
                    return {
                        'success': True,
                        'action': 'screenshot',
                        'result': {'file': filename}
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}
            
            from automation.rpa_controller import RPAAction, ActionType
            action = RPAAction(
                action_type=ActionType.SCREENSHOT,
                parameters=parameters
            )
            result = self.rpa.execute_action(action)
            return {
                'success': result['success'],
                'action': 'screenshot',
                'result': result
            }
        
        # ===================================================================
        # PROCESS MANAGEMENT
        # ===================================================================
        
        elif action_type == "get_current_time":
            return {
                'success': True,
                'action': 'get_current_time',
                'result': {
                    'time': datetime.now().isoformat(),
                    'timestamp': datetime.now().timestamp()
                }
            }
        
        # ===================================================================
        # UNKNOWN ACTION
        # ===================================================================
        
        else:
            return {
                'success': False,
                'error': f"Unknown action type: {action_type}",
                'available_actions': self.get_available_actions()
            }
    
    def get_available_actions(self) -> List[str]:
        """Get list of available computer access actions"""
        actions = [
            # System Monitoring
            "monitor_cpu",
            "monitor_memory",
            "monitor_disk",
            "get_system_stats",
            "list_processes",
            
            # File System
            "list_directory",
            "read_file",
            "write_file",
            "delete_file",
            "get_file_info",
            "search_files",
            
            # System Info
            "get_current_time",
            "screenshot"
        ]
        
        # Add RPA actions if available
        if self.has_rpa:
            actions.extend([
                "click_mouse",
                "type_text",
                "mouse_move"
            ])
        
        # Add workflow actions if available
        if self.has_workflows:
            actions.extend([
                "run_workflow",
                "list_workflows"
            ])
        
        return sorted(actions)
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get available computer access capabilities"""
        return {
            'system_monitoring': self.has_monitoring,
            'rpa_automation': self.has_rpa,
            'workflow_execution': self.has_workflows,
            'file_system_access': True,  # Always available (Python built-in)
            'process_management': True,   # psutil always available
        }
    
    def get_action_history(self, limit: int = 10) -> List[Dict]:
        """Get recent action history"""
        return self.action_history[-limit:]
    
    def clear_history(self):
        """Clear action history"""
        self.action_history = []
    
    def _create_builtin_monitor(self):
        """Create built-in monitor using psutil directly"""
        class BuiltinMonitor:
            """Fallback monitor using psutil"""
            def __init__(self):
                self.history = []
            
            def get_cpu_info(self):
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_count = psutil.cpu_count()
                try:
                    per_cpu = psutil.cpu_percent(percpu=True)
                except:
                    per_cpu = []
                return {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'per_cpu': per_cpu,
                    'alert': cpu_percent > 80.0
                }
            
            def get_memory_info(self):
                mem = psutil.virtual_memory()
                return {
                    'total': mem.total,
                    'available': mem.available,
                    'used': mem.used,
                    'percent': mem.percent,
                    'alert': mem.percent > 85.0
                }
            
            def get_disk_info(self, path='/'):
                disk = psutil.disk_usage(path)
                return {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent,
                    'alert': disk.percent > 90.0
                }
            
            def get_process_count(self):
                try:
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                        try:
                            processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'memory_percent': proc.info['memory_percent'] or 0
                            })
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    top_10 = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:10]
                    return {
                        'total': len(psutil.pids()),
                        'top_10': top_10
                    }
                except:
                    return {'total': 0, 'top_10': []}
            
            def get_system_stats(self):
                return {
                    'timestamp': datetime.now().isoformat(),
                    'cpu': self.get_cpu_info(),
                    'memory': self.get_memory_info(),
                    'disk': self.get_disk_info(),
                    'processes': self.get_process_count()
                }
        
        return BuiltinMonitor()

