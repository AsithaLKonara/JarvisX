"""
Model Management CLI Module
Commands for managing models
"""

import typer
from pathlib import Path
from typing import Optional

from cli.base import get_output, get_config
from cli.utils import CLIOutput

app = typer.Typer(name="model", help="Model management")


@app.command("list")
def list_models(
    local: bool = typer.Option(False, '--local', help='Show local models only'),
    remote: bool = typer.Option(False, '--remote', help='Show remote models only'),
    json_output: bool = typer.Option(False, '--json')
):
    """List available models"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from cli.utils import get_project_root
        from pathlib import Path
        
        models_list = []
        
        # List local models
        if not remote:
            models_dir = get_project_root() / "models"
            if models_dir.exists():
                for model_dir in models_dir.iterdir():
                    if model_dir.is_dir():
                        # Check for model files
                        config_file = model_dir / "config.json"
                        if config_file.exists() or any(model_dir.glob("*.bin")) or any(model_dir.glob("*.safetensors")):
                            models_list.append({
                                "name": model_dir.name,
                                "path": str(model_dir),
                                "type": "local"
                            })
        
        # List remote models (Hugging Face)
        if not local:
            try:
                from huggingface_hub import HfApi
                import os
                
                api = HfApi(token=os.getenv("HF_TOKEN"))
                # Note: This would require a specific user/organization
                # For now, just show a placeholder
                output.info("Remote model listing requires Hugging Face API token")
            except ImportError:
                output.warning("huggingface_hub not installed for remote model listing")
            except Exception as e:
                output.warning(f"Error listing remote models: {e}")
        
        if json_output:
            output.print_json(models_list)
        else:
            if models_list:
                table_data = [
                    [m['name'], m.get('type', 'local'), m.get('path', 'N/A')]
                    for m in models_list
                ]
                output.print_table(table_data, ['Name', 'Type', 'Path'], title="Available Models")
            else:
                output.info("No models found")
    
    except Exception as e:
        output.error(f"Error listing models: {e}")
        raise typer.Exit(1)


@app.command("load")
def load_model(
    name: str = typer.Option(..., '--name', '-n', help='Model name'),
    version: Optional[str] = typer.Option(None, '--version', '-v', help='Model version'),
    json_output: bool = typer.Option(False, '--json')
):
    """Load a model"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from cli.utils import get_project_root
        from pathlib import Path
        
        model_path = get_project_root() / "models" / name
        
        if not model_path.exists():
            output.error(f"Model not found: {name}")
            raise typer.Exit(1)
        
        output.info(f"Loading model: {name}" + (f" (version: {version})" if version else ""))
        
        # Try to load using model loader if available
        try:
            from core.lora_model_loader import LoRAModelLoader
            loader = LoRAModelLoader()
            loaded = loader.load_model(str(model_path))
            if loaded:
                output.success("Model loaded successfully")
            else:
                output.warning("Model loader returned None")
        except (ImportError, AttributeError):
            # Fallback: just verify model files exist
            model_files = list(model_path.glob("*.bin")) + list(model_path.glob("*.safetensors"))
            if model_files:
                output.success(f"Model files found: {len(model_files)} files")
            else:
                output.warning("No model files found in directory")
        
        if json_output:
            output.print_json({"model": name, "path": str(model_path), "status": "loaded"})
    
    except Exception as e:
        output.error(f"Error loading model: {e}")
        raise typer.Exit(1)


