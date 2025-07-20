"""
Test data utilities for structur tests
Provides helper functions to create test files and content.
"""

import os
import tempfile
import shutil


def create_test_file(file_path, content):
    """Create a test file with the given content."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path


def create_test_files(base_dir, files_dict):
    """Create multiple test files from a dictionary of {filename: content}."""
    created_files = []
    for filename, content in files_dict.items():
        file_path = os.path.join(base_dir, filename)
        create_test_file(file_path, content)
        created_files.append(file_path)
    return created_files


def create_sample_markdown_content():
    """Create sample markdown content with various code formats."""
    return """# Sample Document

This is a sample document with various code formats.

## Multiline Code Format

{{workflow}}==This is about how I organize my daily workflow and processes=={{workflow}}

{{productivity}}==This is about productivity tips and techniques=={{productivity}}

{{writing}}==This is about writing processes and techniques=={{writing}}

## Single Line Code Format

==This is about workflow organization=={{workflow}}

==This is about productivity methods=={{productivity}}

==This is about writing strategies=={{writing}}

## Bracket Format

[[ideas]]==This is about creative ideas and brainstorming==[[ideas]]

==This is about writing ideas==[[writing]]

## Theme Codes

{{theme}}==This is about design themes=={{theme}}

==This is about color themes=={{theme}}
"""


def create_sample_codes_file():
    """Create sample codes.txt content."""
    return """# Master codes list
workflow
productivity
writing
ideas
theme
# Additional codes
research
planning
"""


def create_test_directory_structure(base_dir):
    """Create a test directory structure with various file types."""
    structure = {
        "docs/": {
            "readme.md": "{{workflow}}==Documentation workflow=={{workflow}}",
            "guide.txt": "{{productivity}}==Productivity guide=={{productivity}}",
            "config.py": "# This should be ignored",
        },
        "notes/": {
            "daily.md": "{{writing}}==Daily writing notes=={{writing}}",
            "ideas.txt": "{{ideas}}==Creative ideas=={{ideas}}",
        },
        "ignore/": {
            "temp.py": "{{ignore}}==This should be ignored=={{ignore}}",
        }
    }
    
    created_files = []
    for dir_name, files in structure.items():
        dir_path = os.path.join(base_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        
        for filename, content in files.items():
            file_path = os.path.join(dir_path, filename)
            create_test_file(file_path, content)
            created_files.append(file_path)
    
    return created_files


class TestDataManager:
    """Context manager for creating and cleaning up test data."""
    
    def __init__(self):
        self.temp_dir = None
        self.created_files = []
    
    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_file(self, filename, content):
        """Create a file in the temp directory."""
        file_path = os.path.join(self.temp_dir, filename)
        create_test_file(file_path, content)
        self.created_files.append(file_path)
        return file_path
    
    def create_files(self, files_dict):
        """Create multiple files in the temp directory."""
        return create_test_files(self.temp_dir, files_dict)
    
    def get_path(self, filename):
        """Get the full path for a filename in the temp directory."""
        return os.path.join(self.temp_dir, filename)
    
    def create_output_dir(self):
        """Create an output directory for testing."""
        output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir 