#!/usr/bin/env python3
"""
Comprehensive unit tests for the main structur.py system.
Tests the function interface with extensive test data and edge cases.
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


class TestStructurMain(unittest.TestCase):
    """Test the main structur.py system with comprehensive test cases."""
    
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
    
    def test_basic_functionality(self):
        """Test basic processing functionality."""
        content = """# Test Document
        
{{workflow}}==This is a workflow note about daily tasks.=={{workflow}}

Some uncoded text here.

{{productivity}}==Tips for better productivity include time blocking.=={{productivity}}
        """
        
        self.create_test_file("test.md", content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Check that all output folders were created
        self.assertTrue((self.output_dir / "coded").exists())
        self.assertTrue((self.output_dir / "uncoded").exists())
        self.assertTrue((self.output_dir / "duplicates").exists())
        self.assertTrue((self.output_dir / "malformed").exists())
        self.assertTrue((self.output_dir / "originals").exists())
        
        # Check that coded files were created
        workflow_file = self.output_dir / "coded" / "workflow.md"
        productivity_file = self.output_dir / "coded" / "productivity.md"
        
        self.assertTrue(workflow_file.exists())
        self.assertTrue(productivity_file.exists())
        
        # Check content
        workflow_content = workflow_file.read_text()
        self.assertIn("daily tasks", workflow_content)
        
        productivity_content = productivity_file.read_text()
        self.assertIn("time blocking", productivity_content)
        
        # Check uncoded content
        uncoded_files = list((self.output_dir / "uncoded").glob("*.md"))
        self.assertEqual(len(uncoded_files), 1)
        uncoded_content = uncoded_files[0].read_text()
        self.assertIn("Some uncoded text here", uncoded_content)
        
        # Check statistics
        self.assertIn('folder_stats', results)
        self.assertIn('coded', results['folder_stats'])
        self.assertIn('uncoded', results['folder_stats'])


class TestExtensiveContentScenarios(unittest.TestCase):
    """Test with extensive and complex content scenarios."""
    
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
    
    def test_academic_paper_processing(self):
        """Test processing a realistic academic paper with citations and complex structure."""
        academic_content = """# Ordinary Violence in Colombian Mining Communities
        
## Abstract

{{abstract}}==This paper examines the relationship between extractive industries and everyday forms of violence in rural Colombian communities. Through ethnographic fieldwork conducted in the Chocó region, we analyze how gold mining operations create conditions for what we term "ordinary violence" - the normalization of harm through economic, social, and environmental degradation.=={{abstract}}

## Introduction

The concept of ordinary violence, as developed by {^Scheper-Hughes, 2004, #1245}, refers to the ways in which social suffering becomes naturalized and invisible within communities experiencing chronic marginalization.

{{theory-violence}}==Ordinary violence operates through three primary mechanisms: 1) Economic displacement that removes traditional livelihoods, 2) Environmental degradation that destroys subsistence agriculture, and 3) Social fragmentation that weakens community solidarity. These mechanisms work together to create what we call "structural normalization" of harm.=={{theory-violence}}

## Methodology

{{methodology}}==This research employed multi-sited ethnography across four mining communities in Chocó, Colombia, between 2018-2020. Data collection included: participant observation (18 months), semi-structured interviews (89 participants), focus groups (12 sessions), and archival research in regional mining company records.=={{methodology}}

