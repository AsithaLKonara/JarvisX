"""
Task Manager - Handles task creation, tracking, and execution
Phase 1 of Jarvis X V2
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority enumeration"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Task representation"""
    id: str
    name: str
    mode: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

class TaskManager:
    """Manages task lifecycle and execution"""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.task_counter = 0
    
    def create_task(self, name: str, mode: str, priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Create a new task"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(datetime.now().timestamp())}"
        
        task = Task(
            id=task_id,
            name=name,
            mode=mode,
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.tasks.append(task)
        return task_id
    
    def start_task(self, task_id: str) -> bool:
        """Start a task"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.updated_at = datetime.now()
        return True
    
    def complete_task(self, task_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Complete a task"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.updated_at = datetime.now()
        if metadata:
            task.metadata.update(metadata)
        return True
    
    def fail_task(self, task_id: str, error_message: str) -> bool:
        """Mark a task as failed"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        task.status = TaskStatus.FAILED
        task.error_message = error_message
        task.updated_at = datetime.now()
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_tasks_by_mode(self, mode: str) -> List[Task]:
        """Get all tasks for a specific mode"""
        return [task for task in self.tasks if task.mode == mode]
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks"""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]
    
    def get_task_stats(self) -> Dict[str, int]:
        """Get task statistics"""
        stats = {}
        for status in TaskStatus:
            stats[status.value] = len([t for t in self.tasks if t.status == status])
        return stats



