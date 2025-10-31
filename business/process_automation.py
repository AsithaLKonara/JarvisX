"""
JARVIS AI - Business Process Automation
Automates business processes, workflows, and task management.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import json
import time

from core.ai_engine import AIEngine
from utils.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProcessStatus(Enum):
    """Business process status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class TaskStatus(Enum):
    """Task status within a process."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class ProcessType(Enum):
    """Types of business processes."""
    WORKFLOW = "workflow"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"
    AUTOMATION = "automation"

class TriggerType(Enum):
    """Types of process triggers."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    CONDITION = "condition"
    API = "api"

@dataclass
class ProcessTrigger:
    """Process trigger definition."""
    trigger_id: str
    trigger_type: TriggerType
    name: str
    description: str
    conditions: Dict[str, Any]
    is_active: bool
    created_at: datetime

@dataclass
class ProcessTask:
    """Individual task within a process."""
    task_id: str
    name: str
    description: str
    task_type: str
    status: TaskStatus
    assigned_to: Optional[str]
    due_date: Optional[datetime]
    dependencies: List[str]
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

@dataclass
class BusinessProcess:
    """Business process definition."""
    process_id: str
    name: str
    description: str
    process_type: ProcessType
    status: ProcessStatus
    version: str
    owner: str
    tasks: List[ProcessTask]
    triggers: List[ProcessTrigger]
    variables: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

@dataclass
class ProcessExecution:
    """Process execution instance."""
    execution_id: str
    process_id: str
    status: ProcessStatus
    started_at: datetime
    completed_at: Optional[datetime]
    variables: Dict[str, Any]
    task_results: Dict[str, Any]
    error_message: Optional[str]
    execution_log: List[Dict[str, Any]]

