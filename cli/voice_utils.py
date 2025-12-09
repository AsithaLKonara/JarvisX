"""
Voice Command Utilities
Voice command parsing and mapping to CLI commands
"""

import re
from typing import Optional, Dict, List


class VoiceCommandParser:
    """Parse natural language voice commands into CLI commands"""
    
    def __init__(self):
        """Initialize voice command parser"""
        self.command_mappings = self._build_command_mappings()
    
    def _build_command_mappings(self) -> Dict[str, Dict]:
        """Build command mappings from natural language to CLI"""
        return {
            # Training commands (10)
            'start training': {'command': 'training start', 'args': []},
            'train model': {'command': 'training start', 'args': []},
            'begin training': {'command': 'training start', 'args': []},
            'training status': {'command': 'training status', 'args': ['--job-id']},
            'check training': {'command': 'training status', 'args': ['--job-id']},
            'training logs': {'command': 'training logs', 'args': ['--job-id']},
            'show training logs': {'command': 'training logs', 'args': ['--job-id']},
            'cancel training': {'command': 'training cancel', 'args': ['--job-id']},
            'stop training': {'command': 'training cancel', 'args': ['--job-id']},
            'list training': {'command': 'training list', 'args': []},
            'training jobs': {'command': 'training list', 'args': []},
            'evaluate model': {'command': 'training evaluate', 'args': ['--model']},
            
            # Cloud commands (8)
            'cloud status': {'command': 'cloud status', 'args': ['--space']},
            'check cloud': {'command': 'cloud status', 'args': ['--space']},
            'deploy cloud': {'command': 'cloud deploy', 'args': ['--space']},
            'deploy model': {'command': 'cloud deploy', 'args': ['--space']},
            'test cloud': {'command': 'cloud test', 'args': []},
            'monitor cloud': {'command': 'cloud monitor', 'args': ['--space']},
            'cloud logs': {'command': 'cloud logs', 'args': ['--space']},
            'connect cloud': {'command': 'cloud connect', 'args': ['--url']},
            
            # System commands (12)
            'system status': {'command': 'system status', 'args': []},
            'show status': {'command': 'system status', 'args': []},
            'check status': {'command': 'system status', 'args': []},
            'system health': {'command': 'system health', 'args': []},
            'health check': {'command': 'system health', 'args': []},
            'system info': {'command': 'system info', 'args': []},
            'system information': {'command': 'system info', 'args': []},
            'optimize system': {'command': 'system optimize', 'args': ['--auto']},
            'cleanup system': {'command': 'system cleanup', 'args': ['--logs', '--cache']},
            'system cleanup': {'command': 'system cleanup', 'args': ['--logs', '--cache']},
            'system logs': {'command': 'system logs', 'args': []},
            'show logs': {'command': 'system logs', 'args': []},
            
            # Business commands (10)
            'generate invoice': {'command': 'business invoice', 'args': ['--client-id']},
            'create invoice': {'command': 'business invoice', 'args': ['--client-id']},
            'list clients': {'command': 'business client list', 'args': []},
            'show clients': {'command': 'business client list', 'args': []},
            'add client': {'command': 'business client add', 'args': ['--name', '--email']},
            'new client': {'command': 'business client add', 'args': ['--name', '--email']},
            'generate report': {'command': 'business report', 'args': ['--type']},
            'create report': {'command': 'business report', 'args': ['--type']},
            'schedule task': {'command': 'business task schedule', 'args': ['--name', '--cron']},
            'list tasks': {'command': 'business task list', 'args': []},
            'export data': {'command': 'business export', 'args': ['--type', '--output']},
            
            # Model commands (10)
            'list models': {'command': 'model list', 'args': []},
            'show models': {'command': 'model list', 'args': []},
            'load model': {'command': 'model load', 'args': ['--name']},
            'model info': {'command': 'model info', 'args': ['--name']},
            'model information': {'command': 'model info', 'args': ['--name']},
            'test model': {'command': 'model test', 'args': ['--name', '--prompt']},
            'compare models': {'command': 'model compare', 'args': ['--model-a', '--model-b']},
            'upload model': {'command': 'model upload', 'args': ['--path', '--repo']},
            'deploy model': {'command': 'model upload', 'args': ['--path', '--repo']},
            'model details': {'command': 'model info', 'args': ['--name']},
            
            # Workflow commands (8)
            'list workflows': {'command': 'workflow list', 'args': []},
            'show workflows': {'command': 'workflow list', 'args': []},
            'execute workflow': {'command': 'workflow execute', 'args': ['--id']},
            'run workflow': {'command': 'workflow execute', 'args': ['--id']},
            'create workflow': {'command': 'workflow create', 'args': ['--name']},
            'workflow status': {'command': 'workflow status', 'args': ['--execution-id']},
            'workflow analytics': {'command': 'workflow analytics', 'args': []},
            'workflow recommendations': {'command': 'workflow recommend', 'args': []},
            
            # Config commands (6)
            'show config': {'command': 'config show', 'args': []},
            'get config': {'command': 'config get', 'args': []},
            'set config': {'command': 'config set', 'args': []},
            'validate config': {'command': 'config validate', 'args': []},
            'configuration': {'command': 'config show', 'args': []},
            'check config': {'command': 'config validate', 'args': []},
            
            # Voice commands (4)
            'listen': {'command': 'voice listen', 'args': []},
            'speak': {'command': 'voice speak', 'args': []},
            'voice mode': {'command': 'voice interactive', 'args': []},
            'interactive mode': {'command': 'voice interactive', 'args': []},
            
            # General commands (5)
            'status': {'command': 'status', 'args': []},
            'version': {'command': 'version', 'args': []},
            'help': {'command': '--help', 'args': []},
            'what can you do': {'command': '--help', 'args': []},
            'show help': {'command': '--help', 'args': []},
        }
    
    def parse_voice_command(self, text: str) -> Optional[str]:
        """
        Parse voice command text into CLI command
        
        Args:
            text: Natural language command text
            
        Returns:
            CLI command string or None if not recognized
        """
        text_lower = text.lower().strip()
        
        # Direct match
        if text_lower in self.command_mappings:
            mapping = self.command_mappings[text_lower]
            return mapping['command']
        
        # Pattern matching
        for pattern, mapping in self.command_mappings.items():
            if self._matches_pattern(text_lower, pattern):
                command = mapping['command']
                # Extract arguments if possible
                args = self._extract_arguments(text_lower, mapping)
                if args:
                    return f"{command} {args}"
                return command
        
        # Try to extract command keywords
        keywords = self._extract_keywords(text_lower)
        if keywords:
            for pattern, mapping in self.command_mappings.items():
                if all(kw in pattern for kw in keywords):
                    return mapping['command']
        
        return None
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches a pattern"""
        # Simple keyword matching
        pattern_words = set(pattern.split())
        text_words = set(text.split())
        return pattern_words.issubset(text_words) or len(pattern_words.intersection(text_words)) >= len(pattern_words) * 0.7
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract command keywords from text"""
        # Common command keywords
        keywords = []
        words = text.split()
        
        command_words = ['start', 'stop', 'list', 'show', 'get', 'create', 'add', 'delete', 'update', 
                        'status', 'info', 'test', 'train', 'deploy', 'monitor', 'optimize', 'cleanup']
        
        for word in words:
            if word in command_words:
                keywords.append(word)
        
        return keywords
    
    def _extract_arguments(self, text: str, mapping: Dict) -> str:
        """Extract arguments from voice command"""
        # Simple argument extraction
        # This is a basic implementation that can be extended
        args = []
        
        # Extract numbers (for IDs, etc.)
        numbers = re.findall(r'\d+', text)
        if numbers and mapping.get('args'):
            for i, arg in enumerate(mapping['args']):
                if i < len(numbers):
                    args.append(f"{arg} {numbers[i]}")
        
        # Extract quoted strings
        quoted = re.findall(r'"([^"]*)"', text)
        if quoted and mapping.get('args'):
            for i, arg in enumerate(mapping['args']):
                if i < len(quoted):
                    args.append(f"{arg} {quoted[i]}")
        
        return ' '.join(args) if args else ''

