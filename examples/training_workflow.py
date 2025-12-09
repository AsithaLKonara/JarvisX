#!/usr/bin/env python3
"""
Example: Complete Training Workflow
Demonstrates training → status → logs → evaluate workflow
"""

import subprocess
import json
import time
from pathlib import Path


def run_cli_command(cmd: list) -> dict:
    """Run CLI command and return JSON result"""
    result = subprocess.run(
        ["python3", "-m", "cli.main"] + cmd + ["--json"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        print(f"Error: {result.stderr}")
        return {}


def main():
    """Complete training workflow example"""
    print("=" * 60)
    print("Training Workflow Example")
    print("=" * 60)
    
    # 1. Start training
    print("\n1. Starting training job...")
    config_path = "training/training_config.json"
    if not Path(config_path).exists():
        print(f"Config file not found: {config_path}")
        return
    
    result = run_cli_command([
        "training", "start",
        "--config", config_path,
        "--epochs", "5"
    ])
    
    if "job_id" in result:
        job_id = result["job_id"]
        print(f"✅ Training job started: {job_id}")
    else:
        print("❌ Failed to start training")
        return
    
    # 2. Monitor status
    print(f"\n2. Monitoring job status: {job_id}")
    for i in range(10):
        result = run_cli_command([
            "training", "status",
            "--job-id", job_id
        ])
        
        if result.get("status") == "completed":
            print("✅ Training completed!")
            break
        elif result.get("status") == "failed":
            print("❌ Training failed!")
            break
        
        print(f"   Status: {result.get('status', 'unknown')} - Progress: {result.get('progress', 0) * 100:.1f}%")
        time.sleep(2)
    
    # 3. View logs
    print(f"\n3. Viewing training logs: {job_id}")
    result = run_cli_command([
        "training", "logs",
        "--job-id", job_id
    ])
    
    if "logs" in result:
        print(f"   Found {len(result['logs'])} log entries")
    
    # 4. Evaluate model
    print("\n4. Evaluating model...")
    output_dir = result.get("output_dir", "output")
    if Path(output_dir).exists():
        result = run_cli_command([
            "training", "evaluate",
            "--model", output_dir
        ])
        print("✅ Evaluation complete")
    
    print("\n" + "=" * 60)
    print("Workflow complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

