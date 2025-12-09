# JarvisX V2 CLI API Reference

Complete API reference for all CLI commands.

## Table of Contents

- [Training Commands](#training-commands)
- [Cloud Commands](#cloud-commands)
- [System Commands](#system-commands)
- [Business Commands](#business-commands)
- [Workflow Commands](#workflow-commands)
- [Model Commands](#model-commands)
- [Config Commands](#config-commands)
- [Voice Commands](#voice-commands)
- [Common Options](#common-options)

---

## Training Commands

### `training start`

Start a new training job.

**Usage:**
```bash
jarvisx-cli training start --config <path> [OPTIONS]
```

**Options:**
- `--config, -c` (required): Path to training config file
- `--epochs, -e`: Number of training epochs (overrides config)
- `--output-dir, -o`: Output directory (overrides config)
- `--json`: Output in JSON format
- `--voice`: Enable voice output

**Example:**
```bash
jarvisx-cli training start --config training/config.json --epochs 10
```

**Returns:**
```json
{
  "job_id": "uuid-string",
  "status": "pending"
}
```

---

### `training status`

Check training job status.

**Usage:**
```bash
jarvisx-cli training status --job-id <id> [OPTIONS]
```

**Options:**
- `--job-id, -j` (required): Training job ID
- `--json`: Output in JSON format
- `--voice`: Enable voice output

**Example:**
```bash
jarvisx-cli training status --job-id abc123
```

---

### `training logs`

View training job logs.

**Usage:**
```bash
jarvisx-cli training logs --job-id <id> [OPTIONS]
```

**Options:**
- `--job-id, -j` (required): Training job ID
- `--follow, -f`: Follow log output (like tail -f)
- `--level, -l`: Filter by log level (INFO/WARNING/ERROR)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli training logs --job-id abc123 --follow --level ERROR
```

---

### `training list`

List all training jobs.

**Usage:**
```bash
jarvisx-cli training list [OPTIONS]
```

**Options:**
- `--status, -s`: Filter by status (pending/running/completed/failed/cancelled)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli training list --status running
```

---

### `training cancel`

Cancel a running training job.

**Usage:**
```bash
jarvisx-cli training cancel --job-id <id> [OPTIONS]
```

**Options:**
- `--job-id, -j` (required): Training job ID
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli training cancel --job-id abc123
```

---

### `training evaluate`

Evaluate a trained model.

**Usage:**
```bash
jarvisx-cli training evaluate --model <path> [OPTIONS]
```

**Options:**
- `--model, -m` (required): Path to model
- `--dataset, -d`: Path to evaluation dataset
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli training evaluate --model output/model --dataset test_data.json
```

---

## Cloud Commands

### `cloud connect`

Connect to a cloud LLM space.

**Usage:**
```bash
jarvisx-cli cloud connect --url <url> [OPTIONS]
```

**Options:**
- `--url, -u` (required): Cloud space URL
- `--token, -t`: Authentication token
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli cloud connect --url https://user-space.hf.space
```

---

### `cloud deploy`

Deploy model to Hugging Face Space.

**Usage:**
```bash
jarvisx-cli cloud deploy --space <name> [OPTIONS]
```

**Options:**
- `--space, -s` (required): Hugging Face space name
- `--model, -m`: Path to model
- `--hardware, -h`: Hardware type (cpu/gpu)
- `--token, -t`: Hugging Face token
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli cloud deploy --space user/jarvis-model --model output/
```

---

### `cloud status`

Check cloud space status.

**Usage:**
```bash
jarvisx-cli cloud status --space <name> [OPTIONS]
```

**Options:**
- `--space, -s` (required): Hugging Face space name
- `--token, -t`: Hugging Face token
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli cloud status --space user/jarvis-model
```

---

### `cloud test`

Test cloud API endpoint.

**Usage:**
```bash
jarvisx-cli cloud test [OPTIONS]
```

**Options:**
- `--endpoint, -e`: API endpoint (default: /generate)
- `--prompt, -p`: Test prompt (default: Hello)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli cloud test --prompt "What is AI?"
```

---

### `cloud monitor`

Monitor cloud space metrics.

**Usage:**
```bash
jarvisx-cli cloud monitor [OPTIONS]
```

**Options:**
- `--space, -s`: Hugging Face space name
- `--metrics, -m`: Comma-separated metrics (default: latency,errors)
- `--interval, -i`: Update interval in seconds (default: 5)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli cloud monitor --space user/jarvis-model --interval 10
```

---

### `cloud logs`

View cloud space logs.

**Usage:**
```bash
jarvisx-cli cloud logs --space <name> [OPTIONS]
```

**Options:**
- `--space, -s` (required): Hugging Face space name
- `--tail, -n`: Number of lines to show (default: 100)
- `--follow, -f`: Follow log output
- `--token, -t`: Hugging Face token
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli cloud logs --space user/jarvis-model --tail 50
```

---

## System Commands

### `system status`

Show system status.

**Usage:**
```bash
jarvisx-cli system status [OPTIONS]
```

**Options:**
- `--json`: Output in JSON format
- `--voice`: Enable voice output

**Example:**
```bash
jarvisx-cli system status --voice
```

---

### `system health`

Run system health check.

**Usage:**
```bash
jarvisx-cli system health [OPTIONS]
```

**Options:**
- `--full`: Show full health report
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli system health --full
```

---

### `system optimize`

Optimize system resources.

**Usage:**
```bash
jarvisx-cli system optimize [OPTIONS]
```

**Options:**
- `--auto`: Auto-apply optimizations
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli system optimize --auto
```

---

### `system logs`

View system logs.

**Usage:**
```bash
jarvisx-cli system logs [OPTIONS]
```

**Options:**
- `--tail, -n`: Number of lines to show (default: 100)
- `--filter, -f`: Filter by log level (INFO/WARNING/ERROR)
- `--search, -s`: Search for keyword
- `--export, -e`: Export logs to file
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli system logs --tail 50 --filter ERROR --search "training"
```

---

### `system cleanup`

Clean up system files.

**Usage:**
```bash
jarvisx-cli system cleanup [OPTIONS]
```

**Options:**
- `--logs`: Clean up old logs
- `--cache`: Clean up cache
- `--temp`: Clean up temp files
- `--days, -d`: Keep files newer than N days (default: 7)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli system cleanup --logs --cache --days 30
```

---

### `system info`

Show system information.

**Usage:**
```bash
jarvisx-cli system info [OPTIONS]
```

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli system info
```

---

## Business Commands

### `business invoice`

Generate an invoice.

**Usage:**
```bash
jarvisx-cli business invoice --client-id <id> [OPTIONS]
```

**Options:**
- `--client-id, -c` (required): Client ID
- `--template, -t`: Invoice template (default: standard)
- `--output, -o`: Output path
- `--items`: Items as JSON string
- `--tax-rate`: Tax rate (0.0-1.0)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli business invoice --client-id 1 --items '[{"description":"Service","amount":100.0}]'
```

---

### `business client`

Manage clients.

**Usage:**
```bash
jarvisx-cli business client <action> [OPTIONS]
```

**Actions:**
- `list`: List all clients
- `add`: Add new client
- `get`: Get client by ID

**Options:**
- `--id`: Client ID (for get action)
- `--name`: Client name (for add)
- `--email`: Client email (for add)
- `--phone`: Client phone (for add)
- `--company`: Client company (for add)
- `--search, -s`: Search term (for list)
- `--format, -f`: Output format (table/json/csv)
- `--json`: Output in JSON format

**Examples:**
```bash
jarvisx-cli business client list
jarvisx-cli business client add --name "John Doe" --email "john@example.com"
jarvisx-cli business client get --id 1
```

---

### `business report`

Generate business report.

**Usage:**
```bash
jarvisx-cli business report --type <type> [OPTIONS]
```

**Options:**
- `--type, -t` (required): Report type (financial/summary)
- `--period, -p`: Period (monthly/yearly) (default: monthly)
- `--format, -f`: Output format (json/txt) (default: json)
- `--output, -o`: Output path
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli business report --type financial --period monthly --output report.json
```

---

### `business task`

Manage scheduled tasks.

**Usage:**
```bash
jarvisx-cli business task <action> [OPTIONS]
```

**Actions:**
- `schedule`: Schedule a task
- `list`: List all tasks
- `cancel`: Cancel a task

**Options:**
- `--name`: Task name (for schedule)
- `--cron`: Cron expression (for schedule)
- `--id`: Task ID (for cancel)
- `--priority, -p`: Task priority (low/medium/high)
- `--description, -d`: Task description
- `--json`: Output in JSON format

**Examples:**
```bash
jarvisx-cli business task schedule --name "Daily Backup" --cron "0 0 * * *"
jarvisx-cli business task list
jarvisx-cli business task cancel --id 1
```

---

### `business export`

Export business data.

**Usage:**
```bash
jarvisx-cli business export --type <type> --output <path> [OPTIONS]
```

**Options:**
- `--type, -t` (required): Data type (invoices/clients)
- `--format, -f`: Output format (csv/json) (default: csv)
- `--output, -o` (required): Output path
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli business export --type invoices --format csv --output invoices.csv
```

---

## Workflow Commands

### `workflow list`

List available workflows.

**Usage:**
```bash
jarvisx-cli workflow list [OPTIONS]
```

**Options:**
- `--category, -c`: Filter by category
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli workflow list --category automation
```

---

### `workflow execute`

Execute a workflow.

**Usage:**
```bash
jarvisx-cli workflow execute --id <id> [OPTIONS]
```

**Options:**
- `--id, -i` (required): Workflow ID
- `--input`: Input data as JSON
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli workflow execute --id wf-123 --input '{"key":"value"}'
```

---

### `workflow create`

Create a new workflow.

**Usage:**
```bash
jarvisx-cli workflow create [OPTIONS]
```

**Options:**
- `--from-template`: Template name
- `--name`: Workflow name
- `--file, -f`: Workflow JSON file
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli workflow create --file workflow.json --name "My Workflow"
```

---

### `workflow status`

Check workflow execution status.

**Usage:**
```bash
jarvisx-cli workflow status --execution-id <id> [OPTIONS]
```

**Options:**
- `--execution-id, -e` (required): Execution ID
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli workflow status --execution-id exec-123
```

---

### `workflow analytics`

Show workflow analytics.

**Usage:**
```bash
jarvisx-cli workflow analytics [OPTIONS]
```

**Options:**
- `--format, -f`: Output format (table/json) (default: table)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli workflow analytics --format json
```

---

### `workflow recommend`

Get workflow recommendations.

**Usage:**
```bash
jarvisx-cli workflow recommend [OPTIONS]
```

**Options:**
- `--context`: Context as JSON
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli workflow recommend --context '{"goals":["automation"]}'
```

---

## Model Commands

### `model list`

List available models.

**Usage:**
```bash
jarvisx-cli model list [OPTIONS]
```

**Options:**
- `--local`: Show local models only
- `--remote`: Show remote models only
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli model list --local
```

---

### `model load`

Load a model.

**Usage:**
```bash
jarvisx-cli model load --name <name> [OPTIONS]
```

**Options:**
- `--name, -n` (required): Model name
- `--version, -v`: Model version
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli model load --name test-model
```

---

### `model compare`

Compare two models.

**Usage:**
```bash
jarvisx-cli model compare --model-a <name> --model-b <name> [OPTIONS]
```

**Options:**
- `--model-a, -a` (required): First model name
- `--model-b, -b` (required): Second model name
- `--metrics, -m`: Comma-separated metrics (default: size,latency)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli model compare --model-a model-v1 --model-b model-v2
```

---

### `model upload`

Upload model to Hugging Face.

**Usage:**
```bash
jarvisx-cli model upload --path <path> --repo <repo> [OPTIONS]
```

**Options:**
- `--path, -p` (required): Local model path
- `--repo, -r` (required): Hugging Face repository
- `--version, -v`: Model version tag
- `--token, -t`: Hugging Face token
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli model upload --path models/my-model --repo user/my-model
```

---

### `model info`

Show model information.

**Usage:**
```bash
jarvisx-cli model info --name <name> [OPTIONS]
```

**Options:**
- `--name, -n` (required): Model name
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli model info --name test-model
```

---

### `model test`

Test a model with a prompt.

**Usage:**
```bash
jarvisx-cli model test --name <name> [OPTIONS]
```

**Options:**
- `--name, -n` (required): Model name
- `--prompt, -p`: Test prompt (default: Hello)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli model test --name test-model --prompt "What is AI?"
```

---

## Config Commands

### `config show`

Show configuration.

**Usage:**
```bash
jarvisx-cli config show [OPTIONS]
```

**Options:**
- `--format`: Output format (json/yaml)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli config show --format json
```

---

### `config get`

Get configuration value.

**Usage:**
```bash
jarvisx-cli config get <key> [OPTIONS]
```

**Arguments:**
- `key` (required): Configuration key

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli config get log_level
```

---

### `config set`

Set configuration value.

**Usage:**
```bash
jarvisx-cli config set <key> <value> [OPTIONS]
```

**Arguments:**
- `key` (required): Configuration key
- `value` (required): Configuration value

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli config set log_level DEBUG
```

---

### `config validate`

Validate configuration.

**Usage:**
```bash
jarvisx-cli config validate [OPTIONS]
```

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli config validate
```

---

## Voice Commands

### `voice listen`

Listen for voice input.

**Usage:**
```bash
jarvisx-cli voice listen [OPTIONS]
```

**Options:**
- `--timeout, -t`: Listening timeout in seconds (default: 5)
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli voice listen --timeout 10
```

---

### `voice speak`

Convert text to speech.

**Usage:**
```bash
jarvisx-cli voice speak <text> [OPTIONS]
```

**Arguments:**
- `text` (required): Text to speak

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli voice speak "Training completed successfully"
```

---

### `voice interactive`

Interactive voice mode.

**Usage:**
```bash
jarvisx-cli voice interactive [OPTIONS]
```

**Options:**
- `--wake-word, -w`: Wake word to activate
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli voice interactive --wake-word "Hey Jarvis"
```

---

### `voice command`

Execute a voice command.

**Usage:**
```bash
jarvisx-cli voice command <command_text> [OPTIONS]
```

**Arguments:**
- `command_text` (required): Voice command text

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
jarvisx-cli voice command "start training"
```

---

## Common Options

All commands support these common options:

- `--verbose, -v`: Enable verbose output
- `--json`: Output in JSON format (useful for scripting)
- `--config`: Path to configuration file
- `--voice`: Enable voice output (TTS)

**Example:**
```bash
jarvisx-cli system status --verbose --json --voice
```

---

## Exit Codes

- `0`: Success
- `1`: General error
- `130`: User interrupt (Ctrl+C)

---

## JSON Output Format

When using `--json`, commands return structured JSON:

```json
{
  "status": "success",
  "data": {...},
  "message": "Operation completed"
}
```

---

## Error Handling

All commands provide clear error messages:

```bash
jarvisx-cli training status --job-id invalid
# Error: Job not found: invalid
```

Errors are also returned in JSON format when using `--json`:

```json
{
  "status": "error",
  "message": "Job not found: invalid"
}
```

