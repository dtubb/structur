# Structur New - Modular Text Processing System

A reliable, modular text processing system for extracting and organizing coded content from markdown files. This new version uses a removal-based approach to ensure no data loss and provides comprehensive error handling.

## 🌟 Key Features

- **Zero Data Loss**: Removal-based approach ensures original content is never lost
- **Modular Architecture**: Clean separation of concerns with focused, testable modules
- **Global Duplicate Detection**: Tracks duplicates across all files and codes
- **Comprehensive Error Handling**: Robust processing with detailed logging
- **Malformed Block Detection**: Identifies and handles improperly formatted codes
- **Append-Only Mode**: Safe incremental processing without overwriting
- **Multiple Output Folders**: Organized content separation (coded, uncoded, duplicates, malformed, already coded)
- **Code Preservation Option**: Keep code markers in final output if desired

## 📁 Project Structure

```
structur/
├── src/                          # Main source code
│   ├── models/                   # Data models and configuration
│   │   ├── config.py            # Processing configuration
│   │   └── text_block.py        # Text block data models
│   ├── utils/                    # Utility modules
│   │   ├── file_operations.py   # Safe file handling
│   │   ├── text_utils.py        # Text processing utilities
│   │   └── duplicate_detector.py # Duplicate detection system
│   ├── processors/               # Content processing modules
│   │   ├── code_extractor.py    # Code block extraction
│   │   ├── malformed_detector.py # Malformed block detection
│   │   ├── content_filter.py    # Content filtering and removal
│   │   └── main_processor.py    # Main processing orchestrator
│   └── managers/                 # Workflow and folder management
│       ├── folder_manager.py    # Folder structure management
│       └── workflow_manager.py  # Processing workflow coordination
├── tests/                        # Unit tests
├── structur_new.py              # CLI interface
├── requirements_new.txt         # Dependencies
└── README_new.md               # This file
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd structur
```

2. Install dependencies:
```bash
pip install -r requirements_new.txt
```

3. Make the script executable:
```bash
chmod +x structur_new.py
```

## 💡 Usage

### Basic Processing

Process all markdown files in a folder:
```bash
python structur_new.py process input_folder output_folder
```

### Advanced Options

```bash
python structur_new.py process input_folder output_folder \
    --coded-folder "my_codes" \
    --preserve-codes \
    --verbose
```

### Single File Processing

Process a single markdown file:
```bash
python structur_new.py single file.md output_folder
```

### Show Statistics

View statistics for existing output folders:
```bash
python structur_new.py stats output_folder
```

## 🏗️ Architecture Overview

### Core Principles

1. **Removal-Based Processing**: Instead of extracting content, we remove unwanted content from copies
2. **Copy-First Approach**: Always work with copies of original files
3. **Global State Management**: Track duplicates across all files and processing sessions
4. **Modular Design**: Each module has a single, well-defined responsibility
5. **Fail-Safe Operations**: Extensive error handling and validation

### Processing Flow

1. **File Discovery**: Find all markdown files in input directory
2. **Original Backup**: Create copies in originals folder
3. **Content Analysis**: Extract coded blocks, detect malformed blocks
4. **Duplicate Detection**: Check against global duplicate registry
5. **Content Filtering**: Remove coded/malformed content for uncoded extraction
6. **Output Organization**: Write content to appropriate folders
7. **Statistics Generation**: Calculate and report processing statistics

### Output Folders

- `coded/`: Properly formatted coded content (organized by code name)
- `uncoded/`: Content with all codes and malformed blocks removed
- `duplicates/`: Duplicate content with source tracking
- `malformed/`: Improperly formatted code blocks
- `already_coded/`: Content that already exists in output folders
- `originals/`: Backup copies of original files

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific test modules:
```bash
python -m unittest tests.test_code_extractor
python -m unittest tests.test_duplicate_detector
```

## 📝 Code Format Support

The system supports both code formats:

### Double Brace Format
```markdown
{{code-name}}==Content goes here=={{code-name}}
```

### Double Bracket Format
```markdown
[[code-name]]==Content goes here==[[code-name]]
```

## 🔧 Configuration

The system uses the `ProcessingConfig` class for configuration:

```python
from src.models.config import ProcessingConfig
from src.processors.main_processor import StructurProcessor

config = ProcessingConfig(
    input_folder=Path("input"),
    output_base=Path("output"),
    preserve_codes_in_output=True,
    append_mode=True
)

processor = StructurProcessor(config)
```

## 📊 Error Handling

- **File Access Errors**: Graceful handling of permission and access issues
- **Malformed Content**: Detection and separate handling of invalid code blocks
- **Duplicate Content**: Global tracking prevents data duplication
- **Memory Management**: Efficient processing of large files
- **Logging**: Comprehensive logging with configurable levels

## 🆚 Differences from Original

| Feature | Original | New Modular Version |
|---------|----------|-------------------|
| Architecture | Monolithic | Modular, multi-file |
| Data Safety | Risk of loss | Zero data loss guaranteed |
| Duplicate Detection | Per-code only | Global across all content |
| Error Handling | Basic | Comprehensive with logging |
| Testing | Limited | Extensive unit tests |
| Malformed Detection | Basic regex | Advanced pattern recognition |
| Code Organization | Single file | Multiple focused modules |
| Extensibility | Difficult | Easy to extend |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Write tests for new functionality
4. Ensure all tests pass: `python -m pytest`
5. Submit a pull request

## 📜 License

[Include your license information here]

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root directory
2. **Permission Errors**: Check file/folder permissions for input and output directories
3. **Memory Issues**: For very large files, consider processing in smaller batches
4. **Encoding Issues**: All files are processed as UTF-8

### Debug Mode

Enable verbose logging for troubleshooting:
```bash
python structur_new.py process input_folder output_folder --verbose
```

Check the processing log:
```bash
tail -f output_folder/structur_processing.log
```

## 📈 Performance

The new modular system provides:
- **Faster Processing**: Optimized algorithms and reduced redundancy
- **Memory Efficiency**: Streaming processing for large files  
- **Scalability**: Modular architecture supports easy optimization
- **Reliability**: Comprehensive error handling prevents crashes

## 🔮 Future Enhancements

- [ ] Parallel processing for multiple files
- [ ] Plugin system for custom processors
- [ ] Web interface for easier usage
- [ ] Integration with version control systems
- [ ] Advanced statistics and reporting
- [ ] Export to various formats (JSON, XML, etc.) 