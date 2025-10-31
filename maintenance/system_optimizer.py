"""
JARVIS AI - System Optimizer
Advanced system optimization and performance monitoring.
"""

import os
import json
import logging
import time
import psutil
import gc
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import shutil

class SystemOptimizer:
    """
    Advanced system optimizer for Jarvis AI.
    Monitors performance, optimizes resources, and maintains system health.
    """
    
    def __init__(self):
        """Initialize system optimizer."""
        self.logger = logging.getLogger(__name__)
        self.optimization_history = []
        self.performance_metrics = {}
        
        # Optimization settings
        self.optimization_settings = {
            'memory_cleanup_threshold': 0.8,  # 80% memory usage
            'disk_cleanup_threshold': 0.9,    # 90% disk usage
            'log_rotation_size': 10 * 1024 * 1024,  # 10MB
            'cache_cleanup_interval': 3600,   # 1 hour
            'performance_check_interval': 300  # 5 minutes
        }
        
        self.logger.info("System Optimizer initialized")
    
    def optimize_system(self) -> Dict:
        """Perform comprehensive system optimization."""
        try:
            self.logger.info("Starting system optimization...")
            
            optimization_results = {
                'timestamp': datetime.now().isoformat(),
                'memory_optimization': self._optimize_memory(),
                'disk_optimization': self._optimize_disk_space(),
                'database_optimization': self._optimize_databases(),
                'log_optimization': self._optimize_logs(),
                'cache_optimization': self._optimize_cache(),
                'performance_metrics': self._get_performance_metrics()
            }
            
            # Store optimization history
            self.optimization_history.append(optimization_results)
            
            # Cleanup old optimization history
            if len(self.optimization_history) > 100:
                self.optimization_history = self.optimization_history[-50:]
            
            self.logger.info("System optimization completed")
            return optimization_results
        
        except Exception as e:
            self.logger.error(f"Error during system optimization: {e}")
            return {'error': str(e)}
    
    def _optimize_memory(self) -> Dict:
        """Optimize memory usage."""
        try:
            # Get current memory usage
            memory_info = psutil.virtual_memory()
            initial_usage = memory_info.percent
            
            # Force garbage collection
            collected = gc.collect()
            
            # Get memory usage after cleanup
            memory_info_after = psutil.virtual_memory()
            final_usage = memory_info_after.percent
            
            # Calculate improvement
            improvement = initial_usage - final_usage
            
            result = {
                'initial_usage': initial_usage,
                'final_usage': final_usage,
                'improvement': improvement,
                'garbage_collected': collected,
                'status': 'success' if improvement > 0 else 'no_change'
            }
            
            self.logger.info(f"Memory optimization: {improvement:.1f}% improvement")
            return result
        
        except Exception as e:
            self.logger.error(f"Error optimizing memory: {e}")
            return {'error': str(e)}
    
    def _optimize_disk_space(self) -> Dict:
        """Optimize disk space usage."""
        try:
            # Get disk usage
            disk_usage = psutil.disk_usage('/')
            initial_usage = disk_usage.percent
            
            # Clean up temporary files
            temp_files_cleaned = self._cleanup_temp_files()
            
            # Clean up old logs
            log_files_cleaned = self._cleanup_old_logs()
            
            # Clean up cache files
            cache_files_cleaned = self._cleanup_cache_files()
            
            # Get disk usage after cleanup
            disk_usage_after = psutil.disk_usage('/')
            final_usage = disk_usage_after.percent
            
            # Calculate space freed
            space_freed = (initial_usage - final_usage) * disk_usage.total / 100
            
            result = {
                'initial_usage': initial_usage,
                'final_usage': final_usage,
                'space_freed_mb': space_freed / (1024 * 1024),
                'temp_files_cleaned': temp_files_cleaned,
                'log_files_cleaned': log_files_cleaned,
                'cache_files_cleaned': cache_files_cleaned,
                'status': 'success' if space_freed > 0 else 'no_change'
            }
            
            self.logger.info(f"Disk optimization: {space_freed / (1024 * 1024):.1f} MB freed")
            return result
        
        except Exception as e:
            self.logger.error(f"Error optimizing disk space: {e}")
            return {'error': str(e)}
    
    def _optimize_databases(self) -> Dict:
        """Optimize database performance."""
        try:
            optimization_results = {}
            
            # Find and optimize SQLite databases
            db_files = list(Path('.').rglob('*.db')) + list(Path('.').rglob('*.sqlite'))
            
            for db_file in db_files:
                try:
                    # Connect to database
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    
                    # Get initial size
                    initial_size = db_file.stat().st_size
                    
                    # Run VACUUM to optimize database
                    cursor.execute("VACUUM")
                    
                    # Run ANALYZE to update statistics
                    cursor.execute("ANALYZE")
                    
                    # Close connection
                    conn.close()
                    
                    # Get final size
                    final_size = db_file.stat().st_size
                    size_reduction = initial_size - final_size
                    
                    optimization_results[str(db_file)] = {
                        'initial_size': initial_size,
                        'final_size': final_size,
                        'size_reduction': size_reduction,
                        'status': 'success'
                    }
                    
                    self.logger.info(f"Database {db_file} optimized: {size_reduction} bytes freed")
                
                except Exception as e:
                    optimization_results[str(db_file)] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            return {
                'databases_optimized': len(optimization_results),
                'results': optimization_results,
                'status': 'success'
            }
        
        except Exception as e:
            self.logger.error(f"Error optimizing databases: {e}")
            return {'error': str(e)}
    
    def _optimize_logs(self) -> Dict:
        """Optimize log files."""
        try:
            log_files_processed = 0
            total_size_freed = 0
            
            # Find log files
            log_files = list(Path('.').rglob('*.log')) + list(Path('.').rglob('*.txt'))
            
            for log_file in log_files:
                try:
                    # Get file size
                    file_size = log_file.stat().st_size
                    
                    # If file is larger than threshold, rotate it
                    if file_size > self.optimization_settings['log_rotation_size']:
                        # Create backup
                        backup_file = log_file.with_suffix('.log.backup')
                        shutil.move(log_file, backup_file)
                        
                        # Create new empty log file
                        log_file.touch()
                        
                        log_files_processed += 1
                        total_size_freed += file_size
                        
                        self.logger.info(f"Log file rotated: {log_file}")
                
                except Exception as e:
                    self.logger.warning(f"Error processing log file {log_file}: {e}")
            
            return {
                'log_files_processed': log_files_processed,
                'size_freed_mb': total_size_freed / (1024 * 1024),
                'status': 'success'
            }
        
        except Exception as e:
            self.logger.error(f"Error optimizing logs: {e}")
            return {'error': str(e)}
    
    def _optimize_cache(self) -> Dict:
        """Optimize cache files."""
        try:
            cache_dirs = ['cache', 'temp', '__pycache__', '.pytest_cache']
            cache_files_cleaned = 0
            total_size_freed = 0
            
            for cache_dir in cache_dirs:
                cache_path = Path(cache_dir)
                if cache_path.exists():
                    for file_path in cache_path.rglob('*'):
                        if file_path.is_file():
                            try:
                                file_size = file_path.stat().st_size
                                file_path.unlink()
                                cache_files_cleaned += 1
                                total_size_freed += file_size
                            except Exception as e:
                                self.logger.warning(f"Error removing cache file {file_path}: {e}")
            
            return {
                'cache_files_cleaned': cache_files_cleaned,
                'size_freed_mb': total_size_freed / (1024 * 1024),
                'status': 'success'
            }
        
        except Exception as e:
            self.logger.error(f"Error optimizing cache: {e}")
            return {'error': str(e)}
    
    def _cleanup_temp_files(self) -> int:
        """Clean up temporary files."""
        try:
            temp_files_cleaned = 0
            temp_dirs = ['temp', 'tmp', '.tmp']
            
            for temp_dir in temp_dirs:
                temp_path = Path(temp_dir)
                if temp_path.exists():
                    for file_path in temp_path.rglob('*'):
                        if file_path.is_file():
                            try:
                                file_path.unlink()
                                temp_files_cleaned += 1
                            except Exception as e:
                                self.logger.warning(f"Error removing temp file {file_path}: {e}")
            
            return temp_files_cleaned
        
        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {e}")
            return 0
    
    def _cleanup_old_logs(self) -> int:
        """Clean up old log files."""
        try:
            log_files_cleaned = 0
            log_files = list(Path('.').rglob('*.log'))
            
            # Remove logs older than 7 days
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for log_file in log_files:
                try:
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        log_file.unlink()
                        log_files_cleaned += 1
                except Exception as e:
                    self.logger.warning(f"Error removing old log {log_file}: {e}")
            
            return log_files_cleaned
        
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")
            return 0
    
    def _cleanup_cache_files(self) -> int:
        """Clean up cache files."""
        try:
            cache_files_cleaned = 0
            cache_patterns = ['*.pyc', '*.pyo', '__pycache__', '.pytest_cache']
            
            for pattern in cache_patterns:
                for file_path in Path('.').rglob(pattern):
                    try:
                        if file_path.is_file():
                            file_path.unlink()
                            cache_files_cleaned += 1
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)
                            cache_files_cleaned += 1
                    except Exception as e:
                        self.logger.warning(f"Error removing cache {file_path}: {e}")
            
            return cache_files_cleaned
        
        except Exception as e:
            self.logger.error(f"Error cleaning up cache files: {e}")
            return 0
    
    def _get_performance_metrics(self) -> Dict:
        """Get current performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available_mb': memory.available / (1024 * 1024),
                'disk_usage': disk.percent,
                'disk_free_mb': disk.free / (1024 * 1024),
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {'error': str(e)}
    
    def get_system_health(self) -> Dict:
        """Get comprehensive system health report."""
        try:
            health_report = {
                'timestamp': datetime.now().isoformat(),
                'performance_metrics': self._get_performance_metrics(),
                'optimization_history': self.optimization_history[-10:],  # Last 10 optimizations
                'health_score': self._calculate_health_score(),
                'recommendations': self._generate_health_recommendations()
            }
            
            return health_report
        
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return {'error': str(e)}
    
    def _calculate_health_score(self) -> float:
        """Calculate overall system health score."""
        try:
            metrics = self._get_performance_metrics()
            
            # Base score
            health_score = 100.0
            
            # CPU penalty
            cpu_usage = metrics.get('cpu_usage', 0)
            if cpu_usage > 80:
                health_score -= 20
            elif cpu_usage > 60:
                health_score -= 10
            
            # Memory penalty
            memory_usage = metrics.get('memory_usage', 0)
            if memory_usage > 90:
                health_score -= 30
            elif memory_usage > 80:
                health_score -= 15
            
            # Disk penalty
            disk_usage = metrics.get('disk_usage', 0)
            if disk_usage > 95:
                health_score -= 25
            elif disk_usage > 85:
                health_score -= 10
            
            return max(health_score, 0.0)
        
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 0.0
    
    def _generate_health_recommendations(self) -> List[str]:
        """Generate health recommendations based on current metrics."""
        try:
            recommendations = []
            metrics = self._get_performance_metrics()
            
            # CPU recommendations
            cpu_usage = metrics.get('cpu_usage', 0)
            if cpu_usage > 80:
                recommendations.append("High CPU usage detected - consider reducing active processes")
            elif cpu_usage > 60:
                recommendations.append("Moderate CPU usage - monitor for performance issues")
            
            # Memory recommendations
            memory_usage = metrics.get('memory_usage', 0)
            if memory_usage > 90:
                recommendations.append("Critical memory usage - immediate cleanup recommended")
            elif memory_usage > 80:
                recommendations.append("High memory usage - consider memory optimization")
            
            # Disk recommendations
            disk_usage = metrics.get('disk_usage', 0)
            if disk_usage > 95:
                recommendations.append("Critical disk space - immediate cleanup required")
            elif disk_usage > 85:
                recommendations.append("Low disk space - cleanup recommended")
            
            # General recommendations
            if not recommendations:
                recommendations.append("System health is good - continue monitoring")
            
            return recommendations
        
        except Exception as e:
            self.logger.error(f"Error generating health recommendations: {e}")
            return ["Error generating recommendations"]
    
    def schedule_optimization(self, interval_hours: int = 24) -> bool:
        """Schedule automatic optimization."""
        try:
            # This would typically use a scheduler like APScheduler
            # For now, we'll just log the scheduling
            self.logger.info(f"Optimization scheduled for every {interval_hours} hours")
            return True
        
        except Exception as e:
            self.logger.error(f"Error scheduling optimization: {e}")
            return False
    
    def export_optimization_report(self, output_file: str = "optimization_report.json") -> bool:
        """Export optimization report to file."""
        try:
            report = {
                'optimization_history': self.optimization_history,
                'current_metrics': self._get_performance_metrics(),
                'health_score': self._calculate_health_score(),
                'recommendations': self._generate_health_recommendations(),
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Optimization report exported to: {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting optimization report: {e}")
            return False
