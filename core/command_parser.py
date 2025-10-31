"""
Command Parser - Interprets user input and extracts commands and parameters
"""

from typing import Dict, Any, Optional
import re


class CommandParser:
    """
    Parses user input to extract commands, intents, and parameters.
    """
    
    def __init__(self):
        """Initialize the command parser."""
        self.command_patterns = {
            'greeting': r'(hello|hi|hey|good morning|good afternoon|good evening)',
            'goodbye': r'(goodbye|bye|see you|farewell)',
            'help': r'(help|assist|support)',
            'time': r'(what time|what\'s the time|current time)',
            'weather': r'(weather|temperature|forecast)',
            'calculation': r'(calculate|compute|math)',
            'search': r'(search|find|look for)',
            'set_reminder': r'(remind|reminder|set reminder)',
            'play_music': r'(play music|music)',
        }
    
    def parse(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input and extract command information.
        
        Args:
            user_input: User's text input
            
        Returns:
            Dictionary with parsed command details
        """
        if not user_input:
            return {
                'original_text': '',
                'command': None,
                'intent': 'unknown',
                'parameters': {},
                'confidence': 0.0
            }
        
        original_text = user_input
        user_input_lower = user_input.lower().strip()
        
        # Find matching command
        matched_command = None
        for command, pattern in self.command_patterns.items():
            if re.search(pattern, user_input_lower):
                matched_command = command
                break
        
        # Extract parameters based on command
        parameters = self._extract_parameters(user_input, matched_command)
        
        return {
            'original_text': original_text,
            'command': matched_command,
            'intent': matched_command or 'unknown',
            'parameters': parameters,
            'confidence': 0.8 if matched_command else 0.3
        }
    
    def _extract_parameters(self, user_input: str, command: Optional[str]) -> Dict[str, str]:
        """
        Extract parameters specific to a command.
        
        Args:
            user_input: User's input
            command: Identified command
            
        Returns:
            Dictionary of parameters
        """
        parameters = {}
        
        if command == 'set_reminder':
            # Extract time from input
            time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)?', user_input.lower())
            if time_match:
                parameters['time'] = time_match.group(0)
            
            # Extract reminder text
            text_match = re.search(r'remind me (?:at \d{1,2}:\d{2}\s*(?:am|pm)?\s+)?(.+)', user_input, re.IGNORECASE)
            if text_match:
                parameters['text'] = text_match.group(1)
        
        elif command == 'calculation':
            # Extract the calculation
            calc_match = re.search(r'(?:calculate|compute)\s+(.+)', user_input, re.IGNORECASE)
            if calc_match:
                parameters['expression'] = calc_match.group(1)
        
        elif command == 'search':
            # Extract search query
            search_match = re.search(r'(?:search|find|look for)\s+(?:for\s+)?(.+)', user_input, re.IGNORECASE)
            if search_match:
                parameters['query'] = search_match.group(1)
        
        return parameters
    
    def get_intent(self, user_input: str) -> str:
        """Get the intent of the user input."""
        parsed = self.parse(user_input)
        return parsed.get('intent', 'unknown')
    
    def get_confidence(self, user_input: str) -> float:
        """Get the confidence score for the parsed command."""
        parsed = self.parse(user_input)
        return parsed.get('confidence', 0.0)
