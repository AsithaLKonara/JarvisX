"""
Business Mode CLI Module
Commands for business operations and automation
"""

import typer
from pathlib import Path
from typing import Optional

from cli.base import get_output, get_config
from cli.utils import CLIOutput
from business_mode.client_database import ClientDatabase

app = typer.Typer(name="business", help="Business mode operations")


@app.command("invoice")
def generate_invoice(
    client_id: str = typer.Option(..., '--client-id', '-c', help='Client ID'),
    template: str = typer.Option('standard', '--template', '-t', help='Invoice template'),
    output: Optional[str] = typer.Option(None, '--output', '-o', help='Output path'),
    items: Optional[str] = typer.Option(None, '--items', help='Items as JSON string'),
    tax_rate: float = typer.Option(0.0, '--tax-rate', help='Tax rate (0.0-1.0)'),
    json_output: bool = typer.Option(False, '--json')
):
    """Generate an invoice"""
    output_handler = CLIOutput(json_output=json_output)
    
    try:
        from business_mode.invoice_generator import InvoiceGenerator
        from business_mode.client_database import ClientDatabase
        import json
        
        # Get client info
        client_db = ClientDatabase()
        client = client_db.get_client_by_id(int(client_id)) if client_id.isdigit() else None
        
        if not client:
            output_handler.error(f"Client not found: {client_id}")
            raise typer.Exit(1)
        
        client_name = client.get('name', f"Client {client_id}")
        
        # Parse items
        if items:
            try:
                items_list = json.loads(items)
            except json.JSONDecodeError:
                output_handler.error("Invalid JSON for items")
                raise typer.Exit(1)
        else:
            # Default items
            items_list = [{"description": "Service", "amount": 100.0}]
        
        # Generate invoice
        invoice_gen = InvoiceGenerator()
        invoice_id = invoice_gen.create_invoice(
            client_name=client_name,
            items=items_list,
            tax_rate=tax_rate
        )
        
        if not invoice_id:
            output_handler.error("Failed to create invoice")
            raise typer.Exit(1)
        
        # Export if output specified
        if output:
            output_path = Path(output)
            format_type = output_path.suffix[1:] if output_path.suffix else 'json'
            invoice_gen.export_invoice(invoice_id, format=format_type)
            if output_path.suffix:
                # Move to specified location
                import shutil
                source = invoice_gen.output_dir / f"{invoice_id}.{format_type}"
                if source.exists():
                    shutil.move(str(source), str(output_path))
        
        invoice_data = invoice_gen.get_invoice(invoice_id)
        
        if json_output:
            output_handler.print_json(invoice_data)
        else:
            output_handler.success(f"Invoice {invoice_id} generated for {client_name}")
            output_handler.print_dict({
                "Invoice ID": invoice_id,
                "Client": client_name,
                "Total": f"${invoice_data['total']:.2f}",
                "Status": invoice_data['status']
            }, title="Invoice Details")
        
    except Exception as e:
        output_handler.error(f"Error generating invoice: {e}")
        raise typer.Exit(1)


