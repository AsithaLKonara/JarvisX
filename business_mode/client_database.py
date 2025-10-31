"""
Business Mode - Client Database
Client relationship management (CRM), contact management.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ClientDatabase:
    """Manage client relationships"""
    
    def __init__(self, db_path: str = './clients.db'):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                company TEXT,
                industry TEXT,
                status TEXT,
                budget_range TEXT,
                created_at TEXT,
                updated_at TEXT
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                interaction_type TEXT,
                notes TEXT,
                date TEXT,
                outcome TEXT
            )''')
            conn.commit()
            conn.close()
        except Exception:
            pass
    
    def add_client(self, name: str, email: str = '', phone: str = '', company: str = '', industry: str = '', 
                  budget_range: str = '', status: str = 'prospect') -> Optional[int]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute('''INSERT INTO clients (name, email, phone, company, industry, budget_range, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (name, email, phone, company, industry, budget_range, status, now, now))
            conn.commit()
            client_id = cursor.lastrowid
            conn.close()
            return client_id
        except Exception:
            return None
    
    def get_client(self, client_id: int) -> Optional[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT id, name, email, phone, company, industry, status, budget_range, created_at FROM clients WHERE id = ?''', (client_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {'id': row[0], 'name': row[1], 'email': row[2], 'phone': row[3], 'company': row[4], 'industry': row[5], 'status': row[6], 'budget_range': row[7], 'created_at': row[8]}
            return None
        except Exception:
            return None
    
    def search_clients(self, query: str = '', status: Optional[str] = None) -> List[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            sql = "SELECT id, name, email, company, status FROM clients WHERE 1=1"
            params = []
            if query:
                sql += " AND (name LIKE ? OR email LIKE ? OR company LIKE ?)"
                search_term = f"%{query}%"
                params = [search_term, search_term, search_term]
            if status:
                sql += " AND status = ?"
                params.append(status)
            cursor.execute(sql, params)
            clients = [{'id': r[0], 'name': r[1], 'email': r[2], 'company': r[3], 'status': r[4]} for r in cursor.fetchall()]
            conn.close()
            return clients
        except Exception:
            return []
    
    def update_client(self, client_id: int, **kwargs) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            allowed_fields = ['name', 'email', 'phone', 'company', 'industry', 'budget_range', 'status']
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            if not updates:
                return False
            updates['updated_at'] = datetime.now().isoformat()
            query = "UPDATE clients SET " + ", ".join(f"{k} = ?" for k in updates.keys())
            query += " WHERE id = ?"
            cursor.execute(query, list(updates.values()) + [client_id])
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def add_interaction(self, client_id: int, interaction_type: str, notes: str = '', outcome: str = '') -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO interactions (client_id, interaction_type, notes, date, outcome)
                VALUES (?, ?, ?, ?, ?)''',
                (client_id, interaction_type, notes, datetime.now().isoformat(), outcome))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_client_interactions(self, client_id: int) -> List[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT id, interaction_type, notes, date, outcome FROM interactions WHERE client_id = ? ORDER BY date DESC''', (client_id,))
            interactions = [{'id': r[0], 'type': r[1], 'notes': r[2], 'date': r[3], 'outcome': r[4]} for r in cursor.fetchall()]
            conn.close()
            return interactions
        except Exception:
            return []
    
    def get_client_stats(self) -> Dict:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM clients WHERE status = 'prospect'")
            prospects = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM clients WHERE status = 'active'")
            active = cursor.fetchone()[0]
            conn.close()
            return {'total': total, 'prospects': prospects, 'active': active}
        except Exception:
            return {'total': 0, 'prospects': 0, 'active': 0}
    
    def export_clients(self, output_file: str = 'clients.json') -> bool:
        try:
            clients = self.search_clients()
            with open(output_file, 'w') as f:
                json.dump(clients, f, indent=2)
            return True
        except Exception:
            return False
