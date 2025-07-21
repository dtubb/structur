#!/usr/bin/env python3
"""
Structur New - A modular, reliable text processing system for extracting and organizing coded content.

This version uses a removal-based approach to ensure no data loss and provides
comprehensive error handling and logging.
"""

import typer
from pathlib import Path
from typing import Optional
import sys
import logging

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.config import ProcessingConfig
from src.processors.main_processor import StructurProcessor

app = typer.Typer(
    name="structur-new",
    help="Modular text processing system for extracting and organizing coded content",
    add_completion=False
)


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


@app.command()
def process(
    input_folder: Path = typer.Argument(
        ...,
        help="Path to the folder containing markdown and text files to process",
        exists=True,
        file_okay=False,
        dir_okay=True
    ),
    output_folder: Path = typer.Argument(
        ...,
        help="Path to the output folder where results will be saved"
    ),
    coded_folder: str = typer.Option(
        "coded",
        "--coded-folder",
        help="Name of the folder for coded content"
    ),
    uncoded_folder: str = typer.Option(
        "uncoded",
        "--uncoded-folder", 
        help="Name of the folder for uncoded content"
    ),
    duplicates_folder: str = typer.Option(
        "duplicates",
        "--duplicates-folder",
        help="Name of the folder for duplicate content"
    ),
    malformed_folder: str = typer.Option(
        "malformed",
        "--malformed-folder",
        help="Name of the folder for malformed content"
    ),
    preserve_codes: bool = typer.Option(
        False,
        "--preserve-codes",
        help="Preserve code markers in the output files"
    ),
    append_mode: bool = typer.Option(
        True,
        "--append/--overwrite",
        help="Append to existing files instead of overwriting"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    ),
    stats_only: bool = typer.Option(
        False,
        "--stats-only",
        help="Only show statistics, don't process files"
    ),
    codes_file: Optional[Path] = typer.Option(
        None,
        "--codes-file",
        help="Path to codes.txt file to read master codes list"
    ),
    auto_codes_file: bool = typer.Option(
        False,
        "--auto-codes-file",
        help="Automatically create/update codes.txt with extracted codes"
    ),
    regenerate_codes: bool = typer.Option(
        False,
        "--regenerate-codes",
        help="Regenerate empty files for all codes in codes.txt"
    )
):
    """
    Process markdown and text files to extract and organize coded content.
    
    This command processes all markdown and text files in the input folder using a removal-based
    approach that ensures no data loss. Content is organized into separate folders
    based on type (coded, uncoded, duplicates, malformed, already coded).
    """
    setup_logging(verbose)
    
    try:
        # Create processing configuration
        config = ProcessingConfig(
            input_folder=input_folder,
            output_base=output_folder,
            coded_folder=coded_folder,
            uncoded_folder=uncoded_folder,
            duplicates_folder=duplicates_folder,
            malformed_folder=malformed_folder,
            preserve_codes_in_output=preserve_codes,
            append_mode=append_mode,
            global_duplicate_detection=True,
            codes_file=codes_file,
            auto_codes_file=auto_codes_file,
            regenerate_codes=regenerate_codes
        )
        
        # Create processor
        processor = StructurProcessor(config)
        
        # Validate configuration
        if not processor.validate_configuration():
            typer.echo("❌ Configuration validation failed", err=True)
            raise typer.Exit(1)
        
        if stats_only:
            # Show current folder statistics
            folder_stats = processor.get_folder_statistics()
            print_folder_statistics(folder_stats)
            return
        
        # Process the folder
        typer.echo(f"🚀 Processing folder: {input_folder}")
        typer.echo(f"📁 Output folder: {output_folder}")
        
        stats = processor.process_folder()
        
        # Display results
        print_processing_results(stats)
        
        typer.echo("✅ Processing completed successfully!")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def single(
    file_path: Path = typer.Argument(
        ...,
        help="Path to the markdown or text file to process",
        exists=True,
        file_okay=True,
        dir_okay=False
    ),
    output_folder: Path = typer.Argument(
        ...,
        help="Path to the output folder where results will be saved"
    ),
    preserve_codes: bool = typer.Option(
        False,
        "--preserve-codes",
        help="Preserve code markers in the output files"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    )
):
    """
    Process a single markdown or text file.
    
    This command processes a single markdown or text file and extracts coded content
    using the same reliable, removal-based approach.
    """
    setup_logging(verbose)
    
    try:
        # Use the file's parent directory as input folder for configuration
        input_folder = file_path.parent
        
        # Create configuration
        config = ProcessingConfig(
            input_folder=input_folder,
            output_base=output_folder,
            preserve_codes_in_output=preserve_codes
        )
        
        # Create processor
        processor = StructurProcessor(config)
        
        # Validate configuration
        if not processor.validate_configuration():
            typer.echo("❌ Configuration validation failed", err=True)
            raise typer.Exit(1)
        
        # Process the single file
        typer.echo(f"🚀 Processing file: {file_path}")
        typer.echo(f"📁 Output folder: {output_folder}")
        
        success = processor.process_single_file(file_path)
        
        if success:
            # Display results
            stats = processor.get_processing_statistics()
            print_processing_results(stats)
            typer.echo("✅ File processed successfully!")
        else:
            typer.echo("❌ File processing failed", err=True)
            raise typer.Exit(1)
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def stats(
    output_folder: Path = typer.Argument(
        ...,
        help="Path to the output folder to analyze",
        exists=True,
        file_okay=False,
        dir_okay=True
    )
):
    """
    Show statistics for an existing output folder.
    
    This command analyzes the contents of an output folder and shows
    detailed statistics about the processed content.
    """
    try:
        # Create a minimal config for stats
        config = ProcessingConfig(
            input_folder=Path("."),  # Dummy input folder
            output_base=output_folder
        )
        
        processor = StructurProcessor(config)
        folder_stats = processor.get_folder_statistics()
        
        print_folder_statistics(folder_stats)
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


