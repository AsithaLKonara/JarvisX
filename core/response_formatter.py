#!/usr/bin/env python3
"""
Response Formatter - Formats execution results into natural language responses
Converts tool execution results into user-friendly text for TTS output
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """
    Formats action execution results into natural language responses
    """
    
    def __init__(self):
        """Initialize response formatter"""
        self.success_phrases = [
            "Done!",
            "Completed successfully.",
            "All set!",
            "Finished.",
            "Successfully completed."
        ]
        self.error_phrases = [
            "I encountered an error.",
            "Something went wrong.",
            "Unable to complete that.",
            "There was a problem."
        ]
        logger.info("Response Formatter initialized")
    
    def format_action_result(
        self,
        action_type: str,
        tool: str,
        result: Dict[str, Any],
        user_input: str = ""
    ) -> str:
        """
        Format action execution result into natural language
        
        Args:
            action_type: Type of action (system, business, file, etc.)
            tool: Specific tool used
            result: Execution result dictionary
            user_input: Original user input for context
            
        Returns:
            Formatted response string
        """
        if not result:
            return "I couldn't get a result from that action."
        
        success = result.get('success', False)
        
        if success:
            return self.format_success(action_type, tool, result, user_input)
        else:
            return self.format_error(action_type, tool, result, user_input)
    
    def format_success(
        self,
        action_type: str,
        tool: str,
        result: Dict[str, Any],
        user_input: str = ""
    ) -> str:
        """Format successful action result"""
        import random
        
        response_parts = [random.choice(self.success_phrases)]
        
        # Format based on action type
        if action_type == "system":
            response_parts.append(self._format_system_result(tool, result))
        elif action_type == "business":
            response_parts.append(self._format_business_result(tool, result))
        elif action_type == "file":
            response_parts.append(self._format_file_result(tool, result))
        elif action_type == "workflow":
            response_parts.append(self._format_workflow_result(tool, result))
        elif action_type == "cli":
            response_parts.append(self._format_cli_result(tool, result))
        else:
            # Generic success message
            if 'message' in result:
                response_parts.append(result['message'])
            elif 'result' in result:
                response_parts.append(str(result['result']))
        
        return " ".join(response_parts)
    
    def format_error(
        self,
        action_type: str,
        tool: str,
        result: Dict[str, Any],
        user_input: str = ""
    ) -> str:
        """Format error result"""
        import random
        
        response_parts = [random.choice(self.error_phrases)]
        
        error_msg = result.get('error', 'Unknown error')
        if error_msg:
            response_parts.append(f"Error: {error_msg}")
        
        # Add helpful suggestions
        suggestion = self._get_error_suggestion(action_type, tool, error_msg)
        if suggestion:
            response_parts.append(suggestion)
        
        return " ".join(response_parts)
    
    def _format_system_result(self, tool: str, result: Dict[str, Any]) -> str:
        """Format system operation results"""
        if tool == "monitor_cpu":
            cpu_info = result.get('result', {})
            if isinstance(cpu_info, dict):
                percent = cpu_info.get('percent', 0)
                return f"CPU usage is {percent:.1f} percent."
            return "Retrieved CPU information."
        
        elif tool == "monitor_memory":
            mem_info = result.get('result', {})
            if isinstance(mem_info, dict):
                percent = mem_info.get('percent', 0)
                used = mem_info.get('used', 0)
                total = mem_info.get('total', 0)
                if used and total:
                    used_gb = used / (1024**3)
                    total_gb = total / (1024**3)
                    return f"Memory usage is {percent:.1f} percent. Using {used_gb:.1f} gigabytes out of {total_gb:.1f}."
            return "Retrieved memory information."
        
        elif tool == "monitor_disk":
            disk_info = result.get('result', {})
            if isinstance(disk_info, dict):
                percent = disk_info.get('percent', 0)
                return f"Disk usage is {percent:.1f} percent."
            return "Retrieved disk information."
        
        elif tool == "list_processes":
            processes = result.get('result', [])
            if isinstance(processes, list):
                count = len(processes)
                return f"Found {count} running processes."
            return "Retrieved process list."
        
        elif tool == "optimize_system":
            return "System optimization completed."
        
        elif tool == "screenshot":
            path = result.get('result', {}).get('path', '')
            if path:
                return f"Screenshot saved to {path}."
            return "Screenshot captured."
        
        return "System operation completed."
    
    def _format_business_result(self, tool: str, result: Dict[str, Any]) -> str:
        """Format business operation results"""
        if tool == "generate_invoice":
            invoice_id = result.get('result', {}).get('invoice_id', '')
            if invoice_id:
                return f"Invoice {invoice_id} generated successfully."
            return "Invoice generated."
        
        elif tool == "add_client":
            client_id = result.get('result', {}).get('client_id', '')
            if client_id:
                return f"Client added with ID {client_id}."
            return "Client added successfully."
        
        elif tool == "generate_report":
            return "Report generated successfully."
        
        elif tool == "schedule_task":
            task_id = result.get('result', {}).get('task_id', '')
            if task_id:
                return f"Task scheduled with ID {task_id}."
            return "Task scheduled successfully."
        
        elif tool == "export_data":
            path = result.get('result', {}).get('path', '')
            if path:
                return f"Data exported to {path}."
            return "Data exported successfully."
        
        return "Business operation completed."
    
    def _format_file_result(self, tool: str, result: Dict[str, Any]) -> str:
        """Format file operation results"""
        if tool == "read_file":
            content = result.get('result', {}).get('content', '')
            if content:
                lines = len(content.split('\n'))
                return f"Read file with {lines} lines."
            return "File read successfully."
        
        elif tool == "write_file":
            path = result.get('result', {}).get('path', '')
            if path:
                return f"File written to {path}."
            return "File written successfully."
        
        elif tool == "list_directory":
            files = result.get('result', {}).get('files', [])
            if isinstance(files, list):
                count = len(files)
                return f"Found {count} items in directory."
            return "Directory listed successfully."
        
        elif tool == "delete_file":
            return "File deleted successfully."
        
        elif tool == "search_files":
            files = result.get('result', {}).get('files', [])
            if isinstance(files, list):
                count = len(files)
                return f"Found {count} matching files."
            return "File search completed."
        
        return "File operation completed."
    
    def _format_workflow_result(self, tool: str, result: Dict[str, Any]) -> str:
        """Format workflow execution results"""
        if tool == "execute_workflow":
            workflow_name = result.get('result', {}).get('workflow_name', '')
            if workflow_name:
                return f"Workflow {workflow_name} executed successfully."
            return "Workflow executed successfully."
        
        return "Workflow operation completed."
    
    def _format_cli_result(self, tool: str, result: Dict[str, Any]) -> str:
        """Format CLI command execution results"""
        output = result.get('result', {}).get('output', '')
        if output:
            # Truncate long outputs
            if len(output) > 200:
                output = output[:200] + "..."
            return f"Command output: {output}."
        return "Command executed successfully."
    
    def _get_error_suggestion(self, action_type: str, tool: str, error: str) -> Optional[str]:
        """Get helpful suggestion for error"""
        error_lower = error.lower()
        
        if "permission" in error_lower or "access" in error_lower:
            return "You may need administrator permissions for this action."
        
        if "not found" in error_lower or "does not exist" in error_lower:
            return "The requested resource was not found. Please check the path or name."
        
        if "timeout" in error_lower:
            return "The operation timed out. Please try again."
        
        if "network" in error_lower or "connection" in error_lower:
            return "There seems to be a network issue. Please check your connection."
        
        return None
    
    def format_multiple_results(self, results: List[Dict[str, Any]]) -> str:
        """Format multiple action results"""
        if not results:
            return "No results to report."
        
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)
        
        if success_count == total_count:
            return f"All {total_count} operations completed successfully."
        elif success_count > 0:
            return f"{success_count} out of {total_count} operations completed successfully."
        else:
            return "None of the operations completed successfully."
    
    def format_conversational_response(self, ai_response: str, has_actions: bool = False) -> str:
        """Format conversational AI response (when no actions)"""
        if has_actions:
            # If actions were executed, keep response concise
            return ai_response[:500]  # Truncate long responses
        return ai_response

