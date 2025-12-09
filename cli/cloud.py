"""
Cloud Operations CLI Module
Commands for managing cloud deployments and operations
"""

import typer
import os
from pathlib import Path
from typing import Optional

from cli.base import get_output, get_config
from cli.utils import CLIOutput

app = typer.Typer(name="cloud", help="Cloud operations")


@app.command("connect")
def connect_cloud(
    url: str = typer.Option(..., '--url', '-u', help='Cloud space URL'),
    token: Optional[str] = typer.Option(None, '--token', '-t', help='Authentication token'),
    json_output: bool = typer.Option(False, '--json')
):
    """Connect to a cloud LLM space"""
    output = CLIOutput(json_output=json_output)
    
    # Import cloud client
    try:
        from cloud_llm_client import CloudLLMClient
        
        client = CloudLLMClient(base_url=url)
        if client.is_available():
            output.success(f"Connected to cloud space: {url}")
        else:
            output.error(f"Failed to connect to cloud space: {url}")
            raise typer.Exit(1)
    except Exception as e:
        output.error(f"Error connecting to cloud: {e}")
        raise typer.Exit(1)


@app.command("deploy")
def deploy_cloud(
    space: str = typer.Option(..., '--space', '-s', help='Hugging Face space name'),
    model: Optional[str] = typer.Option(None, '--model', '-m', help='Path to model'),
    hardware: Optional[str] = typer.Option(None, '--hardware', '-h', help='Hardware type (cpu/gpu)'),
    token: Optional[str] = typer.Option(None, '--token', '-t', help='Hugging Face token'),
    json_output: bool = typer.Option(False, '--json')
):
    """Deploy to Hugging Face Space"""
    output = CLIOutput(json_output=json_output)
    
    try:
        # Check for Hugging Face Hub
        try:
            from huggingface_hub import HfApi, create_repo, upload_folder
            import os
        except ImportError:
            output.error("huggingface_hub not installed. Install with: pip install huggingface_hub")
            raise typer.Exit(1)
        
        # Get token
        hf_token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
        if not hf_token:
            output.error("Hugging Face token required. Set HF_TOKEN environment variable or use --token")
            raise typer.Exit(1)
        
        api = HfApi(token=hf_token)
        
        output.info(f"Deploying to space: {space}")
        
        # Create or get space
        try:
            # Try to get existing space
            space_info = api.space_info(space)
            output.info(f"Space exists: {space_info.id}")
        except Exception:
            # Create new space
            output.info("Creating new space...")
            try:
                api.create_repo(
                    repo_id=space,
                    repo_type="space",
                    exist_ok=True
                )
                output.success(f"Space created: {space}")
            except Exception as e:
                output.error(f"Failed to create space: {e}")
                raise typer.Exit(1)
        
        # Upload model if provided
        if model:
            model_path = Path(model)
            if not model_path.exists():
                output.error(f"Model path not found: {model}")
                raise typer.Exit(1)
            
            output.info(f"Uploading model from: {model_path}")
            try:
                if model_path.is_file():
                    api.upload_file(
                        path_or_fileobj=str(model_path),
                        path_in_repo=model_path.name,
                        repo_id=space,
                        repo_type="space",
                        token=hf_token
                    )
                elif model_path.is_dir():
                    upload_folder(
                        folder_path=str(model_path),
                        repo_id=space,
                        repo_type="space",
                        token=hf_token
                    )
                output.success("Model uploaded successfully")
            except Exception as e:
                output.error(f"Failed to upload model: {e}")
                raise typer.Exit(1)
        
        # Update hardware if specified
        if hardware:
            output.info(f"Setting hardware to: {hardware}")
            # Note: Hardware configuration typically requires Space settings API
            # This is a placeholder for the actual implementation
            output.warning("Hardware configuration requires Space settings API access")
        
        output.success(f"Deployment to {space} completed")
        
        if json_output:
            output.print_json({
                "space": space,
                "status": "deployed",
                "model_uploaded": model is not None
            })
        
    except Exception as e:
        output.error(f"Error deploying to cloud: {e}")
        raise typer.Exit(1)


@app.command("status")
def cloud_status(
    space: str = typer.Option(..., '--space', '-s', help='Hugging Face space name'),
    token: Optional[str] = typer.Option(None, '--token', '-t', help='Hugging Face token'),
    json_output: bool = typer.Option(False, '--json')
):
    """Check cloud space status"""
    output = CLIOutput(json_output=json_output)
    
    try:
        try:
            from huggingface_hub import HfApi
            import os
        except ImportError:
            output.error("huggingface_hub not installed. Install with: pip install huggingface_hub")
            raise typer.Exit(1)
        
        # Get token
        hf_token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
        api = HfApi(token=hf_token)
        
        output.info(f"Checking status for space: {space}")
        
        try:
            space_info = api.space_info(space)
            
            status_data = {
                "Space ID": space_info.id,
                "Status": getattr(space_info, 'runtime', {}).get('stage', 'unknown'),
                "URL": f"https://huggingface.co/spaces/{space}",
            }
            
            # Try to get runtime info
            try:
                runtime = getattr(space_info, 'runtime', {})
                if runtime:
                    status_data["Runtime"] = runtime.get('stage', 'unknown')
                    status_data["Hardware"] = runtime.get('hardware', 'unknown')
            except:
                pass
            
            if json_output:
                output.print_json(status_data)
            else:
                output.print_dict(status_data, title="Space Status")
                output.success("Space status retrieved successfully")
        
        except Exception as e:
            output.error(f"Failed to get space status: {e}")
            raise typer.Exit(1)
        
    except Exception as e:
        output.error(f"Error checking space status: {e}")
        raise typer.Exit(1)


