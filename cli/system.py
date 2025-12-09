"""
System Monitoring CLI Module
Commands for system monitoring and control
"""

import typer
from typing import Optional

from cli.base import get_output, get_config
from cli.utils import CLIOutput

app = typer.Typer(name="system", help="System monitoring and control")


@app.command("status")
def system_status(
    json_output: bool = typer.Option(False, '--json')
):
    """Show system status"""
    output = CLIOutput(json_output=json_output)
    
    try:
        import psutil
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory
        memory = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        status_data = {
            "CPU": {
                "Usage": f"{cpu_percent}%",
                "Cores": cpu_count
            },
            "Memory": {
                "Used": f"{memory.used / (1024**3):.2f} GB",
                "Total": f"{memory.total / (1024**3):.2f} GB",
                "Percent": f"{memory.percent}%"
            },
            "Disk": {
                "Used": f"{disk.used / (1024**3):.2f} GB",
                "Total": f"{disk.total / (1024**3):.2f} GB",
                "Percent": f"{disk.percent}%"
            }
        }
        
        output.print_dict(status_data, title="System Status")
    except ImportError:
        output.error("psutil not available. Install with: pip install psutil")
        raise typer.Exit(1)
    except Exception as e:
        output.error(f"Error getting system status: {e}")
        raise typer.Exit(1)


@app.command("health")
def system_health(
    full: bool = typer.Option(False, '--full', help='Show full health report'),
    json_output: bool = typer.Option(False, '--json')
):
    """Run system health check"""
    output = CLIOutput(json_output=json_output)
    
    try:
        import psutil
        
        from system_monitor.health_checker import HealthChecker
        from system_monitor.resource_monitor import ResourceMonitor
        
        output.info("Running system health check...")
        
        health_checker = HealthChecker()
        resource_monitor = ResourceMonitor()
        
        # Check CPU
        cpu_info = resource_monitor.get_cpu_info()
        cpu_healthy = cpu_info['percent'] < 90
        health_checker.check_component(
            "CPU",
            cpu_healthy,
            f"Usage: {cpu_info['percent']:.1f}%"
        )
        
        # Check Memory
        memory_info = resource_monitor.get_memory_info()
        memory_healthy = memory_info['percent'] < 90
        health_checker.check_component(
            "Memory",
            memory_healthy,
            f"Usage: {memory_info['percent']:.1f}%"
        )
        
        # Check Disk
        disk_info = resource_monitor.get_disk_info()
        disk_healthy = disk_info['percent'] < 90
        health_checker.check_component(
            "Disk",
            disk_healthy,
            f"Usage: {disk_info['percent']:.1f}%"
        )
        
        # Check services/components
        health_checker.check_component("CLI", True, "CLI system operational")
        
        # Get overall status
        all_status = health_checker.get_all_status()
        
        # Calculate health score
        components = all_status.get('components', {})
        healthy_count = sum(1 for c in components.values() if c.get('status') == 'healthy')
        total_count = len(components)
        health_score = int((healthy_count / total_count) * 100) if total_count > 0 else 0
        
        if json_output:
            output.print_json({
                "health_score": health_score,
                "components": components,
                "overall_status": all_status.get('overall_status', 'unknown')
            })
        else:
            output.print_dict({
                "Health Score": f"{health_score}%",
                "Overall Status": all_status.get('overall_status', 'unknown'),
                "Components Checked": total_count,
                "Healthy": healthy_count
            }, title="System Health")
            
            if full:
                output.print_dict(components, title="Component Details")
        
    except ImportError:
        output.error("Required modules not available. Install: pip install psutil")
        raise typer.Exit(1)
    except Exception as e:
        output.error(f"Error running health check: {e}")
        raise typer.Exit(1)


