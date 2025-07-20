"""Unit tests for the DuplicateDetector module."""

import unittest
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.duplicate_detector import DuplicateDetector


class TestDuplicateDetector(unittest.TestCase):
    """Test cases for DuplicateDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = DuplicateDetector()
    
    def test_first_occurrence_registration(self):
        """Test registering first occurrence of content."""
        content = "This is test content"
        result = self.detector.register_content(content, "file1.md", "test")
        
        self.assertTrue(result)  # Should register successfully
        self.assertEqual(len(self.detector.content_hashes), 1)
    
    def test_duplicate_detection(self):
        """Test detecting duplicate content."""
        content = "This is test content"
        
        # Register first occurrence
        result1 = self.detector.register_content(content, "file1.md", "test")
        self.assertTrue(result1)
        
        # Try to register duplicate
        result2 = self.detector.register_content(content, "file2.md", "test")
        self.assertFalse(result2)  # Should detect as duplicate
        
        self.assertEqual(self.detector.duplicate_count, 1)
    
    def test_case_insensitive_duplicate_detection(self):
        """Test that duplicate detection is case insensitive."""
        content1 = "This is Test Content"
        content2 = "this is test content"
        
        result1 = self.detector.register_content(content1, "file1.md", "test")
        result2 = self.detector.register_content(content2, "file2.md", "test")
        
        self.assertTrue(result1)
        self.assertFalse(result2)  # Should detect as duplicate despite different case
    
    def test_whitespace_normalization(self):
        """Test that duplicate detection normalizes whitespace."""
        content1 = "This is    test content"
        content2 = "This  is test   content"
        
        result1 = self.detector.register_content(content1, "file1.md", "test")
        result2 = self.detector.register_content(content2, "file2.md", "test")
        
        self.assertTrue(result1)
        self.assertFalse(result2)  # Should detect as duplicate despite different whitespace
    
    def test_get_first_occurrence(self):
        """Test getting first occurrence information."""
        content = "This is test content"
        
        self.detector.register_content(content, "file1.md", "test")
        first_occurrence = self.detector.get_first_occurrence(content)
        
        self.assertIsNotNone(first_occurrence)
        self.assertEqual(first_occurrence, ("file1.md", "test"))
    
    def test_check_against_existing_files(self):
        """Test checking content against existing files."""
        existing_files = {
            "file1.md": "This is existing content in file1",
            "file2.md": "This is existing content in file2"
        }
        
        # Content that exists in file1
        content1 = "existing content in file1"
        result1 = self.detector.check_against_existing_files(content1, existing_files)
        self.assertTrue(result1)
        
        # Content that doesn't exist
        content2 = "brand new content"
        result2 = self.detector.check_against_existing_files(content2, existing_files)
        self.assertFalse(result2)
    
    def test_empty_content_handling(self):
        """Test handling of empty or whitespace-only content."""
        empty_content = ""
        whitespace_content = "   \n\t   "
        
        result1 = self.detector.register_content(empty_content, "file1.md", "test")
        result2 = self.detector.register_content(whitespace_content, "file2.md", "test")
        
        self.assertFalse(result1)  # Should reject empty content
        self.assertFalse(result2)  # Should reject whitespace-only content
    
    def test_duplicate_stats(self):
        """Test getting duplicate statistics."""
        content1 = "Content 1"
        content2 = "Content 2"
        content3 = "Content 1"  # Duplicate of content1
        
        self.detector.register_content(content1, "file1.md", "test1")
        self.detector.register_content(content2, "file2.md", "test2")
        self.detector.register_content(content3, "file3.md", "test3")
        
        stats = self.detector.get_duplicate_stats()
        
        self.assertEqual(stats["total_content_registered"], 2)  # Only unique content
        self.assertEqual(stats["duplicate_count"], 1)
        self.assertEqual(stats["unique_content_count"], 2)
    
    def test_reset_functionality(self):
        """Test resetting the detector state."""
        content = "Test content"
        self.detector.register_content(content, "file1.md", "test")
        
        # Verify state before reset
        self.assertEqual(len(self.detector.content_hashes), 1)
        
        # Reset and verify
        self.detector.reset()
        self.assertEqual(len(self.detector.content_hashes), 0)
        self.assertEqual(len(self.detector.seen_content), 0)
        self.assertEqual(self.detector.duplicate_count, 0)
    
    def test_content_hash_generation(self):
        """Test content hash generation."""
        content1 = "This is test content"
        content2 = "This is test content"  # Same content
        content3 = "This is different content"
        
        hash1 = self.detector.generate_content_hash(content1)
        hash2 = self.detector.generate_content_hash(content2)
        hash3 = self.detector.generate_content_hash(content3)
        
        self.assertEqual(hash1, hash2)  # Same content should have same hash
        self.assertNotEqual(hash1, hash3)  # Different content should have different hash
    
    def test_export_duplicate_map(self):
        """Test exporting duplicate map for debugging."""
        content1 = "Content 1"
        content2 = "Content 2"
        
        self.detector.register_content(content1, "file1.md", "test1")
        self.detector.register_content(content2, "file2.md", "test2")
        
        export_data = self.detector.export_duplicate_map()
        
        self.assertIn("content_hashes", export_data)
        self.assertIn("stats", export_data)
        self.assertEqual(len(export_data["content_hashes"]), 2)


if __name__ == "__main__":
    unittest.main() 