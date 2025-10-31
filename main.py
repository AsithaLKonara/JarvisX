#!/usr/bin/env python3
"""
Jarvis X V2 - Main Entry Point
CLI Mode: Pure text input/output
Prepared for LLM Brain Integration (Next Phase)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for Jarvis X V2"""
    try:
        # Import and run CLI interface
        from cli_interface import main as cli_main
        cli_main()
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