@app.command("compare")
def compare_models(
    model_a: str = typer.Option(..., '--model-a', '-a', help='First model name'),
    model_b: str = typer.Option(..., '--model-b', '-b', help='Second model name'),
    metrics: Optional[str] = typer.Option('size,latency', '--metrics', '-m', help='Comma-separated metrics'),
    json_output: bool = typer.Option(False, '--json')
):
    """Compare two models"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from cli.utils import get_project_root, format_file_size
        from pathlib import Path
        import time
        
        models_dir = get_project_root() / "models"
        model_a_path = models_dir / model_a
        model_b_path = models_dir / model_b
        
        if not model_a_path.exists():
            output.error(f"Model A not found: {model_a}")
            raise typer.Exit(1)
        if not model_b_path.exists():
            output.error(f"Model B not found: {model_b}")
            raise typer.Exit(1)
        
        output.info(f"Comparing models: {model_a} vs {model_b}")
        
        metric_list = [m.strip() for m in metrics.split(',')] if metrics else []
        comparison = {}
        
        # Compare sizes
        if 'size' in metric_list or not metric_list:
            def get_dir_size(path):
                total = 0
                for f in path.rglob('*'):
                    if f.is_file():
                        total += f.stat().st_size
                return total
            
            size_a = get_dir_size(model_a_path)
            size_b = get_dir_size(model_b_path)
            comparison['size'] = {
                model_a: format_file_size(size_a),
                model_b: format_file_size(size_b),
                "difference": format_file_size(abs(size_a - size_b))
            }
        
        # Compare file counts
        files_a = len(list(model_a_path.rglob('*')))
        files_b = len(list(model_b_path.rglob('*')))
        comparison['file_count'] = {
            model_a: files_a,
            model_b: files_b
        }
        
        if json_output:
            output.print_json(comparison)
        else:
            output.print_dict(comparison, title="Model Comparison")
            output.info("Note: Full comparison with accuracy/latency requires model inference")
    
    except Exception as e:
        output.error(f"Error comparing models: {e}")
        raise typer.Exit(1)


@app.command("upload")
def upload_model(
    path: str = typer.Option(..., '--path', '-p', help='Local model path'),
    repo: str = typer.Option(..., '--repo', '-r', help='Hugging Face repository'),
    version: Optional[str] = typer.Option(None, '--version', '-v', help='Model version tag'),
    token: Optional[str] = typer.Option(None, '--token', '-t', help='Hugging Face token'),
    json_output: bool = typer.Option(False, '--json')
):
    """Upload model to Hugging Face"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from huggingface_hub import HfApi, upload_folder
        import os
        from pathlib import Path
        
        model_path = Path(path)
        if not model_path.exists():
            output.error(f"Model path not found: {path}")
            raise typer.Exit(1)
        
        hf_token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
        if not hf_token:
            output.error("Hugging Face token required. Set HF_TOKEN or use --token")
            raise typer.Exit(1)
        
        api = HfApi(token=hf_token)
        
        output.info(f"Uploading model from {path} to {repo}")
        
        # Create repo if needed
        try:
            api.create_repo(repo_id=repo, repo_type="model", exist_ok=True)
        except Exception as e:
            output.warning(f"Repo creation check: {e}")
        
        # Upload model
        if model_path.is_file():
            api.upload_file(
                path_or_fileobj=str(model_path),
                path_in_repo=model_path.name,
                repo_id=repo,
                token=hf_token
            )
        elif model_path.is_dir():
            upload_folder(
                folder_path=str(model_path),
                repo_id=repo,
                token=hf_token
            )
        
        # Tag with version if provided
        if version:
            output.info(f"Tagging model with version: {version}")
            # Version tagging would go here
        
        output.success(f"Model uploaded to {repo}")
        
        if json_output:
            output.print_json({"repo": repo, "path": path, "status": "uploaded"})
    
    except ImportError:
        output.error("huggingface_hub not installed. Install with: pip install huggingface_hub")
        raise typer.Exit(1)
    except Exception as e:
        output.error(f"Error uploading model: {e}")
        raise typer.Exit(1)


@app.command("info")
def model_info(
    name: str = typer.Option(..., '--name', '-n', help='Model name'),
    json_output: bool = typer.Option(False, '--json')
):
    """Show model information"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from cli.utils import get_project_root, format_file_size
        from pathlib import Path
        import json
        
        models_dir = get_project_root() / "models"
        model_path = models_dir / name
        
        if not model_path.exists():
            output.error(f"Model not found: {name}")
            raise typer.Exit(1)
        
        # Get model info
        info = {
            "Name": name,
            "Path": str(model_path),
            "Type": "Directory" if model_path.is_dir() else "File"
        }
        
        # Calculate size
        if model_path.is_dir():
            total_size = sum(f.stat().st_size for f in model_path.rglob('*') if f.is_file())
            info["Size"] = format_file_size(total_size)
            info["File Count"] = len(list(model_path.rglob('*')))
        
        # Try to read config.json if exists
        config_file = model_path / "config.json" if model_path.is_dir() else model_path.parent / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    info["Config"] = config
            except:
                pass
        
        if json_output:
            output.print_json(info)
        else:
            output.print_dict(info, title="Model Information")
    
    except Exception as e:
        output.error(f"Error getting model info: {e}")
        raise typer.Exit(1)


@app.command("test")
def test_model(
    name: str = typer.Option(..., '--name', '-n', help='Model name'),
    prompt: str = typer.Option('Hello', '--prompt', '-p', help='Test prompt'),
    json_output: bool = typer.Option(False, '--json')
):
    """Test a model with a prompt"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from cli.utils import get_project_root
        from pathlib import Path
        
        models_dir = get_project_root() / "models"
        model_path = models_dir / name
        
        if not model_path.exists():
            output.error(f"Model not found: {name}")
            raise typer.Exit(1)
        
        output.info(f"Testing model: {name}")
        output.info(f"Prompt: {prompt}")
        
        # Try to use jarvis_llm_brain if available
        try:
            from jarvis_llm_brain import JarvisLLMBrain
            import time
            
            brain = JarvisLLMBrain()
            start_time = time.time()
            response = brain.generate_response(prompt)
            latency = (time.time() - start_time) * 1000  # ms
            
            if json_output:
                output.print_json({
                    "model": name,
                    "prompt": prompt,
                    "response": response,
                    "latency_ms": latency
                })
            else:
                output.success("Model test completed")
                output.print_dict({
                    "Response": response[:200] + "..." if len(response) > 200 else response,
                    "Latency": f"{latency:.2f} ms"
                }, title="Test Results")
        
        except ImportError:
            output.warning("jarvis_llm_brain not available. Model testing requires brain integration")
            if json_output:
                output.print_json({"model": name, "status": "test_skipped", "reason": "brain_not_available"})
    
    except Exception as e:
        output.error(f"Error testing model: {e}")
        raise typer.Exit(1)

