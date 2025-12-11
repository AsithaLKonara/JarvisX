"""
Voice I/O CLI Module
Commands for voice input/output and interactive voice mode
"""

import typer
from typing import Optional
import time

from cli.base import get_output, get_config
from cli.utils import CLIOutput

app = typer.Typer(name="voice", help="Voice I/O operations")


@app.command("listen")
def listen_voice(
    timeout: int = typer.Option(5, '--timeout', '-t', help='Listening timeout in seconds'),
    json_output: bool = typer.Option(False, '--json')
):
    """Listen for voice input and convert to text"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from speech.speech_recognizer import SpeechRecognizer
        
        recognizer = SpeechRecognizer()
        
        if not recognizer.is_available():
            output.error("Speech recognition not available")
            raise typer.Exit(1)
        
        output.info(f"Listening for {timeout} seconds...")
        output.info("Speak now...")
        
        # Record audio
        text = recognizer.listen(timeout=timeout)
        
        if text:
            if json_output:
                output.print_json({"recognized_text": text})
            else:
                output.success(f"Recognized: {text}")
            return text
        else:
            output.warning("No speech detected")
            if json_output:
                output.print_json({"recognized_text": None})
            return None
    
    except ImportError:
        output.error("Speech recognition module not available")
        raise typer.Exit(1)
    except Exception as e:
        output.error(f"Error in voice recognition: {e}")
        raise typer.Exit(1)


@app.command("speak")
def speak_text(
    text: str = typer.Argument(..., help='Text to speak'),
    json_output: bool = typer.Option(False, '--json')
):
    """Convert text to speech"""
    output = CLIOutput(json_output=json_output)
    
    try:
        from speech.text_to_speech import TTSEngine
        import os
        
        engine_name = os.getenv('TTS_ENGINE', 'pyttsx3')
        tts = TTSEngine(engine=engine_name)
        
        if not tts.is_available:
            output.error("TTS engine not available")
            raise typer.Exit(1)
        
        output.info(f"Speaking: {text}")
        success = tts.speak(text, blocking=True)
        
        if success:
            output.success("Speech completed")
            if json_output:
                output.print_json({"status": "success", "text": text})
        else:
            output.error("Speech failed")
            raise typer.Exit(1)
    
    except Exception as e:
        output.error(f"Error in text-to-speech: {e}")
        raise typer.Exit(1)


@app.command("interactive")
def interactive_voice(
    wake_word: Optional[str] = typer.Option(None, '--wake-word', '-w', help='Wake word to activate'),
    json_output: bool = typer.Option(False, '--json')
):
    """Interactive voice mode - continuous listening and command execution"""
    output = CLIOutput(json_output=json_output, voice=True)
    
    try:
        from speech.speech_recognizer import SpeechRecognizer
        from speech.text_to_speech import TTSEngine
        from speech.wake_word_detector import WakeWordDetector
        import os
        
        recognizer = SpeechRecognizer()
        tts_engine = TTSEngine(engine=os.getenv('TTS_ENGINE', 'pyttsx3'))
        
        if not recognizer.is_available():
            output.error("Speech recognition not available")
            raise typer.Exit(1)
        
        if not tts_engine.is_available:
            output.warning("TTS not available, voice output disabled")
            tts_engine = None
        
        # Initialize wake word detector if specified
        wake_detector = None
        if wake_word:
            wake_detector = WakeWordDetector(wake_word=wake_word)
            output.info(f"Wake word detection enabled: '{wake_word}'")
        
        output.success("Voice interactive mode activated")
        output.info("Say 'exit' or 'quit' to stop")
        
        if wake_detector:
            output.info("Wake word mode: Say wake word to activate")
        else:
            output.info("Listening...")
        
        if tts_engine:
            tts_engine.speak("Voice mode activated", blocking=True)
        
        from cli.voice_utils import VoiceCommandParser
        
        parser = VoiceCommandParser()
        active = False  # Whether actively listening for commands
        
        # Start wake word detection if enabled
        if wake_detector:
            def on_wake_word_detected(text: str):
                nonlocal active
                active = True
                if tts_engine:
                    tts_engine.speak("Yes, I'm listening", blocking=False)
                output.info("Wake word detected - listening for command...")
            
            wake_detector.start_listening(on_wake_word_detected)
        
        while True:
            try:
                # If wake word mode, only listen when activated
                if wake_detector and not active:
                    time.sleep(0.5)
                    continue
                
                # Listen for command
                text = recognizer.listen(timeout=10)
                
                if not text:
                    if wake_detector:
                        active = False  # Reset after timeout
                    continue
                
                # Check for exit
                if text.lower() in ['exit', 'quit', 'stop']:
                    output.info("Exiting voice mode...")
                    if wake_detector:
                        wake_detector.stop_listening()
                    if tts_engine:
                        tts_engine.speak("Goodbye", blocking=True)
                    break
                
                # Reset active state if using wake word
                if wake_detector:
                    active = False
                
                # Try to recognize speaker (optional, may not be available)
                try:
                    from speech.speaker_recognizer import SpeakerRecognizer
                    speaker_recognizer = SpeakerRecognizer()
                    speaker = speaker_recognizer.recognize(text=text)
                    if speaker:
                        output.info(f"Recognized speaker: {speaker.name}")
                        # Could personalize responses based on speaker preferences
                except (ImportError, AttributeError):
                    # Speaker recognition not available, skip
                    pass
                
                # Process via unified orchestrator
                output.info(f"Heard: {text}")
                
                if tts_engine:
                    tts_engine.speak("Processing", blocking=False)
                
                # Use unified orchestrator for full pipeline
                try:
                    from core.voice_orchestrator import VoiceOrchestrator
                    
                    voice_orch = VoiceOrchestrator()
                    result = voice_orch.process_voice_input(voice_input=text, enable_tts=True)
                    
                    if result.get('success'):
                        response = result.get('response', 'Done')
                        actions = result.get('actions', [])
                        
                        if actions:
                            output.success(f"Executed {len(actions)} action(s)")
                            if json_output:
                                output.print_json({
                                    "success": True,
                                    "response": response,
                                    "actions": actions,
                                    "execution_results": result.get('execution_results', [])
                                })
                        else:
                            # Conversational response
                            output.info(f"Response: {response}")
                            if json_output:
                                output.print_json({
                                    "success": True,
                                    "response": response,
                                    "type": "conversational"
                                })
                    else:
                        error = result.get('error', 'Unknown error')
                        output.error(f"Error: {error}")
                        if tts_engine:
                            tts_engine.speak(f"Error: {error}", blocking=False)
                
                except ImportError:
                    # Fallback to simple command parsing if unified orchestrator not available
                    command = parser.parse_voice_command(text)
                    if command:
                        output.info(f"Command: {command}")
                        output.warning("Unified orchestrator not available, using simple parsing")
                        if tts_engine:
                            tts_engine.speak("Command recognized but execution requires unified orchestrator", blocking=False)
                    else:
                        output.warning("Command not recognized")
                        if tts_engine:
                            tts_engine.speak("Command not recognized", blocking=False)
                except Exception as e:
                    output.error(f"Error processing command: {e}")
                    if tts_engine:
                        tts_engine.speak("Error occurred", blocking=False)
            
            except KeyboardInterrupt:
                output.info("\nExiting voice mode...")
                if wake_detector:
                    wake_detector.stop_listening()
                break
            except Exception as e:
                output.error(f"Error: {e}")
                if tts_engine:
                    tts_engine.speak("Error occurred", blocking=False)
    
    except Exception as e:
        output.error(f"Error in interactive voice mode: {e}")
        raise typer.Exit(1)


@app.command("command")
def voice_command(
    command_text: str = typer.Argument(..., help='Voice command text'),
    enable_tts: bool = typer.Option(True, '--tts/--no-tts', help='Enable/disable TTS output'),
    json_output: bool = typer.Option(False, '--json')
):
    """Execute a voice command using unified orchestrator"""
    output = CLIOutput(json_output=json_output)
    
    try:
        # Use unified orchestrator for full pipeline
        from core.unified_orchestrator import UnifiedOrchestrator
        
        orchestrator = UnifiedOrchestrator()
        result = orchestrator.process_text_command(command_text, enable_tts=enable_tts)
        
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
                    output.success(f"Executed {len(actions)} action(s)")
                    output.info(f"Response: {response}")
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
                output.error(f"Error: {error}")
                if result.get('response'):
                    output.info(f"Response: {result.get('response')}")
            raise typer.Exit(1)
    
    except ImportError:
        # Fallback to simple command parsing
        try:
            from cli.voice_utils import VoiceCommandParser
            
            parser = VoiceCommandParser()
            command = parser.parse_voice_command(command_text)
            
            if command:
                if json_output:
                    output.print_json({"command": command, "original_text": command_text})
                else:
                    output.success(f"Command: {command}")
                    output.warning("Unified orchestrator not available, using simple parsing")
            else:
                output.warning("Command not recognized")
                if json_output:
                    output.print_json({"command": None, "original_text": command_text})
        except Exception as e:
            output.error(f"Error parsing voice command: {e}")
            raise typer.Exit(1)
    
    except Exception as e:
        output.error(f"Error executing voice command: {e}")
        raise typer.Exit(1)

