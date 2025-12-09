"""
Usage Analytics System
Track command usage, performance metrics, and user analytics
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from cli.utils import get_project_root

logger = logging.getLogger(__name__)


class UsageAnalytics:
    """Track and analyze CLI usage"""
    
    def __init__(self, analytics_file: Optional[Path] = None):
        """
        Initialize usage analytics
        
        Args:
            analytics_file: Path to analytics storage file
        """
        if analytics_file is None:
            analytics_file = get_project_root() / "data" / "usage_analytics.json"
        
        self.analytics_file = Path(analytics_file)
        self.analytics_file.parent.mkdir(parents=True, exist_ok=True)
        self.analytics: Dict = {
            "commands": [],
            "sessions": [],
            "performance": [],
            "errors": []
        }
        self._load_analytics()
    
    def _load_analytics(self):
        """Load analytics data from file"""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r') as f:
                    self.analytics = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load analytics: {e}")
                self.analytics = {"commands": [], "sessions": [], "performance": [], "errors": []}
    
    def _save_analytics(self):
        """Save analytics data to file"""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.analytics, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save analytics: {e}")
    
    def track_command(self, command: str, args: Optional[Dict] = None, duration: Optional[float] = None, success: bool = True):
        """
        Track a command execution
        
        Args:
            command: Command string
            args: Command arguments
            duration: Execution duration in seconds
            success: Whether command succeeded
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "args": args or {},
            "duration": duration,
            "success": success
        }
        
        self.analytics["commands"].append(entry)
        
        # Keep only last 10,000 commands
        if len(self.analytics["commands"]) > 10000:
            self.analytics["commands"] = self.analytics["commands"][-10000:]
        
        self._save_analytics()
    
    def track_performance(self, operation: str, duration: float, metadata: Optional[Dict] = None):
        """
        Track performance metrics
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            metadata: Additional metadata
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration": duration,
            "metadata": metadata or {}
        }
        
        self.analytics["performance"].append(entry)
        
        # Keep only last 5,000 performance entries
        if len(self.analytics["performance"]) > 5000:
            self.analytics["performance"] = self.analytics["performance"][-5000:]
        
        self._save_analytics()
    
    def track_error(self, error_type: str, error_message: str, command: Optional[str] = None):
        """
        Track errors
        
        Args:
            error_type: Type of error
            error_message: Error message
            command: Command that caused error
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "command": command
        }
        
        self.analytics["errors"].append(entry)
        
        # Keep only last 1,000 errors
        if len(self.analytics["errors"]) > 1000:
            self.analytics["errors"] = self.analytics["errors"][-1000:]
        
        self._save_analytics()
    
    def get_command_stats(self, days: int = 7) -> Dict:
        """
        Get command usage statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Statistics dictionary
        """
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        recent_commands = [
            cmd for cmd in self.analytics["commands"]
            if cmd["timestamp"] >= cutoff_str
        ]
        
        if not recent_commands:
            return {
                "total_commands": 0,
                "unique_commands": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "top_commands": []
            }
        
        # Count commands
        command_counts = defaultdict(int)
        command_durations = defaultdict(list)
        success_count = 0
        
        for cmd in recent_commands:
            command_counts[cmd["command"]] += 1
            if cmd.get("duration"):
                command_durations[cmd["command"]].append(cmd["duration"])
            if cmd.get("success", True):
                success_count += 1
        
        # Calculate averages
        avg_durations = {}
        for cmd, durations in command_durations.items():
            if durations:
                avg_durations[cmd] = sum(durations) / len(durations)
        
        # Top commands
        top_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_commands": len(recent_commands),
            "unique_commands": len(command_counts),
            "success_rate": (success_count / len(recent_commands)) * 100 if recent_commands else 0.0,
            "avg_duration": sum(avg_durations.values()) / len(avg_durations) if avg_durations else 0.0,
            "top_commands": [{"command": cmd, "count": count} for cmd, count in top_commands],
            "command_durations": {cmd: dur for cmd, dur in avg_durations.items()}
        }
    
    def get_performance_stats(self, days: int = 7) -> Dict:
        """
        Get performance statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Performance statistics
        """
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        recent_perf = [
            perf for perf in self.analytics["performance"]
            if perf["timestamp"] >= cutoff_str
        ]
        
        if not recent_perf:
            return {
                "total_operations": 0,
                "avg_duration": 0.0,
                "slowest_operations": []
            }
        
        # Group by operation
        operation_durations = defaultdict(list)
        for perf in recent_perf:
            operation_durations[perf["operation"]].append(perf["duration"])
        
        # Calculate averages
        avg_durations = {
            op: sum(durs) / len(durs)
            for op, durs in operation_durations.items()
        }
        
        # Slowest operations
        slowest = sorted(avg_durations.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_operations": len(recent_perf),
            "avg_duration": sum(avg_durations.values()) / len(avg_durations) if avg_durations else 0.0,
            "slowest_operations": [{"operation": op, "avg_duration": dur} for op, dur in slowest]
        }
    
    def get_error_stats(self, days: int = 7) -> Dict:
        """
        Get error statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Error statistics
        """
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        recent_errors = [
            err for err in self.analytics["errors"]
            if err["timestamp"] >= cutoff_str
        ]
        
        if not recent_errors:
            return {
                "total_errors": 0,
                "error_types": {},
                "most_common_errors": []
            }
        
        # Count error types
        error_type_counts = defaultdict(int)
        for err in recent_errors:
            error_type_counts[err["error_type"]] += 1
        
        # Most common errors
        most_common = sorted(error_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_errors": len(recent_errors),
            "error_types": dict(error_type_counts),
            "most_common_errors": [{"type": err_type, "count": count} for err_type, count in most_common]
        }
    
    def get_summary(self, days: int = 7) -> Dict:
        """
        Get comprehensive analytics summary
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Summary dictionary
        """
        return {
            "period_days": days,
            "command_stats": self.get_command_stats(days),
            "performance_stats": self.get_performance_stats(days),
            "error_stats": self.get_error_stats(days)
        }
    
    def clear_analytics(self):
        """Clear all analytics data"""
        self.analytics = {"commands": [], "sessions": [], "performance": [], "errors": []}
        self._save_analytics()


# Global analytics instance
_analytics_instance: Optional[UsageAnalytics] = None


def get_analytics() -> UsageAnalytics:
    """Get global analytics instance"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = UsageAnalytics()
    return _analytics_instance

