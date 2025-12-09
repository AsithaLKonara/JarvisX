"""
Interactive Help System for JarvisX V2 CLI
Provides contextual help and examples
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from typing import Optional

from cli.base import get_output

app = typer.Typer(name="help", help="Interactive help system")
console = Console()


@app.command()
def command(
    command_name: Optional[str] = typer.Argument(None, help="Command or command group to get help for")
):
    """Get help for a specific command or show general help"""
    output = get_output()
    
    if not command_name:
        show_general_help(output)
    else:
        show_command_help(command_name, output)


def show_general_help(output):
    """Show general help with command groups and examples"""
    help_text = """
# JarvisX V2 CLI - Quick Reference

## Command Groups

**Training Operations**
- `training start` - Start a training job
- `training status` - Check training status
- `training list` - List all training jobs
- `training logs` - View training logs

**Cloud Operations**
- `cloud connect` - Connect to cloud LLM
- `cloud deploy` - Deploy to Hugging Face
- `cloud status` - Check cloud status
- `cloud monitor` - Monitor cloud metrics

**System Management**
- `system status` - Show system status
- `system health` - Run health check
- `system optimize` - Optimize system
- `system logs` - View system logs

**Business Operations**
- `business invoice` - Generate invoices
- `business client` - Manage clients
- `business report` - Generate reports
- `business task` - Manage tasks

**Voice Commands**
- `voice listen` - Listen for voice input
- `voice speak` - Text-to-speech output
- `voice interactive` - Interactive voice mode
- `voice command` - Parse voice command

**Model Management**
- `model list` - List available models
- `model load` - Load a model
- `model compare` - Compare models
- `model upload` - Upload to Hugging Face

## Common Options

All commands support:
- `--verbose, -v` - Enable verbose output
- `--json` - Output in JSON format
- `--voice` - Enable voice output (TTS)
- `--config` - Path to configuration file

## Examples

```bash
# Quick status check
jarvisx-cli status

# Start training with voice feedback
jarvisx-cli training start --config config.json --voice

# Generate invoice
jarvisx-cli business invoice --client-id 1

# Interactive voice mode
jarvisx-cli voice interactive

# Get help for specific command
jarvisx-cli help command training
```

## Getting More Help

- `jarvisx-cli --help` - Show all commands
- `jarvisx-cli <command> --help` - Help for specific command
- `jarvisx-cli help command <name>` - Detailed help for command
"""
    
    output.print_panel(
        Markdown(help_text),
        title="JarvisX V2 CLI Help",
        border_style="blue"
    )


def show_command_help(command_name: str, output):
    """Show detailed help for a specific command"""
    command_examples = {
        "training": {
            "description": "Training operations for fine-tuning models",
            "examples": [
                "jarvisx-cli training start --config training/config.json",
                "jarvisx-cli training status --job-id <id>",
                "jarvisx-cli training list",
                "jarvisx-cli training logs --job-id <id> --follow"
            ]
        },
        "cloud": {
            "description": "Cloud deployment and management",
            "examples": [
                "jarvisx-cli cloud connect --url <space-url>",
                "jarvisx-cli cloud deploy --space <name> --model <path>",
                "jarvisx-cli cloud status --space <name>",
                "jarvisx-cli cloud monitor --space <name>"
            ]
        },
        "system": {
            "description": "System monitoring and optimization",
            "examples": [
                "jarvisx-cli system status",
                "jarvisx-cli system health --full",
                "jarvisx-cli system optimize --auto",
                "jarvisx-cli system logs --tail 100"
            ]
        },
        "business": {
            "description": "Business automation and operations",
            "examples": [
                "jarvisx-cli business invoice --client-id 1",
                "jarvisx-cli business client list",
                "jarvisx-cli business client add --name 'John' --email 'john@example.com'",
                "jarvisx-cli business report --type financial"
            ]
        },
        "voice": {
            "description": "Voice input/output operations",
            "examples": [
                "jarvisx-cli voice listen --timeout 5",
                "jarvisx-cli voice speak 'Hello, world'",
                "jarvisx-cli voice interactive",
                "jarvisx-cli voice command 'start training'"
            ]
        },
        "model": {
            "description": "Model management and operations",
            "examples": [
                "jarvisx-cli model list",
                "jarvisx-cli model load --name <model-name>",
                "jarvisx-cli model compare --model1 <name1> --model2 <name2>",
                "jarvisx-cli model upload --model <path> --space <name>"
            ]
        }
    }
    
    if command_name.lower() in command_examples:
        info = command_examples[command_name.lower()]
        help_text = f"""
