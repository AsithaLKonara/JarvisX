"""
JARVIS AI - System Monitor
Background system monitoring and health tracking.
"""

import json
import logging
import os
import psutil
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path

class HealthStatus(Enum):
    """System health status levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"

class MetricType(Enum):
    """Types of system metrics."""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    PROCESS_COUNT = "process_count"
    TEMPERATURE = "temperature"
    UPTIME = "uptime"
    ERROR_RATE = "error_rate"

@dataclass
class SystemMetric:
    """Individual system metric reading."""
    metric_id: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    status: HealthStatus
    threshold_warning: float
    threshold_critical: float
    description: str

@dataclass
class SystemHealth:
    """Overall system health status."""
    health_id: str
    timestamp: datetime
    overall_status: HealthStatus
    overall_score: float
    metrics: List[SystemMetric]
    alerts: List[str]
    recommendations: List[str]
    uptime_seconds: float
    system_info: Dict[str, Any]

@dataclass
class AlertRule:
    """Alert rule configuration."""
    rule_id: str
    metric_type: MetricType
    condition: str  # "greater_than", "less_than", "equals"
    threshold: float
    severity: HealthStatus
    message: str
    enabled: bool = True

class SystemMonitor:
    """
    Background system monitor for continuous health tracking.
    Monitors CPU, memory, disk, network, and other system metrics.
    """
    
    def __init__(self, monitoring_interval: int = 30, alert_callbacks: List[Callable] = None):
        """Initialize System Monitor."""
        self.logger = logging.getLogger(__name__)
        self.monitoring_interval = monitoring_interval
        self.alert_callbacks = alert_callbacks or []
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.monitoring_data = []
        self.health_history = []
        
        # Alert rules
        self.alert_rules = self._create_default_alert_rules()
        
        # System thresholds
        self.thresholds = {
            MetricType.CPU_USAGE: {"warning": 70.0, "critical": 90.0},
            MetricType.MEMORY_USAGE: {"warning": 80.0, "critical": 95.0},
            MetricType.DISK_USAGE: {"warning": 85.0, "critical": 95.0},
            MetricType.PROCESS_COUNT: {"warning": 200, "critical": 300},
            MetricType.ERROR_RATE: {"warning": 5.0, "critical": 10.0}
        }
        
        # Create monitoring directories
        self._create_monitoring_structure()
        
        self.logger.info("System Monitor initialized")
    
    def _create_monitoring_structure(self):
        """Create monitoring directory structure."""
        try:
            directories = [
                'monitoring',
                'monitoring/metrics',
                'monitoring/alerts',
                'monitoring/reports',
                'monitoring/logs'
            ]
            
            for directory in directories:
                dir_path = Path(directory)
                dir_path.mkdir(exist_ok=True)
            
            self.logger.info("Monitoring structure created")
        
        except Exception as e:
            self.logger.error(f"Error creating monitoring structure: {e}")
    
    def _create_default_alert_rules(self) -> List[AlertRule]:
        """Create default alert rules."""
        return [
            AlertRule(
                rule_id="cpu_high",
                metric_type=MetricType.CPU_USAGE,
                condition="greater_than",
                threshold=80.0,
                severity=HealthStatus.WARNING,
                message="High CPU usage detected"
            ),
            AlertRule(
                rule_id="memory_high",
                metric_type=MetricType.MEMORY_USAGE,
                condition="greater_than",
                threshold=85.0,
                severity=HealthStatus.WARNING,
                message="High memory usage detected"
            ),
            AlertRule(
                rule_id="disk_full",
                metric_type=MetricType.DISK_USAGE,
                condition="greater_than",
                threshold=90.0,
                severity=HealthStatus.CRITICAL,
                message="Disk space critically low"
            ),
            AlertRule(
                rule_id="process_count_high",
                metric_type=MetricType.PROCESS_COUNT,
                condition="greater_than",
                threshold=250,
                severity=HealthStatus.WARNING,
                message="High process count detected"
            )
        ]
    
    def start_monitoring(self):
        """Start background monitoring."""
        try:
            if self.is_monitoring:
                self.logger.warning("Monitoring already started")
                return
            
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            self.logger.info("System monitoring started")
        
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
            self.is_monitoring = False
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        try:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            
            self.logger.info("System monitoring stopped")
        
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        try:
            while self.is_monitoring:
                # Collect system metrics
                health = self._collect_system_health()
                
                # Store health data
                self.health_history.append(health)
                self.monitoring_data.append(health)
                
                # Check for alerts
                self._check_alerts(health)
                
                # Clean up old data (keep last 1000 entries)
                if len(self.monitoring_data) > 1000:
                    self.monitoring_data = self.monitoring_data[-1000:]
                
                if len(self.health_history) > 100:
                    self.health_history = self.health_history[-100:]
                
                # Save monitoring data
                self._save_monitoring_data(health)
                
                # Wait for next interval
                time.sleep(self.monitoring_interval)
        
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
            self.is_monitoring = False
    
    def _collect_system_health(self) -> SystemHealth:
        """Collect comprehensive system health data."""
        try:
            health_id = f"health_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.now()
            
            # Collect metrics
            metrics = []
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_metric = SystemMetric(
                metric_id=f"cpu_{uuid.uuid4().hex[:8]}",
                metric_type=MetricType.CPU_USAGE,
                value=cpu_percent,
                unit="%",
                timestamp=timestamp,
                status=self._get_metric_status(cpu_percent, MetricType.CPU_USAGE),
                threshold_warning=self.thresholds[MetricType.CPU_USAGE]["warning"],
                threshold_critical=self.thresholds[MetricType.CPU_USAGE]["critical"],
                description="CPU usage percentage"
            )
            metrics.append(cpu_metric)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_metric = SystemMetric(
                metric_id=f"memory_{uuid.uuid4().hex[:8]}",
                metric_type=MetricType.MEMORY_USAGE,
                value=memory.percent,
                unit="%",
                timestamp=timestamp,
                status=self._get_metric_status(memory.percent, MetricType.MEMORY_USAGE),
                threshold_warning=self.thresholds[MetricType.MEMORY_USAGE]["warning"],
                threshold_critical=self.thresholds[MetricType.MEMORY_USAGE]["critical"],
                description="Memory usage percentage"
            )
            metrics.append(memory_metric)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_metric = SystemMetric(
                metric_id=f"disk_{uuid.uuid4().hex[:8]}",
                metric_type=MetricType.DISK_USAGE,
                value=(disk.used / disk.total) * 100,
                unit="%",
                timestamp=timestamp,
                status=self._get_metric_status((disk.used / disk.total) * 100, MetricType.DISK_USAGE),
                threshold_warning=self.thresholds[MetricType.DISK_USAGE]["warning"],
                threshold_critical=self.thresholds[MetricType.DISK_USAGE]["critical"],
                description="Disk usage percentage"
            )
            metrics.append(disk_metric)
            
            # Process count
            process_count = len(psutil.pids())
            process_metric = SystemMetric(
                metric_id=f"process_{uuid.uuid4().hex[:8]}",
                metric_type=MetricType.PROCESS_COUNT,
                value=process_count,
                unit="count",
                timestamp=timestamp,
                status=self._get_metric_status(process_count, MetricType.PROCESS_COUNT),
                threshold_warning=self.thresholds[MetricType.PROCESS_COUNT]["warning"],
                threshold_critical=self.thresholds[MetricType.PROCESS_COUNT]["critical"],
                description="Number of running processes"
            )
            metrics.append(process_metric)
            
            # Network I/O
            network = psutil.net_io_counters()
            network_metric = SystemMetric(
                metric_id=f"network_{uuid.uuid4().hex[:8]}",
                metric_type=MetricType.NETWORK_IO,
                value=network.bytes_sent + network.bytes_recv,
                unit="bytes",
                timestamp=timestamp,
                status=HealthStatus.GOOD,  # Network I/O doesn't have standard thresholds
                threshold_warning=0,
                threshold_critical=0,
                description="Total network I/O bytes"
            )
            metrics.append(network_metric)
            
            # System uptime
            uptime = time.time() - psutil.boot_time()
            uptime_metric = SystemMetric(
                metric_id=f"uptime_{uuid.uuid4().hex[:8]}",
                metric_type=MetricType.UPTIME,
                value=uptime,
                unit="seconds",
                timestamp=timestamp,
                status=HealthStatus.GOOD,
                threshold_warning=0,
                threshold_critical=0,
                description="System uptime in seconds"
            )
            metrics.append(uptime_metric)
            
            # Calculate overall health
            overall_status, overall_score = self._calculate_overall_health(metrics)
            
            # Generate alerts and recommendations
            alerts = self._generate_alerts(metrics)
            recommendations = self._generate_recommendations(metrics)
            
            # System information
            system_info = {
                "platform": psutil.WINDOWS if os.name == 'nt' else psutil.LINUX if os.name == 'posix' else "unknown",
                "cpu_count": psutil.cpu_count(),
                "total_memory": psutil.virtual_memory().total,
                "total_disk": disk.total,
                "boot_time": psutil.boot_time()
            }
            
            return SystemHealth(
                health_id=health_id,
                timestamp=timestamp,
                overall_status=overall_status,
                overall_score=overall_score,
                metrics=metrics,
                alerts=alerts,
                recommendations=recommendations,
                uptime_seconds=uptime,
                system_info=system_info
            )
        
        except Exception as e:
            self.logger.error(f"Error collecting system health: {e}")
            return self._create_error_health_status(str(e))
    
    def _get_metric_status(self, value: float, metric_type: MetricType) -> HealthStatus:
        """Determine health status based on metric value and thresholds."""
        try:
            thresholds = self.thresholds.get(metric_type, {"warning": 0, "critical": 0})
            
            if value >= thresholds["critical"]:
                return HealthStatus.CRITICAL
            elif value >= thresholds["warning"]:
                return HealthStatus.WARNING
            else:
                return HealthStatus.GOOD
        
        except Exception as e:
            self.logger.error(f"Error determining metric status: {e}")
            return HealthStatus.WARNING
    
    def _calculate_overall_health(self, metrics: List[SystemMetric]) -> tuple[HealthStatus, float]:
        """Calculate overall system health status and score."""
        try:
            if not metrics:
                return HealthStatus.FAILED, 0.0
            
            # Count statuses
            status_counts = {
                HealthStatus.EXCELLENT: 0,
                HealthStatus.GOOD: 0,
                HealthStatus.WARNING: 0,
                HealthStatus.CRITICAL: 0,
                HealthStatus.FAILED: 0
            }
            
            for metric in metrics:
                status_counts[metric.status] += 1
            
            total_metrics = len(metrics)
            
            # Calculate score (0-100)
            score = (
                status_counts[HealthStatus.EXCELLENT] * 100 +
                status_counts[HealthStatus.GOOD] * 80 +
                status_counts[HealthStatus.WARNING] * 50 +
                status_counts[HealthStatus.CRITICAL] * 20 +
                status_counts[HealthStatus.FAILED] * 0
            ) / total_metrics
            
            # Determine overall status
            if status_counts[HealthStatus.CRITICAL] > 0 or status_counts[HealthStatus.FAILED] > 0:
                overall_status = HealthStatus.CRITICAL
            elif status_counts[HealthStatus.WARNING] > total_metrics * 0.3:
                overall_status = HealthStatus.WARNING
            elif status_counts[HealthStatus.GOOD] > total_metrics * 0.7:
                overall_status = HealthStatus.GOOD
            else:
                overall_status = HealthStatus.EXCELLENT
            
            return overall_status, score
        
        except Exception as e:
            self.logger.error(f"Error calculating overall health: {e}")
            return HealthStatus.FAILED, 0.0
    
    def _generate_alerts(self, metrics: List[SystemMetric]) -> List[str]:
        """Generate alerts based on metrics and rules."""
        try:
            alerts = []
            
            for metric in metrics:
                for rule in self.alert_rules:
                    if not rule.enabled or rule.metric_type != metric.metric_type:
                        continue
                    
                    # Check rule condition
                    condition_met = False
                    if rule.condition == "greater_than":
                        condition_met = metric.value > rule.threshold
                    elif rule.condition == "less_than":
                        condition_met = metric.value < rule.threshold
                    elif rule.condition == "equals":
                        condition_met = abs(metric.value - rule.threshold) < 0.01
                    
                    if condition_met and metric.status.value in [rule.severity.value, "critical"]:
                        alert_message = f"{rule.message}: {metric.value:.2f}{metric.unit} (threshold: {rule.threshold})"
                        alerts.append(alert_message)
            
            return alerts
        
        except Exception as e:
            self.logger.error(f"Error generating alerts: {e}")
            return []
    
    def _generate_recommendations(self, metrics: List[SystemMetric]) -> List[str]:
        """Generate recommendations based on metrics."""
        try:
            recommendations = []
            
            for metric in metrics:
                if metric.status == HealthStatus.CRITICAL:
                    if metric.metric_type == MetricType.CPU_USAGE:
                        recommendations.append("Consider closing unnecessary applications or upgrading CPU")
                    elif metric.metric_type == MetricType.MEMORY_USAGE:
                        recommendations.append("Consider closing memory-intensive applications or adding more RAM")
                    elif metric.metric_type == MetricType.DISK_USAGE:
                        recommendations.append("Free up disk space by deleting unnecessary files or adding storage")
                    elif metric.metric_type == MetricType.PROCESS_COUNT:
                        recommendations.append("Consider restarting the system to clean up processes")
                
                elif metric.status == HealthStatus.WARNING:
                    if metric.metric_type == MetricType.CPU_USAGE:
                        recommendations.append("Monitor CPU usage and consider optimizing applications")
                    elif metric.metric_type == MetricType.MEMORY_USAGE:
                        recommendations.append("Monitor memory usage and consider closing unused applications")
                    elif metric.metric_type == MetricType.DISK_USAGE:
                        recommendations.append("Consider cleaning up disk space soon")
            
            return recommendations
        
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _create_error_health_status(self, error_message: str) -> SystemHealth:
        """Create error health status when monitoring fails."""
        return SystemHealth(
            health_id=f"error_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            overall_status=HealthStatus.FAILED,
            overall_score=0.0,
            metrics=[],
            alerts=[f"Monitoring error: {error_message}"],
            recommendations=["Check system monitor configuration and restart if necessary"],
            uptime_seconds=0.0,
            system_info={}
        )
    
    def _check_alerts(self, health: SystemHealth):
        """Check for alerts and trigger callbacks."""
        try:
            if health.alerts:
                for alert in health.alerts:
                    self.logger.warning(f"System Alert: {alert}")
                    
                    # Trigger alert callbacks
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert, health)
                        except Exception as e:
                            self.logger.error(f"Error in alert callback: {e}")
        
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    def _save_monitoring_data(self, health: SystemHealth):
        """Save monitoring data to file."""
        try:
            # Save individual health record
            health_file = Path("monitoring/metrics") / f"health_{health.health_id}.json"
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(health), f, indent=2, ensure_ascii=False, default=str)
            
            # Save summary data
            summary_file = Path("monitoring") / "latest_health.json"
            summary_data = {
                "timestamp": health.timestamp.isoformat(),
                "overall_status": health.overall_status.value,
                "overall_score": health.overall_score,
                "alerts_count": len(health.alerts),
                "recommendations_count": len(health.recommendations),
                "uptime_seconds": health.uptime_seconds
            }
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error(f"Error saving monitoring data: {e}")
    
    def get_current_health(self) -> Optional[SystemHealth]:
        """Get current system health status."""
        try:
            if self.health_history:
                return self.health_history[-1]
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting current health: {e}")
            return None
    
    def get_health_history(self, hours: int = 24) -> List[SystemHealth]:
        """Get health history for specified hours."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return [health for health in self.health_history if health.timestamp >= cutoff_time]
        
        except Exception as e:
            self.logger.error(f"Error getting health history: {e}")
            return []
    
    def get_health_statistics(self) -> Dict[str, Any]:
        """Get health statistics."""
        try:
            if not self.health_history:
                return {"error": "No health data available"}
            
            total_records = len(self.health_history)
            status_counts = {}
            
            for health in self.health_history:
                status = health.overall_status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            avg_score = sum(health.overall_score for health in self.health_history) / total_records
            total_alerts = sum(len(health.alerts) for health in self.health_history)
            
            return {
                "total_records": total_records,
                "status_distribution": status_counts,
                "average_score": avg_score,
                "total_alerts": total_alerts,
                "monitoring_duration_hours": (self.health_history[-1].timestamp - self.health_history[0].timestamp).total_seconds() / 3600 if len(self.health_history) > 1 else 0
            }
        
        except Exception as e:
            self.logger.error(f"Error getting health statistics: {e}")
            return {}
    
    def add_alert_callback(self, callback: Callable):
        """Add alert callback function."""
        try:
            self.alert_callbacks.append(callback)
            self.logger.info("Alert callback added")
        
        except Exception as e:
            self.logger.error(f"Error adding alert callback: {e}")
    
    def update_thresholds(self, metric_type: MetricType, warning: float, critical: float):
        """Update thresholds for a metric type."""
        try:
            self.thresholds[metric_type] = {
                "warning": warning,
                "critical": critical
            }
            self.logger.info(f"Updated thresholds for {metric_type.value}")
        
        except Exception as e:
            self.logger.error(f"Error updating thresholds: {e}")
    
    def add_alert_rule(self, rule: AlertRule):
        """Add new alert rule."""
        try:
            self.alert_rules.append(rule)
            self.logger.info(f"Added alert rule: {rule.rule_id}")
        
        except Exception as e:
            self.logger.error(f"Error adding alert rule: {e}")
    
    def export_health_report(self, output_file: str = None) -> bool:
        """Export comprehensive health report."""
        try:
            if not output_file:
                output_file = f"monitoring/reports/health_report_{int(datetime.now().timestamp())}.json"
            
            report_data = {
                "report_timestamp": datetime.now().isoformat(),
                "monitoring_interval": self.monitoring_interval,
                "is_monitoring": self.is_monitoring,
                "health_statistics": self.get_health_statistics(),
                "current_health": self._serialize_health_data(self.get_current_health()) if self.get_current_health() else None,
                "alert_rules": [asdict(rule) for rule in self.alert_rules],
                "thresholds": {metric_type.value: thresholds for metric_type, thresholds in self.thresholds.items()}
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Health report exported: {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting health report: {e}")
            return False
    
    def _serialize_health_data(self, health: SystemHealth) -> dict:
        """Serialize health data for JSON export."""
        if not health:
            return None
        
        return {
            "health_id": health.health_id,
            "timestamp": health.timestamp.isoformat(),
            "overall_status": health.overall_status.value,
            "overall_score": health.overall_score,
            "metrics": [
                {
                    "metric_id": metric.metric_id,
                    "metric_type": metric.metric_type.value,
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp.isoformat(),
                    "status": metric.status.value,
                    "threshold_warning": metric.threshold_warning,
                    "threshold_critical": metric.threshold_critical,
                    "description": metric.description
                }
                for metric in health.metrics
            ],
            "alerts": [
                {
                    "alert_id": alert.alert_id,
                    "alert_type": alert.alert_type.value,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "metric_id": alert.metric_id,
                    "resolved": alert.resolved
                }
                for alert in health.alerts
            ],
            "recommendations": health.recommendations,
            "system_info": health.system_info
        }
