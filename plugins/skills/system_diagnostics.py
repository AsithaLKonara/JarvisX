"""
JARVIS AI - System Diagnostics Bot Skill
Real-time system health monitoring and diagnostics.
"""

import psutil
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from plugins.plugin_manager import PluginBase

class SystemDiagnosticsBot(PluginBase):
    """
    System Diagnostics Bot for monitoring and optimizing system health.
    Provides real-time CPU, RAM, disk monitoring and optimization recommendations.
    """
    
    def __init__(self):
        """Initialize System Diagnostics Bot."""
        super().__init__("SystemDiagnosticsBot", "1.0.0")
        
        # Update metadata
        self.metadata.update({
            'author': 'Jarvis AI Team',
            'description': 'Real-time system health monitoring and diagnostics',
            'category': 'system',
            'dependencies': ['psutil'],
            'compatibility': '1.0.0'
        })
        
        self.logger = logging.getLogger(f"skill.{self.name}")
        
        # Diagnostic thresholds
        self.thresholds = {
            'cpu_warning': 70,
            'cpu_critical': 90,
            'memory_warning': 80,
            'memory_critical': 95,
            'disk_warning': 85,
            'disk_critical': 95
        }
    
    def initialize(self, config: dict = None) -> bool:
        """Initialize the diagnostics bot."""
        try:
            self.logger.info(f"Initializing {self.name} skill")
            
            # Load configuration if provided
            if config:
                self.thresholds.update(config.get('thresholds', {}))
            
            return super().initialize(config)
        except Exception as e:
            self.logger.error(f"Error initializing {self.name} skill: {e}")
            return False
    
    def process_command(self, command: str, context: dict = None) -> dict:
        """Process system diagnostics commands."""
        try:
            command_lower = command.lower()
            
            # System health check
            if any(keyword in command_lower for keyword in ['health', 'status', 'diagnostics', 'system']):
                return self._get_system_health()
            
            # CPU monitoring
            elif any(keyword in command_lower for keyword in ['cpu', 'processor', 'performance']):
                return self._get_cpu_info()
            
            # Memory monitoring
            elif any(keyword in command_lower for keyword in ['memory', 'ram', 'usage']):
                return self._get_memory_info()
            
            # Disk monitoring
            elif any(keyword in command_lower for keyword in ['disk', 'storage', 'space']):
                return self._get_disk_info()
            
            # Process monitoring
            elif any(keyword in command_lower for keyword in ['process', 'processes', 'running']):
                return self._get_process_info()
            
            # Network monitoring
            elif any(keyword in command_lower for keyword in ['network', 'connection', 'internet']):
                return self._get_network_info()
            
            # Optimization recommendations
            elif any(keyword in command_lower for keyword in ['optimize', 'recommend', 'improve']):
                return self._get_optimization_recommendations()
            
            # General system info
            elif any(keyword in command_lower for keyword in ['info', 'details', 'overview']):
                return self._get_system_overview()
            
            else:
                return {
                    'success': False,
                    'message': f'{self.name} cannot process: {command}',
                    'data': {},
                    'confidence': 0.0
                }
        
        except Exception as e:
            self.logger.error(f"Error processing command in {self.name}: {e}")
            return {
                'success': False,
                'message': f'Error in {self.name}: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _get_system_health(self) -> dict:
        """Get comprehensive system health status."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate health score
            health_score = 100.0
            
            # CPU health
            if cpu_percent > self.thresholds['cpu_critical']:
                health_score -= 30
            elif cpu_percent > self.thresholds['cpu_warning']:
                health_score -= 15
            
            # Memory health
            if memory.percent > self.thresholds['memory_critical']:
                health_score -= 30
            elif memory.percent > self.thresholds['memory_warning']:
                health_score -= 15
            
            # Disk health
            if disk.percent > self.thresholds['disk_critical']:
                health_score -= 25
            elif disk.percent > self.thresholds['disk_warning']:
                health_score -= 10
            
            # Determine status
            if health_score >= 80:
                status = "Excellent"
                message = "System is running optimally"
            elif health_score >= 60:
                status = "Good"
                message = "System is running well with minor issues"
            elif health_score >= 40:
                status = "Fair"
                message = "System needs attention"
            else:
                status = "Poor"
                message = "System requires immediate attention"
            
            return {
                'success': True,
                'message': f'System Health: {status} ({health_score:.1f}/100) - {message}',
                'data': {
                    'health_score': health_score,
                    'status': status,
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'disk_usage': disk.percent,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            }
        
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return {
                'success': False,
                'message': f'Error checking system health: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _get_cpu_info(self) -> dict:
        """Get detailed CPU information."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Calculate average CPU usage
            avg_cpu = sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0
            
            # Determine CPU status
            if avg_cpu > self.thresholds['cpu_critical']:
                status = "Critical"
                message = "CPU usage is critically high"
            elif avg_cpu > self.thresholds['cpu_warning']:
                status = "Warning"
                message = "CPU usage is high"
            else:
                status = "Normal"
                message = "CPU usage is normal"
            
            return {
                'success': True,
                'message': f'CPU Status: {status} - {message}',
                'data': {
                    'cpu_count': cpu_count,
                    'cpu_usage_percent': avg_cpu,
                    'cpu_usage_per_core': cpu_percent,
                    'cpu_frequency': cpu_freq.current if cpu_freq else 'Unknown',
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            }
        
        except Exception as e:
            self.logger.error(f"Error getting CPU info: {e}")
            return {
                'success': False,
                'message': f'Error checking CPU: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _get_memory_info(self) -> dict:
        """Get detailed memory information."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Calculate memory usage percentage
            memory_percent = memory.percent
            
            # Determine memory status
            if memory_percent > self.thresholds['memory_critical']:
                status = "Critical"
                message = "Memory usage is critically high"
            elif memory_percent > self.thresholds['memory_warning']:
                status = "Warning"
                message = "Memory usage is high"
            else:
                status = "Normal"
                message = "Memory usage is normal"
            
            return {
                'success': True,
                'message': f'Memory Status: {status} - {message}',
                'data': {
                    'total_memory_gb': round(memory.total / (1024**3), 2),
                    'available_memory_gb': round(memory.available / (1024**3), 2),
                    'used_memory_gb': round(memory.used / (1024**3), 2),
                    'memory_usage_percent': memory_percent,
                    'swap_total_gb': round(swap.total / (1024**3), 2),
                    'swap_used_gb': round(swap.used / (1024**3), 2),
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            }
        
        except Exception as e:
            self.logger.error(f"Error getting memory info: {e}")
            return {
                'success': False,
                'message': f'Error checking memory: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _get_disk_info(self) -> dict:
        """Get detailed disk information."""
        try:
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Calculate disk usage percentage
            disk_percent = (disk.used / disk.total) * 100
            
            # Determine disk status
            if disk_percent > self.thresholds['disk_critical']:
                status = "Critical"
                message = "Disk space is critically low"
            elif disk_percent > self.thresholds['disk_warning']:
                status = "Warning"
                message = "Disk space is low"
            else:
                status = "Normal"
                message = "Disk space is adequate"
            
            return {
                'success': True,
                'message': f'Disk Status: {status} - {message}',
                'data': {
                    'total_disk_gb': round(disk.total / (1024**3), 2),
                    'used_disk_gb': round(disk.used / (1024**3), 2),
                    'free_disk_gb': round(disk.free / (1024**3), 2),
                    'disk_usage_percent': round(disk_percent, 2),
                    'disk_read_bytes': disk_io.read_bytes if disk_io else 0,
                    'disk_write_bytes': disk_io.write_bytes if disk_io else 0,
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            }
        
        except Exception as e:
            self.logger.error(f"Error getting disk info: {e}")
            return {
                'success': False,
                'message': f'Error checking disk: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _get_process_info(self) -> dict:
        """Get information about running processes."""
        try:
            processes = []
            
            # Get top 10 processes by CPU usage
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 0:  # Only include active processes
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            top_processes = processes[:10]
            
            return {
                'success': True,
                'message': f'Found {len(processes)} active processes',
                'data': {
                    'total_processes': len(processes),
                    'top_processes': top_processes,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error getting process info: {e}")
            return {
                'success': False,
                'message': f'Error checking processes: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _get_network_info(self) -> dict:
        """Get network information."""
        try:
            network_io = psutil.net_io_counters()
            network_connections = len(psutil.net_connections())
            
            return {
                'success': True,
                'message': 'Network information retrieved',
                'data': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_received': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_received': network_io.packets_recv,
                    'active_connections': network_connections,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error getting network info: {e}")
            return {
                'success': False,
                'message': f'Error checking network: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _get_optimization_recommendations(self) -> dict:
        """Get system optimization recommendations."""
        try:
            recommendations = []
            
            # Get current system state
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # CPU recommendations
            if cpu_percent > self.thresholds['cpu_critical']:
                recommendations.append("Close unnecessary applications to reduce CPU usage")
            elif cpu_percent > self.thresholds['cpu_warning']:
                recommendations.append("Monitor CPU usage and consider closing some applications")
            
            # Memory recommendations
            if memory.percent > self.thresholds['memory_critical']:
                recommendations.append("Free up memory by closing applications or restarting the system")
            elif memory.percent > self.thresholds['memory_warning']:
                recommendations.append("Consider closing some applications to free up memory")
            
            # Disk recommendations
            if disk.percent > self.thresholds['disk_critical']:
                recommendations.append("Free up disk space immediately - system is critically low on storage")
            elif disk.percent > self.thresholds['disk_warning']:
                recommendations.append("Consider cleaning up files to free up disk space")
            
            # General recommendations
            if not recommendations:
                recommendations.append("System is running optimally - no immediate optimizations needed")
            
            return {
                'success': True,
                'message': f'Generated {len(recommendations)} optimization recommendations',
                'data': {
                    'recommendations': recommendations,
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'disk_usage': (disk.used / disk.total) * 100,
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error getting optimization recommendations: {e}")
            return {
                'success': False,
                'message': f'Error generating recommendations: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _get_system_overview(self) -> dict:
        """Get comprehensive system overview."""
        try:
            # Get all system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            boot_time = psutil.boot_time()
            
            # Calculate uptime
            uptime_seconds = datetime.now().timestamp() - boot_time
            uptime_hours = uptime_seconds / 3600
            
            return {
                'success': True,
                'message': 'System overview generated',
                'data': {
                    'cpu_usage': cpu_percent,
                    'memory_total_gb': round(memory.total / (1024**3), 2),
                    'memory_used_gb': round(memory.used / (1024**3), 2),
                    'memory_usage_percent': memory.percent,
                    'disk_total_gb': round(disk.total / (1024**3), 2),
                    'disk_used_gb': round(disk.used / (1024**3), 2),
                    'disk_free_gb': round(disk.free / (1024**3), 2),
                    'disk_usage_percent': (disk.used / disk.total) * 100,
                    'uptime_hours': round(uptime_hours, 2),
                    'boot_time': datetime.fromtimestamp(boot_time).isoformat(),
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            }
        
        except Exception as e:
            self.logger.error(f"Error getting system overview: {e}")
            return {
                'success': False,
                'message': f'Error generating system overview: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def get_capabilities(self) -> list:
        """Get skill capabilities."""
        return [
            "System health monitoring",
            "CPU usage analysis",
            "Memory usage tracking",
            "Disk space monitoring",
            "Process management",
            "Network diagnostics",
            "Optimization recommendations",
            "Real-time system metrics"
        ]
