#!/usr/bin/env python3
"""
Action Extractor - Extracts actionable commands from AI responses
Parses AI text responses to identify actions, parameters, and tool routing
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExtractedAction:
    """Represents an extracted action from AI response"""
    action_type: str  # system, business, file, workflow, rpa, cli
    tool: str  # Specific tool name (e.g., monitor_cpu, generate_invoice)
    parameters: Dict[str, Any]  # Action parameters
    confidence: float  # Confidence score (0.0-1.0)
    original_text: str  # Original text that triggered this action


class ActionExtractor:
    """
    Extracts actionable commands from AI responses.
    Supports multiple formats: JSON, XML-like tags, natural language parsing
    """
    
    def __init__(self):
        """Initialize action extractor"""
        self.action_patterns = self._build_action_patterns()
        self.tool_keywords = self._build_tool_keywords()
        logger.info("Action Extractor initialized")
    
    def _build_action_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for action detection"""
        return {
            "system": [
                r"monitor\s+(?:cpu|memory|disk|system)",
                r"check\s+(?:cpu|memory|disk|system|process)",
                r"show\s+(?:cpu|memory|disk|system|process)",
                r"list\s+process",
                r"kill\s+process",
                r"optimize\s+system",
                r"screenshot",
                r"take\s+screenshot"
            ],
            "business": [
                r"generate\s+invoice",
                r"create\s+invoice",
                r"add\s+client",
                r"create\s+client",
                r"generate\s+report",
                r"create\s+report",
                r"schedule\s+task",
                r"create\s+task",
                r"export\s+(?:data|invoice|client)"
            ],
            "file": [
                r"read\s+file",
                r"open\s+file",
                r"write\s+file",
                r"create\s+file",
                r"delete\s+file",
                r"list\s+(?:directory|folder|files)",
                r"search\s+file",
                r"copy\s+file",
                r"move\s+file"
            ],
            "workflow": [
                r"execute\s+workflow",
                r"run\s+workflow",
                r"start\s+workflow",
                r"create\s+workflow"
            ],
            "rpa": [
                r"click\s+(?:on|at)",
                r"type\s+(?:text|into)",
                r"scroll\s+(?:up|down|to)",
                r"press\s+key",
                r"move\s+mouse"
            ],
            "cli": [
                r"run\s+command",
                r"execute\s+command",
                r"run\s+cli",
                r"jarvisx-cli"
            ]
        }
    
    def _build_tool_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """Build keyword mappings for specific tools"""
        return {
            "system": {
                "monitor_cpu": ["cpu", "processor", "usage"],
                "monitor_memory": ["memory", "ram", "usage"],
                "monitor_disk": ["disk", "storage", "space"],
                "list_processes": ["process", "running", "applications"],
                "kill_process": ["kill", "stop", "terminate", "process"],
                "optimize_system": ["optimize", "clean", "system"],
                "screenshot": ["screenshot", "capture", "screen"]
            },
            "business": {
                "generate_invoice": ["invoice", "bill"],
                "add_client": ["client", "customer", "add"],
                "generate_report": ["report", "summary", "financial"],
                "schedule_task": ["task", "schedule", "reminder"],
                "export_data": ["export", "download", "save"]
            },
            "file": {
                "read_file": ["read", "open", "view", "file"],
                "write_file": ["write", "create", "save", "file"],
                "list_directory": ["list", "show", "directory", "folder"],
                "delete_file": ["delete", "remove", "file"],
                "search_files": ["search", "find", "file"]
            },
            "workflow": {
                "execute_workflow": ["execute", "run", "workflow"],
                "create_workflow": ["create", "new", "workflow"]
            },
            "rpa": {
                "click": ["click", "press", "button"],
                "type": ["type", "enter", "text"],
                "scroll": ["scroll", "move"]
            },
            "cli": {
                "execute_command": ["command", "cli", "run"]
            }
        }
    
    def extract_actions(self, ai_response: str, user_input: str = "") -> List[ExtractedAction]:
        """
        Extract actions from AI response
        
        Args:
            ai_response: AI-generated response text
            user_input: Original user input (for context)
            
        Returns:
            List of extracted actions
        """
        actions = []
        
        # Try JSON format first
        json_actions = self._extract_json_actions(ai_response)
        if json_actions:
            actions.extend(json_actions)
        
        # Try XML-like tag format
        tag_actions = self._extract_tag_actions(ai_response)
        if tag_actions:
            actions.extend(tag_actions)
        
        # Fallback to natural language parsing
        if not actions:
            nl_actions = self._extract_natural_language_actions(ai_response, user_input)
            actions.extend(nl_actions)
        
        # Validate and score actions
        validated_actions = []
        for action in actions:
            validated = self._validate_action(action)
            if validated:
                validated_actions.append(validated)
        
        logger.info(f"Extracted {len(validated_actions)} actions from AI response")
        return validated_actions
    
    def _extract_json_actions(self, text: str) -> List[ExtractedAction]:
        """Extract actions from JSON format"""
        actions = []
        
        # Look for JSON objects in the text
        json_pattern = r'\{[^{}]*"actions?"[^{}]*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                data = json.loads(match)
                if isinstance(data, dict) and "actions" in data:
                    for action_data in data["actions"]:
                        if isinstance(action_data, dict):
                            action = self._parse_action_dict(action_data)
                            if action:
                                actions.append(action)
            except json.JSONDecodeError:
                continue
        
        return actions
    
    def _extract_tag_actions(self, text: str) -> List[ExtractedAction]:
        """Extract actions from XML-like tag format"""
        actions = []
        
        # Pattern: <action type="..." tool="..." params="..."/>
        tag_pattern = r'<action\s+type=["\']([^"\']+)["\']\s+tool=["\']([^"\']+)["\'](?:\s+params=["\']([^"\']*)["\'])?\s*/>'
        matches = re.findall(tag_pattern, text, re.IGNORECASE)
        
        for match in matches:
            action_type, tool, params_str = match
            params = {}
            
            # Parse params string (format: key1=value1,key2=value2)
            if params_str:
                for param in params_str.split(','):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key.strip()] = value.strip()
            
            action = ExtractedAction(
                action_type=action_type.lower(),
                tool=tool.lower(),
                parameters=params,
                confidence=0.8,
                original_text=text
            )
            actions.append(action)
        
        return actions
    
    def _extract_natural_language_actions(self, text: str, user_input: str = "") -> List[ExtractedAction]:
        """Extract actions from natural language"""
        actions = []
        text_lower = text.lower()
        user_lower = user_input.lower() if user_input else ""
        combined = f"{user_lower} {text_lower}"
        
        # Check each action type
        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    # Find specific tool
                    tool = self._identify_tool(action_type, combined)
                    if tool:
                        params = self._extract_parameters(action_type, tool, combined)
                        action = ExtractedAction(
                            action_type=action_type,
                            tool=tool,
                            parameters=params,
                            confidence=0.6,  # Lower confidence for NL parsing
                            original_text=text
                        )
                        actions.append(action)
                        break  # One action per type for now
        
        return actions
    
    def _identify_tool(self, action_type: str, text: str) -> Optional[str]:
        """Identify specific tool from text"""
        if action_type not in self.tool_keywords:
            return None
        
        text_lower = text.lower()
        best_match = None
        best_score = 0
        
        for tool, keywords in self.tool_keywords[action_type].items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > best_score:
                best_score = score
                best_match = tool
        
        return best_match if best_score > 0 else None
    
    def _extract_parameters(self, action_type: str, tool: str, text: str) -> Dict[str, Any]:
        """Extract parameters from text"""
        params = {}
        text_lower = text.lower()
        
        # Extract file paths
        file_pattern = r'(?:file|path|location)[\s:]+["\']?([^\s"\']+(?:\.[a-zA-Z0-9]+)?)["\']?'
        file_matches = re.findall(file_pattern, text_lower)
        if file_matches:
            params['path'] = file_matches[0]
        
        # Extract process names/IDs
        process_pattern = r'process(?:es)?[\s:]+["\']?([^\s"\']+)["\']?'
        process_matches = re.findall(process_pattern, text_lower)
        if process_matches:
            params['process'] = process_matches[0]
        
        # Extract client names
        client_pattern = r'client[\s:]+["\']?([^\s"\']+)["\']?'
        client_matches = re.findall(client_pattern, text_lower)
        if client_matches:
            params['client_name'] = client_matches[0]
        
        # Extract amounts
        amount_pattern = r'\$?(\d+(?:\.\d+)?)'
        amount_matches = re.findall(amount_pattern, text)
        if amount_matches:
            try:
                params['amount'] = float(amount_matches[0])
            except ValueError:
                pass
        
        # Extract commands
        command_pattern = r'command[\s:]+["\']([^"\']+)["\']'
        command_matches = re.findall(command_pattern, text_lower)
        if command_matches:
            params['command'] = command_matches[0]
        
        return params
    
    def _parse_action_dict(self, action_dict: Dict) -> Optional[ExtractedAction]:
        """Parse action from dictionary"""
        try:
            return ExtractedAction(
                action_type=action_dict.get("type", "unknown").lower(),
                tool=action_dict.get("tool", "").lower(),
                parameters=action_dict.get("params", {}),
                confidence=action_dict.get("confidence", 0.7),
                original_text=str(action_dict)
            )
        except Exception as e:
            logger.warning(f"Failed to parse action dict: {e}")
            return None
    
    def _validate_action(self, action: ExtractedAction) -> Optional[ExtractedAction]:
        """Validate and enhance action"""
        # Check required fields
        if not action.action_type or not action.tool:
            return None
        
        # Validate action type
        valid_types = ["system", "business", "file", "workflow", "rpa", "cli"]
        if action.action_type not in valid_types:
            logger.warning(f"Invalid action type: {action.action_type}")
            return None
        
        # Enhance parameters with defaults
        if not action.parameters:
            action.parameters = {}
        
        # Adjust confidence based on validation
        if action.confidence < 0.5:
            action.confidence = 0.5
        
        return action

