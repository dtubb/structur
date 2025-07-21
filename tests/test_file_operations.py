"""Unit tests for file operations."""

import unittest
import tempfile
import shutil
from pathlib import Path
from src.utils.file_operations import FileManager


class TestFileOperations(unittest.TestCase):
    """Test file operations functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.file_manager = FileManager()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_read_codes_from_file(self):
        """Test reading codes from a codes.txt file."""
        # Create a test codes.txt file
        codes_content = """# Master codes list
workflow
productivity
writing
# This is a comment
ideas
"""
        codes_file = self.test_dir / "codes.txt"
        codes_file.write_text(codes_content)
        
        # Read codes
        codes = self.file_manager.read_codes_from_file(codes_file)
        
        # Should only read non-comment, non-empty lines
        expected_codes = ["workflow", "productivity", "writing", "ideas"]
        self.assertEqual(codes, expected_codes)
    
    def test_read_codes_from_nonexistent_file(self):
        """Test reading codes from a file that doesn't exist."""
        codes_file = self.test_dir / "nonexistent.txt"
        
        codes = self.file_manager.read_codes_from_file(codes_file)
        
        # Should return empty list
        self.assertEqual(codes, [])
    
    def test_read_codes_from_empty_file(self):
        """Test reading codes from an empty file."""
        codes_file = self.test_dir / "empty.txt"
        codes_file.write_text("")
        
        codes = self.file_manager.read_codes_from_file(codes_file)
        
        # Should return empty list
        self.assertEqual(codes, [])
    
    def test_read_codes_with_only_comments(self):
        """Test reading codes from a file with only comments."""
        codes_content = """# This is a comment
# Another comment
# Yet another comment
"""
        codes_file = self.test_dir / "comments.txt"
        codes_file.write_text(codes_content)
        
        codes = self.file_manager.read_codes_from_file(codes_file)
        
        # Should return empty list
        self.assertEqual(codes, [])
    
    def test_write_codes_to_file_new(self):
        """Test writing codes to a new file."""
        codes_file = self.test_dir / "new_codes.txt"
        codes = ["workflow", "productivity", "writing"]
        
        success = self.file_manager.write_codes_to_file(codes_file, codes, append=False)
        
        self.assertTrue(success)
        self.assertTrue(codes_file.exists())
        
        content = codes_file.read_text()
        self.assertIn("workflow", content)
        self.assertIn("productivity", content)
        self.assertIn("writing", content)
    
    def test_write_codes_to_file_append(self):
        """Test appending codes to an existing file."""
        # Create initial codes.txt
        initial_content = """# Master codes list
existing-code
"""
        codes_file = self.test_dir / "codes.txt"
        codes_file.write_text(initial_content)
        
        # Append new codes
        new_codes = ["new-code", "another-code"]
        success = self.file_manager.write_codes_to_file(codes_file, new_codes, append=True)
        
        self.assertTrue(success)
        
        # Check content
        content = codes_file.read_text()
        self.assertIn("existing-code", content)
        self.assertIn("new-code", content)
        self.assertIn("another-code", content)
    
    def test_write_codes_to_file_no_duplicates(self):
        """Test that writing codes doesn't create duplicates."""
        # Create initial codes.txt
        initial_content = """# Master codes list
existing-code
"""
        codes_file = self.test_dir / "codes.txt"
        codes_file.write_text(initial_content)
        
        # Try to append the same code
        duplicate_codes = ["existing-code"]
        success = self.file_manager.write_codes_to_file(codes_file, duplicate_codes, append=True)
        
        self.assertTrue(success)
        
        # Check that no duplicate was added
        content = codes_file.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        self.assertEqual(len(lines), 1)  # Should still have only one code
        self.assertEqual(lines[0], "existing-code")
    
    def test_write_codes_to_file_mixed_new_and_existing(self):
        """Test writing a mix of new and existing codes."""
        # Create initial codes.txt
        initial_content = """# Master codes list
existing-code
"""
        codes_file = self.test_dir / "codes.txt"
        codes_file.write_text(initial_content)
        
        # Append mix of new and existing codes
        mixed_codes = ["existing-code", "new-code", "another-new"]
        success = self.file_manager.write_codes_to_file(codes_file, mixed_codes, append=True)
        
        self.assertTrue(success)
        
        # Check content
        content = codes_file.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        self.assertEqual(len(lines), 3)  # Should have 3 unique codes
        self.assertIn("existing-code", lines)
        self.assertIn("new-code", lines)
        self.assertIn("another-new", lines)
    
    def test_create_empty_code_files(self):
        """Test creating empty files for codes."""
        codes = ["workflow", "productivity", "writing"]
        
        created_count = self.file_manager.create_empty_code_files(
            self.test_dir, codes, "coded"
        )
        
        self.assertEqual(created_count, 3)
        
        # Check that files were created
        coded_dir = self.test_dir / "coded"
        self.assertTrue((coded_dir / "workflow.md").exists())
        self.assertTrue((coded_dir / "productivity.md").exists())
        self.assertTrue((coded_dir / "writing.md").exists())
        
        # Check file content
        workflow_content = (coded_dir / "workflow.md").read_text()
        self.assertIn("# workflow", workflow_content)
        
        productivity_content = (coded_dir / "productivity.md").read_text()
        self.assertIn("# productivity", productivity_content)
    
    def test_create_empty_code_files_existing_files(self):
        """Test that existing files are not overwritten."""
        # Create an existing file
        coded_dir = self.test_dir / "coded"
        coded_dir.mkdir()
        existing_file = coded_dir / "workflow.md"
        existing_file.write_text("# workflow\n\nExisting content")
        
        codes = ["workflow", "productivity"]
        
        created_count = self.file_manager.create_empty_code_files(
            self.test_dir, codes, "coded"
        )
        
        # Should only create 1 new file (productivity)
        self.assertEqual(created_count, 1)
        
        # Check that existing file wasn't overwritten
        workflow_content = (coded_dir / "workflow.md").read_text()
        self.assertIn("Existing content", workflow_content)
        
        # Check that new file was created
        self.assertTrue((coded_dir / "productivity.md").exists())
    
    def test_create_empty_code_files_empty_list(self):
        """Test creating empty files with empty codes list."""
        codes = []
        
        created_count = self.file_manager.create_empty_code_files(
            self.test_dir, codes, "coded"
        )
        
        self.assertEqual(created_count, 0)
    
    def test_write_codes_to_file_error_handling(self):
        """Test error handling when writing codes fails."""
        # Create a directory with the same name as the file to cause an error
        codes_file = self.test_dir / "codes.txt"
        codes_file.mkdir()  # This will cause an error when trying to write to it
        
        codes = ["workflow", "productivity"]
        
        success = self.file_manager.write_codes_to_file(codes_file, codes, append=False)
        
        # Should return False on error
        self.assertFalse(success)
    
    def test_create_empty_code_files_error_handling(self):
        """Test error handling when creating empty files fails."""
        # Create a file with the same name as the directory to cause an error
        coded_dir = self.test_dir / "coded"
        coded_dir.write_text("This is a file, not a directory")  # This will cause an error
        
        codes = ["workflow"]
        
        created_count = self.file_manager.create_empty_code_files(
            self.test_dir, codes, "coded"
        )
        
        # Should return 0 on error
        self.assertEqual(created_count, 0)
    
    def test_get_markdown_files_md_only(self):
        """Test getting markdown files when only .md files exist."""
        # Create some .md files
        (self.test_dir / "file1.md").write_text("content1")
        (self.test_dir / "file2.md").write_text("content2")
        (self.test_dir / "subdir").mkdir()
        (self.test_dir / "subdir" / "file3.md").write_text("content3")
        
        # Create some non-supported files that should be ignored
        (self.test_dir / "file.py").write_text("content")
        (self.test_dir / "file.json").write_text("content")
        
        files = self.file_manager.get_markdown_files(self.test_dir)
        
        # Should find 3 .md files
        self.assertEqual(len(files), 3)
        
        # Check that all files are .md files
        for file_path in files:
            self.assertEqual(file_path.suffix.lower(), ".md")
        
        # Check that files are sorted alphanumerically
        file_names = [f.name for f in files]
        self.assertEqual(file_names, ["file1.md", "file2.md", "file3.md"])
    
    def test_get_markdown_files_txt_only(self):
        """Test getting text files when only .txt files exist."""
        # Create some .txt files
        (self.test_dir / "file1.txt").write_text("content1")
        (self.test_dir / "file2.txt").write_text("content2")
        (self.test_dir / "file3.txt").write_text("content3")
        
        # Create some non-supported files that should be ignored
        (self.test_dir / "file.py").write_text("content")
        (self.test_dir / "file.json").write_text("content")
        
        files = self.file_manager.get_markdown_files(self.test_dir)
        
        # Should find 3 .txt files
        self.assertEqual(len(files), 3)
        
        # Check that all files are .txt files
        for file_path in files:
            self.assertEqual(file_path.suffix.lower(), ".txt")
        
        # Check that files are sorted alphanumerically
        file_names = [f.name for f in files]
        self.assertEqual(file_names, ["file1.txt", "file2.txt", "file3.txt"])
    
    def test_get_markdown_files_mixed_formats(self):
        """Test getting both .md and .txt files when both exist."""
        # Create mixed files
        (self.test_dir / "file1.md").write_text("content1")
        (self.test_dir / "file2.txt").write_text("content2")
        (self.test_dir / "file3.md").write_text("content3")
        (self.test_dir / "file4.txt").write_text("content4")
        (self.test_dir / "subdir").mkdir()
        (self.test_dir / "subdir" / "file5.md").write_text("content5")
        (self.test_dir / "subdir" / "file6.txt").write_text("content6")
        
        # Create some files that should be ignored
        (self.test_dir / "file.py").write_text("content")
        (self.test_dir / "file.json").write_text("content")
        
        files = self.file_manager.get_markdown_files(self.test_dir)
        
        # Should find 6 files (3 .md + 3 .txt)
        self.assertEqual(len(files), 6)
        
        # Check that all files are either .md or .txt
        for file_path in files:
            self.assertIn(file_path.suffix.lower(), [".md", ".txt"])
        
        # Check that files are sorted alphanumerically
        file_names = [f.name for f in files]
        expected_names = ["file1.md", "file2.txt", "file3.md", "file4.txt", "file5.md", "file6.txt"]
        self.assertEqual(file_names, expected_names)
    
    def test_get_markdown_files_nonexistent_directory(self):
        """Test getting files from a directory that doesn't exist."""
        nonexistent_dir = self.test_dir / "nonexistent"
        
        files = self.file_manager.get_markdown_files(nonexistent_dir)
        
        # Should return empty list
        self.assertEqual(files, [])
    
    def test_get_markdown_files_empty_directory(self):
        """Test getting files from an empty directory."""
        files = self.file_manager.get_markdown_files(self.test_dir)
        
        # Should return empty list
        self.assertEqual(files, [])
    
    def test_get_markdown_files_natural_sorting(self):
        """Test that files are sorted naturally (handling numbers properly)."""
        # Create files with numbers in names
        (self.test_dir / "file1.md").write_text("content1")
        (self.test_dir / "file10.md").write_text("content10")
        (self.test_dir / "file2.md").write_text("content2")
        (self.test_dir / "file20.txt").write_text("content20")
        (self.test_dir / "file3.txt").write_text("content3")
        
        files = self.file_manager.get_markdown_files(self.test_dir)
        
        # Check natural sorting (1, 2, 3, 10, 20)
        file_names = [f.name for f in files]
        expected_names = ["file1.md", "file2.md", "file3.txt", "file10.md", "file20.txt"]
        self.assertEqual(file_names, expected_names)


if __name__ == '__main__':
    unittest.main() 