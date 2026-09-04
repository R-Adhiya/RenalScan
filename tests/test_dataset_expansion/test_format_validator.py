"""
Basic tests for FormatValidator to verify implementation.
"""

import pytest
import tempfile
from pathlib import Path
from PIL import Image
import os
from src.dataset_expansion.validators import FormatValidator, FormatReport, ResolutionReport, ConsistencyReport


def create_test_image(path: str, format: str, size: tuple):
    """Helper to create a test image."""
    img = Image.new('RGB', size, color='red')
    img.save(path, format=format)


def test_analyze_formats_single_format():
    """Test format analysis with a single format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images
        create_test_image(os.path.join(tmpdir, 'img1.jpg'), 'JPEG', (512, 512))
        create_test_image(os.path.join(tmpdir, 'img2.jpg'), 'JPEG', (512, 512))
        create_test_image(os.path.join(tmpdir, 'img3.jpg'), 'JPEG', (512, 512))
        
        validator = FormatValidator([tmpdir])
        report = validator.analyze_formats()
        
        assert report.total_images == 3
        assert report.format_counts.get('JPG', 0) == 3


def test_analyze_formats_mixed_formats():
    """Test format analysis with mixed formats."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images with different formats
        create_test_image(os.path.join(tmpdir, 'img1.jpg'), 'JPEG', (512, 512))
        create_test_image(os.path.join(tmpdir, 'img2.png'), 'PNG', (512, 512))
        create_test_image(os.path.join(tmpdir, 'img3.jpg'), 'JPEG', (512, 512))
        
        validator = FormatValidator([tmpdir])
        report = validator.analyze_formats()
        
        assert report.total_images == 3
        assert report.format_counts.get('JPG', 0) == 2
        assert report.format_counts.get('PNG', 0) == 1


def test_analyze_resolutions_single_resolution():
    """Test resolution analysis with a single resolution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images with same resolution
        create_test_image(os.path.join(tmpdir, 'img1.jpg'), 'JPEG', (512, 512))
        create_test_image(os.path.join(tmpdir, 'img2.jpg'), 'JPEG', (512, 512))
        
        validator = FormatValidator([tmpdir])
        report = validator.analyze_resolutions()
        
        assert report.total_images == 2
        assert report.resolution_counts.get((512, 512), 0) == 2


def test_analyze_resolutions_mixed_resolutions():
    """Test resolution analysis with mixed resolutions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images with different resolutions
        create_test_image(os.path.join(tmpdir, 'img1.jpg'), 'JPEG', (512, 512))
        create_test_image(os.path.join(tmpdir, 'img2.jpg'), 'JPEG', (1024, 1024))
        create_test_image(os.path.join(tmpdir, 'img3.jpg'), 'JPEG', (512, 512))
        
        validator = FormatValidator([tmpdir])
        report = validator.analyze_resolutions()
        
        assert report.total_images == 3
        assert report.resolution_counts.get((512, 512), 0) == 2
        assert report.resolution_counts.get((1024, 1024), 0) == 1


def test_check_consistency_all_match():
    """Test consistency check when all images match target."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images matching target specs
        create_test_image(os.path.join(tmpdir, 'img1.jpg'), 'JPEG', (512, 512))
        create_test_image(os.path.join(tmpdir, 'img2.jpg'), 'JPEG', (512, 512))
        
        validator = FormatValidator([tmpdir])
        report = validator.check_consistency('JPG', (512, 512))
        
        assert report.total_images == 2
        assert report.format_matches == 2
        assert report.format_mismatches == 0
        assert report.resolution_matches == 2
        assert report.resolution_mismatches == 0
        assert len(report.mismatched_files) == 0


def test_check_consistency_format_mismatch():
    """Test consistency check with format mismatches."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images with wrong format
        create_test_image(os.path.join(tmpdir, 'img1.jpg'), 'JPEG', (512, 512))
        create_test_image(os.path.join(tmpdir, 'img2.png'), 'PNG', (512, 512))
        
        validator = FormatValidator([tmpdir])
        report = validator.check_consistency('JPG', (512, 512))
        
        assert report.total_images == 2
        assert report.format_matches == 1
        assert report.format_mismatches == 1
        assert len(report.mismatched_files) == 1
        assert report.mismatched_files[0]['format_mismatch'] == True


def test_check_consistency_resolution_mismatch():
    """Test consistency check with resolution mismatches."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images with wrong resolution
        create_test_image(os.path.join(tmpdir, 'img1.jpg'), 'JPEG', (512, 512))
        create_test_image(os.path.join(tmpdir, 'img2.jpg'), 'JPEG', (1024, 1024))
        
        validator = FormatValidator([tmpdir])
        report = validator.check_consistency('JPG', (512, 512))
        
        assert report.total_images == 2
        assert report.resolution_matches == 1
        assert report.resolution_mismatches == 1
        assert len(report.mismatched_files) == 1
        assert report.mismatched_files[0]['resolution_mismatch'] == True


def test_recommend_preprocessing_no_issues():
    """Test preprocessing recommendations when no issues found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create perfect images
        create_test_image(os.path.join(tmpdir, 'img1.jpg'), 'JPEG', (512, 512))
        
        validator = FormatValidator([tmpdir])
        report = validator.check_consistency('JPG', (512, 512))
        recommendations = validator.recommend_preprocessing(report)
        
        assert len(recommendations) == 1
        assert "no preprocessing needed" in recommendations[0].lower()


def test_recommend_preprocessing_format_issues():
    """Test preprocessing recommendations for format issues."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create images with format issues
        create_test_image(os.path.join(tmpdir, 'img1.png'), 'PNG', (512, 512))
        
        validator = FormatValidator([tmpdir])
        report = validator.check_consistency('JPG', (512, 512))
        recommendations = validator.recommend_preprocessing(report)
        
        # Should recommend format conversion
        recommendations_text = ' '.join(recommendations)
        assert 'format' in recommendations_text.lower()
        assert 'convert' in recommendations_text.lower() or 'mismatch' in recommendations_text.lower()


def test_recommend_preprocessing_resolution_issues():
    """Test preprocessing recommendations for resolution issues."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create images with resolution issues
        create_test_image(os.path.join(tmpdir, 'img1.jpg'), 'JPEG', (1024, 1024))
        
        validator = FormatValidator([tmpdir])
        report = validator.check_consistency('JPG', (512, 512))
        recommendations = validator.recommend_preprocessing(report)
        
        # Should recommend resizing
        recommendations_text = ' '.join(recommendations)
        assert 'resolution' in recommendations_text.lower() or 'resize' in recommendations_text.lower()


def test_multiple_directories():
    """Test validator with multiple image directories."""
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            # Create images in both directories
            create_test_image(os.path.join(tmpdir1, 'img1.jpg'), 'JPEG', (512, 512))
            create_test_image(os.path.join(tmpdir2, 'img2.jpg'), 'JPEG', (512, 512))
            
            validator = FormatValidator([tmpdir1, tmpdir2])
            report = validator.analyze_formats()
            
            assert report.total_images == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
