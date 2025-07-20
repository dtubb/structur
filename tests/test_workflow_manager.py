"""Unit tests for workflow manager."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.managers.workflow_manager import WorkflowManager
from src.models.config import ProcessingConfig
from pathlib import Path


class TestWorkflowManager(unittest.TestCase):
    """Test cases for workflow manager logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = ProcessingConfig(
            input_folder=Path("test_input"),
            output_base=Path("test_output")
        )
        self.workflow_manager = WorkflowManager(self.config)
    
    @patch('src.managers.workflow_manager.FolderManager')
    def test_initialization(self, mock_folder_manager):
        """Test workflow manager initialization."""
        manager = WorkflowManager(self.config)
        self.assertEqual(manager.config, self.config)
        self.assertIsNotNone(manager.file_manager)
        self.assertIsNotNone(manager.duplicate_detector)
        self.assertIsNotNone(manager.code_extractor)
        self.assertIsNotNone(manager.malformed_detector)
        self.assertIsNotNone(manager.content_filter)
    
    def test_file_processing_flow(self):
        """Test the complete file processing flow."""
        # Mock all dependencies
        self.workflow_manager.folder_manager = Mock()
        self.workflow_manager.code_extractor = Mock()
        self.workflow_manager.malformed_detector = Mock()
        self.workflow_manager.content_filter = Mock()
        self.workflow_manager.duplicate_detector = Mock()
        self.workflow_manager.file_manager = Mock()
        
        # Mock file content
        test_content = """Normal text.
{{code}}==Coded content.=={{code}}
Malformed=={{bad}}
More normal text."""
        
        # Mock file operations
        self.workflow_manager.file_manager.read_file_content.return_value = test_content
        
        # Mock return values with proper types
        coded_block = Mock()
        coded_block.code = "code"
        coded_block.content = "Coded content."
        self.workflow_manager.code_extractor.find_all_coded_blocks.return_value = [coded_block]
        
        # Mock the group_blocks_by_code method
        self.workflow_manager.code_extractor.group_blocks_by_code.return_value = {"code": [coded_block]}
        
        malformed_block = Mock()
        malformed_block.content = "=={{bad}}"
        malformed_block.issue_type = "closing_only"
        self.workflow_manager.malformed_detector.find_all_malformed_blocks.return_value = [malformed_block]
        
        self.workflow_manager.content_filter.extract_uncoded_content.return_value = "Normal text.\nMore normal text."
        self.workflow_manager.duplicate_detector.register_content.return_value = True
        
        # Mock folder manager methods
        self.workflow_manager.folder_manager.append_content_to_folder.return_value = None
        
        # Test file processing
        test_file = Path("test.md")
        result = self.workflow_manager.process_single_file(test_file)
        
        # Verify processing was successful
        self.assertTrue(result)
        
        # Verify all processing steps were called
        self.workflow_manager.file_manager.read_file_content.assert_called_once_with(test_file)
        self.workflow_manager.code_extractor.find_all_coded_blocks.assert_called_once()
        self.workflow_manager.malformed_detector.find_all_malformed_blocks.assert_called_once()
        self.workflow_manager.content_filter.extract_uncoded_content.assert_called_once()
    
    def test_coded_content_processing(self):
        """Test processing of coded content."""
        self.workflow_manager.folder_manager = Mock()
        self.workflow_manager.duplicate_detector = Mock()
        self.workflow_manager.duplicate_detector.register_content.return_value = True
        
        # Test with properly formatted coded content
        content = "{{test-code}}==Test content.=={{test-code}}"
        self.workflow_manager._process_coded_content(content, "test.md")
        
        # Should attempt to save coded content
        self.workflow_manager.folder_manager.append_content_to_folder.assert_called()
    
    def test_malformed_content_processing(self):
        """Test processing of malformed content."""
        self.workflow_manager.folder_manager = Mock()
        self.workflow_manager.malformed_detector = Mock()
        self.workflow_manager.duplicate_detector = Mock()
        
        # Mock malformed block
        malformed_block = Mock()
        malformed_block.content = "malformed content=={{bad}}"
        malformed_block.issue_type = "closing_only"
        
        self.workflow_manager.malformed_detector.find_all_malformed_blocks.return_value = [malformed_block]
        self.workflow_manager.duplicate_detector.register_content.return_value = True
        
        content = "Normal text. Malformed content=={{bad}}"
        self.workflow_manager._process_malformed_content(content, "test.md")
        
        # Should process malformed content
        self.workflow_manager.malformed_detector.find_all_malformed_blocks.assert_called_once_with(content, "test.md")
        self.workflow_manager.folder_manager.append_content_to_folder.assert_called()
    
    def test_uncoded_content_processing(self):
        """Test processing of uncoded content (subtractive approach)."""
        self.workflow_manager.folder_manager = Mock()
        self.workflow_manager.content_filter = Mock()
        self.workflow_manager.duplicate_detector = Mock()
        
        # Mock the subtractive filtering
        original_content = """Normal text.
{{code}}==Remove this.=={{code}}
More normal text.
Malformed=={{bad}}
Final text."""
        
        expected_uncoded = """Normal text.
More normal text.
Final text."""
        
        self.workflow_manager.content_filter.extract_uncoded_content.return_value = expected_uncoded
        self.workflow_manager.duplicate_detector.register_content.return_value = True
        
        self.workflow_manager._process_uncoded_content(original_content, "test.md")
        
        # Verify subtractive approach is used
        self.workflow_manager.content_filter.extract_uncoded_content.assert_called_once_with(original_content)
        self.workflow_manager.folder_manager.append_content_to_folder.assert_called_with('uncoded', 'test.md', expected_uncoded)
    
    def test_duplicate_detection_flow(self):
        """Test duplicate detection and handling."""
        self.workflow_manager.folder_manager = Mock()
        self.workflow_manager.duplicate_detector = Mock()
        
        # Test duplicate content (returns False from register_content)
        self.workflow_manager.duplicate_detector.register_content.return_value = False
        
        # Mock the duplicate saving method
        self.workflow_manager._save_duplicate_content = Mock()
        
        content = "Some content"
        self.workflow_manager._process_uncoded_content(content, "test.md")
        
        # Should handle as duplicate
        self.workflow_manager._save_duplicate_content.assert_called_once()
    
    def test_stats_tracking(self):
        """Test that statistics are properly tracked."""
        # Initialize stats
        self.workflow_manager.stats = {
            'files_processed': 0,
            'coded_blocks_found': 0,
            'malformed_blocks_found': 0,
            'duplicates_found': 0
        }
        
        # Mock dependencies
        self.workflow_manager.folder_manager = Mock()
        self.workflow_manager.duplicate_detector = Mock()
        self.workflow_manager.duplicate_detector.register_content.return_value = True
        
        # Test malformed processing
        malformed_block = Mock()
        malformed_block.content = "malformed"
        self.workflow_manager.malformed_detector = Mock()
        self.workflow_manager.malformed_detector.find_all_malformed_blocks.return_value = [malformed_block]
        
        self.workflow_manager._process_malformed_content("content", "test.md")
        
        # Stats should be updated
        self.assertEqual(self.workflow_manager.stats['malformed_blocks_found'], 1)


def mock_open(read_data):
    """Helper to create mock open function."""
    mock = MagicMock()
    mock.return_value.__enter__.return_value.read.return_value = read_data
    return mock


if __name__ == '__main__':
    unittest.main() 