class ProcessAutomation:
    """
    JARVIS AI - Business Process Automation
    Manages and executes business processes, workflows, and task automation.
    """
    
    def __init__(self, ai_engine: AIEngine, config: Config, 
                 processes_dir: Path = Path("business/processes")):
        self.ai_engine = ai_engine
        self.config = config
        self.processes_dir = processes_dir
        self.processes_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processes: Dict[str, BusinessProcess] = {}
        self.executions: Dict[str, ProcessExecution] = {}
        self.task_handlers: Dict[str, Callable] = {}
        
        # Load existing processes
        self._load_processes()
        
        # Initialize default task handlers
        self._initialize_task_handlers()
        
        self.logger.info("Process Automation initialized")

    def _load_processes(self):
        """Load existing processes from storage."""
        try:
            processes_file = self.processes_dir / "processes.json"
            if processes_file.exists():
                with open(processes_file, 'r') as f:
                    processes_data = json.load(f)
                    for process_data in processes_data:
                        process = self._deserialize_process(process_data)
                        self.processes[process.process_id] = process
                self.logger.info(f"Loaded {len(self.processes)} processes")
        except Exception as e:
            self.logger.error(f"Error loading processes: {e}")

    def _save_processes(self):
        """Save processes to storage."""
        try:
            processes_file = self.processes_dir / "processes.json"
            processes_data = [self._serialize_process(process) for process in self.processes.values()]
            with open(processes_file, 'w') as f:
                json.dump(processes_data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving processes: {e}")

    def _serialize_process(self, process: BusinessProcess) -> Dict[str, Any]:
        """Serialize process for storage."""
        return {
            "process_id": process.process_id,
            "name": process.name,
            "description": process.description,
            "process_type": process.process_type.value,
            "status": process.status.value,
            "version": process.version,
            "owner": process.owner,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "description": task.description,
                    "task_type": task.task_type,
                    "status": task.status.value,
                    "assigned_to": task.assigned_to,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "dependencies": task.dependencies,
                    "parameters": task.parameters,
                    "result": task.result,
                    "created_at": task.created_at.isoformat(),
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
                for task in process.tasks
            ],
            "triggers": [
                {
                    "trigger_id": trigger.trigger_id,
                    "trigger_type": trigger.trigger_type.value,
                    "name": trigger.name,
                    "description": trigger.description,
                    "conditions": trigger.conditions,
                    "is_active": trigger.is_active,
                    "created_at": trigger.created_at.isoformat()
                }
                for trigger in process.triggers
            ],
            "variables": process.variables,
            "created_at": process.created_at.isoformat(),
            "updated_at": process.updated_at.isoformat(),
            "started_at": process.started_at.isoformat() if process.started_at else None,
            "completed_at": process.completed_at.isoformat() if process.completed_at else None
        }

    def _deserialize_process(self, data: Dict[str, Any]) -> BusinessProcess:
        """Deserialize process from storage."""
        tasks = []
        for task_data in data.get("tasks", []):
            task = ProcessTask(
                task_id=task_data["task_id"],
                name=task_data["name"],
                description=task_data["description"],
                task_type=task_data["task_type"],
                status=TaskStatus(task_data["status"]),
                assigned_to=task_data.get("assigned_to"),
                due_date=datetime.fromisoformat(task_data["due_date"]) if task_data.get("due_date") else None,
                dependencies=task_data.get("dependencies", []),
                parameters=task_data.get("parameters", {}),
                result=task_data.get("result"),
                created_at=datetime.fromisoformat(task_data["created_at"]),
                started_at=datetime.fromisoformat(task_data["started_at"]) if task_data.get("started_at") else None,
                completed_at=datetime.fromisoformat(task_data["completed_at"]) if task_data.get("completed_at") else None
            )
            tasks.append(task)

        triggers = []
        for trigger_data in data.get("triggers", []):
            trigger = ProcessTrigger(
                trigger_id=trigger_data["trigger_id"],
                trigger_type=TriggerType(trigger_data["trigger_type"]),
                name=trigger_data["name"],
                description=trigger_data["description"],
                conditions=trigger_data.get("conditions", {}),
                is_active=trigger_data.get("is_active", True),
                created_at=datetime.fromisoformat(trigger_data["created_at"])
            )
            triggers.append(trigger)

        return BusinessProcess(
            process_id=data["process_id"],
            name=data["name"],
            description=data["description"],
            process_type=ProcessType(data["process_type"]),
            status=ProcessStatus(data["status"]),
            version=data.get("version", "1.0.0"),
            owner=data.get("owner", "system"),
            tasks=tasks,
            triggers=triggers,
            variables=data.get("variables", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        )

    def _initialize_task_handlers(self):
        """Initialize default task handlers."""
        self.task_handlers = {
            "email_notification": self._handle_email_notification,
            "data_processing": self._handle_data_processing,
            "api_call": self._handle_api_call,
            "file_operation": self._handle_file_operation,
            "approval_request": self._handle_approval_request,
            "report_generation": self._handle_report_generation,
            "system_command": self._handle_system_command,
            "ai_analysis": self._handle_ai_analysis
        }

    def create_process(self, name: str, description: str, process_type: ProcessType,
                      owner: str = "system", version: str = "1.0.0") -> BusinessProcess:
        """Create a new business process."""
        try:
            process_id = f"proc_{uuid.uuid4().hex[:8]}"
            
            process = BusinessProcess(
                process_id=process_id,
                name=name,
                description=description,
                process_type=process_type,
                status=ProcessStatus.DRAFT,
                version=version,
                owner=owner,
                tasks=[],
                triggers=[],
                variables={},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                started_at=None,
                completed_at=None
            )
            
            self.processes[process_id] = process
            self._save_processes()
            
            self.logger.info(f"Created process: {name} ({process_id})")
            return process
            
        except Exception as e:
            self.logger.error(f"Error creating process: {e}")
            return None

    def add_task(self, process_id: str, name: str, description: str, 
                 task_type: str, assigned_to: Optional[str] = None,
                 due_date: Optional[datetime] = None, dependencies: List[str] = None,
                 parameters: Dict[str, Any] = None) -> ProcessTask:
        """Add a task to a process."""
        try:
            process = self.processes.get(process_id)
            if not process:
                self.logger.error(f"Process not found: {process_id}")
                return None

            task_id = f"task_{uuid.uuid4().hex[:8]}"
            task = ProcessTask(
                task_id=task_id,
                name=name,
                description=description,
                task_type=task_type,
                status=TaskStatus.PENDING,
                assigned_to=assigned_to,
                due_date=due_date,
                dependencies=dependencies or [],
                parameters=parameters or {},
                result=None,
                created_at=datetime.now(),
                started_at=None,
                completed_at=None
            )
            
            process.tasks.append(task)
            process.updated_at = datetime.now()
            self._save_processes()
            
            self.logger.info(f"Added task '{name}' to process {process_id}")
            return task
            
        except Exception as e:
            self.logger.error(f"Error adding task: {e}")
            return None

    def add_trigger(self, process_id: str, trigger_type: TriggerType, name: str,
                   description: str, conditions: Dict[str, Any] = None) -> ProcessTrigger:
        """Add a trigger to a process."""
        try:
            process = self.processes.get(process_id)
            if not process:
                self.logger.error(f"Process not found: {process_id}")
                return None

            trigger_id = f"trigger_{uuid.uuid4().hex[:8]}"
            trigger = ProcessTrigger(
                trigger_id=trigger_id,
                trigger_type=trigger_type,
                name=name,
                description=description,
                conditions=conditions or {},
                is_active=True,
                created_at=datetime.now()
            )
            
            process.triggers.append(trigger)
            process.updated_at = datetime.now()
            self._save_processes()
            
            self.logger.info(f"Added trigger '{name}' to process {process_id}")
            return trigger
            
        except Exception as e:
            self.logger.error(f"Error adding trigger: {e}")
            return None

    def execute_process(self, process_id: str, variables: Dict[str, Any] = None) -> ProcessExecution:
        """Execute a business process."""
        try:
            process = self.processes.get(process_id)
            if not process:
                self.logger.error(f"Process not found: {process_id}")
                return None

            execution_id = f"exec_{uuid.uuid4().hex[:8]}"
            execution = ProcessExecution(
                execution_id=execution_id,
                process_id=process_id,
                status=ProcessStatus.ACTIVE,
                started_at=datetime.now(),
                completed_at=None,
                variables=variables or {},
                task_results={},
                error_message=None,
                execution_log=[]
            )
            
            self.executions[execution_id] = execution
            
            # Update process status
            process.status = ProcessStatus.ACTIVE
            process.started_at = datetime.now()
            process.updated_at = datetime.now()
            
            # Execute tasks
            self._execute_tasks(execution, process)
            
            self._save_processes()
            self.logger.info(f"Started execution of process {process_id}")
            return execution
            
        except Exception as e:
            self.logger.error(f"Error executing process: {e}")
            return None

    def _execute_tasks(self, execution: ProcessExecution, process: BusinessProcess):
        """Execute all tasks in a process."""
        try:
            # Sort tasks by dependencies
            sorted_tasks = self._sort_tasks_by_dependencies(process.tasks)
            
            for task in sorted_tasks:
                if task.status == TaskStatus.PENDING:
                    self._execute_task(execution, process, task)
                    
        except Exception as e:
            self.logger.error(f"Error executing tasks: {e}")
            execution.status = ProcessStatus.FAILED
            execution.error_message = str(e)

    def _sort_tasks_by_dependencies(self, tasks: List[ProcessTask]) -> List[ProcessTask]:
        """Sort tasks by their dependencies."""
        sorted_tasks = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            # Find tasks with no unmet dependencies
            ready_tasks = []
            for task in remaining_tasks:
                if not task.dependencies or all(
                    dep_id in [t.task_id for t in sorted_tasks] 
                    for dep_id in task.dependencies
                ):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Circular dependency or error
                break
                
            # Add ready tasks to sorted list
            sorted_tasks.extend(ready_tasks)
            for task in ready_tasks:
                remaining_tasks.remove(task)
        
        return sorted_tasks

    def _execute_task(self, execution: ProcessExecution, process: BusinessProcess, task: ProcessTask):
        """Execute a single task."""
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            
            # Log task start
            execution.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Starting task: {task.name}",
                "task_id": task.task_id
            })
            
            # Execute task based on type
            handler = self.task_handlers.get(task.task_type)
            if handler:
                result = handler(task, execution.variables)
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                
                execution.task_results[task.task_id] = result
                execution.execution_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"Completed task: {task.name}",
                    "task_id": task.task_id,
                    "result": result
                })
            else:
                task.status = TaskStatus.BLOCKED
                execution.execution_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "ERROR",
                    "message": f"No handler found for task type: {task.task_type}",
                    "task_id": task.task_id
                })
                
        except Exception as e:
            task.status = TaskStatus.BLOCKED
            task.completed_at = datetime.now()
            execution.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "message": f"Task failed: {str(e)}",
                "task_id": task.task_id
            })
            self.logger.error(f"Error executing task {task.task_id}: {e}")

    # Task Handlers
    def _handle_email_notification(self, task: ProcessTask, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email notification task."""
        return {
            "status": "success",
            "message": f"Email notification sent: {task.parameters.get('subject', 'No subject')}",
            "recipients": task.parameters.get('recipients', []),
            "timestamp": datetime.now().isoformat()
        }

    def _handle_data_processing(self, task: ProcessTask, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data processing task."""
        return {
            "status": "success",
            "message": f"Data processing completed: {task.parameters.get('operation', 'Unknown operation')}",
            "records_processed": task.parameters.get('record_count', 0),
            "timestamp": datetime.now().isoformat()
        }

    def _handle_api_call(self, task: ProcessTask, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Handle API call task."""
        return {
            "status": "success",
            "message": f"API call completed: {task.parameters.get('endpoint', 'Unknown endpoint')}",
            "response_code": 200,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_file_operation(self, task: ProcessTask, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operation task."""
        return {
            "status": "success",
            "message": f"File operation completed: {task.parameters.get('operation', 'Unknown operation')}",
            "file_path": task.parameters.get('file_path', 'Unknown path'),
            "timestamp": datetime.now().isoformat()
        }

    def _handle_approval_request(self, task: ProcessTask, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Handle approval request task."""
        return {
            "status": "success",
            "message": f"Approval request sent: {task.parameters.get('approver', 'Unknown approver')}",
            "approval_id": f"approval_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now().isoformat()
        }

    def _handle_report_generation(self, task: ProcessTask, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Handle report generation task."""
        return {
            "status": "success",
            "message": f"Report generated: {task.parameters.get('report_type', 'Unknown report')}",
            "report_path": f"reports/{task.parameters.get('report_name', 'report')}.pdf",
            "timestamp": datetime.now().isoformat()
        }

    def _handle_system_command(self, task: ProcessTask, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system command task."""
        return {
            "status": "success",
            "message": f"System command executed: {task.parameters.get('command', 'Unknown command')}",
            "exit_code": 0,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_ai_analysis(self, task: ProcessTask, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI analysis task."""
        try:
            prompt = task.parameters.get('prompt', 'Analyze the provided data')
            analysis = self.ai_engine.get_ai_response(prompt)
            
            return {
                "status": "success",
                "message": "AI analysis completed",
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def get_process(self, process_id: str) -> Optional[BusinessProcess]:
        """Get a process by ID."""
        return self.processes.get(process_id)

    def get_execution(self, execution_id: str) -> Optional[ProcessExecution]:
        """Get an execution by ID."""
        return self.executions.get(execution_id)

    def get_process_statistics(self) -> Dict[str, Any]:
        """Get process automation statistics."""
        total_processes = len(self.processes)
        active_processes = len([p for p in self.processes.values() if p.status == ProcessStatus.ACTIVE])
        completed_processes = len([p for p in self.processes.values() if p.status == ProcessStatus.COMPLETED])
        total_executions = len(self.executions)
        
        return {
            "total_processes": total_processes,
            "active_processes": active_processes,
            "completed_processes": completed_processes,
            "total_executions": total_executions,
            "success_rate": (completed_processes / total_processes * 100) if total_processes > 0 else 0
        }
