"""
JARVIS AI - CRM Integration
Integrates with CRM systems and project management tools.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import json
import requests

from core.ai_engine import AIEngine
from utils.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CRMType(Enum):
    """Types of CRM systems."""
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    PIPEDRIVE = "pipedrive"
    ZOHO = "zoho"
    CUSTOM = "custom"

class ContactStatus(Enum):
    """Contact status in CRM."""
    LEAD = "lead"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    INACTIVE = "inactive"

class DealStage(Enum):
    """Deal stages in sales pipeline."""
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Contact:
    """CRM contact record."""
    contact_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    status: ContactStatus
    source: str
    created_at: datetime
    updated_at: datetime
    custom_fields: Dict[str, Any]

@dataclass
class Deal:
    """CRM deal record."""
    deal_id: str
    title: str
    value: float
    currency: str
    stage: DealStage
    contact_id: str
    owner: str
    created_at: datetime
    updated_at: datetime
    expected_close_date: Optional[datetime]
    probability: float
    custom_fields: Dict[str, Any]

@dataclass
class Task:
    """CRM task record."""
    task_id: str
    title: str
    description: str
    due_date: Optional[datetime]
    priority: TaskPriority
    assigned_to: str
    contact_id: Optional[str]
    deal_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class Project:
    """Project management record."""
    project_id: str
    name: str
    description: str
    status: str
    owner: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget: Optional[float]
    created_at: datetime
    updated_at: datetime

class CRMIntegration:
    """
    JARVIS AI - CRM Integration
    Integrates with various CRM systems and project management tools.
    """
    
    def __init__(self, ai_engine: AIEngine, config: Config, 
                 crm_type: CRMType = CRMType.CUSTOM):
        self.ai_engine = ai_engine
        self.config = config
        self.crm_type = crm_type
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # CRM API configuration
        self.api_base_url = self.config.get(f'{crm_type.value.upper()}_API_URL', '')
        self.api_key = self.config.get(f'{crm_type.value.upper()}_API_KEY', '')
        self.api_token = self.config.get(f'{crm_type.value.upper()}_API_TOKEN', '')
        
        # Local storage for demo purposes
        self.contacts: Dict[str, Contact] = {}
        self.deals: Dict[str, Deal] = {}
        self.tasks: Dict[str, Task] = {}
        self.projects: Dict[str, Project] = {}
        
        # Load existing data
        self._load_data()
        
        self.logger.info(f"CRM Integration initialized for {crm_type.value}")

    def _load_data(self):
        """Load existing CRM data from storage."""
        try:
            data_dir = Path("business/crm_data")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Load contacts
            contacts_file = data_dir / "contacts.json"
            if contacts_file.exists():
                with open(contacts_file, 'r') as f:
                    contacts_data = json.load(f)
                    for contact_data in contacts_data:
                        contact = self._deserialize_contact(contact_data)
                        self.contacts[contact.contact_id] = contact
            
            # Load deals
            deals_file = data_dir / "deals.json"
            if deals_file.exists():
                with open(deals_file, 'r') as f:
                    deals_data = json.load(f)
                    for deal_data in deals_data:
                        deal = self._deserialize_deal(deal_data)
                        self.deals[deal.deal_id] = deal
            
            # Load tasks
            tasks_file = data_dir / "tasks.json"
            if tasks_file.exists():
                with open(tasks_file, 'r') as f:
                    tasks_data = json.load(f)
                    for task_data in tasks_data:
                        task = self._deserialize_task(task_data)
                        self.tasks[task.task_id] = task
            
            # Load projects
            projects_file = data_dir / "projects.json"
            if projects_file.exists():
                with open(projects_file, 'r') as f:
                    projects_data = json.load(f)
                    for project_data in projects_data:
                        project = self._deserialize_project(project_data)
                        self.projects[project.project_id] = project
            
            self.logger.info(f"Loaded {len(self.contacts)} contacts, {len(self.deals)} deals, {len(self.tasks)} tasks, {len(self.projects)} projects")
            
        except Exception as e:
            self.logger.error(f"Error loading CRM data: {e}")

    def _save_data(self):
        """Save CRM data to storage."""
        try:
            data_dir = Path("business/crm_data")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Save contacts
            contacts_file = data_dir / "contacts.json"
            contacts_data = [self._serialize_contact(contact) for contact in self.contacts.values()]
            with open(contacts_file, 'w') as f:
                json.dump(contacts_data, f, indent=2, default=str)
            
            # Save deals
            deals_file = data_dir / "deals.json"
            deals_data = [self._serialize_deal(deal) for deal in self.deals.values()]
            with open(deals_file, 'w') as f:
                json.dump(deals_data, f, indent=2, default=str)
            
            # Save tasks
            tasks_file = data_dir / "tasks.json"
            tasks_data = [self._serialize_task(task) for task in self.tasks.values()]
            with open(tasks_file, 'w') as f:
                json.dump(tasks_data, f, indent=2, default=str)
            
            # Save projects
            projects_file = data_dir / "projects.json"
            projects_data = [self._serialize_project(project) for project in self.projects.values()]
            with open(projects_file, 'w') as f:
                json.dump(projects_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Error saving CRM data: {e}")

    def _serialize_contact(self, contact: Contact) -> Dict[str, Any]:
        """Serialize contact for storage."""
        return {
            "contact_id": contact.contact_id,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "company": contact.company,
            "status": contact.status.value,
            "source": contact.source,
            "created_at": contact.created_at.isoformat(),
            "updated_at": contact.updated_at.isoformat(),
            "custom_fields": contact.custom_fields
        }

    def _deserialize_contact(self, data: Dict[str, Any]) -> Contact:
        """Deserialize contact from storage."""
        return Contact(
            contact_id=data["contact_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data.get("phone"),
            company=data.get("company"),
            status=ContactStatus(data["status"]),
            source=data["source"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            custom_fields=data.get("custom_fields", {})
        )

    def _serialize_deal(self, deal: Deal) -> Dict[str, Any]:
        """Serialize deal for storage."""
        return {
            "deal_id": deal.deal_id,
            "title": deal.title,
            "value": deal.value,
            "currency": deal.currency,
            "stage": deal.stage.value,
            "contact_id": deal.contact_id,
            "owner": deal.owner,
            "created_at": deal.created_at.isoformat(),
            "updated_at": deal.updated_at.isoformat(),
            "expected_close_date": deal.expected_close_date.isoformat() if deal.expected_close_date else None,
            "probability": deal.probability,
            "custom_fields": deal.custom_fields
        }

    def _deserialize_deal(self, data: Dict[str, Any]) -> Deal:
        """Deserialize deal from storage."""
        return Deal(
            deal_id=data["deal_id"],
            title=data["title"],
            value=data["value"],
            currency=data["currency"],
            stage=DealStage(data["stage"]),
            contact_id=data["contact_id"],
            owner=data["owner"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            expected_close_date=datetime.fromisoformat(data["expected_close_date"]) if data.get("expected_close_date") else None,
            probability=data["probability"],
            custom_fields=data.get("custom_fields", {})
        )

    def _serialize_task(self, task: Task) -> Dict[str, Any]:
        """Serialize task for storage."""
        return {
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority.value,
            "assigned_to": task.assigned_to,
            "contact_id": task.contact_id,
            "deal_id": task.deal_id,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }

    def _deserialize_task(self, data: Dict[str, Any]) -> Task:
        """Deserialize task from storage."""
        return Task(
            task_id=data["task_id"],
            title=data["title"],
            description=data["description"],
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            priority=TaskPriority(data["priority"]),
            assigned_to=data["assigned_to"],
            contact_id=data.get("contact_id"),
            deal_id=data.get("deal_id"),
            status=data["status"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

    def _serialize_project(self, project: Project) -> Dict[str, Any]:
        """Serialize project for storage."""
        return {
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "owner": project.owner,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "end_date": project.end_date.isoformat() if project.end_date else None,
            "budget": project.budget,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        }

    def _deserialize_project(self, data: Dict[str, Any]) -> Project:
        """Deserialize project from storage."""
        return Project(
            project_id=data["project_id"],
            name=data["name"],
            description=data["description"],
            status=data["status"],
            owner=data["owner"],
            start_date=datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            end_date=datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None,
            budget=data.get("budget"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

    # Contact Management
    def create_contact(self, first_name: str, last_name: str, email: str,
                      phone: Optional[str] = None, company: Optional[str] = None,
                      source: str = "manual", custom_fields: Dict[str, Any] = None) -> Contact:
        """Create a new contact."""
        try:
            contact_id = f"contact_{uuid.uuid4().hex[:8]}"
            contact = Contact(
                contact_id=contact_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company,
                status=ContactStatus.LEAD,
                source=source,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                custom_fields=custom_fields or {}
            )
            
            self.contacts[contact_id] = contact
            self._save_data()
            
            self.logger.info(f"Created contact: {first_name} {last_name} ({contact_id})")
            return contact
            
        except Exception as e:
            self.logger.error(f"Error creating contact: {e}")
            return None

    def update_contact(self, contact_id: str, **kwargs) -> bool:
        """Update a contact."""
        try:
            contact = self.contacts.get(contact_id)
            if not contact:
                self.logger.error(f"Contact not found: {contact_id}")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)
            
            contact.updated_at = datetime.now()
            self._save_data()
            
            self.logger.info(f"Updated contact: {contact_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating contact: {e}")
            return False

    def get_contact(self, contact_id: str) -> Optional[Contact]:
        """Get a contact by ID."""
        return self.contacts.get(contact_id)

    def search_contacts(self, query: str) -> List[Contact]:
        """Search contacts by name, email, or company."""
        results = []
        query_lower = query.lower()
        
        for contact in self.contacts.values():
            if (query_lower in contact.first_name.lower() or
                query_lower in contact.last_name.lower() or
                query_lower in contact.email.lower() or
                (contact.company and query_lower in contact.company.lower())):
                results.append(contact)
        
        return results

    # Deal Management
    def create_deal(self, title: str, value: float, currency: str, stage: DealStage,
                   contact_id: str, owner: str, expected_close_date: Optional[datetime] = None,
                   probability: float = 0.0, custom_fields: Dict[str, Any] = None) -> Deal:
        """Create a new deal."""
        try:
            deal_id = f"deal_{uuid.uuid4().hex[:8]}"
            deal = Deal(
                deal_id=deal_id,
                title=title,
                value=value,
                currency=currency,
                stage=stage,
                contact_id=contact_id,
                owner=owner,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                expected_close_date=expected_close_date,
                probability=probability,
                custom_fields=custom_fields or {}
            )
            
            self.deals[deal_id] = deal
            self._save_data()
            
            self.logger.info(f"Created deal: {title} ({deal_id})")
            return deal
            
        except Exception as e:
            self.logger.error(f"Error creating deal: {e}")
            return None

    def update_deal(self, deal_id: str, **kwargs) -> bool:
        """Update a deal."""
        try:
            deal = self.deals.get(deal_id)
            if not deal:
                self.logger.error(f"Deal not found: {deal_id}")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(deal, key):
                    setattr(deal, key, value)
            
            deal.updated_at = datetime.now()
            self._save_data()
            
            self.logger.info(f"Updated deal: {deal_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating deal: {e}")
            return False

    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Get a deal by ID."""
        return self.deals.get(deal_id)

    def get_deals_by_contact(self, contact_id: str) -> List[Deal]:
        """Get all deals for a contact."""
        return [deal for deal in self.deals.values() if deal.contact_id == contact_id]

    def get_deals_by_stage(self, stage: DealStage) -> List[Deal]:
        """Get all deals in a specific stage."""
        return [deal for deal in self.deals.values() if deal.stage == stage]

    # Task Management
    def create_task(self, title: str, description: str, assigned_to: str,
                   due_date: Optional[datetime] = None, priority: TaskPriority = TaskPriority.MEDIUM,
                   contact_id: Optional[str] = None, deal_id: Optional[str] = None) -> Task:
        """Create a new task."""
        try:
            task_id = f"task_{uuid.uuid4().hex[:8]}"
            task = Task(
                task_id=task_id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                assigned_to=assigned_to,
                contact_id=contact_id,
                deal_id=deal_id,
                status="pending",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.tasks[task_id] = task
            self._save_data()
            
            self.logger.info(f"Created task: {title} ({task_id})")
            return task
            
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
            return None

    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update a task."""
        try:
            task = self.tasks.get(task_id)
            if not task:
                self.logger.error(f"Task not found: {task_id}")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            task.updated_at = datetime.now()
            self._save_data()
            
            self.logger.info(f"Updated task: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating task: {e}")
            return False

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def get_tasks_by_assignee(self, assigned_to: str) -> List[Task]:
        """Get all tasks assigned to a user."""
        return [task for task in self.tasks.values() if task.assigned_to == assigned_to]

    def get_tasks_by_contact(self, contact_id: str) -> List[Task]:
        """Get all tasks related to a contact."""
        return [task for task in self.tasks.values() if task.contact_id == contact_id]

    # Project Management
    def create_project(self, name: str, description: str, owner: str,
                      start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                      budget: Optional[float] = None) -> Project:
        """Create a new project."""
        try:
            project_id = f"project_{uuid.uuid4().hex[:8]}"
            project = Project(
                project_id=project_id,
                name=name,
                description=description,
                status="active",
                owner=owner,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.projects[project_id] = project
            self._save_data()
            
            self.logger.info(f"Created project: {name} ({project_id})")
            return project
            
        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
            return None

    def update_project(self, project_id: str, **kwargs) -> bool:
        """Update a project."""
        try:
            project = self.projects.get(project_id)
            if not project:
                self.logger.error(f"Project not found: {project_id}")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            project.updated_at = datetime.now()
            self._save_data()
            
            self.logger.info(f"Updated project: {project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating project: {e}")
            return False

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        return self.projects.get(project_id)

    def get_projects_by_owner(self, owner: str) -> List[Project]:
        """Get all projects owned by a user."""
        return [project for project in self.projects.values() if project.owner == owner]

    # Analytics and Reporting
    def get_crm_analytics(self) -> Dict[str, Any]:
        """Get CRM analytics and metrics."""
        total_contacts = len(self.contacts)
        total_deals = len(self.deals)
        total_tasks = len(self.tasks)
        total_projects = len(self.projects)
        
        # Calculate deal pipeline value
        pipeline_value = sum(deal.value for deal in self.deals.values() 
                           if deal.stage not in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST])
        
        # Calculate won deals value
        won_value = sum(deal.value for deal in self.deals.values() 
                       if deal.stage == DealStage.CLOSED_WON)
        
        # Calculate conversion rate
        total_closed = len([deal for deal in self.deals.values() 
                          if deal.stage in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]])
        won_deals = len([deal for deal in self.deals.values() 
                        if deal.stage == DealStage.CLOSED_WON])
        conversion_rate = (won_deals / total_closed * 100) if total_closed > 0 else 0
        
        # Task completion rate
        completed_tasks = len([task for task in self.tasks.values() if task.status == "completed"])
        task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_contacts": total_contacts,
            "total_deals": total_deals,
            "total_tasks": total_tasks,
            "total_projects": total_projects,
            "pipeline_value": pipeline_value,
            "won_value": won_value,
            "conversion_rate": conversion_rate,
            "task_completion_rate": task_completion_rate,
            "deals_by_stage": {
                stage.value: len([deal for deal in self.deals.values() if deal.stage == stage])
                for stage in DealStage
            },
            "contacts_by_status": {
                status.value: len([contact for contact in self.contacts.values() if contact.status == status])
                for status in ContactStatus
            }
        }

    def generate_ai_insights(self, data_type: str = "overview") -> str:
        """Generate AI-powered insights from CRM data."""
        try:
            analytics = self.get_crm_analytics()
            
            if data_type == "overview":
                prompt = f"""
                Analyze the following CRM data and provide insights:
                - Total Contacts: {analytics['total_contacts']}
                - Total Deals: {analytics['total_deals']}
                - Pipeline Value: ${analytics['pipeline_value']:,.2f}
                - Won Value: ${analytics['won_value']:,.2f}
                - Conversion Rate: {analytics['conversion_rate']:.1f}%
                - Task Completion Rate: {analytics['task_completion_rate']:.1f}%
                
                Provide actionable insights and recommendations for improving sales performance.
                """
            elif data_type == "sales":
                prompt = f"""
                Analyze the sales pipeline:
                - Pipeline Value: ${analytics['pipeline_value']:,.2f}
                - Won Value: ${analytics['won_value']:,.2f}
                - Conversion Rate: {analytics['conversion_rate']:.1f}%
                - Deals by Stage: {analytics['deals_by_stage']}
                
                Provide sales strategy recommendations and identify opportunities.
                """
            else:
                prompt = f"""
                Analyze the CRM data: {analytics}
                Provide insights and recommendations.
                """
            
            insights = self.ai_engine.get_ai_response(prompt)
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating AI insights: {e}")
            return f"Error generating insights: {str(e)}"
