"""
Training CLI Module
Commands for managing model training operations
"""

import typer
import json
from pathlib import Path
from typing import Optional
import subprocess
import threading

from cli.base import get_output, get_config, BaseCommand
from cli.utils import CLIOutput
from cli.training_utils import (
    TrainingJobManager,
    TrainingJobStatus,
    load_training_config,
    validate_training_config
)

app = typer.Typer(name="training", help="Training operations")


@app.command("start")
def start_training(
    config: str = typer.Option(..., '--config', '-c', help='Path to training config file'),
    epochs: Optional[int] = typer.Option(None, '--epochs', '-e', help='Number of training epochs'),
    output_dir: Optional[str] = typer.Option(None, '--output-dir', '-o', help='Output directory'),
    json_output: bool = typer.Option(False, '--json')
):
    """Start a training job"""
    output = CLIOutput(json_output=json_output)
    
    # Validate config file
    config_path = Path(config)
    if not config_path.exists():
        output.error(f"Config file not found: {config}")
        raise typer.Exit(1)
    
    try:
        # Load and validate config
        training_config = load_training_config(config)
        if not validate_training_config(training_config):
            output.error("Invalid training configuration")
            raise typer.Exit(1)
        
        # Override config values if provided
        if epochs:
            training_config['training_config']['num_epochs'] = epochs
        if output_dir:
            training_config['output_dir'] = output_dir
        
        # Create job manager
        job_manager = TrainingJobManager()
        
        # Create job
        job_id = job_manager.create_job(
            config_path=str(config_path),
            output_dir=training_config.get('output_dir'),
            epochs=training_config['training_config'].get('num_epochs')
        )
        
        output.success(f"Training job created: {job_id}")
        output.info(f"Config: {config}")
        output.info(f"Output directory: {training_config.get('output_dir', 'default')}")
        output.info(f"Epochs: {training_config['training_config'].get('num_epochs', 'default')}")
        
        if json_output:
            output.print_json({"job_id": job_id, "status": "pending"})
        else:
            output.info(f"\nTo check status: jarvisx-cli training status --job-id {job_id}")
            output.info(f"To view logs: jarvisx-cli training logs --job-id {job_id}")
            output.warning("\nNote: Actual training execution requires integration with training module")
            output.warning("Use the training notebook or training scripts for full training execution")
        
    except Exception as e:
        output.error(f"Error starting training job: {e}")
        raise typer.Exit(1)


@app.command("status")
def training_status(
    job_id: str = typer.Option(..., '--job-id', '-j', help='Training job ID'),
    json_output: bool = typer.Option(False, '--json')
):
    """Check training job status"""
    output = CLIOutput(json_output=json_output)
    
    try:
        job_manager = TrainingJobManager()
        job = job_manager.get_job(job_id)
        
        if not job:
            output.error(f"Job not found: {job_id}")
            raise typer.Exit(1)
        
        if json_output:
            output.print_json(job)
        else:
            status_emoji = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "failed": "❌",
                "cancelled": "🚫"
            }
            emoji = status_emoji.get(job['status'], "❓")
            
            output.print_dict({
                "Job ID": job['job_id'],
                "Status": f"{emoji} {job['status']}",
                "Config": job['config_path'],
                "Output Directory": job['output_dir'] or "Not set",
                "Epochs": job['epochs'] or "Not set",
                "Created": job['created_at'],
                "Started": job['started_at'] or "Not started",
                "Completed": job['completed_at'] or "Not completed",
                "Progress": f"{job['progress'] * 100:.1f}%" if job['progress'] else "0%"
            }, title="Training Job Status")
            
            if job['error_message']:
                output.error(f"Error: {job['error_message']}")
    except Exception as e:
        output.error(f"Error checking job status: {e}")
        raise typer.Exit(1)


