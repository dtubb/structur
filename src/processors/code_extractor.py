"""Code extraction module for finding and parsing coded text blocks."""

import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging

from ..models.text_block import CodedBlock
from ..utils.text_utils import TextProcessor

logger = logging.getLogger(__name__)


class CodeExtractor:
    """Extracts properly formatted coded text blocks."""
    
    def __init__(self, supported_formats: List[str] = None):
        """
        Initialize the code extractor.
        
        Args:
            supported_formats: List of supported code formats (default: ["{{", "[["])
        """
        self.supported_formats = supported_formats or ["{{", "[["]
        self.text_processor = TextProcessor()
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for finding coded blocks."""
        self.patterns = {}
        
        for fmt in self.supported_formats:
            if fmt == "{{":
                pattern = r'\{\{\s*([^}]+)\s*\}\}\s*==\s*(.*?)\s*==\s*\{\{\s*\1\s*\}\}'
            elif fmt == "[[":
                pattern = r'\[\[\s*([^\]]+)\s*\]\]\s*==\s*(.*?)\s*==\s*\[\[\s*\1\s*\]\]'
            else:
                continue
            
            try:
                compiled_pattern = re.compile(pattern, re.DOTALL)
                self.patterns[fmt] = compiled_pattern
                logger.debug(f"Compiled pattern for format {fmt}: {pattern}")
            except re.error as e:
                logger.error(f"Failed to compile pattern for format {fmt}: {e}")
    
    def find_all_coded_blocks(self, text: str, source_file: str = "") -> List[CodedBlock]:
        """
        Find all properly formatted coded blocks in text.
        
        Args:
            text: Text to search
            source_file: Source file path for tracking
            
        Returns:
            List of CodedBlock objects
        """
        if not text:
            return []
        
        coded_blocks = []
        
        for fmt, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            
            for match in matches:
                code = match.group(1).strip()
                content = match.group(2).strip()
                
                if code and content:
                    # Find line numbers for this match
                    line_start, line_end = self._find_line_numbers(text, match.start(), match.end())
                    
                    coded_block = CodedBlock(
                        content=content,
                        source_file=source_file,
                        line_start=line_start,
                        line_end=line_end,
                        code=code,
                        format_type=fmt
                    )
                    
                    coded_blocks.append(coded_block)
                    logger.debug(f"Found coded block: {code} in {source_file}")
        
        return coded_blocks
    
    def extract_code_by_name(self, text: str, code_name: str, source_file: str = "") -> List[CodedBlock]:
        """
        Extract all instances of a specific code from text.
        
        Args:
            text: Text to search
            code_name: Specific code name to extract
            source_file: Source file path for tracking
            
        Returns:
            List of CodedBlock objects with matching code name
        """
        all_blocks = self.find_all_coded_blocks(text, source_file)
        return [block for block in all_blocks if block.code == code_name]
    
    def get_unique_codes(self, text: str) -> List[str]:
        """
        Get list of unique code names found in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of unique code names
        """
        all_blocks = self.find_all_coded_blocks(text)
        codes = {block.code for block in all_blocks}
        return sorted(list(codes))
    
    def group_blocks_by_code(self, blocks: List[CodedBlock]) -> Dict[str, List[CodedBlock]]:
        """
        Group coded blocks by their code name.
        
        Args:
            blocks: List of coded blocks
            
        Returns:
            Dictionary mapping code names to lists of blocks
        """
        grouped = {}
        
        for block in blocks:
            if block.code not in grouped:
                grouped[block.code] = []
            grouped[block.code].append(block)
        
        return grouped
    
    def validate_code_block(self, text: str, start_pos: int, end_pos: int) -> bool:
        """
        Validate that a text range contains a properly formatted code block.
        
        Args:
            text: Full text
            start_pos: Start position of potential block
            end_pos: End position of potential block
            
        Returns:
            True if valid code block
        """
        if start_pos >= end_pos or end_pos > len(text):
            return False
        
        block_text = text[start_pos:end_pos]
        blocks = self.find_all_coded_blocks(block_text)
        
        return len(blocks) == 1 and blocks[0].content.strip()
    
    def _find_line_numbers(self, text: str, start_pos: int, end_pos: int) -> Tuple[int, int]:
        """
        Find line numbers for a text range.
        
        Args:
            text: Full text
            start_pos: Start character position
            end_pos: End character position
            
        Returns:
            Tuple of (start_line, end_line) (1-based)
        """
        if not text or start_pos >= len(text):
            return (1, 1)
        
        # Count newlines before start position
        lines_before_start = text[:start_pos].count('\n')
        start_line = lines_before_start + 1
        
        # Count newlines in the range
        lines_in_range = text[start_pos:end_pos].count('\n')
        end_line = start_line + lines_in_range
        
        return (start_line, end_line)
    
    def get_extraction_stats(self, text: str) -> Dict[str, int]:
        """
        Get statistics about code extraction from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with extraction statistics
        """
        blocks = self.find_all_coded_blocks(text)
        codes = self.get_unique_codes(text)
        
        total_content_length = sum(len(block.content) for block in blocks)
        total_word_count = sum(block.word_count for block in blocks)
        
        return {
            "total_blocks": len(blocks),
            "unique_codes": len(codes),
            "total_content_length": total_content_length,
            "total_word_count": total_word_count,
            "codes_list": codes
        } 