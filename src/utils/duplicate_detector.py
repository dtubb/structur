"""Duplicate detection and management system."""

import hashlib
from typing import Dict, Set, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Manages global duplicate detection across all content."""
    
    def __init__(self):
        """Initialize the duplicate detector."""
        self.content_hashes: Dict[str, Tuple[str, str]] = {}  # hash -> (first_file, first_code)
        self.seen_content: Set[str] = set()  # normalized content strings
        self.duplicate_count: int = 0
    
    def normalize_content_for_comparison(self, content: str) -> str:
        """
        Normalize content for duplicate comparison.
        
        Args:
            content: Raw content
            
        Returns:
            Normalized content string
        """
        if not content:
            return ""
        
        # Remove extra whitespace and normalize line endings
        normalized = content.strip()
        normalized = ' '.join(normalized.split())  # Collapse whitespace
        normalized = normalized.lower()  # Case insensitive comparison
        
        return normalized
    
    def generate_content_hash(self, content: str) -> str:
        """
        Generate a hash for content.
        
        Args:
            content: Content to hash
            
        Returns:
            MD5 hash of normalized content
        """
        normalized = self.normalize_content_for_comparison(content)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, content: str, source_file: str, code: str = "") -> bool:
        """
        Check if content is a duplicate.
        
        Args:
            content: Content to check
            source_file: Source file path
            code: Code identifier (optional)
            
        Returns:
            True if content is a duplicate
        """
        if not content or not content.strip():
            return False
        
        content_hash = self.generate_content_hash(content)
        
        if content_hash in self.content_hashes:
            first_file, first_code = self.content_hashes[content_hash]
            logger.debug(f"Duplicate detected: {source_file}:{code} matches {first_file}:{first_code}")
            return True
        
        return False
    
    def register_content(self, content: str, source_file: str, code: str = "") -> bool:
        """
        Register content as seen (first occurrence).
        
        Args:
            content: Content to register
            source_file: Source file path
            code: Code identifier (optional)
            
        Returns:
            True if content was registered (not a duplicate), False if duplicate
        """
        if not content or not content.strip():
            return False
        
        if self.is_duplicate(content, source_file, code):
            self.duplicate_count += 1
            return False
        
        # Register as first occurrence
        content_hash = self.generate_content_hash(content)
        self.content_hashes[content_hash] = (source_file, code)
        self.seen_content.add(self.normalize_content_for_comparison(content))
        
        logger.debug(f"Registered new content: {source_file}:{code}")
        return True
    
    def get_first_occurrence(self, content: str) -> Optional[Tuple[str, str]]:
        """
        Get the first occurrence information for duplicate content.
        
        Args:
            content: Content to look up
            
        Returns:
            Tuple of (first_file, first_code) if duplicate, None otherwise
        """
        if not content or not content.strip():
            return None
        
        content_hash = self.generate_content_hash(content)
        return self.content_hashes.get(content_hash)
    
    def check_against_existing_files(self, content: str, existing_files: Dict[str, str]) -> bool:
        """
        Check if content already exists in any of the existing files.
        
        Args:
            content: Content to check
            existing_files: Dict of {file_path: file_content}
            
        Returns:
            True if content already exists in any file
        """
        if not content or not content.strip():
            return False
        
        normalized_content = self.normalize_content_for_comparison(content)
        
        for file_path, file_content in existing_files.items():
            if not file_content:
                continue
            
            normalized_file_content = self.normalize_content_for_comparison(file_content)
            if normalized_content in normalized_file_content:
                logger.debug(f"Content already exists in {file_path}")
                return True
        
        return False
    
    def get_duplicate_stats(self) -> Dict[str, int]:
        """
        Get duplicate detection statistics.
        
        Returns:
            Dictionary with duplicate statistics
        """
        return {
            "total_content_registered": len(self.content_hashes),
            "duplicate_count": self.duplicate_count,
            "unique_content_count": len(self.seen_content)
        }
    
    def reset(self) -> None:
        """Reset the duplicate detector state."""
        self.content_hashes.clear()
        self.seen_content.clear()
        self.duplicate_count = 0
        logger.debug("Duplicate detector reset")
    
    def export_duplicate_map(self) -> Dict[str, Dict]:
        """
        Export the current duplicate map for debugging.
        
        Returns:
            Dictionary with duplicate mapping information
        """
        export_data = {
            "content_hashes": {
                h: {"first_file": file, "first_code": code}
                for h, (file, code) in self.content_hashes.items()
            },
            "stats": self.get_duplicate_stats()
        }
        return export_data 