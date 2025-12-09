"""
Enhanced Error Handling
Improved error messages with codes and troubleshooting suggestions
"""

from typing import Dict, Optional, Tuple
import traceback


class ErrorCode:
    """Error code constants"""
    # General errors
    UNKNOWN_ERROR = "ERR_0001"
    CONFIGURATION_ERROR = "ERR_0002"
    PERMISSION_ERROR = "ERR_0003"
    
    # CLI errors
    COMMAND_NOT_FOUND = "ERR_1001"
    INVALID_ARGUMENT = "ERR_1002"
    MISSING_REQUIRED_ARG = "ERR_1003"
    
    # File system errors
    FILE_NOT_FOUND = "ERR_2001"
    FILE_READ_ERROR = "ERR_2002"
    FILE_WRITE_ERROR = "ERR_2003"
    DIRECTORY_NOT_FOUND = "ERR_2004"
    
    # Network errors
    CONNECTION_ERROR = "ERR_3001"
    TIMEOUT_ERROR = "ERR_3002"
    API_ERROR = "ERR_3003"
    
    # Model errors
    MODEL_NOT_FOUND = "ERR_4001"
    MODEL_LOAD_ERROR = "ERR_4002"
    MODEL_INFERENCE_ERROR = "ERR_4003"
    
    # Training errors
    TRAINING_CONFIG_ERROR = "ERR_5001"
    TRAINING_FAILED = "ERR_5002"
    JOB_NOT_FOUND = "ERR_5003"


ERROR_TROUBLESHOOTING: Dict[str, Dict[str, any]] = {
    ErrorCode.CONFIGURATION_ERROR: {
        "message": "Configuration error detected",
        "suggestions": [
            "Check your configuration file exists and is valid JSON/YAML",
            "Run 'jarvisx-cli config validate' to check configuration",
            "Verify all required configuration keys are present"
        ]
    },
    ErrorCode.COMMAND_NOT_FOUND: {
        "message": "Command not found",
        "suggestions": [
            "Check the command spelling",
            "Run 'jarvisx-cli --help' to see available commands",
            "Verify you're using the correct command group"
        ]
    },
    ErrorCode.FILE_NOT_FOUND: {
        "message": "File not found",
        "suggestions": [
            "Verify the file path is correct",
            "Check file permissions",
            "Ensure the file exists in the specified location"
        ]
    },
    ErrorCode.CONNECTION_ERROR: {
        "message": "Connection error",
        "suggestions": [
            "Check your internet connection",
            "Verify the server URL is correct",
            "Check firewall settings",
            "Try again in a few moments"
        ]
    },
    ErrorCode.MODEL_NOT_FOUND: {
        "message": "Model not found",
        "suggestions": [
            "Verify the model name is correct",
            "Run 'jarvisx-cli model list' to see available models",
            "Check if the model needs to be downloaded first"
        ]
    },
    ErrorCode.TRAINING_FAILED: {
        "message": "Training failed",
        "suggestions": [
            "Check training logs for detailed error information",
            "Verify training configuration is valid",
            "Ensure sufficient disk space and memory",
            "Check GPU/CPU availability if required"
        ]
    }
}


def get_error_info(error: Exception, error_code: Optional[str] = None) -> Tuple[str, str, list]:
    """
    Get enhanced error information
    
    Args:
        error: The exception
        error_code: Optional error code
        
    Returns:
        Tuple of (error_code, message, suggestions)
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    # Try to determine error code from error type
    if not error_code:
        if "FileNotFoundError" in error_type or "file" in error_message.lower():
            error_code = ErrorCode.FILE_NOT_FOUND
        elif "PermissionError" in error_type or "permission" in error_message.lower():
            error_code = ErrorCode.PERMISSION_ERROR
        elif "ConnectionError" in error_type or "connection" in error_message.lower():
            error_code = ErrorCode.CONNECTION_ERROR
        elif "TimeoutError" in error_type or "timeout" in error_message.lower():
            error_code = ErrorCode.TIMEOUT_ERROR
        elif "KeyError" in error_type or "config" in error_message.lower():
            error_code = ErrorCode.CONFIGURATION_ERROR
        else:
            error_code = ErrorCode.UNKNOWN_ERROR
    
    # Get troubleshooting info
    troubleshooting = ERROR_TROUBLESHOOTING.get(error_code, {
        "message": error_message,
        "suggestions": [
            "Check the error message above for details",
            "Review the documentation for this command",
            "Run the command with --verbose for more information"
        ]
    })
    
    return error_code, troubleshooting["message"], troubleshooting["suggestions"]


def format_error(error: Exception, error_code: Optional[str] = None, verbose: bool = False) -> str:
    """
    Format error with enhanced information
    
    Args:
        error: The exception
        error_code: Optional error code
        verbose: Include full traceback
        
    Returns:
        Formatted error string
    """
    code, message, suggestions = get_error_info(error, error_code)
    
    lines = [
        f"[bold red]Error {code}:[/bold red] {message}",
        f"[dim]{str(error)}[/dim]",
        "",
        "[bold yellow]Troubleshooting:[/bold yellow]"
    ]
    
    for i, suggestion in enumerate(suggestions, 1):
        lines.append(f"  {i}. {suggestion}")
    
    if verbose:
        lines.append("")
        lines.append("[bold]Full Traceback:[/bold]")
        lines.append(traceback.format_exc())
    
    return "\n".join(lines)

