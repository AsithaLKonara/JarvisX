"""
JARVIS AI - Workflow Orchestrator
Enhanced n8n workflow integration with AI-driven automation.
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import time

class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NodeType(Enum):
    """n8n node types."""
    TRIGGER = "trigger"
    ACTION = "action"
    AI_ROUTER = "ai_router"
    DECISION = "decision"
    DATA_TRANSFORM = "data_transform"
    API_CALL = "api_call"
    NOTIFICATION = "notification"

@dataclass
class WorkflowNode:
    """n8n workflow node."""
    node_id: str
    name: str
    type: NodeType
    parameters: Dict[str, Any]
    position: Tuple[int, int]
    connections: List[str] = None
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []

@dataclass
class WorkflowExecution:
    """Workflow execution record."""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    start_time: datetime
    end_time: datetime = None
    input_data: Dict[str, Any] = None
    output_data: Dict[str, Any] = None
    error_message: str = None
    
    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if self.output_data is None:
            self.output_data = {}

class WorkflowOrchestrator:
    """
    Enhanced workflow orchestrator for n8n integration.
    Provides AI-driven workflow management and execution.
    """
    
    def __init__(self, n8n_base_url: str = "http://localhost:5678"):
        """Initialize workflow orchestrator."""
        self.logger = logging.getLogger(__name__)
        self.n8n_base_url = n8n_base_url
        self.api_key = None
        self.workflows = {}
        self.executions = {}
        self.ai_nodes = {}
        
        # Load n8n workflows
        self._load_n8n_workflows()
        
        self.logger.info("Workflow Orchestrator initialized")
    
    def _load_n8n_workflows(self):
        """Load n8n workflows from the workflows directory."""
        try:
            workflows_dir = Path("n8n-workflows-main")
            if not workflows_dir.exists():
                self.logger.warning("n8n-workflows-main directory not found")
                return
            
            # Find workflow files
            workflow_files = list(workflows_dir.rglob("*.json"))
            self.logger.info(f"Found {len(workflow_files)} workflow files")
            
            for workflow_file in workflow_files:
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        workflow_data = json.load(f)
                    
                    # Extract workflow information
                    workflow_id = workflow_data.get('id', f"workflow_{len(self.workflows)}")
                    workflow_name = workflow_data.get('name', 'Unnamed Workflow')
                    
                    # Parse nodes
                    nodes = []
                    for node_data in workflow_data.get('nodes', []):
                        node = self._parse_workflow_node(node_data)
                        if node:
                            nodes.append(node)
                    
                    # Store workflow
                    self.workflows[workflow_id] = {
                        'id': workflow_id,
                        'name': workflow_name,
                        'nodes': nodes,
                        'connections': workflow_data.get('connections', {}),
                        'active': workflow_data.get('active', False),
                        'file_path': str(workflow_file)
                    }
                
                except Exception as e:
                    self.logger.error(f"Error loading workflow {workflow_file}: {e}")
            
            self.logger.info(f"Loaded {len(self.workflows)} workflows")
        
        except Exception as e:
            self.logger.error(f"Error loading n8n workflows: {e}")
    
    def _parse_workflow_node(self, node_data: Dict[str, Any]) -> Optional[WorkflowNode]:
        """Parse n8n node data into WorkflowNode."""
        try:
            node_id = node_data.get('id')
            name = node_data.get('name', 'Unnamed Node')
            node_type_str = node_data.get('type', 'unknown')
            
            # Map n8n node types to our enum
            node_type_mapping = {
                'n8n-nodes-base.start': NodeType.TRIGGER,
                'n8n-nodes-base.httpRequest': NodeType.API_CALL,
                'n8n-nodes-base.if': NodeType.DECISION,
                'n8n-nodes-base.set': NodeType.DATA_TRANSFORM,
                'n8n-nodes-base.emailSend': NodeType.NOTIFICATION,
                'n8n-nodes-base.slack': NodeType.NOTIFICATION,
                'n8n-nodes-base.webhook': NodeType.TRIGGER,
                'n8n-nodes-base.cron': NodeType.TRIGGER,
                'n8n-nodes-base.merge': NodeType.DATA_TRANSFORM,
                'n8n-nodes-base.function': NodeType.ACTION,
                'n8n-nodes-base.code': NodeType.ACTION
            }
            
            node_type = node_type_mapping.get(node_type_str, NodeType.ACTION)
            
            # Extract parameters
            parameters = node_data.get('parameters', {})
            
            # Extract position
            position = node_data.get('position', [0, 0])
            if isinstance(position, list) and len(position) >= 2:
                position = (position[0], position[1])
            else:
                position = (0, 0)
            
            # Extract connections
            connections = []
            for connection in node_data.get('connections', {}).values():
                for conn in connection:
                    if isinstance(conn, dict) and 'node' in conn:
                        connections.append(conn['node'])
            
            return WorkflowNode(
                node_id=node_id,
                name=name,
                type=node_type,
                parameters=parameters,
                position=position,
                connections=connections
            )
        
        except Exception as e:
            self.logger.error(f"Error parsing workflow node: {e}")
            return None
    
    def get_workflows(self, category: str = None) -> List[Dict[str, Any]]:
        """Get available workflows, optionally filtered by category."""
        try:
            workflows = []
            
            for workflow_id, workflow_data in self.workflows.items():
                workflow_info = {
                    'id': workflow_id,
                    'name': workflow_data['name'],
                    'node_count': len(workflow_data['nodes']),
                    'active': workflow_data['active'],
                    'categories': self._categorize_workflow(workflow_data),
                    'description': self._generate_workflow_description(workflow_data)
                }
                
                if category is None or category in workflow_info['categories']:
                    workflows.append(workflow_info)
            
            return workflows
        
        except Exception as e:
            self.logger.error(f"Error getting workflows: {e}")
            return []
    
    def _categorize_workflow(self, workflow_data: Dict[str, Any]) -> List[str]:
        """Categorize workflow based on its nodes and purpose."""
        try:
            categories = []
            nodes = workflow_data.get('nodes', [])
            
            # Analyze node types to determine categories
            node_types = [node.get('type', '') for node in nodes]
            
            if any('email' in node_type.lower() for node_type in node_types):
                categories.append('email_automation')
            
            if any('slack' in node_type.lower() for node_type in node_types):
                categories.append('team_communication')
            
            if any('webhook' in node_type.lower() for node_type in node_types):
                categories.append('api_integration')
            
            if any('cron' in node_type.lower() for node_type in node_types):
                categories.append('scheduled_tasks')
            
            if any('http' in node_type.lower() for node_type in node_types):
                categories.append('data_processing')
            
            if any('function' in node_type.lower() or 'code' in node_type.lower() for node_type in node_types):
                categories.append('custom_logic')
            
            # Default category
            if not categories:
                categories.append('general')
            
            return categories
        
        except Exception as e:
            self.logger.error(f"Error categorizing workflow: {e}")
            return ['general']
    
    def _generate_workflow_description(self, workflow_data: Dict[str, Any]) -> str:
        """Generate human-readable description for workflow."""
        try:
            name = workflow_data.get('name', 'Unnamed Workflow')
            node_count = len(workflow_data.get('nodes', []))
            categories = self._categorize_workflow(workflow_data)
            
            description = f"{name} - {node_count} nodes"
            
            if categories:
                description += f" - Categories: {', '.join(categories)}"
            
            return description
        
        except Exception as e:
            self.logger.error(f"Error generating workflow description: {e}")
            return "Workflow description unavailable"
    
    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow with given input data."""
        try:
            if workflow_id not in self.workflows:
                return {'success': False, 'error': f'Workflow {workflow_id} not found'}
            
            workflow_data = self.workflows[workflow_id]
            execution_id = f"exec_{int(datetime.now().timestamp())}"
            
            # Create execution record
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.RUNNING,
                start_time=datetime.now(),
                input_data=input_data or {}
            )
            
            self.executions[execution_id] = execution
            
            self.logger.info(f"Executing workflow: {workflow_data['name']}")
            
            # Simulate workflow execution
            # In a real implementation, this would trigger the actual n8n workflow
            result = self._simulate_workflow_execution(workflow_data, input_data)
            
            # Update execution record
            execution.status = WorkflowStatus.COMPLETED if result['success'] else WorkflowStatus.FAILED
            execution.end_time = datetime.now()
            execution.output_data = result.get('output_data', {})
            execution.error_message = result.get('error')
            
            return {
                'success': result['success'],
                'execution_id': execution_id,
                'workflow_name': workflow_data['name'],
                'output_data': result.get('output_data', {}),
                'error': result.get('error'),
                'execution_time': (execution.end_time - execution.start_time).total_seconds()
            }
        
        except Exception as e:
            self.logger.error(f"Error executing workflow: {e}")
            return {'success': False, 'error': str(e)}
    
    def _simulate_workflow_execution(self, workflow_data: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate workflow execution (placeholder for real n8n integration)."""
        try:
            # Simulate processing time
            time.sleep(0.1)
            
            # Generate mock output based on workflow type
            categories = self._categorize_workflow(workflow_data)
            
            output_data = {
                'workflow_id': workflow_data['id'],
                'execution_timestamp': datetime.now().isoformat(),
                'categories': categories,
                'nodes_processed': len(workflow_data['nodes']),
                'input_received': input_data
            }
            
            # Add category-specific mock data
            if 'email_automation' in categories:
                output_data['emails_sent'] = 1
                output_data['recipients'] = ['user@example.com']
            
            elif 'data_processing' in categories:
                output_data['records_processed'] = 100
                output_data['processing_time'] = 0.5
            
            elif 'api_integration' in categories:
                output_data['api_calls_made'] = 3
                output_data['response_status'] = 'success'
            
            return {
                'success': True,
                'output_data': output_data
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_ai_enhanced_workflow(self, base_workflow_id: str, ai_enhancements: Dict[str, Any]) -> Dict[str, Any]:
        """Create AI-enhanced version of a workflow."""
        try:
            if base_workflow_id not in self.workflows:
                return {'success': False, 'error': f'Base workflow {base_workflow_id} not found'}
            
            base_workflow = self.workflows[base_workflow_id]
            
            # Create enhanced workflow
            enhanced_workflow = {
                'id': f"{base_workflow_id}_ai_enhanced",
                'name': f"{base_workflow['name']} (AI Enhanced)",
                'base_workflow_id': base_workflow_id,
                'ai_enhancements': ai_enhancements,
                'nodes': base_workflow['nodes'].copy(),
                'connections': base_workflow['connections'].copy()
            }
            
            # Add AI nodes
            ai_nodes = self._create_ai_nodes(ai_enhancements)
            enhanced_workflow['nodes'].extend(ai_nodes)
            
            # Store enhanced workflow
            self.workflows[enhanced_workflow['id']] = enhanced_workflow
            
            self.logger.info(f"Created AI-enhanced workflow: {enhanced_workflow['name']}")
            return {
                'success': True,
                'enhanced_workflow_id': enhanced_workflow['id'],
                'ai_nodes_added': len(ai_nodes)
            }
        
        except Exception as e:
            self.logger.error(f"Error creating AI-enhanced workflow: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_ai_nodes(self, ai_enhancements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create AI-specific nodes for workflow enhancement."""
        try:
            ai_nodes = []
            
            # AI Router Node
            if ai_enhancements.get('add_ai_router', False):
                ai_router = {
                    'id': f"ai_router_{int(datetime.now().timestamp())}",
                    'name': 'AI Router',
                    'type': 'ai_router',
                    'parameters': {
                        'model': ai_enhancements.get('model', 'gpt-3.5-turbo'),
                        'routing_logic': ai_enhancements.get('routing_logic', 'intent_based'),
                        'confidence_threshold': ai_enhancements.get('confidence_threshold', 0.7)
                    },
                    'position': [400, 200]
                }
                ai_nodes.append(ai_router)
            
            # Decision Node
            if ai_enhancements.get('add_ai_decision', False):
                ai_decision = {
                    'id': f"ai_decision_{int(datetime.now().timestamp())}",
                    'name': 'AI Decision Maker',
                    'type': 'ai_decision',
                    'parameters': {
                        'decision_criteria': ai_enhancements.get('decision_criteria', 'content_analysis'),
                        'fallback_action': ai_enhancements.get('fallback_action', 'continue')
                    },
                    'position': [600, 200]
                }
                ai_nodes.append(ai_decision)
            
            # Adaptive Action Node
            if ai_enhancements.get('add_adaptive_action', False):
                adaptive_action = {
                    'id': f"adaptive_action_{int(datetime.now().timestamp())}",
                    'name': 'Adaptive Action',
                    'type': 'adaptive_action',
                    'parameters': {
                        'action_type': ai_enhancements.get('action_type', 'dynamic_response'),
                        'learning_enabled': ai_enhancements.get('learning_enabled', True)
                    },
                    'position': [800, 200]
                }
                ai_nodes.append(adaptive_action)
            
            return ai_nodes
        
        except Exception as e:
            self.logger.error(f"Error creating AI nodes: {e}")
            return []
    
    def get_workflow_analytics(self) -> Dict[str, Any]:
        """Get analytics for all workflows."""
        try:
            analytics = {
                'total_workflows': len(self.workflows),
                'active_workflows': sum(1 for w in self.workflows.values() if w.get('active', False)),
                'total_executions': len(self.executions),
                'successful_executions': sum(1 for e in self.executions.values() if e.status == WorkflowStatus.COMPLETED),
                'failed_executions': sum(1 for e in self.executions.values() if e.status == WorkflowStatus.FAILED),
                'category_distribution': {},
                'average_execution_time': 0,
                'most_used_workflows': []
            }
            
            # Calculate category distribution
            for workflow in self.workflows.values():
                categories = self._categorize_workflow(workflow)
                for category in categories:
                    analytics['category_distribution'][category] = analytics['category_distribution'].get(category, 0) + 1
            
            # Calculate average execution time
            completed_executions = [e for e in self.executions.values() if e.status == WorkflowStatus.COMPLETED and e.end_time]
            if completed_executions:
                total_time = sum((e.end_time - e.start_time).total_seconds() for e in completed_executions)
                analytics['average_execution_time'] = total_time / len(completed_executions)
            
            # Find most used workflows
            workflow_usage = {}
            for execution in self.executions.values():
                workflow_id = execution.workflow_id
                workflow_usage[workflow_id] = workflow_usage.get(workflow_id, 0) + 1
            
            analytics['most_used_workflows'] = sorted(
                workflow_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return analytics
        
        except Exception as e:
            self.logger.error(f"Error getting workflow analytics: {e}")
            return {}
    
    def recommend_workflows(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend workflows based on user context."""
        try:
            recommendations = []
            
            # Analyze user context
            user_goals = user_context.get('goals', [])
            user_activities = user_context.get('activities', [])
            user_preferences = user_context.get('preferences', {})
            
            # Score workflows based on relevance
            for workflow_id, workflow_data in self.workflows.items():
                score = 0
                categories = self._categorize_workflow(workflow_data)
                
                # Score based on goals
                for goal in user_goals:
                    if any(goal.lower() in category.lower() for category in categories):
                        score += 10
                
                # Score based on activities
                for activity in user_activities:
                    if any(activity.lower() in category.lower() for category in categories):
                        score += 5
                
                # Score based on workflow complexity (prefer simpler workflows)
                node_count = len(workflow_data.get('nodes', []))
                if node_count <= 5:
                    score += 3
                elif node_count <= 10:
                    score += 1
                
                if score > 0:
                    recommendations.append({
                        'workflow_id': workflow_id,
                        'name': workflow_data['name'],
                        'score': score,
                        'categories': categories,
                        'description': self._generate_workflow_description(workflow_data)
                    })
            
            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:10]
        
        except Exception as e:
            self.logger.error(f"Error recommending workflows: {e}")
            return []
    
    def export_workflow_report(self, output_file: str = "workflow_report.json") -> bool:
        """Export comprehensive workflow report."""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'workflows': list(self.workflows.values()),
                'executions': [
                    {
                        'execution_id': exec_id,
                        'workflow_id': exec.workflow_id,
                        'status': exec.status.value,
                        'start_time': exec.start_time.isoformat(),
                        'end_time': exec.end_time.isoformat() if exec.end_time else None,
                        'error_message': exec.error_message
                    }
                    for exec_id, exec in self.executions.items()
                ],
                'analytics': self.get_workflow_analytics()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Workflow report exported: {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting workflow report: {e}")
            return False
