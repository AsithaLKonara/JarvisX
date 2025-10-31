#!/usr/bin/env python3
"""
Jarvis X v2 - Simple CLI Interface
Pure text input/output - Prepared for LLM Brain Integration
Phase: CLI-Only Mode (Pre-LLM Integration)
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Load environment variables from .env FIRST
env_file = Path('.env')
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from core.command_parser import CommandParser
from utils.config import Config
from utils.logger import get_logger

# Try to import Hybrid Brain, fallback to basic AI Engine
try:
    from core.hybrid_brain import HybridBrain
    USE_HYBRID = True
except ImportError:
    from core.ai_engine import AIEngine
    USE_HYBRID = False

logger = get_logger(__name__)


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class CLIJarvis:
    """Simple CLI-based Jarvis interface - Pure text I/O"""
    
    def __init__(self):
        """Initialize CLI Jarvis"""
        self.print_banner()
        
        print(f"\n{Colors.CYAN}[INIT]{Colors.RESET} Loading configuration...")
        self.config = Config()
        
        print(f"{Colors.CYAN}[INIT]{Colors.RESET} Initializing AI Brain System...")
        if USE_HYBRID:
            self.ai_engine = HybridBrain(self.config)
            brain_type = "Hybrid Brain (Custom LLM + HelaGPT)"
            print(f"{Colors.GREEN}[BRAIN]{Colors.RESET} ✓ Hybrid Brain System loaded")
        else:
            from core.ai_engine import AIEngine
            self.ai_engine = AIEngine(self.config)
            brain_type = "HelaGPT Only"
            print(f"{Colors.YELLOW}[BRAIN]{Colors.RESET} ⚠ Using HelaGPT only (Hybrid brain not available)")
        
        print(f"{Colors.CYAN}[INIT]{Colors.RESET} Initializing Command Parser...")
        self.command_parser = CommandParser()
        
        self.brain_type = brain_type
        print(f"{Colors.GREEN}[READY]{Colors.RESET} CLI Mode Active - {brain_type}")
        
        self.print_status()
    
    def print_banner(self):
        """Print application banner"""
        banner = f"""
{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           🤖 JARVIS X V2 - AI DESKTOP ASSISTANT 🤖              ║
║                     CLI MODE - v3.0.0                           ║
║                                                                  ║
║         Pure Text I/O | Prepared for LLM Brain Integration     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.RESET}
        """
        print(banner)
    
    def print_status(self):
        """Print system status"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.RESET}")
        print(f"{Colors.GREEN}SYSTEM STATUS{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.RESET}")
        
        # AI Brain System
        print(f"\n{Colors.BLUE}[AI BRAIN SYSTEM]{Colors.RESET}")
        print(f"  Type: {Colors.GREEN}{self.brain_type}{Colors.RESET}")
        print(f"  State: {self.ai_engine.get_current_state()}")
        
        # Show hybrid brain statistics if available
        if USE_HYBRID and hasattr(self.ai_engine, 'get_statistics'):
            stats = self.ai_engine.get_statistics()
            print(f"\n{Colors.BLUE}[BRAIN STATUS]{Colors.RESET}")
            print(f"  Custom LLM: {'✓ Available' if stats['llm_available'] else '✗ Not available (training in progress)'}")
            print(f"  HelaGPT: {'✓ Available' if stats['helagpt_available'] else '✗ Not available'}")
            if stats['total_calls'] > 0:
                print(f"\n{Colors.BLUE}[USAGE STATS]{Colors.RESET}")
                print(f"  Total queries: {stats['total_calls']}")
                print(f"  LLM calls: {stats['llm_calls']} ({stats['llm_success_rate']:.1f}% success)")
                print(f"  HelaGPT calls: {stats['helagpt_calls']} ({stats['helagpt_success_rate']:.1f}% success)")
                print(f"  Fallback used: {stats['fallback_used']} times")
        else:
            # Basic AI Engine info
            if hasattr(self.ai_engine, 'api_key'):
                print(f"  HelaGPT API: {'✓ Configured' if self.ai_engine.api_key else '✗ Not configured'}")
        
        # CLI Mode
        print(f"\n{Colors.BLUE}[INTERFACE MODE]{Colors.RESET}")
        print(f"  Mode: {Colors.GREEN}CLI (Text Input/Output){Colors.RESET}")
        print(f"  Voice I/O: {Colors.YELLOW}Disabled (Planned for Phase 3){Colors.RESET}")
        print(f"  Avatar UI: {Colors.YELLOW}Disabled (Planned for Phase 4){Colors.RESET}")
        
        # System Info
        print(f"\n{Colors.BLUE}[SYSTEM INFO]{Colors.RESET}")
        import platform
        print(f"  OS: {platform.system()} {platform.release()}")
        print(f"  Python: {platform.python_version()}")
        print(f"  Architecture: {platform.machine()}")
        
        # Next Phase Info
        print(f"\n{Colors.BLUE}[NEXT PHASE]{Colors.RESET}")
        print(f"  Status: {Colors.CYAN}Awaiting LLM Brain Integration{Colors.RESET}")
        print(f"  LLM Training: {Colors.GREEN}In Progress{Colors.RESET}")
        print(f"  Post-LLM: Voice I/O + Avatar UI Integration")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.RESET}\n")
    
    def print_welcome(self):
        """Print welcome message"""
        print(f"""
{Colors.BOLD}{Colors.CYAN}Welcome to Jarvis X v2 CLI!{Colors.RESET}

Available commands:
  • Type any message to chat with Jarvis
  • "help" - Show this help message
  • "status" - Show system status
  • "exit" - Exit the application

{Colors.CYAN}Mode: CLI-Only (Text Input/Output){Colors.RESET}
{Colors.YELLOW}Next Phase: LLM Brain Integration → Voice I/O → Avatar UI{Colors.RESET}
        """)
    
    def log_input(self, user_input: str):
        """Log user input"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n{Colors.CYAN}[{timestamp}]{Colors.RESET} {Colors.BOLD}USER INPUT:{Colors.RESET}")
        print(f"  {user_input}")
    
    def log_parsing(self, parsed: dict):
        """Log command parsing"""
        print(f"\n{Colors.CYAN}[PARSING]{Colors.RESET}")
        print(f"  Command: {parsed.get('command')}")
        print(f"  Intent: {parsed.get('intent')}")
        print(f"  Confidence: {parsed.get('confidence'):.2f}")
        if parsed.get('parameters'):
            print(f"  Parameters: {parsed.get('parameters')}")
    
    def log_ai_processing(self):
        """Log AI processing"""
        print(f"\n{Colors.CYAN}[AI PROCESSING]{Colors.RESET}")
        print(f"  State: {self.ai_engine.get_current_state()}")
    
    def log_emotion(self, emotion: str, confidence: float):
        """Log detected emotion"""
        if emotion:
            print(f"\n{Colors.CYAN}[EMOTION DETECTION]{Colors.RESET}")
            print(f"  Detected Emotion: {emotion}")
            print(f"  Confidence: {confidence:.2f}")
    
    def log_response(self, response: str):
        """Log AI response"""
        print(f"\n{Colors.CYAN}[AI RESPONSE]{Colors.RESET}")
        print(f"  {Colors.GREEN}{response}{Colors.RESET}")
    
    def run(self):
        """Run the CLI interface"""
        self.print_welcome()
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n{Colors.BOLD}{Colors.CYAN}You: {Colors.RESET}").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == "exit":
                    print(f"\n{Colors.YELLOW}Goodbye!{Colors.RESET}")
                    break
                elif user_input.lower() == "help":
                    self.print_welcome()
                    continue
                elif user_input.lower() == "status":
                    self.print_status()
                    continue
                
                # Log input
                self.log_input(user_input)
                
                # Parse command
                parsed = self.command_parser.parse(user_input)
                self.log_parsing(parsed)
                
                # Process with AI
                self.log_ai_processing()
                response = self.ai_engine.get_response(user_input)
                
                # Log emotion if detected
                emotion = self.ai_engine.get_last_emotion()
                confidence = self.ai_engine.get_confidence_score()
                self.log_emotion(emotion, confidence)
                
                # Log response (text only - no TTS)
                self.log_response(response)
                
                print(f"\n{Colors.CYAN}[STATE]{Colors.RESET} Current state: {self.ai_engine.get_current_state()}")
            
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
                break
            except Exception as e:
                print(f"\n{Colors.RED}[ERROR]{Colors.RESET} {e}")
                logger.error(f"Error: {e}", exc_info=True)


def main():
    """Main entry point"""
    try:
        cli = CLIJarvis()
        cli.run()
    except Exception as e:
        print(f"{Colors.RED}[FATAL ERROR]{Colors.RESET} {e}")
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
