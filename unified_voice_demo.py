#!/usr/bin/env python3
"""
Unified Voice Demo - Demo of the unified feature integration pipeline
Demonstrates STT → AI → Action Extraction → Tool Execution → TTS flow
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.unified_orchestrator import UnifiedOrchestrator
from core.voice_orchestrator import VoiceOrchestrator


def demo_text_commands():
    """Demo text-based commands"""
    print("\n" + "="*60)
    print("Unified Orchestrator - Text Command Demo")
    print("="*60 + "\n")
    
    orchestrator = UnifiedOrchestrator()
    
    # Test commands
    test_commands = [
        "Check CPU usage",
        "Show me memory usage",
        "List files in current directory",
        "What's the current time?",
    ]
    
    for command in test_commands:
        print(f"\n📥 Command: {command}")
        print("-" * 60)
        
        result = orchestrator.process_text_command(command, enable_tts=False)
        
        if result.get('success'):
            print(f"✅ Response: {result.get('response', 'No response')}")
            if result.get('actions'):
                print(f"🔧 Actions executed: {result.get('actions')}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        print()


def demo_voice_mode():
    """Demo voice mode with continuous listening"""
    print("\n" + "="*60)
    print("Voice Orchestrator - Voice Mode Demo")
    print("="*60 + "\n")
    
    voice_orch = VoiceOrchestrator()
    
    print("Starting voice mode...")
    print("Say 'stop' to exit\n")
    
    # Start voice mode
    if voice_orch.start_voice_mode(continuous=True, wake_word=False):
        print("✅ Voice mode started. Listening for commands...")
        print("(Press Ctrl+C to stop)\n")
        
        try:
            # Keep running until interrupted
            import time
            while voice_orch.is_listening:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping voice mode...")
            voice_orch.stop_voice_mode()
            print("✅ Voice mode stopped")
    else:
        print("❌ Failed to start voice mode")


def demo_single_voice_command():
    """Demo single voice command processing"""
    print("\n" + "="*60)
    print("Voice Orchestrator - Single Command Demo")
    print("="*60 + "\n")
    
    voice_orch = VoiceOrchestrator()
    
    print("Processing voice command: 'Check system status'")
    print("-" * 60)
    
    result = voice_orch.process_voice_input(
        voice_input="Check system status",
        enable_tts=True
    )
    
    if result.get('success'):
        print(f"✅ Response: {result.get('response', 'No response')}")
        if result.get('actions'):
            print(f"🔧 Actions: {result.get('actions')}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")


def main():
    """Main demo function"""
    print("\n" + "="*60)
    print("JarvisX V2 - Unified Feature Integration Demo")
    print("="*60)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "voice":
            demo_voice_mode()
        elif mode == "single":
            demo_single_voice_command()
        elif mode == "text":
            demo_text_commands()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python unified_voice_demo.py [text|voice|single]")
    else:
        # Default: text commands demo
        demo_text_commands()
        
        print("\n" + "="*60)
        print("To try other modes:")
        print("  python unified_voice_demo.py text   - Text commands")
        print("  python unified_voice_demo.py single - Single voice command")
        print("  python unified_voice_demo.py voice  - Continuous voice mode")
        print("="*60 + "\n")


if __name__ == "__main__":
    main()

