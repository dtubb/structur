"""Workflow management for coordinating the text processing pipeline."""

from pathlib import Path
from typing import List, Dict, Optional, Set
import logging

from ..models.config import ProcessingConfig
from ..models.text_block import CodedBlock, MalformedBlock
from ..utils.file_operations import FileManager
from ..utils.duplicate_detector import DuplicateDetector
from ..processors.code_extractor import CodeExtractor
from ..processors.malformed_detector import MalformedDetector
from ..processors.content_filter import ContentFilter
from .folder_manager import FolderManager

logger = logging.getLogger(__name__)


class WorkflowManager:
    """Manages the complete text processing workflow."""
    
    def __init__(self, config: ProcessingConfig):
        """
        Initialize the workflow manager.
        
        Args:
            config: Processing configuration
        """
        self.config = config
        self.file_manager = FileManager()
        self.duplicate_detector = DuplicateDetector()
        self.code_extractor = CodeExtractor(config.supported_formats)
        self.malformed_detector = MalformedDetector(config.supported_formats)
        self.content_filter = ContentFilter(config.supported_formats)
        self.folder_manager = FolderManager(config)
        
        # Processing statistics
        self.stats = {
            'files_processed': 0,
            'coded_blocks_found': 0,
            'malformed_blocks_found': 0,
            'duplicates_found': 0,
            'total_words_processed': 0,
            'errors': []
        }
    
    def process_single_file(self, file_path: Path) -> bool:
        """
        Process a single file using the removal-based approach.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            True if processing successful, False otherwise
        """
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Read original content
            original_content = self.file_manager.read_file_content(file_path)
            if original_content is None:
                logger.error(f"Failed to read file: {file_path}")
                return False
            
            # Handle empty files (content is empty string)
            if original_content == "":
                logger.info(f"Processing empty file: {file_path}")
                original_content = ""
            
            # Create a copy in originals folder
            original_copy_path = self.folder_manager.create_originals_copy(file_path)
            if not original_copy_path:
                logger.warning(f"Failed to create original copy for: {file_path}")
            
            # Extract all types of content
            filename = file_path.name
            
            # 1. Process coded blocks
            self._process_coded_content(original_content, filename)
            
            # 2. Process malformed blocks  
            self._process_malformed_content(original_content, filename)
            
            # 3. Process uncoded content
            self._process_uncoded_content(original_content, filename)
            
            self.stats['files_processed'] += 1
            logger.info(f"Successfully processed: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Error processing file {file_path}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
    
    def _process_coded_content(self, content: str, filename: str) -> None:
        """
        Process and extract coded content from text.
        
        Args:
            content: Original text content
            filename: Source filename
        """
        # Find all coded blocks
        coded_blocks = self.code_extractor.find_all_coded_blocks(content, filename)
        
        # Group blocks by code name
        grouped_blocks = self.code_extractor.group_blocks_by_code(coded_blocks)
        
        # Collect all unique codes for codes.txt management
        extracted_codes = list(grouped_blocks.keys())
        
        for code_name, blocks in grouped_blocks.items():
            # Combine content from all blocks with the same code
            combined_content_parts = []
            
            for block in blocks:
                # Check for duplicates globally
                if self.duplicate_detector.register_content(block.content, filename, code_name):
                    # Not a duplicate, add to output
                    if self.config.preserve_codes_in_output:
                        combined_content_parts.append(block.get_full_block(preserve_codes=True))
                    else:
                        combined_content_parts.append(block.content)
                    self.stats['coded_blocks_found'] += 1
                else:
                    # Is a duplicate, save to duplicates folder
                    self._save_duplicate_content(block.content, filename, code_name)
                    self.stats['duplicates_found'] += 1
            
            # Write combined content to coded folder
            if combined_content_parts:
                combined_content = '\n\n'.join(combined_content_parts)
                coded_filename = f"{code_name}.md"
                
                # Append to coded folder (folder_manager handles duplicate checking)
                self.folder_manager.append_content_to_folder('coded', coded_filename, combined_content)
        
        # Handle codes.txt functionality
        self._handle_codes_txt_management(extracted_codes, filename)
    
    def _process_malformed_content(self, content: str, filename: str) -> None:
        """
        Process and extract malformed content from text.
        
        Args:
            content: Original text content
            filename: Source filename
        """
        # Find all malformed blocks
        malformed_blocks = self.malformed_detector.find_all_malformed_blocks(content, filename)
        
        for block in malformed_blocks:
            # Check for duplicates
            if self.duplicate_detector.register_content(block.content, filename, f"malformed_{block.issue_type}"):
                # Save to malformed folder
                self.folder_manager.append_content_to_folder('malformed', filename, block.content)
                self.stats['malformed_blocks_found'] += 1
            else:
                # Is a duplicate
                self._save_duplicate_content(block.content, filename, f"malformed_{block.issue_type}")
                self.stats['duplicates_found'] += 1
    
    def _process_uncoded_content(self, content: str, filename: str) -> None:
        """
        Process and extract uncoded content by removing coded and malformed content.
        
        Args:
            content: Original text content
            filename: Source filename
        """
        # Create a clean copy with coded and malformed content removed
        uncoded_content = self.content_filter.extract_uncoded_content(content)
        
        if uncoded_content and uncoded_content.strip():
            # Check for duplicates
            if self.duplicate_detector.register_content(uncoded_content, filename, "uncoded"):
                # Append to uncoded folder (folder_manager handles duplicate checking)
                self.folder_manager.append_content_to_folder('uncoded', filename, uncoded_content)
            else:
                # Is a duplicate
                self._save_duplicate_content(uncoded_content, filename, "uncoded")
                self.stats['duplicates_found'] += 1
    
    def _save_duplicate_content(self, content: str, filename: str, content_type: str) -> None:
        """
        Save duplicate content to the duplicates folder using folder-based organization.
        Saves only the clean uncoded text content with all coded/malformed/other markers removed.
        
        Args:
            content: Duplicate content (may contain markers)
            filename: Source filename
            content_type: Type of content (code name, malformed type, etc.)
        """
        # Get information about the first occurrence
        first_occurrence = self.duplicate_detector.get_first_occurrence(content)
        if first_occurrence:
            first_file, first_code = first_occurrence
            
            # Apply full subtractive processing - extract only uncoded content
            # This removes coded blocks, malformed blocks, and other markup
            clean_content = self.content_filter.extract_uncoded_content(content)
            
            # Skip if no clean content remains after processing
            if not clean_content or not clean_content.strip():
                return
            
            # Create folder name from first 128 characters of clean content
            content_preview = clean_content.strip().replace('\n', ' ').replace('\r', ' ')
            # Remove problematic characters for folder names
            folder_name = "".join(c for c in content_preview[:128] if c.isalnum() or c in ' -_.,()[]{}')
            folder_name = folder_name.strip()
            if not folder_name:
                folder_name = f"duplicate_{hash(clean_content) % 10000}"
            
            # Create the duplicate folder structure
            duplicate_base_path = self.config.duplicates_path / folder_name
            self.folder_manager.file_manager.ensure_directory_exists(duplicate_base_path)
            
            # Save only the clean uncoded duplicate content
            current_file_path = duplicate_base_path / filename
            self.folder_manager.file_manager.write_file_content(current_file_path, clean_content)
            
            # Create a metadata file to track the first occurrence and content type
            metadata_content = f"Duplicate of: {first_file} ({first_code})\nFirst seen in: {first_file}\nContent type: {content_type}\nOriginal content length: {len(content)} chars\nClean uncoded length: {len(clean_content)} chars\n"
            metadata_path = duplicate_base_path / "_metadata.txt"
            if not metadata_path.exists():
                self.folder_manager.file_manager.write_file_content(metadata_path, metadata_content)
    
    def _handle_codes_txt_management(self, extracted_codes: List[str], filename: str) -> None:
        """
        Handles the management of codes.txt, including reading from it, writing extracted codes,
        and regenerating empty files.
        
        Args:
            extracted_codes: List of unique code names found in the current file.
            filename: Source filename.
        """
        # Only handle codes.txt if auto_codes_file is enabled
        if not self.config.auto_codes_file:
            return
        
        # Determine codes.txt path (in the same directory as the input file)
        codes_txt_path = self.config.codes_path / "codes.txt"
        
        # Write extracted codes to codes.txt
        if extracted_codes:
            success = self.folder_manager.file_manager.write_codes_to_file(
                codes_txt_path, extracted_codes, append=True
            )
            if success:
                logger.info(f"Updated codes.txt with {len(extracted_codes)} codes from {filename}")
            else:
                logger.warning(f"Failed to update codes.txt with codes from {filename}")
        
        # Handle regenerate_codes functionality
        if self.config.regenerate_codes:
            # Read all codes from codes.txt
            all_codes = self.folder_manager.file_manager.read_codes_from_file(codes_txt_path)
            if all_codes:
                created_count = self.folder_manager.file_manager.create_empty_code_files(
                    self.config.output_base, all_codes, self.config.coded_folder
                )
                logger.info(f"Regenerated {created_count} empty code files from codes.txt")
    
    def process_folder(self, input_folder: Path) -> Dict[str, int]:
        """
        Process all markdown files in a folder.
        
        Args:
            input_folder: Path to input folder
            
        Returns:
            Dictionary with processing statistics
        """
        logger.info(f"Starting folder processing: {input_folder}")
        
        # Get all markdown files
        md_files = self.file_manager.get_markdown_files(input_folder)
        
        if not md_files:
            logger.warning(f"No markdown files found in: {input_folder}")
            return self.stats
        
        logger.info(f"Found {len(md_files)} markdown files to process")
        
        # Process each file
        for file_path in md_files:
            self.process_single_file(file_path)
        
        # Calculate final statistics
        self._calculate_final_stats()
        
        logger.info(f"Folder processing complete. Stats: {self.stats}")
        return self.stats
    
    def _calculate_final_stats(self) -> None:
        """Calculate final processing statistics."""
        folder_stats = self.folder_manager.get_folder_stats()
        
        # Add folder statistics to overall stats
        self.stats.update({
            'folder_stats': folder_stats,
            'duplicate_detector_stats': self.duplicate_detector.get_duplicate_stats()
        })
        
        # Calculate total word counts
        total_words = sum(folder['total_words'] for folder in folder_stats.values())
        self.stats['total_words_processed'] = total_words
    
    def cleanup_and_finalize(self) -> None:
        """Perform cleanup and finalization tasks."""
        logger.info("Performing cleanup and finalization")
        
        # Handle regenerate_codes functionality if enabled
        if self.config.regenerate_codes:
            codes_txt_path = self.config.codes_path / "codes.txt"
            if codes_txt_path.exists():
                all_codes = self.folder_manager.file_manager.read_codes_from_file(codes_txt_path)
                if all_codes:
                    created_count = self.folder_manager.file_manager.create_empty_code_files(
                        self.config.output_base, all_codes, self.config.coded_folder
                    )
                    logger.info(f"Regenerated {created_count} empty code files from codes.txt")
        
        # Remove empty files
        empty_files_removed = self.folder_manager.cleanup_empty_files()
        if empty_files_removed > 0:
            logger.info(f"Removed {empty_files_removed} empty files")
        
        # Log final report
        self._log_final_report()
    
    def _log_final_report(self) -> None:
        """Log a comprehensive final report."""
        logger.info("=== PROCESSING REPORT ===")
        logger.info(f"Files processed: {self.stats['files_processed']}")
        logger.info(f"Coded blocks found: {self.stats['coded_blocks_found']}")
        logger.info(f"Malformed blocks found: {self.stats['malformed_blocks_found']}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']}")
        logger.info(f"Total words processed: {self.stats['total_words_processed']}")
        
        if 'folder_stats' in self.stats:
            logger.info("=== FOLDER STATISTICS ===")
            for folder_type, stats in self.stats['folder_stats'].items():
                logger.info(f"{folder_type}: {stats['file_count']} files, {stats['total_words']} words")
        
        if self.stats['errors']:
            logger.error(f"Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                logger.error(f"  - {error}")
        
        logger.info("=== END REPORT ===")
    
    def get_processing_stats(self) -> Dict:
        """
        Get current processing statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        return self.stats.copy() 