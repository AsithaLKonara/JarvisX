"""
JARVIS AI - Plugin Manager
Advanced plugin system for extensible functionality.
"""

import os
import json
import logging
import importlib
import importlib.util
import inspect
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
from datetime import datetime
import sys

class PluginBase:
    """
    Base class for all Jarvis AI plugins.
    Provides standard interface and lifecycle management.
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """Initialize plugin."""
        self.name = name
        self.version = version
        self.is_enabled = False
        self.is_loaded = False
        self.logger = logging.getLogger(f"plugin.{name}")
        
        # Plugin metadata
        self.metadata = {
            'name': name,
            'version': version,
            'author': 'Unknown',
            'description': 'No description provided',
            'category': 'general',
            'dependencies': [],
            'compatibility': '1.0.0'
        }
    
    def initialize(self, config: Dict = None) -> bool:
        """Initialize the plugin."""
        try:
            self.logger.info(f"Initializing plugin: {self.name}")
            self.is_loaded = True
            return True
        except Exception as e:
            self.logger.error(f"Error initializing plugin {self.name}: {e}")
            return False
    
    def enable(self) -> bool:
        """Enable the plugin."""
        try:
            self.logger.info(f"Enabling plugin: {self.name}")
            self.is_enabled = True
            return True
        except Exception as e:
            self.logger.error(f"Error enabling plugin {self.name}: {e}")
            return False
    
    def disable(self) -> bool:
        """Disable the plugin."""
        try:
            self.logger.info(f"Disabling plugin: {self.name}")
            self.is_enabled = False
            return True
        except Exception as e:
            self.logger.error(f"Error disabling plugin {self.name}: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources."""
        try:
            self.logger.info(f"Cleaning up plugin: {self.name}")
            self.is_loaded = False
            self.is_enabled = False
            return True
        except Exception as e:
            self.logger.error(f"Error cleaning up plugin {self.name}: {e}")
            return False
    
    def get_info(self) -> Dict:
        """Get plugin information."""
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.is_enabled,
            'loaded': self.is_loaded,
            'metadata': self.metadata
        }
    
    def process_command(self, command: str, context: Dict = None) -> Dict:
        """Process a command (to be overridden by plugins)."""
        return {
            'success': False,
            'message': f'Plugin {self.name} does not implement command processing',
            'data': {}
        }
    
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities (to be overridden by plugins)."""
        return []

class PluginManager:
    """
    Advanced plugin manager for Jarvis AI.
    Handles plugin loading, management, and lifecycle.
    """
    
    def __init__(self, plugins_dir: str = "plugins"):
        """Initialize plugin manager."""
        self.logger = logging.getLogger(__name__)
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        
        # Plugin registry
        self.plugins = {}
        self.enabled_plugins = {}
        self.plugin_configs = {}
        
        # Plugin lifecycle
        self.plugin_lifecycle = {
            'loaded': [],
            'enabled': [],
            'disabled': [],
            'failed': []
        }
        
        self.logger.info("Plugin Manager initialized")
    
    def load_plugins(self) -> Dict:
        """Load all available plugins."""
        try:
            self.logger.info("Loading plugins...")
            
            load_results = {
                'total_found': 0,
                'successfully_loaded': 0,
                'failed_to_load': 0,
                'plugins': {}
            }
            
            # Find plugin files
            plugin_files = list(self.plugins_dir.rglob("*.py"))
            load_results['total_found'] = len(plugin_files)
            
            for plugin_file in plugin_files:
                try:
                    plugin_name = plugin_file.stem
                    
                    # Skip __init__.py files
                    if plugin_name == '__init__':
                        continue
                    
                    # Load plugin
                    plugin = self._load_plugin_from_file(plugin_file)
                    
                    if plugin:
                        self.plugins[plugin_name] = plugin
                        load_results['successfully_loaded'] += 1
                        load_results['plugins'][plugin_name] = 'success'
                        self.plugin_lifecycle['loaded'].append(plugin_name)
                    else:
                        load_results['failed_to_load'] += 1
                        load_results['plugins'][plugin_name] = 'failed'
                        self.plugin_lifecycle['failed'].append(plugin_name)
                
                except Exception as e:
                    self.logger.error(f"Error loading plugin {plugin_file}: {e}")
                    load_results['failed_to_load'] += 1
                    load_results['plugins'][plugin_file.stem] = 'error'
                    self.plugin_lifecycle['failed'].append(plugin_file.stem)
            
            self.logger.info(f"Plugin loading completed: {load_results['successfully_loaded']} loaded, {load_results['failed_to_load']} failed")
            return load_results
        
        except Exception as e:
            self.logger.error(f"Error loading plugins: {e}")
            return {'error': str(e)}
    
    def _load_plugin_from_file(self, plugin_file: Path) -> Optional[PluginBase]:
        """Load a plugin from a Python file."""
        try:
            # Import the plugin module
            spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginBase) and 
                    obj != PluginBase):
                    plugin_classes.append(obj)
            
            if not plugin_classes:
                self.logger.warning(f"No plugin classes found in {plugin_file}")
                return None
            
            # Use the first plugin class found
            plugin_class = plugin_classes[0]
            plugin_instance = plugin_class()
            
            # Initialize the plugin
            if plugin_instance.initialize():
                return plugin_instance
            else:
                self.logger.error(f"Failed to initialize plugin {plugin_file.stem}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error loading plugin from {plugin_file}: {e}")
            return None
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a specific plugin."""
        try:
            if plugin_name not in self.plugins:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False
            
            plugin = self.plugins[plugin_name]
            
            if plugin.enable():
                self.enabled_plugins[plugin_name] = plugin
                self.plugin_lifecycle['enabled'].append(plugin_name)
                self.logger.info(f"Plugin {plugin_name} enabled")
                return True
            else:
                self.logger.error(f"Failed to enable plugin {plugin_name}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error enabling plugin {plugin_name}: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a specific plugin."""
        try:
            if plugin_name not in self.enabled_plugins:
                self.logger.warning(f"Plugin {plugin_name} is not enabled")
                return True
            
            plugin = self.enabled_plugins[plugin_name]
            
            if plugin.disable():
                del self.enabled_plugins[plugin_name]
                self.plugin_lifecycle['disabled'].append(plugin_name)
                self.logger.info(f"Plugin {plugin_name} disabled")
                return True
            else:
                self.logger.error(f"Failed to disable plugin {plugin_name}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error disabling plugin {plugin_name}: {e}")
            return False
    
    def process_command_with_plugins(self, command: str, context: Dict = None) -> Dict:
        """Process command using enabled plugins."""
        try:
            results = {
                'processed': False,
                'plugin_responses': [],
                'best_response': None
            }
            
            # Try each enabled plugin
            for plugin_name, plugin in self.enabled_plugins.items():
                try:
                    if plugin.is_enabled:
                        response = plugin.process_command(command, context)
                        results['plugin_responses'].append({
                            'plugin': plugin_name,
                            'response': response
                        })
                        
                        # If plugin successfully processed the command
                        if response.get('success', False):
                            results['processed'] = True
                            if not results['best_response'] or response.get('confidence', 0) > results['best_response'].get('confidence', 0):
                                results['best_response'] = response
                except Exception as e:
                    self.logger.warning(f"Error processing command with plugin {plugin_name}: {e}")
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error processing command with plugins: {e}")
            return {'error': str(e)}
    
    def get_plugin_info(self, plugin_name: str) -> Dict:
        """Get information about a specific plugin."""
        try:
            if plugin_name not in self.plugins:
                return {'error': f'Plugin {plugin_name} not found'}
            
            plugin = self.plugins[plugin_name]
            return plugin.get_info()
        
        except Exception as e:
            self.logger.error(f"Error getting plugin info for {plugin_name}: {e}")
            return {'error': str(e)}
    
    def get_all_plugins_info(self) -> Dict:
        """Get information about all plugins."""
        try:
            plugins_info = {}
            
            for plugin_name, plugin in self.plugins.items():
                plugins_info[plugin_name] = plugin.get_info()
            
            return {
                'total_plugins': len(self.plugins),
                'enabled_plugins': len(self.enabled_plugins),
                'plugins': plugins_info,
                'lifecycle': self.plugin_lifecycle
            }
        
        except Exception as e:
            self.logger.error(f"Error getting all plugins info: {e}")
            return {'error': str(e)}
    
    def create_plugin_template(self, plugin_name: str, category: str = "general") -> bool:
        """Create a plugin template for development."""
        try:
            plugin_file = self.plugins_dir / f"{plugin_name}.py"
            
            if plugin_file.exists():
                self.logger.warning(f"Plugin {plugin_name} already exists")
                return False
            
            # Create plugin template
            template_content = f'''"""
JARVIS AI - {plugin_name.title()} Plugin
Custom plugin for {plugin_name} functionality.
"""

import logging
from plugins.plugin_manager import PluginBase

class {plugin_name.title()}Plugin(PluginBase):
    """
    {plugin_name.title()} plugin for Jarvis AI.
    """
    
    def __init__(self):
        super().__init__("{plugin_name}", "1.0.0")
        
        # Plugin metadata
        self.metadata.update({{
            'author': 'Your Name',
            'description': 'Description of {plugin_name} plugin',
            'category': '{category}',
            'dependencies': [],
            'compatibility': '1.0.0'
        }})
        
        self.logger = logging.getLogger(f"plugin.{{self.name}}")
    
    def initialize(self, config: dict = None) -> bool:
        """Initialize the plugin."""
        try:
            self.logger.info(f"Initializing {{self.name}} plugin")
            
            # Add your initialization code here
            
            return super().initialize(config)
        except Exception as e:
            self.logger.error(f"Error initializing {{self.name}} plugin: {{e}}")
            return False
    
    def process_command(self, command: str, context: dict = None) -> dict:
        """Process a command."""
        try:
            # Add your command processing logic here
            command_lower = command.lower()
            
            if "{plugin_name}" in command_lower:
                return {{
                    'success': True,
                    'message': f'{{self.name}} plugin processed: {{command}}',
                    'data': {{'plugin': self.name, 'command': command}},
                    'confidence': 0.8
                }}
            
            return {{
                'success': False,
                'message': f'{{self.name}} plugin cannot process: {{command}}',
                'data': {{}},
                'confidence': 0.0
            }}
        
        except Exception as e:
            self.logger.error(f"Error processing command in {{self.name}} plugin: {{e}}")
            return {{
                'success': False,
                'message': f'Error in {{self.name}} plugin: {{e}}',
                'data': {{}},
                'confidence': 0.0
            }}
    
    def get_capabilities(self) -> list:
        """Get plugin capabilities."""
        return [
            "{plugin_name} processing",
            "Custom functionality",
            "Command handling"
        ]
'''
            
            # Write template file
            with open(plugin_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            self.logger.info(f"Plugin template created: {plugin_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating plugin template: {e}")
            return False
    
    def cleanup_plugins(self) -> bool:
        """Cleanup all plugins."""
        try:
            self.logger.info("Cleaning up plugins...")
            
            # Disable all enabled plugins
            for plugin_name in list(self.enabled_plugins.keys()):
                self.disable_plugin(plugin_name)
            
            # Cleanup all plugins
            for plugin_name, plugin in self.plugins.items():
                plugin.cleanup()
            
            # Clear registries
            self.plugins.clear()
            self.enabled_plugins.clear()
            self.plugin_lifecycle = {
                'loaded': [],
                'enabled': [],
                'disabled': [],
                'failed': []
            }
            
            self.logger.info("Plugin cleanup completed")
            return True
        
        except Exception as e:
            self.logger.error(f"Error cleaning up plugins: {e}")
            return False
    
    def export_plugin_report(self, output_file: str = "plugin_report.json") -> bool:
        """Export plugin report to file."""
        try:
            report = {
                'plugin_manager_info': {
                    'plugins_dir': str(self.plugins_dir),
                    'total_plugins': len(self.plugins),
                    'enabled_plugins': len(self.enabled_plugins),
                    'lifecycle': self.plugin_lifecycle
                },
                'plugins': self.get_all_plugins_info(),
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Plugin report exported to: {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting plugin report: {e}")
            return False
