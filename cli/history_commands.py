"""
CLI History Commands
Commands for managing and viewing command history
"""

import typer
from typing import Optional
from rich.table import Table
from rich.console import Console
from datetime import datetime

from cli.base import get_output
from cli.history import get_history

app = typer.Typer(name="history", help="Command history management")

console = Console()


@app.command("list")
def list_history(
    limit: int = typer.Option(10, '--limit', '-n', help='Number of commands to show'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """List recent command history"""
    output = get_output()
    history = get_history()
    
    try:
        recent = history.get_recent(limit)
        
        if json_output:
            import json
            output.print(json.dumps(recent, indent=2))
            return
        
        if not recent:
            output.info("No command history found.")
            return
        
        # Create table
        table = Table(title=f"Command History (Last {len(recent)} commands)")
        table.add_column("Time", style="cyan", no_wrap=True)
        table.add_column("Command", style="green")
        table.add_column("Args", style="yellow")
        
        for entry in recent:
            timestamp = entry.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    time_str = timestamp
            else:
                time_str = "Unknown"
            
            command = entry.get('command', '')
            args = entry.get('args', {})
            args_str = ', '.join([f"{k}={v}" for k, v in args.items()]) if args else ""
            
            table.add_row(time_str, command, args_str)
        
        output.print(table)
        output.success(f"Showing {len(recent)} recent commands")
        
    except Exception as e:
        output.error(f"Failed to list history: {e}")
        raise typer.Exit(1)


@app.command("search")
def search_history(
    query: str = typer.Argument(..., help='Search query'),
    limit: int = typer.Option(10, '--limit', '-n', help='Maximum results'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Search command history"""
    output = get_output()
    history = get_history()
    
    try:
        results = history.search(query, limit)
        
        if json_output:
            import json
            output.print(json.dumps(results, indent=2))
            return
        
        if not results:
            output.info(f"No commands found matching '{query}'")
            return
        
        # Create table
        table = Table(title=f"Search Results for '{query}' ({len(results)} found)")
        table.add_column("Time", style="cyan", no_wrap=True)
        table.add_column("Command", style="green")
        table.add_column("Args", style="yellow")
        
        for entry in results:
            timestamp = entry.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    time_str = timestamp
            else:
                time_str = "Unknown"
            
            command = entry.get('command', '')
            args = entry.get('args', {})
            args_str = ', '.join([f"{k}={v}" for k, v in args.items()]) if args else ""
            
            table.add_row(time_str, command, args_str)
        
        output.print(table)
        output.success(f"Found {len(results)} matching commands")
        
    except Exception as e:
        output.error(f"Failed to search history: {e}")
        raise typer.Exit(1)


@app.command("clear")
def clear_history(
    confirm: bool = typer.Option(False, '--yes', '-y', help='Skip confirmation'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Clear command history"""
    output = get_output()
    history = get_history()
    
    try:
        if not confirm:
            if not json_output:
                output.warning("This will clear all command history.")
                response = typer.confirm("Are you sure?", default=False)
                if not response:
                    output.info("Operation cancelled.")
                    return
        
        count = len(history.history)
        history.clear()
        
        if json_output:
            import json
            output.print(json.dumps({"cleared": count, "status": "success"}, indent=2))
        else:
            output.success(f"Cleared {count} commands from history")
        
    except Exception as e:
        output.error(f"Failed to clear history: {e}")
        raise typer.Exit(1)


@app.command("stats")
def history_stats(
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Show command history statistics"""
    output = get_output()
    history = get_history()
    
    try:
        total = len(history.history)
        
        if json_output:
            import json
            stats = {
                "total_commands": total,
                "max_history": history.max_history,
                "history_file": str(history.history_file)
            }
            output.print(json.dumps(stats, indent=2))
            return
        
        if total == 0:
            output.info("No command history available.")
            return
        
        # Count commands by type
        command_counts = {}
        for entry in history.history:
            cmd = entry.get('command', 'unknown')
            command_counts[cmd] = command_counts.get(cmd, 0) + 1
        
        # Create table
        table = Table(title="Command History Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Commands", str(total))
        table.add_row("Max History", str(history.max_history))
        table.add_row("History File", str(history.history_file))
        table.add_row("Unique Commands", str(len(command_counts)))
        
        output.print(table)
        
        # Show top commands
        if command_counts:
            top_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            cmd_table = Table(title="Top 5 Most Used Commands")
            cmd_table.add_column("Command", style="green")
            cmd_table.add_column("Count", style="yellow")
            
            for cmd, count in top_commands:
                cmd_table.add_row(cmd, str(count))
            
            output.print(cmd_table)
        
        output.success("History statistics displayed")
        
    except Exception as e:
        output.error(f"Failed to get history stats: {e}")
        raise typer.Exit(1)

