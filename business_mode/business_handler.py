"""
Business Mode Handler - Main orchestration component
Integrates all business mode sub-modules for Command Center.
"""

from typing import Dict, List, Optional
from datetime import datetime
from .finance_tracker import FinanceTracker
from .invoice_generator import InvoiceGenerator
from .email_templates import EmailTemplates
from .task_scheduler import TaskScheduler
from .client_database import ClientDatabase


class BusinessModeHandler:
    """Main orchestration for Business Mode"""
    
    def __init__(self):
        self.finance_tracker = FinanceTracker()
        self.invoice_generator = InvoiceGenerator()
        self.email_templates = EmailTemplates()
        self.task_scheduler = TaskScheduler()
        self.client_database = ClientDatabase()
        self.workflow_history = []
    
    def add_income(self, amount: float, description: str = '', project: str = '') -> bool:
        return self.finance_tracker.add_income(amount, description, project)
    
    def add_expense(self, amount: float, category: str, description: str = '') -> bool:
        return self.finance_tracker.add_expense(amount, category, description)
    
    def get_financial_summary(self) -> Dict:
        return {
            'balance': self.finance_tracker.get_balance(),
            'monthly': self.finance_tracker.get_monthly_summary(),
            'taxes': self.finance_tracker.calculate_taxes()
        }
    
    def create_invoice(self, client_name: str, items: List[Dict], tax_rate: float = 0.0) -> Optional[str]:
        return self.invoice_generator.create_invoice(client_name, items, tax_rate)
    
    def create_email(self, template_name: str, fields: Dict) -> Optional[Dict]:
        return self.email_templates.create_email(template_name, fields)
    
    def get_email_templates(self) -> List[str]:
        return self.email_templates.list_templates()
    
    def create_task(self, title: str, due_date: str, priority: str = 'medium') -> bool:
        return self.task_scheduler.create_task(title, due_date, priority)
    
    def get_pending_tasks(self) -> List[Dict]:
        return self.task_scheduler.get_tasks(status='pending')
    
    def complete_task(self, task_id: int) -> bool:
        return self.task_scheduler.complete_task(task_id)
    
    def get_overdue_tasks(self) -> List[Dict]:
        return self.task_scheduler.get_overdue_tasks()
    
    def add_client(self, name: str, email: str = '', company: str = '') -> Optional[int]:
        return self.client_database.add_client(name, email=email, company=company)
    
    def search_clients(self, query: str = '') -> List[Dict]:
        return self.client_database.search_clients(query)
    
    def log_client_interaction(self, client_id: int, interaction_type: str, notes: str = '') -> bool:
        return self.client_database.add_interaction(client_id, interaction_type, notes)
    
    def get_client_history(self, client_id: int) -> List[Dict]:
        return self.client_database.get_client_interactions(client_id)
    
    def complete_client_workflow(self, client_name: str, project_name: str, budget: float) -> Dict:
        try:
            client_id = self.add_client(client_name)
            self.add_income(budget, description=f"Project: {project_name}", project=project_name)
            invoice_id = self.create_invoice(client_name, [{'description': project_name, 'amount': budget}])
            self._log_operation('complete_workflow', {'client': client_name, 'project': project_name})
            return {'client_id': client_id, 'invoice_id': invoice_id, 'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_daily_summary(self) -> Dict:
        return {
            'financial': self.get_financial_summary(),
            'overdue_tasks': self.get_overdue_tasks(),
            'pending_tasks': self.get_pending_tasks()[:5],
            'generated_at': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'finance_tracker': 'operational',
            'invoice_generator': 'operational',
            'email_templates': 'operational',
            'task_scheduler': 'operational',
            'client_database': 'operational',
            'workflow_history_count': len(self.workflow_history)
        }
    
    def _log_operation(self, operation: str, details: Dict):
        self.workflow_history.append({
            'operation': operation,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
