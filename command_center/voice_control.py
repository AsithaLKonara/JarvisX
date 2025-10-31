"""
Voice Control - Handles voice input and output
Phase 1 of Jarvis X V2
"""

import speech_recognition as sr
import pyttsx3
from typing import Optional, Callable
import threading
import queue

class VoiceControl:
    """Handles voice input and output operations"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.is_listening = False
        self.voice_queue = queue.Queue()
        self.callbacks = {}
        
        # Configure TTS
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)
    
    def speak(self, text: str) -> bool:
        """Speak text using TTS"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen for voice input"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=timeout)
            
            text = self.recognizer.recognize_google(audio)
            return text.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"Voice recognition error: {e}")
            return None
    
    def start_continuous_listening(self, callback: Callable[[str], None]):
        """Start continuous voice listening"""
        def listen_worker():
            while self.is_listening:
                try:
                    text = self.listen(timeout=1)
                    if text:
                        callback(text)
                except Exception as e:
                    print(f"Continuous listening error: {e}")
        
        self.is_listening = True
        thread = threading.Thread(target=listen_worker)
        thread.daemon = True
        thread.start()
    
    def stop_listening(self):
        """Stop continuous voice listening"""
        self.is_listening = False
    
    def register_callback(self, command: str, callback: Callable[[str], None]):
        """Register a voice command callback"""
        self.callbacks[command.lower()] = callback
    
    def process_voice_command(self, text: str) -> bool:
        """Process a voice command"""
        for command, callback in self.callbacks.items():
            if command in text:
                callback(text)
                return True
        return False



