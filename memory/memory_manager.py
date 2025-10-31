"""
JARVIS AI - Memory Manager
Handles memory storage, retrieval, and learning.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.config import Config

class MemoryManager:
    """
    Memory manager for storing and retrieving user interactions and preferences.
    Uses SQLite for local storage.
    """
    
    def __init__(self, db_path: str = "jarvis_memory.db"):
        """Initialize the memory manager."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.connection = None
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database."""
        try:
            # Create database directory if it doesn't exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            self._create_tables()
            
            self.logger.info(f"Memory database initialized: {self.db_path}")
        
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables."""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Commands table
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
        
        # Memory table
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
        
        # Patterns table
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
        
        # Conversations table
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
        
        # Content sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                topic TEXT,
                project_path TEXT,
                start_time REAL,
                end_time REAL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Content plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content_type TEXT,
                title TEXT,
                description TEXT,
                tags TEXT,
                plan_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Content series table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                series_name TEXT NOT NULL,
                playlist_id TEXT,
                topics TEXT,
                total_videos INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
        self.logger.info("Database tables created successfully")
    
    def store_input(self, user_input: str, user_id: int = 1):
        """
        Store user input in memory.
        
        Args:
            user_input: User input text
            user_id: User ID (default: 1)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO commands (user_id, command_text, created_at)
                VALUES (?, ?, ?)
            """, (user_id, user_input, datetime.now()))
            
            self.connection.commit()
            self.logger.debug(f"Stored user input: {user_input[:50]}...")
        
        except Exception as e:
            self.logger.error(f"Error storing input: {e}")
    
    def store_response(self, response: str, user_id: int = 1):
        """
        Store AI response in memory.
        
        Args:
            response: AI response text
            user_id: User ID (default: 1)
        """
        try:
            cursor = self.connection.cursor()
            
            # Get the last command for this user
            cursor.execute("""
                SELECT id FROM commands 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (user_id,))
            
            command_row = cursor.fetchone()
            if command_row:
                command_id = command_row['id']
                
                # Update the command with response
                cursor.execute("""
                    UPDATE commands 
                    SET ai_response = ?, success = ?
                    WHERE id = ?
                """, (response, True, command_id))
            
            self.connection.commit()
            self.logger.debug(f"Stored AI response: {response[:50]}...")
        
        except Exception as e:
            self.logger.error(f"Error storing response: {e}")
    
    def store_conversation(self, user_input: str, ai_response: str, 
                          context: Dict = None, user_id: int = 1):
        """
        Store a complete conversation exchange.
        
        Args:
            user_input: User input text
            ai_response: AI response text
            context: Additional context information
            user_id: User ID (default: 1)
        """
        try:
            cursor = self.connection.cursor()
            context_json = json.dumps(context) if context else None
            
            cursor.execute("""
                INSERT INTO conversations (user_id, user_input, ai_response, context, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, user_input, ai_response, context_json, datetime.now()))
            
            self.connection.commit()
            self.logger.debug("Stored conversation exchange")
        
        except Exception as e:
            self.logger.error(f"Error storing conversation: {e}")
    
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
        """
        Get conversation context for AI processing.
        
        Args:
            user_id: User ID (default: 1)
            limit: Number of recent conversations to include
            
        Returns:
            Context dictionary
        """
        try:
            cursor = self.connection.cursor()
            
            # Get recent conversations
            cursor.execute("""
                SELECT user_input, ai_response, created_at
                FROM conversations 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'user': row['user_input'],
                    'assistant': row['ai_response'],
                    'timestamp': row['created_at']
                })
            
            # Get user preferences
            preferences = self.get_user_preferences(user_id)
            
            # Get recent patterns
            patterns = self.get_recent_patterns(user_id, limit=3)
            
            return {
                'conversations': conversations,
                'preferences': preferences,
                'patterns': patterns,
                'user_id': user_id
            }
        
        except Exception as e:
            self.logger.error(f"Error getting context: {e}")
            return {}
    
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
        """Save any pending changes to the database."""
        try:
            if self.connection:
                self.connection.commit()
                self.logger.debug("Memory changes saved")
        except Exception as e:
            self.logger.error(f"Error saving memory: {e}")
    
    def store_content_session(self, session_info: Dict):
        """Store content creation session information."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO content_sessions (session_name, topic, project_path, start_time, end_time, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_info.get('name', ''),
                session_info.get('topic', ''),
                session_info.get('project_path', ''),
                session_info.get('start_time', 0),
                session_info.get('end_time', 0),
                session_info.get('status', 'active')
            ))
            self.connection.commit()
            self.logger.info(f"Stored content session: {session_info.get('name', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Error storing content session: {e}")
    
    def store_content_plan(self, content_info: Dict):
        """Store content creation plan."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO content_plans (topic, content_type, title, description, tags, plan_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                content_info.get('topic', ''),
                content_info.get('type', ''),
                content_info.get('title', ''),
                content_info.get('description', ''),
                json.dumps(content_info.get('tags', [])),
                json.dumps(content_info.get('plan', {}))
            ))
            self.connection.commit()
            self.logger.info(f"Stored content plan: {content_info.get('topic', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Error storing content plan: {e}")
    
    def store_content_series(self, series_info: Dict):
        """Store content series information."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO content_series (series_name, playlist_id, topics, total_videos)
                VALUES (?, ?, ?, ?)
            """, (
                series_info.get('name', ''),
                series_info.get('playlist_id', ''),
                json.dumps(series_info.get('topics', [])),
                series_info.get('total_videos', 0)
            ))
            self.connection.commit()
            self.logger.info(f"Stored content series: {series_info.get('name', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Error storing content series: {e}")
    
    def get_content_sessions(self) -> List[Dict]:
        """Get all content creation sessions."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM content_sessions ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting content sessions: {e}")
            return []
    
    def close(self):
        """Close the database connection."""
        try:
            if self.connection:
                self.connection.close()
                self.logger.info("Memory database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database: {e}")
    
    def __del__(self):
        """Destructor to ensure database connection is closed."""
        self.close()