@app.command("client")
def client_operations(
    action: str = typer.Argument(..., help='Action: list, add, get, update, delete'),
    client_id: Optional[str] = typer.Option(None, '--id', help='Client ID'),
    name: Optional[str] = typer.Option(None, '--name', help='Client name'),
    email: Optional[str] = typer.Option(None, '--email', help='Client email'),
    phone: Optional[str] = typer.Option(None, '--phone', help='Client phone'),
    company: Optional[str] = typer.Option(None, '--company', help='Client company'),
    search: Optional[str] = typer.Option(None, '--search', '-s', help='Search term'),
    format: str = typer.Option('table', '--format', '-f', help='Output format (table/json/csv)'),
    json_output: bool = typer.Option(False, '--json')
):
    """Manage clients"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from business_mode.client_database import ClientDatabase
        
        client_db = ClientDatabase()
        
        if action == "list":
            clients = client_db.list_clients()
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                clients = [c for c in clients if search_lower in str(c).lower()]
            
            if json_output or format == 'json':
                output.print_json(clients)
            elif format == 'csv':
                import csv
                import sys
                if clients:
                    writer = csv.DictWriter(sys.stdout, fieldnames=['id', 'name', 'email', 'phone', 'company', 'status'])
                    writer.writeheader()
                    writer.writerows(clients)
            else:
                if clients:
                    table_data = [
                        [str(c.get('id', '')), c.get('name', ''), c.get('email', ''), c.get('company', ''), c.get('status', '')]
                        for c in clients
                    ]
                    output.print_table(table_data, ['ID', 'Name', 'Email', 'Company', 'Status'], title="Clients")
                else:
                    output.info("No clients found")
        
        elif action == "add":
            if not name:
                output.error("Name is required for adding a client")
                raise typer.Exit(1)
            
            client_id = client_db.add_client(
                name=name,
                email=email or '',
                phone=phone or '',
                company=company or ''
            )
            
            if client_id:
                output.success(f"Client added with ID: {client_id}")
                if json_output:
                    client = client_db.get_client_by_id(client_id)
                    output.print_json(client)
            else:
                output.error("Failed to add client")
                raise typer.Exit(1)
        
        elif action == "get":
            if not client_id:
                output.error("Client ID required")
                raise typer.Exit(1)
            
            client = client_db.get_client_by_id(int(client_id))
            if client:
                if json_output:
                    output.print_json(client)
                else:
                    output.print_dict(client, title="Client Details")
            else:
                output.error(f"Client not found: {client_id}")
                raise typer.Exit(1)
        
        else:
            output.error(f"Unknown action: {action}")
            raise typer.Exit(1)
    
    except Exception as e:
        output.error(f"Error in client operation: {e}")
        raise typer.Exit(1)


@app.command("report")
def generate_report(
    report_type: str = typer.Option(..., '--type', '-t', help='Report type (financial/summary)'),
    period: str = typer.Option('monthly', '--period', '-p', help='Period (monthly/yearly)'),
    format: str = typer.Option('json', '--format', '-f', help='Output format (json/txt)'),
    output: Optional[str] = typer.Option(None, '--output', '-o', help='Output path'),
    json_output: bool = typer.Option(False, '--json')
):
    """Generate business report"""
    output_handler = CLIOutput(json_output=json_output)
    
    try:
        from business_mode.finance_tracker import FinanceTracker
        from business_mode.invoice_generator import InvoiceGenerator
        from datetime import datetime, timedelta
        import json
        
        finance = FinanceTracker()
        invoices = InvoiceGenerator()
        
        # Calculate date range
        now = datetime.now()
        if period == 'monthly':
            start_date = now.replace(day=1)
            end_date = now
        elif period == 'yearly':
            start_date = now.replace(month=1, day=1)
            end_date = now
        else:
            start_date = now - timedelta(days=30)
            end_date = now
        
        report_data = {
            "report_type": report_type,
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        if report_type == "financial":
            # Get financial summary
            summary = finance.get_summary()
            report_data["financial"] = summary
            
            # Get invoices
            invoice_list = invoices.list_invoices()
            report_data["invoices"] = {
                "total": len(invoice_list),
                "paid": len([i for i in invoice_list if i.get('status') == 'paid']),
                "pending": len([i for i in invoice_list if i.get('status') == 'draft'])
            }
        
        elif report_type == "summary":
            # Business summary
            client_db = ClientDatabase()
            clients = client_db.list_clients()
            
            report_data["summary"] = {
                "total_clients": len(clients),
                "total_invoices": len(invoices.list_invoices()),
                "period": period
            }
        
        # Save report
        if output:
            output_path = Path(output)
            if format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(report_data, f, indent=2)
            else:
                # Text format
                with open(output_path, 'w') as f:
                    f.write(f"{report_type.upper()} REPORT - {period.upper()}\n")
                    f.write("=" * 60 + "\n")
                    f.write(json.dumps(report_data, indent=2))
            output_handler.success(f"Report saved to: {output_path}")
        
        if json_output:
            output_handler.print_json(report_data)
        else:
            output_handler.success(f"{report_type} report generated")
            output_handler.print_dict(report_data, title=f"{report_type.upper()} Report")
        
    except Exception as e:
        output_handler.error(f"Error generating report: {e}")
        raise typer.Exit(1)


@app.command("task")
def task_operations(
    action: str = typer.Argument(..., help='Action: schedule, list, cancel'),
    name: Optional[str] = typer.Option(None, '--name', help='Task name'),
    cron: Optional[str] = typer.Option(None, '--cron', help='Cron expression or due date'),
    task_id: Optional[str] = typer.Option(None, '--id', help='Task ID'),
    priority: str = typer.Option('medium', '--priority', '-p', help='Task priority (low/medium/high)'),
    description: Optional[str] = typer.Option(None, '--description', '-d', help='Task description'),
    json_output: bool = typer.Option(False, '--json')
):
    """Manage scheduled tasks"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from business_mode.task_scheduler import TaskScheduler
        
        scheduler = TaskScheduler()
        
        if action == "schedule":
            if not name:
                output.error("Task name is required")
                raise typer.Exit(1)
            
            if not cron:
                output.error("Due date or cron expression is required")
                raise typer.Exit(1)
            
            # For now, treat cron as due_date (can be extended for actual cron)
            success = scheduler.create_task(
                title=name,
                due_date=cron,
                priority=priority,
                description=description or ''
            )
            
            if success:
                output.success(f"Task '{name}' scheduled")
                if json_output:
                    tasks = scheduler.list_tasks()
                    output.print_json([t for t in tasks if t.get('title') == name])
            else:
                output.error("Failed to schedule task")
                raise typer.Exit(1)
        
        elif action == "list":
            tasks = scheduler.list_tasks()
            
            if json_output:
                output.print_json(tasks)
            else:
                if tasks:
                    table_data = [
                        [str(t.get('id', '')), t.get('title', ''), t.get('status', ''), t.get('priority', ''), t.get('due_date', '')]
                        for t in tasks
                    ]
                    output.print_table(table_data, ['ID', 'Title', 'Status', 'Priority', 'Due Date'], title="Scheduled Tasks")
                else:
                    output.info("No tasks found")
        
        elif action == "cancel":
            if not task_id:
                output.error("Task ID is required")
                raise typer.Exit(1)
            
            # Mark task as cancelled
            success = scheduler.update_task(int(task_id), status='cancelled')
            
            if success:
                output.success(f"Task {task_id} cancelled")
            else:
                output.error(f"Failed to cancel task {task_id}")
                raise typer.Exit(1)
        
        else:
            output.error(f"Unknown action: {action}")
            raise typer.Exit(1)
    
    except Exception as e:
        output.error(f"Error in task operation: {e}")
        raise typer.Exit(1)


