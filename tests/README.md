# Structur Tests

This directory contains comprehensive unit tests for the `structur.py` script.

## Test Structure

- `test_structur.py` - Main test suite with all unit tests
- `test_data.py` - Test data utilities and helper functions
- `run_tests.py` - Test runner script
- `README.md` - This file

## Running Tests

### Option 1: Using the test runner script
```bash
python tests/run_tests.py
```

### Option 2: Using unittest directly
```bash
python -m unittest tests.test_structur -v
```

### Option 3: Using pytest (if installed)
```bash
pytest tests/ -v
```

## Test Coverage

The test suite covers all major functions in `structur.py`:

### Core Functions
- `read_codes_from_file()` - Reading codes from files
- `regenerate_empty_code_files()` - Creating empty code files
- `process_file()` - Processing individual files
- `write_code_files()` - Writing extracted codes to files
- `process_folder()` - Processing entire folders
- `main()` - Main CLI function

### Test Scenarios
- File processing with different code formats (`{{ }}` and `[[ ]]`)
- Multiline and single-line code extraction
- Code filtering functionality
- Duplicate handling
- Source link generation
- Output folder naming and sanitization
- Extension filtering
- Codes file integration
- Error handling for non-existent files/folders

## Test Data

The tests use temporary files and directories that are automatically cleaned up after each test. Test data includes:

- Sample markdown files with various code formats
- Codes.txt files with different content
- Directory structures with multiple file types
- Edge cases (empty files, files with only comments, etc.)

## Adding New Tests

To add new tests:

1. Add test methods to the `TestStructurFunctions` class in `test_structur.py`
2. Follow the naming convention: `test_function_name_scenario()`
3. Use the `setUp()` and `tearDown()` methods for test fixtures
4. Use the `TestDataManager` context manager for complex test data setup

## Test Utilities

The `test_data.py` module provides utilities for:

- Creating test files with specific content
- Generating sample markdown content
- Creating directory structures
- Managing temporary test data

## Continuous Integration

These tests can be easily integrated into CI/CD pipelines. The test runner exits with appropriate exit codes:

- Exit code 0: All tests passed
- Exit code 1: Some tests failed 