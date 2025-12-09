"""
Base CLI Classes and Utilities
Common base classes for CLI commands
"""

import os
from typing import Optional
from pathlib import Path
from functools import wraps

import typer
from typer import Option, Context

from cli.utils import CLIOutput, get_project_root
from utils.config import Config
from utils.logger import get_logger as get_logger_util


# Global CLI context
_cli_context = {
    'config': None,
    'output': None,
    'verbose': False,
    'json_output': False
}


def get_cli_context() -> dict:
    """Get global CLI context"""
    return _cli_context


def init_cli_context(
    verbose: bool = False,
    json_output: bool = False,
    config_path: Optional[str] = None,
    voice: bool = False
):
    """Initialize CLI context"""
    _cli_context['verbose'] = verbose
    _cli_context['json_output'] = json_output
    _cli_context['voice'] = voice
    
    # Initialize config
    if config_path:
        _cli_context['config'] = Config(config_path)
    else:
        _cli_context['config'] = Config()
    
    # Initialize output handler
    _cli_context['output'] = CLIOutput(
        use_rich=True,
        json_output=json_output,
        voice=voice
    )
    
    # Set logging level based on verbose
    log_level = "DEBUG" if verbose else "INFO"
    _cli_context['logger'] = get_logger_util(__name__, log_level)


def get_config() -> Config:
    """Get configuration instance"""
    if _cli_context.get('config') is None:
        _cli_context['config'] = Config()
    return _cli_context['config']


def get_output() -> CLIOutput:
    """Get output handler"""
    if _cli_context['output'] is None:
        _cli_context['output'] = CLIOutput()
    return _cli_context['output']


def get_logger():
    """Get logger instance"""
    if 'logger' not in _cli_context:
        _cli_context['logger'] = get_logger_util(__name__)
    return _cli_context['logger']


# Common options decorator
def common_options(func):
    """Decorator to add common options to commands"""
    @wraps(func)
    @Option('--verbose', '-v', is_flag=True, help='Enable verbose output')
    @Option('--json', is_flag=True, help='Output in JSON format')
    @Option('--config', help='Path to configuration file')
    def wrapper(*args, verbose: bool = False, json: bool = False, config: Optional[str] = None, **kwargs):
        init_cli_context(verbose=verbose, json_output=json, config_path=config)
        return func(*args, **kwargs)
    return wrapper


# Typer callback for common options
def common_callback(
    ctx: Context,
    verbose: bool = Option(False, '--verbose', '-v', help='Enable verbose output'),
    json_output: bool = Option(False, '--json', help='Output in JSON format'),
    config: Optional[str] = Option(None, '--config', help='Path to configuration file'),
    voice: bool = Option(False, '--voice', help='Enable voice output (TTS)')
):
    """Common callback for CLI commands"""
    init_cli_context(verbose=verbose, json_output=json_output, config_path=config, voice=voice)
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['json_output'] = json_output
    ctx.obj['voice'] = voice
    ctx.obj['config'] = get_config()


class BaseCommand:
    """Base class for CLI commands"""
    
    def __init__(self):
        self.config = get_config()
        self.output = get_output()
        self.logger = get_logger()
        self.project_root = get_project_root()
    
    def validate_project_root(self) -> bool:
        """Validate that we're in the project root"""
        # Check for key project files
        required_files = ['main.py', 'requirements.txt', 'README.md']
        for file in required_files:
            if not (self.project_root / file).exists():
                self.output.error(f"Project file not found: {file}")
                self.output.info(f"Current directory: {self.project_root}")
                return False
        return True

