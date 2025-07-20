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
    
    def test_square_bracket_format_comprehensive(self):
        """Comprehensive test for [[]] format extraction."""
        
        # Test 1: Basic square bracket extraction
        text = "[[test]]==This is square bracket content==[[test]]"
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].code, "test")
        self.assertEqual(blocks[0].content, "This is square bracket content")
        self.assertEqual(blocks[0].format_type, "[[")
        
        # Test 2: Multiple square bracket blocks
        text = """
        [[first]]==First square bracket block==[[first]]
        [[second]]==Second square bracket block==[[second]]
        [[third]]==Third square bracket block==[[third]]
        """
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 3)
        codes = [block.code for block in blocks]
        self.assertIn("first", codes)
        self.assertIn("second", codes)
        self.assertIn("third", codes)
        
        # All should be square bracket format
        for block in blocks:
            self.assertEqual(block.format_type, "[[")
        
        # Test 3: Square brackets with whitespace
        text = "[[  spaced  ]]==Content with spaces in code name==[[  spaced  ]]"
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].code, "spaced")  # Whitespace is stripped
        self.assertEqual(blocks[0].content, "Content with spaces in code name")
        self.assertEqual(blocks[0].format_type, "[[")
        
        # Test 4: Square brackets with special characters in code name
        text = "[[code-with-dashes]]==Content with dashes==[[code-with-dashes]]"
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].code, "code-with-dashes")
        self.assertEqual(blocks[0].format_type, "[[")
        
        # Test 5: Square brackets with multi-line content
        text = """[[multiline]]==This is a multi-line content block.
It spans several lines and contains various content.
Line 3 with more content.
Final line of the block.==[[multiline]]"""
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].code, "multiline")
        self.assertIn("Line 3 with more content", blocks[0].content)
        self.assertIn("Final line of the block", blocks[0].content)
        self.assertEqual(blocks[0].format_type, "[[")
        
        # Test 6: Mixed square brackets and curly braces
        text = """
        [[square]]==Square bracket content==[[square]]
        {{curly}}==Curly brace content=={{curly}}
        [[another-square]]==Another square bracket==[[another-square]]
        """
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 3)
        
        square_blocks = [b for b in blocks if b.format_type == "[["]
        curly_blocks = [b for b in blocks if b.format_type == "{{"]
        
        self.assertEqual(len(square_blocks), 2)
        self.assertEqual(len(curly_blocks), 1)
        
        # Test 7: Square brackets with nested-looking content
        text = "[[nested]]==This has [[brackets]] that look nested but aren't==[[nested]]"
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].code, "nested")
        self.assertIn("[[brackets]]", blocks[0].content)  # Should preserve as text
        self.assertEqual(blocks[0].format_type, "[[")
        
        # Test 8: Square brackets with empty content
        text = "[[empty]]==[[empty]]"
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 0)  # Empty content blocks are not processed
        
        # Test 9: Square brackets with unicode content
        text = "[[unicode]]==Content with unicode: ∫₀^∞, ∀x∈ℝ, 你好世界, 🚀🎉==[[unicode]]"
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].code, "unicode")
        self.assertIn("∫₀^∞", blocks[0].content)
        self.assertIn("你好世界", blocks[0].content)
        self.assertIn("🚀🎉", blocks[0].content)
        self.assertEqual(blocks[0].format_type, "[[")
        
        # Test 10: Square brackets with long code names
        long_name = "b" * 50
        text = f"[[{long_name}]]==Content with long code name==[[{long_name}]]"
        blocks = self.extractor.find_all_coded_blocks(text, "test.md")
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].code, long_name)
        self.assertEqual(blocks[0].content, "Content with long code name")
        self.assertEqual(blocks[0].format_type, "[[")
    
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