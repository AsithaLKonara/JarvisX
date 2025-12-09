#!/usr/bin/env python3
"""
Example: Cloud Deployment Workflow
Demonstrates model training → deployment → monitoring
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
    """Cloud deployment workflow example"""
    print("=" * 60)
    print("Cloud Deployment Workflow Example")
    print("=" * 60)
    
    # 1. Connect to cloud
    print("\n1. Connecting to cloud space...")
    space_url = "https://example-space.hf.space"
    
    result = run_cli_command([
        "cloud", "connect",
        "--url", space_url
    ])
    
    if result.get("status") == "success":
        print("✅ Connected to cloud space")
    else:
        print("⚠️  Cloud connection test (may require valid URL)")
    
    # 2. Check space status
    print("\n2. Checking space status...")
    space_name = "example-user/example-space"
    
    result = run_cli_command([
        "cloud", "status",
        "--space", space_name
    ])
    
    if result:
        print(f"   Space: {result.get('Space ID', 'unknown')}")
        print(f"   Status: {result.get('Status', 'unknown')}")
    
    # 3. Deploy model (example)
    print("\n3. Deploying model...")
    model_path = "models/test_model"
    
    if Path(model_path).exists():
        result = run_cli_command([
            "cloud", "deploy",
            "--space", space_name,
            "--model", model_path,
            "--hardware", "cpu"
        ])
        print("✅ Deployment initiated")
    else:
        print("⚠️  Model path not found (skipping deployment)")
    
    # 4. Monitor deployment
    print("\n4. Monitoring deployment...")
    print("   (Monitoring would run here)")
    print("   Use: jarvisx-cli cloud monitor --space <space-name>")
    
    print("\n" + "=" * 60)
    print("Cloud deployment workflow complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