@app.command("logs")
def training_logs(
    job_id: str = typer.Option(..., '--job-id', '-j', help='Training job ID'),
    follow: bool = typer.Option(False, '--follow', '-f', help='Follow log output'),
    level: Optional[str] = typer.Option(None, '--level', '-l', help='Filter by log level (INFO/WARNING/ERROR)'),
    json_output: bool = typer.Option(False, '--json')
):
    """View training job logs"""
    output = CLIOutput(json_output=json_output)
    
    try:
        job_manager = TrainingJobManager()
        job = job_manager.get_job(job_id)
        
        if not job:
            output.error(f"Job not found: {job_id}")
            raise typer.Exit(1)
        
        log_file = job_manager.get_log_file(job_id)
        
        if not log_file or not log_file.exists():
            output.warning(f"No log file found for job {job_id}")
            output.info("Logs will be available once training starts")
            return
        
        # Filter log levels
        log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL']
        filter_level = level.upper() if level else None
        
        if filter_level and filter_level not in log_levels:
            output.error(f"Invalid log level: {level}. Valid levels: {', '.join(log_levels)}")
            raise typer.Exit(1)
        
        def filter_log_line(line: str) -> bool:
            """Filter log line by level"""
            if not filter_level:
                return True
            return filter_level in line.upper()
        
        def read_logs():
            """Read and display logs"""
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    if follow:
                        # Follow mode: tail and continue reading
                        import time
                        # Read existing content
                        lines = f.readlines()
                        for line in lines:
                            if filter_log_line(line):
                                if json_output:
                                    output.print_json({"log": line.rstrip()})
                                else:
                                    print(line.rstrip())
                        
                        # Follow new lines
                        while True:
                            line = f.readline()
                            if line:
                                if filter_log_line(line):
                                    if json_output:
                                        output.print_json({"log": line.rstrip()})
                                    else:
                                        print(line.rstrip())
                            else:
                                time.sleep(0.1)
                    else:
                        # Read all logs
                        lines = f.readlines()
                        filtered_lines = [line for line in lines if filter_log_line(line)]
                        
                        if json_output:
                            output.print_json({"logs": [line.rstrip() for line in filtered_lines]})
                        else:
                            for line in filtered_lines:
                                print(line.rstrip())
            except KeyboardInterrupt:
                if follow:
                    output.info("\nStopped following logs")
            except Exception as e:
                output.error(f"Error reading logs: {e}")
                raise typer.Exit(1)
        
        if json_output:
            output.info(f"Reading logs from: {log_file}")
        else:
            output.info(f"Logs for job {job_id}:")
            output.info(f"Log file: {log_file}")
            if filter_level:
                output.info(f"Filter: {filter_level}")
            if follow:
                output.info("Following logs (Ctrl+C to stop)...")
            print()
        
        read_logs()
        
    except KeyboardInterrupt:
        if follow:
            output.info("\nStopped following logs")
    except Exception as e:
        output.error(f"Error viewing logs: {e}")
        raise typer.Exit(1)


@app.command("list")
def list_training_jobs(
    status: Optional[str] = typer.Option(None, '--status', '-s', help='Filter by status'),
    json_output: bool = typer.Option(False, '--json')
):
    """List all training jobs"""
    output = CLIOutput(json_output=json_output)
    
    try:
        job_manager = TrainingJobManager()
        
        filter_status = None
        if status:
            try:
                filter_status = TrainingJobStatus(status.lower())
            except ValueError:
                output.error(f"Invalid status: {status}")
                output.info("Valid statuses: pending, running, completed, failed, cancelled")
                raise typer.Exit(1)
        
        jobs = job_manager.list_jobs(filter_status)
        
        if json_output:
            output.print_json(jobs)
        else:
            if jobs:
                table_data = []
                for job in jobs:
                    status_emoji = {
                        "pending": "⏳",
                        "running": "🔄",
                        "completed": "✅",
                        "failed": "❌",
                        "cancelled": "🚫"
                    }
                    emoji = status_emoji.get(job['status'], "❓")
                    table_data.append([
                        job['job_id'][:8] + "...",
                        f"{emoji} {job['status']}",
                        Path(job['config_path']).name if job['config_path'] else "N/A",
                        f"{job['progress'] * 100:.1f}%" if job['progress'] else "0%",
                        job['created_at'][:19] if job['created_at'] else "N/A"
                    ])
                output.print_table(
                    table_data,
                    ['Job ID', 'Status', 'Config', 'Progress', 'Created'],
                    title="Training Jobs"
                )
            else:
                output.info("No training jobs found")
    except Exception as e:
        output.error(f"Error listing jobs: {e}")
        raise typer.Exit(1)


