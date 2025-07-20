"""Integration tests for the complete workflow with realistic data."""

import unittest
import tempfile
import shutil
from pathlib import Path
from src.processors.main_processor import StructurProcessor
from src.models.config import ProcessingConfig


class TestWorkflowIntegration(unittest.TestCase):
    """Test the complete workflow with realistic scenarios."""
    
    def setUp(self):
        """Set up test fixtures with temporary directories."""
        self.test_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.test_dir) / "input"
        self.output_dir = Path(self.test_dir) / "output"
        self.input_dir.mkdir()
        self.output_dir.mkdir()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def create_test_file(self, filename: str, content: str):
        """Helper to create test files."""
        file_path = self.input_dir / filename
        file_path.write_text(content)
        return file_path
    
    def test_pure_uncoded_file(self):
        """Test processing a file with only uncoded content."""
        content = """# Introduction

This is a normal document with no coded content.

## Background

This section explains the background of the research.

The methodology involved participant observation and interviews."""
        
        self.create_test_file("uncoded_doc.md", content)
        
        # Process the file
        config = ProcessingConfig(
            input_folder=self.input_dir,
            output_base=self.output_dir
        )
        processor = StructurProcessor(config)
        processor.process_folder()
        
        # Check results
        self.assertTrue((self.output_dir / "uncoded" / "uncoded_doc.md").exists())
        # Coded folder should either not exist or be empty
        if (self.output_dir / "coded").exists():
            self.assertEqual(len(list((self.output_dir / "coded").glob("*.md"))), 0)
        # Malformed folder should either not exist or be empty
        if (self.output_dir / "malformed").exists():
            self.assertEqual(len(list((self.output_dir / "malformed").glob("*.md"))), 0)
        
        # Verify uncoded content is preserved
        uncoded_content = (self.output_dir / "uncoded" / "uncoded_doc.md").read_text()
        self.assertIn("Introduction", uncoded_content)
        self.assertIn("participant observation", uncoded_content)
    
    def test_properly_coded_file(self):
        """Test processing a file with properly formatted codes."""
        content = """# Research Document

This is the introduction.

{{methodology}}==The research methodology involved three phases:
1. Literature review
2. Data collection through interviews
3. Analysis using thematic coding

Data was collected over 6 months.=={{methodology}}

This is the conclusion section.

{{findings}}==Key findings include:
- Pattern A was observed in 80% of cases
- Pattern B emerged as significant
- Theoretical implications are discussed=={{findings}}

Final thoughts and recommendations."""
        
        self.create_test_file("coded_doc.md", content)
        
        # Process the file
        config = ProcessingConfig(
            input_folder=self.input_dir,
            output_base=self.output_dir
        )
        processor = StructurProcessor(config)
        processor.process_folder()
        
        # Check results
        self.assertTrue((self.output_dir / "coded" / "methodology.md").exists())
        self.assertTrue((self.output_dir / "coded" / "findings.md").exists())
        self.assertTrue((self.output_dir / "uncoded" / "coded_doc.md").exists())
        
        # Verify coded content is extracted
        methodology_content = (self.output_dir / "coded" / "methodology.md").read_text()
        self.assertIn("three phases", methodology_content)
        self.assertIn("Data was collected", methodology_content)
        
        findings_content = (self.output_dir / "coded" / "findings.md").read_text()
        self.assertIn("Pattern A was observed", findings_content)
        
        # Verify uncoded content excludes coded blocks
        uncoded_content = (self.output_dir / "uncoded" / "coded_doc.md").read_text()
        self.assertIn("This is the introduction", uncoded_content)
        self.assertIn("This is the conclusion", uncoded_content)
        self.assertIn("Final thoughts", uncoded_content)
        self.assertNotIn("three phases", uncoded_content)
        self.assertNotIn("Pattern A was observed", uncoded_content)
    
    def test_malformed_content_file(self):
        """Test processing a file with malformed codes."""
        content = """# Document with Issues

This is normal content.

{{good-code}}==This is properly formatted.=={{good-code}}

This paragraph ends with malformed content=={{broken-closing}}

More normal content here.

Another issue with wrong format==[[broken-bracket]]

Final paragraph."""
        
        self.create_test_file("malformed_doc.md", content)
        
        # Process the file
        config = ProcessingConfig(
            input_folder=self.input_dir,
            output_base=self.output_dir
        )
        processor = StructurProcessor(config)
        processor.process_folder()
        
        # Check results
        self.assertTrue((self.output_dir / "coded" / "good-code.md").exists())
        self.assertTrue((self.output_dir / "malformed" / "malformed_doc.md").exists())
        self.assertTrue((self.output_dir / "uncoded" / "malformed_doc.md").exists())
        
        # Verify proper code is extracted
        good_content = (self.output_dir / "coded" / "good-code.md").read_text()
        self.assertIn("properly formatted", good_content)
        
        # Verify malformed content is captured
        malformed_content = (self.output_dir / "malformed" / "malformed_doc.md").read_text()
        self.assertTrue(len(malformed_content.strip()) > 0)
        
        # Verify uncoded content excludes both coded and malformed
        uncoded_content = (self.output_dir / "uncoded" / "malformed_doc.md").read_text()
        self.assertIn("This is normal content", uncoded_content)
        self.assertIn("More normal content", uncoded_content)
        self.assertIn("Final paragraph", uncoded_content)
        self.assertNotIn("properly formatted", uncoded_content)
        self.assertNotIn("=={{broken-closing}}", uncoded_content)
        self.assertNotIn("==[[broken-bracket]]", uncoded_content)
    
    def test_duplicate_content_detection(self):
        """Test detection and handling of duplicate content."""
        # Create two files with duplicate coded content
        content1 = """# File 1

{{shared-code}}==This content appears in multiple files.
It should be detected as duplicate.=={{shared-code}}

Unique content in file 1."""
        
        content2 = """# File 2

Different introduction.

{{shared-code}}==This content appears in multiple files.
It should be detected as duplicate.=={{shared-code}}

Unique content in file 2."""
        
        self.create_test_file("file1.md", content1)
        self.create_test_file("file2.md", content2)
        
        # Process the files
        config = ProcessingConfig(
            input_folder=self.input_dir,
            output_base=self.output_dir
        )
        processor = StructurProcessor(config)
        processor.process_folder()
        
        # Check that duplicates are handled
        self.assertTrue((self.output_dir / "duplicates").exists())
        
        # Only one instance should be in coded folder
        coded_content = (self.output_dir / "coded" / "shared-code.md").read_text()
        self.assertIn("appears in multiple files", coded_content)
        
        # Duplicate should be in duplicates folder
        duplicate_files = list((self.output_dir / "duplicates").rglob("*.md"))
        self.assertTrue(len(duplicate_files) > 0)
    
    def test_mixed_formats_file(self):
        """Test processing files with both {{}} and [[]] formats."""
        content = """# Mixed Format Document

Introduction text.

{{curly-code}}==Content in curly braces format.
Multiple lines of content.=={{curly-code}}

Middle section text.

[[square-code]]==Content in square brackets format.
Also multiple lines.==[[square-code]]

Conclusion text."""
        
        self.create_test_file("mixed_formats.md", content)
        
        # Process the file
        config = ProcessingConfig(
            input_folder=self.input_dir,
            output_base=self.output_dir
        )
        processor = StructurProcessor(config)
        processor.process_folder()
        
        # Check both formats are processed
        self.assertTrue((self.output_dir / "coded" / "curly-code.md").exists())
        self.assertTrue((self.output_dir / "coded" / "square-code.md").exists())
        
        # Verify content is correctly extracted
        curly_content = (self.output_dir / "coded" / "curly-code.md").read_text()
        self.assertIn("curly braces format", curly_content)
        
        square_content = (self.output_dir / "coded" / "square-code.md").read_text()
        self.assertIn("square brackets format", square_content)
        
        # Verify uncoded content excludes both formats
        uncoded_content = (self.output_dir / "uncoded" / "mixed_formats.md").read_text()
        self.assertIn("Introduction text", uncoded_content)
        self.assertIn("Middle section text", uncoded_content)
        self.assertIn("Conclusion text", uncoded_content)
        self.assertNotIn("curly braces format", uncoded_content)
        self.assertNotIn("square brackets format", uncoded_content)
    
    def test_complex_realistic_document(self):
        """Test with a complex, realistic academic document."""
        content = """# Ordinary Violence: An Ethnographic Study

## Abstract

This study examines the phenomenon of ordinary violence in urban contexts.

{{abstract}}==This ethnographic study examines ordinary violence in Medellín, Colombia.
Through 18 months of fieldwork, we analyzed how violence becomes normalized
in everyday life. Findings suggest three key patterns of normalization.=={{abstract}}

## Introduction

Violence has been studied extensively, but ordinary violence remains understudied.

{{introduction}}==Previous research has focused on spectacular violence while ignoring
the mundane forms that shape daily experience. This study fills that gap
by examining how violence becomes ordinary through repeated exposure.=={{introduction}}

## Methodology

The research methodology followed standard ethnographic approaches.

Some text with issues=={{broken-method}}

{{fieldwork}}==Fieldwork was conducted over 18 months in Comuna 13, Medellín.
Data collection involved:
- Participant observation (daily, 6-8 hours)
- In-depth interviews (45 participants)
- Photo documentation
- Field notes and reflexive journaling=={{fieldwork}}

## Findings

Three main patterns emerged from the analysis.

{{findings}}==Pattern 1: Normalization through repetition
Residents described how daily exposure to violence made it feel "normal"

Pattern 2: Adaptation strategies
Communities developed coping mechanisms and safety protocols

Pattern 3: Resistance practices
Subtle forms of resistance emerged in everyday practices=={{findings}}

## Conclusion

This study contributes to understanding violence as ordinary.

Final thoughts and recommendations for future research."""
        
        self.create_test_file("ethnographic_study.md", content)
        
        # Process the file
        config = ProcessingConfig(
            input_folder=self.input_dir,
            output_base=self.output_dir
        )
        processor = StructurProcessor(config)
        processor.process_folder()
        
        # Check all sections are properly processed
        coded_files = ["abstract.md", "introduction.md", "fieldwork.md", "findings.md"]
        for coded_file in coded_files:
            self.assertTrue((self.output_dir / "coded" / coded_file).exists(),
                          f"Missing coded file: {coded_file}")
        
        # Check malformed content is detected
        self.assertTrue((self.output_dir / "malformed" / "ethnographic_study.md").exists())
        
        # Verify specific content extraction
        abstract_content = (self.output_dir / "coded" / "abstract.md").read_text()
        self.assertIn("18 months of fieldwork", abstract_content)
        
        fieldwork_content = (self.output_dir / "coded" / "fieldwork.md").read_text()
        self.assertIn("Comuna 13", fieldwork_content)
        self.assertIn("45 participants", fieldwork_content)
        
        # Verify uncoded content preserves structure
        uncoded_content = (self.output_dir / "uncoded" / "ethnographic_study.md").read_text()
        self.assertIn("# Ordinary Violence", uncoded_content)
        self.assertIn("## Introduction", uncoded_content)
        self.assertIn("Violence has been studied", uncoded_content)
        self.assertIn("Final thoughts", uncoded_content)
        
        # Should not contain coded content
        self.assertNotIn("18 months of fieldwork", uncoded_content)
        self.assertNotIn("Comuna 13", uncoded_content)
    
    def test_word_count_accuracy(self):
        """Test that word counts are accurate and no content is lost."""
        content = """This is a test document with exactly fifty words in total content.
        
{{coded-section}}==This coded section has exactly twenty words in it for testing purposes.=={{coded-section}}

The remaining uncoded section has exactly twenty more words for testing."""
        
        self.create_test_file("word_count_test.md", content)
        
        # Count original words
        original_words = len(content.split())
        
        # Process the file
        config = ProcessingConfig(
            input_folder=self.input_dir,
            output_base=self.output_dir
        )
        processor = StructurProcessor(config)
        processor.process_folder()
        
        # Count words in all outputs
        coded_content = (self.output_dir / "coded" / "coded-section.md").read_text()
        coded_words = len(coded_content.split())
        
        uncoded_content = (self.output_dir / "uncoded" / "word_count_test.md").read_text()
        uncoded_words = len(uncoded_content.split())
        
        # Account for code markers being removed
        # Original content has markers like {{coded-section}}== and =={{coded-section}}
        # These should be subtracted from word count
        marker_words = len("{{coded-section}}== =={{coded-section}}".split())
        expected_content_words = original_words - marker_words
        
        total_processed_words = coded_words + uncoded_words
        
        # Allow small variance for whitespace normalization
        self.assertAlmostEqual(total_processed_words, expected_content_words, delta=2,
                             msg=f"Word count mismatch. Original: {original_words}, "
                                 f"Processed: {total_processed_words}, "
                                 f"Expected content: {expected_content_words}")


if __name__ == '__main__':
    unittest.main() 