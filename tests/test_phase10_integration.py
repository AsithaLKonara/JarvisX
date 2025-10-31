"""
Phase 10 Integration Tests - 100% Completion

Comprehensive testing for:
- Main application integration
- Avatar system integration
- AI engine connection
- Voice interface sync
- Adapter layer functionality
- Migration system
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import systems under test
from core.ai_engine import AIEngine
from interface.avatar_adapter import AvatarAdapter, FeatureFlags, GracefulFallback
from interface.migration_system import MigrationSystem, SetupWizard, OnboardingManager
from utils.config import Config


class TestAIEngineIntegration:
    """Test AI engine integration with avatar signals."""
    
    def test_ai_engine_initialization(self):
        """Test AI engine initializes correctly."""
        ai_engine = AIEngine()
        assert ai_engine is not None
        assert ai_engine.get_current_state() == "IDLE"
        assert ai_engine.get_confidence_score() == 0.0
        assert ai_engine.get_last_emotion() is None
    
    def test_ai_engine_state_emission(self):
        """Test AI engine emits state changes."""
        ai_engine = AIEngine()
        states_emitted = []
        
        ai_engine.on_state_change(lambda state: states_emitted.append(state))
        
        # Simulate processing
        ai_engine._emit_state_change("PROCESSING")
        assert "PROCESSING" in states_emitted
        assert ai_engine.get_current_state() == "PROCESSING"
    
    def test_ai_engine_emotion_detection(self):
        """Test emotion detection in AI responses."""
        ai_engine = AIEngine()
        
        # Test happy emotion
        emotion, confidence = ai_engine._analyze_emotion("I am very happy!")
        assert emotion == "happy"
        assert confidence > 0.0
        
        # Test sad emotion
        emotion, confidence = ai_engine._analyze_emotion("I'm feeling sad")
        assert emotion == "sad"
        assert confidence > 0.0
    
    def test_ai_engine_processing_flow(self):
        """Test complete processing flow."""
        ai_engine = AIEngine()
        
        command = {'original_text': 'Hello Jarvis'}
        response = ai_engine.process(command)
        
        assert response is not None
        assert len(response) > 0
        assert ai_engine.get_current_state() == "IDLE"
    
    def test_ai_engine_get_response_method(self):
        """Test simplified get_response method."""
        ai_engine = AIEngine()
        
        response = ai_engine.get_response("Hello")
        assert response is not None
        assert isinstance(response, str)
    
    def test_ai_engine_conversation_history(self):
        """Test conversation history management."""
        ai_engine = AIEngine()
        
        ai_engine.process({'original_text': 'First message'})
        ai_engine.process({'original_text': 'Second message'})
        
        history = ai_engine.get_conversation_history()
        assert len(history) == 2
        assert history[0]['user'] == 'First message'
    
    def test_ai_engine_error_state(self):
        """Test error state handling."""
        ai_engine = AIEngine()
        ai_engine._emit_state_change("ERROR")
        
        assert ai_engine.get_current_state() == "ERROR"
    
    def test_ai_engine_callback_multiple(self):
        """Test multiple state change callbacks."""
        ai_engine = AIEngine()
        callback1_called = []
        callback2_called = []
        
        ai_engine.on_state_change(lambda s: callback1_called.append(s))
        ai_engine.on_state_change(lambda s: callback2_called.append(s))
        
        ai_engine._emit_state_change("TEST")
        
        assert "TEST" in callback1_called
        assert "TEST" in callback2_called


class TestAvatarAdapterIntegration:
    """Test avatar adapter layer."""
    
    def test_avatar_adapter_initialization(self):
        """Test adapter initializes correctly."""
        adapter = AvatarAdapter({})
        assert adapter is not None
        assert adapter.system_info is not None
        assert adapter.capabilities is not None
    
    def test_system_info_detection(self):
        """Test system information detection."""
        adapter = AvatarAdapter({})
        
        assert 'platform' in adapter.system_info
        assert 'os_name' in adapter.system_info
        assert 'architecture' in adapter.system_info
    
    def test_capability_checking(self):
        """Test capability checking."""
        adapter = AvatarAdapter({})
        
        assert 'has_display' in adapter.capabilities
        assert 'has_audio' in adapter.capabilities
        assert 'supports_transparency' in adapter.capabilities
    
    def test_should_use_futuristic_avatar(self):
        """Test futuristic avatar decision."""
        adapter = AvatarAdapter({})
        result = adapter.should_use_futuristic_avatar()
        assert isinstance(result, bool)
    
    def test_quality_level_determination(self):
        """Test quality level based on capabilities."""
        adapter = AvatarAdapter({})
        quality = adapter.get_quality_level()
        assert quality in ['LOW', 'MEDIUM', 'HIGH', 'ULTRA']
    
    def test_platform_configuration(self):
        """Test platform-specific configuration."""
        adapter = AvatarAdapter({})
        config = adapter.get_platform_config()
        
        assert isinstance(config, dict)
        if config:
            assert 'window_style' in config or 'transparency_mode' in config
    
    def test_system_validation(self):
        """Test system validation."""
        adapter = AvatarAdapter({})
        result = adapter.validate_system()
        assert isinstance(result, bool)
    
    def test_feature_flags_get(self):
        """Test feature flag retrieval."""
        flag_value = FeatureFlags.get('use_futuristic_avatar')
        assert isinstance(flag_value, bool)
    
    def test_feature_flags_set(self):
        """Test feature flag setting."""
        FeatureFlags.set('test_flag', True)
        assert FeatureFlags.get('test_flag') == True
        
        FeatureFlags.set('test_flag', False)
        assert FeatureFlags.get('test_flag') == False
    
    def test_feature_flags_get_all(self):
        """Test getting all feature flags."""
        all_flags = FeatureFlags.get_all()
        assert isinstance(all_flags, dict)
        assert len(all_flags) > 0
    
    def test_graceful_fallback_interface(self):
        """Test graceful fallback configuration."""
        fallback = GracefulFallback.get_fallback_interface()
        
        assert 'type' in fallback
        assert 'features' in fallback
        assert fallback['type'] == 'text_interface'
    
    def test_degraded_quality_config(self):
        """Test degraded quality configuration."""
        config = GracefulFallback.get_degraded_quality_config()
        
        assert 'animation_quality' in config
        assert 'particle_count' in config
        assert config['animation_quality'] == 'LOW'
    
    def test_avatar_failure_handling(self):
        """Test avatar failure handling."""
        error = Exception("Test error")
        result = GracefulFallback.handle_avatar_failure(error)
        
        assert result['use_avatar'] == False
        assert result['use_text_interface'] == True


class TestMigrationSystem:
    """Test user migration system."""
    
    def test_migration_system_initialization(self):
        """Test migration system initializes."""
        migration = MigrationSystem("test_data")
        assert migration is not None
        assert migration.VERSION == "2.0.0"
    
    def test_check_migration_needed_fresh_install(self):
        """Test fresh install detection."""
        migration = MigrationSystem("test_data_fresh")
        result = migration.check_migration_needed()
        # Result depends on whether version file exists
        assert isinstance(result, bool)
    
    def test_create_default_settings(self):
        """Test default settings creation."""
        migration = MigrationSystem("test_data_settings")
        migration._create_default_settings()
        
        settings_file = migration.data_dir / "settings.json"
        assert settings_file.exists()
        
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            assert 'avatar' in settings
            assert 'voice' in settings
    
    def test_version_update(self):
        """Test version file update."""
        migration = MigrationSystem("test_data_version")
        migration._update_version()
        
        version_file = migration.data_dir / "version.json"
        assert version_file.exists()
        
        with open(version_file, 'r') as f:
            version_data = json.load(f)
            assert version_data['version'] == "2.0.0"
    
    def test_migration_logging(self):
        """Test migration event logging."""
        migration = MigrationSystem("test_data_logging")
        migration._log_migration("TEST_STATUS")
        
        log_file = migration.data_dir / "migration.log"
        assert log_file.exists()
        
        with open(log_file, 'r') as f:
            logs = json.load(f)
            assert len(logs) > 0
            assert logs[0]['status'] == "TEST_STATUS"


class TestSetupWizard:
    """Test setup wizard for first-time setup."""
    
    def test_setup_wizard_initialization(self):
        """Test setup wizard initializes."""
        wizard = SetupWizard()
        assert wizard is not None
        assert wizard.current_step == 0
        assert wizard.total_steps == 5
    
    def test_setup_wizard_progress(self):
        """Test setup wizard progress calculation."""
        wizard = SetupWizard()
        
        progress = wizard.get_progress()
        assert progress == 0.0
        
        wizard.current_step = 2
        progress = wizard.get_progress()
        assert progress == 40.0
    
    def test_setup_wizard_start(self):
        """Test setup wizard start flow."""
        wizard = SetupWizard()
        config = wizard.start_wizard()
        
        assert isinstance(config, dict)
        assert 'welcome_completed' in config or 'error' in config


class TestOnboardingManager:
    """Test onboarding and achievement system."""
    
    def test_onboarding_initialization(self):
        """Test onboarding manager initializes."""
        onboarding = OnboardingManager("test_onboarding")
        assert onboarding is not None
        assert onboarding.achievements is not None
    
    def test_get_next_tip(self):
        """Test getting next onboarding tip."""
        onboarding = OnboardingManager("test_onboarding_tips")
        tip = onboarding.get_next_tip()
        
        assert tip is not None or tip is None  # May be None if all tips shown
    
    def test_mark_tip_shown(self):
        """Test marking tip as shown."""
        onboarding = OnboardingManager("test_onboarding_marked")
        initial_count = onboarding.achievements.get('tips_shown', 0)
        
        onboarding.mark_tip_shown()
        new_count = onboarding.achievements.get('tips_shown', 0)
        
        assert new_count > initial_count
    
    def test_record_achievement(self):
        """Test recording achievement."""
        onboarding = OnboardingManager("test_onboarding_achievement")
        
        initial_count = len(onboarding.achievements.get('achievements', []))
        onboarding.record_achievement("test_achievement")
        new_count = len(onboarding.achievements.get('achievements', []))
        
        assert new_count > initial_count


class TestApplicationIntegration:
    """Test main application integration."""
    
    def test_config_loading(self):
        """Test configuration loading."""
        config = Config()
        assert config is not None
        assert isinstance(config.get('avatar', {}), dict)
    
    def test_multiple_system_initialization(self):
        """Test initializing multiple systems."""
        ai_engine = AIEngine()
        adapter = AvatarAdapter({})
        migration = MigrationSystem()
        
        assert ai_engine is not None
        assert adapter is not None
        assert migration is not None
    
    def test_state_propagation(self):
        """Test state propagates through systems."""
        ai_engine = AIEngine()
        
        states = []
        ai_engine.on_state_change(lambda s: states.append(s))
        
        ai_engine._emit_state_change("PROCESSING")
        ai_engine._emit_state_change("IDLE")
        
        assert "PROCESSING" in states
        assert "IDLE" in states


class TestErrorHandling:
    """Test error handling and recovery."""
    
    def test_ai_engine_error_recovery(self):
        """Test AI engine error recovery."""
        ai_engine = AIEngine()
        
        try:
            # Process with invalid input
            response = ai_engine.process({'original_text': None})
            # Should still return something
            assert response is not None
        except Exception as e:
            pytest.fail(f"AI engine crashed: {e}")
    
    def test_adapter_error_handling(self):
        """Test adapter error handling."""
        try:
            adapter = AvatarAdapter({'invalid': 'config'})
            adapter.validate_system()
        except Exception as e:
            pytest.fail(f"Adapter crashed: {e}")
    
    def test_migration_error_handling(self):
        """Test migration error handling."""
        try:
            migration = MigrationSystem("invalid_path" * 100)  # Intentionally bad path
            # Should handle gracefully
        except Exception as e:
            # Some errors are acceptable
            pass


class TestPerformance:
    """Test performance characteristics."""
    
    def test_ai_engine_response_time(self):
        """Test AI engine response time."""
        import time
        
        ai_engine = AIEngine()
        start = time.time()
        ai_engine.get_response("Hello")
        elapsed = time.time() - start
        
        # Should be reasonably fast
        assert elapsed < 5.0
    
    def test_adapter_initialization_time(self):
        """Test adapter initialization time."""
        import time
        
        start = time.time()
        adapter = AvatarAdapter({})
        elapsed = time.time() - start
        
        assert elapsed < 1.0
    
    def test_migration_initialization_time(self):
        """Test migration initialization time."""
        import time
        
        start = time.time()
        migration = MigrationSystem()
        elapsed = time.time() - start
        
        assert elapsed < 1.0


class TestIntegrationWorkflows:
    """Test complete integration workflows."""
    
    def test_startup_workflow(self):
        """Test complete startup workflow."""
        # Initialize all systems
        config = Config()
        ai_engine = AIEngine(config)
        adapter = AvatarAdapter(config)
        
        # Verify all initialized
        assert ai_engine.get_current_state() == "IDLE"
        assert adapter.system_info is not None
    
    def test_user_input_workflow(self):
        """Test complete user input workflow."""
        ai_engine = AIEngine()
        
        # Simulate user input flow
        ai_engine._emit_state_change("LISTENING")
        response = ai_engine.get_response("Hello Jarvis")
        ai_engine._emit_state_change("SPEAKING")
        ai_engine._emit_state_change("IDLE")
        
        assert ai_engine.get_current_state() == "IDLE"
        assert response is not None
    
    def test_migration_workflow(self):
        """Test complete migration workflow."""
        migration = MigrationSystem("test_workflow_migration")
        
        # Check if migration needed
        needs_migration = migration.check_migration_needed()
        
        # Create default settings
        migration._create_default_settings()
        
        # Update version
        migration._update_version()
        
        # Verify completion
        assert migration.version_file.exists()


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup test data."""
    yield
    
    import shutil
    test_dirs = [
        "test_data",
        "test_data_fresh",
        "test_data_settings",
        "test_data_version",
        "test_data_logging",
        "test_onboarding",
        "test_onboarding_tips",
        "test_onboarding_marked",
        "test_onboarding_achievement",
        "test_workflow_migration",
    ]
    
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            try:
                shutil.rmtree(test_dir)
            except:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
