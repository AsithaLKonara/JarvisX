"""
Workflow Orchestration CLI Module
Commands for managing workflows and automation
"""

import typer
import json
from typing import Optional

from cli.base import get_output, get_config
from cli.utils import CLIOutput

app = typer.Typer(name="workflow", help="Workflow orchestration")


@app.command("list")
def list_workflows(
    category: Optional[str] = typer.Option(None, '--category', '-c', help='Filter by category'),
    json_output: bool = typer.Option(False, '--json')
):
    """List available workflows"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from automation.workflow_orchestrator import WorkflowOrchestrator
        
        orchestrator = WorkflowOrchestrator()
        workflows = orchestrator.get_workflows(category=category)
        
        if json_output:
            output.print_json(workflows)
        else:
            if workflows:
                table_data = [
                    [w['id'], w['name'], str(w['node_count']), 'Active' if w['active'] else 'Inactive']
                    for w in workflows
                ]
                output.print_table(table_data, ['ID', 'Name', 'Nodes', 'Status'], title="Available Workflows")
            else:
                output.info("No workflows found")
    except Exception as e:
        output.error(f"Error listing workflows: {e}")
        raise typer.Exit(1)


@app.command("execute")
def execute_workflow(
    workflow_id: str = typer.Option(..., '--id', '-i', help='Workflow ID'),
    input_data: Optional[str] = typer.Option(None, '--input', help='Input data as JSON'),
    json_output: bool = typer.Option(False, '--json')
):
    """Execute a workflow"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from automation.workflow_orchestrator import WorkflowOrchestrator
        
        orchestrator = WorkflowOrchestrator()
        
        # Parse input data if provided
        parsed_input = {}
        if input_data:
            try:
                parsed_input = json.loads(input_data)
            except json.JSONDecodeError:
                output.error("Invalid JSON input data")
                raise typer.Exit(1)
        
        result = orchestrator.execute_workflow(workflow_id, parsed_input)
        
        if result.get('success'):
            output.success(f"Workflow '{result['workflow_name']}' executed successfully")
            if json_output:
                output.print_json(result)
        else:
            output.error(f"Workflow execution failed: {result.get('error', 'Unknown error')}")
            raise typer.Exit(1)
    except Exception as e:
        output.error(f"Error executing workflow: {e}")
        raise typer.Exit(1)


@app.command("create")
def create_workflow(
    from_template: Optional[str] = typer.Option(None, '--from-template', help='Template name'),
    name: Optional[str] = typer.Option(None, '--name', help='Workflow name'),
    workflow_file: Optional[str] = typer.Option(None, '--file', '-f', help='Workflow JSON file'),
    json_output: bool = typer.Option(False, '--json')
):
    """Create a new workflow"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from automation.workflow_orchestrator import WorkflowOrchestrator
        from pathlib import Path
        import json
        
        orchestrator = WorkflowOrchestrator()
        
        if workflow_file:
            # Load workflow from file
            workflow_path = Path(workflow_file)
            if not workflow_path.exists():
                output.error(f"Workflow file not found: {workflow_file}")
                raise typer.Exit(1)
            
            with open(workflow_path, 'r') as f:
                workflow_data = json.load(f)
            
            workflow_name = name or workflow_data.get('name', workflow_path.stem)
            output.info(f"Creating workflow '{workflow_name}' from file: {workflow_file}")
            
            # Register workflow
            workflow_id = workflow_data.get('id', f"workflow_{workflow_name}")
            orchestrator.workflows[workflow_id] = workflow_data
            
            output.success(f"Workflow '{workflow_name}' created with ID: {workflow_id}")
            
            if json_output:
                output.print_json({"workflow_id": workflow_id, "name": workflow_name, "status": "created"})
        
        elif from_template:
            # Create from template
            output.info(f"Creating workflow from template: {from_template}")
            # Template-based creation would go here
            output.warning("Template-based workflow creation requires template definitions")
        
        else:
            output.error("Either --file or --from-template must be specified")
            raise typer.Exit(1)
    
    except Exception as e:
        output.error(f"Error creating workflow: {e}")
        raise typer.Exit(1)


@app.command("status")
def workflow_status(
    execution_id: str = typer.Option(..., '--execution-id', '-e', help='Execution ID'),
    json_output: bool = typer.Option(False, '--json')
):
    """Check workflow execution status"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from automation.workflow_orchestrator import WorkflowOrchestrator
        
        orchestrator = WorkflowOrchestrator()
        
        # Get execution status
        execution = orchestrator.executions.get(execution_id)
        
        if not execution:
            output.error(f"Execution not found: {execution_id}")
            raise typer.Exit(1)
        
        status_data = {
            "Execution ID": execution_id,
            "Workflow ID": execution.workflow_id,
            "Status": execution.status.value,
            "Start Time": execution.start_time.isoformat() if execution.start_time else "N/A",
            "End Time": execution.end_time.isoformat() if execution.end_time else "Running"
        }
        
        if execution.error_message:
            status_data["Error"] = execution.error_message
        
        if json_output:
            output.print_json(status_data)
        else:
            output.print_dict(status_data, title="Workflow Execution Status")
    
    except Exception as e:
        output.error(f"Error checking workflow status: {e}")
        raise typer.Exit(1)


@app.command("analytics")
def workflow_analytics(
    format: str = typer.Option('table', '--format', '-f', help='Output format (table/json)'),
    json_output: bool = typer.Option(False, '--json')
):
    """Show workflow analytics"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from automation.workflow_orchestrator import WorkflowOrchestrator
        
        orchestrator = WorkflowOrchestrator()
        analytics = orchestrator.get_workflow_analytics()
        
        if json_output or format == 'json':
            output.print_json(analytics)
        else:
            output.print_dict(analytics, title="Workflow Analytics")
    except Exception as e:
        output.error(f"Error getting analytics: {e}")
        raise typer.Exit(1)


@app.command("recommend")
def recommend_workflows(
    context: Optional[str] = typer.Option(None, '--context', help='Context as JSON'),
    json_output: bool = typer.Option(False, '--json')
):
    """Get workflow recommendations"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from automation.workflow_orchestrator import WorkflowOrchestrator
        
        orchestrator = WorkflowOrchestrator()
        
        # Parse context if provided
        user_context = {}
        if context:
            try:
                user_context = json.loads(context)
            except json.JSONDecodeError:
                output.error("Invalid JSON context")
                raise typer.Exit(1)
        
        recommendations = orchestrator.recommend_workflows(user_context)
        
        if recommendations:
            if json_output:
                output.print_json(recommendations)
            else:
                table_data = [
                    [r['workflow_id'], r['name'], str(r['score']), ', '.join(r['categories'])]
                    for r in recommendations
                ]
                output.print_table(table_data, ['ID', 'Name', 'Score', 'Categories'], title="Recommended Workflows")
        else:
            output.info("No workflow recommendations available")
    except Exception as e:
        output.error(f"Error getting recommendations: {e}")
        raise typer.Exit(1)