@app.command("optimize")
def system_optimize(
    auto: bool = typer.Option(False, '--auto', help='Auto-apply optimizations'),
    json_output: bool = typer.Option(False, '--json')
):
    """Optimize system resources"""
    output = CLIOutput(json_output=json_output)
    
    try:
        import psutil
        import gc
        from pathlib import Path
        from cli.utils import get_project_root
        
        output.info("Analyzing system resources...")
        
        from system_monitor.resource_monitor import ResourceMonitor
        monitor = ResourceMonitor()
        
        cpu_info = monitor.get_cpu_info()
        memory_info = monitor.get_memory_info()
        disk_info = monitor.get_disk_info()
        
        optimizations = []
        
        # Memory optimization
        if memory_info['percent'] > 70:
            if auto:
                gc.collect()
                optimizations.append("Garbage collection performed")
            else:
                optimizations.append("Recommendation: Run garbage collection (memory usage high)")
        
        # Disk optimization suggestions
        if disk_info['percent'] > 80:
            optimizations.append("Recommendation: Clean up old files (disk usage high)")
        
        # CPU optimization suggestions
        if cpu_info['percent'] > 80:
            optimizations.append("Recommendation: Reduce active processes (CPU usage high)")
        
        # Cache cleanup
        project_root = get_project_root()
        cache_dir = project_root / "cache"
        if cache_dir.exists():
            cache_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            if cache_size > 100 * 1024 * 1024:  # > 100MB
                if auto:
                    # Clean cache
                    for file in cache_dir.rglob('*'):
                        if file.is_file():
                            try:
                                file.unlink()
                            except:
                                pass
                    optimizations.append(f"Cleaned cache directory ({cache_size / (1024*1024):.1f} MB)")
                else:
                    optimizations.append(f"Recommendation: Clean cache ({cache_size / (1024*1024):.1f} MB)")
        
        if json_output:
            output.print_json({
                "optimizations": optimizations,
                "cpu_usage": cpu_info['percent'],
                "memory_usage": memory_info['percent'],
                "disk_usage": disk_info['percent']
            })
        else:
            if optimizations:
                output.info("Optimizations performed/recommended:")
                for opt in optimizations:
                    output.info(f"  • {opt}")
            else:
                output.success("System is already optimized")
            
            output.print_dict({
                "CPU Usage": f"{cpu_info['percent']:.1f}%",
                "Memory Usage": f"{memory_info['percent']:.1f}%",
                "Disk Usage": f"{disk_info['percent']:.1f}%"
            }, title="Current Resource Usage")
        
    except ImportError:
        output.error("Required modules not available. Install: pip install psutil")
        raise typer.Exit(1)
    except Exception as e:
        output.error(f"Error optimizing system: {e}")
        raise typer.Exit(1)


