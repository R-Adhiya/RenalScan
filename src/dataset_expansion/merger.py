"""
Dataset merging for dataset expansion.

This module implements dataset merging with stratified train/valid/test splits,
file copying, and data.yaml configuration management.
"""

import os
import shutil
import random
import yaml
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Sample:
    """Represents an image-label pair in the dataset."""
    image_path: str
    label_path: str
    source: str  # "current" or "roboflow"
    hash: str = ""  # Optional perceptual hash for duplicate detection


@dataclass
class DatasetSplits:
    """Holds train/valid/test splits of samples."""
    train: List[Sample]
    valid: List[Sample]
    test: List[Sample]
    
    def get_counts(self) -> Dict[str, int]:
        """Return count of samples in each split."""
        return {
            'train': len(self.train),
            'valid': len(self.valid),
            'test': len(self.test),
            'total': len(self.train) + len(self.valid) + len(self.test)
        }


class DatasetMerger:
    """
    Merges datasets with proper stratified train/valid/test splits.
    
    Combines current and source datasets, removes duplicates, creates
    70/15/15 splits, and updates configuration files.
    """
    
    def __init__(
        self,
        current_data_dir: str,
        source_data_dir: str,
        output_data_dir: str,
        duplicates_to_remove: List[str] = None
    ):
        """
        Initialize DatasetMerger with dataset directories.
        
        Args:
            current_data_dir: Path to current dataset directory
            source_data_dir: Path to source dataset directory
            output_data_dir: Path to output merged dataset directory
            duplicates_to_remove: List of image paths to exclude from merge
        """
        self.current_data_dir = current_data_dir
        self.source_data_dir = source_data_dir
        self.output_data_dir = output_data_dir
        self.duplicates_to_remove = set(duplicates_to_remove) if duplicates_to_remove else set()
    
    def collect_all_samples(self) -> List[Sample]:
        """
        Collect all image-label pairs from both datasets.
        
        Scans train/valid/test directories in both current and source datasets,
        matches image files with their corresponding label files, and excludes
        any duplicates marked for removal.
        
        Returns:
            List of Sample objects representing all valid image-label pairs
            
        Raises:
            FileNotFoundError: If required directories don't exist
        """
        samples = []
        
        # Define split directories to scan
        splits = ['train', 'valid', 'test']
        
        # Collect from current dataset
        for split in splits:
            images_dir = os.path.join(self.current_data_dir, split, 'images')
            labels_dir = os.path.join(self.current_data_dir, split, 'labels')
            
            if os.path.exists(images_dir) and os.path.exists(labels_dir):
                split_samples = self._collect_from_directory(
                    images_dir, labels_dir, source="current"
                )
                samples.extend(split_samples)
        
        # Collect from source dataset
        for split in splits:
            images_dir = os.path.join(self.source_data_dir, split, 'images')
            labels_dir = os.path.join(self.source_data_dir, split, 'labels')
            
            if os.path.exists(images_dir) and os.path.exists(labels_dir):
                split_samples = self._collect_from_directory(
                    images_dir, labels_dir, source="roboflow"
                )
                samples.extend(split_samples)
        
        # Filter out duplicates
        filtered_samples = [
            sample for sample in samples
            if sample.image_path not in self.duplicates_to_remove
        ]
        
        print(f"Collected {len(samples)} samples total")
        print(f"Filtered out {len(samples) - len(filtered_samples)} duplicates")
        print(f"Final sample count: {len(filtered_samples)}")
        
        return filtered_samples
    
    def _collect_from_directory(
        self,
        images_dir: str,
        labels_dir: str,
        source: str
    ) -> List[Sample]:
        """
        Collect samples from a single directory pair.
        
        Args:
            images_dir: Directory containing images
            labels_dir: Directory containing labels
            source: Source identifier ("current" or "roboflow")
            
        Returns:
            List of Sample objects from this directory
        """
        samples = []
        
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        image_files = [
            f for f in os.listdir(images_dir)
            if os.path.splitext(f)[1].lower() in image_extensions
        ]
        
        for image_file in image_files:
            image_path = os.path.join(images_dir, image_file)
            
            # Construct corresponding label path
            label_file = os.path.splitext(image_file)[0] + '.txt'
            label_path = os.path.join(labels_dir, label_file)
            
            # Only include if both image and label exist
            if os.path.exists(label_path):
                samples.append(Sample(
                    image_path=image_path,
                    label_path=label_path,
                    source=source
                ))
        
        return samples
    
    def stratified_split(
        self,
        samples: List[Sample],
        ratios: Tuple[float, float, float] = (0.70, 0.15, 0.15)
    ) -> DatasetSplits:
        """
        Create train/valid/test splits with specified ratios.
        
        Randomly shuffles samples and splits them according to the given ratios.
        Ensures random distribution across all splits.
        
        Args:
            samples: List of all samples to split
            ratios: Tuple of (train_ratio, valid_ratio, test_ratio), default (0.70, 0.15, 0.15)
            
        Returns:
            DatasetSplits object with train/valid/test splits
            
        Raises:
            ValueError: If ratios don't sum to 1.0 or if samples list is empty
        """
        # Validate ratios
        if abs(sum(ratios) - 1.0) > 1e-6:
            raise ValueError(f"Split ratios must sum to 1.0, got {sum(ratios)}")
        
        if not samples:
            raise ValueError("Cannot split empty sample list")
        
        train_ratio, valid_ratio, test_ratio = ratios
        
        # Shuffle samples for randomization
        shuffled_samples = samples.copy()
        random.shuffle(shuffled_samples)
        
        total_count = len(shuffled_samples)
        
        # Calculate split sizes
        train_size = int(train_ratio * total_count)
        valid_size = int(valid_ratio * total_count)
        # Test gets the remainder to ensure all samples are included
        
        # Split samples
        train_samples = shuffled_samples[:train_size]
        valid_samples = shuffled_samples[train_size:train_size + valid_size]
        test_samples = shuffled_samples[train_size + valid_size:]
        
        splits = DatasetSplits(
            train=train_samples,
            valid=valid_samples,
            test=test_samples
        )
        
        print(f"Split {total_count} samples:")
        print(f"  Train: {len(train_samples)} ({len(train_samples)/total_count*100:.1f}%)")
        print(f"  Valid: {len(valid_samples)} ({len(valid_samples)/total_count*100:.1f}%)")
        print(f"  Test: {len(test_samples)} ({len(test_samples)/total_count*100:.1f}%)")
        
        return splits
    
    def copy_files_to_splits(self, splits: DatasetSplits, output_dir: str) -> None:
        """
        Copy images and labels to their respective split directories.
        
        Creates YOLO directory structure and copies all files from splits
        to their designated directories:
        - train/images, train/labels
        - valid/images, valid/labels
        - test/images, test/labels
        
        Args:
            splits: DatasetSplits object with train/valid/test splits
            output_dir: Root output directory for merged dataset
            
        Raises:
            IOError: If file copy operations fail
            ValueError: If output directory cannot be created
        """
        # Create YOLO directory structure
        split_names = ['train', 'valid', 'test']
        for split_name in split_names:
            images_dir = os.path.join(output_dir, split_name, 'images')
            labels_dir = os.path.join(output_dir, split_name, 'labels')
            
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(labels_dir, exist_ok=True)
        
        # Copy files for each split
        self._copy_split_files(splits.train, os.path.join(output_dir, 'train'))
        self._copy_split_files(splits.valid, os.path.join(output_dir, 'valid'))
        self._copy_split_files(splits.test, os.path.join(output_dir, 'test'))
        
        print(f"Successfully copied all files to {output_dir}")
    
    def _copy_split_files(self, samples: List[Sample], split_dir: str) -> None:
        """
        Copy image and label files for a single split.
        
        Args:
            samples: List of samples to copy
            split_dir: Directory for this split (e.g., 'data/train')
        """
        images_dir = os.path.join(split_dir, 'images')
        labels_dir = os.path.join(split_dir, 'labels')
        
        for sample in samples:
            # Copy image
            image_filename = os.path.basename(sample.image_path)
            dest_image_path = os.path.join(images_dir, image_filename)
            shutil.copy2(sample.image_path, dest_image_path)
            
            # Copy label
            label_filename = os.path.basename(sample.label_path)
            dest_label_path = os.path.join(labels_dir, label_filename)
            shutil.copy2(sample.label_path, dest_label_path)
    
    def backup_original_data_yaml(self, data_yaml_path: str) -> None:
        """
        Create backup of original data.yaml configuration.
        
        Creates a timestamped backup file to preserve the original configuration
        before making any modifications.
        
        Args:
            data_yaml_path: Path to data.yaml file to backup
            
        Raises:
            FileNotFoundError: If data_yaml_path doesn't exist
            IOError: If backup creation fails
        """
        if not os.path.exists(data_yaml_path):
            raise FileNotFoundError(f"data.yaml not found: {data_yaml_path}")
        
        # Create timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{data_yaml_path}.backup_{timestamp}"
        
        try:
            shutil.copy2(data_yaml_path, backup_path)
            print(f"Created backup: {backup_path}")
        except Exception as e:
            raise IOError(f"Failed to create backup of {data_yaml_path}: {e}")
    
    def update_data_yaml(
        self,
        output_dir: str,
        class_names: List[str],
        original_yaml_path: str = None
    ) -> None:
        """
        Update data.yaml with new paths and split statistics.
        
        Creates or updates data.yaml with:
        - Paths to train/valid/test directories
        - Class names
        - Number of classes
        - Preserves additional configuration fields from original
        
        Args:
            output_dir: Root directory of merged dataset
            class_names: List of class names for the dataset
            original_yaml_path: Optional path to original data.yaml to preserve settings
            
        Raises:
            IOError: If YAML operations fail
        """
        # Build new configuration
        config = {
            'path': os.path.abspath(output_dir),
            'train': 'train/images',
            'val': 'valid/images',
            'test': 'test/images',
            'nc': len(class_names),
            'names': class_names
        }
        
        # Preserve additional fields from original if provided
        if original_yaml_path and os.path.exists(original_yaml_path):
            try:
                with open(original_yaml_path, 'r') as f:
                    original_config = yaml.safe_load(f)
                
                # Preserve fields that aren't being updated
                preserve_fields = ['roboflow', 'download', 'yaml_file']
                for field in preserve_fields:
                    if field in original_config:
                        config[field] = original_config[field]
            except Exception as e:
                print(f"Warning: Could not read original yaml {original_yaml_path}: {e}")
        
        # Write updated configuration
        output_yaml_path = os.path.join(output_dir, 'data.yaml')
        
        try:
            with open(output_yaml_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            print(f"Updated data.yaml at {output_yaml_path}")
            print(f"  Classes: {class_names}")
            print(f"  Train: {config['train']}")
            print(f"  Valid: {config['val']}")
            print(f"  Test: {config['test']}")
        except Exception as e:
            raise IOError(f"Failed to write data.yaml to {output_yaml_path}: {e}")
