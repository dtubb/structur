"""
Structur - A modular text processing system for extracting and organizing coded content.

This package provides a reliable, modular approach to processing text files with
coded blocks while ensuring no data loss through copy-based operations.
"""

__version__ = "2.0.0"
__author__ = "Structur Project"

from .models.config import ProcessingConfig
from .processors.main_processor import StructurProcessor

__all__ = ["ProcessingConfig", "StructurProcessor"] 