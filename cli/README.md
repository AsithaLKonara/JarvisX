# JarvisX V2 CLI Documentation

## Installation

The CLI is installed automatically when you install JarvisX V2. To use it:

```bash
# Install dependencies
pip install -r requirements.txt

# The CLI is available as 'jarvisx-cli'
jarvisx-cli --help
```

## Quick Start

```bash
# Show system status
jarvisx-cli status

# Show version
jarvisx-cli version

# Get help for any command
jarvisx-cli training --help
jarvisx-cli cloud --help
jarvisx-cli system --help
```

## Command Groups

### Training Commands

```bash
# Start a training job
jarvisx-cli training start --config training/training_config.json

# Check training status
jarvisx-cli training status --job-id <job-id>

# List all training jobs
jarvisx-cli training list

# View training logs
jarvisx-cli training logs --job-id <job-id> --follow

# Cancel a training job
jarvisx-cli training cancel --job-id <job-id>
```

### Cloud Operations

```bash
# Connect to cloud LLM
jarvisx-cli cloud connect --url <space-url>

# Deploy to Hugging Face Space
jarvisx-cli cloud deploy --space <space-name> --model <model-path>

# Check cloud status
jarvisx-cli cloud status --space <space-name>

# Test cloud API
jarvisx-cli cloud test --prompt "Hello"

# Monitor cloud metrics
jarvisx-cli cloud monitor --space <space-name> --metrics latency,errors
```

### System Commands

```bash
# Show system status
jarvisx-cli system status

# Run health check
jarvisx-cli system health --full

# Optimize system
jarvisx-cli system optimize --auto

# View system logs
jarvisx-cli system logs --tail 100

# Clean up system files
jarvisx-cli system cleanup --logs --cache --temp
```

### Business Mode

```bash
# Generate invoice
jarvisx-cli business invoice generate --client-id <id> --template standard

# List clients
jarvisx-cli business client list

# Add client
jarvisx-cli business client add --name "John Doe" --email "john@example.com"

# Generate report
jarvisx-cli business report --type financial --period monthly

# Export data
jarvisx-cli business export --type invoices --format csv --output invoices.csv
```

### Workflow Management

```bash
# List workflows
jarvisx-cli workflow list

# Execute workflow
jarvisx-cli workflow execute --id <workflow-id> --input '{"key": "value"}'

# Check workflow status
jarvisx-cli workflow status --execution-id <execution-id>

# View analytics
jarvisx-cli workflow analytics

# Get recommendations
jarvisx-cli workflow recommend --context '{"goals": ["automation"]}'
```

### Model Management

```bash
# List models
jarvisx-cli model list --local --remote

# Load model
jarvisx-cli model load --name <model-name> --version <version>

# Compare models
jarvisx-cli model compare --model-a <name> --model-b <name>

# Upload model
jarvisx-cli model upload --path <local-path> --repo <hf-repo>

# Test model
jarvisx-cli model test --name <model-name> --prompt "Hello"
```

### Configuration

```bash
# Show configuration
jarvisx-cli config show --format json

# Set configuration value
jarvisx-cli config set --key <key> --value <value>

# Get configuration value
jarvisx-cli config get --key <key>

# Validate configuration
jarvisx-cli config validate
```

## Voice Commands

JarvisX CLI supports voice input/output for hands-free operation:

```bash
# Listen for voice input
jarvisx-cli voice listen --timeout 5

# Convert text to speech
jarvisx-cli voice speak "Hello, this is Jarvis"

# Interactive voice mode (continuous listening)
jarvisx-cli voice interactive

# Parse a voice command
jarvisx-cli voice command "start training"
```

### Voice Command Examples

The voice command parser recognizes natural language commands:

- "start training" → `training start`
- "system status" → `system status`
- "list models" → `model list`
- "generate invoice" → `business invoice`
- "cloud status" → `cloud status`

## Common Options

All commands support these common options:

- `--verbose, -v`: Enable verbose output
- `--json`: Output in JSON format (useful for scripting)
- `--config`: Path to configuration file
- `--voice`: Enable voice output (TTS) for command results

Example:
```bash
jarvisx-cli system status --verbose --json --voice
```

## JSON Output

For scripting and automation, use `--json` flag:

```bash
# Get status as JSON
jarvisx-cli status --json

# Parse in script
STATUS=$(jarvisx-cli status --json)
echo $STATUS | jq '.System.OS'
```

## Error Handling

The CLI provides clear error messages and exit codes:

- Exit code 0: Success
- Exit code 1: General error
- Exit code 130: User interrupt (Ctrl+C)

## Development

To extend the CLI, add new commands to the appropriate module in `cli/`:

- `cli/training.py` - Training operations
- `cli/cloud.py` - Cloud operations
- `cli/system.py` - System monitoring
- `cli/business.py` - Business operations
- `cli/workflow.py` - Workflow management
- `cli/model.py` - Model management
- `cli/config.py` - Configuration
- `cli/voice.py` - Voice I/O operations
- `cli/voice_utils.py` - Voice command parsing

## Examples

### Automated Training Pipeline

```bash
#!/bin/bash
# Start training
JOB_ID=$(jarvisx-cli training start --config training/config.json --json | jq -r '.job_id')

# Monitor until complete
while true; do
    STATUS=$(jarvisx-cli training status --job-id $JOB_ID --json | jq -r '.status')
    if [ "$STATUS" = "completed" ]; then
        echo "Training completed!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "Training failed!"
        exit 1
    fi
    sleep 10
done

# Deploy to cloud
jarvisx-cli cloud deploy --space jarvis-llm-brain --model output/
```

### System Health Check

```bash
#!/bin/bash
# Run health check
HEALTH=$(jarvisx-cli system health --full --json)

# Check CPU usage
CPU=$(echo $HEALTH | jq -r '.CPU.Usage')
if (( $(echo "$CPU > 80" | bc -l) )); then
    echo "High CPU usage detected: $CPU%"
    jarvisx-cli system optimize --auto
fi
```

## Troubleshooting

### CLI not found

If `jarvisx-cli` command is not found:

```bash
# Install in development mode
pip install -e .

# Or use Python module directly
python -m cli.main
```

### Import errors

Make sure you're in the project root directory and all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Configuration issues

Validate your configuration:

```bash
jarvisx-cli config validate
```

## Support

For issues or questions, please refer to the main project README or open an issue on GitHub.

