# 🧪 JarvisX V2 Test Suite

Comprehensive test suite for JarvisX V2 covering unit tests, integration tests, and end-to-end tests.

## 📋 Test Structure

```
tests/
├── README.md (this file)
├── conftest.py - Pytest configuration and fixtures
├── test_cli_validation.py - CLI input validation tests
├── test_cli_integration.py - CLI integration tests
├── test_core_modules.py - Core module tests
├── test_cli_training.py - Training CLI tests
├── test_cli_cloud.py - Cloud CLI tests
├── test_cli_system.py - System CLI tests
├── test_cli_business.py - Business CLI tests
├── test_cli_model.py - Model CLI tests
├── test_cli_workflow.py - Workflow CLI tests
├── test_cli_voice.py - Voice CLI tests
├── test_cli_config.py - Config CLI tests
├── test_cli_history.py - History CLI tests
└── integration/
    └── test_end_to_end.py - End-to-end tests
```

## 🚀 Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_cli_validation.py
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run Specific Test Class
```bash
pytest tests/test_cli_validation.py::TestPathValidation
```

### Run Specific Test Function
```bash
pytest tests/test_cli_validation.py::TestPathValidation::test_valid_path
```

## 📝 Test Categories

### Unit Tests
- **test_cli_validation.py** - Input validation functions
- **test_core_modules.py** - Core module functionality
- **test_cli_*.py** - Individual CLI command tests

### Integration Tests
- **test_cli_integration.py** - CLI workflow integration
- **integration/test_end_to_end.py** - End-to-end workflows

## 🎯 Test Coverage Goals

- **Unit Tests:** 80%+ coverage
- **Integration Tests:** All major workflows
- **E2E Tests:** Critical user paths

## 📊 Current Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| CLI Validation | 100% | ✅ |
| CLI Integration | 60% | ⏳ |
| Core Modules | 40% | ⏳ |
| CLI Commands | 50% | ⏳ |

## 🔧 Test Fixtures

### Available Fixtures (in conftest.py)
- `project_root_path` - Project root directory
- `sample_config` - Sample configuration
- `sample_training_config` - Sample training config
- `temp_dir` - Temporary directory
- `mock_output` - Mock CLI output

## 📝 Writing Tests

### Example Test
```python
def test_validation_function():
    """Test validation function"""
    from cli.utils import validate_url
    assert validate_url("https://example.com") is True
    assert validate_url("not-a-url") is False
```

### Using Fixtures
```python
def test_with_fixture(temp_dir, sample_config):
    """Test using fixtures"""
    assert temp_dir.exists()
    assert sample_config is not None
```

## 🐛 Debugging Tests

### Run with Debugger
```bash
pytest tests/ --pdb
```

### Run with Print Statements
```bash
pytest tests/ -s
```

### Run with Logging
```bash
pytest tests/ --log-cli-level=DEBUG
```

## ✅ Test Checklist

- [x] Input validation tests
- [x] CLI integration tests
- [x] Core module tests
- [ ] All CLI command tests
- [ ] End-to-end tests
- [ ] Performance tests
- [ ] Error handling tests

## 📚 Test Documentation

- **Unit Tests:** Test individual functions and classes
- **Integration Tests:** Test component interactions
- **E2E Tests:** Test complete user workflows

## 🤝 Contributing Tests

When adding new tests:
1. Follow existing test structure
2. Use descriptive test names
3. Add docstrings to test functions
4. Use fixtures when appropriate
5. Aim for high coverage

---

**Last Updated:** 2025-01-XX  
**Test Framework:** pytest  
**Coverage Tool:** pytest-cov

