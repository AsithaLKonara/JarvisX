"""
Caching Utilities for CLI Commands
Implements response caching to improve performance
"""

import json
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import time


class CLICache:
    """Cache manager for CLI command responses"""
    
    def __init__(self, cache_dir: Optional[Path] = None, ttl: int = 300):
        """
        Initialize cache
        
        Args:
            cache_dir: Cache directory (default: project_root/cache/cli)
            ttl: Time to live in seconds (default: 5 minutes)
        """
        if cache_dir is None:
            from cli.utils import get_project_root
            cache_dir = get_project_root() / "cache" / "cli"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
    
    def _get_cache_key(self, command: str, args: Dict[str, Any]) -> str:
        """Generate cache key from command and arguments"""
        # Create hash from command and args
        cache_data = {
            "command": command,
            "args": sorted(args.items()) if args else {}
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get(self, command: str, args: Dict[str, Any]) -> Optional[Any]:
        """
        Get cached result
        
        Args:
            command: CLI command name
            args: Command arguments
            
        Returns:
            Cached result or None if not found/expired
        """
        cache_key = self._get_cache_key(command, args)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > timedelta(seconds=self.ttl):
                cache_file.unlink()  # Remove expired cache
                return None
            
            return cache_data['result']
        except Exception:
            # If cache is corrupted, remove it
            cache_file.unlink(missing_ok=True)
            return None
    
    def set(self, command: str, args: Dict[str, Any], result: Any):
        """
        Cache result
        
        Args:
            command: CLI command name
            args: Command arguments
            result: Result to cache
        """
        cache_key = self._get_cache_key(command, args)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            cache_data = {
                "command": command,
                "args": args,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, default=str)
        except Exception:
            # Silently fail if caching fails
            pass
    
    def clear(self, command: Optional[str] = None):
        """
        Clear cache
        
        Args:
            command: Specific command to clear (None = clear all)
        """
        if command:
            # Clear specific command cache
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    if cache_data.get('command') == command:
                        cache_file.unlink()
                except Exception:
                    cache_file.unlink(missing_ok=True)
        else:
            # Clear all cache
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink(missing_ok=True)
    
    def cleanup_expired(self):
        """Remove all expired cache entries"""
        now = datetime.now()
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if now - cached_time > timedelta(seconds=self.ttl):
                    cache_file.unlink()
            except Exception:
                cache_file.unlink(missing_ok=True)


# Global cache instance
_cache_instance: Optional[CLICache] = None


def get_cache() -> CLICache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CLICache()
    return _cache_instance


def cache_command(command: str, ttl: Optional[int] = None):
    """
    Decorator to cache command results
    
    Args:
        command: Command name
        ttl: Time to live in seconds (None = use default)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache()
            if ttl:
                cache.ttl = ttl
            
            # Get from cache
            cache_key = {
                "args": args,
                "kwargs": kwargs
            }
            cached_result = cache.get(command, cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute and cache
            result = func(*args, **kwargs)
            cache.set(command, cache_key, result)
            return result
        return wrapper
    return decorator

