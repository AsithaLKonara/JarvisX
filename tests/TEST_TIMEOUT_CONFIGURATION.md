# Test Timeout Configuration

## Overview

All CLI tests now have timeout protection to prevent tests from hanging indefinitely. This ensures tests complete in a reasonable time and fail fast if they get stuck.

## Configuration

### Global Timeout Settings

**File:** `pyproject.toml`

```toml
[tool.pytest.ini_options]
timeout = 10  # Default timeout: 10 seconds
timeout_method = "thread"  # Use thread-based timeout
```

### Per-File Timeouts

Different test files have different timeout requirements:

- **test_cli_main.py**: 5 seconds (module-level: `pytestmark = pytest.mark.timeout(5)`)
- **test_cli_common_options.py**: 5 seconds (module-level)
- **test_cli_unified.py**: 5 seconds (module-level + per-test)
- **test_cli_voice.py**: 10 seconds (voice operations may take longer)
- **integration/test_e2e_*.py**: 15 seconds (E2E tests may take longer)

### Per-Test Timeouts

Individual tests can override the default timeout:

```python
@pytest.mark.timeout(5)
def test_specific_function():
    # This test will timeout after 5 seconds
    pass
```

## Why Tests Might Hang

### Common Causes

1. **Voice Input Waiting**: Tests that try to listen for actual voice input
   - **Solution**: Mock `SpeechRecognizer.listen()` to return immediately

2. **Network Requests**: Tests waiting for network responses
   - **Solution**: Mock network requests using `@patch('requests.get')` or similar

3. **File I/O Operations**: Tests waiting for file operations
   - **Solution**: Mock file operations or use temporary directories

4. **Missing Mocks**: Tests calling real functions instead of mocks
   - **Solution**: Ensure all external dependencies are properly mocked

5. **Infinite Loops**: Tests stuck in loops
   - **Solution**: Add timeout protection and ensure loops have exit conditions

## Timeout Behavior

- **Default**: 10 seconds per test
- **Voice Tests**: 10 seconds (may need actual voice input)
- **E2E Tests**: 15 seconds (complete workflows)
- **Unit Tests**: 5 seconds (fast, isolated tests)

## Running Tests with Timeout

```bash
# Run with default timeout (10s)
pytest tests/ -v

# Override timeout for specific run
pytest tests/ --timeout=5

# Disable timeout (not recommended)
pytest tests/ --timeout=0

# Run with verbose timeout info
pytest tests/ -v --timeout=5 --tb=short
```

## Timeout Error Messages

When a test times out, you'll see:

```
FAILED tests/test_cli_voice.py::TestVoiceCLI::test_listen_voice - TimeoutError: Test exceeded 10.0s timeout
```

## Best Practices

1. **Mock External Dependencies**: Always mock voice I/O, network, and file operations
2. **Use Appropriate Timeouts**: Don't set timeouts too low for legitimate slow operations
3. **Test Isolation**: Ensure tests don't depend on external resources
4. **Fast Feedback**: Keep unit tests under 5 seconds
5. **E2E Tests**: Allow more time (15s) for complete workflows

## Files with Timeout Configuration

- `pyproject.toml` - Global timeout settings
- `tests/test_cli_main.py` - 5s timeout
- `tests/test_cli_common_options.py` - 5s timeout
- `tests/test_cli_unified.py` - 5s timeout (module + per-test)
- `tests/test_cli_voice.py` - 10s timeout
- `tests/integration/test_e2e_*.py` - 15s timeout

## Troubleshooting

### Test Still Hanging

1. Check if mocks are properly applied
2. Verify no actual I/O operations are being called
3. Check for infinite loops in test code
4. Increase timeout if operation is legitimately slow
5. Use `--timeout=0` temporarily to see where it hangs

### Timeout Too Short

If legitimate tests are timing out:
1. Increase timeout for that specific test: `@pytest.mark.timeout(30)`
2. Mark as slow test: `@pytest.mark.slow`
3. Review if test is doing unnecessary work

### Timeout Not Working

1. Verify `pytest-timeout` is installed: `pip install pytest-timeout`
2. Check `pyproject.toml` has timeout configuration
3. Ensure `timeout_method = "thread"` is set

