"""Unit tests for content filtering (subtractive approach)."""

import unittest
from src.processors.content_filter import ContentFilter


class TestContentFilter(unittest.TestCase):
    """Test cases for content filtering."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.filter = ContentFilter(["{{", "[["])
    
    def test_extract_uncoded_from_pure_text(self):
        """Test extracting uncoded content from text with no codes."""
        text = """This is a normal paragraph.

Another paragraph with regular content.

# A heading

Some more text."""
        result = self.filter.extract_uncoded_content(text)
        # Should return the original text (normalized)
        self.assertIn("This is a normal paragraph", result)
        self.assertIn("Another paragraph", result)
        self.assertIn("# A heading", result)
    
    def test_extract_uncoded_removes_proper_codes(self):
        """Test that properly formatted codes are removed."""
        text = """This is normal text.

{{code1}}==This should be removed.=={{code1}}

This should remain.

[[code2]]==This should also be removed.==[[code2]]

Final paragraph should remain."""
        result = self.filter.extract_uncoded_content(text)
        
        # Should contain uncoded text
        self.assertIn("This is normal text", result)
        self.assertIn("This should remain", result)
        self.assertIn("Final paragraph should remain", result)
        
        # Should NOT contain coded content
        self.assertNotIn("This should be removed", result)
        self.assertNotIn("This should also be removed", result)
        self.assertNotIn("{{code1}}", result)
        self.assertNotIn("[[code2]]", result)
    
    def test_extract_uncoded_removes_malformed(self):
        """Test that malformed codes are removed."""
        text = """This is normal text.

This has malformed ending=={{bad-code}}

This should remain.

Another malformed line==[[bad-bracket]]

Final text remains."""
        result = self.filter.extract_uncoded_content(text)
        
        # Should contain uncoded text
        self.assertIn("This is normal text", result)
        self.assertIn("This should remain", result)
        self.assertIn("Final text remains", result)
        
        # Should NOT contain malformed content
        self.assertNotIn("=={{bad-code}}", result)
        self.assertNotIn("==[[bad-bracket]]", result)
    
    def test_extract_uncoded_complex_scenario(self):
        """Test extraction with mixed content types."""
        text = """# Document Title

This is the introduction paragraph.

{{intro}}==This is coded introduction content that should be removed.=={{intro}}

This paragraph should remain as uncoded content.

Some text with malformed ending=={{broken}}

{{methods}}==This is the methods section coded content.
It spans multiple lines.
All of this should be removed.=={{methods}}

This is the conclusion paragraph that should remain.

Another malformed: ending==[[broken2]]

Final uncoded paragraph."""
        result = self.filter.extract_uncoded_content(text)
        
        # Should contain uncoded text
        self.assertIn("# Document Title", result)
        self.assertIn("This is the introduction paragraph", result)
        self.assertIn("This paragraph should remain", result)
        self.assertIn("This is the conclusion paragraph", result)
        self.assertIn("Final uncoded paragraph", result)
        
        # Should NOT contain coded content
        self.assertNotIn("This is coded introduction content", result)
        self.assertNotIn("This is the methods section", result)
        self.assertNotIn("{{intro}}", result)
        self.assertNotIn("{{methods}}", result)
        
        # Should NOT contain malformed content
        self.assertNotIn("=={{broken}}", result)
        self.assertNotIn("==[[broken2]]", result)
    
    def test_extract_uncoded_preserves_structure(self):
        """Test that text structure is preserved after filtering."""
        text = """Paragraph 1

{{code}}==Remove this=={{code}}

Paragraph 2

Paragraph 3"""
        result = self.filter.extract_uncoded_content(text)
        
        # Should maintain paragraph structure
        lines = [line.strip() for line in result.split('\n') if line.strip()]
        self.assertIn("Paragraph 1", lines)
        self.assertIn("Paragraph 2", lines)
        self.assertIn("Paragraph 3", lines)
        # Should not have coded content
        self.assertNotIn("Remove this", result)
    
    def test_extract_uncoded_empty_input(self):
        """Test extraction with empty or None input."""
        self.assertEqual(self.filter.extract_uncoded_content(""), "")
        self.assertEqual(self.filter.extract_uncoded_content(None), "")
    
    def test_extract_uncoded_only_codes(self):
        """Test extraction from text that contains only codes."""
        text = """{{code1}}==Only coded content here.=={{code1}}

{{code2}}==More coded content.=={{code2}}"""
        result = self.filter.extract_uncoded_content(text)
        
        # Should be empty or only whitespace after filtering
        self.assertTrue(len(result.strip()) == 0)
    
    def test_extract_uncoded_nested_like_content(self):
        """Test extraction with content that looks like nested codes."""
        text = """Normal text here.

{{outer}}==This contains text with {{inner}} markers but they're inside a code block.=={{outer}}

This should remain.

Text mentioning {{code}} markers but not actually coded.

Malformed ending=={{bad}}"""
        result = self.filter.extract_uncoded_content(text)
        
        # Should contain uncoded text
        self.assertIn("Normal text here", result)
        self.assertIn("This should remain", result)
        self.assertIn("Text mentioning {{code}} markers", result)
        
        # Should NOT contain coded content
        self.assertNotIn("This contains text with {{inner}}", result)
        self.assertNotIn("=={{bad}}", result)
    
    def test_remove_coded_blocks_only(self):
        """Test removing only coded blocks (not malformed)."""
        text = """Normal text.

{{code}}==Remove this.=={{code}}

Keep this.

Malformed ending=={{bad}}"""
        result = self.filter.remove_coded_blocks(text)
        
        # Should remove coded but keep malformed
        self.assertIn("Normal text", result)
        self.assertIn("Keep this", result)
        self.assertIn("=={{bad}}", result)  # Malformed should remain
        self.assertNotIn("Remove this", result)
    
    def test_remove_malformed_blocks_only(self):
        """Test removing only malformed blocks (not coded)."""
        text = """Normal text.

{{code}}==Keep this coded content.=={{code}}

Keep this normal text.

Malformed ending=={{bad}}"""
        result = self.filter.remove_malformed_blocks(text)
        
        # Should remove malformed but keep coded
        self.assertIn("Normal text", result)
        self.assertIn("Keep this normal text", result)
        self.assertIn("Keep this coded content", result)  # Coded should remain
        self.assertNotIn("=={{bad}}", result)


if __name__ == '__main__':
    unittest.main() 