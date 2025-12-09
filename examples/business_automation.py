#!/usr/bin/env python3
"""
Example: Business Automation Workflow
Demonstrates client management → invoice generation → reporting
"""

import subprocess
import json
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
    """Business automation workflow example"""
    print("=" * 60)
    print("Business Automation Workflow Example")
    print("=" * 60)
    
    # 1. Add client
    print("\n1. Adding client...")
    result = run_cli_command([
        "business", "client", "add",
        "--name", "Example Corp",
        "--email", "contact@example.com",
        "--company", "Example Corporation"
    ])
    
    if result:
        client_id = result.get("id")
        print(f"✅ Client added: {client_id}")
    else:
        print("❌ Failed to add client")
        return
    
    # 2. Generate invoice
    print("\n2. Generating invoice...")
    items_json = json.dumps([
        {"description": "Consulting Services", "amount": 1000.0},
        {"description": "Development Work", "amount": 2000.0}
    ])
    
    result = run_cli_command([
        "business", "invoice",
        "--client-id", str(client_id),
        "--items", items_json,
        "--tax-rate", "0.1"
    ])
    
    if result:
        invoice_id = result.get("invoice_id")
        print(f"✅ Invoice generated: {invoice_id}")
        print(f"   Total: ${result.get('total', 0):.2f}")
    
    # 3. Generate report
    print("\n3. Generating financial report...")
    result = run_cli_command([
        "business", "report",
        "--type", "financial",
        "--period", "monthly"
    ])
    
    if result:
        print("✅ Report generated")
        print(f"   Summary: {result.get('summary', {})}")
    
    # 4. Export data
    print("\n4. Exporting data...")
    output_file = "exports/business_data.csv"
    Path("exports").mkdir(exist_ok=True)
    
    result = run_cli_command([
        "business", "export",
        "--type", "invoices",
        "--format", "csv",
        "--output", output_file
    ])
    
    if Path(output_file).exists():
        print(f"✅ Data exported to: {output_file}")
    
    print("\n" + "=" * 60)
    print("Business workflow complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

