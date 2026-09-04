"""
Property-based tests for RoboflowDownloader.

Tests verify correctness properties for download result reporting
and other downloader functionality.
"""

import pytest
from hypothesis import given, strategies as st

from src.dataset_expansion.downloader import DownloadResult, RoboflowDownloader


# Feature: dataset-expansion, Property 1: Download Reporting Completeness
@given(
    train_count=st.integers(min_value=0, max_value=10000),
    valid_count=st.integers(min_value=0, max_value=5000),
    test_count=st.integers(min_value=0, max_value=5000),
    success=st.booleans(),
    download_path=st.text(min_size=1, max_size=100),
)
def test_property_download_result_completeness(
    train_count: int,
    valid_count: int,
    test_count: int,
    success: bool,
    download_path: str,
):
    """
    Property 1: Download Reporting Completeness
    
    For any download result with varying image counts across splits,
    the DownloadResult should accurately report:
    - Total images = sum of all splits
    - Individual split counts
    - Success status
    - Download path
    
    This validates that download result reporting is complete and accurate
    regardless of the distribution of images across splits.
    
    Validates: Requirements 1.3
    """
    # Calculate expected total
    expected_total = train_count + valid_count + test_count
    
    # Create DownloadResult with generated values
    result = DownloadResult(
        success=success,
        total_images=expected_total,
        train_images=train_count,
        valid_images=valid_count,
        test_images=test_count,
        download_path=download_path,
        error_message=None if success else "Mock error"
    )
    
    # Property 1: Total images should equal sum of splits
    assert result.total_images == train_count + valid_count + test_count, (
        f"Total images ({result.total_images}) should equal "
        f"train ({train_count}) + valid ({valid_count}) + test ({test_count})"
    )
    
    # Property 2: Individual counts should be preserved
    assert result.train_images == train_count, (
        f"Train count mismatch: expected {train_count}, got {result.train_images}"
    )
    assert result.valid_images == valid_count, (
        f"Valid count mismatch: expected {valid_count}, got {result.valid_images}"
    )
    assert result.test_images == test_count, (
        f"Test count mismatch: expected {test_count}, got {result.test_images}"
    )
    
    # Property 3: Success status should be preserved
    assert result.success == success, (
        f"Success status mismatch: expected {success}, got {result.success}"
    )
    
    # Property 4: Download path should be preserved
    assert result.download_path == download_path, (
        f"Download path mismatch: expected '{download_path}', got '{result.download_path}'"
    )
    
    # Property 5: Error message should be present if not successful
    if not success:
        assert result.error_message is not None, (
            "Error message should be present when success is False"
        )


# Feature: dataset-expansion, Property 1: Download Reporting Completeness (structure validation)
@given(
    train_count=st.integers(min_value=0, max_value=10000),
    valid_count=st.integers(min_value=0, max_value=5000),
    test_count=st.integers(min_value=0, max_value=5000),
)
def test_property_download_result_structure_info(
    train_count: int,
    valid_count: int,
    test_count: int,
):
    """
    Property 1: Download Reporting Completeness (Structure Info)
    
    For any download result, the report should contain complete structure
    information about the downloaded dataset, including all three standard
    YOLO splits (train, valid, test).
    
    This validates that the download result provides sufficient information
    about the dataset structure for verification purposes.
    
    Validates: Requirements 1.3
    """
    expected_total = train_count + valid_count + test_count
    
    result = DownloadResult(
        success=True,
        total_images=expected_total,
        train_images=train_count,
        valid_images=valid_count,
        test_images=test_count,
        download_path="/mock/path/to/dataset"
    )
    
    # Property: Result contains all required structure fields
    assert hasattr(result, 'train_images'), "Missing train_images field"
    assert hasattr(result, 'valid_images'), "Missing valid_images field"
    assert hasattr(result, 'test_images'), "Missing test_images field"
    assert hasattr(result, 'total_images'), "Missing total_images field"
    assert hasattr(result, 'download_path'), "Missing download_path field"
    assert hasattr(result, 'success'), "Missing success field"
    
    # Property: All counts should be non-negative
    assert result.train_images >= 0, "Train count should be non-negative"
    assert result.valid_images >= 0, "Valid count should be non-negative"
    assert result.test_images >= 0, "Test count should be non-negative"
    assert result.total_images >= 0, "Total count should be non-negative"
    
    # Property: Total should be consistent with splits
    assert result.total_images == (
        result.train_images + result.valid_images + result.test_images
    ), "Total should equal sum of all splits"


# Unit test for zero-image edge case
def test_download_result_empty_dataset():
    """
    Edge case: Download result with no images should still be valid.
    """
    result = DownloadResult(
        success=True,
        total_images=0,
        train_images=0,
        valid_images=0,
        test_images=0,
        download_path="/empty/dataset"
    )
    
    assert result.success is True
    assert result.total_images == 0
    assert result.train_images == 0
    assert result.valid_images == 0
    assert result.test_images == 0


# Unit test for error case
def test_download_result_with_error():
    """
    Edge case: Download failure should report error message.
    """
    error_msg = "Network timeout"
    result = DownloadResult(
        success=False,
        total_images=0,
        train_images=0,
        valid_images=0,
        test_images=0,
        download_path="",
        error_message=error_msg
    )
    
    assert result.success is False
    assert result.error_message == error_msg
    assert result.total_images == 0
