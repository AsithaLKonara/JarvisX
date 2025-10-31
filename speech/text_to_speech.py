"""
Text-to-Speech Engine - Converts text responses to speech
Supports multiple engines: pyttsx3 (offline), gTTS (online), and ElevenLabs (premium)
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class TTSEngine:
    """Text-to-Speech engine with multiple backend support"""
    
    def __init__(
        self,
        engine: str = "pyttsx3",
        language: str = "en",
        voice_id: Optional[str] = None,
        rate: int = 150,
        volume: float = 1.0,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize TTS engine
        
        Args:
            engine: TTS engine to use ('pyttsx3', 'gtts', 'elevenlabs')
            language: Language code (e.g., 'en', 'si')
            voice_id: Specific voice ID (engine-dependent)
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            cache_dir: Directory for caching audio files
        """
        self.engine_name = engine
        self.language = language
        self.voice_id = voice_id
        self.rate = rate
        self.volume = volume
        self.cache_dir = Path(cache_dir) if cache_dir else Path("cache/tts")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.engine = None
        self.is_available = False
        
        # Initialize the selected engine
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the selected TTS engine"""
        try:
            if self.engine_name == "pyttsx3":
                self._init_pyttsx3()
            elif self.engine_name == "gtts":
                self._init_gtts()
            elif self.engine_name == "elevenlabs":
                self._init_elevenlabs()
            else:
                logger.warning(f"Unknown TTS engine: {self.engine_name}, falling back to pyttsx3")
                self.engine_name = "pyttsx3"
                self._init_pyttsx3()
        except Exception as e:
            logger.error(f"Failed to initialize {self.engine_name}: {e}")
            self.is_available = False
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 (offline TTS)"""
        try:
            import pyttsx3
            
            self.engine = pyttsx3.init()
            
            # Set properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Set voice if specified
            if self.voice_id:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if self.voice_id in voice.id or self.voice_id in voice.name:
                        self.engine.setProperty('voice', voice.id)
                        break
            
            self.is_available = True
            logger.info("✅ pyttsx3 TTS initialized (offline)")
            
        except ImportError:
            logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")
            self.is_available = False
        except Exception as e:
            logger.error(f"pyttsx3 initialization failed: {e}")
            self.is_available = False
    
    def _init_gtts(self):
        """Initialize gTTS (online TTS)"""
        try:
            from gtts import gTTS
            import pygame
            
            # Just verify imports work
            self.is_available = True
            logger.info("✅ gTTS initialized (online)")
            
        except ImportError:
            logger.warning("gTTS not installed. Install with: pip install gtts pygame")
            self.is_available = False
        except Exception as e:
            logger.error(f"gTTS initialization failed: {e}")
            self.is_available = False
    
    def _init_elevenlabs(self):
        """Initialize ElevenLabs (premium TTS)"""
        try:
            from elevenlabs import generate, play, set_api_key
            
            # Get API key from environment
            api_key = os.getenv('ELEVENLABS_API_KEY')
            if not api_key:
                logger.warning("ELEVENLABS_API_KEY not set in environment")
                self.is_available = False
                return
            
            set_api_key(api_key)
            self.is_available = True
            logger.info("✅ ElevenLabs TTS initialized (premium)")
            
        except ImportError:
            logger.warning("elevenlabs not installed. Install with: pip install elevenlabs")
            self.is_available = False
        except Exception as e:
            logger.error(f"ElevenLabs initialization failed: {e}")
            self.is_available = False
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
            blocking: Wait for speech to finish before returning
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            logger.warning("TTS engine not available")
            return False
        
        if not text or not text.strip():
            return False
        
        try:
            if self.engine_name == "pyttsx3":
                return self._speak_pyttsx3(text, blocking)
            elif self.engine_name == "gtts":
                return self._speak_gtts(text, blocking)
            elif self.engine_name == "elevenlabs":
                return self._speak_elevenlabs(text, blocking)
            return False
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    def _speak_pyttsx3(self, text: str, blocking: bool) -> bool:
        """Speak using pyttsx3"""
        try:
            self.engine.say(text)
            if blocking:
                self.engine.runAndWait()
            else:
                # Non-blocking mode
                self.engine.startLoop(False)
                self.engine.iterate()
                self.engine.endLoop()
            return True
        except Exception as e:
            logger.error(f"pyttsx3 speak error: {e}")
            return False
    
    def _speak_gtts(self, text: str, blocking: bool) -> bool:
        """Speak using gTTS"""
        try:
            from gtts import gTTS
            import pygame
            import hashlib
            
            # Create cache filename
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_file = self.cache_dir / f"{text_hash}_{self.language}.mp3"
            
            # Generate or use cached audio
            if not cache_file.exists():
                tts = gTTS(text=text, lang=self.language, slow=False)
                tts.save(str(cache_file))
            
            # Play audio
            pygame.mixer.init()
            pygame.mixer.music.load(str(cache_file))
            pygame.mixer.music.play()
            
            if blocking:
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            
            return True
            
        except Exception as e:
            logger.error(f"gTTS speak error: {e}")
            return False
    
    def _speak_elevenlabs(self, text: str, blocking: bool) -> bool:
        """Speak using ElevenLabs"""
        try:
            from elevenlabs import generate, play
            
            voice = self.voice_id or "Adam"  # Default voice
            
            audio = generate(
                text=text,
                voice=voice,
                model="eleven_monolingual_v1"
            )
            
            if blocking:
                play(audio)
            
            return True
            
        except Exception as e:
            logger.error(f"ElevenLabs speak error: {e}")
            return False
    
    def stop(self):
        """Stop any ongoing speech"""
        try:
            if self.engine_name == "pyttsx3" and self.engine:
                self.engine.stop()
            elif self.engine_name == "gtts":
                import pygame
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
        except Exception as e:
            logger.error(f"Error stopping TTS: {e}")
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        if self.engine_name == "pyttsx3" and self.engine:
            try:
                voices = self.engine.getProperty('voices')
                return [
                    {
                        'id': voice.id,
                        'name': voice.name,
                        'languages': voice.languages,
                        'gender': getattr(voice, 'gender', 'unknown')
                    }
                    for voice in voices
                ]
            except Exception as e:
                logger.error(f"Error getting voices: {e}")
                return []
        return []
    
    def set_voice(self, voice_id: str) -> bool:
        """Set the voice to use"""
        if self.engine_name == "pyttsx3" and self.engine:
            try:
                self.engine.setProperty('voice', voice_id)
                self.voice_id = voice_id
                return True
            except Exception as e:
                logger.error(f"Error setting voice: {e}")
                return False
        elif self.engine_name in ["elevenlabs"]:
            self.voice_id = voice_id
            return True
        return False
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate (words per minute)"""
        if self.engine_name == "pyttsx3" and self.engine:
            try:
                self.engine.setProperty('rate', rate)
                self.rate = rate
                return True
            except Exception as e:
                logger.error(f"Error setting rate: {e}")
                return False
        return False
    
    def set_volume(self, volume: float) -> bool:
        """Set volume (0.0 to 1.0)"""
        if self.engine_name == "pyttsx3" and self.engine:
            try:
                self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
                self.volume = volume
                return True
            except Exception as e:
                logger.error(f"Error setting volume: {e}")
                return False
        return False


def test_tts():
    """Test TTS functionality"""
    print("🎤 Testing TTS Engines...\n")
    
    # Test pyttsx3 (offline)
    print("1. Testing pyttsx3 (offline)...")
    tts1 = TTSEngine(engine="pyttsx3", rate=150)
    if tts1.is_available:
        print("   ✅ pyttsx3 available")
        tts1.speak("Hello! I am Jarvis, your AI assistant.", blocking=True)
        print("   ✅ Speech completed")
    else:
        print("   ❌ pyttsx3 not available")
    
    print()
    
    # Test gTTS (online)
    print("2. Testing gTTS (online)...")
    tts2 = TTSEngine(engine="gtts", language="en")
    if tts2.is_available:
        print("   ✅ gTTS available")
        tts2.speak("This is Google Text to Speech.", blocking=True)
        print("   ✅ Speech completed")
    else:
        print("   ❌ gTTS not available")
    
    print()
    print("🎉 TTS testing complete!")


if __name__ == "__main__":
    test_tts()

