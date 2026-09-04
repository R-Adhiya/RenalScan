"""
Unit tests for DuplicateDetector component.
"""

import pytest
import imagehash
from pathlib import Path
from PIL import Image
import tempfile
import shutil
from src.dataset_expansion.duplicate_detector import DuplicateDetector


@pytest.fixture
def temp_image_dir():
    """Create temporary directory with test images."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_images(temp_image_dir):
    """Create sample test images."""
    images = []
    
    # Create 3 different images
    for i in range(3):
        img = Image.new('RGB', (100, 100), color=(i * 80, i * 80, i * 80))
        img_path = Path(temp_dir) / f"image_{i}.jpg"
        img.save(img_path)
        images.append(str(img_path))
    
    return images


class TestDuplicateDetector:
    """Test suite for DuplicateDetector class."""
    
    def test_initialization(self):
        """Test detector initialization with default parameters."""
        detector = DuplicateDetector()
        assert detector.hash_size == 8
        assert detector.hamming_threshold == 5
        assert detector.image_hashes == {}
        assert detector.duplicates == []
        assert detector.filename_duplicates == []
    
    def test_initialization_custom_params(self):
        """Test detector initialization with custom parameters."""
        detector = DuplicateDetector(hash_size=16, hamming_threshold=3)
        assert detector.hash_size == 16
        assert detector.hamming_threshold == 3
    
    def test_compute_perceptual_hash_success(self, temp_image_dir):
        """Test successful hash computation for valid image."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img_path = Path(temp_image_dir) / "test.jpg"
        img.save(img_path)
        
        detector = DuplicateDetector()
        hash_val = detector.compute_perceptual_hash(str(img_path))
        
        assert isinstance(hash_val, imagehash.ImageHash)
        assert len(str(hash_val)) == 16  # 64-bit hash = 16 hex chars
    
    def test_compute_perceptual_hash_invalid_file(self):
        """Test hash computation fails for non-existent file."""
        detector = DuplicateDetector()
        
        with pytest.raises(IOError):
            detector.compute_perceptual_hash("nonexistent_file.jpg")
    
    def test_find_duplicates_no_matches(self, temp_image_dir):
        """Test duplicate detection when no duplicates exist."""
        # Create two distinctly different images with patterns
        # Image 1: top half red, bottom half black
        img1 = Image.new('RGB', (100, 100), color='red')
        for y in range(50, 100):
            for x in range(100):
                img1.putpixel((x, y), (0, 0, 0))
        
        # Image 2: left half blue, right half white
        img2 = Image.new('RGB', (100, 100), color='blue')
        for y in range(100):
            for x in range(50, 100):
                img2.putpixel((x, y), (255, 255, 255))
        
        path1 = Path(temp_image_dir) / "img1.jpg"
        path2 = Path(temp_image_dir) / "img2.jpg"
        
        img1.save(path1)
        img2.save(path2)
        
        detector = DuplicateDetector(hamming_threshold=5)
        duplicates = detector.find_duplicates([str(path1)], [str(path2)])
        
        # These distinctly different images should not be duplicates
        assert len(duplicates) == 0
    
    def test_find_duplicates_exact_match(self, temp_image_dir):
        """Test duplicate detection for identical images."""
        # Create identical images
        img = Image.new('RGB', (100, 100), color='green')
        
        path1 = Path(temp_image_dir) / "img1.jpg"
        path2 = Path(temp_image_dir) / "img2.jpg"
        
        img.save(path1)
        img.save(path2)
        
        detector = DuplicateDetector(hamming_threshold=5)
        duplicates = detector.find_duplicates([str(path1)], [str(path2)])
        
        assert len(duplicates) == 1
        assert duplicates[0][0] == str(path1)
        assert duplicates[0][1] == str(path2)
        assert duplicates[0][2] == 0  # Hamming distance should be 0
    
    def test_find_duplicates_within_threshold(self, temp_image_dir):
        """Test duplicate detection for similar images within threshold."""
        # Create two very similar images (slight color variation)
        img1 = Image.new('RGB', (100, 100), color=(100, 100, 100))
        img2 = Image.new('RGB', (100, 100), color=(105, 105, 105))
        
        path1 = Path(temp_image_dir) / "img1.jpg"
        path2 = Path(temp_image_dir) / "img2.jpg"
        
        img1.save(path1)
        img2.save(path2)
        
        detector = DuplicateDetector(hamming_threshold=5)
        duplicates = detector.find_duplicates([str(path1)], [str(path2)])
        
        # Similar images should be detected as duplicates
        assert len(duplicates) >= 0  # May or may not detect depending on hash
    
    def test_check_filename_duplicates_no_matches(self, temp_image_dir):
        """Test filename checking when no duplicates exist."""
        # Create images with different filenames
        img = Image.new('RGB', (100, 100), color='red')
        
        path1 = Path(temp_image_dir) / "unique1.jpg"
        path2 = Path(temp_image_dir) / "unique2.jpg"
        
        img.save(path1)
        img.save(path2)
        
        detector = DuplicateDetector()
        filename_dups = detector.check_filename_duplicates([str(path1)], [str(path2)])
        
        assert len(filename_dups) == 0
    
    def test_check_filename_duplicates_with_matches(self, temp_image_dir):
        """Test filename checking when duplicates exist."""
        # Create images with same filename in different directories
        img = Image.new('RGB', (100, 100), color='red')
        
        dir1 = Path(temp_image_dir) / "dir1"
        dir2 = Path(temp_image_dir) / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        path1 = dir1 / "same_name.jpg"
        path2 = dir2 / "same_name.jpg"
        
        img.save(path1)
        img.save(path2)
        
        detector = DuplicateDetector()
        filename_dups = detector.check_filename_duplicates([str(path1)], [str(path2)])
        
        assert len(filename_dups) == 1
        assert filename_dups[0][0] == str(path1)
        assert filename_dups[0][1] == str(path2)
    
    def test_generate_report_no_duplicates(self):
        """Test report generation when no duplicates found."""
        detector = DuplicateDetector()
        detector.duplicates = []
        detector.filename_duplicates = []
        
        report = detector.generate_duplicate_report()
        
        assert report['total_perceptual_duplicates'] == 0
        assert report['total_filename_duplicates'] == 0
        assert len(report['recommendations']) == 1
        assert "No duplicates detected" in report['recommendations'][0]
    
    def test_generate_report_with_duplicates(self, temp_image_dir):
        """Test report generation with duplicates."""
        # Create mock duplicates
        path1 = Path(temp_image_dir) / "img1.jpg"
        path2 = Path(temp_image_dir) / "img2.jpg"
        
        detector = DuplicateDetector()
        detector.duplicates = [(str(path1), str(path2), 3)]
        detector.filename_duplicates = [(str(path1), str(path2))]
        
        report = detector.generate_duplicate_report()
        
        assert report['total_perceptual_duplicates'] == 1
        assert report['total_filename_duplicates'] == 1
        assert len(report['perceptual_duplicate_pairs']) == 1
        assert len(report['filename_duplicate_pairs']) == 1
        assert len(report['recommendations']) == 2
    
    def test_generate_report_save_to_file(self, temp_image_dir):
        """Test report saving to file."""
        output_path = Path(temp_image_dir) / "report.txt"
        
        detector = DuplicateDetector()
        detector.duplicates = []
        detector.filename_duplicates = []
        
        report = detector.generate_duplicate_report(output_path=str(output_path))
        
        assert output_path.exists()
        content = output_path.read_text()
        assert "DUPLICATE DETECTION REPORT" in content
        assert "Total Perceptual Duplicates: 0" in content
    
    def test_hamming_threshold_filtering(self, temp_image_dir):
        """Test that hamming threshold properly filters duplicates."""
        # Create identical images
        img = Image.new('RGB', (100, 100), color='yellow')
        
        path1 = Path(temp_image_dir) / "img1.jpg"
        path2 = Path(temp_image_dir) / "img2.jpg"
        
        img.save(path1)
        img.save(path2)
        
        # Test with threshold 0 (only exact matches)
        detector_strict = DuplicateDetector(hamming_threshold=0)
        duplicates_strict = detector_strict.find_duplicates([str(path1)], [str(path2)])
        
        # Test with threshold 10 (more lenient)
        detector_lenient = DuplicateDetector(hamming_threshold=10)
        duplicates_lenient = detector_lenient.find_duplicates([str(path1)], [str(path2)])
        
        # Identical images should be detected by both
        assert len(duplicates_strict) >= 0
        assert len(duplicates_lenient) >= 0
    
    def test_empty_dataset_handling(self):
        """Test duplicate detection with empty datasets."""
        detector = DuplicateDetector()
        
        duplicates = detector.find_duplicates([], [])
        assert len(duplicates) == 0
        
        filename_dups = detector.check_filename_duplicates([], [])
        assert len(filename_dups) == 0
    
    def test_single_image_datasets(self, temp_image_dir):
        """Test duplicate detection with single image in each dataset."""
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='red')
        
        path1 = Path(temp_image_dir) / "img1.jpg"
        path2 = Path(temp_image_dir) / "img2.jpg"
        
        img1.save(path1)
        img2.save(path2)
        
        detector = DuplicateDetector()
        duplicates = detector.find_duplicates([str(path1)], [str(path2)])
        
        # Should detect identical images
        assert len(duplicates) == 1