@app.command("test")
def test_cloud(
    endpoint: str = typer.Option('/generate', '--endpoint', '-e', help='API endpoint'),
    prompt: str = typer.Option('Hello', '--prompt', '-p', help='Test prompt'),
    json_output: bool = typer.Option(False, '--json')
):
    """Test cloud API endpoint"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from cloud_llm_client import CloudLLMClient
        
        client = CloudLLMClient()
        if not client.is_available():
            output.error("Cloud LLM not available. Set CLOUD_LLM_URL environment variable.")
            raise typer.Exit(1)
        
        response = client.generate(prompt, max_new_tokens=50)
        output.success("Cloud API test successful")
        output.info(f"Response: {response[:100]}...")
    except Exception as e:
        output.error(f"Cloud API test failed: {e}")
        raise typer.Exit(1)


@app.command("monitor")
def monitor_cloud(
    space: Optional[str] = typer.Option(None, '--space', '-s', help='Hugging Face space name'),
    metrics: Optional[str] = typer.Option('latency,errors', '--metrics', '-m', help='Comma-separated metrics'),
    interval: int = typer.Option(5, '--interval', '-i', help='Update interval in seconds'),
    json_output: bool = typer.Option(False, '--json')
):
    """Monitor cloud space metrics"""
    output = CLIOutput(json_output=json_output)
    
    try:
        import time
        from cloud_llm_client import CloudLLMClient
        
        if not space:
            # Try to get from environment
            cloud_url = os.getenv("CLOUD_LLM_URL", "")
            if cloud_url:
                output.info(f"Using cloud URL from environment: {cloud_url}")
            else:
                output.error("Space name or CLOUD_LLM_URL required")
                raise typer.Exit(1)
        else:
            cloud_url = f"https://huggingface.co/spaces/{space}"
        
        client = CloudLLMClient(base_url=cloud_url)
        
        if not client.is_available():
            output.error("Cloud space is not available")
            raise typer.Exit(1)
        
        metric_list = [m.strip() for m in metrics.split(',')] if metrics else []
        
        output.info(f"Monitoring metrics: {', '.join(metric_list)}")
        output.info(f"Update interval: {interval} seconds")
        output.info("Press Ctrl+C to stop")
        
        try:
            import time
            request_count = 0
            error_count = 0
            total_latency = 0.0
            
            while True:
                start_time = time.time()
                
                try:
                    # Test request
                    response = client.generate("test", max_new_tokens=10)
                    request_count += 1
                    latency = (time.time() - start_time) * 1000  # Convert to ms
                    total_latency += latency
                    
                    if json_output:
                        output.print_json({
                            "timestamp": time.time(),
                            "requests": request_count,
                            "errors": error_count,
                            "latency_ms": latency,
                            "avg_latency_ms": total_latency / request_count if request_count > 0 else 0
                        })
                    else:
                        avg_latency = total_latency / request_count if request_count > 0 else 0
                        metrics_data = {
                            "Requests": request_count,
                            "Errors": error_count,
                            "Current Latency": f"{latency:.2f} ms",
                            "Avg Latency": f"{avg_latency:.2f} ms"
                        }
                        output.print_dict(metrics_data, title="Cloud Metrics")
                        
                except Exception as e:
                    error_count += 1
                    output.warning(f"Request failed: {e}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            output.info("\nMonitoring stopped")
        
    except Exception as e:
        output.error(f"Error monitoring cloud: {e}")
        raise typer.Exit(1)


@app.command("logs")
def cloud_logs(
    space: str = typer.Option(..., '--space', '-s', help='Hugging Face space name'),
    tail: int = typer.Option(100, '--tail', '-n', help='Number of lines to show'),
    follow: bool = typer.Option(False, '--follow', '-f', help='Follow log output'),
    token: Optional[str] = typer.Option(None, '--token', '-t', help='Hugging Face token'),
    json_output: bool = typer.Option(False, '--json')
):
    """View cloud space logs"""
    output = CLIOutput(json_output=json_output)
    
    try:
        try:
            from huggingface_hub import HfApi
            import os
        except ImportError:
            output.error("huggingface_hub not installed. Install with: pip install huggingface_hub")
            raise typer.Exit(1)
        
        # Get token
        hf_token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
        api = HfApi(token=hf_token)
        
        output.info(f"Fetching logs for space: {space}")
        
        try:
            # Get space logs
            # Note: Hugging Face API may have different methods for logs
            # This is a placeholder implementation
            space_info = api.space_info(space)
            
            # Try to get logs via API
            # Note: Actual log retrieval depends on HF API capabilities
            output.info("Retrieving logs...")
            
            # For now, provide instructions
            if not json_output:
                output.info(f"Space logs URL: https://huggingface.co/spaces/{space}/logs")
                output.warning("Direct log API access may require Space owner permissions")
                output.info("You can view logs in the Hugging Face Space dashboard")
            
            if json_output:
                output.print_json({
                    "space": space,
                    "logs_url": f"https://huggingface.co/spaces/{space}/logs",
                    "note": "Logs available via Space dashboard"
                })
        
        except Exception as e:
            output.error(f"Failed to retrieve logs: {e}")
            output.info(f"View logs at: https://huggingface.co/spaces/{space}/logs")
            raise typer.Exit(1)
        
    except Exception as e:
        output.error(f"Error viewing logs: {e}")
        raise typer.Exit(1)

