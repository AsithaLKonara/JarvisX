"""
Status and Version Commands
"""

import typer
from cli.base import get_output, get_config
from cli.utils import CLIOutput, get_project_root


def status_command(
    verbose: bool = typer.Option(False, '--verbose', '-v'),
    json_output: bool = typer.Option(False, '--json')
):
    """Show overall system status"""
    output = CLIOutput(json_output=json_output)
    config = get_config()
    
    # Get system information
    import platform
    import sys
    
    status_info = {
        "System": {
            "OS": f"{platform.system()} {platform.release()}",
            "Python": platform.python_version(),
            "Architecture": platform.machine()
        },
        "Configuration": {
            "Config File": config.config_file if hasattr(config, 'config_file') else "default",
            "Log Level": config.get('log_level', 'INFO')
        },
        "Project": {
            "Root": str(get_project_root())
        }
    }
    
    output.print_dict(status_info, title="System Status")


def version_command(
    json_output: bool = typer.Option(False, '--json')
):
    """Show version information"""
    output = CLIOutput(json_output=json_output)
    
    version_info = {
        "version": "2.0.0",
        "cli_version": "1.0.0",
        "model_version": "7B-LoRA-v1"
    }
    
    if json_output:
        output.print_json(version_info)
    else:
        output.info(f"JarvisX V2 CLI Version: {version_info['cli_version']}")
        output.info(f"JarvisX Version: {version_info['version']}")
        output.info(f"Model Version: {version_info['model_version']}")

