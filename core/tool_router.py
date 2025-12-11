#!/usr/bin/env python3
"""
Tool Router - Routes actions to appropriate tools
Intelligently routes extracted actions to the correct tool module
"""

import logging
from typing import Dict, Any, Optional, List
from core.action_extractor import ExtractedAction

logger = logging.getLogger(__name__)


class ToolRouter:
    """
    Routes actions to appropriate tools based on action type and tool name
    """
    
    def __init__(self):
        """Initialize tool router"""
        self.tools = {}
        self._initialize_tools()
        logger.info("Tool Router initialized")
    
    def _initialize_tools(self):
        """Initialize all available tools"""
        # System/Computer Access
        try:
            from core.computer_access import ComputerAccessLayer
            self.tools['system'] = ComputerAccessLayer(safety_mode=True, auto_confirm_safe=True)
            self.tools['file'] = self.tools['system']  # File ops use computer access
            logger.info("✅ ComputerAccessLayer loaded")
        except Exception as e:
            logger.warning(f"ComputerAccessLayer not available: {e}")
            self.tools['system'] = None
            self.tools['file'] = None
        
        # Business Operations
        try:
            from business_mode.business_handler import BusinessModeHandler
            self.tools['business'] = BusinessModeHandler()
            logger.info("✅ BusinessModeHandler loaded")
        except Exception as e:
            logger.warning(f"BusinessModeHandler not available: {e}")
            self.tools['business'] = None
        
        # System Monitoring
        try:
            from system_monitor.resource_monitor import ResourceMonitor
            self.tools['monitor'] = ResourceMonitor()
            logger.info("✅ ResourceMonitor loaded")
        except Exception as e:
            logger.warning(f"ResourceMonitor not available: {e}")
            self.tools['monitor'] = None
        
        # Workflow Orchestration
        try:
            from automation.workflow_orchestrator import WorkflowOrchestrator
            self.tools['workflow'] = WorkflowOrchestrator()
            logger.info("✅ WorkflowOrchestrator loaded")
        except Exception as e:
            logger.warning(f"WorkflowOrchestrator not available: {e}")
            self.tools['workflow'] = None
        
        # RPA Controller
        try:
            from automation.rpa_controller import RPAController
            self.tools['rpa'] = RPAController(safety_mode=True)
            logger.info("✅ RPAController loaded")
        except Exception as e:
            logger.warning(f"RPAController not available: {e}")
            self.tools['rpa'] = None
        
        # CLI Executor
        try:
            from core.cli_executor import CLIExecutor
            self.tools['cli'] = CLIExecutor()
            logger.info("✅ CLIExecutor loaded")
        except Exception as e:
            logger.warning(f"CLIExecutor not available: {e}")
            self.tools['cli'] = None
    
    def route_action(self, action: ExtractedAction) -> Dict[str, Any]:
        """
        Route action to appropriate tool and execute
        
        Args:
            action: Extracted action to route
            
        Returns:
            Execution result dictionary
        """
        try:
            # Get tool for action type
            tool = self._get_tool_for_action(action)
            
            if not tool:
                return {
                    'success': False,
                    'error': f"Tool not available for action type: {action.action_type}",
                    'action_type': action.action_type,
                    'tool': action.tool
                }
            
            # Execute action via tool
            result = self._execute_via_tool(tool, action)
            
            return result
        
        except Exception as e:
            logger.error(f"Error routing action: {e}")
            return {
                'success': False,
                'error': str(e),
                'action_type': action.action_type,
                'tool': action.tool
            }
    
    def _get_tool_for_action(self, action: ExtractedAction):
        """Get appropriate tool for action"""
        action_type = action.action_type
        
        # Direct mapping
        if action_type in self.tools:
            tool = self.tools[action_type]
            if tool is not None:
                return tool
        
        # Special cases
        if action_type == "system" and self.tools.get('system'):
            return self.tools['system']
        
        if action_type == "file" and self.tools.get('file'):
            return self.tools['file']
        
        # Fallback to CLI for unknown actions
        if self.tools.get('cli'):
            logger.info(f"Using CLI executor as fallback for {action_type}")
            return self.tools['cli']
        
        return None
    
    def _execute_via_tool(
        self,
        tool: Any,
        action: ExtractedAction
    ) -> Dict[str, Any]:
        """Execute action via specific tool"""
        action_type = action.action_type
        tool_name = action.tool
        params = action.parameters
        
        try:
            # System/Computer Access
            if action_type in ["system", "file"] and hasattr(tool, 'execute_action'):
                return tool.execute_action(tool_name, params)
            
            # Business Operations
            elif action_type == "business" and hasattr(tool, 'create_invoice'):
                return self._execute_business_action(tool, tool_name, params)
            
            # Workflow Operations
            elif action_type == "workflow" and hasattr(tool, 'execute_workflow'):
                return self._execute_workflow_action(tool, tool_name, params)
            
            # RPA Operations
            elif action_type == "rpa" and hasattr(tool, 'execute_action'):
                return self._execute_rpa_action(tool, tool_name, params)
            
            # CLI Operations
            elif action_type == "cli" and hasattr(tool, 'execute_command'):
                return self._execute_cli_action(tool, tool_name, params)
            
            # Monitor operations (use system tool)
            elif action_type == "system" and tool_name.startswith("monitor"):
                if hasattr(tool, 'execute_action'):
                    return tool.execute_action(tool_name, params)
            
            # Unknown tool/action combination
            return {
                'success': False,
                'error': f"Unknown tool/action combination: {action_type}/{tool_name}",
                'action_type': action_type,
                'tool': tool_name
            }
        
        except Exception as e:
            logger.error(f"Error executing action via tool: {e}")
            return {
                'success': False,
                'error': str(e),
                'action_type': action_type,
                'tool': tool_name
            }
    
    def _execute_business_action(
        self,
        tool: Any,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute business action"""
        try:
            if tool_name == "generate_invoice":
                client_name = params.get('client_name', 'Client')
                items = params.get('items', [{'description': 'Service', 'amount': 100.0}])
                tax_rate = params.get('tax_rate', 0.0)
                invoice_id = tool.create_invoice(client_name, items, tax_rate)
                return {
                    'success': invoice_id is not None,
                    'result': {'invoice_id': invoice_id} if invoice_id else {},
                    'action': 'generate_invoice'
                }
            
            elif tool_name == "add_client":
                name = params.get('client_name') or params.get('name', '')
                email = params.get('email', '')
                company = params.get('company', '')
                client_id = tool.add_client(name, email=email, company=company)
                return {
                    'success': client_id is not None,
                    'result': {'client_id': client_id} if client_id else {},
                    'action': 'add_client'
                }
            
            elif tool_name == "generate_report":
                summary = tool.get_daily_summary()
                return {
                    'success': True,
                    'result': summary,
                    'action': 'generate_report'
                }
            
            elif tool_name == "schedule_task":
                title = params.get('title', 'Task')
                due_date = params.get('due_date', '')
                priority = params.get('priority', 'medium')
                success = tool.create_task(title, due_date, priority)
                return {
                    'success': success,
                    'result': {},
                    'action': 'schedule_task'
                }
            
            else:
                return {
                    'success': False,
                    'error': f"Unknown business action: {tool_name}",
                    'action': tool_name
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': tool_name
            }
    
    def _execute_workflow_action(
        self,
        tool: Any,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute workflow action"""
        try:
            if tool_name == "execute_workflow":
                workflow_id = params.get('workflow_id') or params.get('id', '')
                input_data = params.get('input', {})
                result = tool.execute_workflow(workflow_id, input_data)
                return {
                    'success': result.get('success', False),
                    'result': result,
                    'action': 'execute_workflow'
                }
            
            else:
                return {
                    'success': False,
                    'error': f"Unknown workflow action: {tool_name}",
                    'action': tool_name
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': tool_name
            }
    
    def _execute_rpa_action(
        self,
        tool: Any,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute RPA action"""
        try:
            # RPA actions are handled via execute_action method
            # Map tool_name to RPA action type
            rpa_action_type = tool_name.replace('_', ' ').title()
            return tool.execute_action(rpa_action_type, params)
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': tool_name
            }
    
    def _execute_cli_action(
        self,
        tool: Any,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute CLI action"""
        try:
            # Extract command from params or tool_name
            command = params.get('command', tool_name)
            
            # Execute via CLI executor
            result = tool.execute_command(command, json_output=True)
            
            return {
                'success': result.get('success', False),
                'result': result,
                'action': 'execute_cli'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': tool_name
            }
    
    def get_available_tools(self) -> Dict[str, bool]:
        """Get list of available tools"""
        return {
            'system': self.tools.get('system') is not None,
            'business': self.tools.get('business') is not None,
            'monitor': self.tools.get('monitor') is not None,
            'workflow': self.tools.get('workflow') is not None,
            'rpa': self.tools.get('rpa') is not None,
            'cli': self.tools.get('cli') is not None,
            'file': self.tools.get('file') is not None
        }

