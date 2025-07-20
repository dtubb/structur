"""Text processing utilities."""

import re
from typing import List
import logging

logger = logging.getLogger(__name__)


class TextProcessor:
    """Handles basic text processing operations."""
    
    def __init__(self):
        """Initialize the text processor."""
        pass
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        if not text:
            return ""
        
        # Replace multiple consecutive newlines with double newlines
        normalized = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Strip leading and trailing whitespace
        normalized = normalized.strip()
        
        return normalized
    
    def remove_empty_lines(self, text: str) -> str:
        """
        Remove empty lines from text.
        
        Args:
            text: Input text
            
        Returns:
            Text with empty lines removed
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)
    
    def count_words(self, text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Input text
            
        Returns:
            Number of words
        """
        if not text:
            return 0
        
        # Split on whitespace and filter out empty strings
        words = [word for word in text.split() if word.strip()]
        return len(words)
    
    def extract_lines_range(self, text: str, start_line: int, end_line: int) -> str:
        """
        Extract a range of lines from text.
        
        Args:
            text: Input text
            start_line: Starting line number (1-based)
            end_line: Ending line number (1-based, inclusive)
            
        Returns:
            Extracted lines as string
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        
        # Convert to 0-based indexing
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        if start_idx >= len(lines) or end_idx <= start_idx:
            return ""
        
        return '\n'.join(lines[start_idx:end_idx])
    
    def find_line_numbers(self, text: str, search_pattern: str) -> List[int]:
        """
        Find line numbers where a pattern occurs.
        
        Args:
            text: Input text
            search_pattern: Pattern to search for
            
        Returns:
            List of line numbers (1-based) where pattern is found
        """
        if not text or not search_pattern:
            return []
        
        lines = text.split('\n')
        line_numbers = []
        
        for i, line in enumerate(lines, 1):
            if search_pattern in line:
                line_numbers.append(i)
        
        return line_numbers
    
    def remove_pattern(self, text: str, pattern: str, flags: int = 0) -> str:
        """
        Remove a regex pattern from text.
        
        Args:
            text: Input text
            pattern: Regex pattern to remove
            flags: Regex flags
            
        Returns:
            Text with pattern removed
        """
        if not text:
            return ""
        
        try:
            result = re.sub(pattern, '', text, flags=flags)
            return result
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
            return text
    
    def split_by_pattern(self, text: str, pattern: str, flags: int = 0) -> List[str]:
        """
        Split text by a regex pattern.
        
        Args:
            text: Input text
            pattern: Regex pattern to split on
            flags: Regex flags
            
        Returns:
            List of text segments
        """
        if not text:
            return []
        
        try:
            segments = re.split(pattern, text, flags=flags)
            # Filter out empty segments
            return [segment for segment in segments if segment.strip()]
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
            return [text]
    
    def escape_regex_chars(self, text: str) -> str:
        """
        Escape special regex characters in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with regex characters escaped
        """
        if not text:
            return ""
        
        return re.escape(text)
    
    def is_whitespace_only(self, text: str) -> bool:
        """
        Check if text contains only whitespace.
        
        Args:
            text: Input text
            
        Returns:
            True if text is empty or whitespace only
        """
        return not text or not text.strip()
    
    def clean_line_endings(self, text: str) -> str:
        """
        Normalize line endings to Unix style.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized line endings
        """
        if not text:
            return ""
        
        # Replace Windows and Mac line endings with Unix
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        return text 