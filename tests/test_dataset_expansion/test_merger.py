"""
Unit tests for DatasetMerger component.

Tests dataset merging functionality including:
- Sample collection from multiple datasets
- Stratified train/valid/test splitting
- File copying to proper directory structure
- YAML configuration updates
"""

import os
import shutil
import tempfile
import yaml
import pytest
from pathlib import Path
from PIL import Image
import numpy as np

from src.dataset_expansion.merger import DatasetMerger, Sample, DatasetSplits


class TestDatasetMerger:
    """Test suite for DatasetMerger component."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_base = tempfile.mkdtemp()
        current_dir = os.path.join(temp_base, "current_dataset")
        source_di
