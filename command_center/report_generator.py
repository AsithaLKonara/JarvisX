"""
Report Generator - Creates system reports and summaries
Phase 1 of Jarvis X V2
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
import json

class ReportGenerator:
    """Generates various system reports"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
    
    def generate_system_status_report(self, hub_status: Dict[str, Any], 
                                    task_stats: Dict[str, int]) -> Dict[str, Any]:
        """Generate system status report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_status': hub_status,
            'task_statistics': task_stats,
            'uptime': hub_status.get('uptime', 'unknown'),
            'active_mode': hub_status.get('active_mode', 'none'),
            'total_tasks': sum(task_stats.values())
        }
        return report
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily activity report"""
        today = datetime.now().date()
        report = {
            'date': today.isoformat(),
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_operations': 0,
                'successful_operations': 0,
                'failed_operations': 0,
                'modes_used': []
            },
            'recommendations': []
        }
        return report
    
    def generate_performance_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': metrics,
            'analysis': {
                'cpu_usage': metrics.get('cpu_usage', 0),
                'memory_usage': metrics.get('memory_usage', 0),
                'disk_usage': metrics.get('disk_usage', 0)
            },
            'recommendations': self._analyze_performance(metrics)
        }
        return report
    
    def _analyze_performance(self, metrics: Dict[str, Any]) -> List[str]:
        """Analyze performance metrics and provide recommendations"""
        recommendations = []
        
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > 80:
            recommendations.append("High CPU usage detected - consider optimizing processes")
        
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > 90:
            recommendations.append("High memory usage - consider freeing up resources")
        
        disk_usage = metrics.get('disk_usage', 0)
        if disk_usage > 85:
            recommendations.append("High disk usage - consider cleaning up files")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: str) -> bool:
        """Save report to file"""
        try:
            report_file = self.log_dir / filename
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False



