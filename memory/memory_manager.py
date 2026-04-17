"""
Memory manager used by runtime context and long-term memory.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class MemoryManager:
    """SQLite-backed memory manager with short helper methods."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        self._init_database()
    
    def _init_database(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                command_text TEXT NOT NULL,
                intent TEXT,
                success BOOLEAN,
                ai_response TEXT,
                response_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                memory_type TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        self.connection.commit()
    
    def store_conversation(self, user_input: str, ai_response: str, context: Dict = None, user_id: int = 1):
        cursor = self.connection.cursor()
        context_json = json.dumps(context or {})
        cursor.execute(
            """
            INSERT INTO conversations (user_id, user_input, ai_response, context, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, user_input, ai_response, context_json, datetime.now()),
        )
        self.connection.commit()
    
    def store_memory(self, memory_type: str, key: str, value: Any, 
                    confidence: float = 1.0, user_id: int = 1):
        """
        Store a memory item.
        
        Args:
            memory_type: Type of memory (preference, pattern, fact)
            key: Memory key
            value: Memory value
            confidence: Confidence score (0.0 to 1.0)
            user_id: User ID (default: 1)
        """
        try:
            cursor = self.connection.cursor()
            value_json = json.dumps(value) if not isinstance(value, str) else value
            
            # Check if memory already exists
            cursor.execute("""
                SELECT id FROM memory 
                WHERE user_id = ? AND memory_type = ? AND key = ?
            """, (user_id, memory_type, key))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing memory
                cursor.execute("""
                    UPDATE memory 
                    SET value = ?, confidence = ?, updated_at = ?
                    WHERE id = ?
                """, (value_json, confidence, datetime.now(), existing['id']))
            else:
                # Insert new memory
                cursor.execute("""
                    INSERT INTO memory (user_id, memory_type, key, value, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, memory_type, key, value_json, confidence, datetime.now()))
            
            self.connection.commit()
            self.logger.debug(f"Stored memory: {memory_type}/{key}")
        
        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
    
    def get_memory(self, memory_type: str, key: str, user_id: int = 1) -> Optional[Any]:
        """
        Retrieve a memory item.
        
        Args:
            memory_type: Type of memory
            key: Memory key
            user_id: User ID (default: 1)
            
        Returns:
            Memory value or None if not found
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT value FROM memory 
                WHERE user_id = ? AND memory_type = ? AND key = ?
            """, (user_id, memory_type, key))
            
            row = cursor.fetchone()
            if row:
                value = row['value']
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        
        except Exception as e:
            self.logger.error(f"Error retrieving memory: {e}")
            return None
    
    def get_context(self, user_id: int = 1, limit: int = 5) -> Dict:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT user_input, ai_response, created_at
            FROM conversations
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        conversations = [
            {"user": row["user_input"], "assistant": row["ai_response"], "timestamp": row["created_at"]}
            for row in cursor.fetchall()
        ]
        return {
            "conversations": conversations,
            "preferences": self.get_user_preferences(user_id),
            "patterns": self.get_recent_patterns(user_id, limit=3),
            "user_id": user_id,
        }
    
    def get_user_preferences(self, user_id: int = 1) -> Dict:
        """
        Get user preferences.
        
        Args:
            user_id: User ID (default: 1)
            
        Returns:
            User preferences dictionary
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT preferences FROM users WHERE id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row and row['preferences']:
                return json.loads(row['preferences'])
            return {}
        
        except Exception as e:
            self.logger.error(f"Error getting user preferences: {e}")
            return {}
    
    def get_recent_patterns(self, user_id: int = 1, limit: int = 5) -> List[Dict]:
        """
        Get recent user patterns.
        
        Args:
            user_id: User ID (default: 1)
            limit: Number of patterns to retrieve
            
        Returns:
            List of pattern dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT pattern_type, pattern_data, frequency, last_seen
                FROM patterns 
                WHERE user_id = ?
                ORDER BY frequency DESC, last_seen DESC
                LIMIT ?
            """, (user_id, limit))
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    'type': row['pattern_type'],
                    'data': json.loads(row['pattern_data']),
                    'frequency': row['frequency'],
                    'last_seen': row['last_seen']
                })
            
            return patterns
        
        except Exception as e:
            self.logger.error(f"Error getting recent patterns: {e}")
            return []
    
    def save(self):
        if self.connection:
            self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
