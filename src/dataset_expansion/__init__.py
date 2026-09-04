"""
Dataset Expansion Module

This module provides functionality for expanding the RenalScan training dataset
by merging additional datasets from Roboflow with proper verification and validation.

Components:
- RoboflowDownloader: Download datasets from Roboflow
- ClassValidator: Validate class definitions compatibility
- FormatValidator: Check image format and resolution consistency
- QualityChecker: Visual validation of annotation quality
- DuplicateDetector: Identify duplicate images
- DatasetMerger: Combine datasets with proper splits
- ReportGenerator: Generate comprehensive verification reports
"""

from .validators import ClassValidator, FormatValidator, ValidationResult
from .duplicate_detector import DuplicateDetector
from .merger import DatasetMerger, Sample, DatasetSplits
from .report_generator import ReportGenerator

__version__ = "1.0.0"

__all__ = [
    'ClassValidator',
    'FormatValidator',
    'ValidationResult',
    'DuplicateDetector',
    'DatasetMerger',
    'Sample',
    'DatasetSplits',
    'ReportGenerator',
]
