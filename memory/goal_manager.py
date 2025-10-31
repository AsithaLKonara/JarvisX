"""
JARVIS AI - Goal Memory System
Long-term objective tracking and semantic memory management.
"""

import json
import logging
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

class GoalStatus(Enum):
    """Goal status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class GoalPriority(Enum):
    """Goal priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Goal:
    """Individual goal with metadata."""
    id: str
    title: str
    description: str
    status: GoalStatus = GoalStatus.ACTIVE
    priority: GoalPriority = GoalPriority.MEDIUM
    created_at: datetime = None
    updated_at: datetime = None
    completed_at: datetime = None
    due_date: datetime = None
    tags: List[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.tags is None:
            self.tags = []
        if self.context is None:
            self.context = {}

@dataclass
class Subtask:
    """Subtask within a goal."""
    id: str
    goal_id: str
    title: str
    description: str
    status: GoalStatus = GoalStatus.ACTIVE
    priority: GoalPriority = GoalPriority.MEDIUM
    dependencies: List[str] = None
    created_at: datetime = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ProjectHistory:
    """Project history entry."""
    id: str
    project_name: str
    description: str
    start_date: datetime
    end_date: datetime = None
    status: str = "active"
    outcomes: List[str] = None
    lessons_learned: List[str] = None
    technologies_used: List[str] = None
    
    def __post_init__(self):
        if self.outcomes is None:
            self.outcomes = []
        if self.lessons_learned is None:
            self.lessons_learned = []
        if self.technologies_used is None:
            self.technologies_used = []

class GoalManager:
    """
    Advanced goal memory system with semantic search and long-term tracking.
    Manages goals, subtasks, and project history with vector database integration.
    """
    
    def __init__(self, db_path: str = "jarvis_goals.db"):
        """Initialize goal manager."""
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.connection = None
        
        # Initialize database
        self._init_database()
        
        # Vector database for semantic search (placeholder for FAISS/ChromaDB)
        self.vector_db = None
        self._init_vector_db()
        
        self.logger.info("Goal Manager initialized")
    
    def _init_database(self):
        """Initialize SQLite database for goals."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            self._create_tables()
            
            self.logger.info(f"Goal database initialized: {self.db_path}")
        
        except Exception as e:
            self.logger.error(f"Error initializing goal database: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables."""
        cursor = self.connection.cursor()
        
        # Goals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                priority INTEGER DEFAULT 2,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                due_date TIMESTAMP,
                tags TEXT,
                context TEXT
            )
        """)
        
        # Subtasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subtasks (
                id TEXT PRIMARY KEY,
                goal_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                priority INTEGER DEFAULT 2,
                dependencies TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES goals (id)
            )
        """)
        
        # Project history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_history (
                id TEXT PRIMARY KEY,
                project_name TEXT NOT NULL,
                description TEXT,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                status TEXT DEFAULT 'active',
                outcomes TEXT,
                lessons_learned TEXT,
                technologies_used TEXT
            )
        """)
        
        # Goal relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goal_relationships (
                id TEXT PRIMARY KEY,
                parent_goal_id TEXT,
                child_goal_id TEXT,
                relationship_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_goal_id) REFERENCES goals (id),
                FOREIGN KEY (child_goal_id) REFERENCES goals (id)
            )
        """)
        
        self.connection.commit()
        self.logger.info("Goal database tables created successfully")
    
    def _init_vector_db(self):
        """Initialize vector database for semantic search."""
        try:
            # Placeholder for vector database integration
            # In production, this would use FAISS or ChromaDB
            self.vector_db = {
                'embeddings': {},
                'index': None
            }
            self.logger.info("Vector database initialized (placeholder)")
        
        except Exception as e:
            self.logger.warning(f"Vector database initialization failed: {e}")
            self.vector_db = None
    
    def create_goal(self, title: str, description: str = "", priority: GoalPriority = GoalPriority.MEDIUM,
                   due_date: datetime = None, tags: List[str] = None, context: Dict = None) -> str:
        """
        Create a new goal.
        
        Args:
            title: Goal title
            description: Goal description
            priority: Goal priority
            due_date: Optional due date
            tags: Optional tags
            context: Optional context data
            
        Returns:
            Goal ID
        """
        try:
            goal_id = f"goal_{int(datetime.now().timestamp())}"
            
            goal = Goal(
                id=goal_id,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                tags=tags or [],
                context=context or {}
            )
            
            # Store in database
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO goals (id, title, description, status, priority, due_date, tags, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                goal.id,
                goal.title,
                goal.description,
                goal.status.value,
                goal.priority.value,
                goal.due_date,
                json.dumps(goal.tags),
                json.dumps(goal.context)
            ))
            
            self.connection.commit()
            
            # Add to vector database
            self._add_to_vector_db(goal)
            
            self.logger.info(f"Goal created: {goal_id}")
            return goal_id
        
        except Exception as e:
            self.logger.error(f"Error creating goal: {e}")
            raise
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get goal by ID."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_goal(row)
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting goal {goal_id}: {e}")
            return None
    
    def update_goal(self, goal_id: str, **updates) -> bool:
        """Update goal with new data."""
        try:
            goal = self.get_goal(goal_id)
            if not goal:
                return False
            
            # Update fields
            for key, value in updates.items():
                if hasattr(goal, key):
                    setattr(goal, key, value)
            
            goal.updated_at = datetime.now()
            
            # Update database
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE goals SET
                    title = ?, description = ?, status = ?, priority = ?,
                    updated_at = ?, completed_at = ?, due_date = ?,
                    tags = ?, context = ?
                WHERE id = ?
            """, (
                goal.title, goal.description, goal.status.value, goal.priority.value,
                goal.updated_at, goal.completed_at, goal.due_date,
                json.dumps(goal.tags), json.dumps(goal.context), goal_id
            ))
            
            self.connection.commit()
            
            # Update vector database
            self._update_vector_db(goal)
            
            self.logger.info(f"Goal updated: {goal_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error updating goal {goal_id}: {e}")
            return False
    
    def complete_goal(self, goal_id: str) -> bool:
        """Mark goal as completed."""
        return self.update_goal(goal_id, status=GoalStatus.COMPLETED, completed_at=datetime.now())
    
    def add_subtask(self, goal_id: str, title: str, description: str = "",
                   priority: GoalPriority = GoalPriority.MEDIUM, dependencies: List[str] = None) -> str:
        """Add subtask to a goal."""
        try:
            subtask_id = f"subtask_{int(datetime.now().timestamp())}"
            
            subtask = Subtask(
                id=subtask_id,
                goal_id=goal_id,
                title=title,
                description=description,
                priority=priority,
                dependencies=dependencies or []
            )
            
            # Store in database
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO subtasks (id, goal_id, title, description, status, priority, dependencies)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                subtask.id, subtask.goal_id, subtask.title, subtask.description,
                subtask.status.value, subtask.priority.value, json.dumps(subtask.dependencies)
            ))
            
            self.connection.commit()
            
            self.logger.info(f"Subtask created: {subtask_id}")
            return subtask_id
        
        except Exception as e:
            self.logger.error(f"Error creating subtask: {e}")
            raise
    
    def get_goal_subtasks(self, goal_id: str) -> List[Subtask]:
        """Get all subtasks for a goal."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM subtasks WHERE goal_id = ?", (goal_id,))
            rows = cursor.fetchall()
            
            return [self._row_to_subtask(row) for row in rows]
        
        except Exception as e:
            self.logger.error(f"Error getting subtasks for goal {goal_id}: {e}")
            return []
    
    def get_active_goals(self) -> List[Goal]:
        """Get all active goals."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM goals WHERE status = 'active' ORDER BY priority DESC, created_at")
            rows = cursor.fetchall()
            
            return [self._row_to_goal(row) for row in rows]
        
        except Exception as e:
            self.logger.error(f"Error getting active goals: {e}")
            return []
    
    def get_goals_by_priority(self, priority: GoalPriority) -> List[Goal]:
        """Get goals by priority level."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM goals WHERE priority = ? ORDER BY created_at", (priority.value,))
            rows = cursor.fetchall()
            
            return [self._row_to_goal(row) for row in rows]
        
        except Exception as e:
            self.logger.error(f"Error getting goals by priority: {e}")
            return []
    
    def search_goals(self, query: str, limit: int = 10) -> List[Goal]:
        """Search goals using semantic search."""
        try:
            # Simple text search (placeholder for vector search)
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM goals 
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY priority DESC, created_at
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            rows = cursor.fetchall()
            
            return [self._row_to_goal(row) for row in rows]
        
        except Exception as e:
            self.logger.error(f"Error searching goals: {e}")
            return []
    
    def add_project_history(self, project_name: str, description: str = "",
                          start_date: datetime = None, technologies: List[str] = None) -> str:
        """Add project to history."""
        try:
            project_id = f"project_{int(datetime.now().timestamp())}"
            
            if start_date is None:
                start_date = datetime.now()
            
            project = ProjectHistory(
                id=project_id,
                project_name=project_name,
                description=description,
                start_date=start_date,
                technologies_used=technologies or []
            )
            
            # Store in database
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO project_history (id, project_name, description, start_date, technologies_used)
                VALUES (?, ?, ?, ?, ?)
            """, (
                project.id, project.project_name, project.description,
                project.start_date, json.dumps(project.technologies_used)
            ))
            
            self.connection.commit()
            
            self.logger.info(f"Project added to history: {project_id}")
            return project_id
        
        except Exception as e:
            self.logger.error(f"Error adding project history: {e}")
            raise
    
    def complete_project(self, project_id: str, outcomes: List[str] = None, lessons: List[str] = None) -> bool:
        """Mark project as completed."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE project_history SET
                    status = 'completed', end_date = ?, outcomes = ?, lessons_learned = ?
                WHERE id = ?
            """, (datetime.now(), json.dumps(outcomes or []), json.dumps(lessons or []), project_id))
            
            self.connection.commit()
            
            self.logger.info(f"Project completed: {project_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error completing project {project_id}: {e}")
            return False
    
    def get_project_history(self, limit: int = 20) -> List[ProjectHistory]:
        """Get project history."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM project_history 
                ORDER BY start_date DESC 
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            
            return [self._row_to_project(row) for row in rows]
        
        except Exception as e:
            self.logger.error(f"Error getting project history: {e}")
            return []
    
    def get_goals_summary(self) -> Dict[str, Any]:
        """Get comprehensive goals summary."""
        try:
            cursor = self.connection.cursor()
            
            # Count goals by status
            cursor.execute("SELECT status, COUNT(*) FROM goals GROUP BY status")
            status_counts = dict(cursor.fetchall())
            
            # Count goals by priority
            cursor.execute("SELECT priority, COUNT(*) FROM goals GROUP BY priority")
            priority_counts = dict(cursor.fetchall())
            
            # Get recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM goals 
                WHERE created_at > datetime('now', '-7 days')
            """)
            recent_goals = cursor.fetchone()[0]
            
            # Get completion rate
            cursor.execute("SELECT COUNT(*) FROM goals WHERE status = 'completed'")
            completed = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM goals")
            total = cursor.fetchone()[0]
            completion_rate = (completed / total * 100) if total > 0 else 0
            
            return {
                'total_goals': total,
                'status_breakdown': status_counts,
                'priority_breakdown': priority_counts,
                'recent_goals': recent_goals,
                'completion_rate': round(completion_rate, 2),
                'active_goals': len(self.get_active_goals())
            }
        
        except Exception as e:
            self.logger.error(f"Error getting goals summary: {e}")
            return {}
    
    def _row_to_goal(self, row) -> Goal:
        """Convert database row to Goal object."""
        return Goal(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            status=GoalStatus(row['status']),
            priority=GoalPriority(row['priority']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
            due_date=datetime.fromisoformat(row['due_date']) if row['due_date'] else None,
            tags=json.loads(row['tags']) if row['tags'] else [],
            context=json.loads(row['context']) if row['context'] else {}
        )
    
    def _row_to_subtask(self, row) -> Subtask:
        """Convert database row to Subtask object."""
        return Subtask(
            id=row['id'],
            goal_id=row['goal_id'],
            title=row['title'],
            description=row['description'],
            status=GoalStatus(row['status']),
            priority=GoalPriority(row['priority']),
            dependencies=json.loads(row['dependencies']) if row['dependencies'] else [],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None
        )
    
    def _row_to_project(self, row) -> ProjectHistory:
        """Convert database row to ProjectHistory object."""
        return ProjectHistory(
            id=row['id'],
            project_name=row['project_name'],
            description=row['description'],
            start_date=datetime.fromisoformat(row['start_date']) if row['start_date'] else None,
            end_date=datetime.fromisoformat(row['end_date']) if row['end_date'] else None,
            status=row['status'],
            outcomes=json.loads(row['outcomes']) if row['outcomes'] else [],
            lessons_learned=json.loads(row['lessons_learned']) if row['lessons_learned'] else [],
            technologies_used=json.loads(row['technologies_used']) if row['technologies_used'] else []
        )
    
    def _add_to_vector_db(self, goal: Goal):
        """Add goal to vector database for semantic search."""
        try:
            if self.vector_db:
                # Placeholder for vector embedding
                text = f"{goal.title} {goal.description}"
                self.vector_db['embeddings'][goal.id] = {
                    'text': text,
                    'embedding': None  # Would be actual vector embedding
                }
        except Exception as e:
            self.logger.warning(f"Error adding to vector DB: {e}")
    
    def _update_vector_db(self, goal: Goal):
        """Update goal in vector database."""
        try:
            if self.vector_db and goal.id in self.vector_db['embeddings']:
                text = f"{goal.title} {goal.description}"
                self.vector_db['embeddings'][goal.id]['text'] = text
        except Exception as e:
            self.logger.warning(f"Error updating vector DB: {e}")
    
    def close(self):
        """Close database connection."""
        try:
            if self.connection:
                self.connection.close()
                self.logger.info("Goal database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database: {e}")
    
    def __del__(self):
        """Destructor to ensure database connection is closed."""
        self.close()
