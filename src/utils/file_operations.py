"""File operation utilities with safe handling and deduplication."""

import shutil
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """Handles all file operations with safety guarantees."""
    
    def __init__(self):
        """Initialize the file manager."""
        pass
    
    def ensure_directory_exists(self, directory: Path) -> None:
        """Create directory if it doesn't exist."""
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
    
    def copy_file_safely(self, source: Path, destination: Path) -> bool:
        """
        Copy a file safely, ensuring destination directory exists.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if copy successful, False otherwise
        """
        try:
            if not source.exists():
                logger.error(f"Source file does not exist: {source}")
                return False
            
            self.ensure_directory_exists(destination.parent)
            shutil.copy2(source, destination)
            logger.debug(f"Copied file: {source} -> {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy file {source} to {destination}: {e}")
            return False
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """
        Read file content safely.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string, or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Read file: {file_path} ({len(content)} characters)")
            return content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    def write_file_content(self, file_path: Path, content: str, mode: str = 'w') -> bool:
        """
        Write content to file safely.
        
        Args:
            file_path: Path to write to
            content: Content to write
            mode: Write mode ('w' for overwrite, 'a' for append)
            
        Returns:
            True if write successful, False otherwise
        """
        try:
            self.ensure_directory_exists(file_path.parent)
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Wrote file: {file_path} ({len(content)} characters, mode={mode})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return False
    
    def append_content_if_not_exists(self, file_path: Path, content: str) -> bool:
        """
        Append content to file only if it doesn't already exist in the file.
        
        Args:
            file_path: Path to the file
            content: Content to append
            
        Returns:
            True if content was appended or already exists, False on error
        """
        try:
            # Read existing content if file exists
            existing_content = ""
            if file_path.exists():
                existing_content = self.read_file_content(file_path) or ""
            
            # Check if content already exists
            content_normalized = content.strip()
            if content_normalized in existing_content:
                logger.debug(f"Content already exists in {file_path}, skipping append")
                return True
            
            # Append the content
            append_content = f"\n\n{content}" if existing_content else content
            return self.write_file_content(file_path, append_content, mode='a')
            
        except Exception as e:
            logger.error(f"Failed to append content to {file_path}: {e}")
            return False
    
    def get_markdown_files(self, directory: Path) -> List[Path]:
        """
        Get all markdown and text files in a directory recursively, sorted alphanumerically.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of markdown and text file paths, sorted alphanumerically
        """
        try:
            if not directory.exists():
                logger.warning(f"Directory does not exist: {directory}")
                return []
            
            # Get both .md and .txt files
            md_files = list(directory.rglob("*.md"))
            txt_files = list(directory.rglob("*.txt"))
            all_files = md_files + txt_files
            
            # Sort files alphanumerically (like Finder)
            def natural_sort_key(path):
                """Natural sort key that handles numbers properly."""
                import re
                # Convert filename to string and split by numbers
                return [int(text) if text.isdigit() else text.lower()
                       for text in re.split('([0-9]+)', path.name)]
            
            all_files.sort(key=natural_sort_key)
            
            logger.debug(f"Found {len(all_files)} files ({len(md_files)} .md, {len(txt_files)} .txt) in {directory}")
            return all_files
            
        except Exception as e:
            logger.error(f"Failed to get markdown files from {directory}: {e}")
            return []
    
    def backup_file(self, file_path: Path, backup_suffix: str = ".backup") -> Optional[Path]:
        """
        Create a backup of a file.
        
        Args:
            file_path: File to backup
            backup_suffix: Suffix for backup file
            
        Returns:
            Path to backup file, or None if failed
        """
        try:
            if not file_path.exists():
                logger.error(f"Cannot backup non-existent file: {file_path}")
                return None
            
            backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
            if self.copy_file_safely(file_path, backup_path):
                logger.debug(f"Created backup: {backup_path}")
                return backup_path
            return None
            
        except Exception as e:
            logger.error(f"Failed to backup file {file_path}: {e}")
            return None
    
    def read_codes_from_file(self, codes_file_path: Path) -> list[str]:
        """
        Read codes from a codes.txt file.
        
        Args:
            codes_file_path: Path to the codes.txt file
            
        Returns:
            List of code names (stripped of whitespace and comments)
        """
        try:
            if not codes_file_path.exists():
                logger.warning(f"Codes file does not exist: {codes_file_path}")
                return []
            
            codes = []
            with open(codes_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        codes.append(line)
            
            logger.debug(f"Read {len(codes)} codes from {codes_file_path}")
            return codes
            
        except Exception as e:
            logger.error(f"Failed to read codes from {codes_file_path}: {e}")
            return []
    
    def write_codes_to_file(self, codes_file_path: Path, codes: list[str], append: bool = True) -> bool:
        """
        Write codes to a codes.txt file.
        
        Args:
            codes_file_path: Path to the codes.txt file
            codes: List of code names to write
            append: If True, append to existing file; if False, overwrite
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.ensure_directory_exists(codes_file_path.parent)
            
            # Read existing codes if appending
            existing_codes = set()
            if append and codes_file_path.exists():
                existing_codes = set(self.read_codes_from_file(codes_file_path))
            
            # Filter out duplicates
            new_codes = [code for code in codes if code not in existing_codes]
            
            if not new_codes:
                logger.debug(f"No new codes to write to {codes_file_path}")
                return True
            
            # Write codes
            mode = 'a' if append else 'w'
            with open(codes_file_path, mode, encoding='utf-8') as f:
                if append and codes_file_path.exists():
                    f.write('\n')  # Add separator
                f.write('\n'.join(new_codes))
                f.write('\n')
            
            logger.info(f"Wrote {len(new_codes)} new codes to {codes_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write codes to {codes_file_path}: {e}")
            return False
    
    def create_empty_code_files(self, output_base: Path, codes: list[str], coded_folder: str = "coded") -> int:
        """
        Create empty files for all codes in the coded folder.
        
        Args:
            output_base: Base output directory
            codes: List of code names
            coded_folder: Name of the coded folder
            
        Returns:
            Number of files created
        """
        try:
            coded_dir = output_base / coded_folder
            self.ensure_directory_exists(coded_dir)
            
            created_count = 0
            for code in codes:
                code_file = coded_dir / f"{code}.md"
                if not code_file.exists():
                    # Create empty file with a header
                    content = f"# {code}\n\n"
                    if self.write_file_content(code_file, content):
                        created_count += 1
                        logger.debug(f"Created empty file for code: {code}")
            
            logger.info(f"Created {created_count} empty code files in {coded_dir}")
            return created_count
            
        except Exception as e:
            logger.error(f"Failed to create empty code files: {e}")
            return 0 