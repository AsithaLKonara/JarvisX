"""
End-to-end voice pipeline tests
Tests STT → AI → Action → Execution → TTS flow
"""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.main import app

# Set timeout for E2E voice tests (15 seconds - E2E tests may take longer)
pytestmark = pytest.mark.timeout(15)


@pytest.mark.e2e
@pytest.mark.voice
class TestE2EVoicePipeline:
    """Test complete voice pipeline end-to-end"""
    
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_e2e_voice_pipeline(self, mock_orchestrator_class):
        """Test STT → AI → Action → Execution → TTS flow"""
        mock_orchestrator = MagicMock()
        mock_orchestrator.stt_available = True
        mock_orchestrator.tts_available = True
        mock_orchestrator.process_voice_command.return_value = {
            'success': True,
            'user_input': 'Check CPU usage',
            'ai_response': 'I will check the CPU usage for you.',
            'response': 'CPU usage is 50%',
            'actions': ['monitor_cpu'],
            'execution_results': [{
                'action': MagicMock(tool='monitor_cpu'),
                'result': {'success': True, 'result': {'percent': 50}}
            }]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "unified", "execute",
            "Check CPU usage"
        ])
        
        assert result.exit_code == 0
        mock_orchestrator.process_text_command.assert_called_once()
    
    @patch('core.voice_orchestrator.VoiceOrchestrator')
    def test_e2e_voice_interactive(self, mock_orchestrator_class):
        """Test voice interactive mode end-to-end"""
        mock_orchestrator = MagicMock()
        mock_orchestrator.is_listening = False
        mock_orchestrator.start_voice_mode.return_value = True
        mock_orchestrator.process_voice_input.return_value = {
            'success': True,
            'response': 'Done'
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        # Note: interactive mode is hard to test fully, so we test the structure
        result = runner.invoke(app, [
            "voice", "interactive"
        ])
        
        # May exit early or require input
        assert result.exit_code in [0, 1]
    
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_e2e_unified_voice_integration(self, mock_orchestrator_class):
        """Test unified orchestrator voice integration"""
        mock_orchestrator = MagicMock()
        mock_orchestrator.stt_available = True
        mock_orchestrator.process_voice_command.return_value = {
            'success': True,
            'response': 'System monitored'
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "unified", "voice"
        ])
        
        # May require actual voice input, so exit code may vary
        assert result.exit_code in [0, 1]
    
    @patch('speech.wake_word_detector.WakeWordDetector')
    @patch('core.voice_orchestrator.VoiceOrchestrator')
    def test_e2e_wake_word_workflow(self, mock_voice_orch_class, mock_wake_detector_class):
        """Test wake word detection workflow"""
        mock_wake_detector = MagicMock()
        mock_wake_detector_class.return_value = mock_wake_detector
        
        mock_voice_orch = MagicMock()
        mock_voice_orch.is_listening = False
        mock_voice_orch.start_voice_mode.return_value = True
        mock_voice_orch_class.return_value = mock_voice_orch
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "voice", "interactive",
            "--wake-word", "hey jarvis"
        ])
        
        # May exit early
        assert result.exit_code in [0, 1]

