"""
Command History
Track and replay CLI command history
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from cli.utils import get_project_root

logger = logging.getLogger(__name__)


class CommandHistory:
    """Manage CLI command history"""
    
    def __init__(self, history_file: Optional[Path] = None, max_history: int = 1000):
        """
        Initialize command history
        
        Args:
            history_file: Path to history file
            max_history: Maximum number of commands to store
        """
        if history_file is None:
            history_file = get_project_root() / "data" / "cli_history.json"
        
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.max_history = max_history
        self.history: List[Dict] = []
        self._load_history()
    
    def _load_history(self):
        """Load command history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load command history: {e}")
    
    def _save_history(self):
        """Save command history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save command history: {e}")
    
    def add(self, command: str, args: Optional[Dict] = None, result: Optional[str] = None):
        """
        Add command to history
        
        Args:
            command: Command string
            args: Command arguments
            result: Command result (optional)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "args": args or {},
            "result": result
        }
        
        self.history.append(entry)
        
        # Trim history if too long
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        self._save_history()
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search command history
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching commands
        """
        query_lower = query.lower()
        matches = [
            entry for entry in self.history
            if query_lower in entry['command'].lower()
        ]
        return matches[-limit:]
    
    def get_recent(self, limit: int = 10) -> List[Dict]:
        """
        Get recent commands
        
        Args:
            limit: Number of recent commands
            
        Returns:
            List of recent commands
        """
        return self.history[-limit:]
    
    def clear(self):
        """Clear command history"""
        self.history = []
        self._save_history()


# Global history instance
_history_instance: Optional[CommandHistory] = None


def get_history() -> CommandHistory:
    """Get global command history instance"""
    global _history_instance
    if _history_instance is None:
        _history_instance = CommandHistory()
    return _history_instance