# {command_name.title()} Commands

**Description:** {info['description']}

## Examples

"""
        for example in info['examples']:
            help_text += f"```bash\n{example}\n```\n\n"
        
        help_text += f"""
## Get Detailed Help

```bash
jarvisx-cli {command_name} --help
```
"""
        output.print_panel(
            Markdown(help_text),
            title=f"Help: {command_name.title()}",
            border_style="green"
        )
    else:
        output.error(f"Command '{command_name}' not found. Use 'jarvisx-cli --help' to see all commands.")


@app.command()
def examples():
    """Show usage examples"""
    examples_text = """
# JarvisX V2 CLI - Usage Examples

## Basic Operations

```bash
# Check system status
jarvisx-cli status

# Show version
jarvisx-cli version

# Get help
jarvisx-cli --help
```

## Training Workflow

```bash
# Start training
jarvisx-cli training start --config training/config.json

# Monitor training
jarvisx-cli training status --job-id <id>

# View logs in real-time
jarvisx-cli training logs --job-id <id> --follow

# Evaluate model
jarvisx-cli training evaluate --job-id <id>
```

## Voice Operations

```bash
# Listen for voice input
jarvisx-cli voice listen --timeout 10

# Speak text
jarvisx-cli voice speak "Training completed"

# Interactive voice mode
jarvisx-cli voice interactive

# Parse voice command
jarvisx-cli voice command "start training"
```

## Business Automation

```bash
# Add a client
jarvisx-cli business client add --name "Acme Corp" --email "contact@acme.com"

# Generate invoice
jarvisx-cli business invoice --client-id 1 --template standard

# Generate report
jarvisx-cli business report --type financial --period monthly

# Export data
jarvisx-cli business export --type invoices --format csv
```

## Cloud Deployment

```bash
# Connect to cloud
jarvisx-cli cloud connect --url https://huggingface.co/spaces/user/space

# Deploy model
jarvisx-cli cloud deploy --space my-space --model ./models/my-model

# Monitor deployment
jarvisx-cli cloud monitor --space my-space --metrics latency,errors
```

## Advanced Usage

```bash
# JSON output for scripting
jarvisx-cli status --json | jq '.System.OS'

# Verbose output for debugging
jarvisx-cli training start --config config.json --verbose

# Voice-enabled commands
jarvisx-cli system status --voice

# Using templates
jarvisx-cli template list
jarvisx-cli template execute --name my-template
```
"""
    
    output = get_output()
    output.print_panel(
        Markdown(examples_text),
        title="Usage Examples",
        border_style="cyan"
    )


@app.command()
def quickstart():
    """Show quick start guide"""
    quickstart_text = """
# Quick Start Guide

## 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
jarvisx-cli version
```

## 2. First Commands

```bash
# Check system status
jarvisx-cli status

# Enable tab completion (bash/zsh)
eval "$(jarvisx-cli --show-completion bash)"  # or zsh

# Get help
jarvisx-cli --help
```

## 3. Common Workflows

### Training a Model
```bash
jarvisx-cli training start --config training/config.json
jarvisx-cli training status
```

### Voice Interaction
```bash
jarvisx-cli voice interactive
# Say: "start training"
```

### Business Operations
```bash
jarvisx-cli business client add --name "Client Name" --email "email@example.com"
jarvisx-cli business invoice --client-id 1
```

## 4. Next Steps

- Read full documentation: `docs/CLI_GUIDE.md`
- Try examples: `examples/`
- Get help: `jarvisx-cli help examples`
"""
    
    output = get_output()
    output.print_panel(
        Markdown(quickstart_text),
        title="Quick Start Guide",
        border_style="yellow"
    )

