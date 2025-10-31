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
        """
        Prepare the message for HelaGPT API.
        
        Args:
            command: Parsed command dictionary
            context: Additional context information
            
        Returns:
            Formatted message string
        """
        # Base system message
        system_message = (
            "You are Jarvis, a helpful AI assistant. "
            "You can help with file management, application control, "
            "web searches, and general productivity tasks. "
            "Be concise and helpful in your responses."
        )
        
        # Add context if available
        if context:
            context_info = f"Context: {json.dumps(context, indent=2)}"
            system_message += f"\n\n{context_info}"
        
        # Prepare user message
        user_message = command.get('original_text', '')
        
        # Add command details if available
        if command.get('action'):
            user_message += f"\n\nAction: {command['action']}"
        if command.get('parameters'):
            user_message += f"\nParameters: {command['parameters']}"
        
        return user_message
    
    def _get_ai_response(self, message: str) -> str:
        """
        Get response from HelaGPT API.
        
        Args:
            message: User message to process
            
        Returns:
            AI response string
        """
        if not self.api_key or not self.base_url:
            return self._get_fallback_response(message)
        
        try:
            # Prepare API request headers
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Prepare conversation history
            messages = []
            for conv in self.conversation_history[-5:]:  # Last 5 exchanges
                messages.append({'role': 'user', 'content': conv['user']})
                messages.append({'role': 'assistant', 'content': conv['assistant']})
            
            # Add current message
            messages.append({'role': 'user', 'content': message})
            
            # Prepare request data according to HelaGPT API format
            data = {
                'messages': messages
            }
            
            # Make API request
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('type') == 'text':
                    return result.get('text', 'I apologize, but I could not process your request.')
                elif result.get('type') == 'empty':
                    # Handle empty responses gracefully
                    return self._get_fallback_response(message)
                else:
                    self.logger.error(f"API returned unexpected response type: {result}")
                    return self._get_fallback_response(message)
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return self._get_fallback_response(message)
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {e}")
            return self._get_fallback_response(message)
        except Exception as e:
            self.logger.error(f"Unexpected error in AI response: {e}")
            return self._get_fallback_response(message)
    
    def _get_fallback_response(self, message: str) -> str:
        """
        Get a fallback response when API is unavailable.
        
        Args:
            message: User message
            
        Returns:
            Fallback response string
        """
        # Simple keyword-based responses
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm Jarvis, your AI assistant. How can I help you today?"
        elif any(word in message_lower for word in ['help', 'what can you do']):
            return "I can help you with file management, opening applications, web searches, and general productivity tasks. What would you like me to do?"
        elif any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! Is there anything else I can help you with?"
        elif any(word in message_lower for word in ['bye', 'goodbye', 'exit']):
            return "Goodbye! Have a great day!"
        else:
            return "I understand you said: " + message + ". I'm still learning, so please be patient with me!"
    
    def _update_history(self, user_input: str, ai_response: str):
        """
        Update conversation history.
        
        Args:
            user_input: User input
            ai_response: AI response
        """
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
        """
        Prepare the message for HelaGPT API.
        
        Args:
            command: Parsed command dictionary
            context: Additional context information
            
        Returns:
            Formatted message string
        """
        # Base system message
        system_message = (
            "You are Jarvis, a helpful AI assistant. "
            "You can help with file management, application control, "
            "web searches, and general productivity tasks. "
            "Be concise and helpful in your responses."
        )
        
        # Add context if available
        if context:
            context_info = f"Context: {json.dumps(context, indent=2)}"
            system_message += f"\n\n{context_info}"
        
        # Prepare user message
        user_message = command.get('original_text', '')
        
        # Add command details if available
        if command.get('action'):
            user_message += f"\n\nAction: {command['action']}"
        if command.get('parameters'):
            user_message += f"\nParameters: {command['parameters']}"
        
        return user_message
    
    def _get_ai_response(self, message: str) -> str:
        """
        Get response from HelaGPT API.
        
        Args:
            message: User message to process
            
        Returns:
            AI response string
        """
        if not self.api_key or not self.base_url:
            return self._get_fallback_response(message)
        
        try:
            # Prepare API request headers
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Prepare conversation history
            messages = []
            for conv in self.conversation_history[-5:]:  # Last 5 exchanges
                messages.append({'role': 'user', 'content': conv['user']})
                messages.append({'role': 'assistant', 'content': conv['assistant']})
            
            # Add current message
            messages.append({'role': 'user', 'content': message})
            
            # Prepare request data according to HelaGPT API format
            data = {
                'messages': messages
            }
            
            # Make API request
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('type') == 'text':
                    return result.get('text', 'I apologize, but I could not process your request.')
                elif result.get('type') == 'empty':
                    # Handle empty responses gracefully
                    return self._get_fallback_response(message)
                else:
                    self.logger.error(f"API returned unexpected response type: {result}")
                    return self._get_fallback_response(message)
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return self._get_fallback_response(message)
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {e}")
            return self._get_fallback_response(message)
        except Exception as e:
            self.logger.error(f"Unexpected error in AI response: {e}")
            return self._get_fallback_response(message)
    
    def _get_fallback_response(self, message: str) -> str:
        """
        Get a fallback response when API is unavailable.
        
        Args:
            message: User message
            
        Returns:
            Fallback response string
        """
        # Simple keyword-based responses
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm Jarvis, your AI assistant. How can I help you today?"
        elif any(word in message_lower for word in ['help', 'what can you do']):
            return "I can help you with file management, opening applications, web searches, and general productivity tasks. What would you like me to do?"
        elif any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! Is there anything else I can help you with?"
        elif any(word in message_lower for word in ['bye', 'goodbye', 'exit']):
            return "Goodbye! Have a great day!"
        else:
            return "I understand you said: " + message + ". I'm still learning, so please be patient with me!"
    
    def _update_history(self, user_input: str, ai_response: str):
        """
        Update conversation history.
        
        Args:
            user_input: User input
            ai_response: AI response
        """
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






