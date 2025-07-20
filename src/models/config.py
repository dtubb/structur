"""Configuration models for the Structur processing system."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ProcessingConfig:
    """Configuration for text processing operations."""
    
    # Core paths
    input_folder: Path
    output_base: Path
    
    # Folder names
    coded_folder: str = "coded"
    uncoded_folder: str = "uncoded"
    duplicates_folder: str = "duplicates"
    malformed_folder: str = "malformed"
    originals_folder: str = "originals"
    
    # Processing options
    preserve_codes_in_output: bool = False
    append_mode: bool = True
    global_duplicate_detection: bool = True
    
    # Supported formats
    supported_formats: List[str] = field(default_factory=lambda: ["{{", "[["])
    
    # Codes.txt functionality
    codes_file: Optional[Path] = None
    auto_codes_file: bool = False
    regenerate_codes: bool = False
    
    @property
    def coded_path(self) -> Path:
        """Get the path to the coded folder."""
        return self.output_base / self.coded_folder
    
    @property
    def uncoded_path(self) -> Path:
        """Get the path to the uncoded folder."""
        return self.output_base / self.uncoded_folder
    
    @property
    def duplicates_path(self) -> Path:
        """Get the path to the duplicates folder."""
        return self.output_base / self.duplicates_folder
    
    @property
    def malformed_path(self) -> Path:
        """Get the path to the malformed folder."""
        return self.output_base / self.malformed_folder
    
    @property
    def originals_path(self) -> Path:
        """Get the path to the originals folder."""
        return self.output_base / self.originals_folder
    
    @property
    def codes_path(self) -> Path:
        """Get the path to the codes.txt file directory."""
        if self.codes_file:
            return self.codes_file.parent
        return self.input_folder
    
    def get_all_output_paths(self) -> List[Path]:
        """Get all output folder paths."""
        return [
            self.coded_path,
            self.uncoded_path,
            self.duplicates_path,
            self.malformed_path,
            self.originals_path
        ] 