"""
Configuration utilities
"""
import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".jarvisx" / "config.json"

def load_config() -> dict:
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(config: dict):
    """Save configuration to file"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

