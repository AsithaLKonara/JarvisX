"""
Voice Personality System
Customizable voice tones, context-aware responses, and emotional intelligence
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class VoiceTone(Enum):
    """Voice tone options"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    FORMAL = "formal"
    ENTHUSIASTIC = "enthusiastic"
    CALM = "calm"


class VoicePersonality:
    """Manages voice personality and tone"""
    
    def __init__(
        self,
        tone: VoiceTone = VoiceTone.PROFESSIONAL,
        enthusiasm_level: float = 0.5,
        formality_level: float = 0.5
    ):
        """
        Initialize voice personality
        
        Args:
            tone: Base voice tone
            enthusiasm_level: Enthusiasm level (0.0-1.0)
            formality_level: Formality level (0.0-1.0)
        """
        self.tone = tone
        self.enthusiasm_level = enthusiasm_level
        self.formality_level = formality_level
        self.context_history = []
    
    def adapt_response(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Adapt response text based on personality and context
        
        Args:
            text: Original text
            context: Optional context (command type, success/error, etc.)
            
        Returns:
            Adapted text
        """
        adapted = text
        
        # Add tone-based prefixes/suffixes
        if context:
            if context.get('is_success'):
                adapted = self._add_success_tone(adapted)
            elif context.get('is_error'):
                adapted = self._add_error_tone(adapted)
            elif context.get('is_info'):
                adapted = self._add_info_tone(adapted)
        
        # Adjust formality
        if self.formality_level > 0.7:
            adapted = self._make_formal(adapted)
        elif self.formality_level < 0.3:
            adapted = self._make_casual(adapted)
        
        # Adjust enthusiasm
        if self.enthusiasm_level > 0.7:
            adapted = self._add_enthusiasm(adapted)
        
        return adapted
    
    def _add_success_tone(self, text: str) -> str:
        """Add success tone to text"""
        if self.tone == VoiceTone.ENTHUSIASTIC:
            return f"Great! {text}"
        elif self.tone == VoiceTone.PROFESSIONAL:
            return f"Success: {text}"
        elif self.tone == VoiceTone.FRIENDLY:
            return f"Awesome! {text}"
        else:
            return text
    
    def _add_error_tone(self, text: str) -> str:
        """Add error tone to text"""
        if self.tone == VoiceTone.CALM:
            return f"I encountered an issue: {text}"
        elif self.tone == VoiceTone.PROFESSIONAL:
            return f"Error: {text}"
        else:
            return f"Oops, {text.lower()}"
    
    def _add_info_tone(self, text: str) -> str:
        """Add info tone to text"""
        if self.tone == VoiceTone.FORMAL:
            return f"Information: {text}"
        else:
            return text
    
    def _make_formal(self, text: str) -> str:
        """Make text more formal"""
        # Simple formalization
        replacements = {
            "can't": "cannot",
            "won't": "will not",
            "I'm": "I am"
        }
        for informal, formal in replacements.items():
            text = text.replace(informal, formal)
        return text
    
    def _make_casual(self, text: str) -> str:
        """Make text more casual"""
        # Simple casualization
        if text.startswith("Success:"):
            text = text.replace("Success:", "Done!")
        if text.startswith("Error:"):
            text = text.replace("Error:", "Hmm,")
        return text
    
    def _add_enthusiasm(self, text: str) -> str:
        """Add enthusiasm to text"""
        if "!" not in text:
            text = text.rstrip(".") + "!"
        return text
    
    def set_tone(self, tone: VoiceTone):
        """Set voice tone"""
        self.tone = tone
        logger.info(f"Voice tone set to: {tone.value}")
    
    def set_enthusiasm(self, level: float):
        """Set enthusiasm level (0.0-1.0)"""
        self.enthusiasm_level = max(0.0, min(1.0, level))
    
    def set_formality(self, level: float):
        """Set formality level (0.0-1.0)"""
        self.formality_level = max(0.0, min(1.0, level))


# Global personality instance
_personality_instance: Optional[VoicePersonality] = None


def get_voice_personality() -> VoicePersonality:
    """Get global voice personality instance"""
    global _personality_instance
    if _personality_instance is None:
        _personality_instance = VoicePersonality()
    return _personality_instance