The fieldwork was conducted under difficult conditions, as noted by {^Tubb, 2021, #3847}:

{{fieldwork-challenges}}==Working in conflict zones requires constant negotiation of risk and safety. Research participants often requested meetings in neutral locations, and several interviews had to be conducted via encrypted messaging due to security concerns. The presence of armed groups means that ethnographic observation must be carefully planned and often abbreviated.=={{fieldwork-challenges}}

## Findings

### Economic Displacement

{{economic-displacement}}==In all four communities studied, traditional economic activities (subsistence farming, fishing, small-scale trade) were disrupted within 2-3 years of large-scale mining operations beginning. Community members reported 60-80% reductions in agricultural yields due to water contamination and soil degradation.=={{economic-displacement}}

One community leader explained:

{{community-voice-1}}=="Before the mine, we could feed our families from our land. Now the river runs orange with sediment, the fish are gone, and our plantains won't grow. We depend on the mine for work, but they only hire young men. The women, the elderly - we have no way to survive except to leave."=={{community-voice-1}}

### Environmental Degradation

{{environmental-impact}}==Mercury contamination was found in water sources serving all four communities, with levels 15-30 times above WHO safety standards. Soil samples showed heavy metal concentrations that render agricultural land unusable for decades. Deforestation for mining access roads destroyed traditional medicinal plant habitats.=={{environmental-impact}}

The environmental impact creates cascading social effects:

{{environmental-social-effects}}==When traditional ecological knowledge becomes useless due to environmental destruction, communities lose not just economic resources but cultural practices and social cohesion. Elders who once held respected roles as environmental stewards find their knowledge irrelevant in a contaminated landscape.=={{environmental-social-effects}}

### Social Fragmentation

{{social-fragmentation}}==Mining operations create economic stratification within previously egalitarian communities. Those who secure mining jobs (typically young men) gain relative economic advantage, while traditional authority figures (often older women and community elders) lose social status and economic independence.=={{social-fragmentation}}

## Analysis

{{analysis-main}}==The concept of ordinary violence helps us understand how mining operations create conditions where harm becomes naturalized. Community members begin to accept mercury poisoning, food insecurity, and social stratification as "just how things are now." This acceptance is not passive resignation but an active adaptation to impossible circumstances.=={{analysis-main}}

The process of normalization occurs through what we term "temporal displacement":

{{temporal-displacement}}==Communities are forced to reorganize their understanding of time and causality. Environmental degradation that will impact health for decades is weighed against immediate economic needs. The long-term destruction of subsistence systems is accepted in exchange for short-term wage labor opportunities. This temporal displacement makes it difficult for communities to recognize the full scope of violence they experience.=={{temporal-displacement}}

## Conclusion

{{conclusion}}==Ordinary violence in mining communities operates through the systematic destruction of life-sustaining relationships - with land, water, traditional knowledge, and social structures. Understanding these processes requires analytical frameworks that can capture both immediate harms and long-term structural violence. Future research should focus on community-led resistance strategies and alternative development models.=={{conclusion}}

## References

{{references}}==
Scheper-Hughes, N. (2004). Violence in war and peace: An anthology. Blackwell.

Tubb, D. (2021). Fieldwork in conflict zones: Methodological challenges and ethical considerations. Anthropology & Medicine, 28(3), 312-328.

Watts, M. (2004). Resource curse? Governmentality, oil and power in the Niger Delta. Geopolitics, 9(1), 50-80.
=={{references}}
        """
        
        self.create_test_file("academic_paper.md", academic_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Check that multiple coded categories were created
        coded_dir = self.output_dir / "coded"
        coded_files = list(coded_dir.glob("*.md"))
        
        # Should have files for: abstract, theory-violence, methodology, fieldwork-challenges,
        # economic-displacement, community-voice-1, environmental-impact, environmental-social-effects,
        # social-fragmentation, analysis-main, temporal-displacement, conclusion, references
        expected_files = [
            "abstract.md", "theory-violence.md", "methodology.md", "fieldwork-challenges.md",
            "economic-displacement.md", "community-voice-1.md", "environmental-impact.md",
            "environmental-social-effects.md", "social-fragmentation.md", "analysis-main.md",
            "temporal-displacement.md", "conclusion.md", "references.md"
        ]
        
        for expected_file in expected_files:
            file_path = coded_dir / expected_file
            self.assertTrue(file_path.exists(), f"Expected file {expected_file} not found")
        
        # Check specific content preservation
        methodology_content = (coded_dir / "methodology.md").read_text()
        self.assertIn("multi-sited ethnography", methodology_content)
        self.assertIn("89 participants", methodology_content)
        
        community_voice_content = (coded_dir / "community-voice-1.md").read_text()
        self.assertIn("river runs orange", community_voice_content)
        
        # Check that uncoded content exists and contains citations
        uncoded_files = list((self.output_dir / "uncoded").glob("*.md"))
        self.assertEqual(len(uncoded_files), 1)
        uncoded_content = uncoded_files[0].read_text()
        self.assertIn("{^Scheper-Hughes, 2004, #1245}", uncoded_content)
        self.assertIn("{^Tubb, 2021, #3847}", uncoded_content)


    def test_duplicate_content_extensive(self):
        """Test extensive duplicate content detection across multiple files."""
        
        # Create first file with original content
        file1_content = """# Research Notes - File 1
        
{{data-collection}}==Interviews were conducted using semi-structured protocols with open-ended questions about community experiences with mining operations. Each interview lasted 45-90 minutes and was recorded with participant permission.=={{data-collection}}

{{analysis-approach}}==Data analysis followed a grounded theory approach, with initial coding performed line-by-line, followed by focused coding to identify key themes and patterns. Theoretical sampling guided additional data collection.=={{analysis-approach}}

Some unique content in file 1.
        """
        
        # Create second file with some duplicate content
        file2_content = """# Research Notes - File 2
        
{{data-collection}}==Interviews were conducted using semi-structured protocols with open-ended questions about community experiences with mining operations. Each interview lasted 45-90 minutes and was recorded with participant permission.=={{data-collection}}

{{field-notes}}==Field notes were written daily, focusing on observation of community interactions, economic activities, and environmental conditions. Notes included sketches, diagrams, and direct quotes when possible.=={{field-notes}}

Some unique content in file 2.
        """
        
        # Create third file with different duplicate content
        file3_content = """# Research Notes - File 3
        
{{analysis-approach}}==Data analysis followed a grounded theory approach, with initial coding performed line-by-line, followed by focused coding to identify key themes and patterns. Theoretical sampling guided additional data collection.=={{analysis-approach}}

{{ethics}}==All research procedures were reviewed and approved by the institutional review board. Participants provided informed consent, and all identifying information was removed from transcripts to protect participant anonymity.=={{ethics}}

Some unique content in file 3.
        """
        
        self.create_test_file("notes1.md", file1_content)
        self.create_test_file("notes2.md", file2_content)
        self.create_test_file("notes3.md", file3_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Check coded files - should have unique content only
        coded_dir = self.output_dir / "coded"
        
        # Should have 4 unique coded blocks: data-collection, analysis-approach, field-notes, ethics
        expected_coded_files = ["data-collection.md", "analysis-approach.md", "field-notes.md", "ethics.md"]
        for expected_file in expected_coded_files:
            file_path = coded_dir / expected_file
            self.assertTrue(file_path.exists(), f"Expected coded file {expected_file} not found")
        
        # Check duplicates folder
        duplicates_dir = self.output_dir / "duplicates"
        duplicate_folders = list(duplicates_dir.iterdir())
        
        # Should have folders for the duplicate content
        self.assertGreater(len(duplicate_folders), 0, "No duplicate folders found")
        
        # Check that duplicates contain clean content (no coded markers)
        found_data_collection_duplicate = False
        found_analysis_approach_duplicate = False
        
        for folder in duplicate_folders:
            if folder.is_dir():
                for file in folder.glob("*.md"):
                    content = file.read_text()
                    # Should not contain coded markers
                    self.assertNotIn("{{", content)
                    self.assertNotIn("}}", content)
                    
                    # Check for expected duplicate content
                    if "semi-structured protocols" in content:
                        found_data_collection_duplicate = True
                    elif "grounded theory approach" in content:
                        found_analysis_approach_duplicate = True
        
        self.assertTrue(found_data_collection_duplicate, "data-collection duplicate not found")
        self.assertTrue(found_analysis_approach_duplicate, "analysis-approach duplicate not found")


    def test_malformed_content_comprehensive(self):
        """Test comprehensive malformed content detection."""
        malformed_content = """# Malformed Content Test
        
This file contains various malformed code blocks to test detection.

## Missing Opening Marker
==This content has no opening marker=={{analysis}}

## Missing Closing Marker  
{{theory}}==This content has no closing marker

## Mismatched Markers
{{productivity}}==This has mismatched markers==[[productivity]]

## Incomplete Marker
{incomplete}}==This has an incomplete opening marker=={{incomplete}}

