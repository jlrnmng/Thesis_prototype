# Tests Directory

This directory contains all test files for the Hirely application.

## Test Files

### Security & Session Tests
- `test_session_security.py` - Tests for session security and timeout functionality
- `test_cache_prevention.py` - Tests to ensure no-cache headers are properly set
- `test_multi_admin.py` - Tests for multi-admin functionality

### Feature Tests
- `test_profile.py` - Tests for user profile functionality
- `test_profile_functionality.py` - Extended profile feature tests
- `test_functionality.py` - General application functionality tests

### Preprocessing Tests
- `test_preprocessing_simple.py` - Simple demonstration of preprocessing features
- `test_preprocessing_demo.py` - Detailed preprocessing demonstration
- `test_improved_preprocessing.py` - Comparison of old vs. new preprocessing

## Running Tests

To run all tests:
```bash
python -m pytest tests/
```

To run a specific test:
```bash
python tests/test_profile.py
```

## Test Coverage

Tests cover:
- ✅ User authentication and session management
- ✅ Profile creation and updates
- ✅ Resume upload and processing
- ✅ Text preprocessing with stop word removal
- ✅ Security headers and cache prevention
- ✅ Multi-admin job management
