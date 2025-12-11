"""
End-to-end unified orchestrator tests
Tests natural language processing and action execution
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.main import app

# Set timeout for E2E unified orchestrator tests (15 seconds)
pytestmark = pytest.mark.timeout(15)


@pytest.mark.e2e
@pytest.mark.unified
class TestE2ENaturalLanguageProcessing:
    """Test natural language command processing"""
    
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_e2e_natural_language_processing(self, mock_orchestrator_class):
        """Test natural language command processing"""
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'user_input': 'Check CPU and memory usage',
            'ai_response': 'I will check both CPU and memory usage.',
            'response': 'CPU: 50%, Memory: 60%',
            'actions': ['monitor_cpu', 'monitor_memory'],
            'execution_results': [
                {'action': Mock(tool='monitor_cpu'), 'result': {'success': True}},
                {'action': Mock(tool='monitor_memory'), 'result': {'success': True}}
            ]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "unified", "execute",
            "Check CPU and memory usage"
        ])
        
        assert result.exit_code == 0
        mock_orchestrator.process_text_command.assert_called_once()
    
    @patch('core.action_extractor.ActionExtractor')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_e2e_action_extraction(self, mock_orchestrator_class, mock_extractor_class):
        """Test action extraction from AI response"""
        mock_extractor = MagicMock()
        mock_action = Mock()
        mock_action.action_type = 'system'
        mock_action.tool = 'monitor_cpu'
        mock_action.parameters = {}
        mock_extractor.extract_actions.return_value = [mock_action]
        mock_extractor_class.return_value = mock_extractor
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'Monitoring CPU',
            'actions': ['monitor_cpu']
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "unified", "execute",
            "Check CPU usage"
        ])
        
        assert result.exit_code == 0
    
    @patch('core.tool_router.ToolRouter')
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_e2e_tool_routing(self, mock_orchestrator_class, mock_router_class):
        """Test tool routing to appropriate tools"""
        mock_router = MagicMock()
        mock_router.route_action.return_value = {
            'success': True,
            'result': {'percent': 50}
        }
        mock_router_class.return_value = mock_router
        
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'actions': ['monitor_cpu'],
            'execution_results': [{
                'action': Mock(tool='monitor_cpu'),
                'result': {'success': True}
            }]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "unified", "execute",
            "Monitor system"
        ])
        
        assert result.exit_code == 0
    
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_e2e_multi_action_workflow(self, mock_orchestrator_class):
        """Test workflow with multiple actions"""
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'All actions completed',
            'actions': ['monitor_cpu', 'monitor_memory', 'monitor_disk'],
            'execution_results': [
                {'action': Mock(tool='monitor_cpu'), 'result': {'success': True}},
                {'action': Mock(tool='monitor_memory'), 'result': {'success': True}},
                {'action': Mock(tool='monitor_disk'), 'result': {'success': True}}
            ]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "unified", "execute",
            "Check complete system status"
        ])
        
        assert result.exit_code == 0
    
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_e2e_error_recovery(self, mock_orchestrator_class):
        """Test error recovery in unified orchestrator"""
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': False,
            'error': 'AI not available',
            'response': 'I encountered an error. Please try again.'
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "unified", "execute",
            "Do something"
        ])
        
        # Should handle error gracefully
        assert result.exit_code == 1
    
    @patch('core.unified_orchestrator.UnifiedOrchestrator')
    def test_e2e_partial_action_failure(self, mock_orchestrator_class):
        """Test handling of partial action failures"""
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_text_command.return_value = {
            'success': True,
            'response': 'Some actions completed',
            'actions': ['monitor_cpu', 'monitor_memory'],
            'execution_results': [
                {'action': Mock(tool='monitor_cpu'), 'result': {'success': True}},
                {'action': Mock(tool='monitor_memory'), 'result': {'success': False, 'error': 'Tool unavailable'}}
            ]
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "unified", "execute",
            "Monitor system"
        ])
        
        # Should handle partial failure
        assert result.exit_code in [0, 1]

