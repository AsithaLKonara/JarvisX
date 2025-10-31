"""
Business Mode - Finance Tracker
Income/expense tracking, profitability analysis, tax calculations.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    """Transaction types"""
    INCOME = 'income'
    EXPENSE = 'expense'


class ExpenseCategory(Enum):
    """Expense categories"""
    SUPPLIES = 'supplies'
    MARKETING = 'marketing'
    UTILITIES = 'utilities'
    TRAVEL = 'travel'
    OTHER = 'other'


class FinanceTracker:
    """Manage business finances"""
    
    TAX_RATES = {'federal': 0.24, 'state': 0.10, 'local': 0.02}
    
    def __init__(self, db_path: str = './finance.db'):
        """Initialize finance tracker"""
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                type TEXT,
                amount REAL,
                category TEXT,
                description TEXT,
                project TEXT,
                date TEXT,
                created_at TEXT
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                budget REAL,
                status TEXT,
                created_at TEXT
            )''')
            conn.commit()
            conn.close()
        except Exception:
            pass
    
    def add_income(self, amount: float, description: str = '', project: str = '') -> bool:
        """Add income transaction"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute('''INSERT INTO transactions 
                (type, amount, category, description, project, date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                ('income', amount, 'income', description, project, 
                 now.strftime('%Y-%m-%d'), now.isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def add_expense(self, amount: float, category: str = 'other', description: str = '', project: str = '') -> bool:
        """Add expense transaction"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute('''INSERT INTO transactions 
                (type, amount, category, description, project, date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                ('expense', amount, category, description, project,
                 now.strftime('%Y-%m-%d'), now.isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_balance(self) -> float:
        """Get current balance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'")
            income = cursor.fetchone()[0] or 0
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")
            expenses = cursor.fetchone()[0] or 0
            conn.close()
            return income - expenses
        except Exception:
            return 0.0
    
    def get_monthly_summary(self) -> Dict:
        """Get monthly financial summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            today = datetime.now()
            month_start = today.strftime('%Y-%m-01')
            cursor.execute('''SELECT SUM(amount) FROM transactions 
                WHERE type = 'income' AND date >= ?''', (month_start,))
            monthly_income = cursor.fetchone()[0] or 0
            cursor.execute('''SELECT SUM(amount) FROM transactions 
                WHERE type = 'expense' AND date >= ?''', (month_start,))
            monthly_expenses = cursor.fetchone()[0] or 0
            conn.close()
            return {'income': monthly_income, 'expenses': monthly_expenses, 'net': monthly_income - monthly_expenses}
        except Exception:
            return {'income': 0, 'expenses': 0, 'net': 0}
    
    def calculate_taxes(self) -> Dict:
        """Calculate estimated taxes"""
        try:
            balance = self.get_balance()
            return {'federal': balance * self.TAX_RATES['federal'], 'state': balance * self.TAX_RATES['state'], 
                   'local': balance * self.TAX_RATES['local'], 'total': balance * sum(self.TAX_RATES.values())}
        except Exception:
            return {'federal': 0, 'state': 0, 'local': 0, 'total': 0}
    
    def create_project(self, name: str, budget: float) -> bool:
        """Create project with budget"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO projects (name, budget, status, created_at) VALUES (?, ?, ?, ?)''',
                (name, budget, 'active', datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_project_profitability(self, project_name: str) -> Optional[Dict]:
        """Get project profitability"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT SUM(amount) FROM transactions WHERE type = 'income' AND project = ?''', (project_name,))
            income = cursor.fetchone()[0] or 0
            cursor.execute('''SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND project = ?''', (project_name,))
            expenses = cursor.fetchone()[0] or 0
            conn.close()
            return {'income': income, 'expenses': expenses, 'profit': income - expenses, 
                   'margin': ((income - expenses) / income * 100) if income > 0 else 0}
        except Exception:
            return None
    
    def list_projects(self) -> List[Dict]:
        """List all projects"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, budget, status FROM projects")
            projects = [{'id': r[0], 'name': r[1], 'budget': r[2], 'status': r[3]} for r in cursor.fetchall()]
            conn.close()
            return projects
        except Exception:
            return []
    
    def get_expense_by_category(self) -> Dict[str, float]:
        """Get expenses by category"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT category, SUM(amount) FROM transactions WHERE type = 'expense' GROUP BY category''')
            expenses = {r[0]: r[1] for r in cursor.fetchall()}
            conn.close()
            return expenses
        except Exception:
            return {}
