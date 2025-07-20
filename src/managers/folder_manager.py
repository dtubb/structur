"""Folder management for organizing output content."""

from pathlib import Path
from typing import Dict, List, Optional
import logging

from ..models.config import ProcessingConfig
from ..utils.file_operations import FileManager

logger = logging.getLogger(__name__)


class FolderManager:
    """Manages folder structure and organization for output content."""
    
    def __init__(self, config: ProcessingConfig):
        """
        Initialize the folder manager.
        
        Args:
            config: Processing configuration
        """
        self.config = config
        self.file_manager = FileManager()
        self._ensure_all_folders_exist()
    
    def _ensure_all_folders_exist(self) -> None:
        """Ensure all required output folders exist."""
        for folder_path in self.config.get_all_output_paths():
            self.file_manager.ensure_directory_exists(folder_path)
            logger.debug(f"Ensured folder exists: {folder_path}")
    
    def get_folder_path(self, folder_type: str) -> Optional[Path]:
        """
        Get the path for a specific folder type.
        
        Args:
            folder_type: Type of folder ('coded', 'uncoded', etc.)
            
        Returns:
            Path to the folder, or None if invalid type
        """
        folder_mapping = {
            'coded': self.config.coded_path,
            'uncoded': self.config.uncoded_path,
            'duplicates': self.config.duplicates_path,
            'malformed': self.config.malformed_path,
            'originals': self.config.originals_path
        }
        
        return folder_mapping.get(folder_type)
    
    def get_output_file_path(self, folder_type: str, filename: str) -> Optional[Path]:
        """
        Get the full output file path for a specific folder and filename.
        
        Args:
            folder_type: Type of folder
            filename: Name of the file
            
        Returns:
            Full path to the output file
        """
        folder_path = self.get_folder_path(folder_type)
        if folder_path:
            return folder_path / filename
        return None
    
    def create_originals_copy(self, source_file: Path) -> Optional[Path]:
        """
        Create a copy of the original file in the originals folder.
        
        Args:
            source_file: Source file to copy
            
        Returns:
            Path to the copied file, or None if failed
        """
        if not source_file.exists():
            logger.error(f"Source file does not exist: {source_file}")
            return None
        
        original_filename = source_file.name
        destination_path = self.config.originals_path / original_filename
        
        if self.file_manager.copy_file_safely(source_file, destination_path):
            logger.info(f"Created original copy: {destination_path}")
            return destination_path
        
        return None
    
    def write_content_to_folder(self, folder_type: str, filename: str, content: str) -> bool:
        """
        Write content to a file in the specified folder.
        
        Args:
            folder_type: Type of folder
            filename: Name of the file
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        output_path = self.get_output_file_path(folder_type, filename)
        if not output_path:
            logger.error(f"Invalid folder type: {folder_type}")
            return False
        
        if self.config.append_mode:
            return self.file_manager.append_content_if_not_exists(output_path, content)
        else:
            return self.file_manager.write_file_content(output_path, content)
    
    def append_content_to_folder(self, folder_type: str, filename: str, content: str) -> bool:
        """
        Append content to a file in the specified folder, avoiding duplicates.
        
        Args:
            folder_type: Type of folder
            filename: Name of the file
            content: Content to append
            
        Returns:
            True if successful, False otherwise
        """
        output_path = self.get_output_file_path(folder_type, filename)
        if not output_path:
            logger.error(f"Invalid folder type: {folder_type}")
            return False
        
        return self.file_manager.append_content_if_not_exists(output_path, content)
    
    def check_content_exists_in_folder(self, folder_type: str, content: str) -> bool:
        """
        Check if content already exists in any file within a folder.
        
        Args:
            folder_type: Type of folder to check
            content: Content to search for
            
        Returns:
            True if content exists, False otherwise
        """
        folder_path = self.get_folder_path(folder_type)
        if not folder_path or not folder_path.exists():
            return False
        
        # Get all files in the folder
        existing_files = {}
        for file_path in folder_path.rglob("*.md"):
            file_content = self.file_manager.read_file_content(file_path)
            if file_content:
                existing_files[str(file_path)] = file_content
        
        # Use duplicate detector logic
        from ..utils.duplicate_detector import DuplicateDetector
        detector = DuplicateDetector()
        
        return detector.check_against_existing_files(content, existing_files)
    
    def get_existing_file_content(self, folder_type: str, filename: str) -> Optional[str]:
        """
        Get existing content from a file in a folder.
        
        Args:
            folder_type: Type of folder
            filename: Name of the file
            
        Returns:
            File content if exists, None otherwise
        """
        file_path = self.get_output_file_path(folder_type, filename)
        if file_path and file_path.exists():
            return self.file_manager.read_file_content(file_path)
        return None
    
    def list_files_in_folder(self, folder_type: str) -> List[Path]:
        """
        List all files in a specific folder.
        
        Args:
            folder_type: Type of folder
            
        Returns:
            List of file paths in the folder
        """
        folder_path = self.get_folder_path(folder_type)
        if folder_path and folder_path.exists():
            return list(folder_path.rglob("*.md"))
        return []
    
    def get_folder_stats(self) -> Dict[str, Dict]:
        """
        Get statistics about all folders.
        
        Returns:
            Dictionary with folder statistics
        """
        stats = {}
        
        folder_types = ['coded', 'uncoded', 'duplicates', 'malformed', 'originals']
        
        for folder_type in folder_types:
            folder_path = self.get_folder_path(folder_type)
            if folder_path and folder_path.exists():
                files = self.list_files_in_folder(folder_type)
                total_size = sum(f.stat().st_size for f in files if f.exists())
                total_words = 0
                
                for file_path in files:
                    content = self.file_manager.read_file_content(file_path)
                    if content:
                        from ..utils.text_utils import TextProcessor
                        processor = TextProcessor()
                        total_words += processor.count_words(content)
                
                stats[folder_type] = {
                    'file_count': len(files),
                    'total_size_bytes': total_size,
                    'total_words': total_words,
                    'folder_path': str(folder_path)
                }
            else:
                stats[folder_type] = {
                    'file_count': 0,
                    'total_size_bytes': 0,
                    'total_words': 0,
                    'folder_path': str(folder_path) if folder_path else 'N/A'
                }
        
        return stats
    
    def cleanup_empty_files(self) -> int:
        """
        Remove empty files from all output folders.
        
        Returns:
            Number of files removed
        """
        removed_count = 0
        
        for folder_type in ['coded', 'uncoded', 'duplicates', 'malformed']:
            files = self.list_files_in_folder(folder_type)
            
            for file_path in files:
                content = self.file_manager.read_file_content(file_path)
                if not content or not content.strip():
                    try:
                        file_path.unlink()
                        logger.debug(f"Removed empty file: {file_path}")
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to remove empty file {file_path}: {e}")
        
        return removed_count 