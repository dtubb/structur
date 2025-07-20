# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and it adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1.dev2] - 2025-07-20

### Added
- **Codes.txt Management**: Complete implementation of codes.txt functionality for managing master codes lists
  - `--codes-file` option to read from existing codes.txt files
  - `--auto-codes-file` option to automatically create/update codes.txt with extracted codes
  - `--regenerate-codes` option to create empty files for all codes in codes.txt
  - Automatic duplicate prevention when appending to codes.txt
- **Recursive Folder Processing**: Enhanced to process deeply nested folder structures
  - Processes all `.md` files in subdirectories at any depth
  - Maintains folder structure awareness
- **Alphanumeric File Sorting**: Implemented natural sorting (like Finder) for consistent file processing order
  - Files processed in alphanumeric order: `1.md`, `2.md`, `10.md`, `a.md`, `z.md`
  - Consistent and repeatable processing order
- **Comprehensive Unit Tests**: Added extensive test coverage for new features
  - 23 new tests for codes.txt functionality
  - 7 new tests for recursive folder processing and sorting
  - 13 new tests for square bracket format comprehensive coverage
  - Tests for mixed file types, special characters, deep nesting
  - Total test count: 122 tests
- **Processing Report Enhancements**: Added percentage calculations in processing reports
  - Shows percentage of each output folder relative to originals
  - Displays total percentage to verify completeness
- **Shell Script Improvements**: Enhanced `structur.sh` for better codes.txt integration
  - Automatically detects and uses existing codes.txt files
  - Provides feedback on codes.txt usage
- **Project Cleanup**: Removed test cruft and organized project structure
  - Moved test files to `tests/test_data/`
  - Created `examples/` folder with sample files and documentation
  - Removed macOS packaging (preparing for future GUI development)
- **Programmatic Function Interface**: Added `process_structur()` function for calling structur from other Python scripts
- **Logging System**: Replaced all print statements with proper Python logging
- **Verbose Control**: Added `verbose` parameter to control output verbosity (True/False)
- **Return Value Structure**: Function now returns detailed dictionary with operation results
- **Silent Mode**: Ability to run structur with minimal output for integration scenarios
- **Version Management**: Added `__version__` variable and `version` command for CLI
- **Changelog**: Added comprehensive CHANGELOG.md following Keep a Changelog format
- **Project Configuration**: Added comprehensive `.gitignore` file for Python projects
- **Duplicate Text Extraction**: Added `--duplicate-folder` option to extract duplicate text instances to separate files
- **Word Count Reporting**: Added comprehensive word count statistics showing original, coded, uncoded, and duplicate word counts with difference analysis

### Changed
- **Unified Code Format**: Simplified to single format `{{code}}==text=={{code}}` and `[[code]]==text==[[code]]` for both single line and multiline text
- **Removed Old Format**: Eliminated the old `==text=={{code}}` and `==text==[[code]]` formats to prevent confusion and overlap issues
- **File Operations**: Updated `get_markdown_files()` to use natural sorting
- **Configuration**: Enhanced `ProcessingConfig` with codes.txt options
- **Workflow Manager**: Added codes.txt management and percentage reporting
- **Project Structure**: Cleaner, more organized directory layout
- **Documentation**: Updated README with examples folder and usage instructions
- **Function Signatures**: Updated all internal functions to accept optional logger parameter
- **Output Control**: Verbose mode now properly controls all output levels
- **Error Handling**: Improved error messages with proper logging levels
- **Test Coverage**: Enhanced test suite to cover both CLI and programmatic usage patterns
- **Shell Script Behavior**: `structur.sh` now automatically creates and updates codes.txt files in the same directory as input files
- **Environment Management**: Migrated from conda to Python virtual environments (`.venv`) for better portability

### Fixed
- **Codes.txt Path Resolution**: Fixed issue where codes.txt was written to wrong location
- **Indentation Errors**: Fixed Python syntax errors in structur.py
- **Test Coverage**: All 109 tests now passing with comprehensive coverage
- **Duplicate Detection**: Resolved issues with false duplicate detection caused by overlapping regex patterns
- **Pattern Overlap**: Eliminated the problem where the same text was being matched by both multiline and single line patterns
- **Regenerate Codes Logic**: Fixed bug where regenerate_codes only worked with verbose=True
- **Logger State Management**: Fixed logger persistence issues between function calls
- **Test Output Capture**: Fixed test capture to properly handle both stdout and stderr
- **Function Return Values**: Ensured consistent return value structure across all usage patterns
- **Duplicate Text Detection**: Fixed issue where same text content was being appended multiple times to existing files
- **Content Parsing**: Fixed parsing logic to properly handle both markdown headers (with `--link-to-source`) and plain text content

### Technical Details
- **Dependencies**: No new dependencies added
- **Backward Compatibility**: Breaking change - old `==text=={{code}}` and `==text==[[code]]` formats no longer supported
- **Performance**: Improved performance by eliminating duplicate pattern matching and improving file sorting
- **Code Quality**: Enhanced error handling and logging throughout
- **API Changes**: New `process_structur()` function added, existing functions enhanced with optional logger parameter

## [0.0.1.dev1] - 2024-10-13

### Added
- Initial CLI implementation with typer
- Support for {{code}} and [[code]] formats
- File and folder processing capabilities
- Code filtering and extension filtering
- Source linking functionality
- Basic test suite
- Documentation and examples