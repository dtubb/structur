# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and it adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1.dev3] - 2025-01-27

### Changed
- **Unified Code Format**: Simplified to single format `{{code}}==text=={{code}}` for both single line and multiline text
- **Removed Old Format**: Eliminated the old `==text=={{code}}` format to prevent confusion and overlap issues
- **Updated Documentation**: Updated README.md and example.md to reflect the new unified format
- **Simplified Logic**: Removed separate multiline and single line pattern matching, now uses unified pattern

### Fixed
- **Duplicate Detection**: Resolved issues with false duplicate detection caused by overlapping regex patterns
- **Pattern Overlap**: Eliminated the problem where the same text was being matched by both multiline and single line patterns

### Technical Details
- **Regex Patterns**: Simplified to single pattern per format ({{}} and [[]])
- **Backward Compatibility**: Breaking change - old `==text=={{code}}` format no longer supported
- **Performance**: Improved performance by eliminating duplicate pattern matching

## [0.0.1.dev2] - 2025-07-25

### Added
- **Programmatic Function Interface**: Added `process_structur()` function for calling structur from other Python scripts
- **Logging System**: Replaced all print statements with proper Python logging
- **Verbose Control**: Added `verbose` parameter to control output verbosity (True/False)
- **Return Value Structure**: Function now returns detailed dictionary with operation results
- **Silent Mode**: Ability to run structur with minimal output for integration scenarios
- **Enhanced Test Suite**: Added unit tests (59 total tests including 15 new tests for duplicate detection, uncoded text extraction, and duplicate text extraction).
- **Updated Documentation**: Added programmatic usage examples and logging system documentation
- **Version Management**: Added `__version__` variable and `version` command for CLI
- **Changelog**: Added comprehensive CHANGELOG.md following Keep a Changelog format
- **Auto Codes File**: Added `--auto-codes-file` option to automatically create/update codes.txt with extracted codes
- **Codes File Management**: Added `write_codes_to_file()` function for appending new codes to existing codes.txt files
- **Shell Script Integration**: Updated `structur.sh` to automatically use codes.txt functionality
- **Project Configuration**: Added comprehensive `.gitignore` file for Python projects

### Changed
- **Function Signatures**: Updated all internal functions to accept optional logger parameter
- **Output Control**: Verbose mode now properly controls all output levels
- **Error Handling**: Improved error messages with proper logging levels
- **Test Coverage**: Enhanced test suite to cover both CLI and programmatic usage patterns
- **Shell Script Behavior**: `structur.sh` now automatically creates and updates codes.txt files in the same directory as input files
- **Environment Management**: Migrated from conda to Python virtual environments (`.venv`) for better portability

### Fixed
- **Regenerate Codes Logic**: Fixed bug where regenerate_codes only worked with verbose=True
- **Logger State Management**: Fixed logger persistence issues between function calls
- **Test Output Capture**: Fixed test capture to properly handle both stdout and stderr
- **Function Return Values**: Ensured consistent return value structure across all usage patterns
- **Duplicate Text Detection**: Fixed issue where same text content was being appended multiple times to existing files
- **Content Parsing**: Fixed parsing logic to properly handle both markdown headers (with `--link-to-source`) and plain text content
- **Shell Script Enhancement**: Updated `structur.sh` to automatically create uncoded folders with naming pattern `{input}_uncoded`
- **Documentation Updates**: Added comprehensive documentation for uncoded text feature in README and CLI help
- **Duplicate Text Extraction**: Added `--duplicate-folder` option to extract duplicate text instances to separate files, helping identify and analyze duplicate content
- **Word Count Reporting**: Added comprehensive word count statistics showing original, coded, uncoded, and duplicate word counts with difference analysis
- **Enhanced Shell Script**: Updated `structur.sh` to automatically create duplicate folders with naming pattern `{input}_duplicates`

### Technical Details
- **Dependencies**: No new dependencies added
- **Backward Compatibility**: CLI interface remains unchanged
- **API Changes**: New `process_structur()` function added, existing functions enhanced with optional logger parameter
- **Performance**: Improved output handling with structured logging

## [0.0.1.dev1] - 2024-10-13

### Added
- Initial CLI implementation with typer
- Support for {{code}} and [[code]] formats
- File and folder processing capabilities
- Code filtering and extension filtering
- Source linking functionality
- Basic test suite
- Documentation and examples