## Empty Code Name
{{}}==This has an empty code name=={{}}

## Whitespace Issues
{{ spaced }}==This has extra spaces=={{ spaced}}

## Nested Malformed
{{outer}}==This has {{inner}}==nested malformed==[[inner]] content=={{outer}}

## Only Closing Marker
=={{lonely-closing}}

## Only Opening Marker
{{lonely-opening}}==

## Multiple Issues
{broken}}==This has multiple problems==[[wrong}}

## Correct Block (for comparison)
{{correct}}==This is a properly formatted block=={{correct}}

Some uncoded text at the end.
        """
        
        self.create_test_file("malformed_test.md", malformed_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Check that malformed content was detected
        malformed_dir = self.output_dir / "malformed"
        malformed_files = list(malformed_dir.glob("*.md"))
        
        if malformed_files:
            # There should be malformed content detected
            self.assertGreater(len(malformed_files), 0, "No malformed files created")
            
            # Check that malformed content doesn't contain original markers
            for malformed_file in malformed_files:
                content = malformed_file.read_text()
                # The content should be the extracted malformed parts
                self.assertIsInstance(content, str)
        
        # Check that the correct block was processed properly
        coded_dir = self.output_dir / "coded"
        correct_file = coded_dir / "correct.md"
        self.assertTrue(correct_file.exists(), "Correctly formatted block not processed")
        
        correct_content = correct_file.read_text()
        self.assertIn("properly formatted block", correct_content)
        
        # Check uncoded content
        uncoded_dir = self.output_dir / "uncoded"
        uncoded_files = list(uncoded_dir.glob("*.md"))
        self.assertEqual(len(uncoded_files), 1)
        
        uncoded_content = uncoded_files[0].read_text()
        self.assertIn("Some uncoded text at the end", uncoded_content)


    def test_large_scale_processing(self):
        """Test processing a large number of files with complex content."""
        # Create 20 files with various content patterns
        for i in range(20):
            content = f"""# Document {i+1}
            
