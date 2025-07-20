"""Text block data models."""

from dataclasses import dataclass
from typing import Optional
import hashlib


@dataclass
class TextBlock:
    """Base class for text content blocks."""
    
    content: str
    source_file: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    
    @property
    def content_hash(self) -> str:
        """Generate a hash of the content for duplicate detection."""
        normalized_content = self.content.strip().replace('\n', ' ').replace('\r', '')
        return hashlib.md5(normalized_content.encode('utf-8')).hexdigest()
    
    @property
    def word_count(self) -> int:
        """Count words in the content."""
        return len(self.content.split())
    
    def is_empty(self) -> bool:
        """Check if the content is empty or whitespace only."""
        return not self.content.strip()


@dataclass
class CodedBlock(TextBlock):
    """Represents a properly formatted coded text block."""
    
    code: str = ""
    format_type: str = "{{"  # "{{" or "[["
    
    def get_full_block(self, preserve_codes: bool = False) -> str:
        """Get the full block with or without code markers."""
        if preserve_codes:
            if self.format_type == "{{":
                return f"{{{{{self.code}}}}}=={self.content}=={{{{{self.code}}}}}"
            else:
                return f"[[{self.code}]]=={self.content}==[[{self.code}]]"
        return self.content


@dataclass
class MalformedBlock(TextBlock):
    """Represents a malformed coded text block."""
    
    malformed_pattern: str = ""
    issue_type: str = "unknown"  # "missing_opening", "missing_closing", "mismatched_codes", etc.
    
    def get_issue_description(self) -> str:
        """Get a human-readable description of the malformation issue."""
        descriptions = {
            "missing_opening": "Missing opening code marker",
            "missing_closing": "Missing closing code marker", 
            "mismatched_codes": "Opening and closing codes don't match",
            "invalid_format": "Invalid code format structure",
            "nested_codes": "Nested code blocks detected"
        }
        return descriptions.get(self.issue_type, "Unknown malformation") 