"""
Business Mode - Email Templates
Pre-written email templates with dynamic field insertion.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class EmailTemplates:
    """Manage email templates"""
    
    TEMPLATES = {
        'client_proposal': {'subject': 'Project Proposal: {project_name}', 'body': 'Dear {client_name},\n\nPlease find attached our proposal for {project_name}.\n\nBudget: ${budget}\nTimeline: {timeline}\n\nBest regards,\n{your_name}'},
        'invoice_sent': {'subject': 'Invoice {invoice_id} - {project_name}', 'body': 'Dear {client_name},\n\nYour invoice {invoice_id} for {project_name} is attached.\n\nAmount Due: ${amount}\nDue Date: {due_date}\n\nThank you!'},
        'follow_up': {'subject': 'Follow-up: {subject}', 'body': 'Hi {client_name},\n\nI wanted to follow up on {subject}.\n\nPlease let me know if you have any questions.\n\nBest regards,\n{your_name}'},
        'meeting_reminder': {'subject': 'Meeting Reminder: {meeting_title}', 'body': 'Hi {attendee_name},\n\nThis is a reminder about our meeting:\n\nTitle: {meeting_title}\nDate: {meeting_date}\nTime: {meeting_time}\nLocation: {location}\n\nLook forward to seeing you!'},
        'thank_you': {'subject': 'Thank You - {project_name}', 'body': 'Dear {client_name},\n\nThank you for choosing us for {project_name}.\n\nWe appreciate your business and look forward to working with you.\n\nBest regards,\n{your_name}'},
        'status_update': {'subject': 'Status Update: {project_name}', 'body': 'Hi {client_name},\n\nHere\'s the latest status on {project_name}:\n\nProgress: {progress}%\nNext Steps: {next_steps}\nETA: {eta}\n\nBest regards,\n{your_name}'}
    }
    
    def __init__(self, db_path: str = './email_templates.json'):
        self.db_path = Path(db_path)
        self.custom_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_templates(self):
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.custom_templates, f, indent=2)
        except Exception:
            pass
    
    def get_template(self, template_name: str) -> Optional[Dict]:
        if template_name in self.TEMPLATES:
            return self.TEMPLATES[template_name].copy()
        return self.custom_templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        return list(self.TEMPLATES.keys()) + list(self.custom_templates.keys())
    
    def create_email(self, template_name: str, fields: Dict) -> Optional[Dict]:
        try:
            template = self.get_template(template_name)
            if not template:
                return None
            subject = template['subject']
            body = template['body']
            for key, value in fields.items():
                placeholder = f"{{{key}}}"
                subject = subject.replace(placeholder, str(value))
                body = body.replace(placeholder, str(value))
            return {'subject': subject, 'body': body, 'template': template_name, 'created_at': datetime.now().isoformat()}
        except Exception:
            return None
    
    def add_custom_template(self, name: str, subject: str, body: str) -> bool:
        try:
            self.custom_templates[name] = {'subject': subject, 'body': body}
            self._save_templates()
            return True
        except Exception:
            return False
    
    def get_template_variables(self, template_name: str) -> List[str]:
        template = self.get_template(template_name)
        if not template:
            return []
        import re
        text = template['subject'] + ' ' + template['body']
        variables = re.findall(r'\{(\w+)\}', text)
        return list(set(variables))