def print_processing_results(stats: dict) -> None:
    """Print processing results in a formatted way."""
    typer.echo("\n📊 PROCESSING RESULTS")
    typer.echo("=" * 50)
    
    # Basic stats
    typer.echo(f"Files processed: {stats.get('files_processed', 0)}")
    typer.echo(f"Coded blocks found: {stats.get('coded_blocks_found', 0)}")
    typer.echo(f"Malformed blocks found: {stats.get('malformed_blocks_found', 0)}")
    typer.echo(f"Duplicates found: {stats.get('duplicates_found', 0)}")
    typer.echo(f"Total words processed: {stats.get('total_words_processed', 0)}")

    # Folder stats
    if 'folder_stats' in stats:
        typer.echo("\n📁 FOLDER BREAKDOWN")
        typer.echo("-" * 30)
        for folder_type, folder_info in stats['folder_stats'].items():
            file_count = folder_info.get('file_count', 0)
            word_count = folder_info.get('total_words', 0)
            typer.echo(f"{folder_type:15}: {file_count:3d} files, {word_count:6d} words")
    
    # Errors
    if stats.get('errors'):
        typer.echo(f"\n⚠️  ERRORS ({len(stats['errors'])})")
        typer.echo("-" * 20)
        for error in stats['errors'][:5]:  # Show first 5 errors
            typer.echo(f"  • {error}")
        if len(stats['errors']) > 5:
            typer.echo(f"  ... and {len(stats['errors']) - 5} more errors")


def print_folder_statistics(folder_stats: dict) -> None:
    """Print folder statistics in a formatted way."""
    typer.echo("\n📊 FOLDER STATISTICS")
    typer.echo("=" * 50)
    
    total_files = 0
    total_words = 0
    
    for folder_type, stats in folder_stats.items():
        file_count = stats.get('file_count', 0)
        word_count = stats.get('total_words', 0)
        size_mb = stats.get('total_size_bytes', 0) / (1024 * 1024)
        
        total_files += file_count
        total_words += word_count
        
        typer.echo(f"{folder_type:15}: {file_count:3d} files, {word_count:6d} words, {size_mb:.1f} MB")
    
    typer.echo("-" * 50)
    typer.echo(f"{'TOTAL':15}: {total_files:3d} files, {total_words:6d} words")


def process_folder(
    input_folder: str | Path,
    output_folder: str | Path,
    coded_folder: str = "coded",
    uncoded_folder: str = "uncoded", 
    duplicates_folder: str = "duplicates",
    malformed_folder: str = "malformed",
    originals_folder: str = "originals",
    verbose: bool = False,
    codes_file: Optional[Path] = None,
    auto_codes_file: bool = False,
    regenerate_codes: bool = False
) -> dict:
    """
    Process a folder of markdown files programmatically.

    Args:
        input_folder: Path to folder containing markdown files
        output_folder: Path to output folder 
        coded_folder: Name of coded content subfolder
        uncoded_folder: Name of uncoded content subfolder
        duplicates_folder: Name of duplicates subfolder
        malformed_folder: Name of malformed content subfolder
        originals_folder: Name of originals subfolder
        verbose: Enable verbose logging

    Returns:
        Dictionary containing processing statistics
    """
    # Setup logging
    setup_logging(verbose)
    
    # Convert to Path objects
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Create configuration
    config = ProcessingConfig(
        input_folder=input_path,
        output_base=output_path,
        coded_folder=coded_folder,
        uncoded_folder=uncoded_folder,
        duplicates_folder=duplicates_folder,
        malformed_folder=malformed_folder,
        preserve_codes_in_output=False,
        append_mode=True,
        global_duplicate_detection=True,
        codes_file=codes_file,
        auto_codes_file=auto_codes_file,
        regenerate_codes=regenerate_codes
    )
    
    # Create and run processor
    processor = StructurProcessor(config)
    results = processor.process_folder()
    
    return results


