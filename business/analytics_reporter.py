"""
JARVIS AI - Analytics Reporter
Generates automated reports and analytics for business processes.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from core.ai_engine import AIEngine
from utils.config import Config
from business.process_automation import ProcessAutomation, ProcessStatus
from business.crm_integration import CRMIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Types of reports."""
    PERFORMANCE = "performance"
    SALES = "sales"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    CUSTOMER = "customer"
    COMPREHENSIVE = "comprehensive"

class ReportFormat(Enum):
    """Report output formats."""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"

class ChartType(Enum):
    """Types of charts."""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"

@dataclass
class ReportSection:
    """Report section definition."""
    section_id: str
    title: str
    content: str
    chart_type: Optional[ChartType]
    chart_data: Optional[Dict[str, Any]]
    metrics: Dict[str, Any]
    insights: str

@dataclass
class BusinessReport:
    """Business report definition."""
    report_id: str
    title: str
    report_type: ReportType
    generated_at: datetime
    time_period: str
    sections: List[ReportSection]
    summary: str
    recommendations: List[str]
    metadata: Dict[str, Any]

class AnalyticsReporter:
    """
    JARVIS AI - Analytics Reporter
    Generates automated reports and analytics for business processes.
    """
    
    def __init__(self, ai_engine: AIEngine, config: Config,
                 process_automation: ProcessAutomation,
                 crm_integration: CRMIntegration,
                 reports_dir: Path = Path("business/reports")):
        self.ai_engine = ai_engine
        self.config = config
        self.process_automation = process_automation
        self.crm_integration = crm_integration
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.reports: Dict[str, BusinessReport] = {}
        
        # Load existing reports
        self._load_reports()
        
        self.logger.info("Analytics Reporter initialized")

    def _load_reports(self):
        """Load existing reports from storage."""
        try:
            reports_file = self.reports_dir / "reports.json"
            if reports_file.exists():
                with open(reports_file, 'r') as f:
                    reports_data = json.load(f)
                    for report_data in reports_data:
                        report = self._deserialize_report(report_data)
                        self.reports[report.report_id] = report
                self.logger.info(f"Loaded {len(self.reports)} reports")
        except Exception as e:
            self.logger.error(f"Error loading reports: {e}")

    def _save_reports(self):
        """Save reports to storage."""
        try:
            reports_file = self.reports_dir / "reports.json"
            reports_data = [self._serialize_report(report) for report in self.reports.values()]
            with open(reports_file, 'w') as f:
                json.dump(reports_data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving reports: {e}")

    def _serialize_report(self, report: BusinessReport) -> Dict[str, Any]:
        """Serialize report for storage."""
        return {
            "report_id": report.report_id,
            "title": report.title,
            "report_type": report.report_type.value,
            "generated_at": report.generated_at.isoformat(),
            "time_period": report.time_period,
            "sections": [
                {
                    "section_id": section.section_id,
                    "title": section.title,
                    "content": section.content,
                    "chart_type": section.chart_type.value if section.chart_type else None,
                    "chart_data": section.chart_data,
                    "metrics": section.metrics,
                    "insights": section.insights
                }
                for section in report.sections
            ],
            "summary": report.summary,
            "recommendations": report.recommendations,
            "metadata": report.metadata
        }

    def _deserialize_report(self, data: Dict[str, Any]) -> BusinessReport:
        """Deserialize report from storage."""
        sections = []
        for section_data in data.get("sections", []):
            section = ReportSection(
                section_id=section_data["section_id"],
                title=section_data["title"],
                content=section_data["content"],
                chart_type=ChartType(section_data["chart_type"]) if section_data.get("chart_type") else None,
                chart_data=section_data.get("chart_data"),
                metrics=section_data.get("metrics", {}),
                insights=section_data.get("insights", "")
            )
            sections.append(section)

        return BusinessReport(
            report_id=data["report_id"],
            title=data["title"],
            report_type=ReportType(data["report_type"]),
            generated_at=datetime.fromisoformat(data["generated_at"]),
            time_period=data["time_period"],
            sections=sections,
            summary=data["summary"],
            recommendations=data.get("recommendations", []),
            metadata=data.get("metadata", {})
        )

    def generate_performance_report(self, time_period: str = "last_30_days") -> BusinessReport:
        """Generate a performance analytics report."""
        try:
            report_id = f"perf_{uuid.uuid4().hex[:8]}"
            sections = []
            
            # Process Performance Section
            process_stats = self.process_automation.get_process_statistics()
            process_section = ReportSection(
                section_id=f"section_{uuid.uuid4().hex[:8]}",
                title="Process Performance",
                content=f"""
                Process Automation Performance:
                - Total Processes: {process_stats['total_processes']}
                - Active Processes: {process_stats['active_processes']}
                - Completed Processes: {process_stats['completed_processes']}
                - Success Rate: {process_stats['success_rate']:.1f}%
                """,
                chart_type=ChartType.PIE,
                chart_data={
                    "labels": ["Active", "Completed", "Failed"],
                    "values": [
                        process_stats['active_processes'],
                        process_stats['completed_processes'],
                        process_stats['total_processes'] - process_stats['active_processes'] - process_stats['completed_processes']
                    ]
                },
                metrics=process_stats,
                insights="Process automation is showing strong performance with high completion rates."
            )
            sections.append(process_section)
            
            # CRM Performance Section
            crm_analytics = self.crm_integration.get_crm_analytics()
            crm_section = ReportSection(
                section_id=f"section_{uuid.uuid4().hex[:8]}",
                title="CRM Performance",
                content=f"""
                CRM Performance Metrics:
                - Total Contacts: {crm_analytics['total_contacts']}
                - Total Deals: {crm_analytics['total_deals']}
                - Pipeline Value: ${crm_analytics['pipeline_value']:,.2f}
                - Conversion Rate: {crm_analytics['conversion_rate']:.1f}%
                - Task Completion Rate: {crm_analytics['task_completion_rate']:.1f}%
                """,
                chart_type=ChartType.BAR,
                chart_data={
                    "labels": ["Contacts", "Deals", "Tasks", "Projects"],
                    "values": [
                        crm_analytics['total_contacts'],
                        crm_analytics['total_deals'],
                        crm_analytics['total_tasks'],
                        crm_analytics['total_projects']
                    ]
                },
                metrics=crm_analytics,
                insights="CRM system shows healthy activity with good conversion rates."
            )
            sections.append(crm_section)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(sections)
            
            report = BusinessReport(
                report_id=report_id,
                title=f"Performance Report - {time_period}",
                report_type=ReportType.PERFORMANCE,
                generated_at=datetime.now(),
                time_period=time_period,
                sections=sections,
                summary=ai_insights,
                recommendations=self._generate_recommendations(sections),
                metadata={"generated_by": "Jarvis AI", "version": "1.0"}
            )
            
            self.reports[report_id] = report
            self._save_reports()
            
            self.logger.info(f"Generated performance report: {report_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return None

    def generate_sales_report(self, time_period: str = "last_30_days") -> BusinessReport:
        """Generate a sales analytics report."""
        try:
            report_id = f"sales_{uuid.uuid4().hex[:8]}"
            sections = []
            
            # Sales Pipeline Section
            crm_analytics = self.crm_integration.get_crm_analytics()
            pipeline_section = ReportSection(
                section_id=f"section_{uuid.uuid4().hex[:8]}",
                title="Sales Pipeline",
                content=f"""
                Sales Pipeline Analysis:
                - Total Pipeline Value: ${crm_analytics['pipeline_value']:,.2f}
                - Won Deals Value: ${crm_analytics['won_value']:,.2f}
                - Conversion Rate: {crm_analytics['conversion_rate']:.1f}%
                - Total Deals: {crm_analytics['total_deals']}
                """,
                chart_type=ChartType.BAR,
                chart_data={
                    "labels": list(crm_analytics['deals_by_stage'].keys()),
                    "values": list(crm_analytics['deals_by_stage'].values())
                },
                metrics=crm_analytics,
                insights="Sales pipeline shows strong activity with good conversion potential."
            )
            sections.append(pipeline_section)
            
            # Customer Analysis Section
            customer_section = ReportSection(
                section_id=f"section_{uuid.uuid4().hex[:8]}",
                title="Customer Analysis",
                content=f"""
                Customer Base Analysis:
                - Total Contacts: {crm_analytics['total_contacts']}
                - Customer Distribution: {crm_analytics['contacts_by_status']}
                """,
                chart_type=ChartType.PIE,
                chart_data={
                    "labels": list(crm_analytics['contacts_by_status'].keys()),
                    "values": list(crm_analytics['contacts_by_status'].values())
                },
                metrics=crm_analytics['contacts_by_status'],
                insights="Customer base shows good diversity across different statuses."
            )
            sections.append(customer_section)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(sections)
            
            report = BusinessReport(
                report_id=report_id,
                title=f"Sales Report - {time_period}",
                report_type=ReportType.SALES,
                generated_at=datetime.now(),
                time_period=time_period,
                sections=sections,
                summary=ai_insights,
                recommendations=self._generate_recommendations(sections),
                metadata={"generated_by": "Jarvis AI", "version": "1.0"}
            )
            
            self.reports[report_id] = report
            self._save_reports()
            
            self.logger.info(f"Generated sales report: {report_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating sales report: {e}")
            return None

    def generate_comprehensive_report(self, time_period: str = "last_30_days") -> BusinessReport:
        """Generate a comprehensive business report."""
        try:
            report_id = f"comp_{uuid.uuid4().hex[:8]}"
            sections = []
            
            # Executive Summary Section
            process_stats = self.process_automation.get_process_statistics()
            crm_analytics = self.crm_integration.get_crm_analytics()
            
            executive_section = ReportSection(
                section_id=f"section_{uuid.uuid4().hex[:8]}",
                title="Executive Summary",
                content=f"""
                Business Performance Overview:
                
                Process Automation:
                - Total Processes: {process_stats['total_processes']}
                - Success Rate: {process_stats['success_rate']:.1f}%
                
                CRM Performance:
                - Total Contacts: {crm_analytics['total_contacts']}
                - Pipeline Value: ${crm_analytics['pipeline_value']:,.2f}
                - Conversion Rate: {crm_analytics['conversion_rate']:.1f}%
                """,
                chart_type=None,
                chart_data=None,
                metrics={**process_stats, **crm_analytics},
                insights="Overall business performance shows strong metrics across all areas."
            )
            sections.append(executive_section)
            
            # Process Performance Section
            process_section = ReportSection(
                section_id=f"section_{uuid.uuid4().hex[:8]}",
                title="Process Performance",
                content=f"""
                Process Automation Metrics:
                - Active Processes: {process_stats['active_processes']}
                - Completed Processes: {process_stats['completed_processes']}
                - Total Executions: {process_stats['total_executions']}
                """,
                chart_type=ChartType.LINE,
                chart_data={
                    "labels": ["Active", "Completed", "Failed"],
                    "values": [
                        process_stats['active_processes'],
                        process_stats['completed_processes'],
                        process_stats['total_processes'] - process_stats['active_processes'] - process_stats['completed_processes']
                    ]
                },
                metrics=process_stats,
                insights="Process automation is performing well with high success rates."
            )
            sections.append(process_section)
            
            # Sales Performance Section
            sales_section = ReportSection(
                section_id=f"section_{uuid.uuid4().hex[:8]}",
                title="Sales Performance",
                content=f"""
                Sales Metrics:
                - Pipeline Value: ${crm_analytics['pipeline_value']:,.2f}
                - Won Value: ${crm_analytics['won_value']:,.2f}
                - Conversion Rate: {crm_analytics['conversion_rate']:.1f}%
                - Task Completion: {crm_analytics['task_completion_rate']:.1f}%
                """,
                chart_type=ChartType.BAR,
                chart_data={
                    "labels": ["Pipeline", "Won", "Conversion Rate", "Task Completion"],
                    "values": [
                        crm_analytics['pipeline_value'],
                        crm_analytics['won_value'],
                        crm_analytics['conversion_rate'],
                        crm_analytics['task_completion_rate']
                    ]
                },
                metrics=crm_analytics,
                insights="Sales performance shows strong pipeline and conversion metrics."
            )
            sections.append(sales_section)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(sections)
            
            report = BusinessReport(
                report_id=report_id,
                title=f"Comprehensive Business Report - {time_period}",
                report_type=ReportType.COMPREHENSIVE,
                generated_at=datetime.now(),
                time_period=time_period,
                sections=sections,
                summary=ai_insights,
                recommendations=self._generate_recommendations(sections),
                metadata={"generated_by": "Jarvis AI", "version": "1.0"}
            )
            
            self.reports[report_id] = report
            self._save_reports()
            
            self.logger.info(f"Generated comprehensive report: {report_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {e}")
            return None

    def _generate_ai_insights(self, sections: List[ReportSection]) -> str:
        """Generate AI-powered insights from report sections."""
        try:
            # Collect all metrics
            all_metrics = {}
            for section in sections:
                all_metrics.update(section.metrics)
            
            prompt = f"""
            Analyze the following business metrics and provide comprehensive insights:
            
            Metrics: {all_metrics}
            
            Provide:
            1. Key performance indicators analysis
            2. Trends and patterns identified
            3. Areas of strength and improvement
            4. Strategic recommendations
            5. Risk assessment
            
            Format as a professional executive summary.
            """
            
            insights = self.ai_engine.get_ai_response(prompt)
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating AI insights: {e}")
            return f"Error generating insights: {str(e)}"

    def _generate_recommendations(self, sections: List[ReportSection]) -> List[str]:
        """Generate actionable recommendations based on report data."""
        try:
            # Collect all metrics
            all_metrics = {}
            for section in sections:
                all_metrics.update(section.metrics)
            
            prompt = f"""
            Based on these business metrics: {all_metrics}
            
            Generate 5-7 specific, actionable recommendations for improving business performance.
            Focus on:
            - Process optimization
            - Sales improvement
            - Operational efficiency
            - Strategic initiatives
            
            Return as a numbered list of recommendations.
            """
            
            recommendations_text = self.ai_engine.get_ai_response(prompt)
            
            # Parse recommendations into list
            recommendations = []
            for line in recommendations_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Clean up the recommendation
                    clean_line = line.lstrip('0123456789.-• ').strip()
                    if clean_line:
                        recommendations.append(clean_line)
            
            return recommendations[:7]  # Limit to 7 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]

    def export_report(self, report_id: str, format: ReportFormat, output_path: Optional[Path] = None) -> Path:
        """Export a report to specified format."""
        try:
            report = self.reports.get(report_id)
            if not report:
                self.logger.error(f"Report not found: {report_id}")
                return None
            
            if not output_path:
                output_path = self.reports_dir / f"{report_id}.{format.value}"
            
            if format == ReportFormat.JSON:
                return self._export_json(report, output_path)
            elif format == ReportFormat.HTML:
                return self._export_html(report, output_path)
            elif format == ReportFormat.CSV:
                return self._export_csv(report, output_path)
            else:
                self.logger.error(f"Unsupported format: {format}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            return None

    def _export_json(self, report: BusinessReport, output_path: Path) -> Path:
        """Export report as JSON."""
        try:
            report_data = self._serialize_report(report)
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            return output_path
        except Exception as e:
            self.logger.error(f"Error exporting JSON: {e}")
            return None

    def _export_html(self, report: BusinessReport, output_path: Path) -> Path:
        """Export report as HTML."""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{report.title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .metrics {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; }}
                    .recommendations {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{report.title}</h1>
                    <p>Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Time Period: {report.time_period}</p>
                </div>
                
                <div class="section">
                    <h2>Summary</h2>
                    <p>{report.summary}</p>
                </div>
            """
            
            for section in report.sections:
                html_content += f"""
                <div class="section">
                    <h3>{section.title}</h3>
                    <p>{section.content}</p>
                    <div class="metrics">
                        <h4>Metrics:</h4>
                        <pre>{json.dumps(section.metrics, indent=2)}</pre>
                    </div>
                    <p><strong>Insights:</strong> {section.insights}</p>
                </div>
                """
            
            html_content += f"""
                <div class="recommendations">
                    <h2>Recommendations</h2>
                    <ol>
            """
            for rec in report.recommendations:
                html_content += f"<li>{rec}</li>"
            
            html_content += """
                    </ol>
                </div>
            </body>
            </html>
            """
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error exporting HTML: {e}")
            return None

    def _export_csv(self, report: BusinessReport, output_path: Path) -> Path:
        """Export report as CSV."""
        try:
            # Create a DataFrame with report data
            data = []
            for section in report.sections:
                row = {
                    'Section': section.title,
                    'Content': section.content,
                    'Insights': section.insights,
                    'Metrics': json.dumps(section.metrics)
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error exporting CSV: {e}")
            return None

    def get_report(self, report_id: str) -> Optional[BusinessReport]:
        """Get a report by ID."""
        return self.reports.get(report_id)

    def get_all_reports(self) -> List[BusinessReport]:
        """Get all reports."""
        return list(self.reports.values())

    def get_reports_by_type(self, report_type: ReportType) -> List[BusinessReport]:
        """Get reports by type."""
        return [report for report in self.reports.values() if report.report_type == report_type]

    def get_report_statistics(self) -> Dict[str, Any]:
        """Get report generation statistics."""
        total_reports = len(self.reports)
        reports_by_type = {}
        for report in self.reports.values():
            report_type = report.report_type.value
            reports_by_type[report_type] = reports_by_type.get(report_type, 0) + 1
        
        return {
            "total_reports": total_reports,
            "reports_by_type": reports_by_type,
            "latest_report": max(self.reports.values(), key=lambda r: r.generated_at).title if self.reports else None
        }
