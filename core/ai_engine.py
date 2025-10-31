"""
JARVIS AI - AI Engine with Avatar Integration
Handles HelaGPT API integration and AI processing with state management.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
from utils.config import Config
import os

# Try to import PySide6 signals, fallback to None if not available
try:
    from PySide6.QtCore import Signal, QObject
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False


class AIEngine(QObject if HAS_PYSIDE else object):
    """
    AI Engine for processing user inputs and generating responses.
    Integrates with HelaGPT API with avatar state management.
    """
    
    # PySide6 signals if available
    if HAS_PYSIDE:
        state_changed = Signal(str)           # state_name
        processing_started = Signal()
        processing_completed = Signal(str)    # response
        emotion_detected = Signal(str, float) # emotion_name, confidence
        confidence_updated = Signal(float)    # confidence_score
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the AI Engine."""
        if HAS_PYSIDE:
            super().__init__()
        
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        self.api_key = self.config.get('helagpt_api_key') or os.getenv('HELAGPT_API_KEY')
        self.base_url = self.config.get('helagpt_base_url') or os.getenv('HELAGPT_BASE_URL')
        self.conversation_history = []
        self.current_state = "IDLE"
        self.confidence_score = 0.0
        self.last_emotion = None
        
        # State callbacks
        self.state_callbacks = []
        
        if not self.api_key:
            self.logger.warning("HelaGPT API key not found. AI features will be limited.")
    
    def on_state_change(self, callback: Callable):
        """Register callback for state changes."""
        self.state_callbacks.append(callback)
    
    def _emit_state_change(self, new_state: str):
        """Emit state change signal."""
        self.current_state = new_state
        
        # Emit PySide6 signal if available
        if HAS_PYSIDE:
            self.state_changed.emit(new_state)
        
        # Call registered callbacks
        for callback in self.state_callbacks:
            try:
                callback(new_state)
            except Exception as e:
                self.logger.error(f"Error in state change callback: {e}")
    
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
            # Emit processing started
            self._emit_state_change("PROCESSING")
            if HAS_PYSIDE:
                self.processing_started.emit()
            
            # Prepare the message for HelaGPT
            message = self._prepare_message(command, context)
            
            # Analyze emotion from input
            emotion, confidence = self._analyze_emotion(message)
            if emotion:
                self.last_emotion = emotion
                self.confidence_score = confidence
                if HAS_PYSIDE:
                    self.emotion_detected.emit(emotion, confidence)
            
            # Get AI response
            response = self._get_ai_response(message)
            
            # Update conversation history
            self._update_history(command.get('original_text', ''), response)
            
            # Emit processing completed
            if HAS_PYSIDE:
                self.processing_completed.emit(response)
            self._emit_state_change("IDLE")
            
            return response
        
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            self._emit_state_change("ERROR")
            return "I'm sorry, I encountered an error processing your request."
    
    def get_response(self, user_input: str) -> str:
        """
        Get a response for user input (simplified interface).
        
        Args:
            user_input: User's text input
            
        Returns:
            AI-generated response
        """
        command = {'original_text': user_input}
        return self.process(command)
    
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
    
    def _analyze_emotion(self, message: str) -> tuple:
        """
        Analyze emotion in user message.
        
        Returns:
            Tuple of (emotion_name, confidence_score)
        """
        try:
            message_lower = message.lower()
            
            # Simple emotion detection based on keywords
            emotions = {
                'happy': ['happy', 'great', 'excellent', 'wonderful', 'amazing', 'love'],
                'sad': ['sad', 'down', 'depressed', 'unhappy', 'miserable'],
                'angry': ['angry', 'furious', 'mad', 'hate', 'despise'],
                'confused': ['confused', 'puzzled', 'unclear', 'uncertain', 'lost'],
                'excited': ['excited', 'thrilled', 'eager', 'enthusiastic', 'pumped'],
            }
            
            scores = {}
            for emotion, keywords in emotions.items():
                score = sum(message_lower.count(keyword) for keyword in keywords)
                if score > 0:
                    scores[emotion] = score
            
            if scores:
                best_emotion = max(scores, key=scores.get)
                confidence = min(scores[best_emotion] / len(message.split()), 1.0)
                return best_emotion, confidence
            
            return None, 0.0
        
        except Exception as e:
            self.logger.error(f"Error analyzing emotion: {e}")
            return None, 0.0
    
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
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 exchanges
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_current_state(self) -> str:
        """Get current AI engine state."""
        return self.current_state
    
    def get_confidence_score(self) -> float:
        """Get confidence score for last response."""
        return self.confidence_score
    
    def get_last_emotion(self) -> Optional[str]:
        """Get last detected emotion."""
        return self.last_emotion
