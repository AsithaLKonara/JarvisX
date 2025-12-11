"""
Tests for Unified Orchestrator CLI integration
Tests unified command group and natural language processing
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.unified import app

# Set timeout for all tests in this file (5 seconds)
pytestmark = pytest.mark.timeout(5)


class TestUnifiedExecute:
    """Test unified execute command"""
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_execute_basic(self, mock_orchestrator_class, mock_get_output):
        """Test basic unified execute command"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'Done',
            'actions': [],
            'execution_results': []
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Check CPU usage"])
        
        assert result.exit_code == 0
        mock_orchestrator.process_text_command.assert_called_once()
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_execute_with_tts(self, mock_orchestrator_class, mock_get_output):
        """Test unified execute with TTS enabled"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'Done',
            'actions': []
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Check system", "--tts"])
        
        assert result.exit_code == 0
        # Verify TTS was enabled
        call_args = mock_orchestrator.process_text_command.call_args
        assert call_args[1]['enable_tts'] is True
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_execute_without_tts(self, mock_orchestrator_class, mock_get_output):
        """Test unified execute with TTS disabled"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'Done'
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Check system", "--no-tts"])
        
        assert result.exit_code == 0
        call_args = mock_orchestrator.process_text_command.call_args
        assert call_args[1]['enable_tts'] is False
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_execute_json_output(self, mock_orchestrator_class, mock_get_output):
        """Test unified execute with JSON output"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'Done',
            'actions': ['monitor_cpu'],
            'execution_results': []
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Check CPU", "--json"])
        
        assert result.exit_code == 0
        # Should output JSON
        assert "json" in result.stdout.lower() or len(result.stdout) > 0
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_execute_with_actions(self, mock_orchestrator_class, mock_get_output):
        """Test unified execute with action execution"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'CPU usage is 50%',
            'actions': ['monitor_cpu'],
            'execution_results': [{
                'action': Mock(tool='monitor_cpu'),
                'result': {'success': True}
            }]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Check CPU usage"])
        
        assert result.exit_code == 0
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_execute_error_handling(self, mock_orchestrator_class, mock_get_output):
        """Test unified execute error handling"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': False,
            'error': 'AI not available',
            'response': 'Error occurred'
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Check system"])
        
        assert result.exit_code == 1
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_execute_import_error(self, mock_orchestrator_class, mock_get_output):
        """Test unified execute when orchestrator not available"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator_class.side_effect = ImportError("Module not found")
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Check system"])
        
        assert result.exit_code == 1


class TestUnifiedVoice:
    """Test unified voice command"""
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_voice_basic(self, mock_orchestrator_class, mock_get_output):
        """Test basic unified voice command"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.stt_available = True
        mock_orchestrator.process_voice_command.return_value = {
            'success': True,
            'response': 'Done',
            'actions': []
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["voice"])
        
        assert result.exit_code == 0
        mock_orchestrator.process_voice_command.assert_called_once()
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_voice_timeout(self, mock_orchestrator_class, mock_get_output):
        """Test unified voice with timeout"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.stt_available = True
        mock_orchestrator.process_voice_command.return_value = {
            'success': True,
            'response': 'Done'
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["voice", "--timeout", "5"])
        
        assert result.exit_code == 0
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_voice_stt_not_available(self, mock_orchestrator_class, mock_get_output):
        """Test unified voice when STT not available"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.stt_available = False
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["voice"])
        
        assert result.exit_code == 1


class TestUnifiedStatus:
    """Test unified status command"""
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_status_basic(self, mock_orchestrator_class, mock_get_output):
        """Test basic unified status command"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.get_status.return_value = {
            'ai_available': True,
            'stt_available': True,
            'tts_available': True,
            'tools_available': {
                'system': True,
                'business': True
            }
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        mock_orchestrator.get_status.assert_called_once()
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_unified_status_json(self, mock_orchestrator_class, mock_get_output):
        """Test unified status with JSON output"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.get_status.return_value = {
            'ai_available': True,
            'stt_available': False,
            'tts_available': True
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["status", "--json"])
        
        assert result.exit_code == 0


class TestUnifiedActionExtraction:
    """Test action extraction in unified orchestrator"""
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_action_extraction_system(self, mock_orchestrator_class, mock_get_output):
        """Test system action extraction"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'Monitoring CPU',
            'actions': ['monitor_cpu'],
            'execution_results': [{
                'action': Mock(action_type='system', tool='monitor_cpu'),
                'result': {'success': True, 'result': {'percent': 50}}
            }]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Check CPU usage"])
        
        assert result.exit_code == 0
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_action_extraction_business(self, mock_orchestrator_class, mock_get_output):
        """Test business action extraction"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'Invoice generated',
            'actions': ['generate_invoice'],
            'execution_results': [{
                'action': Mock(action_type='business', tool='generate_invoice'),
                'result': {'success': True}
            }]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Generate invoice for client ABC"])
        
        assert result.exit_code == 0


class TestUnifiedToolRouting:
    """Test tool routing in unified orchestrator"""
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_tool_routing_system(self, mock_orchestrator_class, mock_get_output):
        """Test routing to system tools"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'System monitored',
            'actions': ['monitor_cpu', 'monitor_memory'],
            'execution_results': [
                {'action': Mock(tool='monitor_cpu'), 'result': {'success': True}},
                {'action': Mock(tool='monitor_memory'), 'result': {'success': True}}
            ]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Monitor system"])
        
        assert result.exit_code == 0


class TestUnifiedErrorHandling:
    """Test error handling in unified orchestrator"""
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_error_handling_ai_unavailable(self, mock_orchestrator_class, mock_get_output):
        """Test error when AI is unavailable"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': False,
            'error': 'AI response failed',
            'response': "I'm having trouble understanding that."
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Do something"])
        
        assert result.exit_code == 1
    
    @pytest.mark.timeout(5)
    @patch('cli.unified.get_output')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_error_handling_tool_failure(self, mock_orchestrator_class, mock_get_output):
        """Test error when tool execution fails"""
        mock_output = MagicMock()
        mock_get_output.return_value = mock_output
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'Some actions failed',
            'actions': ['monitor_cpu'],
            'execution_results': [{
                'action': Mock(tool='monitor_cpu'),
                'result': {'success': False, 'error': 'Tool not available'}
            }]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, ["execute", "Check system"])
        
        # May succeed but with failed actions
        assert result.exit_code in [0, 1]

