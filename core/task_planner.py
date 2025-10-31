"""
JARVIS AI - Task Planner
Agentic reasoning framework for intelligent task decomposition and execution.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from core.ai_engine import AIEngine

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Subtask:
    """Individual subtask within a task plan."""
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = None
    estimated_duration: int = 0  # minutes
    actual_duration: int = 0
    result: Any = None
    error: str = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class TaskPlan:
    """Complete task plan with subtasks."""
    id: str
    main_task: str
    subtasks: List[Subtask]
    reasoning_chain: List[str]
    estimated_total_duration: int
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class ExecutionResult:
    """Result of task execution."""
    success: bool
    message: str
    data: Dict[str, Any]
    execution_time: float
    subtask_results: List[Dict[str, Any]]

class TaskPlanner:
    """
    Advanced task planner with ReAct-style reasoning.
    Breaks down complex commands into executable subtasks.
    """
    
    def __init__(self, ai_engine: AIEngine = None):
        """Initialize task planner."""
        self.logger = logging.getLogger(__name__)
        self.ai_engine = ai_engine or AIEngine()
        self.active_plans = {}
        self.completed_plans = {}
        
        # Reasoning patterns
        self.reasoning_patterns = {
            'react': self._react_reasoning,
            'chain_of_thought': self._chain_of_thought_reasoning,
            'step_by_step': self._step_by_step_reasoning
        }
        
        self.logger.info("Task Planner initialized")
    
    def decompose_task(self, command: str, context: Dict = None) -> TaskPlan:
        """
        Decompose a complex command into subtasks using AI reasoning.
        
        Args:
            command: The main task command
            context: Additional context information
            
        Returns:
            TaskPlan with subtasks and reasoning
        """
        try:
            self.logger.info(f"Decomposing task: {command}")
            
            # Generate reasoning chain
            reasoning_chain = self._generate_reasoning_chain(command, context)
            
            # Use AI to break down the task
            subtasks_data = self._ai_task_decomposition(command, context, reasoning_chain)
            
            # Create subtasks
            subtasks = []
            for i, subtask_data in enumerate(subtasks_data):
                subtask = Subtask(
                    id=f"subtask_{i+1}",
                    description=subtask_data['description'],
                    priority=TaskPriority(subtask_data.get('priority', 2)),
                    estimated_duration=subtask_data.get('duration', 0),
                    dependencies=subtask_data.get('dependencies', [])
                )
                subtasks.append(subtask)
            
            # Create task plan
            plan_id = f"plan_{int(datetime.now().timestamp())}"
            plan = TaskPlan(
                id=plan_id,
                main_task=command,
                subtasks=subtasks,
                reasoning_chain=reasoning_chain,
                estimated_total_duration=sum(st.estimated_duration for st in subtasks),
                priority=self._determine_priority(command, context)
            )
            
            # Store active plan
            self.active_plans[plan_id] = plan
            
            self.logger.info(f"Task decomposed into {len(subtasks)} subtasks")
            return plan
        
        except Exception as e:
            self.logger.error(f"Error decomposing task: {e}")
            raise
    
    def execute_plan(self, plan: TaskPlan) -> ExecutionResult:
        """
        Execute a task plan with dependency management.
        
        Args:
            plan: Task plan to execute
            
        Returns:
            ExecutionResult with execution details
        """
        try:
            start_time = datetime.now()
            self.logger.info(f"Executing task plan: {plan.id}")
            
            plan.status = TaskStatus.IN_PROGRESS
            subtask_results = []
            execution_success = True
            
            # Sort subtasks by priority and dependencies
            execution_order = self._determine_execution_order(plan.subtasks)
            
            for subtask in execution_order:
                try:
                    # Check dependencies
                    if not self._check_dependencies(subtask, subtask_results):
                        self.logger.warning(f"Dependencies not met for {subtask.id}")
                        continue
                    
                    # Execute subtask
                    subtask.status = TaskStatus.IN_PROGRESS
                    result = self._execute_subtask(subtask, plan)
                    
                    subtask_results.append({
                        'subtask_id': subtask.id,
                        'status': subtask.status.value,
                        'result': result,
                        'duration': subtask.actual_duration
                    })
                    
                    if subtask.status == TaskStatus.FAILED:
                        execution_success = False
                        self.logger.error(f"Subtask {subtask.id} failed: {subtask.error}")
                
                except Exception as e:
                    subtask.status = TaskStatus.FAILED
                    subtask.error = str(e)
                    execution_success = False
                    self.logger.error(f"Error executing subtask {subtask.id}: {e}")
            
            # Update plan status
            if execution_success:
                plan.status = TaskStatus.COMPLETED
                self.completed_plans[plan.id] = plan
                if plan.id in self.active_plans:
                    del self.active_plans[plan.id]
            else:
                plan.status = TaskStatus.FAILED
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ExecutionResult(
                success=execution_success,
                message=f"Plan execution {'completed' if execution_success else 'failed'}",
                data={'plan_id': plan.id, 'subtasks_executed': len(subtask_results)},
                execution_time=execution_time,
                subtask_results=subtask_results
            )
        
        except Exception as e:
            self.logger.error(f"Error executing plan: {e}")
            return ExecutionResult(
                success=False,
                message=f"Plan execution failed: {e}",
                data={},
                execution_time=0,
                subtask_results=[]
            )
    
    def reason_about_task(self, task: str) -> List[str]:
        """
        Generate reasoning chain for a task.
        
        Args:
            task: Task to reason about
            
        Returns:
            List of reasoning steps
        """
        try:
            reasoning_prompt = f"""
            Analyze this task and provide step-by-step reasoning:
            Task: {task}
            
            Consider:
            1. What needs to be done?
            2. What are the dependencies?
            3. What could go wrong?
            4. What are the success criteria?
            5. How can this be optimized?
            
            Provide clear, logical reasoning steps.
            """
            
            # Use AI engine for reasoning
            response = self.ai_engine._get_ai_response(reasoning_prompt)
            
            # Parse reasoning steps
            reasoning_steps = self._parse_reasoning_response(response)
            
            self.logger.info(f"Generated {len(reasoning_steps)} reasoning steps")
            return reasoning_steps
        
        except Exception as e:
            self.logger.error(f"Error generating reasoning: {e}")
            return [f"Error generating reasoning: {e}"]
    
    def _generate_reasoning_chain(self, command: str, context: Dict = None) -> List[str]:
        """Generate reasoning chain for task decomposition."""
        try:
            # Use different reasoning patterns based on task complexity
            if self._is_complex_task(command):
                return self.reasoning_patterns['react'](command, context)
            else:
                return self.reasoning_patterns['step_by_step'](command, context)
        
        except Exception as e:
            self.logger.error(f"Error generating reasoning chain: {e}")
            return ["Error in reasoning generation"]
    
    def _react_reasoning(self, command: str, context: Dict = None) -> List[str]:
        """ReAct-style reasoning (Reason → Act → Observe → Reflect)."""
        reasoning = [
            f"REASON: Analyzing task '{command}' to understand requirements",
            f"ACT: Breaking down into logical subtasks",
            f"OBSERVE: Identifying dependencies and constraints",
            f"REFLECT: Optimizing execution order and resource allocation"
        ]
        return reasoning
    
    def _chain_of_thought_reasoning(self, command: str, context: Dict = None) -> List[str]:
        """Chain-of-thought reasoning pattern."""
        reasoning = [
            f"Step 1: Understand the main objective: {command}",
            "Step 2: Identify required resources and capabilities",
            "Step 3: Break down into sequential steps",
            "Step 4: Identify potential obstacles and solutions",
            "Step 5: Plan execution strategy"
        ]
        return reasoning
    
    def _step_by_step_reasoning(self, command: str, context: Dict = None) -> List[str]:
        """Simple step-by-step reasoning."""
        reasoning = [
            f"Analyze: {command}",
            "Identify: Key components and requirements",
            "Plan: Sequential execution steps",
            "Execute: Follow the plan systematically"
        ]
        return reasoning
    
    def _ai_task_decomposition(self, command: str, context: Dict, reasoning_chain: List[str]) -> List[Dict]:
        """Use AI to decompose task into subtasks."""
        try:
            decomposition_prompt = f"""
            Task: {command}
            Context: {context or 'No additional context'}
            Reasoning: {'; '.join(reasoning_chain)}
            
            Break this task down into specific, actionable subtasks. For each subtask, provide:
            1. Description (what needs to be done)
            2. Priority (1=low, 2=medium, 3=high, 4=critical)
            3. Duration in minutes
            4. Dependencies (list of other subtask IDs this depends on)
            
            Format as JSON array of objects with keys: description, priority, duration, dependencies
            """
            
            response = self.ai_engine._get_ai_response(decomposition_prompt)
            
            # Parse AI response
            subtasks = self._parse_subtasks_response(response)
            
            return subtasks
        
        except Exception as e:
            self.logger.error(f"Error in AI task decomposition: {e}")
            # Fallback to simple decomposition
            return self._simple_task_decomposition(command)
    
    def _parse_subtasks_response(self, response: str) -> List[Dict]:
        """Parse AI response into subtask data."""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._fallback_parse_subtasks(response)
        
        except Exception as e:
            self.logger.warning(f"Error parsing AI response: {e}")
            return self._fallback_parse_subtasks(response)
    
    def _fallback_parse_subtasks(self, response: str) -> List[Dict]:
        """Fallback parsing when JSON extraction fails."""
        lines = response.split('\n')
        subtasks = []
        
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('#'):
                subtasks.append({
                    'description': line.strip(),
                    'priority': 2,
                    'duration': 5,
                    'dependencies': []
                })
        
        return subtasks[:5]  # Limit to 5 subtasks
    
    def _simple_task_decomposition(self, command: str) -> List[Dict]:
        """Simple fallback task decomposition."""
        return [
            {
                'description': f"Analyze requirements for: {command}",
                'priority': 3,
                'duration': 2,
                'dependencies': []
            },
            {
                'description': f"Execute main task: {command}",
                'priority': 4,
                'duration': 10,
                'dependencies': ['subtask_1']
            },
            {
                'description': f"Verify completion of: {command}",
                'priority': 2,
                'duration': 1,
                'dependencies': ['subtask_2']
            }
        ]
    
    def _determine_priority(self, command: str, context: Dict = None) -> TaskPriority:
        """Determine task priority based on command and context."""
        high_priority_keywords = ['urgent', 'immediate', 'critical', 'emergency']
        low_priority_keywords = ['later', 'when possible', 'optional']
        
        command_lower = command.lower()
        
        if any(keyword in command_lower for keyword in high_priority_keywords):
            return TaskPriority.CRITICAL
        elif any(keyword in command_lower for keyword in low_priority_keywords):
            return TaskPriority.LOW
        else:
            return TaskPriority.MEDIUM
    
    def _is_complex_task(self, command: str) -> bool:
        """Determine if task is complex based on keywords and length."""
        complex_keywords = ['create', 'build', 'develop', 'analyze', 'generate', 'organize']
        return (len(command.split()) > 5 or 
                any(keyword in command.lower() for keyword in complex_keywords))
    
    def _determine_execution_order(self, subtasks: List[Subtask]) -> List[Subtask]:
        """Determine optimal execution order based on dependencies."""
        # Simple topological sort
        ordered = []
        remaining = subtasks.copy()
        
        while remaining:
            # Find tasks with no unmet dependencies
            ready_tasks = []
            for task in remaining:
                if not task.dependencies or all(
                    dep in [t.id for t in ordered] for dep in task.dependencies
                ):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Handle circular dependencies
                ready_tasks = [remaining[0]]
            
            # Sort by priority
            ready_tasks.sort(key=lambda t: t.priority.value, reverse=True)
            ordered.extend(ready_tasks)
            
            for task in ready_tasks:
                remaining.remove(task)
        
        return ordered
    
    def _check_dependencies(self, subtask: Subtask, completed_results: List[Dict]) -> bool:
        """Check if subtask dependencies are met."""
        if not subtask.dependencies:
            return True
        
        completed_ids = [result['subtask_id'] for result in completed_results]
        return all(dep in completed_ids for dep in subtask.dependencies)
    
    def _execute_subtask(self, subtask: Subtask, plan: TaskPlan) -> Any:
        """Execute individual subtask."""
        try:
            start_time = datetime.now()
            self.logger.info(f"Executing subtask: {subtask.description}")
            
            # Simulate subtask execution
            # In a real implementation, this would call appropriate handlers
            result = self._simulate_subtask_execution(subtask, plan)
            
            subtask.status = TaskStatus.COMPLETED
            subtask.result = result
            subtask.actual_duration = int((datetime.now() - start_time).total_seconds() / 60)
            
            self.logger.info(f"Subtask completed: {subtask.id}")
            return result
        
        except Exception as e:
            subtask.status = TaskStatus.FAILED
            subtask.error = str(e)
            self.logger.error(f"Subtask failed: {subtask.id} - {e}")
            raise
    
    def _simulate_subtask_execution(self, subtask: Subtask, plan: TaskPlan) -> Any:
        """Simulate subtask execution (placeholder for real implementation)."""
        # This would be replaced with actual task execution logic
        import time
        time.sleep(0.1)  # Simulate work
        
        return {
            'subtask_id': subtask.id,
            'description': subtask.description,
            'status': 'completed',
            'result': f"Successfully executed: {subtask.description}"
        }
    
    def _parse_reasoning_response(self, response: str) -> List[str]:
        """Parse AI reasoning response into steps."""
        # Split by common delimiters
        steps = []
        for delimiter in ['\n', ';', '.']:
            if delimiter in response:
                steps = [step.strip() for step in response.split(delimiter) if step.strip()]
                break
        
        if not steps:
            steps = [response.strip()]
        
        return steps[:10]  # Limit to 10 steps
    
    def get_active_plans(self) -> Dict[str, TaskPlan]:
        """Get all active task plans."""
        return self.active_plans.copy()
    
    def get_completed_plans(self) -> Dict[str, TaskPlan]:
        """Get all completed task plans."""
        return self.completed_plans.copy()
    
    def get_plan_status(self, plan_id: str) -> Optional[Dict]:
        """Get status of a specific plan."""
        if plan_id in self.active_plans:
            plan = self.active_plans[plan_id]
        elif plan_id in self.completed_plans:
            plan = self.completed_plans[plan_id]
        else:
            return None
        
        return {
            'plan_id': plan.id,
            'main_task': plan.main_task,
            'status': plan.status.value,
            'subtasks': [
                {
                    'id': st.id,
                    'description': st.description,
                    'status': st.status.value,
                    'priority': st.priority.value
                }
                for st in plan.subtasks
            ],
            'progress': self._calculate_progress(plan)
        }
    
    def _calculate_progress(self, plan: TaskPlan) -> float:
        """Calculate completion progress for a plan."""
        if not plan.subtasks:
            return 0.0
        
        completed = sum(1 for st in plan.subtasks if st.status == TaskStatus.COMPLETED)
        return (completed / len(plan.subtasks)) * 100
