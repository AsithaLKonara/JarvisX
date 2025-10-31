"""
JARVIS AI - Configuration Manager
Handles application configuration and environment variables.
"""

import os
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path

class Config:
    """
    Configuration manager for Jarvis AI.
    Handles environment variables and configuration files.
    """
    
    def __init__(self, config_file: str = "config/settings.json"):
        """Initialize configuration manager."""
        self.logger = logging.getLogger(__name__)
        self.config_file = Path(config_file)
        self.config_data = {}
        
        # Load configuration
        self._load_config()
        
        self.logger.info("Configuration manager initialized")
    
    def _load_config(self):
        """Load configuration from file and environment."""
        try:
            # Load from file if exists
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            
            # Override with environment variables
            self._load_env_vars()
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config_data = {}
    
    def _load_env_vars(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'HELAGPT_API_KEY': 'helagpt_api_key',
            'HELAGPT_BASE_URL': 'helagpt_base_url',
            'LOG_LEVEL': 'log_level',
            'DEBUG': 'debug'
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self.config_data[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config_data[key] = value
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved to: {self.config_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration data."""
        return self.config_data.copy()
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values."""
        try:
            self.config_data.update(updates)
            return self.save()
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return False
