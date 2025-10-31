"""
Business Mode - Task Scheduler
Task management, prioritization, calendar integration.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class TaskScheduler:
    """Manage business tasks"""
    
    def __init__(self, db_path: str = './tasks.db'):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority TEXT,
                status TEXT,
                project TEXT,
                created_at TEXT
            )''')
            conn.commit()
            conn.close()
        except Exception:
            pass
    
    def create_task(self, title: str, due_date: str, priority: str = 'medium', description: str = '', project: str = '') -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO tasks (title, description, due_date, priority, status, project, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (title, description, due_date, priority, 'pending', project, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_tasks(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            query = "SELECT id, title, due_date, priority, status FROM tasks WHERE 1=1"
            params = []
            if status:
                query += " AND status = ?"
                params.append(status)
            if priority:
                query += " AND priority = ?"
                params.append(priority)
            cursor.execute(query, params)
            tasks = [{'id': r[0], 'title': r[1], 'due_date': r[2], 'priority': r[3], 'status': r[4]} for r in cursor.fetchall()]
            conn.close()
            return tasks
        except Exception:
            return []
    
    def complete_task(self, task_id: int) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", ('completed', task_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_overdue_tasks(self) -> List[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            today = datetime.now().isoformat().split('T')[0]
            cursor.execute('''SELECT id, title, due_date FROM tasks WHERE due_date < ? AND status != 'completed' ORDER BY due_date ASC''', (today,))
            tasks = [{'id': r[0], 'title': r[1], 'due_date': r[2]} for r in cursor.fetchall()]
            conn.close()
            return tasks
        except Exception:
            return []
    
    def get_task_count_by_priority(self) -> Dict[str, int]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
            counts = {r[0]: r[1] for r in cursor.fetchall()}
            conn.close()
            return counts
        except Exception:
            return {}
