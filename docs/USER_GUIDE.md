# 📖 JarvisX V2 - Complete User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [CLI Commands Reference](#cli-commands-reference)
5. [Voice Commands](#voice-commands)
6. [Common Workflows](#common-workflows)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Introduction

JarvisX V2 is a comprehensive AI assistant with a powerful command-line interface (CLI) that supports:
- **31+ CLI Commands** for training, deployment, system management, and business automation
- **Voice Integration** with Text-to-Speech (TTS) and Speech-to-Text (STT)
- **Plugin System** for extensibility
- **Command History** and analytics
- **Cloud Deployment** to Hugging Face Spaces

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (for cloning the repository)

### Install JarvisX V2

```bash
# Clone the repository
git clone https://github.com/AsithaLKonara/JarvisX.git
cd JarvisX

# Install dependencies
pip install -r requirements.txt

# Verify installation
jarvisx-cli version
```

### Enable Tab Completion (Optional but Recommended)

**Bash:**
```bash
eval "$(jarvisx-cli --show-completion bash)"
echo 'eval "$(jarvisx-cli --show-completion bash)"' >> ~/.bashrc
```

**Zsh:**
```bash
eval "$(jarvisx-cli --show-completion zsh)"
echo 'eval "$(jarvisx-cli --show-completion zsh)"' >> ~/.zshrc
```

---

## Quick Start

### 1. Check System Status

```bash
jarvisx-cli status
```

### 2. Get Help

```bash
# General help
jarvisx-cli --help

# Help for specific command group
jarvisx-cli training --help

# Interactive help
jarvisx-cli help quickstart
jarvisx-cli help examples
```

### 3. Try Voice Commands

```bash
# Interactive voice mode
jarvisx-cli voice interactive

# Or use voice output for any command
jarvisx-cli status --voice
```

---

## CLI Commands Reference

### Training Commands

Manage model training jobs:

```bash
# Start training
jarvisx-cli training start --config training/config.json

# Check status
jarvisx-cli training status --job-id <job-id>

# List all jobs
jarvisx-cli training list

# View logs
jarvisx-cli training logs --job-id <job-id> --follow

# Cancel training
jarvisx-cli training cancel --job-id <job-id>

# Evaluate model
jarvisx-cli training evaluate --job-id <job-id>
```

### Cloud Commands

Deploy and manage cloud deployments:

```bash
# Connect to cloud space
jarvisx-cli cloud connect --url <space-url>

# Deploy model
jarvisx-cli cloud deploy --space <space-name> --model <model-path>

# Check status
jarvisx-cli cloud status --space <space-name>

# Monitor metrics
jarvisx-cli cloud monitor --space <space-name> --metrics latency,errors

# View logs
jarvisx-cli cloud logs --space <space-name> --tail 100

# Test API
jarvisx-cli cloud test --prompt "Hello, Jarvis"
```

### System Commands

Monitor and optimize your system:

```bash
# System status
jarvisx-cli system status

# Health check
jarvisx-cli system health --full

# Optimize system
jarvisx-cli system optimize --auto

# View logs
jarvisx-cli system logs --tail 100

# Cleanup
jarvisx-cli system cleanup --logs --cache --temp
```

### Business Commands

Automate business operations:

```bash
# Generate invoice
jarvisx-cli business invoice --client-id <id> --template standard

# Client management
jarvisx-cli business client list
jarvisx-cli business client add --name "John Doe" --email "john@example.com"
jarvisx-cli business client get --id <id>

# Generate reports
jarvisx-cli business report --type financial --period monthly

# Task management
jarvisx-cli business task schedule --name "Weekly Report" --cron "0 0 * * 0"
jarvisx-cli business task list
jarvisx-cli business task cancel --id <id>

# Export data
jarvisx-cli business export --type invoices --format csv --output invoices.csv
```

### Model Commands

Manage AI models:

```bash
# List models
jarvisx-cli model list
jarvisx-cli model list --local
jarvisx-cli model list --remote

# Load model
jarvisx-cli model load --name <model-name>

# Compare models
jarvisx-cli model compare --model1 <name1> --model2 <name2>

# Upload model
jarvisx-cli model upload --model <path> --space <space-name>

# Model info
jarvisx-cli model info --name <model-name>

# Test model
jarvisx-cli model test --name <model-name> --prompt "Test prompt"
```

### Voice Commands

Voice input/output operations:

```bash
# Listen for voice input
jarvisx-cli voice listen --timeout 10

# Text-to-speech
jarvisx-cli voice speak "Hello, this is Jarvis"

# Interactive voice mode
jarvisx-cli voice interactive

# Parse voice command
jarvisx-cli voice command "start training"
```

### History Commands

Manage command history:

```bash
# List recent commands
jarvisx-cli history list --limit 20

# Search history
jarvisx-cli history search "training"

# Statistics
jarvisx-cli history stats

# Clear history
jarvisx-cli history clear

# Export history
jarvisx-cli history export --format json --output history.json
```

### Plugin Commands

Manage plugins:

```bash
# List plugins
jarvisx-cli plugin list
jarvisx-cli plugin list --enabled

# Enable/disable plugin
jarvisx-cli plugin enable <plugin-name>
jarvisx-cli plugin disable <plugin-name>

# Plugin info
jarvisx-cli plugin info <plugin-name>

# Create plugin
jarvisx-cli plugin create <plugin-name>

# Reload plugins
jarvisx-cli plugin reload
```

### Analytics Commands

View usage analytics:

```bash
# Summary
jarvisx-cli analytics summary

# Command statistics
jarvisx-cli analytics commands

# Performance metrics
jarvisx-cli analytics performance

# Error statistics
jarvisx-cli analytics errors

# Clear analytics
jarvisx-cli analytics clear
```

### Template Commands

Manage command templates:

```bash
# List templates
jarvisx-cli template list

# Create template
jarvisx-cli template create --name my-template --commands "training start;training status"

# Execute template
jarvisx-cli template execute --name my-template

# Delete template
jarvisx-cli template delete --name my-template
```

### Config Commands

Manage configuration:

```bash
# Show config
jarvisx-cli config show

# Set value
jarvisx-cli config set --key <key> --value <value>

# Get value
jarvisx-cli config get --key <key>

# Validate config
jarvisx-cli config validate
```

---

## Voice Commands

### Natural Language Voice Commands

The voice command parser recognizes natural language and maps it to CLI commands:

**Training:**
- "start training" → `training start`
- "training status" → `training status`
- "list training jobs" → `training list`

**System:**
- "system status" → `system status`
- "health check" → `system health`
- "optimize system" → `system optimize`

**Business:**
- "generate invoice" → `business invoice`
- "list clients" → `business client list`
- "add client" → `business client add`

**Cloud:**
- "cloud status" → `cloud status`
- "deploy model" → `cloud deploy`
- "monitor cloud" → `cloud monitor`

### Voice Output

Enable voice output for any command using the `--voice` flag:

```bash
jarvisx-cli status --voice
jarvisx-cli training start --config config.json --voice
jarvisx-cli system health --voice
```

---

## Common Workflows

### Complete Training Workflow

```bash
# 1. Start training
JOB_ID=$(jarvisx-cli training start --config training/config.json --json | jq -r '.job_id')

# 2. Monitor status
jarvisx-cli training status --job-id $JOB_ID

# 3. View logs
jarvisx-cli training logs --job-id $JOB_ID --follow

# 4. Evaluate when complete
jarvisx-cli training evaluate --job-id $JOB_ID

# 5. Deploy to cloud
jarvisx-cli cloud deploy --space my-model --model ./models/trained-model
```

### Business Automation Workflow

```bash
# 1. Add client
jarvisx-cli business client add --name "Acme Corp" --email "contact@acme.com"

# 2. Generate invoice
jarvisx-cli business invoice --client-id 1 --template standard

# 3. Generate monthly report
jarvisx-cli business report --type financial --period monthly

# 4. Export data
jarvisx-cli business export --type invoices --format csv --output invoices.csv
```

### Voice-Enabled Workflow

```bash
# Start interactive voice mode
jarvisx-cli voice interactive

# Say commands naturally:
# - "start training"
# - "system status"
# - "generate invoice"
# - "exit" (to quit)
```

---

## Advanced Features

### JSON Output for Scripting

All commands support `--json` flag for programmatic access:

```bash
# Get status as JSON
STATUS=$(jarvisx-cli status --json)

# Parse with jq
echo $STATUS | jq '.System.OS'
echo $STATUS | jq '.System.Memory.Used'
```

### Command Templates

Create reusable command sequences:

```bash
# Create template
jarvisx-cli template create --name daily-check \
  --commands "system status;system health;cloud status"

# Execute template
jarvisx-cli template execute --name daily-check
```

### Command History

```bash
# View recent commands
jarvisx-cli history list

# Search for specific commands
jarvisx-cli history search "training"

# Export history
jarvisx-cli history export --format csv --days 30
```

### Usage Analytics

```bash
# View analytics summary
jarvisx-cli analytics summary

# Check most used commands
jarvisx-cli analytics commands

# Monitor performance
jarvisx-cli analytics performance
```

---

## Troubleshooting

### Common Issues

**1. Command not found**
```bash
# Verify installation
jarvisx-cli version

# Check PATH
which jarvisx-cli
```

**2. Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

**3. Voice not working**
```bash
# Check TTS/STT availability
jarvisx-cli voice listen --timeout 5

# Install missing dependencies
pip install pyttsx3 gTTS speechrecognition vosk
```

**4. Permission errors**
```bash
# Check file permissions
ls -la ~/.jarvisx/

# Fix permissions if needed
chmod -R 755 ~/.jarvisx/
```

### Getting Help

```bash
# General help
jarvisx-cli --help

# Command-specific help
jarvisx-cli <command> --help

# Interactive help
jarvisx-cli help command <command-name>
jarvisx-cli help examples
jarvisx-cli help quickstart
```

### Debug Mode

Enable verbose output for debugging:

```bash
jarvisx-cli <command> --verbose
```

---

## Best Practices

### 1. Use Configuration Files

Create configuration files for repeated operations:

```json
{
  "training": {
    "config_path": "training/config.json",
    "model_path": "./models/my-model"
  },
  "cloud": {
    "default_space": "my-space",
    "api_key": "your-api-key"
  }
}
```

### 2. Enable Tab Completion

```bash
# Add to your shell profile
eval "$(jarvisx-cli --show-completion bash)"
```

### 3. Use JSON Output for Automation

```bash
# In scripts, use JSON output
RESULT=$(jarvisx-cli status --json)
# Parse with jq or Python
```

### 4. Regular System Maintenance

```bash
# Weekly cleanup
jarvisx-cli system cleanup --logs --cache --temp

# Health check
jarvisx-cli system health --full
```

### 5. Monitor Usage

```bash
# Check analytics regularly
jarvisx-cli analytics summary

# Review command history
jarvisx-cli history stats
```

### 6. Use Templates for Common Workflows

```bash
# Create templates for repeated workflows
jarvisx-cli template create --name deploy \
  --commands "training evaluate;cloud deploy;cloud status"
```

---

## Additional Resources

- **CLI Documentation**: `cli/README.md`
- **Examples**: `examples/`
- **API Reference**: `docs/api/cli_api_reference.md`
- **GitHub Repository**: https://github.com/AsithaLKonara/JarvisX

---

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Use `jarvisx-cli help` for interactive help

---

**Happy automating with JarvisX V2! 🚀**

