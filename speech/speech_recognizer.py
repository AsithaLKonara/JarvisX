"""
Speech Recognizer - Handles speech-to-text conversion with advanced features
Supports online (Google) and offline (Vosk) recognition with noise cancellation
"""

from typing import Optional, Dict, Any
import logging
import numpy as np

# Optional: scipy for advanced noise cancellation
try:
    from scipy import signal
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("scipy not available - noise cancellation disabled. Install with: pip install scipy")

logger = logging.getLogger(__name__)


class NoiseFilter:
    """Advanced noise cancellation using spectral subtraction"""
    
    def __init__(self, noise_reduction_factor: float = 0.8):
        """
        Initialize noise filter
        
        Args:
            noise_reduction_factor: How aggressively to remove noise (0.0-1.0)
        """
        self.noise_reduction_factor = noise_reduction_factor
        self.noise_profile = None
        self.is_available = HAS_SCIPY
    
    def learn_noise_profile(self, audio_data: np.ndarray, sample_rate: int):
        """Learn noise characteristics from quiet audio"""
        if not HAS_SCIPY:
            logger.warning("scipy required for noise learning")
            return
        
        # Compute FFT
        fft = np.fft.rfft(audio_data)
        magnitude = np.abs(fft)
        
        # Store as noise profile
        self.noise_profile = magnitude * self.noise_reduction_factor
    
    def reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Reduce noise from audio using spectral subtraction
        
        Args:
            audio_data: Raw audio samples
            
        Returns:
            Noise-reduced audio
        """
        if self.noise_profile is None or not HAS_SCIPY:
            return audio_data
        
        try:
            # Apply FFT
            fft = np.fft.rfft(audio_data)
            magnitude = np.abs(fft)
            phase = np.angle(fft)
            
            # Subtract noise profile
            cleaned_magnitude = np.maximum(magnitude - self.noise_profile, 0.1)
            
            # Reconstruct signal
            cleaned_fft = cleaned_magnitude * np.exp(1j * phase)
            cleaned_audio = np.fft.irfft(cleaned_fft, n=len(audio_data))
            
            # Normalize to prevent clipping
            max_val = np.max(np.abs(cleaned_audio))
            if max_val > 0:
                cleaned_audio = cleaned_audio / max_val * 0.95
            
            return cleaned_audio.astype(np.float32)
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return audio_data


class OfflineSTT:
    """Offline speech recognition using Vosk"""
    
    def __init__(self):
        """Initialize offline STT engine"""
        self.is_available = self._check_availability()
        self.recognizer = None
        if self.is_available:
            self._init_vosk()
    
    def _check_availability(self) -> bool:
        """Check if Vosk is available"""
        try:
            import vosk
            return True
        except ImportError:
            logger.warning("Vosk not available - offline STT disabled. Install with: pip install vosk")
            return False
    
    def _init_vosk(self):
        """Initialize Vosk recognizer"""
        try:
            import vosk
            import json
            
            vosk.SetLogLevel(-1)  # Suppress Vosk logging
            
            # Create recognizer with default model
            self.recognizer = vosk.KaldiRecognizer(vosk.Model(), 16000)
        except Exception as e:
            logger.error(f"Failed to initialize Vosk: {e}")
            self.is_available = False
    
    def recognize(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Optional[str]:
        """
        Recognize speech offline using Vosk
        
        Args:
            audio_data: Audio samples
            sample_rate: Sample rate of audio
            
        Returns:
            Recognized text or None
        """
        if not self.is_available or not self.recognizer:
            return None
        
        try:
            import json
            
            # Convert to bytes
            audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            
            if self.recognizer.AcceptWaveform(audio_bytes):
                result_json = json.loads(self.recognizer.Result())
                return result_json.get('result', [{}])[0].get('conf', 0) > 0.5 and result_json.get('result', '') or None
            else:
                result_json = json.loads(self.recognizer.PartialResult())
                return result_json.get('partial', '').strip() or None
        except Exception as e:
            logger.error(f"Vosk recognition error: {e}")
            return None


class SpeechRecognizer:
    """
    Advanced speech recognizer with multiple engines
    Supports: Google Cloud (online), Vosk (offline), with noise cancellation
    """
    
    def __init__(self, use_offline: bool = False, enable_noise_reduction: bool = True):
        """
        Initialize speech recognizer
        
        Args:
            use_offline: Prefer offline recognition (Vosk) if available
            enable_noise_reduction: Enable noise cancellation
        """
        self.use_offline = use_offline
        self.enable_noise_reduction = enable_noise_reduction
        self.is_available = self._check_availability()
        self.offline_stt = OfflineSTT() if use_offline else None
        self.noise_filter = NoiseFilter() if enable_noise_reduction else None
        
        if not self.is_available:
            logger.warning("Speech recognition not available, using fallback mode")
    
    def _check_availability(self) -> bool:
        """Check if any speech recognition is available"""
        try:
            import speech_recognition
            return True
        except ImportError:
            return False
    
    def _preprocess_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Preprocess audio: normalize, noise reduction, etc.
        
        Args:
            audio_data: Raw audio samples
            
        Returns:
            Preprocessed audio
        """
        # Normalize
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val
        
        # Apply high-pass filter to remove low-frequency noise (if scipy available)
        if HAS_SCIPY:
            try:
                sos = signal.butter(4, 80, 'hp', fs=16000, output='sos')
                audio_data = signal.sosfilt(sos, audio_data)
            except:
                pass
        
        # Noise reduction
        if self.enable_noise_reduction and self.noise_filter:
            audio_data = self.noise_filter.reduce_noise(audio_data)
        
        return audio_data.astype(np.float32)
    
    def listen(self, timeout: int = 10, engine: str = "auto") -> Optional[str]:
        """
        Listen for speech input and convert to text
        
        Args:
            timeout: Maximum time to listen in seconds
            engine: "auto" (best available), "google", or "offline"
            
        Returns:
            Recognized text or None if no speech detected
        """
        if not self.is_available:
            logger.warning("Speech recognition disabled, using fallback")
            return "Hello Jarvis"
        
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            # Adjust microphone settings for better quality
            recognizer.dynamic_energy_threshold = True
            recognizer.operation_timeout = timeout
            
            with sr.Microphone() as source:
                logger.info(f"Listening for speech (timeout: {timeout}s)...")
                
                # Calibrate for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                try:
                    audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout-1)
                    logger.info("Speech captured, converting to text...")
                    
                    # Convert to numpy array for processing
                    audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # Preprocess
                    audio_data = self._preprocess_audio(audio_data)
                    
                    # Try offline first if enabled
                    if engine in ["auto", "offline"] and self.offline_stt and self.offline_stt.is_available:
                        logger.info("Trying offline recognition...")
                        text = self.offline_stt.recognize(audio_data)
                        if text:
                            logger.info(f"Offline: {text}")
                            return text
                    
                    # Fallback to Google
                    if engine in ["auto", "google"]:
                        logger.info("Trying Google Speech Recognition...")
                        text = recognizer.recognize_google(audio)
                        logger.info(f"Google: {text}")
                        return text
                    
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio")
                    return None
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    if engine == "google":
                        return None
                    # Try offline if Google fails
                    if self.offline_stt and self.offline_stt.is_available:
                        logger.info("Google failed, trying offline...")
                        text = self.offline_stt.recognize(audio_data)
                        return text
        
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return None
    
    def learn_noise(self, duration: int = 2):
        """
        Learn noise profile for better noise reduction
        
        Args:
            duration: Duration to learn noise (seconds)
        """
        if not self.noise_filter:
            logger.warning("Noise filter not enabled")
            return
        
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                logger.info(f"Learning noise profile for {duration}s...")
                audio = recognizer.listen(source, timeout=duration)
                
                audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32) / 32768.0
                self.noise_filter.learn_noise_profile(audio_data, 16000)
                
                logger.info("Noise profile learned")
        except Exception as e:
            logger.error(f"Error learning noise profile: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Speech recognizer cleaned up")
