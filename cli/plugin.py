"""
CLI Plugin Management Commands
Commands for managing plugins
"""

import typer
from typing import Optional
from rich.table import Table

from cli.base import get_output
from plugins.plugin_manager import PluginManager

app = typer.Typer(name="plugin", help="Plugin management")

# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get or create plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
        _plugin_manager.load_plugins()
    return _plugin_manager


@app.command("list")
def list_plugins(
    enabled_only: bool = typer.Option(False, '--enabled', '-e', help='Show only enabled plugins'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """List all available plugins"""
    output = get_output()
    manager = get_plugin_manager()
    
    try:
        plugins_info = manager.get_all_plugins_info()
        
        if json_output:
            import json
            output.print(json.dumps(plugins_info, indent=2, default=str))
            return
        
        plugins = plugins_info.get('plugins', {})
        
        if enabled_only:
            enabled = manager.enabled_plugins.keys()
            plugins = {k: v for k, v in plugins.items() if k in enabled}
        
        if not plugins:
            output.info("No plugins found." if not enabled_only else "No enabled plugins found.")
            return
        
        # Create table
        table = Table(title="Available Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Category", style="blue")
        table.add_column("Description", style="white")
        
        for name, info in plugins.items():
            status = "✅ Enabled" if info.get('enabled') else "❌ Disabled"
            metadata = info.get('metadata', {})
            table.add_row(
                name,
                info.get('version', 'N/A'),
                status,
                metadata.get('category', 'general'),
                metadata.get('description', 'No description')[:50]
            )
        
        output.print(table)
        output.success(f"Found {len(plugins)} plugin(s)")
        
    except Exception as e:
        output.error(f"Failed to list plugins: {e}")
        raise typer.Exit(1)


@app.command("enable")
def enable_plugin(
    plugin_name: str = typer.Argument(..., help='Plugin name to enable'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Enable a plugin"""
    output = get_output()
    manager = get_plugin_manager()
    
    try:
        success = manager.enable_plugin(plugin_name)
        
        if json_output:
            import json
            output.print(json.dumps({"success": success, "plugin": plugin_name}, indent=2))
            return
        
        if success:
            output.success(f"Plugin '{plugin_name}' enabled successfully")
        else:
            output.error(f"Failed to enable plugin '{plugin_name}'")
            raise typer.Exit(1)
        
    except Exception as e:
        output.error(f"Failed to enable plugin: {e}")
        raise typer.Exit(1)


@app.command("disable")
def disable_plugin(
    plugin_name: str = typer.Argument(..., help='Plugin name to disable'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Disable a plugin"""
    output = get_output()
    manager = get_plugin_manager()
    
    try:
        success = manager.disable_plugin(plugin_name)
        
        if json_output:
            import json
            output.print(json.dumps({"success": success, "plugin": plugin_name}, indent=2))
            return
        
        if success:
            output.success(f"Plugin '{plugin_name}' disabled successfully")
        else:
            output.error(f"Failed to disable plugin '{plugin_name}'")
            raise typer.Exit(1)
        
    except Exception as e:
        output.error(f"Failed to disable plugin: {e}")
        raise typer.Exit(1)


@app.command("info")
def plugin_info(
    plugin_name: str = typer.Argument(..., help='Plugin name'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Get detailed information about a plugin"""
    output = get_output()
    manager = get_plugin_manager()
    
    try:
        info = manager.get_plugin_info(plugin_name)
        
        if json_output:
            import json
            output.print(json.dumps(info, indent=2, default=str))
            return
        
        if 'error' in info:
            output.error(info['error'])
            raise typer.Exit(1)
        
        # Display plugin info
        output.print_panel(
            f"Plugin: {info.get('name', 'N/A')}\n"
            f"Version: {info.get('version', 'N/A')}\n"
            f"Status: {'✅ Enabled' if info.get('enabled') else '❌ Disabled'}\n"
            f"Loaded: {'Yes' if info.get('loaded') else 'No'}",
            title="Plugin Information"
        )
        
        metadata = info.get('metadata', {})
        if metadata:
            output.print("\n[bold]Metadata:[/bold]")
            output.print(f"  Author: {metadata.get('author', 'N/A')}")
            output.print(f"  Category: {metadata.get('category', 'N/A')}")
            output.print(f"  Description: {metadata.get('description', 'N/A')}")
            if metadata.get('dependencies'):
                output.print(f"  Dependencies: {', '.join(metadata['dependencies'])}")
        
        capabilities = manager.plugins.get(plugin_name)
        if capabilities:
            caps = capabilities.get_capabilities()
            if caps:
                output.print("\n[bold]Capabilities:[/bold]")
                for cap in caps:
                    output.print(f"  • {cap}")
        
    except Exception as e:
        output.error(f"Failed to get plugin info: {e}")
        raise typer.Exit(1)


@app.command("create")
def create_plugin(
    plugin_name: str = typer.Argument(..., help='Plugin name'),
    category: str = typer.Option("general", '--category', '-c', help='Plugin category'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Create a new plugin template"""
    output = get_output()
    manager = get_plugin_manager()
    
    try:
        success = manager.create_plugin_template(plugin_name, category)
        
        if json_output:
            import json
            output.print(json.dumps({"success": success, "plugin": plugin_name}, indent=2))
            return
        
        if success:
            output.success(f"Plugin template '{plugin_name}' created successfully")
            output.info(f"Edit plugins/{plugin_name}.py to implement your plugin")
        else:
            output.error(f"Failed to create plugin template (plugin may already exist)")
            raise typer.Exit(1)
        
    except Exception as e:
        output.error(f"Failed to create plugin: {e}")
        raise typer.Exit(1)


@app.command("reload")
def reload_plugins(
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Reload all plugins"""
    output = get_output()
    global _plugin_manager
    _plugin_manager = None  # Reset manager
    
    manager = get_plugin_manager()
    
    try:
        results = manager.load_plugins()
        
        if json_output:
            import json
            output.print(json.dumps(results, indent=2, default=str))
            return
        
        output.success(f"Reloaded plugins: {results.get('successfully_loaded', 0)} loaded, {results.get('failed_to_load', 0)} failed")
        
    except Exception as e:
        output.error(f"Failed to reload plugins: {e}")
        raise typer.Exit(1)

