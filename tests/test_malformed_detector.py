"""Unit tests for malformed content detection."""

import unittest
from src.processors.malformed_detector import MalformedDetector


class TestMalformedDetector(unittest.TestCase):
    """Test cases for malformed content detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = MalformedDetector(["{{", "[["])
    
    def test_no_malformed_content(self):
        """Test text with no malformed content."""
        text = "This is just normal text with no codes."
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 0)
    
    def test_properly_formatted_content(self):
        """Test text with properly formatted coded blocks."""
        text = """{{good-code}}==This is properly coded content.=={{good-code}}
        
This is normal text.

[[another-code]]==More coded content.==[[another-code]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 0)
    
    def test_closing_only_malformed(self):
        """Test text with closing-only malformed blocks."""
        text = """This is normal text.

This text ends with malformed closing=={{bad-code}}

More normal text.

Another malformed ending==[[bad-bracket]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 2)
        
        # Check the malformed content
        codes = [block.malformed_pattern for block in malformed]
        self.assertIn("=={{bad-code}}", codes[0])
        self.assertIn("==[[bad-bracket]]", codes[1])
    
    def test_mixed_good_and_malformed(self):
        """Test text with both good and malformed content."""
        text = """{{good-code}}==This is properly coded.=={{good-code}}

This is normal text.

This has malformed closing=={{bad-code}}

[[good-bracket]]==More good content.==[[good-bracket]]

Another malformed=={{another-bad}}"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 2)
    
    def test_false_positive_prevention(self):
        """Test that properly matched codes are not flagged as malformed."""
        text = """{{code1}}==Content here.
Some middle content.
More content with ending=={{code1}}"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 0, "Should not flag properly matched opening/closing pairs")
    
    def test_multiple_formats(self):
        """Test malformed detection across different formats."""
        text = """Good: {{code1}}==Content=={{code1}}
Bad: Text ending=={{bad1}}
Good: [[code2]]==Content==[[code2]]
Bad: Text ending==[[bad2]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 2)
        
        # Check both formats are detected
        patterns = [block.malformed_pattern for block in malformed]
        has_curly = any("=={{bad1}}" in pattern for pattern in patterns)
        has_square = any("==[[bad2]]" in pattern for pattern in patterns)
        self.assertTrue(has_curly, "Should detect malformed curly brace format")
        self.assertTrue(has_square, "Should detect malformed square bracket format")
    
    def test_malformed_codes_in_different_contexts(self):
        """Test malformed codes in various text contexts."""
        text = """# Heading

Normal paragraph text ending with=={{malformed1}}

- List item
- Another item with bad ending=={{malformed2}}

> Quote text ending badly=={{malformed3}}

```code block```

Final paragraph with issue==[[malformed4]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 4)
    
    def test_edge_cases(self):
        """Test edge cases and special characters."""
        text = """Text with special chars: ending=={{code-with-dashes}}
Text with numbers: ending=={{code123}}
Text with underscores: ending=={{code_under_score}}
Empty code: ending=={{}}
Spaces in code: ending=={{ spaced code }}"""
        malformed = self.detector.find_all_malformed_blocks(text)
        # All should be detected as malformed (no matching openings)
        self.assertEqual(len(malformed), 5)
    
    def test_performance_with_large_text(self):
        """Test performance with larger text blocks."""
        # Create a large text with scattered malformed content
        large_text = "Normal text. " * 1000
        large_text += "Bad ending=={{malformed}}\n"
        large_text += "More normal text. " * 1000
        
        malformed = self.detector.find_all_malformed_blocks(large_text)
        self.assertEqual(len(malformed), 1)


if __name__ == '__main__':
    unittest.main() 