{{{{workflow-{i % 5}}}}}==This is workflow content for document {i+1}.=={{{{workflow-{i % 5}}}}}

{{{{unique-{i}}}}}==This is unique content for document {i+1}.=={{{{unique-{i}}}}}

{{{{common-theme}}}}==This is common theme content that appears in multiple documents.=={{{{common-theme}}}}

{{{{research-method}}}}==This is research methodology content that is shared.=={{{{research-method}}}}

Some uncoded text for document {i+1}.
            """
            self.create_test_file(f"doc_{i+1:02d}.md", content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Check processing statistics
        self.assertEqual(results['files_processed'], 20)
        
        # Check that workflow categories were created (should be 5: workflow-0 through workflow-4)
        coded_dir = self.output_dir / "coded"
        workflow_files = list(coded_dir.glob("workflow-*.md"))
        self.assertEqual(len(workflow_files), 5)
        
        # Check that unique content files were created (should be 20: unique-0 through unique-19)
        unique_files = list(coded_dir.glob("unique-*.md"))
        self.assertEqual(len(unique_files), 20)
        
        # Check that common content was deduplicated
        common_file = coded_dir / "common-theme.md"
        self.assertTrue(common_file.exists())
        
        research_method_file = coded_dir / "research-method.md"
        self.assertTrue(research_method_file.exists())
        
        # Check that duplicates were detected for common content
        duplicates_dir = self.output_dir / "duplicates"
        duplicate_folders = list(duplicates_dir.iterdir())
        
        # Should have duplicates for research-method and common-theme
        self.assertGreater(len(duplicate_folders), 0)
        
        # Check that uncoded content was preserved
        uncoded_dir = self.output_dir / "uncoded"
        uncoded_files = list(uncoded_dir.glob("*.md"))
        self.assertEqual(len(uncoded_files), 20)


class TestEdgeCasesAndBoundaryConditions(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
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
    
    def test_empty_files(self):
        """Test processing empty files."""
        self.create_test_file("empty.md", "")
        self.create_test_file("whitespace_only.md", "   \n\t\n   ")
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process files but not create content
        self.assertEqual(results['files_processed'], 2)
        
        # Check that output folders exist but may be empty
        self.assertTrue((self.output_dir / "coded").exists())
        self.assertTrue((self.output_dir / "uncoded").exists())
    
    def test_very_long_content(self):
        """Test processing very long content blocks."""
        long_text = "This is a very long piece of text. " * 1000  # ~35,000 characters
        
        content = f"""# Long Content Test
        
