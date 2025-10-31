"""
System Monitor - Resource Monitor
CPU, memory, disk, and process tracking.
"""

import psutil
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class ResourceMonitor:
    """Monitor system resources"""
    
    def __init__(self):
        """Initialize resource monitor"""
        self.history = []
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0
        }
    
    def get_cpu_info(self) -> Dict:
        """Get CPU information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            return {
                'percent': cpu_percent,
                'count': cpu_count,
                'per_cpu': psutil.cpu_percent(percpu=True),
                'alert': cpu_percent > self.alert_thresholds['cpu_percent']
            }
        except Exception:
            return {'percent': 0, 'count': 0, 'per_cpu': [], 'alert': False}
    
    def get_memory_info(self) -> Dict:
        """Get memory information"""
        try:
            mem = psutil.virtual_memory()
            return {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'percent': mem.percent,
                'alert': mem.percent > self.alert_thresholds['memory_percent']
            }
        except Exception:
            return {'total': 0, 'available': 0, 'used': 0, 'percent': 0, 'alert': False}
    
    def get_disk_info(self, path: str = '/') -> Dict:
        """Get disk information"""
        try:
            disk = psutil.disk_usage(path)
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent,
                'alert': disk.percent > self.alert_thresholds['disk_percent']
            }
        except Exception:
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0, 'alert': False}
    
    def get_process_count(self) -> Dict:
        """Get process information"""
        try:
            return {
                'total': len(psutil.pids()),
                'top_10': self._get_top_processes()
            }
        except Exception:
            return {'total': 0, 'top_10': []}
    
    def _get_top_processes(self) -> List[Dict]:
        """Get top 10 processes by memory"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory_percent': proc.info['memory_percent']
                    })
                except psutil.NoSuchProcess:
                    pass
            return sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:10]
        except Exception:
            return []
    
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        timestamp = datetime.now().isoformat()
        stats = {
            'timestamp': timestamp,
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'processes': self.get_process_count()
        }
        self.history.append(stats)
        return stats
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get recent monitoring history"""
        return self.history[-limit:]
    
    def clear_history(self):
        """Clear monitoring history"""
        self.history = []
