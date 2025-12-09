"""
Speaker Recognition
Multi-user support with voice authentication and personalized responses
"""

import logging
import hashlib
from typing import Optional, Dict, List
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class SpeakerProfile:
    """Profile for a recognized speaker"""
    
    def __init__(self, speaker_id: str, name: str, voice_features: Optional[Dict] = None):
        """
        Initialize speaker profile
        
        Args:
            speaker_id: Unique speaker ID
            name: Speaker name
            voice_features: Voice feature vector (for recognition)
        """
        self.speaker_id = speaker_id
        self.name = name
        self.voice_features = voice_features or {}
        self.preferences = {}
        self.recognition_count = 0
    
    def update_features(self, features: Dict):
        """Update voice features"""
        self.voice_features.update(features)
        self.recognition_count += 1


class SpeakerRecognizer:
    """Recognize speakers from voice"""
    
    def __init__(self, profiles_file: Optional[Path] = None):
        """
        Initialize speaker recognizer
        
        Args:
            profiles_file: Path to speaker profiles file
        """
        if profiles_file is None:
            from cli.utils import get_project_root
            profiles_file = get_project_root() / "data" / "speaker_profiles.json"
        
        self.profiles_file = Path(profiles_file)
        self.profiles_file.parent.mkdir(parents=True, exist_ok=True)
        self.profiles: Dict[str, SpeakerProfile] = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """Load speaker profiles from file"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    for speaker_id, profile_data in data.items():
                        self.profiles[speaker_id] = SpeakerProfile(
                            speaker_id=speaker_id,
                            name=profile_data.get('name', 'Unknown'),
                            voice_features=profile_data.get('voice_features', {})
                        )
            except Exception as e:
                logger.warning(f"Failed to load speaker profiles: {e}")
    
    def _save_profiles(self):
        """Save speaker profiles to file"""
        try:
            data = {
                speaker_id: {
                    "name": profile.name,
                    "voice_features": profile.voice_features,
                    "preferences": profile.preferences
                }
                for speaker_id, profile in self.profiles.items()
            }
            with open(self.profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save speaker profiles: {e}")
    
    def register_speaker(self, name: str, voice_sample: Optional[str] = None) -> str:
        """
        Register a new speaker
        
        Args:
            name: Speaker name
            voice_sample: Optional voice sample text
            
        Returns:
            Speaker ID
        """
        # Generate speaker ID from name
        speaker_id = hashlib.md5(name.encode()).hexdigest()[:8]
        
        # Create profile
        profile = SpeakerProfile(
            speaker_id=speaker_id,
            name=name,
            voice_features={"sample": voice_sample} if voice_sample else {}
        )
        
        self.profiles[speaker_id] = profile
        self._save_profiles()
        
        logger.info(f"Registered speaker: {name} (ID: {speaker_id})")
        return speaker_id
    
    def recognize(self, audio_data: Optional[bytes] = None, text: Optional[str] = None) -> Optional[SpeakerProfile]:
        """
        Recognize speaker from audio or text
        
        Args:
            audio_data: Audio data (for future audio-based recognition)
            text: Recognized text (for text-based recognition)
            
        Returns:
            Speaker profile or None if not recognized
        """
        # Simple text-based recognition (can be enhanced with audio analysis)
        if text:
            # Check for speaker name in text
            text_lower = text.lower()
            for profile in self.profiles.values():
                if profile.name.lower() in text_lower:
                    logger.info(f"Recognized speaker: {profile.name}")
                    return profile
        
        # If no match, return None (unknown speaker)
        return None
    
    def get_profile(self, speaker_id: str) -> Optional[SpeakerProfile]:
        """Get speaker profile by ID"""
        return self.profiles.get(speaker_id)
    
    def list_speakers(self) -> List[SpeakerProfile]:
        """List all registered speakers"""
        return list(self.profiles.values())
    
    def update_preferences(self, speaker_id: str, preferences: Dict):
        """Update speaker preferences"""
        if speaker_id in self.profiles:
            self.profiles[speaker_id].preferences.update(preferences)
            self._save_profiles()


# Global recognizer instance
_recognizer_instance: Optional[SpeakerRecognizer] = None


def get_speaker_recognizer() -> SpeakerRecognizer:
    """Get global speaker recognizer instance"""
    global _recognizer_instance
    if _recognizer_instance is None:
        _recognizer_instance = SpeakerRecognizer()
    return _recognizer_instance

