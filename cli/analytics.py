"""
CLI Analytics Commands
Commands for viewing usage analytics and metrics
"""

import typer
from typing import Optional
from rich.table import Table
from datetime import datetime

from cli.base import get_output
from utils.usage_analytics import get_analytics

app = typer.Typer(name="analytics", help="Usage analytics and metrics")


@app.command("summary")
def analytics_summary(
    days: int = typer.Option(7, '--days', '-d', help='Number of days to analyze'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Show analytics summary"""
    output = get_output()
    analytics = get_analytics()
    
    try:
        summary = analytics.get_summary(days)
        
        if json_output:
            import json
            output.print(json.dumps(summary, indent=2, default=str))
            return
        
        # Display summary
        cmd_stats = summary["command_stats"]
        perf_stats = summary["performance_stats"]
        error_stats = summary["error_stats"]
        
        output.print_panel(
            f"Analytics Summary (Last {days} days)",
            title="Usage Analytics"
        )
        
        # Command statistics
        output.print("\n[bold cyan]Command Statistics:[/bold cyan]")
        output.print(f"  Total Commands: {cmd_stats['total_commands']}")
        output.print(f"  Unique Commands: {cmd_stats['unique_commands']}")
        output.print(f"  Success Rate: {cmd_stats['success_rate']:.1f}%")
        if cmd_stats['avg_duration'] > 0:
            output.print(f"  Avg Duration: {cmd_stats['avg_duration']:.2f}s")
        
        if cmd_stats['top_commands']:
            output.print("\n  [bold]Top Commands:[/bold]")
            for cmd_info in cmd_stats['top_commands'][:5]:
                output.print(f"    • {cmd_info['command']}: {cmd_info['count']} times")
        
        # Performance statistics
        if perf_stats['total_operations'] > 0:
            output.print("\n[bold cyan]Performance Statistics:[/bold cyan]")
            output.print(f"  Total Operations: {perf_stats['total_operations']}")
            output.print(f"  Avg Duration: {perf_stats['avg_duration']:.2f}s")
        
        # Error statistics
        if error_stats['total_errors'] > 0:
            output.print("\n[bold yellow]Error Statistics:[/bold yellow]")
            output.print(f"  Total Errors: {error_stats['total_errors']}")
            if error_stats['most_common_errors']:
                output.print("  [bold]Most Common Errors:[/bold]")
                for err_info in error_stats['most_common_errors'][:5]:
                    output.print(f"    • {err_info['type']}: {err_info['count']} times")
        
        output.success("Analytics summary displayed")
        
    except Exception as e:
        output.error(f"Failed to get analytics summary: {e}")
        raise typer.Exit(1)


@app.command("commands")
def command_stats(
    days: int = typer.Option(7, '--days', '-d', help='Number of days to analyze'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Show command usage statistics"""
    output = get_output()
    analytics = get_analytics()
    
    try:
        stats = analytics.get_command_stats(days)
        
        if json_output:
            import json
            output.print(json.dumps(stats, indent=2, default=str))
            return
        
        if stats['total_commands'] == 0:
            output.info(f"No commands tracked in the last {days} days.")
            return
        
        # Create table
        table = Table(title=f"Command Statistics (Last {days} days)")
        table.add_column("Command", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Avg Duration", style="yellow")
        
        for cmd_info in stats['top_commands']:
            cmd = cmd_info['command']
            count = cmd_info['count']
            avg_dur = stats['command_durations'].get(cmd, 0.0)
            dur_str = f"{avg_dur:.2f}s" if avg_dur > 0 else "N/A"
            table.add_row(cmd, str(count), dur_str)
        
        output.print(table)
        output.success(f"Total: {stats['total_commands']} commands, Success Rate: {stats['success_rate']:.1f}%")
        
    except Exception as e:
        output.error(f"Failed to get command stats: {e}")
        raise typer.Exit(1)


@app.command("performance")
def performance_stats(
    days: int = typer.Option(7, '--days', '-d', help='Number of days to analyze'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Show performance statistics"""
    output = get_output()
    analytics = get_analytics()
    
    try:
        stats = analytics.get_performance_stats(days)
        
        if json_output:
            import json
            output.print(json.dumps(stats, indent=2, default=str))
            return
        
        if stats['total_operations'] == 0:
            output.info(f"No performance data in the last {days} days.")
            return
        
        # Create table
        table = Table(title=f"Performance Statistics (Last {days} days)")
        table.add_column("Operation", style="cyan")
        table.add_column("Avg Duration", style="yellow")
        
        for op_info in stats['slowest_operations']:
            table.add_row(
                op_info['operation'],
                f"{op_info['avg_duration']:.2f}s"
            )
        
        output.print(table)
        output.success(f"Total Operations: {stats['total_operations']}, Avg: {stats['avg_duration']:.2f}s")
        
    except Exception as e:
        output.error(f"Failed to get performance stats: {e}")
        raise typer.Exit(1)


@app.command("errors")
def error_stats(
    days: int = typer.Option(7, '--days', '-d', help='Number of days to analyze'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Show error statistics"""
    output = get_output()
    analytics = get_analytics()
    
    try:
        stats = analytics.get_error_stats(days)
        
        if json_output:
            import json
            output.print(json.dumps(stats, indent=2, default=str))
            return
        
        if stats['total_errors'] == 0:
            output.success(f"No errors in the last {days} days! 🎉")
            return
        
        # Create table
        table = Table(title=f"Error Statistics (Last {days} days)")
        table.add_column("Error Type", style="red")
        table.add_column("Count", style="yellow")
        
        for err_info in stats['most_common_errors']:
            table.add_row(err_info['type'], str(err_info['count']))
        
        output.print(table)
        output.warning(f"Total Errors: {stats['total_errors']}")
        
    except Exception as e:
        output.error(f"Failed to get error stats: {e}")
        raise typer.Exit(1)


@app.command("clear")
def clear_analytics(
    confirm: bool = typer.Option(False, '--yes', '-y', help='Skip confirmation'),
    json_output: bool = typer.Option(False, '--json', help='Output in JSON format')
):
    """Clear all analytics data"""
    output = get_output()
    analytics = get_analytics()
    
    try:
        if not confirm:
            if not json_output:
                output.warning("This will clear all analytics data.")
                response = typer.confirm("Are you sure?", default=False)
                if not response:
                    output.info("Operation cancelled.")
                    return
        
        analytics.clear_analytics()
        
        if json_output:
            import json
            output.print(json.dumps({"success": True, "message": "Analytics cleared"}, indent=2))
        else:
            output.success("Analytics data cleared")
        
    except Exception as e:
        output.error(f"Failed to clear analytics: {e}")
        raise typer.Exit(1)