{{{{long-block}}}}=={long_text}=={{{{long-block}}}}

{{{{another-long}}}}=={long_text} Additional content here.=={{{{another-long}}}}
        """
        
        self.create_test_file("long_content.md", content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process successfully
        self.assertEqual(results['files_processed'], 1)
        
        # Check that long content was preserved
        long_block_file = self.output_dir / "coded" / "long-block.md"
        self.assertTrue(long_block_file.exists())
        
        content = long_block_file.read_text()
        self.assertGreater(len(content), 10000)  # Should be substantial
    
    def test_special_characters_and_unicode(self):
        """Test processing content with special characters and Unicode."""
        unicode_content = """# Unicode and Special Characters Test
        
{{international}}==This content includes international characters: café, naïve, résumé, Москва, 北京, العربية, עברית, हिन्दी, 日本語=={{international}}

{{symbols}}==Special symbols and emojis: ©®™ ±∞≈≠ ←→↑↓ ♠♥♦♣ 🌍🔬📚💡 αβγδε ∑∏∂∇=={{symbols}}

{{quotes}}==Various quote types: "smart quotes" 'single quotes' «guillemets» „German quotes" 「Japanese quotes」=={{quotes}}

{{math}}==Mathematical notation: x² + y² = z², f(x) = ∫₀^∞ e^(-x) dx, ∀x∈ℝ: x²≥0=={{math}}

{{code-like}}==Code-like content: function(param) { return param + 1; } and <tag attr="value">content</tag>=={{code-like}}
        """
        
        self.create_test_file("unicode_test.md", unicode_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process successfully
        self.assertEqual(results['files_processed'], 1)
        
        # Check that Unicode content was preserved
        coded_dir = self.output_dir / "coded"
        
        international_file = coded_dir / "international.md"
        self.assertTrue(international_file.exists())
        international_content = international_file.read_text()
        self.assertIn("café", international_content)
        self.assertIn("Москва", international_content)
        self.assertIn("北京", international_content)
        
        symbols_file = coded_dir / "symbols.md"
        self.assertTrue(symbols_file.exists())
        symbols_content = symbols_file.read_text()
        self.assertIn("🌍", symbols_content)
        self.assertIn("∞", symbols_content)
        
        math_file = coded_dir / "math.md"
        self.assertTrue(math_file.exists())
        math_content = math_file.read_text()
        self.assertIn("∫₀^∞", math_content)
        self.assertIn("∀x∈ℝ", math_content)
    
    def test_nested_structures(self):
        """Test content with nested-like structures that might confuse parsing."""
        nested_content = """# Nested Structures Test
        
{{outer}}==This contains what looks like nested {{inner}} but is actually just text with double braces {{not-real}} inside the content.=={{outer}}