Handles memory storage, retrieval, and learning.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.config import Config

class MemoryManager:
    """
    Memory manager for storing and retrieving user interactions and preferences.
    Uses SQLite for local storage.
    """
    
    def __init__(self, db_path: str = "jarvis_memory.db"):
        """Initialize the memory manager."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.connection = None
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database."""
        try:
            # Create database directory if it doesn't exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            self._create_tables()
            
            self.logger.info(f"Memory database initialized: {self.db_path}")
        
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables."""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Commands table
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
        
        # Memory table
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
        
        # Patterns table
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
        
        # Conversations table
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
        
        # Content sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                topic TEXT,
                project_path TEXT,
                start_time REAL,
                end_time REAL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Content plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content_type TEXT,
                title TEXT,
                description TEXT,
                tags TEXT,
                plan_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Content series table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                series_name TEXT NOT NULL,
                playlist_id TEXT,
                topics TEXT,
                total_videos INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
        self.logger.info("Database tables created successfully")
    
    def store_input(self, user_input: str, user_id: int = 1):
        """
        Store user input in memory.
        
        Args:
            user_input: User input text
            user_id: User ID (default: 1)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO commands (user_id, command_text, created_at)
                VALUES (?, ?, ?)
            """, (user_id, user_input, datetime.now()))
            
            self.connection.commit()
            self.logger.debug(f"Stored user input: {user_input[:50]}...")
        
        except Exception as e:
            self.logger.error(f"Error storing input: {e}")
    
    def store_response(self, response: str, user_id: int = 1):
        """
        Store AI response in memory.
        
        Args:
            response: AI response text
            user_id: User ID (default: 1)
        """
        try:
            cursor = self.connection.cursor()
            
            # Get the last command for this user
            cursor.execute("""
                SELECT id FROM commands 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (user_id,))
            
            command_row = cursor.fetchone()
            if command_row:
                command_id = command_row['id']
                
                # Update the command with response
                cursor.execute("""
                    UPDATE commands 
                    SET ai_response = ?, success = ?
                    WHERE id = ?
                """, (response, True, command_id))
            
            self.connection.commit()
            self.logger.debug(f"Stored AI response: {response[:50]}...")
        
        except Exception as e:
            self.logger.error(f"Error storing response: {e}")
    
    def store_conversation(self, user_input: str, ai_response: str, 
                          context: Dict = None, user_id: int = 1):
        """
        Store a complete conversation exchange.
        
        Args:
            user_input: User input text
            ai_response: AI response text
            context: Additional context information
            user_id: User ID (default: 1)
        """
        try:
            cursor = self.connection.cursor()
            context_json = json.dumps(context) if context else None
            
            cursor.execute("""
                INSERT INTO conversations (user_id, user_input, ai_response, context, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, user_input, ai_response, context_json, datetime.now()))
            
            self.connection.commit()
            self.logger.debug("Stored conversation exchange")
        
        except Exception as e:
            self.logger.error(f"Error storing conversation: {e}")
    
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
        """
        Get conversation context for AI processing.
        
        Args:
            user_id: User ID (default: 1)
            limit: Number of recent conversations to include
            
        Returns:
            Context dictionary
        """
        try:
            cursor = self.connection.cursor()
            
            # Get recent conversations
            cursor.execute("""
                SELECT user_input, ai_response, created_at
                FROM conversations 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'user': row['user_input'],
                    'assistant': row['ai_response'],
                    'timestamp': row['created_at']
                })
            
            # Get user preferences
            preferences = self.get_user_preferences(user_id)
            
            # Get recent patterns
            patterns = self.get_recent_patterns(user_id, limit=3)
            
            return {
                'conversations': conversations,
                'preferences': preferences,
                'patterns': patterns,
                'user_id': user_id
            }
        
        except Exception as e:
            self.logger.error(f"Error getting context: {e}")
            return {}
    
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
        """Save any pending changes to the database."""
        try:
            if self.connection:
                self.connection.commit()
                self.logger.debug("Memory changes saved")
        except Exception as e:
            self.logger.error(f"Error saving memory: {e}")
    
    def store_content_session(self, session_info: Dict):
        """Store content creation session information."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO content_sessions (session_name, topic, project_path, start_time, end_time, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_info.get('name', ''),
                session_info.get('topic', ''),
                session_info.get('project_path', ''),
                session_info.get('start_time', 0),
                session_info.get('end_time', 0),
                session_info.get('status', 'active')
            ))
            self.connection.commit()
            self.logger.info(f"Stored content session: {session_info.get('name', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Error storing content session: {e}")
    
    def store_content_plan(self, content_info: Dict):
        """Store content creation plan."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO content_plans (topic, content_type, title, description, tags, plan_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                content_info.get('topic', ''),
                content_info.get('type', ''),
                content_info.get('title', ''),
                content_info.get('description', ''),
                json.dumps(content_info.get('tags', [])),
                json.dumps(content_info.get('plan', {}))
            ))
            self.connection.commit()
            self.logger.info(f"Stored content plan: {content_info.get('topic', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Error storing content plan: {e}")
    
    def store_content_series(self, series_info: Dict):
        """Store content series information."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO content_series (series_name, playlist_id, topics, total_videos)
                VALUES (?, ?, ?, ?)
            """, (
                series_info.get('name', ''),
                series_info.get('playlist_id', ''),
                json.dumps(series_info.get('topics', [])),
                series_info.get('total_videos', 0)
            ))
            self.connection.commit()
            self.logger.info(f"Stored content series: {series_info.get('name', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Error storing content series: {e}")
    
    def get_content_sessions(self) -> List[Dict]:
        """Get all content creation sessions."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM content_sessions ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting content sessions: {e}")
            return []
    
    def close(self):
        """Close the database connection."""
        try:
            if self.connection:
                self.connection.close()
                self.logger.info("Memory database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database: {e}")
    
    def __del__(self):
        """Destructor to ensure database connection is closed."""
        self.close()





