"""Main processor class for the Structur text processing system."""

from pathlib import Path
from typing import Dict, Optional
import logging

from ..models.config import ProcessingConfig
from ..managers.workflow_manager import WorkflowManager

logger = logging.getLogger(__name__)


class StructurProcessor:
    """Main processor for the Structur text processing system."""
    
    def __init__(self, config: ProcessingConfig):
        """
        Initialize the Structur processor.
        
        Args:
            config: Processing configuration
        """
        self.config = config
        self.workflow_manager = WorkflowManager(config)
        
        # Setup logging
        self._setup_logging()
        
        logger.info(f"Structur processor initialized with config: {config}")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        # Ensure output directory exists
        self.config.output_base.mkdir(parents=True, exist_ok=True)
        
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Clear existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set up new handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler
        log_file = self.config.output_base / 'structur_processing.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Set level
        root_logger.setLevel(logging.INFO)
    
    def process_folder(self, input_folder: Optional[Path] = None) -> Dict:
        """
        Process all markdown files in the specified folder.
        
        Args:
            input_folder: Path to input folder (uses config if not provided)
            
        Returns:
            Dictionary with processing statistics
        """
        folder_to_process = input_folder or self.config.input_folder
        
        if not folder_to_process.exists():
            raise ValueError(f"Input folder does not exist: {folder_to_process}")
        
        if not folder_to_process.is_dir():
            raise ValueError(f"Input path is not a directory: {folder_to_process}")
        
        logger.info(f"Starting processing of folder: {folder_to_process}")
        
        try:
            # Process the folder using workflow manager
            stats = self.workflow_manager.process_folder(folder_to_process)
            
            # Perform cleanup and finalization
            self.workflow_manager.cleanup_and_finalize()
            
            logger.info("Processing completed successfully")
            return stats
            
        except Exception as e:
            logger.error(f"Error during processing: {e}")
            raise
    
    def process_single_file(self, file_path: Path) -> bool:
        """
        Process a single file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            True if processing successful, False otherwise
        """
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return False
        
        # Check if file is a supported format (.md or .txt)
        if file_path.suffix.lower() not in ['.md', '.txt']:
            logger.warning(f"File is not a supported format (expected .md or .txt): {file_path}")
            return False
        
        logger.info(f"Processing single file: {file_path}")
        
        try:
            result = self.workflow_manager.process_single_file(file_path)
            
            if result:
                # Calculate and log stats for single file
                stats = self.workflow_manager.get_processing_stats()
                logger.info(f"Single file processing stats: {stats}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return False
    
    def get_processing_statistics(self) -> Dict:
        """
        Get current processing statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        return self.workflow_manager.get_processing_stats()
    
    def get_folder_statistics(self) -> Dict:
        """
        Get statistics about output folders.
        
        Returns:
            Dictionary with folder statistics
        """
        return self.workflow_manager.folder_manager.get_folder_stats()
    
    def reset_processing_state(self) -> None:
        """Reset the processing state for a new run."""
        logger.info("Resetting processing state")
        self.workflow_manager.duplicate_detector.reset()
        self.workflow_manager.stats = {
            'files_processed': 0,
            'coded_blocks_found': 0,
            'malformed_blocks_found': 0,
            'duplicates_found': 0,
            'total_words_processed': 0,
            'errors': []
        }
    
    @classmethod
    def create_with_simple_config(cls, 
                                input_folder: Path, 
                                output_folder: Path,
                                preserve_codes: bool = False,
                                append_mode: bool = True) -> 'StructurProcessor':
        """
        Create a processor with a simple configuration.
        
        Args:
            input_folder: Path to input folder
            output_folder: Path to output folder
            preserve_codes: Whether to preserve code markers in output
            append_mode: Whether to use append mode
            
        Returns:
            Configured StructurProcessor instance
        """
        config = ProcessingConfig(
            input_folder=input_folder,
            output_base=output_folder,
            preserve_codes_in_output=preserve_codes,
            append_mode=append_mode
        )
        
        return cls(config)
    
    def validate_configuration(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check input folder
            if not self.config.input_folder.exists():
                logger.error(f"Input folder does not exist: {self.config.input_folder}")
                return False
            
            # Check if output base can be created
            try:
                self.config.output_base.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Cannot create output folder: {self.config.output_base}: {e}")
                return False
            
            # Check supported formats
            if not self.config.supported_formats:
                logger.error("No supported formats configured")
                return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False 