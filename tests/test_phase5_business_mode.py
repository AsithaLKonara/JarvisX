"""
Phase 5: Business Mode - Comprehensive Test Suite
Tests for all business mode components.
"""

import unittest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from business_mode.finance_tracker import FinanceTracker
from business_mode.invoice_generator import InvoiceGenerator
from business_mode.email_templates import EmailTemplates
from business_mode.task_scheduler import TaskScheduler
from business_mode.client_database import ClientDatabase
from business_mode.business_handler import BusinessModeHandler


class TestFinanceTracker(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.tracker = FinanceTracker(db_path=self.temp_db.name)
    
    def tearDown(self):
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    def test_add_income(self):
        result = self.tracker.add_income(1000.0, "Client A")
        self.assertTrue(result)
    
    def test_add_expense(self):
        result = self.tracker.add_expense(50.0, "supplies")
        self.assertTrue(result)
    
    def test_get_balance(self):
        self.tracker.add_income(1000.0)
        self.tracker.add_expense(200.0, "supplies")
        balance = self.tracker.get_balance()
        self.assertEqual(balance, 800.0)


class TestInvoiceGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.generator = InvoiceGenerator(output_dir=self.temp_dir)
    
    def test_create_invoice(self):
        items = [{'description': 'Service A', 'amount': 500.0}]
        invoice_id = self.generator.create_invoice('Client A', items)
        self.assertIsNotNone(invoice_id)
    
    def test_get_invoice_total(self):
        items = [{'description': 'Service', 'amount': 100.0}]
        invoice_id = self.generator.create_invoice('Client A', items)
        total = self.generator.get_invoice_total(invoice_id)
        self.assertEqual(total, 100.0)


class TestEmailTemplates(unittest.TestCase):
    def setUp(self):
        self.templates = EmailTemplates()
    
    def test_get_template(self):
        template = self.templates.get_template('client_proposal')
        self.assertIsNotNone(template)
    
    def test_create_email(self):
        email = self.templates.create_email('thank_you', {'client_name': 'John', 'project_name': 'Web Design', 'your_name': 'Jane'})
        self.assertIsNotNone(email)


class TestTaskScheduler(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.scheduler = TaskScheduler(db_path=self.temp_db.name)
    
    def tearDown(self):
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    def test_create_task(self):
        result = self.scheduler.create_task('Task 1', datetime.now().strftime('%Y-%m-%d'))
        self.assertTrue(result)
    
    def test_get_tasks(self):
        self.scheduler.create_task('Task 1', datetime.now().strftime('%Y-%m-%d'))
        tasks = self.scheduler.get_tasks()
        self.assertGreater(len(tasks), 0)


class TestClientDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db = ClientDatabase(db_path=self.temp_db.name)
    
    def tearDown(self):
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    def test_add_client(self):
        client_id = self.db.add_client('John Doe', 'john@example.com')
        self.assertIsNotNone(client_id)
    
    def test_search_clients(self):
        self.db.add_client('John Doe', 'john@example.com')
        results = self.db.search_clients('John')
        self.assertGreater(len(results), 0)


class TestBusinessHandler(unittest.TestCase):
    def setUp(self):
        self.handler = BusinessModeHandler()
    
    def test_add_income(self):
        result = self.handler.add_income(1000.0, 'Test project')
        self.assertTrue(result)
    
    def test_create_invoice(self):
        invoice_id = self.handler.create_invoice('Client A', [{'description': 'Service', 'amount': 500}])
        self.assertIsNotNone(invoice_id)
    
    def test_add_client(self):
        client_id = self.handler.add_client('John Doe', 'john@example.com')
        self.assertIsNotNone(client_id)


if __name__ == '__main__':
    unittest.main()