@app.command("export")
def export_data(
    data_type: str = typer.Option(..., '--type', '-t', help='Data type (invoices/clients)'),
    format: str = typer.Option('csv', '--format', '-f', help='Output format (csv/json)'),
    output: str = typer.Option(..., '--output', '-o', help='Output path'),
    json_output: bool = typer.Option(False, '--json')
):
    """Export business data"""
    output_handler = CLIOutput(json_output=json_output)
    
    try:
        import json
        import csv
        from pathlib import Path
        
        output_path = Path(output)
        
        if data_type == "invoices":
            from business_mode.invoice_generator import InvoiceGenerator
            
            invoice_gen = InvoiceGenerator()
            invoices = invoice_gen.list_invoices()
            
            if format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(invoices, f, indent=2)
            else:  # CSV
                if invoices:
                    with open(output_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=invoices[0].keys())
                        writer.writeheader()
                        writer.writerows(invoices)
                else:
                    # Create empty CSV with headers
                    with open(output_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=['invoice_id', 'client_name', 'total', 'status'])
                        writer.writeheader()
        
        elif data_type == "clients":
            from business_mode.client_database import ClientDatabase
            
            client_db = ClientDatabase()
            clients = client_db.list_clients()
            
            if format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(clients, f, indent=2)
            else:  # CSV
                if clients:
                    with open(output_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=clients[0].keys())
                        writer.writeheader()
                        writer.writerows(clients)
                else:
                    with open(output_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'email', 'company', 'status'])
                        writer.writeheader()
        
        else:
            output_handler.error(f"Unknown data type: {data_type}")
            raise typer.Exit(1)
        
        output_handler.success(f"Exported {data_type} to {output_path} ({format} format)")
        
        if json_output:
            output_handler.print_json({"exported": str(output_path), "format": format, "type": data_type})
        
    except Exception as e:
        output_handler.error(f"Error exporting data: {e}")
        raise typer.Exit(1)

