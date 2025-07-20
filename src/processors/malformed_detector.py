"""Malformed code block detection module."""

import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging

from ..models.text_block import MalformedBlock
from ..utils.text_utils import TextProcessor

logger = logging.getLogger(__name__)


class MalformedDetector:
    """Detects malformed coded text blocks."""
    
    def __init__(self, supported_formats: List[str] = None):
        """
        Initialize the malformed detector.
        
        Args:
            supported_formats: List of supported code formats (default: ["{{", "[["])
        """
        self.supported_formats = supported_formats or ["{{", "[["]
        self.text_processor = TextProcessor()
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for detecting malformed blocks."""
        self.malformed_patterns = {}
        
        for fmt in self.supported_formats:
            patterns = {}
            
            if fmt == "{{":
                # More comprehensive patterns that catch all malformed variations
                patterns.update({
                    # Only closing marker without proper opening
                    "closing_only": r'=={{\s*([^}]*)\s*}}',
                    # Opening marker without proper closing
                    "missing_closing": r'\{\{\s*([^}]*)\s*\}\}\s*==(?!.*?=={{\s*\1\s*}})',
                    # Incomplete structure patterns - only when followed by ==
                    "incomplete_structure": r'\{\{[^}]*==(?:[^=]|=[^{])*?(?=\n|$)',
                    # Wrong number of braces - too few (single braces with equals)
                    "single_brace": r'(?<!\{)\{(?!\{)[^}]*\}(?!\})\s*==|==\s*(?<!\{)\{(?!\{)[^}]*\}(?!\})',
                    # Wrong number of braces - too many
                    "too_many_braces": r'\{{3,}|\}{3,}',
                    # Wrong number of equals - single = with braces
                    "single_equals": r'(?<!=)=(?!=)\s*\{\{[^}]*\}\}|\{\{[^}]*\}\}\s*(?<!=)=(?!=)',
                    # Wrong number of equals - too many ===
                    "too_many_equals": r'={3,}',
                    # Mixed wrong patterns like ={code} or {code}=
                    "mixed_wrong": r'(?<!=)=(?!=)\s*\{[^}]*\}|\{[^}]*\}\s*(?<!=)=(?!=)'
                })
            elif fmt == "[[":
                # Comprehensive patterns for [[ format
                patterns.update({
                    # Only closing marker without proper opening  
                    "closing_only": r'==\[\[\s*([^\]]*)\s*\]\]',
                    # Opening marker without proper closing
                    "missing_closing": r'\[\[\s*([^\]]*)\s*\]\]\s*==(?!.*?==\[\[\s*\1\s*\]\])',
                    # Incomplete structure patterns - only when followed by ==
                    "incomplete_structure": r'\[\[[^\]]*==(?:[^=]|=[^\[])*?(?=\n|$)',
                    # Wrong number of brackets - too few (single brackets with equals)
                    "single_bracket": r'(?<!\[)\[(?!\[)[^\]]*\](?!\])\s*==|==\s*(?<!\[)\[(?!\[)[^\]]*\](?!\])',
                    # Wrong number of brackets - too many
                    "too_many_brackets": r'\[{3,}|\]{3,}',
                    # Wrong number of equals - single = with brackets
                    "single_equals": r'(?<!=)=(?!=)\s*\[\[[^\]]*\]\]|\[\[[^\]]*\]\]\s*(?<!=)=(?!=)',
                    # Wrong number of equals - too many ===
                    "too_many_equals": r'={3,}',
                    # Mixed wrong patterns like =[code] or [code]=
                    "mixed_wrong": r'(?<!=)=(?!=)\s*\[[^\]]*\]|\[[^\]]*\]\s*(?<!=)=(?!=)'
                })
            
            try:
                compiled_patterns = {}
                for pattern_name, pattern in patterns.items():
                    compiled_patterns[pattern_name] = re.compile(pattern, re.DOTALL | re.MULTILINE)
                    logger.debug(f"Compiled malformed pattern {pattern_name} for format {fmt}")
                
                self.malformed_patterns[fmt] = compiled_patterns
            except re.error as e:
                logger.error(f"Failed to compile malformed patterns for format {fmt}: {e}")
                # Fallback to basic patterns if complex ones fail
                basic_patterns = {
                    "closing_only": r'=={{\s*([^}]*)\s*}}' if fmt == "{{" else r'==\[\[\s*([^\]]*)\s*\]\]',
                    "missing_closing": (r'\{\{\s*([^}]*)\s*\}\}\s*==(?!.*?=={{\s*\1\s*}})' if fmt == "{{"
                                      else r'\[\[\s*([^\]]*)\s*\]\]\s*==(?!.*?==\[\[\s*\1\s*\]\])')
                }
                compiled_basic = {}
                for name, pattern in basic_patterns.items():
                    try:
                        compiled_basic[name] = re.compile(pattern, re.DOTALL | re.MULTILINE)
                    except re.error:
                        pass
                self.malformed_patterns[fmt] = compiled_basic
    
    def find_all_malformed_blocks(self, text: str, source_file: str = "") -> List[MalformedBlock]:
        """
        Find all malformed coded blocks in text.
        
        Args:
            text: Text to search
            source_file: Source file path for tracking
            
        Returns:
            List of MalformedBlock objects
        """
        if not text:
            return []
        
        malformed_blocks = []
        
        # First, identify all properly formatted blocks to exclude from malformed detection
        properly_formatted = self._find_properly_formatted_blocks(text)
        logger.debug(f"Found {len(properly_formatted)} properly formatted blocks")
        
        for fmt, patterns in self.malformed_patterns.items():
            for issue_type, pattern in patterns.items():
                try:
                    matches = pattern.finditer(text)
                    for match in matches:
                        logger.debug(f"Found malformed match: {issue_type} at {match.start()}-{match.end()}: {match.group(0)[:50]}...")
                        
                        # Check if this match overlaps with any properly formatted block
                        if not self._overlaps_with_proper_blocks(match, properly_formatted):
                            # Extract the malformed content
                            content = self._extract_malformed_content(match, issue_type)
                            
                            if content and content.strip():
                                # Find line numbers for this match
                                line_start, line_end = self._find_line_numbers(text, match.start(), match.end())
                                
                                malformed_block = MalformedBlock(
                                    content=content.strip(),
                                    source_file=source_file,
                                    line_start=line_start,
                                    line_end=line_end,
                                    malformed_pattern=match.group(0),
                                    issue_type=issue_type
                                )
                                
                                malformed_blocks.append(malformed_block)
                                logger.debug(f"Added malformed block: {issue_type} in {source_file}")
                        else:
                            logger.debug(f"Skipping malformed match due to overlap with proper block")
                except Exception as e:
                    logger.error(f"Error processing malformed pattern {issue_type}: {e}")
        
        # Deduplicate overlapping malformed blocks
        deduplicated = self._deduplicate_malformed_blocks(malformed_blocks)
        logger.debug(f"Found {len(malformed_blocks)} malformed blocks, {len(deduplicated)} after deduplication")
        
        return deduplicated
    
    def _extract_malformed_content(self, match: re.Match, issue_type: str) -> str:
        """
        Extract content from a malformed block match.
        
        Args:
            match: Regex match object
            issue_type: Type of malformation
            
        Returns:
            Extracted content
        """
        try:
            if issue_type in ["missing_closing", "missing_opening", "mismatched_codes"]:
                # Try to get the main content (usually group 2)
                if match.lastindex and match.lastindex >= 2:
                    return match.group(2).strip()
                elif match.lastindex and match.lastindex >= 1:
                    return match.group(1).strip()
            
            # For other types, return the full match
            return match.group(0).strip()
            
        except (IndexError, AttributeError):
            return match.group(0).strip() if match else ""
    
    def _deduplicate_malformed_blocks(self, blocks: List[MalformedBlock]) -> List[MalformedBlock]:
        """
        Remove duplicate malformed blocks that overlap.
        
        Args:
            blocks: List of malformed blocks
            
        Returns:
            Deduplicated list of malformed blocks
        """
        if not blocks:
            return []
        
        # Sort by start line, then by issue type priority
        issue_priority = {
            "missing_closing": 1,
            "missing_opening": 2,
            "mismatched_codes": 3,
            "incomplete_structure": 4,
            "closing_only": 5
        }
        
        sorted_blocks = sorted(blocks, key=lambda b: (
            b.line_start or 0,
            issue_priority.get(b.issue_type, 99)
        ))
        
        deduplicated = []
        for block in sorted_blocks:
            # Check if this block overlaps with any already added block
            overlaps = False
            for existing in deduplicated:
                if self._blocks_overlap(block, existing):
                    overlaps = True
                    break
            
            if not overlaps:
                deduplicated.append(block)
        
        return deduplicated
    
    def _blocks_overlap(self, block1: MalformedBlock, block2: MalformedBlock) -> bool:
        """
        Check if two malformed blocks overlap.
        
        Args:
            block1: First malformed block
            block2: Second malformed block
            
        Returns:
            True if blocks overlap
        """
        if not all([block1.line_start, block1.line_end, block2.line_start, block2.line_end]):
            return False
        
        # Check for line number overlap
        return not (block1.line_end < block2.line_start or block2.line_end < block1.line_start)
    
    def find_closing_only_malformed(self, text: str, source_file: str = "") -> List[MalformedBlock]:
        """
        Find specifically closing-only malformed blocks (content ending with ==code markers).
        
        Args:
            text: Text to search
            source_file: Source file path for tracking
            
        Returns:
            List of MalformedBlock objects with closing-only issues
        """
        if not text:
            return []
        
        malformed_blocks = []
        lines = text.split('\n')
        
        for fmt in self.supported_formats:
            if fmt == "{{":
                pattern = r'.*?=={{\s*([^}]*)\s*}}.*?$'
            elif fmt == "[[":
                pattern = r'.*?==\[\[\s*([^\]]*)\s*\]\].*?$'
            else:
                continue
            
            try:
                regex = re.compile(pattern)
                for line_num, line in enumerate(lines, 1):
                    match = regex.search(line)
                    if match:
                        # Check if this line doesn't have a corresponding opening
                        full_content = '\n'.join(lines[:line_num])
                        if not self._has_matching_opening(full_content, match.group(1), fmt):
                            malformed_block = MalformedBlock(
                                content=line.strip(),
                                source_file=source_file,
                                line_start=line_num,
                                line_end=line_num,
                                malformed_pattern=line,
                                issue_type="closing_only"
                            )
                            malformed_blocks.append(malformed_block)
            except re.error as e:
                logger.error(f"Error in closing-only detection for format {fmt}: {e}")
        
        return malformed_blocks
    
    def _has_matching_opening(self, text: str, code: str, fmt: str) -> bool:
        """
        Check if text has a matching opening marker for the given code.
        
        Args:
            text: Text to search
            code: Code to match
            fmt: Format type
            
        Returns:
            True if matching opening found
        """
        if fmt == "{{":
            opening_pattern = rf'\{{\{{\s*{re.escape(code)}\s*\}}\}}\s*=='
        elif fmt == "[[":
            opening_pattern = rf'\[\[\s*{re.escape(code)}\s*\]\]\s*=='
        else:
            return False
        
        try:
            return bool(re.search(opening_pattern, text))
        except re.error:
            return False
    
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
    
    def get_malformed_stats(self, text: str) -> Dict[str, int]:
        """
        Get statistics about malformed blocks in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with malformed statistics
        """
        blocks = self.find_all_malformed_blocks(text)
        
        issue_counts = {}
        for block in blocks:
            issue_type = block.issue_type
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        total_content_length = sum(len(block.content) for block in blocks)
        total_word_count = sum(block.word_count for block in blocks)
        
        return {
            "total_malformed_blocks": len(blocks),
            "issue_type_counts": issue_counts,
            "total_content_length": total_content_length,
            "total_word_count": total_word_count
        } 
    
    def _find_properly_formatted_blocks(self, text: str) -> List[tuple]:
        """
        Find all properly formatted blocks to avoid flagging them as malformed.
        
        Returns:
            List of (start, end) tuples for properly formatted blocks
        """
        proper_blocks = []
        
        for fmt in self.supported_formats:
            if fmt == "{{":
                # Proper format: {{code}}==content=={{code}}
                pattern = re.compile(r'\{\{\s*([^}]+)\s*\}\}\s*==\s*(.*?)\s*==\s*\{\{\s*\1\s*\}\}', re.DOTALL)
            elif fmt == "[[":
                # Proper format: [[code]]==content==[[code]]
                pattern = re.compile(r'\[\[\s*([^\]]+)\s*\]\]\s*==\s*(.*?)\s*==\s*\[\[\s*\1\s*\]\]', re.DOTALL)
            else:
                continue
            
            for match in pattern.finditer(text):
                proper_blocks.append((match.start(), match.end()))
                logger.debug(f"Found proper block: {match.start()}-{match.end()}: {match.group(0)[:50]}...")
        
        logger.debug(f"Total proper blocks found: {len(proper_blocks)}")
        return proper_blocks
    
    def _overlaps_with_proper_blocks(self, match: re.Match, proper_blocks: List[tuple]) -> bool:
        """
        Check if a match overlaps with any properly formatted block.
        
        Args:
            match: Regex match to check
            proper_blocks: List of (start, end) tuples for proper blocks
            
        Returns:
            True if match overlaps with a proper block
        """
        match_start, match_end = match.start(), match.end()
        
        for block_start, block_end in proper_blocks:
            # Check for any overlap
            overlaps = not (match_end <= block_start or match_start >= block_end)
            if overlaps:
                logger.debug(f"Malformed match {match_start}-{match_end} overlaps with proper block {block_start}-{block_end}")
                return True
        
        logger.debug(f"Malformed match {match_start}-{match_end} does not overlap with any proper blocks")
        return False 