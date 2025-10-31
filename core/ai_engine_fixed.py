"""
JARVIS AI - AI Engine
Handles HelaGPT API integration and AI processing.
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from utils.config import Config

class AIEngine:
    """
    AI Engine for processing user inputs and generating responses.
    Integrates with HelaGPT API for natural language processing.
    """
    
    def __init__(self):
        """Initialize the AI Engine."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        self.api_key = self.config.get('HELAGPT_API_KEY')
        self.base_url = self.config.get('HELAGPT_BASE_URL')
        self.conversation_history = []
        
        if not self.api_key:
            self.logger.warning("HelaGPT API key not found. AI features will be limited.")
    
    def process(self, command: Dict, context: Dict = None) -> str:
        """
        Process a command and generate an AI response.
        
        Args:
            command: Parsed command dictionary
            context: Additional context information
            
        Returns:
            AI-generated response string
        """
        try:
            # Prepare the message for HelaGPT
            message = self._prepare_message(command, context)
            
            # Get AI response
            response = self._get_ai_response(message)
            
            # Update conversation history
            self._update_history(command.get('original_text', ''), response)
            
            return response
        
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return "I'm sorry, I encountered an error processing your request."
    
    def _prepare_message(self, command: Dict, context: Dict = None) -> str:
        """Prepare message for HelaGPT API."""
        try:
            # Extract the main message
            message = command.get('original_text', '')
            
            # Add context if available
            if context:
                context_str = f"Context: {json.dumps(context)}"
                message = f"{message}\n\n{context_str}"
            
            return message
        
        except Exception as e:
            self.logger.error(f"Error preparing message: {e}")
            return command.get('original_text', '')
    
    def _get_ai_response(self, message: str) -> str:
        """Get response from HelaGPT API."""
        try:
            if not self.api_key or not self.base_url:
                return self._get_fallback_response(message)
            
            # Prepare request data
            data = {
                "messages": [
                    {"role": "user", "content": message}
                ]
            }
            
            # Add conversation history if available
            if self.conversation_history:
                history_messages = []
                for entry in self.conversation_history[-5:]:  # Last 5 exchanges
                    if 'user' in entry:
                        history_messages.append({"role": "user", "content": entry['user']})
                    if 'assistant' in entry:
                        history_messages.append({"role": "assistant", "content": entry['assistant']})
                
                data["messages"] = history_messages + data["messages"]
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, dict):
                    if 'response' in result:
                        return result['response']
                    elif 'text' in result:
                        # Handle HelaGPT format
                        if result.get('type') == 'empty':
                            return "I understand your request, but I need more information to provide a helpful response."
                        return result['text']
                    else:
                        return str(result)
                else:
                    return str(result)
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return self._get_fallback_response(message)
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {e}")
            return self._get_fallback_response(message)
        except Exception as e:
            self.logger.error(f"Error getting AI response: {e}")
            return self._get_fallback_response(message)
    
    def _get_fallback_response(self, message: str) -> str:
        """Get fallback response when API is unavailable."""
        message_lower = message.lower()
        
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hello! I'm Jarvis, your AI assistant. How can I help you today?"
        elif any(question in message_lower for question in ['what', 'how', 'why', 'when', 'where']):
            return "That's an interesting question. I'd be happy to help you find the answer!"
        elif 'goodbye' in message_lower or 'bye' in message_lower:
            return "Goodbye! Have a great day!"
        else:
            return "I understand you said: " + message + ". I'm still learning, so please be patient with me!"
    
    def _update_history(self, user_input: str, ai_response: str):
        """Update conversation history."""
        self.conversation_history.append({
            'user': user_input,
            'assistant': ai_response,
            'timestamp': self._get_timestamp()
        })
        
        # Keep only last 10 exchanges
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