@app.command("cancel")
def cancel_training(
    job_id: str = typer.Option(..., '--job-id', '-j', help='Training job ID'),
    json_output: bool = typer.Option(False, '--json')
):
    """Cancel a training job"""
    output = CLIOutput(json_output=json_output)
    
    try:
        job_manager = TrainingJobManager()
        job = job_manager.get_job(job_id)
        
        if not job:
            output.error(f"Job not found: {job_id}")
            raise typer.Exit(1)
        
        if job['status'] in ['completed', 'failed', 'cancelled']:
            output.warning(f"Job {job_id} is already {job['status']}")
            if json_output:
                output.print_json({"job_id": job_id, "status": job['status'], "message": "Job already terminated"})
            return
        
        # Try to kill the process if running
        process_id = job_manager.get_process_id(job_id)
        if process_id:
            try:
                import psutil
                import os
                
                # Get process
                try:
                    process = psutil.Process(process_id)
                    if process.is_running():
                        # Kill process tree
                        for child in process.children(recursive=True):
                            try:
                                child.kill()
                            except psutil.NoSuchProcess:
                                pass
                        
                        try:
                            process.kill()
                            output.info(f"Terminated process {process_id}")
                        except psutil.NoSuchProcess:
                            pass
                except psutil.NoSuchProcess:
                    output.info(f"Process {process_id} not found (may have already terminated)")
            except ImportError:
                output.warning("psutil not available. Install with: pip install psutil")
                # Try using os.kill as fallback
                try:
                    import signal
                    os.kill(process_id, signal.SIGTERM)
                    output.info(f"Sent termination signal to process {process_id}")
                except (ProcessLookupError, OSError):
                    pass
        
        # Update job status
        job_manager.update_job_status(
            job_id,
            TrainingJobStatus.CANCELLED,
            error_message="Cancelled by user"
        )
        
        output.success(f"Training job {job_id} cancelled")
        
        if json_output:
            updated_job = job_manager.get_job(job_id)
            output.print_json(updated_job)
        
    except Exception as e:
        output.error(f"Error cancelling job: {e}")
        raise typer.Exit(1)


@app.command("evaluate")
def evaluate_model(
    model: str = typer.Option(..., '--model', '-m', help='Path to model'),
    dataset: Optional[str] = typer.Option(None, '--dataset', '-d', help='Path to evaluation dataset'),
    json_output: bool = typer.Option(False, '--json')
):
    """Evaluate a trained model"""
    output = CLIOutput(json_output=json_output)
    
    try:
        model_path = Path(model)
        if not model_path.exists():
            output.error(f"Model path not found: {model}")
            raise typer.Exit(1)
        
        output.info(f"Loading model from: {model_path}")
        
        # Try to load model using core model loader
        try:
            from core.lora_model_loader import LoRAModelLoader
            
            loader = LoRAModelLoader()
            loaded_model = loader.load_model(str(model_path))
            
            if loaded_model:
                output.success("Model loaded successfully")
            else:
                output.warning("Model loader returned None, attempting direct evaluation")
        except ImportError:
            output.warning("LoRAModelLoader not available, using basic evaluation")
        except Exception as e:
            output.warning(f"Error loading with LoRAModelLoader: {e}, using basic evaluation")
        
        # Basic evaluation metrics
        metrics = {
            "model_path": str(model_path),
            "model_size": _get_model_size(model_path),
            "evaluation_status": "completed"
        }
        
        # If dataset provided, try to evaluate
        if dataset:
            dataset_path = Path(dataset)
            if not dataset_path.exists():
                output.warning(f"Dataset not found: {dataset}, skipping dataset evaluation")
            else:
                output.info(f"Evaluating on dataset: {dataset_path}")
                try:
                    # Try to load and evaluate dataset
                    import json
                    with open(dataset_path, 'r') as f:
                        dataset_data = json.load(f)
                    
                    # Basic metrics
                    if isinstance(dataset_data, dict) and 'examples' in dataset_data:
                        num_examples = len(dataset_data['examples'])
                        metrics["dataset_examples"] = num_examples
                        metrics["dataset_path"] = str(dataset_path)
                        output.info(f"Dataset contains {num_examples} examples")
                    
                    # Note: Full evaluation would require running the model on the dataset
                    # This is a placeholder that can be extended
                    metrics["evaluation_note"] = "Full evaluation requires model inference on dataset"
                    
                except Exception as e:
                    output.warning(f"Error evaluating dataset: {e}")
                    metrics["dataset_error"] = str(e)
        
        # Display results
        if json_output:
            output.print_json(metrics)
        else:
            output.print_dict(metrics, title="Model Evaluation Results")
            output.info("\nNote: For full evaluation with loss/accuracy metrics, integrate with training module")
        
    except Exception as e:
        output.error(f"Error evaluating model: {e}")
        raise typer.Exit(1)


def _get_model_size(model_path: Path) -> str:
    """Calculate total size of model directory"""
    try:
        total_size = 0
        if model_path.is_file():
            total_size = model_path.stat().st_size
        elif model_path.is_dir():
            for file_path in model_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        
        # Format size
        from cli.utils import format_file_size
        return format_file_size(total_size)
    except Exception:
        return "Unknown"

