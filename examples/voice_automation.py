#!/usr/bin/env python3
"""
Example: Voice-Enabled Automation
Demonstrates voice commands for common tasks
"""

import subprocess
import json


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
    """Voice automation example"""
    print("=" * 60)
    print("Voice Automation Example")
    print("=" * 60)
    
    # Example voice commands
    voice_commands = [
        "system status",
        "list models",
        "show status",
        "start training",
        "cloud status"
    ]
    
    print("\nVoice Command Examples:")
    print("-" * 60)
    
    for voice_cmd in voice_commands:
        print(f"\nVoice: '{voice_cmd}'")
        
        # Parse voice command
        result = run_cli_command([
            "voice", "command",
            voice_cmd
        ])
        
        if result.get("command"):
            print(f"  → Parsed: {result['command']}")
        else:
            print(f"  → Not recognized")
    
    print("\n" + "=" * 60)
    print("Voice command examples complete!")
    print("=" * 60)
    print("\nTo use interactive voice mode:")
    print("  jarvisx-cli voice interactive")
    print("\nTo use voice output with commands:")
    print("  jarvisx-cli system status --voice")


if __name__ == "__main__":
    main()

