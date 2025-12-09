"""
JarvisX V2 CLI - Main Entry Point
Command-line interface for JarvisX V2 operations
"""

import sys
from pathlib import Path

import typer
from typer import Option

from cli.base import common_callback, get_output, get_config
from cli.utils import get_project_root
from cli.history import get_history

# Import command groups
try:
    from cli import training
    from cli import cloud
    from cli import system
    from cli import business
    from cli import workflow
    from cli import model
    from cli import config
    from cli import status
    from cli import voice
    from cli import history_commands
except ImportError as e:
    # Handle import errors gracefully
    import sys
    print(f"Error importing CLI modules: {e}", file=sys.stderr)
    print("Make sure you're running from the project root directory", file=sys.stderr)
    sys.exit(1)

# Create main Typer app
app = typer.Typer(
    name="jarvisx-cli",
    help="JarvisX V2 Command Line Interface",
    add_completion=False,
    no_args_is_help=True
)

# Add command groups
app.add_typer(training.app, name="training", help="Training operations")
app.add_typer(cloud.app, name="cloud", help="Cloud operations")
app.add_typer(system.app, name="system", help="System monitoring and control")
app.add_typer(business.app, name="business", help="Business mode operations")
app.add_typer(workflow.app, name="workflow", help="Workflow orchestration")
app.add_typer(model.app, name="model", help="Model management")
app.add_typer(config.app, name="config", help="Configuration management")
app.add_typer(voice.app, name="voice", help="Voice I/O operations")
app.add_typer(history_commands.app, name="history", help="Command history management")

# Add standalone commands
app.command(name="status")(status.status_command)
app.command(name="version")(status.version_command)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = Option(False, '--verbose', '-v', help='Enable verbose output'),
    json_output: bool = Option(False, '--json', help='Output in JSON format'),
    config_path: str = Option(None, '--config', help='Path to configuration file'),
    voice: bool = Option(False, '--voice', help='Enable voice output (TTS)')
):
    """
    JarvisX V2 Command Line Interface
    
    A comprehensive CLI for managing training, deployment, system operations,
    business automation, and workflows.
    """
    # Apply common callback
    common_callback(ctx, verbose, json_output, config_path, voice)
    
    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        output = get_output()
        output.print_panel(
            "JarvisX V2 CLI\n\nUse 'jarvisx-cli --help' to see available commands.",
            title="Welcome"
        )


def cli():
    """Entry point for CLI"""
    try:
        # Track command in history (before execution)
        try:
            import sys
            # Skip history tracking for history commands themselves
            if len(sys.argv) > 1 and sys.argv[1] != 'history':
                history = get_history()
                # Build command string from sys.argv (skip script name)
                cmd_parts = sys.argv[1:]
                # Filter out common flags that aren't part of the command
                filtered = [p for p in cmd_parts if not p.startswith('--verbose') and 
                           not p.startswith('-v') and not p.startswith('--json') and
                           not p.startswith('--config') and not p.startswith('--voice')]
                command_str = ' '.join(filtered) if filtered else ' '.join(cmd_parts)
                history.add(command_str, args={})
        except Exception:
            # Silently fail history tracking to not break CLI
            pass
        
        app()
    except KeyboardInterrupt:
        output = get_output()
        output.warning("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        output = get_output()
        output.error(f"Unexpected error: {e}")
        if get_config().get('verbose', False):
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli()

