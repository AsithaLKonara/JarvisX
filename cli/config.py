"""
Configuration Management Commands
"""

import typer
import json
from pathlib import Path
from typing import Optional

from cli.base import get_output, get_config
from cli.utils import CLIOutput, validate_config_file

app = typer.Typer(name="config", help="Configuration management")


@app.command("show")
def show_config(
    format: str = typer.Option("json", "--format", "-f", help="Output format (json/yaml)"),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Show current configuration"""
    output = CLIOutput(json_output=json_output)
    config = get_config()
    
    config_data = config.get_all()
    
    if format.lower() == "yaml":
        try:
            import yaml
            output.print_panel(yaml.dump(config_data, default_flow_style=False), title="Configuration")
        except ImportError:
            output.warning("YAML format requires PyYAML. Falling back to JSON.")
            output.print_json(config_data)
    else:
        output.print_json(config_data)


@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
    json_output: bool = typer.Option(False, '--json')
):
    """Set a configuration value"""
    output = CLIOutput(json_output=json_output)
    config = get_config()
    
    try:
        # Try to parse as JSON if possible
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, ValueError):
            pass  # Keep as string
        
        config.set(key, value)
        if config.save():
            output.success(f"Configuration '{key}' set to '{value}'")
        else:
            output.error("Failed to save configuration")
    except Exception as e:
        output.error(f"Error setting configuration: {e}")


@app.command("get")
def get_config_value(
    key: str = typer.Argument(..., help="Configuration key"),
    json_output: bool = typer.Option(False, '--json')
):
    """Get a configuration value"""
    output = CLIOutput(json_output=json_output)
    config = get_config()
    
    value = config.get(key)
    if value is not None:
        if json_output:
            output.print_json({key: value})
        else:
            output.info(f"{key}: {value}")
    else:
        output.warning(f"Configuration key '{key}' not found")


@app.command("validate")
def validate_config(
    config_path: Optional[str] = typer.Option(None, '--path', help='Path to config file'),
    json_output: bool = typer.Option(False, '--json')
):
    """Validate configuration file"""
    output = CLIOutput(json_output=json_output)
    
    if config_path:
        path = Path(config_path)
    else:
        config = get_config()
        path = config.config_file if hasattr(config, 'config_file') else Path("config/settings.json")
    
    if validate_config_file(str(path)):
        output.success(f"Configuration file is valid: {path}")
    else:
        output.error(f"Configuration file is invalid or not found: {path}")

