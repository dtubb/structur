"""Content filtering module for removing specific types of content from text."""

import re
from typing import List, Set
from pathlib import Path
import logging

from ..models.text_block import CodedBlock, MalformedBlock
from ..utils.text_utils import TextProcessor
from .code_extractor import CodeExtractor
from .malformed_detector import MalformedDetector

logger = logging.getLogger(__name__)


class ContentFilter:
    """Filters and removes content from text while preserving structure."""
    
    def __init__(self, supported_formats: List[str] = None):
        """
        Initialize the content filter.
        
        Args:
            supported_formats: List of supported code formats (default: ["{{", "[["])
        """
        self.supported_formats = supported_formats or ["{{", "[["]
        self.text_processor = TextProcessor()
        self.code_extractor = CodeExtractor(supported_formats)
        self.malformed_detector = MalformedDetector(supported_formats)
    
    def remove_coded_blocks(self, text: str, preserve_structure: bool = True) -> str:
        """
        Remove all properly formatted coded blocks from text.
        
        Args:
            text: Input text
            preserve_structure: Whether to preserve line structure
            
        Returns:
            Text with coded blocks removed
        """
        if not text:
            return ""
        
        result_text = text
        
        # Get all coded blocks and remove them
        coded_blocks = self.code_extractor.find_all_coded_blocks(text)
        
        # Sort by position (reverse order to maintain positions)
        coded_blocks.sort(key=lambda b: (b.line_start or 0, b.line_end or 0), reverse=True)
        
        for fmt in self.supported_formats:
            if fmt == "{{":
                pattern = r'\{\{\s*(.*?)\s*\}\}\s*==\s*(.*?)\s*==\s*\{\{\s*\1\s*\}\}'
            elif fmt == "[[":
                pattern = r'\[\[\s*(.*?)\s*\]\]\s*==\s*(.*?)\s*==\s*\[\[\s*\1\s*\]\]'
            else:
                continue
            
            try:
                if preserve_structure:
                    # Replace with placeholder to maintain line structure
                    result_text = re.sub(pattern, '', result_text, flags=re.DOTALL)
                else:
                    result_text = re.sub(pattern, '', result_text, flags=re.DOTALL)
            except re.error as e:
                logger.error(f"Error removing coded blocks for format {fmt}: {e}")
        
        return self.text_processor.normalize_whitespace(result_text)
    
    def remove_malformed_blocks(self, text: str, preserve_structure: bool = True) -> str:
        """
        Remove all malformed coded blocks from text.
        
        Args:
            text: Input text
            preserve_structure: Whether to preserve line structure
            
        Returns:
            Text with malformed blocks removed
        """
        if not text:
            return ""
        
        result_text = text
        
        # Get all malformed blocks from the detector
        malformed_blocks = self.malformed_detector.find_all_malformed_blocks(text)
        
        # Remove each malformed block by its exact content
        for block in malformed_blocks:
            if hasattr(block, 'content') and block.content:
                # Remove the exact malformed content
                result_text = result_text.replace(block.content, '')
        
        return self.text_processor.normalize_whitespace(result_text)
    
    def remove_closing_only_malformed(self, text: str) -> str:
        """
        Remove lines that end with closing markers but have no opening.
        
        Args:
            text: Input text
            
        Returns:
            Text with closing-only malformed lines removed
        """
        if not text:
            return ""
        
        # Use the malformed detector to find closing-only malformed blocks
        malformed_blocks = self.malformed_detector.find_closing_only_malformed(text)
        
        result_text = text
        for block in malformed_blocks:
            if hasattr(block, 'content') and block.content:
                # Remove the exact malformed content
                result_text = result_text.replace(block.content, '')
        
        return self.text_processor.normalize_whitespace(result_text)
    
    def extract_uncoded_content(self, text: str) -> str:
        """
        Extract only uncoded content by removing all coded and malformed blocks.
        
        Args:
            text: Input text
            
        Returns:
            Only uncoded content
        """
        if not text:
            return ""
        
        # Start with original text
        result_text = text
        
        # Remove properly formatted coded blocks
        result_text = self.remove_coded_blocks(result_text)
        
        # Remove malformed blocks
        result_text = self.remove_malformed_blocks(result_text)
        
        # Remove closing-only malformed lines
        result_text = self.remove_closing_only_malformed(result_text)
        
        return self.text_processor.normalize_whitespace(result_text)
    
    def extract_clean_text(self, text: str) -> str:
        """
        Extract clean text content by removing all coded markers, malformed blocks, etc.
        This is essentially the same as extract_uncoded_content but with clearer naming
        when used for duplicate content processing.
        
        Args:
            text: Input text that may contain coded markers, malformed blocks, etc.
            
        Returns:
            Clean text with all markup removed
        """
        return self.extract_uncoded_content(text)
    
    def filter_by_codes(self, text: str, codes_to_keep: Set[str]) -> str:
        """
        Keep only content from specific codes, remove everything else.
        
        Args:
            text: Input text
            codes_to_keep: Set of code names to preserve
            
        Returns:
            Text containing only specified codes
        """
        if not text or not codes_to_keep:
            return ""
        
        # Extract all coded blocks
        coded_blocks = self.code_extractor.find_all_coded_blocks(text)
        
        # Filter to only desired codes
        filtered_blocks = [block for block in coded_blocks if block.code in codes_to_keep]
        
        # Combine content from filtered blocks
        content_parts = []
        for block in filtered_blocks:
            content_parts.append(block.content)
        
        return '\n\n'.join(content_parts)
    
    def remove_duplicate_content(self, text: str, known_duplicates: Set[str]) -> str:
        """
        Remove known duplicate content from text.
        
        Args:
            text: Input text
            known_duplicates: Set of content strings that are duplicates
            
        Returns:
            Text with duplicate content removed
        """
        if not text or not known_duplicates:
            return text
        
        result_text = text
        
        # Remove each known duplicate
        for duplicate_content in known_duplicates:
            if duplicate_content.strip():
                # Escape special regex characters
                escaped_content = re.escape(duplicate_content.strip())
                
                # Remove the duplicate content
                try:
                    result_text = re.sub(escaped_content, '', result_text, flags=re.DOTALL)
                except re.error as e:
                    logger.error(f"Error removing duplicate content: {e}")
        
        return self.text_processor.normalize_whitespace(result_text)
    
    def create_clean_copy(self, text: str, 
                         remove_coded: bool = False,
                         remove_malformed: bool = False,
                         remove_duplicates: Set[str] = None) -> str:
        """
        Create a clean copy of text with specified content removed.
        
        Args:
            text: Input text
            remove_coded: Whether to remove coded blocks
            remove_malformed: Whether to remove malformed blocks
            remove_duplicates: Set of duplicate content to remove
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        result_text = text
        
        if remove_coded:
            result_text = self.remove_coded_blocks(result_text)
        
        if remove_malformed:
            result_text = self.remove_malformed_blocks(result_text)
        
        if remove_duplicates:
            result_text = self.remove_duplicate_content(result_text, remove_duplicates)
        
        return self.text_processor.normalize_whitespace(result_text)
    
    def get_filter_stats(self, original_text: str, filtered_text: str) -> dict:
        """
        Get statistics about the filtering operation.
        
        Args:
            original_text: Original text before filtering
            filtered_text: Text after filtering
            
        Returns:
            Dictionary with filtering statistics
        """
        original_words = self.text_processor.count_words(original_text)
        filtered_words = self.text_processor.count_words(filtered_text)
        
        return {
            "original_word_count": original_words,
            "filtered_word_count": filtered_words,
            "words_removed": original_words - filtered_words,
            "removal_percentage": ((original_words - filtered_words) / original_words * 100) if original_words > 0 else 0
        } 