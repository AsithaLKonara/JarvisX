#!/usr/bin/env python3
"""
Voice Orchestrator - Voice-specific orchestrator with continuous listening
Handles wake word detection, continuous listening, and voice feedback
"""

import logging
import threading
import queue
from typing import Dict, Any, Optional, Callable
from core.unified_orchestrator import UnifiedOrchestrator

logger = logging.getLogger(__name__)


class VoiceOrchestrator:
    """
    Voice-specific orchestrator that handles:
    - Continuous listening
    - Wake word detection
    - Voice command processing
    - Voice feedback
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize voice orchestrator
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize unified orchestrator
        self.orchestrator = UnifiedOrchestrator(config)
        
        # Voice control state
        self.is_listening = False
        self.is_continuous_mode = False
        self.wake_word_enabled = False
        self.wake_word = "hey jarvis"
        
        # Threading
        self.listen_thread = None
        self.command_queue = queue.Queue()
        self.stop_event = threading.Event()
        
        # Callbacks
        self.on_command_callback: Optional[Callable] = None
        self.on_wake_word_callback: Optional[Callable] = None
        
        self.logger.info("✅ Voice Orchestrator initialized")
    
    def start_voice_mode(
        self,
        continuous: bool = True,
        wake_word: bool = False
    ) -> bool:
        """
        Start voice mode with continuous listening
        
        Args:
            continuous: Enable continuous listening
            wake_word: Enable wake word detection
            
        Returns:
            True if started successfully
        """
        if self.is_listening:
            self.logger.warning("Voice mode already active")
            return False
        
        self.is_continuous_mode = continuous
        self.wake_word_enabled = wake_word
        
        try:
            if continuous:
                self._start_continuous_listening()
            else:
                self.is_listening = True
            
            self.logger.info(f"🎤 Voice mode started (continuous: {continuous}, wake_word: {wake_word})")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to start voice mode: {e}")
            return False
    
    def stop_voice_mode(self):
        """Stop voice mode"""
        self.is_listening = False
        self.is_continuous_mode = False
        self.stop_event.set()
        
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2.0)
        
        self.logger.info("🎤 Voice mode stopped")
    
    def process_voice_input(
        self,
        voice_input: Optional[str] = None,
        enable_tts: bool = True
    ) -> Dict[str, Any]:
        """
        Process voice input through unified pipeline
        
        Args:
            voice_input: Voice input text (if None, will listen)
            enable_tts: Whether to speak response
            
        Returns:
            Processing results
        """
        return self.orchestrator.process_voice_command(
            voice_input=voice_input,
            enable_tts=enable_tts
        )
    
    def _start_continuous_listening(self):
        """Start continuous listening thread"""
        self.is_listening = True
        self.stop_event.clear()
        
        self.listen_thread = threading.Thread(
            target=self._continuous_listen_loop,
            daemon=True
        )
        self.listen_thread.start()
    
    def _continuous_listen_loop(self):
        """Continuous listening loop"""
        self.logger.info("🎤 Starting continuous listening loop...")
        
        while self.is_listening and not self.stop_event.is_set():
            try:
                # Check for wake word if enabled
                if self.wake_word_enabled:
                    if not self._check_wake_word():
                        continue
                
                # Listen for command
                if self.orchestrator.stt_available and self.orchestrator.stt:
                    self.logger.info("🎤 Listening for command...")
                    text = self.orchestrator.stt.listen(timeout=5)
                    
                    if text:
                        self.logger.info(f"📥 Heard: {text}")
                        
                        # Process command
                        result = self.process_voice_input(voice_input=text, enable_tts=True)
                        
                        # Call callback if set
                        if self.on_command_callback:
                            try:
                                self.on_command_callback(result)
                            except Exception as e:
                                self.logger.error(f"Command callback error: {e}")
                
                # Small delay to prevent CPU spinning
                import time
                time.sleep(0.1)
            
            except KeyboardInterrupt:
                self.logger.info("Continuous listening interrupted")
                break
            except Exception as e:
                self.logger.error(f"Error in listening loop: {e}")
                import time
                time.sleep(1.0)  # Wait before retrying
    
    def _check_wake_word(self) -> bool:
        """Check for wake word"""
        if not self.orchestrator.stt_available or not self.orchestrator.stt:
            return False
        
        try:
            # Listen briefly for wake word
            text = self.orchestrator.stt.listen(timeout=2)
            if text and self.wake_word.lower() in text.lower():
                self.logger.info(f"🔔 Wake word detected: {self.wake_word}")
                
                # Acknowledge wake word
                if self.orchestrator.tts_available:
                    self.orchestrator.tts.speak("Yes, I'm listening", blocking=True)
                
                # Call callback if set
                if self.on_wake_word_callback:
                    try:
                        self.on_wake_word_callback()
                    except Exception as e:
                        self.logger.error(f"Wake word callback error: {e}")
                
                return True
        except Exception as e:
            self.logger.debug(f"Wake word check: {e}")
        
        return False
    
    def set_wake_word(self, wake_word: str):
        """Set custom wake word"""
        self.wake_word = wake_word.lower()
        self.logger.info(f"Wake word set to: {self.wake_word}")
    
    def set_command_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback for when commands are processed"""
        self.on_command_callback = callback
    
    def set_wake_word_callback(self, callback: Callable[[], None]):
        """Set callback for when wake word is detected"""
        self.on_wake_word_callback = callback
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice orchestrator status"""
        return {
            'is_listening': self.is_listening,
            'is_continuous_mode': self.is_continuous_mode,
            'wake_word_enabled': self.wake_word_enabled,
            'wake_word': self.wake_word,
            'orchestrator_status': self.orchestrator.get_status()
        }