@app.command("logs")
def system_logs(
    tail: int = typer.Option(100, '--tail', '-n', help='Number of lines to show'),
    filter: Optional[str] = typer.Option(None, '--filter', '-f', help='Filter by log level (INFO/WARNING/ERROR)'),
    search: Optional[str] = typer.Option(None, '--search', '-s', help='Search for keyword'),
    export: Optional[str] = typer.Option(None, '--export', '-e', help='Export logs to file'),
    json_output: bool = typer.Option(False, '--json')
):
    """View system logs"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from pathlib import Path
        from cli.utils import get_project_root
        
        log_dir = get_project_root() / "logs"
        log_file = log_dir / "jarvis.log"
        
        if not log_file.exists():
            output.warning(f"Log file not found: {log_file}")
            return
        
        output.info(f"Reading logs from: {log_file}")
        
        # Read logs
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Apply filters
        filtered_lines = lines
        
        if filter:
            filter_upper = filter.upper()
            filtered_lines = [line for line in filtered_lines if filter_upper in line.upper()]
        
        if search:
            search_lower = search.lower()
            filtered_lines = [line for line in filtered_lines if search_lower in line.lower()]
        
        # Get last N lines
        if tail > 0:
            filtered_lines = filtered_lines[-tail:]
        
        # Export if requested
        if export:
            export_path = Path(export)
            with open(export_path, 'w') as f:
                f.writelines(filtered_lines)
            output.success(f"Logs exported to: {export_path}")
        
        if json_output:
            output.print_json({
                "log_file": str(log_file),
                "lines": [line.rstrip() for line in filtered_lines],
                "total_lines": len(filtered_lines)
            })
        else:
            if filter or search:
                output.info(f"Filtered logs ({len(filtered_lines)} lines)")
            else:
                output.info(f"Last {len(filtered_lines)} lines")
            print()
            for line in filtered_lines:
                print(line.rstrip())
        
    except Exception as e:
        output.error(f"Error reading logs: {e}")
        raise typer.Exit(1)


@app.command("cleanup")
def system_cleanup(
    logs: bool = typer.Option(False, '--logs', help='Clean up old logs'),
    cache: bool = typer.Option(False, '--cache', help='Clean up cache'),
    temp: bool = typer.Option(False, '--temp', help='Clean up temp files'),
    days: int = typer.Option(7, '--days', '-d', help='Keep files newer than N days'),
    json_output: bool = typer.Option(False, '--json')
):
    """Clean up system files"""
    output = CLIOutput(json_output=json_output)
    
    if not (logs or cache or temp):
        output.warning("No cleanup options specified. Use --logs, --cache, or --temp")
        return
    
    try:
        from pathlib import Path
        from datetime import datetime, timedelta
        from cli.utils import get_project_root
        
        project_root = get_project_root()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cleanup_summary = {
            "logs_cleaned": 0,
            "cache_cleaned": 0,
            "temp_cleaned": 0,
            "total_size_freed": 0
        }
        
        output.info(f"Cleaning up files older than {days} days...")
        
        # Clean logs
        if logs:
            log_dir = project_root / "logs"
            if log_dir.exists():
                for log_file in log_dir.glob("*.log*"):
                    try:
                        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            size = log_file.stat().st_size
                            log_file.unlink()
                            cleanup_summary["logs_cleaned"] += 1
                            cleanup_summary["total_size_freed"] += size
                    except Exception as e:
                        output.warning(f"Error cleaning log file {log_file}: {e}")
        
        # Clean cache
        if cache:
            cache_dir = project_root / "cache"
            if cache_dir.exists():
                for cache_file in cache_dir.rglob('*'):
                    if cache_file.is_file():
                        try:
                            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                            if file_time < cutoff_date:
                                size = cache_file.stat().st_size
                                cache_file.unlink()
                                cleanup_summary["cache_cleaned"] += 1
                                cleanup_summary["total_size_freed"] += size
                        except Exception as e:
                            pass  # Ignore errors for cache cleanup
        
        # Clean temp files
        if temp:
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            # Only clean JarvisX temp files
            for temp_file in temp_dir.glob("jarvisx_*"):
                if temp_file.is_file():
                    try:
                        file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            size = temp_file.stat().st_size
                            temp_file.unlink()
                            cleanup_summary["temp_cleaned"] += 1
                            cleanup_summary["total_size_freed"] += size
                    except Exception as e:
                        pass
        
        # Format size
        from cli.utils import format_file_size
        size_freed = format_file_size(cleanup_summary["total_size_freed"])
        
        if json_output:
            output.print_json({
                **cleanup_summary,
                "size_freed": size_freed
            })
        else:
            output.success("Cleanup completed")
            output.print_dict({
                "Logs Cleaned": cleanup_summary["logs_cleaned"],
                "Cache Files Cleaned": cleanup_summary["cache_cleaned"],
                "Temp Files Cleaned": cleanup_summary["temp_cleaned"],
                "Total Size Freed": size_freed
            }, title="Cleanup Summary")
        
    except Exception as e:
        output.error(f"Error during cleanup: {e}")
        raise typer.Exit(1)


@app.command("info")
def system_info(
    json_output: bool = typer.Option(False, '--json')
):
    """Show system information"""
    output = CLIOutput(json_output=json_output)
    
    import platform
    import sys
    
    info = {
        "Platform": platform.platform(),
        "System": platform.system(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Python": sys.version
    }
    
    output.print_dict(info, title="System Information")

