"""
JARVIS AI - Workflow Optimizer
Optimizes business workflows and processes for maximum efficiency.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np
from collections import defaultdict

from core.ai_engine import AIEngine
from utils.config import Config
from business.process_automation import ProcessAutomation, BusinessProcess, ProcessTask, TaskStatus

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """Types of workflow optimizations."""
    PERFORMANCE = "performance"
    COST = "cost"
    TIME = "time"
    RESOURCE = "resource"
    QUALITY = "quality"

class OptimizationLevel(Enum):
    """Optimization levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class OptimizationSuggestion:
    """Workflow optimization suggestion."""
    suggestion_id: str
    process_id: str
    optimization_type: OptimizationType
    level: OptimizationLevel
    title: str
    description: str
    current_value: float
    suggested_value: float
    improvement_percentage: float
    implementation_effort: str
    expected_benefit: str
    created_at: datetime

@dataclass
class WorkflowMetrics:
    """Workflow performance metrics."""
    process_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_completion_time: float
    total_execution_time: float
    success_rate: float
    efficiency_score: float
    bottleneck_tasks: List[str]
    resource_utilization: Dict[str, float]
    cost_analysis: Dict[str, float]

@dataclass
class OptimizationReport:
    """Workflow optimization report."""
    report_id: str
    process_id: str
    generated_at: datetime
    current_metrics: WorkflowMetrics
    suggestions: List[OptimizationSuggestion]
    overall_score: float
    priority_actions: List[str]
    estimated_improvement: Dict[str, float]