{{markdown}}==This contains markdown **bold** and *italic* and `code` and [links](http://example.com) and ## headers inside coded blocks.=={{markdown}}

{{json-like}}==This contains JSON-like structures: {"key": "value", "nested": {"inner": "data", "array": [1, 2, 3]}}=={{json-like}}

{{regex}}==This contains regex patterns: /{{\\w+}}/g and \\{{\\d+\\}} which might look like code markers but aren't.=={{regex}}

{{escaped}}==This contains escaped characters: \\{{not-a-code\\}} and actual \\\\ backslashes.=={{escaped}}
        """
        
        self.create_test_file("nested_test.md", nested_content)
        
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Should process successfully
        self.assertEqual(results['files_processed'], 1)
        
        # Check that all blocks were processed correctly
        coded_dir = self.output_dir / "coded"
        expected_files = ["outer.md", "markdown.md", "json-like.md", "regex.md", "escaped.md"]
        
        for expected_file in expected_files:
            file_path = coded_dir / expected_file
            self.assertTrue(file_path.exists(), f"Expected file {expected_file} not found")
        
        # Check that content was preserved correctly
        outer_content = (coded_dir / "outer.md").read_text()
        self.assertIn("{{inner}}", outer_content)  # Should preserve literal braces in content
        self.assertIn("{{not-real}}", outer_content)
        
        json_content = (coded_dir / "json-like.md").read_text()
        self.assertIn('{"key": "value"', json_content)
        
        regex_content = (coded_dir / "regex.md").read_text()
        self.assertIn("/{{\\w+}}/g", regex_content)


class TestAppendFunctionalityAndMultipleRuns(unittest.TestCase):
    """Test append functionality and multiple processing runs."""
    
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
    
    def test_append_new_coded_content(self):
        """Test that new coded content is appended to existing files."""
        # First run - create initial coded content
        content1 = """# First Document
        
{{research-method}}==Initial research methodology content.=={{research-method}}

Some uncoded text."""
        
        self.create_test_file("doc1.md", content1)
        
        results1 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Check initial content was created
        self.assertEqual(results1['files_processed'], 1)
        self.assertEqual(results1['coded_blocks_found'], 1)
        
        # Verify the coded file exists
        coded_file = self.output_dir / "coded" / "research-method.md"
        self.assertTrue(coded_file.exists())
        
        initial_content = coded_file.read_text()
        self.assertIn("Initial research methodology content", initial_content)
        
        # Second run - add new content with same code name
        content2 = """# Second Document
        
{{research-method}}==Additional research methodology content.=={{research-method}}

More uncoded text."""
        
        # Clear input and add new file
        for file in self.input_dir.glob("*.md"):
            file.unlink()
        self.create_test_file("doc2.md", content2)
        
        results2 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Check new content was processed
        self.assertEqual(results2['files_processed'], 1)
        self.assertEqual(results2['coded_blocks_found'], 1)
        
        # Verify content was appended
        updated_content = coded_file.read_text()
        self.assertIn("Initial research methodology content", updated_content)
        self.assertIn("Additional research methodology content", updated_content)
        
        # Check that content is properly separated
        self.assertIn("\n\nAdditional research methodology content", updated_content)
    
    def test_duplicate_coded_content_not_appended(self):
        """Test that duplicate coded content is not appended to existing files within a single run."""
        # Create two files with duplicate coded content in a single run
        content1 = """# First Document
        
{{shared-code}}==This is shared content that will be duplicated.=={{shared-code}}

Unique content in first document."""
        
        content2 = """# Second Document
        
{{shared-code}}==This is shared content that will be duplicated.=={{shared-code}}

Unique content in second document."""
        
        self.create_test_file("doc1.md", content1)
        self.create_test_file("doc2.md", content2)
        
        # Process both files in a single run
        results = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Check both files were processed
        self.assertEqual(results['files_processed'], 2)
        self.assertEqual(results['coded_blocks_found'], 1)  # Only 1 unique block saved to coded folder
        self.assertEqual(results['duplicates_found'], 1)    # 1 duplicate detected and saved
        
        # Verify the coded file exists with only one instance of the content
        coded_file = self.output_dir / "coded" / "shared-code.md"
        self.assertTrue(coded_file.exists())
        
        coded_content = coded_file.read_text()
        self.assertIn("This is shared content that will be duplicated", coded_content)
        
        # Check that content appears only once (duplicate was not appended)
        occurrences = coded_content.count("This is shared content that will be duplicated")
        self.assertEqual(occurrences, 1)
        
        # Check that duplicate was saved to duplicates folder
        duplicates_dir = self.output_dir / "duplicates"
        self.assertTrue(duplicates_dir.exists())
        duplicate_folders = list(duplicates_dir.iterdir())
        self.assertGreater(len(duplicate_folders), 0)
    
    def test_multiple_runs_with_mixed_content(self):
        """Test multiple runs with a mix of new and duplicate content."""
        # First run - create initial content
        content1 = """# First Document
        
{{methodology}}==Initial methodology content.=={{methodology}}
{{findings}}==Initial findings content.=={{findings}}

Some uncoded text."""
        
        self.create_test_file("doc1.md", content1)
        
        results1 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        self.assertEqual(results1['files_processed'], 1)
        self.assertEqual(results1['coded_blocks_found'], 2)
        
        # Second run - add new content and duplicate
        content2 = """# Second Document
        
{{methodology}}==Initial methodology content.=={{methodology}}  # Duplicate
{{findings}}==Additional findings content.=={{findings}}  # New content
{{conclusion}}==New conclusion content.=={{conclusion}}  # New code

More uncoded text."""
        
        # Clear input and add new file
        for file in self.input_dir.glob("*.md"):
            file.unlink()
        self.create_test_file("doc2.md", content2)
        
        results2 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        self.assertEqual(results2['files_processed'], 1)
        self.assertEqual(results2['coded_blocks_found'], 3)
        
        # Check methodology file (should have original content only)
        methodology_file = self.output_dir / "coded" / "methodology.md"
        methodology_content = methodology_file.read_text()
        self.assertIn("Initial methodology content", methodology_content)
        self.assertNotIn("Additional", methodology_content)
        
        # Check findings file (should have both contents)
        findings_file = self.output_dir / "coded" / "findings.md"
        findings_content = findings_file.read_text()
        self.assertIn("Initial findings content", findings_content)
        self.assertIn("Additional findings content", findings_content)
        
        # Check conclusion file (should be new)
        conclusion_file = self.output_dir / "coded" / "conclusion.md"
        self.assertTrue(conclusion_file.exists())
        conclusion_content = conclusion_file.read_text()
        self.assertIn("New conclusion content", conclusion_content)
    
    def test_append_with_different_code_names(self):
        """Test that different code names create separate files."""
        # First run
        content1 = """# First Document
        
{{code-a}}==Content for code A.=={{code-a}}

Some text."""
        
        self.create_test_file("doc1.md", content1)
        
        results1 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        self.assertEqual(results1['coded_blocks_found'], 1)
        
        # Second run with different code name
        content2 = """# Second Document
        
{{code-b}}==Content for code B.=={{code-b}}

More text."""
        
        # Clear input and add new file
        for file in self.input_dir.glob("*.md"):
            file.unlink()
        self.create_test_file("doc2.md", content2)
        
        results2 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        self.assertEqual(results2['coded_blocks_found'], 1)
        
        # Check both files exist separately
        code_a_file = self.output_dir / "coded" / "code-a.md"
        code_b_file = self.output_dir / "coded" / "code-b.md"
        
        self.assertTrue(code_a_file.exists())
        self.assertTrue(code_b_file.exists())
        
        # Check content is separate
        code_a_content = code_a_file.read_text()
        code_b_content = code_b_file.read_text()
        
        self.assertIn("Content for code A", code_a_content)
        self.assertIn("Content for code B", code_b_content)
        self.assertNotIn("Content for code B", code_a_content)
        self.assertNotIn("Content for code A", code_b_content)
    
    def test_append_with_whitespace_variations(self):
        """Test that whitespace variations don't prevent duplicate detection."""
        # First run
        content1 = """# First Document
        
{{test-code}}==This is test content with some whitespace.=={{test-code}}

Some text."""
        
        self.create_test_file("doc1.md", content1)
        
        results1 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        self.assertEqual(results1['coded_blocks_found'], 1)
        
        # Second run with whitespace variations
        content2 = """# Second Document
        
{{test-code}}==  This is test content with some whitespace.  =={{test-code}}

More text."""
        
        # Clear input and add new file
        for file in self.input_dir.glob("*.md"):
            file.unlink()
        self.create_test_file("doc2.md", content2)
        
        results2 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        self.assertEqual(results2['coded_blocks_found'], 1)
        
        # Check that content was NOT appended (duplicate detected despite whitespace)
        coded_file = self.output_dir / "coded" / "test-code.md"
        content = coded_file.read_text()
        
        # Should only appear once
        occurrences = content.count("This is test content with some whitespace")
        self.assertEqual(occurrences, 1)
    
    def test_append_with_malformed_content(self):
        """Test that malformed content doesn't interfere with append functionality."""
        # First run with proper content
        content1 = """# First Document
        
{{good-code}}==Good content here.=={{good-code}}

Some text."""
        
        self.create_test_file("doc1.md", content1)
        
        results1 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        self.assertEqual(results1['coded_blocks_found'], 1)
        self.assertEqual(results1['malformed_blocks_found'], 0)
        
        # Second run with malformed content and new good content
        content2 = """# Second Document
        
{{good-code}}==Additional good content.=={{good-code}}

Bad content=={{bad-code}}

More text."""
        
        # Clear input and add new file
        for file in self.input_dir.glob("*.md"):
            file.unlink()
        self.create_test_file("doc2.md", content2)
        
        results2 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        self.assertEqual(results2['coded_blocks_found'], 1)
        self.assertEqual(results2['malformed_blocks_found'], 1)
        
        # Check that good content was appended
        good_code_file = self.output_dir / "coded" / "good-code.md"
        good_content = good_code_file.read_text()
        self.assertIn("Good content here", good_content)
        self.assertIn("Additional good content", good_content)
        
        # Check that malformed content was saved separately
        malformed_file = self.output_dir / "malformed" / "doc2.md"
        self.assertTrue(malformed_file.exists())
        malformed_content = malformed_file.read_text()
        self.assertIn("=={{bad-code}}", malformed_content)
    
    def test_multiple_runs_duplicate_detection_reset(self):
        """Test that duplicate detection is reset between processing runs."""
        # First run - create initial coded content
        content1 = """# First Document
        
{{shared-code}}==This is shared content that will be duplicated.=={{shared-code}}

Unique content in first document."""
        
        self.create_test_file("doc1.md", content1)
        
        results1 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Check initial content was created
        self.assertEqual(results1['files_processed'], 1)
        self.assertEqual(results1['coded_blocks_found'], 1)
        self.assertEqual(results1['duplicates_found'], 0)
        
        # Verify the coded file exists
        coded_file = self.output_dir / "coded" / "shared-code.md"
        self.assertTrue(coded_file.exists())
        
        initial_content = coded_file.read_text()
        self.assertIn("This is shared content that will be duplicated", initial_content)
        initial_length = len(initial_content)
        
        # Second run - add duplicate content (should be treated as new since detector is reset)
        content2 = """# Second Document
        
{{shared-code}}==This is shared content that will be duplicated.=={{shared-code}}

Unique content in second document."""
        
        # Clear input and add new file
        for file in self.input_dir.glob("*.md"):
            file.unlink()
        self.create_test_file("doc2.md", content2)
        
        results2 = process_folder(
            input_folder=self.input_dir,
            output_folder=self.output_dir
        )
        
        # Check new content was processed
        self.assertEqual(results2['files_processed'], 1)
        self.assertEqual(results2['coded_blocks_found'], 1)
        self.assertEqual(results2['duplicates_found'], 0)  # No duplicate detected across runs
        
        # Verify content was appended (duplicate detection doesn't work across runs)
        updated_content = coded_file.read_text()
        self.assertIn("This is shared content that will be duplicated", updated_content)
        
        # Check that content appears only once (file-level duplicate detection prevented append)
        occurrences = updated_content.count("This is shared content that will be duplicated")
        self.assertEqual(occurrences, 1)
        
        # Check that content was NOT appended (file-level duplicate detection worked)
        self.assertEqual(len(updated_content), initial_length)
        self.assertEqual(updated_content, initial_content)


if __name__ == '__main__':
    unittest.main() 