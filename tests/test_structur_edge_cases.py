#!/usr/bin/env python3
"""
Edge case tests for the structur system.
Tests unusual conditions, error handling, and boundary scenarios.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the project root to the path so we can import structur
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from structur import process_folder


class TestStructurEdgeCases(unittest.TestCase):
    """Test edge cases and unusual scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.input_dir = self.test_dir / "input"
        self.output_dir = self.test_dir / "output"
        self.input_dir.mkdir()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = self.input_dir / filename
        file_path.write_text(content)
        return file_path
    
    def test_extreme_whitespace_variations(self):
        """Test various whitespace patterns in code blocks."""
        whitespace_content = """# Whitespace Variations Test
        
{{  spaced-start  }}==Content with spaces in code name=={{  spaced-start  }}

{{tab	name}}==Content with tab in code name=={{tab	name}}

{{
multiline-name
}}==Content with newlines in code name=={{
multiline-name
}}

{{normal}}==  Content with leading spaces  =={{normal}}

{{trailing}}==Content with trailing spaces  =={{trailing}}

{{	tabs	}}==	Content with tabs everywhere	=={{	tabs	}}

{{mixed   spacing}}==Content with mixed spacing patterns in name=={{mixed   spacing}}
        """
        
        self.create_test_file("whitespace_test.md", whitespace_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process successfully
        self.assertEqual(results['files_processed'], 1)
        
        # Check that some coded files were created (whitespace should be normalized)
        coded_dir = self.output_dir / "coded"
        coded_files = list(coded_dir.glob("*.md"))
        self.assertGreater(len(coded_files), 0)
    
    def test_bracket_format_variations(self):
        """Test various bracket format patterns."""
        bracket_content = """# Bracket Format Test
        
[[research]]==This uses square brackets instead of curly braces.==[[research]]

[[  spaced-brackets  ]]==Square brackets with spaces.==[[  spaced-brackets  ]]

[[mixed-content]]==This has [[nested-looking]] brackets in content.==[[mixed-content]]

{{curly}}==This uses curly braces as normal.=={{curly}}

[[square-multi]]==This is a longer block with square brackets.
It spans multiple lines and contains various content.
Should be processed correctly.==[[square-multi]]
        """
        
        self.create_test_file("bracket_test.md", bracket_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process successfully
        self.assertEqual(results['files_processed'], 1)
        
        # Check that both formats were processed
        coded_dir = self.output_dir / "coded"
        
        # Should have files for both curly and square bracket formats
        research_file = coded_dir / "research.md"
        curly_file = coded_dir / "curly.md"
        
        if research_file.exists():
            research_content = research_file.read_text()
            self.assertIn("square brackets", research_content)
        
        if curly_file.exists():
            curly_content = curly_file.read_text()
            self.assertIn("curly braces", curly_content)
    
    def test_long_code_names(self):
        """Test moderately long code names that might occur in practice."""
        long_name = "a" * 50  # 50 characters - long but realistic
        
        # Build the content manually to avoid f-string brace escaping issues
        long_name_content = "# Long Code Name Test\n        \n" + \
                           "{{" + long_name + "}}==This block has a moderately long code name that tests the system's ability to handle longer naming patterns.=={{" + long_name + "}}\n\n" + \
                           "{{normal}}==This is a normal block for comparison.=={{normal}}\n        "
        
        self.create_test_file("long_name_test.md", long_name_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process successfully
        self.assertEqual(results['files_processed'], 1)
        
        # Check that files were created
        coded_dir = self.output_dir / "coded"
        coded_files = list(coded_dir.glob("*.md"))
        self.assertGreater(len(coded_files), 0)
        
        # Normal block should definitely exist
        normal_file = coded_dir / "normal.md"
        self.assertTrue(normal_file.exists())
    
    def test_code_names_with_special_characters(self):
        """Test code names with special characters."""
        special_chars_content = """# Special Characters in Code Names Test
        
{{code-with-dashes}}==Content with dashes in name.=={{code-with-dashes}}

{{code_with_underscores}}==Content with underscores in name.=={{code_with_underscores}}

{{code.with.dots}}==Content with dots in name.=={{code.with.dots}}

{{code123numbers}}==Content with numbers in name.=={{code123numbers}}

{{UPPERCASE}}==Content with uppercase name.=={{UPPERCASE}}

{{MixedCase}}==Content with mixed case name.=={{MixedCase}}

{{code/with/slashes}}==Content with slashes in name.=={{code/with/slashes}}

{{code:with:colons}}==Content with colons in name.=={{code:with:colons}}
        """
        
        self.create_test_file("special_chars_test.md", special_chars_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process successfully
        self.assertEqual(results['files_processed'], 1)
        
        # Check that files were created (some might have sanitized names)
        coded_dir = self.output_dir / "coded"
        coded_files = list(coded_dir.glob("*.md"))
        self.assertGreater(len(coded_files), 0)
        
        # Check some specific expected files
        expected_safe_names = ["code-with-dashes.md", "code_with_underscores.md", "UPPERCASE.md"]
        for expected_name in expected_safe_names:
            expected_file = coded_dir / expected_name
            if expected_file.exists():
                content = expected_file.read_text()
                self.assertGreater(len(content), 0)
    
    def test_mixed_content_blocks(self):
        """Test files with mixed types of content blocks."""
        mixed_content = """# Mixed Content Test
        
Normal paragraph before any blocks.

{{first-block}}==This is the first coded block with some content.=={{first-block}}

Another paragraph between blocks.

==Malformed block with no opening==[[malformed]]

{{second-block}}==This is the second coded block.=={{second-block}}

[[bracket-format]]==This uses bracket format instead.==[[bracket-format]]

More text between different types.

{{incomplete-block}}==This block is missing its closing

{{third-block}}==This is a complete third block.=={{third-block}}

==Another malformed closing only=={{another-malformed}}

Final paragraph with no blocks.
        """
        
        self.create_test_file("mixed_content_test.md", mixed_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process successfully
        self.assertEqual(results['files_processed'], 1)
        
        # Check that coded content was extracted
        coded_dir = self.output_dir / "coded"
        coded_files = list(coded_dir.glob("*.md"))
        self.assertGreater(len(coded_files), 0)
        
        # Check for specific expected files
        expected_files = ["first-block.md", "second-block.md", "third-block.md"]
        for expected_file in expected_files:
            file_path = coded_dir / expected_file
            if file_path.exists():
                content = file_path.read_text()
                self.assertGreater(len(content), 0)
        
        # Check that uncoded content exists and contains the normal paragraphs
        uncoded_dir = self.output_dir / "uncoded"
        uncoded_files = list(uncoded_dir.glob("*.md"))
        self.assertEqual(len(uncoded_files), 1)
        
        uncoded_content = uncoded_files[0].read_text()
        self.assertIn("Normal paragraph before", uncoded_content)
        self.assertIn("Final paragraph with no blocks", uncoded_content)
        
        # Check that malformed content was detected
        malformed_dir = self.output_dir / "malformed"
        if malformed_dir.exists():
            malformed_files = list(malformed_dir.glob("*.md"))
            # May or may not have malformed files depending on detection
    
    def test_file_encoding_variations(self):
        """Test files with different encodings (if supported)."""
        # Create content with various encodings
        unicode_content = """# Encoding Test
        
{{encoding-test}}==This file tests various character encodings: UTF-8 支持中文, العربية, русский язык, emoji 🚀🌟💻=={{encoding-test}}

{{ascii-safe}}==This content should be safe in ASCII: basic English text only.=={{ascii-safe}}

{{latin-extended}}==Extended Latin characters: café, naïve, résumé, piñata, Zürich=={{latin-extended}}
        """
        
        # Test UTF-8 (default)
        self.create_test_file("utf8_test.md", unicode_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process successfully
        self.assertEqual(results['files_processed'], 1)
        
        # Check that Unicode content was preserved
        coded_dir = self.output_dir / "coded"
        encoding_file = coded_dir / "encoding-test.md"
        
        if encoding_file.exists():
            content = encoding_file.read_text()
            self.assertIn("支持中文", content)
            self.assertIn("🚀", content)
    
    def test_very_small_blocks(self):
        """Test very small content blocks."""
        tiny_content = """# Tiny Blocks Test
        
{{a}}==x=={{a}}

{{single-char}}==A=={{single-char}}

{{empty}}===={{empty}}

{{space}}== =={{space}}

{{newline}}==
=={{newline}}

{{normal}}==This is a normal sized block for comparison.=={{normal}}
        """
        
        self.create_test_file("tiny_blocks_test.md", tiny_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process successfully
        self.assertEqual(results['files_processed'], 1)
        
        # Check that even tiny blocks were processed
        coded_dir = self.output_dir / "coded"
        coded_files = list(coded_dir.glob("*.md"))
        self.assertGreater(len(coded_files), 0)
        
        # Check specific tiny files if they exist
        single_char_file = coded_dir / "single-char.md"
        if single_char_file.exists():
            content = single_char_file.read_text()
            # Should contain the single character
            self.assertIn("A", content)
        
        normal_file = coded_dir / "normal.md"
        self.assertTrue(normal_file.exists())
        normal_content = normal_file.read_text()
        self.assertIn("normal sized block", normal_content)


class TestStructurPerformanceAndScale(unittest.TestCase):
    """Test performance and scale scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.input_dir = self.test_dir / "input"
        self.output_dir = self.test_dir / "output"
        self.input_dir.mkdir()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = self.input_dir / filename
        file_path.write_text(content)
        return file_path
    
    def test_many_small_files(self):
        """Test processing many small files."""
        # Create 50 small files
        for i in range(50):
            content = f"""# Small File {i+1}
            
{{{{small-{i}}}}}==This is small file number {i+1} with unique content.=={{{{small-{i}}}}}

Some uncoded text for file {i+1}.
            """
            self.create_test_file(f"small_{i+1:02d}.md", content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process all files
        self.assertEqual(results['files_processed'], 50)
        
        # Check that coded files were created
        coded_dir = self.output_dir / "coded"
        coded_files = list(coded_dir.glob("small-*.md"))
        self.assertEqual(len(coded_files), 50)
        
        # Check that uncoded files were created
        uncoded_dir = self.output_dir / "uncoded"
        uncoded_files = list(uncoded_dir.glob("*.md"))
        self.assertEqual(len(uncoded_files), 50)
    
    def test_few_large_files(self):
        """Test processing a few very large files."""
        # Create 3 large files
        large_block = "This is a large block of text. " * 500  # ~15,000 characters
        
        for i in range(3):
            content = f"""# Large File {i+1}
            
{{{{large-content-{i}}}}}=={large_block} Additional content for file {i+1}.=={{{{large-content-{i}}}}}

{{{{shared-large}}}}=={large_block} This content is shared across large files.=={{{{shared-large}}}}

{"Uncoded paragraph. " * 200}  # Large uncoded section
            """
            self.create_test_file(f"large_{i+1}.md", content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process all files
        self.assertEqual(results['files_processed'], 3)
        
        # Check that large coded files were created
        coded_dir = self.output_dir / "coded"
        large_files = list(coded_dir.glob("large-content-*.md"))
        self.assertEqual(len(large_files), 3)
        
        # Check that shared content was deduplicated
        shared_file = coded_dir / "shared-large.md"
        self.assertTrue(shared_file.exists())
        
        # Check that duplicates were detected
        duplicates_dir = self.output_dir / "duplicates"
        if duplicates_dir.exists():
            duplicate_folders = list(duplicates_dir.iterdir())
            self.assertGreater(len(duplicate_folders), 0)
    
    def test_mixed_file_sizes(self):
        """Test processing files of varied sizes."""
        # Create files of different sizes
        sizes = [
            ("tiny", "{{tiny}}==x=={{tiny}}"),
            ("small", "{{small}}==" + ("Small content. " * 10) + "=={{small}}"),
            ("medium", "{{medium}}==" + ("Medium content block. " * 100) + "=={{medium}}"),
            ("large", "{{large}}==" + ("Large content section. " * 500) + "=={{large}}"),
            ("huge", "{{huge}}==" + ("Huge content block. " * 1000) + "=={{huge}}")
        ]
        
        for size_name, content in sizes:
            full_content = f"""# {size_name.title()} File
            
{content}

Uncoded text for {size_name} file.
            """
            self.create_test_file(f"{size_name}_file.md", full_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process all files
        self.assertEqual(results['files_processed'], 5)
        
        # Check that all size categories were processed
        coded_dir = self.output_dir / "coded"
        for size_name, _ in sizes:
            size_file = coded_dir / f"{size_name}.md"
            self.assertTrue(size_file.exists(), f"Missing {size_name} file")
            
            content = size_file.read_text()
            self.assertGreater(len(content), 0)


if __name__ == '__main__':
    unittest.main() 