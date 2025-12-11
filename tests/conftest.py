"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure pytest timeout for all tests
# Timeouts are configured in pyproject.toml


@pytest.fixture
def project_root_path():
    """Return project root path"""
    return project_root


@pytest.fixture
def sample_config():
    """Return sample configuration dictionary"""
    return {
        "log_level": "INFO",
        "debug": False,
        "use_cloud_llm": False,
        "cloud_llm_url": "https://example.com",
    }


@pytest.fixture
def sample_training_config():
    """Return sample training configuration"""
    return {
        "model_name": "test-model",
        "dataset_path": "data/test_dataset.json",
        "output_dir": "output/test",
        "training_config": {
            "num_epochs": 1,
            "batch_size": 4,
            "learning_rate": 0.0001
        }
    }


@pytest.fixture
def temp_dir(tmp_path):
    """Return temporary directory for tests"""
    return tmp_path


@pytest.fixture
def mock_output(monkeypatch):
    """Mock CLI output for testing"""
    from cli.utils import CLIOutput
    output = CLIOutput(json_output=True)
    return output


@pytest.fixture
def mock_unified_orchestrator():
    """Mock unified orchestrator for testing"""
    from unittest.mock import MagicMock
    mock_orch = MagicMock()
    mock_orch.ai_available = True
    mock_orch.stt_available = True
    mock_orch.tts_available = True
    mock_orch.process_text_command.return_value = {
        'success': True,
        'response': 'Done',
        'actions': [],
        'execution_results': []
    }
    return mock_orch


@pytest.fixture
def mock_stt():
    """Mock speech-to-text for testing"""
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.is_available.return_value = True
    mock.listen.return_value = "Test voice input"
    return mock


@pytest.fixture
def mock_tts():
    """Mock text-to-speech for testing"""
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.is_available = True
    mock.speak.return_value = True
    return mock

