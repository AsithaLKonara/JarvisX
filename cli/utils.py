"""
CLI Utility Functions
Helper functions for output formatting, colors, and common operations
"""

import json
import sys
from typing import Any, Dict, Optional
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


class CLIOutput:
    """Handles CLI output formatting with Rich or fallback to ANSI colors"""
    
    def __init__(self, use_rich: bool = True, json_output: bool = False, voice: bool = False):
        self.use_rich = use_rich and RICH_AVAILABLE
        self.json_output = json_output
        self.voice = voice
        self.console = Console() if self.use_rich else None
        self.tts_engine = None
        
        # Initialize TTS if voice mode enabled
        if self.voice:
            try:
                from speech.text_to_speech import TTSEngine
                import os
                tts_engine_name = os.getenv('TTS_ENGINE', 'pyttsx3')
                self.tts_engine = TTSEngine(engine=tts_engine_name)
                if not self.tts_engine.is_available:
                    self.tts_engine = None
            except Exception:
                self.tts_engine = None
    
    def success(self, message: str):
        """Print success message"""
        if self.json_output:
            self._print_json({"status": "success", "message": message})
        elif self.use_rich:
            self.console.print(f"[green]✓[/green] {message}")
        else:
            print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
        
        # Voice output
        if self.voice and self.tts_engine and not self.json_output:
            try:
                self.tts_engine.speak(message, blocking=False)
            except Exception:
                pass  # Ignore TTS errors
    
    def error(self, message: str):
        """Print error message"""
        if self.json_output:
            self._print_json({"status": "error", "message": message})
        elif self.use_rich:
            self.console.print(f"[red]✗[/red] {message}")
        else:
            print(f"{Colors.RED}✗{Colors.RESET} {message}")
        
        # Voice output
        if self.voice and self.tts_engine and not self.json_output:
            try:
                self.tts_engine.speak(f"Error: {message}", blocking=False)
            except Exception:
                pass
    
    def warning(self, message: str):
        """Print warning message"""
        if self.json_output:
            self._print_json({"status": "warning", "message": message})
        elif self.use_rich:
            self.console.print(f"[yellow]⚠[/yellow] {message}")
        else:
            print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")
    
    def info(self, message: str):
        """Print info message"""
        if self.json_output:
            self._print_json({"status": "info", "message": message})
        elif self.use_rich:
            self.console.print(f"[blue]ℹ[/blue] {message}")
        else:
            print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")
        
        # Voice output (only for important info, not verbose)
        if self.voice and self.tts_engine and not self.json_output and len(message) < 100:
            try:
                self.tts_engine.speak(message, blocking=False)
            except Exception:
                pass
    
    def print_table(self, data: list, headers: list, title: Optional[str] = None):
        """Print data as a table"""
        if self.json_output:
            self._print_json({"data": data, "headers": headers})
        elif self.use_rich:
            table = Table(box=box.ROUNDED)
            for header in headers:
                table.add_column(header, style="cyan")
            for row in data:
                table.add_row(*[str(cell) for cell in row])
            if title:
                self.console.print(Panel(table, title=title))
            else:
                self.console.print(table)
        else:
            # Simple text table
            if title:
                print(f"\n{Colors.BOLD}{title}{Colors.RESET}")
            print(" | ".join(headers))
            print("-" * (sum(len(h) for h in headers) + len(headers) * 3))
            for row in data:
                print(" | ".join(str(cell) for cell in row))
    
    def print_panel(self, content: str, title: Optional[str] = None, style: str = "blue"):
        """Print content in a panel"""
        if self.json_output:
            self._print_json({"title": title, "content": content})
        elif self.use_rich:
            self.console.print(Panel(content, title=title, border_style=style))
        else:
            if title:
                print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
                print("=" * len(title))
            print(content)
    
    def print_json(self, data: Any):
        """Print data as JSON"""
        print(json.dumps(data, indent=2, default=str))
    
    def _print_json(self, data: Any):
        """Internal method to print JSON"""
        self.print_json(data)
    
    def print_dict(self, data: Dict[str, Any], title: Optional[str] = None):
        """Print dictionary as formatted output"""
        if self.json_output:
            self._print_json(data)
        elif self.use_rich:
            if title:
                self.console.print(f"\n[bold cyan]{title}[/bold cyan]")
            for key, value in data.items():
                self.console.print(f"  [cyan]{key}:[/cyan] {value}")
        else:
            if title:
                print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
            for key, value in data.items():
                print(f"  {Colors.CYAN}{key}:{Colors.RESET} {value}")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def validate_config_file(config_path: str) -> bool:
    """Validate configuration file exists and is readable"""
    path = Path(config_path)
    if not path.exists():
        return False
    if not path.is_file():
        return False
    try:
        with open(path, 'r') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, IOError):
        return False


def get_project_root() -> Path:
    """Get the project root directory"""
    current = Path(__file__).resolve()
    # Go up from cli/utils.py to project root
    return current.parent.parent


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if not"""
    path.mkdir(parents=True, exist_ok=True)
    return path