@app.command()
def version():
    """Show version information."""
    from src import __version__
    typer.echo(f"Structur New v{__version__}")
    typer.echo("A modular, reliable text processing system")


@app.command()
def main(
    input_path: Path = typer.Argument(
        ...,
        help="Path to the input file or folder to process",
        exists=True
    ),
    output_folder: Optional[Path] = typer.Option(
        None,
        "--output-folder",
        help="Path to the output folder (defaults to input_path_structur)"
    ),
    coded_folder: str = typer.Option(
        "coded",
        "--coded-folder",
        help="Name of the folder for coded content"
    ),
    uncoded_folder: str = typer.Option(
        "uncoded",
        "--uncoded-folder", 
        help="Name of the folder for uncoded content"
    ),
    duplicates_folder: str = typer.Option(
        "duplicates",
        "--duplicates-folder",
        help="Name of the folder for duplicate content"
    ),
    malformed_folder: str = typer.Option(
        "malformed",
        "--malformed-folder",
        help="Name of the folder for malformed content"
    ),
    preserve_codes: bool = typer.Option(
        False,
        "--preserve-codes",
        help="Preserve code markers in the output files"
    ),
    append_mode: bool = typer.Option(
        True,
        "--append/--overwrite",
        help="Append to existing files instead of overwriting"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    ),
    codes_file: Optional[Path] = typer.Option(
        None,
        "--codes-file",
        help="Path to codes.txt file to read master codes list"
    ),
    auto_codes_file: bool = typer.Option(
        False,
        "--auto-codes-file",
        help="Automatically create/update codes.txt with extracted codes"
    ),
    regenerate_codes: bool = typer.Option(
        False,
        "--regenerate-codes",
        help="Regenerate empty files for all codes in codes.txt"
    )
):
    """
    Main command for processing files or folders.
    
    This is an alias for the process command that works with both files and folders.
    """
    setup_logging(verbose)
    
    # Determine if input is a file or folder
    if input_path.is_file():
        # Process single file
        if output_folder is None:
            output_folder = input_path.parent / f"{input_path.stem}_structur"
        
        # Create configuration for single file
        config = ProcessingConfig(
            input_folder=input_path.parent,
            output_base=output_folder,
            coded_folder=coded_folder,
            uncoded_folder=uncoded_folder,
            duplicates_folder=duplicates_folder,
            malformed_folder=malformed_folder,
            preserve_codes_in_output=preserve_codes,
            append_mode=append_mode,
            global_duplicate_detection=True,
            codes_file=codes_file,
            auto_codes_file=auto_codes_file,
            regenerate_codes=regenerate_codes
        )
        
        # Process the single file
        processor = StructurProcessor(config)
        success = processor.process_single_file(input_path)
        
        if success:
            # Display results
            stats = processor.get_processing_statistics()
            print_processing_results(stats)
            typer.echo("✅ File processed successfully!")
        else:
            typer.echo("❌ File processing failed", err=True)
            raise typer.Exit(1)
            
    elif input_path.is_dir():
        # Process folder
        if output_folder is None:
            output_folder = input_path.parent / f"{input_path.name}_structur"
        
        # Create configuration for folder processing
        config = ProcessingConfig(
            input_folder=input_path,
            output_base=output_folder,
            coded_folder=coded_folder,
            uncoded_folder=uncoded_folder,
            duplicates_folder=duplicates_folder,
            malformed_folder=malformed_folder,
            preserve_codes_in_output=preserve_codes,
            append_mode=append_mode,
            global_duplicate_detection=True,
            codes_file=codes_file,
            auto_codes_file=auto_codes_file,
            regenerate_codes=regenerate_codes
        )
        
        # Process the folder
        processor = StructurProcessor(config)
        stats = processor.process_folder()
        
        # Display results
        print_processing_results(stats)
        typer.echo("✅ Folder processed successfully!")
    else:
        typer.echo("❌ Input path must be a file or directory", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()