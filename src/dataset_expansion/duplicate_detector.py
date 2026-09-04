"""
Duplicate detection for dataset expansion.

This module implements perceptual hashing and filename-based duplicate detection
to identify duplicate images between datasets.
"""

import imagehash
from pathlib import Path
from PIL import Image
from typing import Dict, List, Tuple, Set
from collections import defaultdict


class DuplicateDetector:
    """
    Detects duplicate images using perceptual hashing and filename comparison.
    
    Uses Hamming distance ≤ 5 threshold for perceptual hash matching.
    """
    
    def __init__(self, hash_size: int = 8, hamming_threshold: int = 5):
        """
        Initialize duplicate detector.
        
        Args:
            hash_size: Size of perceptual hash (default 8 for 64-bit hash)
            hamming_threshold: Maximum Hamming distance for duplicate detection (default 5)
        """
        self.hash_size = hash_size
        self.hamming_threshold = hamming_threshold
        self.image_hashes: Dict[str, imagehash.ImageHash] = {}
        self.duplicates: List[Tuple[str, str, int]] = []
        self.filename_duplicates: List[Tuple[str, str]] = []
    
    def compute_perceptual_hash(self, image_path: str) -> imagehash.ImageHash:
        """
        Compute perceptual hash for an image using average hashing.
        
        Args:
            image_path: Path to image file
            
        Returns:
            ImageHash object representing the perceptual hash
            
        Raises:
            IOError: If image cannot be opened or processed
        """
        try:
            with Image.open(image_path) as img:
                # Use average hash for perceptual hashing
                return imagehash.average_hash(img, hash_size=self.hash_size)
        except Exception as e:
            raise IOError(f"Failed to compute hash for {image_path}: {str(e)}")
    
    def find_duplicates(
        self,
        dataset1_images: List[str],
        dataset2_images: List[str]
    ) -> List[Tuple[str, str, int]]:
        """
        Find duplicate images between two datasets using perceptual hashing.
        
        Computes hashes for all images and identifies pairs with Hamming distance ≤ threshold.
        
        Args:
            dataset1_images: List of image paths from first dataset
            dataset2_images: List of image paths from second dataset
            
        Returns:
            List of tuples (image1_path, image2_path, hamming_distance)
        """
        self.duplicates = []
        self.image_hashes = {}
        
        # Compute hashes for dataset1
        print(f"Computing hashes for {len(dataset1_images)} images from dataset 1...")
        for img_path in dataset1_images:
            try:
                hash_val = self.compute_perceptual_hash(img_path)
                self.image_hashes[img_path] = hash_val
            except IOError as e:
                print(f"Warning: {e}")
                continue
        
        # Compute hashes for dataset2 and compare
        print(f"Computing hashes for {len(dataset2_images)} images from dataset 2...")
        dataset2_hashes = {}
        for img_path in dataset2_images:
            try:
                hash_val = self.compute_perceptual_hash(img_path)
                dataset2_hashes[img_path] = hash_val
            except IOError as e:
                print(f"Warning: {e}")
                continue
        
        # Find duplicates by comparing hashes
        print(f"Comparing {len(self.image_hashes)} vs {len(dataset2_hashes)} hashes...")
        for path1, hash1 in self.image_hashes.items():
            for path2, hash2 in dataset2_hashes.items():
                hamming_dist = hash1 - hash2  # imagehash overloads - operator for Hamming distance
                if hamming_dist <= self.hamming_threshold:
                    self.duplicates.append((path1, path2, hamming_dist))
        
        return self.duplicates
    
    def check_filename_duplicates(
        self,
        dataset1_images: List[str],
        dataset2_images: List[str]
    ) -> List[Tuple[str, str]]:
        """
        Check for exact filename matches between datasets.
        
        Args:
            dataset1_images: List of image paths from first dataset
            dataset2_images: List of image paths from second dataset
            
        Returns:
            List of tuples (image1_path, image2_path) with matching filenames
        """
        self.filename_duplicates = []
        
        # Build filename to path mapping for dataset1
        filename_map: Dict[str, str] = {}
        for img_path in dataset1_images:
            filename = Path(img_path).name
            filename_map[filename] = img_path
        
        # Check dataset2 filenames against dataset1
        for img_path in dataset2_images:
            filename = Path(img_path).name
            if filename in filename_map:
                self.filename_duplicates.append((filename_map[filename], img_path))
        
        return self.filename_duplicates
    
    def generate_duplicate_report(self, output_path: str = None) -> Dict:
        """
        Generate comprehensive duplicate detection report.
        
        Args:
            output_path: Optional path to save report as text file
            
        Returns:
            Dictionary containing:
                - total_perceptual_duplicates: Count of perceptual hash duplicates
                - total_filename_duplicates: Count of filename duplicates
                - perceptual_duplicate_pairs: List of duplicate details
                - filename_duplicate_pairs: List of filename match details
                - recommendations: List of recommended actions
        """
        report = {
            'total_perceptual_duplicates': len(self.duplicates),
            'total_filename_duplicates': len(self.filename_duplicates),
            'perceptual_duplicate_pairs': [],
            'filename_duplicate_pairs': [],
            'recommendations': []
        }
        
        # Add perceptual duplicate details
        for path1, path2, dist in self.duplicates:
            report['perceptual_duplicate_pairs'].append({
                'dataset1_image': path1,
                'dataset2_image': path2,
                'hamming_distance': dist
            })
        
        # Add filename duplicate details
        for path1, path2 in self.filename_duplicates:
            report['filename_duplicate_pairs'].append({
                'dataset1_image': path1,
                'dataset2_image': path2
            })
        
        # Generate recommendations
        if report['total_perceptual_duplicates'] > 0:
            report['recommendations'].append(
                f"Found {report['total_perceptual_duplicates']} perceptual duplicates. "
                f"Consider removing images from dataset 2 to avoid redundancy."
            )
        
        if report['total_filename_duplicates'] > 0:
            report['recommendations'].append(
                f"Found {report['total_filename_duplicates']} filename duplicates. "
                f"These may be identical images or require renaming to avoid conflicts."
            )
        
        if report['total_perceptual_duplicates'] == 0 and report['total_filename_duplicates'] == 0:
            report['recommendations'].append(
                "No duplicates detected. Datasets can be safely merged."
            )
        
        # Save report to file if requested
        if output_path:
            self._save_report_to_file(report, output_path)
        
        return report
    
    def _save_report_to_file(self, report: Dict, output_path: str):
        """Save duplicate detection report to text file."""
        with open(output_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("DUPLICATE DETECTION REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Total Perceptual Duplicates: {report['total_perceptual_duplicates']}\n")
            f.write(f"Total Filename Duplicates: {report['total_filename_duplicates']}\n\n")
            
            if report['perceptual_duplicate_pairs']:
                f.write("-" * 60 + "\n")
                f.write("PERCEPTUAL HASH DUPLICATES\n")
                f.write("-" * 60 + "\n")
                for dup in report['perceptual_duplicate_pairs']:
                    f.write(f"\nDataset 1: {dup['dataset1_image']}\n")
                    f.write(f"Dataset 2: {dup['dataset2_image']}\n")
                    f.write(f"Hamming Distance: {dup['hamming_distance']}\n")
            
            if report['filename_duplicate_pairs']:
                f.write("\n" + "-" * 60 + "\n")
                f.write("FILENAME DUPLICATES\n")
                f.write("-" * 60 + "\n")
                for dup in report['filename_duplicate_pairs']:
                    f.write(f"\nDataset 1: {dup['dataset1_image']}\n")
                    f.write(f"Dataset 2: {dup['dataset2_image']}\n")
            
            f.write("\n" + "-" * 60 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 60 + "\n")
            for rec in report['recommendations']:
                f.write(f"\n• {rec}\n")
            
            f.write("\n" + "=" * 60 + "\n")
