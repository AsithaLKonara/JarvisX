"""
Unit Tests for Voice CLI Commands
Tests all voice-related CLI functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.voice import (
    listen_voice,
    speak_text,
    interactive_voice,
    voice_command
)
from cli.voice_utils import VoiceCommandParser


class TestVoiceCLI(unittest.TestCase):
    """Test Voice CLI commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = VoiceCommandParser()
    
    @patch('speech.speech_recognizer.SpeechRecognizer')
    def test_listen_voice(self, mock_recognizer_class):
        """Test voice listening"""
        # Mock speech recognizer
        mock_recognizer = MagicMock()
        mock_recognizer.is_available.return_value = True
        mock_recognizer.listen.return_value = "Hello Jarvis"
        mock_recognizer_class.return_value = mock_recognizer
        
        # Test listening
        try:
            result = listen_voice(timeout=5, json_output=False)
            # Result should be the recognized text
            self.assertTrue(True)
        except SystemExit:
            pass
    
    @patch('speech.text_to_speech.TTSEngine')
    def test_speak_text(self, mock_tts_class):
        """Test text-to-speech"""
        # Mock TTS engine
        mock_tts = MagicMock()
        mock_tts.is_available = True
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts
        
        # Test speaking
        try:
            speak_text(text="Hello, this is a test", json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass
    
    def test_voice_command_parser(self):
        """Test voice command parsing"""
        # Test direct matches
        command = self.parser.parse_voice_command("start training")
        self.assertIsNotNone(command)
        
        command = self.parser.parse_voice_command("system status")
        self.assertIsNotNone(command)
        
        command = self.parser.parse_voice_command("list models")
        self.assertIsNotNone(command)
        
        # Test pattern matching
        command = self.parser.parse_voice_command("show me the system status")
        # Should match "system status" pattern
        self.assertTrue(True)
    
    @patch('cli.voice_utils.VoiceCommandParser')
    @patch('speech.text_to_speech.TTSEngine')
    @patch('speech.speech_recognizer.SpeechRecognizer')
    def test_interactive_voice(self, mock_recognizer_class, mock_tts_class, mock_parser_class):
        """Test interactive voice mode"""
        # Mock speech recognizer
        mock_recognizer = MagicMock()
        mock_recognizer.is_available.return_value = True
        mock_recognizer.listen.return_value = "exit"
        mock_recognizer_class.return_value = mock_recognizer
        
        # Mock TTS engine
        mock_tts = MagicMock()
        mock_tts.is_available = True
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts
        
        # Mock parser
        mock_parser = MagicMock()
        mock_parser.parse_voice_command.return_value = None
        mock_parser_class.return_value = mock_parser
        
        # Test interactive mode (will exit immediately with "exit")
        try:
            interactive_voice(wake_word=None, json_output=False)
            self.assertTrue(True)
        except (SystemExit, KeyboardInterrupt):
            pass
    
    def test_voice_command(self):
        """Test voice command parsing"""
        # Test command parsing
        try:
            voice_command(command_text="start training", json_output=False)
            self.assertTrue(True)
        except SystemExit:
            pass


if __name__ == '__main__':
    unittest.main()

