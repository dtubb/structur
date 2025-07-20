"""Unit tests for the CodeExtractor module."""

import unittest
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.processors.code_extractor import CodeExtractor
from src.models.text_block import CodedBlock


class TestCodeExtractor(unittest.TestCase):
    """Test cases for CodeExtractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = CodeExtractor()
    
    def test_find_simple_coded_block(self):
        """Test finding a simple coded block."""
        text = "{{test}}==This is a test content=={{test}}"
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].code, "test")
        self.assertEqual(blocks[0].content, "This is a test content")
        self.assertEqual(blocks[0].format_type, "{{")
    
    def test_find_multiple_coded_blocks(self):
        """Test finding multiple coded blocks."""
        text = """
        {{intro}}==Introduction content=={{intro}}
        
        Some uncoded text here.
        
        [[conclusion]]==Conclusion content==[[conclusion]]
        """
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 2)
        
        # Check intro block
        intro_block = next(b for b in blocks if b.code == "intro")
        self.assertEqual(intro_block.content, "Introduction content")
        self.assertEqual(intro_block.format_type, "{{")
        
        # Check conclusion block
        conclusion_block = next(b for b in blocks if b.code == "conclusion")
        self.assertEqual(conclusion_block.content, "Conclusion content")
        self.assertEqual(conclusion_block.format_type, "[[")
    
    def test_extract_code_by_name(self):
        """Test extracting blocks by specific code name."""
        text = """
        {{test}}==First test content=={{test}}
        {{other}}==Other content=={{other}}
        {{test}}==Second test content=={{test}}
        """
        test_blocks = self.extractor.extract_code_by_name(text, "test", "test.md")
        
        self.assertEqual(len(test_blocks), 2)
        self.assertEqual(test_blocks[0].content, "First test content")
        self.assertEqual(test_blocks[1].content, "Second test content")
    
    def test_get_unique_codes(self):
        """Test getting unique code names."""
        text = """
        {{intro}}==Content 1=={{intro}}
        {{body}}==Content 2=={{body}}
        {{intro}}==Content 3=={{intro}}
        [[conclusion]]==Content 4==[[conclusion]]
        """
        codes = self.extractor.get_unique_codes(text)
        
        self.assertEqual(set(codes), {"intro", "body", "conclusion"})
    
    def test_group_blocks_by_code(self):
        """Test grouping blocks by code name."""
        text = """
        {{test}}==Content 1=={{test}}
        {{other}}==Content 2=={{other}}
        {{test}}==Content 3=={{test}}
        """
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        grouped = self.extractor.group_blocks_by_code(blocks)
        
        self.assertEqual(len(grouped["test"]), 2)
        self.assertEqual(len(grouped["other"]), 1)
    
    def test_multiline_content(self):
        """Test extracting multiline content."""
        text = """{{multiline}}==This is a
        multiline content block
        with several lines=={{multiline}}"""
        
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 1)
        self.assertIn("multiline content block", blocks[0].content)
        self.assertIn("several lines", blocks[0].content)
    
    def test_empty_content(self):
        """Test handling empty content."""
        text = "{{empty}}=={{empty}}"
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        # Should not create block for empty content
        self.assertEqual(len(blocks), 0)
    
    def test_whitespace_handling(self):
        """Test handling of whitespace in codes and content."""
        text = "{{ spaced }}== Content with spaces =={{ spaced }}"
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].code, "spaced")
        self.assertEqual(blocks[0].content, "Content with spaces")
    
    def test_get_extraction_stats(self):
        """Test getting extraction statistics."""
        text = """
        {{intro}}==Introduction content=={{intro}}
        {{body}}==Body content with more words=={{body}}
        """
        stats = self.extractor.get_extraction_stats(text)
        
        self.assertEqual(stats["total_blocks"], 2)
        self.assertEqual(stats["unique_codes"], 2)
        self.assertGreater(stats["total_word_count"], 0)
        self.assertIn("intro", stats["codes_list"])
        self.assertIn("body", stats["codes_list"])


if __name__ == "__main__":
    unittest.main() 