"""
CLI Command Templates
Save and execute command templates for quick access
"""

import json
import typer
from typing import Optional
from pathlib import Path
from rich.table import Table

from cli.base import get_output
from cli.utils import get_project_root

app = typer.Typer(name="template", help="Command templates management")

TEMPLATES_FILE = get_project_root() / "data" / "command_templates.json"


def _load_templates() -> dict:
    """Load templates from file"""
    if TEMPLATES_FILE.exists():
        try:
            with open(TEMPLATES_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def _save_templates(templates: dict):
    """Save templates to file"""
    TEMPLATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(templates, f, indent=2)


@app.command("save")
def save_template(
    name: str = typer.Argument(..., help='Template name'),
    command: str = typer.Argument(..., help='Command to save'),
    description: Optional[str] = typer.Option(None, '--description', '-d', help='Template description'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Save a command template"""
    output = get_output()
    
    try:
        templates = _load_templates()
        
        templates[name] = {
            "command": command,
            "description": description or f"Template for {name}",
            "created": str(Path(__file__).stat().st_mtime)  # Simple timestamp
        }
        
        _save_templates(templates)
        
        if json_output:
            import json
            output.print(json.dumps({"success": True, "template": name}, indent=2))
        else:
            output.success(f"Template '{name}' saved successfully")
        
    except Exception as e:
        output.error(f"Failed to save template: {e}")
        raise typer.Exit(1)


@app.command("list")
def list_templates(
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """List all saved templates"""
    output = get_output()
    
    try:
        templates = _load_templates()
        
        if json_output:
            import json
            output.print(json.dumps(templates, indent=2))
            return
        
        if not templates:
            output.info("No templates saved.")
            return
        
        # Create table
        table = Table(title="Command Templates")
        table.add_column("Name", style="cyan")
        table.add_column("Command", style="green")
        table.add_column("Description", style="yellow")
        
        for name, template in templates.items():
            cmd = template.get('command', '')[:50]
            desc = template.get('description', 'No description')[:40]
            table.add_row(name, cmd, desc)
        
        output.print(table)
        output.success(f"Found {len(templates)} template(s)")
        
    except Exception as e:
        output.error(f"Failed to list templates: {e}")
        raise typer.Exit(1)


@app.command("get")
def get_template(
    name: str = typer.Argument(..., help='Template name'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Get a template command"""
    output = get_output()
    
    try:
        templates = _load_templates()
        
        if name not in templates:
            output.error(f"Template '{name}' not found")
            raise typer.Exit(1)
        
        template = templates[name]
        
        if json_output:
            import json
            output.print(json.dumps(template, indent=2))
        else:
            output.print(template['command'])
        
    except Exception as e:
        output.error(f"Failed to get template: {e}")
        raise typer.Exit(1)


@app.command("delete")
def delete_template(
    name: str = typer.Argument(..., help='Template name'),
    confirm: bool = typer.Option(False, '--yes', '-y', help='Skip confirmation'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Delete a template"""
    output = get_output()
    
    try:
        templates = _load_templates()
        
        if name not in templates:
            output.error(f"Template '{name}' not found")
            raise typer.Exit(1)
        
        if not confirm:
            if not json_output:
                output.warning(f"This will delete template '{name}'.")
                response = typer.confirm("Are you sure?", default=False)
                if not response:
                    output.info("Operation cancelled.")
                    return
        
        del templates[name]
        _save_templates(templates)
        
        if json_output:
            import json
            output.print(json.dumps({"success": True, "template": name}, indent=2))
        else:
            output.success(f"Template '{name}' deleted successfully")
        
    except Exception as e:
        output.error(f"Failed to delete template: {e}")
        raise typer.Exit(1)


@app.command("execute")
def execute_template(
    name: str = typer.Argument(..., help='Template name'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Execute a saved template"""
    output = get_output()
    
    try:
        templates = _load_templates()
        
        if name not in templates:
            output.error(f"Template '{name}' not found")
            raise typer.Exit(1)
        
        command = templates[name]['command']
        
        if json_output:
            import json
            output.print(json.dumps({"command": command, "template": name}, indent=2))
        else:
            output.info(f"Executing template '{name}': {command}")
            # Note: Actual execution would require subprocess or CLI integration
            output.print(f"[bold]Command:[/bold] {command}")
            output.info("Use this command with your CLI or copy it to execute")
        
    except Exception as e:
        output.error(f"Failed to execute template: {e}")
        raise typer.Exit(1)

