"""
JARVIS AI - Health Reporter
Comprehensive health reporting and analytics system.
"""

import json
import logging
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

class ReportType(Enum):
    """Types of health reports."""
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ERROR_ANALYSIS = "error_analysis"
    RESOURCE_USAGE = "resource_usage"
    TREND_ANALYSIS = "trend_analysis"
    COMPREHENSIVE = "comprehensive"

class ReportFormat(Enum):
    """Report output formats."""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    CHART = "chart"

@dataclass
class HealthMetric:
    """Health metric data point."""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    status: str
    trend: str  # "improving", "stable", "declining"

@dataclass
class HealthReport:
    """Comprehensive health report."""
    report_id: str
    report_type: ReportType
    generated_at: datetime
    time_range: Tuple[datetime, datetime]
    overall_health_score: float
    system_status: str
    key_metrics: List[HealthMetric]
    alerts: List[str]
    recommendations: List[str]
    charts: List[str]
    summary: str

class HealthReporter:
    """
    Comprehensive health reporting and analytics system.
    Generates detailed reports on system health, performance, and trends.
    """
    
    def __init__(self, system_monitor=None, auto_repair=None, fallback_restore=None):
        """Initialize Health Reporter."""
        self.logger = logging.getLogger(__name__)
        self.system_monitor = system_monitor
        self.auto_repair = auto_repair
        self.fallback_restore = fallback_restore
        
        # Report storage
        self.reports = []
        self.report_templates = self._create_report_templates()
        
        # Create reporting directories
        self._create_reporting_structure()
        
        self.logger.info("Health Reporter initialized")
    
    def _create_reporting_structure(self):
        """Create reporting directory structure."""
        try:
            directories = [
                'reports',
                'reports/system',
                'reports/performance',
                'reports/errors',
                'reports/trends',
                'reports/charts',
                'reports/exports'
            ]
            
            for directory in directories:
                dir_path = Path(directory)
                dir_path.mkdir(exist_ok=True)
            
            self.logger.info("Reporting structure created")
        
        except Exception as e:
            self.logger.error(f"Error creating reporting structure: {e}")
    
    def _create_report_templates(self) -> Dict[str, str]:
        """Create report templates."""
        return {
            "system_health": """
# System Health Report

## Overview
- **Report Generated:** {timestamp}
- **Overall Health Score:** {health_score}/100
- **System Status:** {system_status}

## Key Metrics
{metrics_table}

## Alerts
{alerts_list}

## Recommendations
{recommendations_list}

## Summary
{summary}
""",
            
            "performance_analysis": """
# Performance Analysis Report

## Performance Overview
- **Average CPU Usage:** {avg_cpu}%
- **Average Memory Usage:** {avg_memory}%
- **Peak CPU Usage:** {peak_cpu}%
- **Peak Memory Usage:** {peak_memory}%

## Performance Trends
{performance_charts}

## Bottlenecks Identified
{bottlenecks}

## Optimization Recommendations
{optimization_recommendations}
""",
            
            "comprehensive": """
# Comprehensive Health Report

## Executive Summary
{executive_summary}

## System Health
{system_health_section}

## Performance Analysis
{performance_section}

## Error Analysis
{error_section}

## Resource Usage
{resource_section}

## Trends and Patterns
{trends_section}

## Recommendations
{recommendations_section}

## Action Items
{action_items}
"""
        }
    
    def generate_report(self, report_type: ReportType, time_range_hours: int = 24, 
                       format: ReportFormat = ReportFormat.HTML) -> Optional[HealthReport]:
        """Generate comprehensive health report."""
        try:
            self.logger.info(f"Generating {report_type.value} report for last {time_range_hours} hours")
            
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_range_hours)
            
            # Collect data
            health_data = self._collect_health_data(start_time, end_time)
            performance_data = self._collect_performance_data(start_time, end_time)
            error_data = self._collect_error_data(start_time, end_time)
            
            # Generate report
            report_id = f"report_{uuid.uuid4().hex[:8]}"
            
            report = HealthReport(
                report_id=report_id,
                report_type=report_type,
                generated_at=datetime.now(),
                time_range=(start_time, end_time),
                overall_health_score=self._calculate_overall_health_score(health_data),
                system_status=self._determine_system_status(health_data),
                key_metrics=self._extract_key_metrics(health_data),
                alerts=self._generate_alerts(health_data, error_data),
                recommendations=self._generate_recommendations(health_data, performance_data),
                charts=[],
                summary=""
            )
            
            # Generate charts if requested
            if format == ReportFormat.CHART:
                report.charts = self._generate_charts(health_data, performance_data)
            
            # Generate summary
            report.summary = self._generate_summary(report)
            
            # Store report
            self.reports.append(report)
            
            # Export report
            self._export_report(report, format)
            
            self.logger.info(f"Report generated: {report_id}")
            return report
        
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return None
    
    def _collect_health_data(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Collect health data for the specified time range."""
        try:
            health_data = []
            
            if self.system_monitor:
                # Get health history from system monitor
                health_history = self.system_monitor.get_health_history(
                    hours=int((end_time - start_time).total_seconds() / 3600)
                )
                
                for health in health_history:
                    if start_time <= health.timestamp <= end_time:
                        health_data.append({
                            "timestamp": health.timestamp,
                            "overall_score": health.overall_score,
                            "overall_status": health.overall_status.value,
                            "metrics": [
                                {
                                    "type": metric.metric_type.value,
                                    "value": metric.value,
                                    "unit": metric.unit,
                                    "status": metric.status.value
                                }
                                for metric in health.metrics
                            ],
                            "alerts": health.alerts,
                            "recommendations": health.recommendations
                        })
            
            return health_data
        
        except Exception as e:
            self.logger.error(f"Error collecting health data: {e}")
            return []
    
    def _collect_performance_data(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Collect performance data for the specified time range."""
        try:
            performance_data = []
            
            if self.system_monitor:
                health_history = self.system_monitor.get_health_history(
                    hours=int((end_time - start_time).total_seconds() / 3600)
                )
                
                for health in health_history:
                    if start_time <= health.timestamp <= end_time:
                        # Extract performance metrics
                        cpu_metric = next((m for m in health.metrics if m.metric_type.value == "cpu_usage"), None)
                        memory_metric = next((m for m in health.metrics if m.metric_type.value == "memory_usage"), None)
                        disk_metric = next((m for m in health.metrics if m.metric_type.value == "disk_usage"), None)
                        
                        if cpu_metric or memory_metric or disk_metric:
                            performance_data.append({
                                "timestamp": health.timestamp,
                                "cpu_usage": cpu_metric.value if cpu_metric else 0,
                                "memory_usage": memory_metric.value if memory_metric else 0,
                                "disk_usage": disk_metric.value if disk_metric else 0,
                                "uptime": health.uptime_seconds
                            })
            
            return performance_data
        
        except Exception as e:
            self.logger.error(f"Error collecting performance data: {e}")
            return []
    
    def _collect_error_data(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Collect error data for the specified time range."""
        try:
            error_data = []
            
            # Collect from system monitor alerts
            if self.system_monitor:
                health_history = self.system_monitor.get_health_history(
                    hours=int((end_time - start_time).total_seconds() / 3600)
                )
                
                for health in health_history:
                    if start_time <= health.timestamp <= end_time and health.alerts:
                        for alert in health.alerts:
                            error_data.append({
                                "timestamp": health.timestamp,
                                "alert": alert,
                                "severity": "warning" if "warning" in alert.lower() else "error",
                                "component": "system"
                            })
            
            # Collect from auto repair system
            if self.auto_repair:
                repair_history = self.auto_repair.get_repair_history(
                    hours=int((end_time - start_time).total_seconds() / 3600)
                )
                
                for session in repair_history:
                    for action in session.actions:
                        if not action.success and action.error_message:
                            error_data.append({
                                "timestamp": action.start_time or session.start_time,
                                "alert": action.error_message,
                                "severity": "error",
                                "component": "repair"
                            })
            
            return error_data
        
        except Exception as e:
            self.logger.error(f"Error collecting error data: {e}")
            return []
    
    def _calculate_overall_health_score(self, health_data: List[Dict[str, Any]]) -> float:
        """Calculate overall health score from health data."""
        try:
            if not health_data:
                return 0.0
            
            scores = [data["overall_score"] for data in health_data]
            return sum(scores) / len(scores)
        
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 0.0
    
    def _determine_system_status(self, health_data: List[Dict[str, Any]]) -> str:
        """Determine overall system status."""
        try:
            if not health_data:
                return "unknown"
            
            # Get latest status
            latest_data = health_data[-1]
            return latest_data["overall_status"]
        
        except Exception as e:
            self.logger.error(f"Error determining system status: {e}")
            return "unknown"
    
    def _extract_key_metrics(self, health_data: List[Dict[str, Any]]) -> List[HealthMetric]:
        """Extract key metrics from health data."""
        try:
            key_metrics = []
            
            if not health_data:
                return key_metrics
            
            # Get latest metrics
            latest_data = health_data[-1]
            
            for metric_data in latest_data["metrics"]:
                metric = HealthMetric(
                    metric_name=metric_data["type"],
                    value=metric_data["value"],
                    unit=metric_data["unit"],
                    timestamp=latest_data["timestamp"],
                    status=metric_data["status"],
                    trend="stable"  # Would need historical data to calculate trend
                )
                key_metrics.append(metric)
            
            return key_metrics
        
        except Exception as e:
            self.logger.error(f"Error extracting key metrics: {e}")
            return []
    
    def _generate_alerts(self, health_data: List[Dict[str, Any]], error_data: List[Dict[str, Any]]) -> List[str]:
        """Generate alerts from health and error data."""
        try:
            alerts = []
            
            # Collect alerts from health data
            for data in health_data:
                alerts.extend(data.get("alerts", []))
            
            # Collect alerts from error data
            for error in error_data:
                alerts.append(f"{error['component']}: {error['alert']}")
            
            return list(set(alerts))  # Remove duplicates
        
        except Exception as e:
            self.logger.error(f"Error generating alerts: {e}")
            return []
    
    def _generate_recommendations(self, health_data: List[Dict[str, Any]], 
                                performance_data: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations from health and performance data."""
        try:
            recommendations = []
            
            # Collect recommendations from health data
            for data in health_data:
                recommendations.extend(data.get("recommendations", []))
            
            # Generate performance-based recommendations
            if performance_data:
                avg_cpu = sum(p["cpu_usage"] for p in performance_data) / len(performance_data)
                avg_memory = sum(p["memory_usage"] for p in performance_data) / len(performance_data)
                
                if avg_cpu > 70:
                    recommendations.append("Consider optimizing CPU-intensive processes")
                
                if avg_memory > 80:
                    recommendations.append("Consider adding more RAM or optimizing memory usage")
            
            return list(set(recommendations))  # Remove duplicates
        
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _generate_charts(self, health_data: List[Dict[str, Any]], 
                        performance_data: List[Dict[str, Any]]) -> List[str]:
        """Generate charts for the report."""
        try:
            chart_files = []
            
            if not performance_data:
                return chart_files
            
            # Create performance trend chart
            timestamps = [pd.to_datetime(p["timestamp"]) for p in performance_data]
            cpu_values = [p["cpu_usage"] for p in performance_data]
            memory_values = [p["memory_usage"] for p in performance_data]
            
            plt.figure(figsize=(12, 8))
            
            # CPU usage chart
            plt.subplot(2, 1, 1)
            plt.plot(timestamps, cpu_values, label='CPU Usage', color='blue')
            plt.title('CPU Usage Over Time')
            plt.ylabel('CPU Usage (%)')
            plt.legend()
            plt.grid(True)
            
            # Memory usage chart
            plt.subplot(2, 1, 2)
            plt.plot(timestamps, memory_values, label='Memory Usage', color='red')
            plt.title('Memory Usage Over Time')
            plt.ylabel('Memory Usage (%)')
            plt.xlabel('Time')
            plt.legend()
            plt.grid(True)
            
            plt.tight_layout()
            
            # Save chart
            chart_file = f"reports/charts/performance_trend_{int(time.time())}.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            chart_files.append(chart_file)
            
            return chart_files
        
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}")
            return []
    
    def _generate_summary(self, report: HealthReport) -> str:
        """Generate executive summary for the report."""
        try:
            summary_parts = []
            
            # Overall health
            if report.overall_health_score >= 80:
                summary_parts.append(f"System is in excellent health with a score of {report.overall_health_score:.1f}/100.")
            elif report.overall_health_score >= 60:
                summary_parts.append(f"System is in good health with a score of {report.overall_health_score:.1f}/100.")
            elif report.overall_health_score >= 40:
                summary_parts.append(f"System health is moderate with a score of {report.overall_health_score:.1f}/100. Attention needed.")
            else:
                summary_parts.append(f"System health is poor with a score of {report.overall_health_score:.1f}/100. Immediate action required.")
            
            # Alerts
            if report.alerts:
                summary_parts.append(f"Found {len(report.alerts)} active alerts that require attention.")
            else:
                summary_parts.append("No active alerts detected.")
            
            # Recommendations
            if report.recommendations:
                summary_parts.append(f"Generated {len(report.recommendations)} recommendations for system optimization.")
            
            return " ".join(summary_parts)
        
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return "Error generating summary"
    
    def _export_report(self, report: HealthReport, format: ReportFormat):
        """Export report in specified format."""
        try:
            if format == ReportFormat.JSON:
                self._export_json_report(report)
            elif format == ReportFormat.HTML:
                self._export_html_report(report)
            elif format == ReportFormat.CSV:
                self._export_csv_report(report)
            elif format == ReportFormat.CHART:
                self._export_chart_report(report)
        
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
    
    def _export_json_report(self, report: HealthReport):
        """Export report as JSON."""
        try:
            report_file = f"reports/exports/health_report_{report.report_id}.json"
            
            report_data = {
                "report_id": report.report_id,
                "report_type": report.report_type.value,
                "generated_at": report.generated_at.isoformat(),
                "time_range": {
                    "start": report.time_range[0].isoformat(),
                    "end": report.time_range[1].isoformat()
                },
                "overall_health_score": report.overall_health_score,
                "system_status": report.system_status,
                "key_metrics": [
                    {
                        "metric_name": metric.metric_name,
                        "value": metric.value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp.isoformat(),
                        "status": metric.status,
                        "trend": metric.trend
                    }
                    for metric in report.key_metrics
                ],
                "alerts": report.alerts,
                "recommendations": report.recommendations,
                "charts": report.charts,
                "summary": report.summary
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"JSON report exported: {report_file}")
        
        except Exception as e:
            self.logger.error(f"Error exporting JSON report: {e}")
    
    def _export_html_report(self, report: HealthReport):
        """Export report as HTML."""
        try:
            report_file = f"reports/exports/health_report_{report.report_id}.html"
            
            # Get template
            template = self.report_templates.get(report.report_type.value, self.report_templates["comprehensive"])
            
            # Format template with report data
            html_content = template.format(
                timestamp=report.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
                health_score=report.overall_health_score,
                system_status=report.system_status,
                metrics_table=self._format_metrics_table(report.key_metrics),
                alerts_list=self._format_alerts_list(report.alerts),
                recommendations_list=self._format_recommendations_list(report.recommendations),
                summary=report.summary,
                executive_summary=report.summary
            )
            
            # Add HTML structure
            full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Health Report - {report.report_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        .metric {{ background-color: #f4f4f4; padding: 10px; margin: 5px 0; }}
        .alert {{ background-color: #ffebee; padding: 10px; margin: 5px 0; border-left: 4px solid #f44336; }}
        .recommendation {{ background-color: #e8f5e8; padding: 10px; margin: 5px 0; border-left: 4px solid #4caf50; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            self.logger.info(f"HTML report exported: {report_file}")
        
        except Exception as e:
            self.logger.error(f"Error exporting HTML report: {e}")
    
    def _export_csv_report(self, report: HealthReport):
        """Export report as CSV."""
        try:
            report_file = f"reports/exports/health_report_{report.report_id}.csv"
            
            # Create CSV data
            csv_data = []
            csv_data.append(["Metric", "Value", "Unit", "Status", "Trend"])
            
            for metric in report.key_metrics:
                csv_data.append([
                    metric.metric_name,
                    str(metric.value),
                    metric.unit,
                    metric.status,
                    metric.trend
                ])
            
            # Write CSV file
            with open(report_file, 'w', encoding='utf-8') as f:
                for row in csv_data:
                    f.write(','.join(row) + '\n')
            
            self.logger.info(f"CSV report exported: {report_file}")
        
        except Exception as e:
            self.logger.error(f"Error exporting CSV report: {e}")
    
    def _export_chart_report(self, report: HealthReport):
        """Export report with charts."""
        try:
            # Charts are already generated in _generate_charts
            self.logger.info(f"Chart report exported with {len(report.charts)} charts")
        
        except Exception as e:
            self.logger.error(f"Error exporting chart report: {e}")
    
    def _format_metrics_table(self, metrics: List[HealthMetric]) -> str:
        """Format metrics as HTML table."""
        try:
            if not metrics:
                return "<p>No metrics available</p>"
            
            table_html = "<table><tr><th>Metric</th><th>Value</th><th>Unit</th><th>Status</th><th>Trend</th></tr>"
            
            for metric in metrics:
                table_html += f"<tr><td>{metric.metric_name}</td><td>{metric.value}</td><td>{metric.unit}</td><td>{metric.status}</td><td>{metric.trend}</td></tr>"
            
            table_html += "</table>"
            return table_html
        
        except Exception as e:
            self.logger.error(f"Error formatting metrics table: {e}")
            return "<p>Error formatting metrics</p>"
    
    def _format_alerts_list(self, alerts: List[str]) -> str:
        """Format alerts as HTML list."""
        try:
            if not alerts:
                return "<p>No alerts</p>"
            
            alerts_html = "<ul>"
            for alert in alerts:
                alerts_html += f"<li class='alert'>{alert}</li>"
            alerts_html += "</ul>"
            
            return alerts_html
        
        except Exception as e:
            self.logger.error(f"Error formatting alerts list: {e}")
            return "<p>Error formatting alerts</p>"
    
    def _format_recommendations_list(self, recommendations: List[str]) -> str:
        """Format recommendations as HTML list."""
        try:
            if not recommendations:
                return "<p>No recommendations</p>"
            
            rec_html = "<ul>"
            for rec in recommendations:
                rec_html += f"<li class='recommendation'>{rec}</li>"
            rec_html += "</ul>"
            
            return rec_html
        
        except Exception as e:
            self.logger.error(f"Error formatting recommendations list: {e}")
            return "<p>Error formatting recommendations</p>"
    
    def get_report_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get report history for specified hours."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return [
                {
                    "report_id": report.report_id,
                    "report_type": report.report_type.value,
                    "generated_at": report.generated_at.isoformat(),
                    "overall_health_score": report.overall_health_score,
                    "system_status": report.system_status,
                    "alerts_count": len(report.alerts),
                    "recommendations_count": len(report.recommendations)
                }
                for report in self.reports
                if report.generated_at >= cutoff_time
            ]
        
        except Exception as e:
            self.logger.error(f"Error getting report history: {e}")
            return []
    
    def get_reporting_statistics(self) -> Dict[str, Any]:
        """Get reporting statistics."""
        try:
            total_reports = len(self.reports)
            
            if not total_reports:
                return {"total_reports": 0}
            
            # Calculate statistics
            avg_health_score = sum(r.overall_health_score for r in self.reports) / total_reports
            
            status_counts = {}
            for report in self.reports:
                status = report.system_status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "total_reports": total_reports,
                "average_health_score": avg_health_score,
                "status_distribution": status_counts,
                "latest_report_time": max(r.generated_at for r in self.reports).isoformat() if self.reports else None
            }
        
        except Exception as e:
            self.logger.error(f"Error getting reporting statistics: {e}")
            return {}
    
    def schedule_automatic_reporting(self, interval_hours: int = 24):
        """Schedule automatic report generation."""
        try:
            # This would typically be implemented with a scheduler
            # For now, we'll just log the intention
            self.logger.info(f"Automatic reporting scheduled every {interval_hours} hours")
        
        except Exception as e:
            self.logger.error(f"Error scheduling automatic reporting: {e}")
    
    def export_reporting_summary(self, output_file: str = None) -> bool:
        """Export comprehensive reporting summary."""
        try:
            if not output_file:
                output_file = f"reports/reporting_summary_{int(datetime.now().timestamp())}.json"
            
            summary_data = {
                "summary_timestamp": datetime.now().isoformat(),
                "reporting_statistics": self.get_reporting_statistics(),
                "recent_reports": self.get_report_history(168),  # Last week
                "system_components": {
                    "system_monitor": self.system_monitor is not None,
                    "auto_repair": self.auto_repair is not None,
                    "fallback_restore": self.fallback_restore is not None
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Reporting summary exported: {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting reporting summary: {e}")
            return False
