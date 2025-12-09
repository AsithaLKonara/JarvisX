"""
Wake Word Detection
Implements "Hey Jarvis" wake word detection with background listening
"""

import logging
import numpy as np
from typing import Optional, Callable
import threading
import time

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Detect wake words for hands-free activation"""
    
    def __init__(
        self,
        wake_word: str = "hey jarvis",
        sensitivity: float = 0.7,
        energy_threshold: int = 300
    ):
        """
        Initialize wake word detector
        
        Args:
            wake_word: Wake word phrase (default: "hey jarvis")
            sensitivity: Detection sensitivity (0.0-1.0)
            energy_threshold: Audio energy threshold
        """
        self.wake_word = wake_word.lower()
        self.sensitivity = sensitivity
        self.energy_threshold = energy_threshold
        self.is_listening = False
        self.callback: Optional[Callable] = None
        self._listening_thread: Optional[threading.Thread] = None
    
    def start_listening(self, callback: Callable):
        """
        Start background listening for wake word
        
        Args:
            callback: Function to call when wake word detected
        """
        if self.is_listening:
            logger.warning("Already listening for wake word")
            return
        
        self.callback = callback
        self.is_listening = True
        
        # Start listening thread
        self._listening_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self._listening_thread.start()
        logger.info(f"Wake word detection started: '{self.wake_word}'")
    
    def stop_listening(self):
        """Stop background listening"""
        self.is_listening = False
        if self._listening_thread:
            self._listening_thread.join(timeout=1.0)
        logger.info("Wake word detection stopped")
    
    def _listen_loop(self):
        """Background listening loop"""
        try:
            from speech.speech_recognizer import SpeechRecognizer
            
            recognizer = SpeechRecognizer()
            
            if not recognizer.is_available():
                logger.warning("Speech recognition not available for wake word")
                return
            
            logger.info("Wake word detector listening...")
            
            while self.is_listening:
                try:
                    # Listen for short duration
                    text = recognizer.listen(timeout=2)
                    
                    if text:
                        text_lower = text.lower()
                        # Check if wake word is in the recognized text
                        if self.wake_word in text_lower:
                            logger.info(f"Wake word detected: '{self.wake_word}'")
                            if self.callback:
                                self.callback(text)
                    
                    # Small delay to prevent CPU spinning
                    time.sleep(0.1)
                
                except Exception as e:
                    logger.debug(f"Wake word detection error: {e}")
                    time.sleep(0.5)
        
        except ImportError:
            logger.warning("Speech recognizer not available")
        except Exception as e:
            logger.error(f"Wake word detection failed: {e}")
    
    def detect_in_text(self, text: str) -> bool:
        """
        Check if wake word is in text
        
        Args:
            text: Text to check
            
        Returns:
            True if wake word detected
        """
        return self.wake_word in text.lower()
    
    def is_active(self) -> bool:
        """Check if detector is actively listening"""
        return self.is_listening and self._listening_thread and self._listening_thread.is_alive()

