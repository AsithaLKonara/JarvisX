"""
JARVIS AI - RPA Controller
Robotic Process Automation layer for GUI automation and workflow execution.
"""

import time
import logging
import pyautogui
import keyboard
import pynput
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path

class ActionType(Enum):
    """Types of RPA actions."""
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    DRAG = "drag"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    FIND_IMAGE = "find_image"
    KEY_COMBINATION = "key_combination"
    MOUSE_MOVE = "mouse_move"

@dataclass
class RPAAction:
    """Individual RPA action."""
    action_type: ActionType
    parameters: Dict[str, Any]
    delay: float = 0.5
    retry_count: int = 3
    timeout: float = 10.0
    description: str = ""

@dataclass
class WorkflowStep:
    """Workflow step with actions and conditions."""
    step_id: str
    name: str
    actions: List[RPAAction]
    conditions: List[Dict[str, Any]] = None
    on_success: str = None
    on_failure: str = None
    timeout: float = 30.0

@dataclass
class WorkflowBlueprint:
    """Complete workflow blueprint."""
    blueprint_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    variables: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class RPAController:
    """
    Advanced RPA controller for GUI automation.
    Handles mouse, keyboard, and screen interactions with AI decision making.
    """
    
    def __init__(self, safety_mode: bool = True):
        """Initialize RPA controller."""
        self.logger = logging.getLogger(__name__)
        self.safety_mode = safety_mode
        
        # Configure pyautogui
        pyautogui.FAILSAFE = safety_mode
        pyautogui.PAUSE = 0.1
        
        # State tracking
        self.current_workflow = None
        self.workflow_history = []
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # AI decision making
        self.ai_decision_enabled = True
        self.confidence_threshold = 0.7
        
        self.logger.info("RPA Controller initialized")
    
    def execute_action(self, action: RPAAction) -> Dict[str, Any]:
        """Execute a single RPA action."""
        try:
            self.logger.info(f"Executing action: {action.action_type.value}")
            
            result = {
                'success': False,
                'action_type': action.action_type.value,
                'timestamp': datetime.now().isoformat(),
                'error': None
            }
            
            # Execute based on action type
            if action.action_type == ActionType.CLICK:
                result = self._execute_click(action)
            elif action.action_type == ActionType.TYPE:
                result = self._execute_type(action)
            elif action.action_type == ActionType.SCROLL:
                result = self._execute_scroll(action)
            elif action.action_type == ActionType.DRAG:
                result = self._execute_drag(action)
            elif action.action_type == ActionType.WAIT:
                result = self._execute_wait(action)
            elif action.action_type == ActionType.SCREENSHOT:
                result = self._execute_screenshot(action)
            elif action.action_type == ActionType.FIND_IMAGE:
                result = self._execute_find_image(action)
            elif action.action_type == ActionType.KEY_COMBINATION:
                result = self._execute_key_combination(action)
            elif action.action_type == ActionType.MOUSE_MOVE:
                result = self._execute_mouse_move(action)
            else:
                result['error'] = f"Unknown action type: {action.action_type}"
            
            # Add delay after action
            if action.delay > 0:
                time.sleep(action.delay)
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error executing action: {e}")
            return {
                'success': False,
                'action_type': action.action_type.value,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def execute_workflow(self, blueprint: WorkflowBlueprint) -> Dict[str, Any]:
        """Execute a complete workflow blueprint."""
        try:
            self.logger.info(f"Executing workflow: {blueprint.name}")
            
            self.current_workflow = blueprint
            workflow_result = {
                'workflow_id': blueprint.blueprint_id,
                'name': blueprint.name,
                'start_time': datetime.now().isoformat(),
                'steps_completed': 0,
                'steps_failed': 0,
                'total_steps': len(blueprint.steps),
                'success': False,
                'error': None
            }
            
            # Execute each step
            for step in blueprint.steps:
                try:
                    self.logger.info(f"Executing step: {step.name}")
                    
                    # Check conditions if any
                    if step.conditions and not self._check_conditions(step.conditions):
                        self.logger.warning(f"Conditions not met for step: {step.name}")
                        continue
                    
                    # Execute step actions
                    step_result = self._execute_step(step)
                    
                    if step_result['success']:
                        workflow_result['steps_completed'] += 1
                        self.logger.info(f"Step completed: {step.name}")
                    else:
                        workflow_result['steps_failed'] += 1
                        self.logger.error(f"Step failed: {step.name} - {step_result.get('error', 'Unknown error')}")
                        
                        # Handle failure
                        if step.on_failure:
                            self._handle_step_failure(step, step_result)
                        else:
                            break
                
                except Exception as e:
                    self.logger.error(f"Error executing step {step.name}: {e}")
                    workflow_result['steps_failed'] += 1
                    break
            
            # Determine overall success
            workflow_result['success'] = workflow_result['steps_failed'] == 0
            workflow_result['end_time'] = datetime.now().isoformat()
            
            # Store in history
            self.workflow_history.append(workflow_result)
            
            self.logger.info(f"Workflow completed: {workflow_result['success']}")
            return workflow_result
        
        except Exception as e:
            self.logger.error(f"Error executing workflow: {e}")
            return {
                'success': False,
                'error': str(e),
                'workflow_id': blueprint.blueprint_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def create_workflow_blueprint(self, name: str, description: str, steps: List[WorkflowStep]) -> WorkflowBlueprint:
        """Create a new workflow blueprint."""
        blueprint_id = f"workflow_{int(datetime.now().timestamp())}"
        
        blueprint = WorkflowBlueprint(
            blueprint_id=blueprint_id,
            name=name,
            description=description,
            steps=steps
        )
        
        self.logger.info(f"Created workflow blueprint: {name}")
        return blueprint
    
    def save_workflow_blueprint(self, blueprint: WorkflowBlueprint, file_path: str) -> bool:
        """Save workflow blueprint to file."""
        try:
            # Convert to serializable format
            blueprint_data = {
                'blueprint_id': blueprint.blueprint_id,
                'name': blueprint.name,
                'description': blueprint.description,
                'steps': [
                    {
                        'step_id': step.step_id,
                        'name': step.name,
                        'actions': [
                            {
                                'action_type': action.action_type.value,
                                'parameters': action.parameters,
                                'delay': action.delay,
                                'retry_count': action.retry_count,
                                'timeout': action.timeout,
                                'description': action.description
                            }
                            for action in step.actions
                        ],
                        'conditions': step.conditions or [],
                        'on_success': step.on_success,
                        'on_failure': step.on_failure,
                        'timeout': step.timeout
                    }
                    for step in blueprint.steps
                ],
                'variables': blueprint.variables or {},
                'created_at': blueprint.created_at.isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(blueprint_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Workflow blueprint saved: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving workflow blueprint: {e}")
            return False
    
    def load_workflow_blueprint(self, file_path: str) -> Optional[WorkflowBlueprint]:
        """Load workflow blueprint from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct blueprint
            steps = []
            for step_data in data['steps']:
                actions = []
                for action_data in step_data['actions']:
                    action = RPAAction(
                        action_type=ActionType(action_data['action_type']),
                        parameters=action_data['parameters'],
                        delay=action_data.get('delay', 0.5),
                        retry_count=action_data.get('retry_count', 3),
                        timeout=action_data.get('timeout', 10.0),
                        description=action_data.get('description', '')
                    )
                    actions.append(action)
                
                step = WorkflowStep(
                    step_id=step_data['step_id'],
                    name=step_data['name'],
                    actions=actions,
                    conditions=step_data.get('conditions'),
                    on_success=step_data.get('on_success'),
                    on_failure=step_data.get('on_failure'),
                    timeout=step_data.get('timeout', 30.0)
                )
                steps.append(step)
            
            blueprint = WorkflowBlueprint(
                blueprint_id=data['blueprint_id'],
                name=data['name'],
                description=data['description'],
                steps=steps,
                variables=data.get('variables', {}),
                created_at=datetime.fromisoformat(data['created_at'])
            )
            
            self.logger.info(f"Workflow blueprint loaded: {file_path}")
            return blueprint
        
        except Exception as e:
            self.logger.error(f"Error loading workflow blueprint: {e}")
            return None
    
    def _execute_click(self, action: RPAAction) -> Dict[str, Any]:
        """Execute click action."""
        try:
            x = action.parameters.get('x')
            y = action.parameters.get('y')
            button = action.parameters.get('button', 'left')
            clicks = action.parameters.get('clicks', 1)
            
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, button=button)
            else:
                # Click at current mouse position
                pyautogui.click(clicks=clicks, button=button)
            
            return {'success': True, 'coordinates': (x, y), 'button': button}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_type(self, action: RPAAction) -> Dict[str, Any]:
        """Execute type action."""
        try:
            text = action.parameters.get('text', '')
            interval = action.parameters.get('interval', 0.0)
            
            pyautogui.typewrite(text, interval=interval)
            
            return {'success': True, 'text': text}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_scroll(self, action: RPAAction) -> Dict[str, Any]:
        """Execute scroll action."""
        try:
            clicks = action.parameters.get('clicks', 3)
            x = action.parameters.get('x')
            y = action.parameters.get('y')
            
            if x is not None and y is not None:
                pyautogui.scroll(clicks, x=x, y=y)
            else:
                pyautogui.scroll(clicks)
            
            return {'success': True, 'clicks': clicks}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_drag(self, action: RPAAction) -> Dict[str, Any]:
        """Execute drag action."""
        try:
            start_x = action.parameters.get('start_x')
            start_y = action.parameters.get('start_y')
            end_x = action.parameters.get('end_x')
            end_y = action.parameters.get('end_y')
            duration = action.parameters.get('duration', 1.0)
            button = action.parameters.get('button', 'left')
            
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration, button=button)
            
            return {'success': True, 'start': (start_x, start_y), 'end': (end_x, end_y)}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_wait(self, action: RPAAction) -> Dict[str, Any]:
        """Execute wait action."""
        try:
            duration = action.parameters.get('duration', 1.0)
            time.sleep(duration)
            
            return {'success': True, 'duration': duration}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_screenshot(self, action: RPAAction) -> Dict[str, Any]:
        """Execute screenshot action."""
        try:
            filename = action.parameters.get('filename', f"screenshot_{int(time.time())}.png")
            region = action.parameters.get('region')  # (x, y, width, height)
            
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            file_path = self.screenshots_dir / filename
            screenshot.save(file_path)
            
            return {'success': True, 'file_path': str(file_path)}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_find_image(self, action: RPAAction) -> Dict[str, Any]:
        """Execute find image action."""
        try:
            image_path = action.parameters.get('image_path')
            confidence = action.parameters.get('confidence', 0.8)
            region = action.parameters.get('region')
            
            if region:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
            else:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            
            if location:
                center = pyautogui.center(location)
                return {'success': True, 'location': center, 'confidence': confidence}
            else:
                return {'success': False, 'error': 'Image not found'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_key_combination(self, action: RPAAction) -> Dict[str, Any]:
        """Execute key combination action."""
        try:
            keys = action.parameters.get('keys', [])
            interval = action.parameters.get('interval', 0.0)
            
            pyautogui.hotkey(*keys)
            
            return {'success': True, 'keys': keys}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_mouse_move(self, action: RPAAction) -> Dict[str, Any]:
        """Execute mouse move action."""
        try:
            x = action.parameters.get('x')
            y = action.parameters.get('y')
            duration = action.parameters.get('duration', 0.0)
            
            pyautogui.moveTo(x, y, duration=duration)
            
            return {'success': True, 'coordinates': (x, y)}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a workflow step."""
        try:
            step_result = {
                'step_id': step.step_id,
                'name': step.name,
                'success': True,
                'actions_executed': 0,
                'actions_failed': 0,
                'error': None
            }
            
            for action in step.actions:
                action_result = self.execute_action(action)
                
                if action_result['success']:
                    step_result['actions_executed'] += 1
                else:
                    step_result['actions_failed'] += 1
                    step_result['success'] = False
                    step_result['error'] = action_result.get('error', 'Action failed')
                    break
            
            return step_result
        
        except Exception as e:
            return {
                'step_id': step.step_id,
                'name': step.name,
                'success': False,
                'error': str(e)
            }
    
    def _check_conditions(self, conditions: List[Dict[str, Any]]) -> bool:
        """Check if conditions are met."""
        try:
            for condition in conditions:
                condition_type = condition.get('type')
                
                if condition_type == 'image_exists':
                    image_path = condition.get('image_path')
                    confidence = condition.get('confidence', 0.8)
                    location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                    if not location:
                        return False
                
                elif condition_type == 'text_exists':
                    # This would require OCR - placeholder for now
                    pass
                
                elif condition_type == 'time_condition':
                    current_hour = datetime.now().hour
                    start_hour = condition.get('start_hour', 0)
                    end_hour = condition.get('end_hour', 23)
                    if not (start_hour <= current_hour <= end_hour):
                        return False
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error checking conditions: {e}")
            return False
    
    def _handle_step_failure(self, step: WorkflowStep, step_result: Dict[str, Any]):
        """Handle step failure."""
        try:
            if step.on_failure == 'retry':
                # Retry the step
                self.logger.info(f"Retrying step: {step.name}")
                # Implementation would retry the step
            elif step.on_failure == 'skip':
                # Skip to next step
                self.logger.info(f"Skipping step: {step.name}")
            elif step.on_failure == 'abort':
                # Abort workflow
                self.logger.error(f"Aborting workflow due to step failure: {step.name}")
        
        except Exception as e:
            self.logger.error(f"Error handling step failure: {e}")
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get workflow execution history."""
        return self.workflow_history.copy()
    
    def create_common_workflows(self) -> Dict[str, WorkflowBlueprint]:
        """Create common workflow blueprints."""
        workflows = {}
        
        # Email automation workflow
        email_workflow = self.create_workflow_blueprint(
            name="Send Email",
            description="Automate email sending",
            steps=[
                WorkflowStep(
                    step_id="open_email_client",
                    name="Open Email Client",
                    actions=[
                        RPAAction(
                            action_type=ActionType.KEY_COMBINATION,
                            parameters={'keys': ['cmd', 'space']},
                            description="Open Spotlight"
                        ),
                        RPAAction(
                            action_type=ActionType.TYPE,
                            parameters={'text': 'Mail'},
                            description="Type Mail"
                        ),
                        RPAAction(
                            action_type=ActionType.KEY_COMBINATION,
                            parameters={'keys': ['enter']},
                            description="Press Enter"
                        )
                    ]
                ),
                WorkflowStep(
                    step_id="compose_email",
                    name="Compose Email",
                    actions=[
                        RPAAction(
                            action_type=ActionType.KEY_COMBINATION,
                            parameters={'keys': ['cmd', 'n']},
                            description="New email"
                        )
                    ]
                )
            ]
        )
        workflows['send_email'] = email_workflow
        
        # File organization workflow
        file_org_workflow = self.create_workflow_blueprint(
            name="Organize Files",
            description="Automate file organization",
            steps=[
                WorkflowStep(
                    step_id="open_finder",
                    name="Open Finder",
                    actions=[
                        RPAAction(
                            action_type=ActionType.KEY_COMBINATION,
                            parameters={'keys': ['cmd', 'space']},
                            description="Open Spotlight"
                        ),
                        RPAAction(
                            action_type=ActionType.TYPE,
                            parameters={'text': 'Finder'},
                            description="Type Finder"
                        ),
                        RPAAction(
                            action_type=ActionType.KEY_COMBINATION,
                            parameters={'keys': ['enter']},
                            description="Press Enter"
                        )
                    ]
                )
            ]
        )
        workflows['organize_files'] = file_org_workflow
        
        return workflows