class WorkflowOptimizer:
    """
    JARVIS AI - Workflow Optimizer
    Analyzes and optimizes business workflows for maximum efficiency.
    """
    
    def __init__(self, ai_engine: AIEngine, config: Config,
                 process_automation: ProcessAutomation,
                 optimization_dir: Path = Path("business/optimization")):
        self.ai_engine = ai_engine
        self.config = config
        self.process_automation = process_automation
        self.optimization_dir = optimization_dir
        self.optimization_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.optimization_history: Dict[str, List[OptimizationSuggestion]] = {}
        self.workflow_metrics: Dict[str, WorkflowMetrics] = {}
        
        # Load existing optimization data
        self._load_optimization_data()
        
        self.logger.info("Workflow Optimizer initialized")

    def _load_optimization_data(self):
        """Load existing optimization data from storage."""
        try:
            optimization_file = self.optimization_dir / "optimization_data.json"
            if optimization_file.exists():
                with open(optimization_file, 'r') as f:
                    data = json.load(f)
                    self.optimization_history = data.get("optimization_history", {})
                    self.workflow_metrics = data.get("workflow_metrics", {})
                self.logger.info("Loaded optimization data")
        except Exception as e:
            self.logger.error(f"Error loading optimization data: {e}")

    def _save_optimization_data(self):
        """Save optimization data to storage."""
        try:
            optimization_file = self.optimization_dir / "optimization_data.json"
            data = {
                "optimization_history": self.optimization_history,
                "workflow_metrics": self.workflow_metrics
            }
            with open(optimization_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving optimization data: {e}")

    def analyze_workflow(self, process_id: str) -> WorkflowMetrics:
        """Analyze a workflow and generate performance metrics."""
        try:
            process = self.process_automation.get_process(process_id)
            if not process:
                self.logger.error(f"Process not found: {process_id}")
                return None
            
            # Calculate basic metrics
            total_tasks = len(process.tasks)
            completed_tasks = len([task for task in process.tasks if task.status == TaskStatus.COMPLETED])
            failed_tasks = len([task for task in process.tasks if task.status == TaskStatus.BLOCKED])
            
            # Calculate timing metrics
            task_times = []
            for task in process.tasks:
                if task.started_at and task.completed_at:
                    duration = (task.completed_at - task.started_at).total_seconds()
                    task_times.append(duration)
            
            average_completion_time = np.mean(task_times) if task_times else 0
            total_execution_time = sum(task_times)
            
            # Calculate success rate
            success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Calculate efficiency score
            efficiency_score = self._calculate_efficiency_score(process)
            
            # Identify bottleneck tasks
            bottleneck_tasks = self._identify_bottlenecks(process)
            
            # Calculate resource utilization
            resource_utilization = self._calculate_resource_utilization(process)
            
            # Calculate cost analysis
            cost_analysis = self._calculate_cost_analysis(process)
            
            metrics = WorkflowMetrics(
                process_id=process_id,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                average_completion_time=average_completion_time,
                total_execution_time=total_execution_time,
                success_rate=success_rate,
                efficiency_score=efficiency_score,
                bottleneck_tasks=bottleneck_tasks,
                resource_utilization=resource_utilization,
                cost_analysis=cost_analysis
            )
            
            self.workflow_metrics[process_id] = metrics
            self._save_optimization_data()
            
            self.logger.info(f"Analyzed workflow: {process_id}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing workflow: {e}")
            return None

    def _calculate_efficiency_score(self, process: BusinessProcess) -> float:
        """Calculate workflow efficiency score."""
        try:
            # Base score from success rate
            success_rate = len([task for task in process.tasks if task.status == TaskStatus.COMPLETED]) / len(process.tasks) * 100 if process.tasks else 0
            
            # Penalty for failed tasks
            failure_penalty = len([task for task in process.tasks if task.status == TaskStatus.BLOCKED]) * 10
            
            # Bonus for parallel execution potential
            parallel_bonus = self._calculate_parallel_potential(process) * 5
            
            # Calculate final score
            efficiency_score = max(0, min(100, success_rate - failure_penalty + parallel_bonus))
            return efficiency_score
            
        except Exception as e:
            self.logger.error(f"Error calculating efficiency score: {e}")
            return 0

    def _calculate_parallel_potential(self, process: BusinessProcess) -> float:
        """Calculate potential for parallel task execution."""
        try:
            if not process.tasks:
                return 0
            
            # Count tasks with no dependencies
            independent_tasks = len([task for task in process.tasks if not task.dependencies])
            
            # Calculate dependency depth
            max_depth = self._calculate_max_dependency_depth(process.tasks)
            
            # Parallel potential = independent tasks / total tasks * (1 - depth penalty)
            depth_penalty = min(0.5, max_depth * 0.1)
            parallel_potential = (independent_tasks / len(process.tasks)) * (1 - depth_penalty)
            
            return parallel_potential
            
        except Exception as e:
            self.logger.error(f"Error calculating parallel potential: {e}")
            return 0

    def _calculate_max_dependency_depth(self, tasks: List[ProcessTask]) -> int:
        """Calculate maximum dependency depth in task graph."""
        try:
            # Build dependency graph
            graph = defaultdict(list)
            in_degree = defaultdict(int)
            
            for task in tasks:
                in_degree[task.task_id] = 0
            
            for task in tasks:
                for dep_id in task.dependencies:
                    graph[dep_id].append(task.task_id)
                    in_degree[task.task_id] += 1
            
            # Find longest path using topological sort
            queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
            depth = {task_id: 0 for task_id in queue}
            
            while queue:
                current = queue.pop(0)
                for neighbor in graph[current]:
                    in_degree[neighbor] -= 1
                    depth[neighbor] = max(depth[neighbor], depth[current] + 1)
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            return max(depth.values()) if depth else 0
            
        except Exception as e:
            self.logger.error(f"Error calculating dependency depth: {e}")
            return 0

    def _identify_bottlenecks(self, process: BusinessProcess) -> List[str]:
        """Identify bottleneck tasks in the workflow."""
        try:
            bottlenecks = []
            
            # Find tasks with high failure rate
            for task in process.tasks:
                if task.status == TaskStatus.BLOCKED:
                    bottlenecks.append(f"{task.name} (Blocked)")
            
            # Find tasks with long completion times
            task_times = []
            for task in process.tasks:
                if task.started_at and task.completed_at:
                    duration = (task.completed_at - task.started_at).total_seconds()
                    task_times.append((task.name, duration))
            
            if task_times:
                avg_time = np.mean([time for _, time in task_times])
                for name, time in task_times:
                    if time > avg_time * 2:  # 2x average time
                        bottlenecks.append(f"{name} (Slow: {time:.1f}s)")
            
            return bottlenecks
            
        except Exception as e:
            self.logger.error(f"Error identifying bottlenecks: {e}")
            return []

    def _calculate_resource_utilization(self, process: BusinessProcess) -> Dict[str, float]:
        """Calculate resource utilization metrics."""
        try:
            # Count tasks by assignee
            assignee_counts = defaultdict(int)
            for task in process.tasks:
                if task.assigned_to:
                    assignee_counts[task.assigned_to] += 1
            
            # Calculate utilization percentages
            total_tasks = len(process.tasks)
            utilization = {}
            for assignee, count in assignee_counts.items():
                utilization[assignee] = (count / total_tasks * 100) if total_tasks > 0 else 0
            
            return dict(utilization)
            
        except Exception as e:
            self.logger.error(f"Error calculating resource utilization: {e}")
            return {}

    def _calculate_cost_analysis(self, process: BusinessProcess) -> Dict[str, float]:
        """Calculate cost analysis for the workflow."""
        try:
            # Estimate costs based on task complexity and duration
            total_cost = 0
            task_costs = {}
            
            for task in process.tasks:
                # Base cost per task type
                base_costs = {
                    "email_notification": 0.10,
                    "data_processing": 0.50,
                    "api_call": 0.25,
                    "file_operation": 0.15,
                    "approval_request": 0.20,
                    "report_generation": 1.00,
                    "system_command": 0.30,
                    "ai_analysis": 2.00
                }
                
                task_cost = base_costs.get(task.task_type, 0.25)
                
                # Add time-based cost
                if task.started_at and task.completed_at:
                    duration_hours = (task.completed_at - task.started_at).total_seconds() / 3600
                    task_cost += duration_hours * 10  # $10/hour
                
                task_costs[task.task_id] = task_cost
                total_cost += task_cost
            
            return {
                "total_cost": total_cost,
                "average_task_cost": total_cost / len(process.tasks) if process.tasks else 0,
                "task_costs": task_costs
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating cost analysis: {e}")
            return {"total_cost": 0, "average_task_cost": 0, "task_costs": {}}

    def generate_optimization_suggestions(self, process_id: str) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions for a workflow."""
        try:
            metrics = self.workflow_metrics.get(process_id)
            if not metrics:
                metrics = self.analyze_workflow(process_id)
                if not metrics:
                    return []
            
            suggestions = []
            
            # Performance optimization suggestions
            if metrics.success_rate < 80:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"suggestion_{uuid.uuid4().hex[:8]}",
                    process_id=process_id,
                    optimization_type=OptimizationType.PERFORMANCE,
                    level=OptimizationLevel.HIGH,
                    title="Improve Task Success Rate",
                    description=f"Current success rate is {metrics.success_rate:.1f}%. Focus on failed tasks and improve error handling.",
                    current_value=metrics.success_rate,
                    suggested_value=90.0,
                    improvement_percentage=((90.0 - metrics.success_rate) / metrics.success_rate * 100) if metrics.success_rate > 0 else 100,
                    implementation_effort="Medium",
                    expected_benefit="Reduced failures and improved reliability",
                    created_at=datetime.now()
                )
                suggestions.append(suggestion)
            
            # Time optimization suggestions
            if metrics.average_completion_time > 300:  # 5 minutes
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"suggestion_{uuid.uuid4().hex[:8]}",
                    process_id=process_id,
                    optimization_type=OptimizationType.TIME,
                    level=OptimizationLevel.MEDIUM,
                    title="Reduce Task Completion Time",
                    description=f"Average completion time is {metrics.average_completion_time:.1f} seconds. Consider parallelization or task optimization.",
                    current_value=metrics.average_completion_time,
                    suggested_value=metrics.average_completion_time * 0.7,
                    improvement_percentage=30,
                    implementation_effort="High",
                    expected_benefit="Faster process execution",
                    created_at=datetime.now()
                )
                suggestions.append(suggestion)
            
            # Resource optimization suggestions
            if metrics.resource_utilization:
                max_utilization = max(metrics.resource_utilization.values())
                if max_utilization > 80:
                    suggestion = OptimizationSuggestion(
                        suggestion_id=f"suggestion_{uuid.uuid4().hex[:8]}",
                        process_id=process_id,
                        optimization_type=OptimizationType.RESOURCE,
                        level=OptimizationLevel.MEDIUM,
                        title="Balance Resource Utilization",
                        description=f"Some resources are over-utilized (max: {max_utilization:.1f}%). Redistribute tasks for better balance.",
                        current_value=max_utilization,
                        suggested_value=70.0,
                        improvement_percentage=((max_utilization - 70.0) / max_utilization * 100) if max_utilization > 0 else 0,
                        implementation_effort="Low",
                        expected_benefit="Better resource distribution and reduced bottlenecks",
                        created_at=datetime.now()
                    )
                    suggestions.append(suggestion)
            
            # Cost optimization suggestions
            if metrics.cost_analysis.get("total_cost", 0) > 100:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"suggestion_{uuid.uuid4().hex[:8]}",
                    process_id=process_id,
                    optimization_type=OptimizationType.COST,
                    level=OptimizationLevel.MEDIUM,
                    title="Reduce Process Costs",
                    description=f"Total process cost is ${metrics.cost_analysis.get('total_cost', 0):.2f}. Consider optimizing expensive tasks.",
                    current_value=metrics.cost_analysis.get("total_cost", 0),
                    suggested_value=metrics.cost_analysis.get("total_cost", 0) * 0.8,
                    improvement_percentage=20,
                    implementation_effort="Medium",
                    expected_benefit="Reduced operational costs",
                    created_at=datetime.now()
                )
                suggestions.append(suggestion)
            
            # Store suggestions
            if process_id not in self.optimization_history:
                self.optimization_history[process_id] = []
            self.optimization_history[process_id].extend(suggestions)
            self._save_optimization_data()
            
            self.logger.info(f"Generated {len(suggestions)} optimization suggestions for {process_id}")
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error generating optimization suggestions: {e}")
            return []

    def create_optimization_report(self, process_id: str) -> OptimizationReport:
        """Create a comprehensive optimization report."""
        try:
            # Analyze workflow if not already done
            metrics = self.workflow_metrics.get(process_id)
            if not metrics:
                metrics = self.analyze_workflow(process_id)
                if not metrics:
                    return None
            
            # Generate suggestions
            suggestions = self.generate_optimization_suggestions(process_id)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(metrics, suggestions)
            
            # Generate priority actions
            priority_actions = self._generate_priority_actions(suggestions)
            
            # Calculate estimated improvement
            estimated_improvement = self._calculate_estimated_improvement(suggestions)
            
            report = OptimizationReport(
                report_id=f"opt_report_{uuid.uuid4().hex[:8]}",
                process_id=process_id,
                generated_at=datetime.now(),
                current_metrics=metrics,
                suggestions=suggestions,
                overall_score=overall_score,
                priority_actions=priority_actions,
                estimated_improvement=estimated_improvement
            )
            
            self.logger.info(f"Created optimization report for {process_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error creating optimization report: {e}")
            return None

    def _calculate_overall_score(self, metrics: WorkflowMetrics, suggestions: List[OptimizationSuggestion]) -> float:
        """Calculate overall optimization score."""
        try:
            # Base score from efficiency
            base_score = metrics.efficiency_score
            
            # Bonus for high-impact suggestions
            high_impact_suggestions = len([s for s in suggestions if s.level == OptimizationLevel.HIGH])
            suggestion_bonus = high_impact_suggestions * 5
            
            # Penalty for bottlenecks
            bottleneck_penalty = len(metrics.bottleneck_tasks) * 2
            
            overall_score = max(0, min(100, base_score + suggestion_bonus - bottleneck_penalty))
            return overall_score
            
        except Exception as e:
            self.logger.error(f"Error calculating overall score: {e}")
            return 0

    def _generate_priority_actions(self, suggestions: List[OptimizationSuggestion]) -> List[str]:
        """Generate priority actions based on suggestions."""
        try:
            # Sort suggestions by level and improvement percentage
            sorted_suggestions = sorted(suggestions, 
                                      key=lambda s: (s.level.value, s.improvement_percentage), 
                                      reverse=True)
            
            priority_actions = []
            for suggestion in sorted_suggestions[:5]:  # Top 5 actions
                action = f"{suggestion.title}: {suggestion.description}"
                priority_actions.append(action)
            
            return priority_actions
            
        except Exception as e:
            self.logger.error(f"Error generating priority actions: {e}")
            return []

    def _calculate_estimated_improvement(self, suggestions: List[OptimizationSuggestion]) -> Dict[str, float]:
        """Calculate estimated improvement from suggestions."""
        try:
            improvements = {
                "performance": 0,
                "time": 0,
                "cost": 0,
                "resource": 0,
                "quality": 0
            }
            
            for suggestion in suggestions:
                opt_type = suggestion.optimization_type.value
                if opt_type in improvements:
                    improvements[opt_type] += suggestion.improvement_percentage
            
            return improvements
            
        except Exception as e:
            self.logger.error(f"Error calculating estimated improvement: {e}")
            return {}

    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        try:
            total_suggestions = sum(len(suggestions) for suggestions in self.optimization_history.values())
            total_processes = len(self.workflow_metrics)
            
            # Calculate average efficiency
            efficiency_scores = []
            for metrics in self.workflow_metrics.values():
                if hasattr(metrics, 'efficiency_score'):
                    efficiency_scores.append(metrics.efficiency_score)
                elif isinstance(metrics, dict) and 'efficiency_score' in metrics:
                    efficiency_scores.append(metrics['efficiency_score'])
            avg_efficiency = np.mean(efficiency_scores) if efficiency_scores else 0
            
            # Count suggestions by type
            suggestion_types = defaultdict(int)
            for suggestions in self.optimization_history.values():
                for suggestion in suggestions:
                    if hasattr(suggestion, 'optimization_type'):
                        suggestion_types[suggestion.optimization_type.value] += 1
                    elif isinstance(suggestion, dict) and 'optimization_type' in suggestion:
                        suggestion_types[suggestion['optimization_type']] += 1
                    else:
                        # Default to 'general' if we can't determine the type
                        suggestion_types['general'] += 1
            
            return {
                "total_processes_analyzed": total_processes,
                "total_suggestions_generated": total_suggestions,
                "average_efficiency_score": avg_efficiency,
                "suggestions_by_type": dict(suggestion_types),
                "processes_with_optimizations": len(self.optimization_history)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting optimization statistics: {e}")
            return {}

    def get_workflow_metrics(self, process_id: str) -> Optional[WorkflowMetrics]:
        """Get workflow metrics for a process."""
        return self.workflow_metrics.get(process_id)

    def get_optimization_history(self, process_id: str) -> List[OptimizationSuggestion]:
        """Get optimization history for a process."""
        return self.optimization_history.get(process_id, [])
