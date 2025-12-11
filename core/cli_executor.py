#!/usr/bin/env python3
"""
CLI Executor - Programmatic execution of CLI commands
Wraps the CLI interface to allow programmatic command execution
"""

import subprocess
import sys
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class CLIExecutor:
    """
    Executes CLI commands programmatically
    Provides interface to run jarvisx-cli commands from code
    """
    
    def __init__(self, cli_module_path: str = "cli.main"):
        """
        Initialize CLI executor
        
        Args:
            cli_module_path: Path to CLI main module (default: cli.main)
        """
        self.cli_module_path = cli_module_path
        self.project_root = Path(__file__).parent.parent
        logger.info("CLI Executor initialized")
    
    def execute_command(
        self,
        command: str,
        args: Optional[List[str]] = None,
        json_output: bool = True,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute a CLI command programmatically
        
        Args:
            command: CLI command (e.g., "training list", "system status")
            args: Additional arguments
            json_output: Request JSON output
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Build command list
            cmd_list = [
                sys.executable,
                "-m",
                self.cli_module_path,
                *command.split()
            ]
            
            if args:
                cmd_list.extend(args)
            
            if json_output:
                cmd_list.append("--json")
            
            logger.info(f"Executing CLI command: {' '.join(cmd_list)}")
            
            # Execute command
            result = subprocess.run(
                cmd_list,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Parse output
            output = result.stdout.strip()
            error = result.stderr.strip()
            
            # Try to parse JSON output
            json_data = None
            if json_output and output:
                try:
                    import json
                    json_data = json.loads(output)
                except json.JSONDecodeError:
                    pass
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'output': output,
                'error': error,
                'json': json_data,
                'command': command
            }
        
        except subprocess.TimeoutExpired:
            logger.error(f"CLI command timed out: {command}")
            return {
                'success': False,
                'error': 'Command execution timed out',
                'command': command
            }
        
        except Exception as e:
            logger.error(f"Error executing CLI command: {e}")
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
    
    def execute_training_command(
        self,
        action: str,
        job_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute training-related CLI command"""
        cmd = f"training {action}"
        args = []
        
        if job_id:
            args.extend(["--job-id", job_id])
        
        for key, value in kwargs.items():
            if value is not None:
                args.extend([f"--{key.replace('_', '-')}", str(value)])
        
        return self.execute_command(cmd, args)
    
    def execute_system_command(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute system-related CLI command"""
        cmd = f"system {action}"
        args = []
        
        for key, value in kwargs.items():
            if value is not None:
                args.extend([f"--{key.replace('_', '-')}", str(value)])
        
        return self.execute_command(cmd, args)
    
    def execute_business_command(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute business-related CLI command"""
        cmd = f"business {action}"
        args = []
        
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, list):
                    args.extend([f"--{key.replace('_', '-')}", ",".join(map(str, value))])
                else:
                    args.extend([f"--{key.replace('_', '-')}", str(value)])
        
        return self.execute_command(cmd, args)
    
    def execute_cloud_command(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute cloud-related CLI command"""
        cmd = f"cloud {action}"
        args = []
        
        for key, value in kwargs.items():
            if value is not None:
                args.extend([f"--{key.replace('_', '-')}", str(value)])
        
        return self.execute_command(cmd, args)
    
    def execute_workflow_command(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute workflow-related CLI command"""
        cmd = f"workflow {action}"
        args = []
        
        for key, value in kwargs.items():
            if value is not None:
                args.extend([f"--{key.replace('_', '-')}", str(value)])
        
        return self.execute_command(cmd, args)
    
    def execute_model_command(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute model-related CLI command"""
        cmd = f"model {action}"
        args = []
        
        for key, value in kwargs.items():
            if value is not None:
                args.extend([f"--{key.replace('_', '-')}", str(value)])
        
        return self.execute_command(cmd, args)

