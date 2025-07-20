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
    
    def test_square_bracket_malformed_comprehensive(self):
        """Comprehensive test for malformed [[]] format detection."""
        
        # Test 1: Basic malformed square bracket patterns
        text = """This is normal text.

This text ends with malformed closing==[[bad-bracket]]

More normal text.

Another malformed ending==[[another-bad]]

[[good-code]]==This is properly formatted.==[[good-code]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 2)
        
        # Check that malformed patterns are detected
        patterns = [block.malformed_pattern for block in malformed]
        self.assertTrue(any("==[[bad-bracket]]" in pattern for pattern in patterns))
        self.assertTrue(any("==[[another-bad]]" in pattern for pattern in patterns))
        
        # Test 2: Incomplete square bracket structures
        text = """[[incomplete]]==This block is missing its closing

[[complete]]==This block is complete.==[[complete]]

[[another-incomplete]]==This is also incomplete

[[final-complete]]==This one is complete too.==[[final-complete]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 2)  # Should detect incomplete blocks
        
        # Test 3: Wrong bracket patterns
        text = """[wrong-single]==This uses single brackets.==[wrong-single]

[[[too-many]]]==This uses too many brackets.==[[[too-many]]]

[[correct]]==This uses correct double brackets.==[[correct]]

[wrong-again]==Another single bracket attempt.==[wrong-again]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertGreater(len(malformed), 0)  # Should detect wrong patterns
        
        # Test 4: Mixed good and malformed square brackets
        text = """[[good1]]==This is properly formatted.==[[good1]]

This has malformed closing==[[bad1]]

[[good2]]==More good content.==[[good2]]

Another malformed==[[bad2]]

[[good3]]==Final good content.==[[good3]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 2)
        
        # Test 5: Square brackets with nested-looking content (should not be malformed)
        text = """[[nested-looking]]==This content has [[brackets]] that look like they might be nested but are just text content.
It also has [single brackets] and [[double brackets]] in the content.
This should not confuse the parser.==[[nested-looking]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 0, "Should not flag properly matched opening/closing pairs with nested-looking content")
        
        # Test 6: Square brackets with whitespace variations
        text = """[[  spaced  ]]==Content with spaces in code name==[[  spaced  ]]

This has malformed with spaces==[[  bad-spaced  ]]

[[normal]]==Normal content.==[[normal]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 1)
        
        # Test 7: Square brackets with special characters in code names
        text = """[[code-with-dashes]]==Content with dashes.==[[code-with-dashes]]

This has malformed with dashes==[[bad-with-dashes]]

[[code_with_underscores]]==Content with underscores.==[[code_with_underscores]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 1)
        
        # Test 8: Square brackets with unicode content
        text = """[[unicode]]==Content with unicode: ∫₀^∞, ∀x∈ℝ, 你好世界, 🚀🎉==[[unicode]]

This has malformed with unicode==[[bad-unicode]]

[[normal]]==Normal content.==[[normal]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 1)
        
        # Test 9: Square brackets with long code names
        long_name = "b" * 50
        text = f"""[[{long_name}]]==Content with long code name.==[[{long_name}]]

This has malformed with long name==[[{long_name}-bad]]

[[normal]]==Normal content.==[[normal]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertEqual(len(malformed), 1)
        
        # Test 10: Edge cases with square brackets
        text = """[[edge]]==Edge case content.==[[edge]]

This has edge case malformed==[[edge-bad]]

[[empty]]==[[empty]]

This has empty malformed==[[]]

[[single]]==Single line content.==[[single]]"""
        malformed = self.detector.find_all_malformed_blocks(text)
        self.assertGreater(len(malformed), 0)  # Should detect malformed patterns
    
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