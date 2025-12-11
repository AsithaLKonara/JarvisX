"""
Unified Orchestrator CLI Module
Provides natural language command processing via unified orchestrator
"""

import typer
from typing import Optional

from cli.base import get_output, get_config
from cli.utils import CLIOutput

app = typer.Typer(name="unified", help="Unified natural language command processing")


@app.command("execute")
def execute_command(
    command: str = typer.Argument(..., help='Natural language command'),
    enable_tts: bool = typer.Option(True, '--tts/--no-tts', help='Enable/disable TTS output'),
    json_output: bool = typer.Option(False, '--json')
):
    """
    Execute a natural language command using unified orchestrator
    
    Processes command through: STT → AI → Action Extraction → Tool Execution → TTS
    
    Examples:
        jarvisx-cli unified execute "Check CPU usage"
        jarvisx-cli unified execute "Generate invoice for client ABC"
        jarvisx-cli unified execute "Monitor system and optimize"
    """
    output = CLIOutput(json_output=json_output)
    
    try:
        from core.unified_orchestrator import UnifiedOrchestrator
        
        output.info(f"Processing command: {command}")
        
        orchestrator = UnifiedOrchestrator()
        result = orchestrator.process_text_command(command, enable_tts=enable_tts)
        
        if result.get('success'):
            response = result.get('response', 'Done')
            actions = result.get('actions', [])
            execution_results = result.get('execution_results', [])
            
            if json_output:
                output.print_json({
                    "success": True,
                    "user_input": result.get('user_input'),
                    "ai_response": result.get('ai_response'),
                    "response": response,
                    "actions": actions,
                    "execution_results": execution_results
                })
            else:
                if actions:
                    output.success(f"✅ Executed {len(actions)} action(s)")
                    for i, action in enumerate(actions, 1):
                        output.info(f"  {i}. {action}")
                    output.info(f"\nResponse: {response}")
                else:
                    output.info(f"Response: {response}")
        else:
            error = result.get('error', 'Unknown error')
            if json_output:
                output.print_json({
                    "success": False,
                    "error": error,
                    "response": result.get('response', '')
                })
            else:
                output.error(f"❌ Error: {error}")
                if result.get('response'):
                    output.info(f"Response: {result.get('response')}")
            raise typer.Exit(1)
    
    except ImportError as e:
        output.error(f"Unified orchestrator not available: {e}")
        output.info("Make sure all dependencies are installed")
        raise typer.Exit(1)
    except Exception as e:
        output.error(f"Error executing command: {e}")
        if get_config().get('verbose', False):
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command("voice")
def execute_voice(
    timeout: int = typer.Option(10, '--timeout', '-t', help='Listening timeout in seconds'),
    enable_tts: bool = typer.Option(True, '--tts/--no-tts', help='Enable/disable TTS output'),
    json_output: bool = typer.Option(False, '--json')
):
    """
    Listen for voice input and execute via unified orchestrator
    
    Listens for voice command, processes through unified pipeline, and executes actions.
    """
    output = CLIOutput(json_output=json_output)
    
    try:
        from core.unified_orchestrator import UnifiedOrchestrator
        
        orchestrator = UnifiedOrchestrator()
        
        if not orchestrator.stt_available:
            output.error("Speech recognition not available")
            raise typer.Exit(1)
        
        output.info(f"Listening for {timeout} seconds...")
        output.info("Speak your command now...")
        
        # Process voice command (will listen via STT)
        result = orchestrator.process_voice_command(enable_tts=enable_tts)
        
        if result.get('success'):
            response = result.get('response', 'Done')
            actions = result.get('actions', [])
            
            if json_output:
                output.print_json({
                    "success": True,
                    "user_input": result.get('user_input'),
                    "response": response,
                    "actions": actions
                })
            else:
                if actions:
                    output.success(f"✅ Executed {len(actions)} action(s)")
                output.info(f"Response: {response}")
        else:
            error = result.get('error', 'Unknown error')
            if json_output:
                output.print_json({
                    "success": False,
                    "error": error
                })
            else:
                output.error(f"❌ Error: {error}")
            raise typer.Exit(1)
    
    except ImportError as e:
        output.error(f"Unified orchestrator not available: {e}")
        raise typer.Exit(1)
    except Exception as e:
        output.error(f"Error processing voice command: {e}")
        raise typer.Exit(1)


@app.command("status")
def unified_status(
    json_output: bool = typer.Option(False, '--json')
):
    """Check unified orchestrator status"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from core.unified_orchestrator import UnifiedOrchestrator
        
        orchestrator = UnifiedOrchestrator()
        status = orchestrator.get_status()
        
        if json_output:
            output.print_json(status)
        else:
            output.print_dict({
                "AI Available": "✅ Yes" if status.get('ai_available') else "❌ No",
                "STT Available": "✅ Yes" if status.get('stt_available') else "❌ No",
                "TTS Available": "✅ Yes" if status.get('tts_available') else "❌ No",
                "Tools Available": status.get('tools_available', {})
            }, title="Unified Orchestrator Status")
    
    except Exception as e:
        output.error(f"Error getting status: {e}")
        raise typer.Exit(1)

