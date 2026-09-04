"""
Validators for dataset expansion pipeline.

This module provides validators for class definitions and format consistency
between the current dataset and source datasets.
"""

import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import yaml
from PIL import Image


@dataclass
class ValidationResult:
    """Result of class validation between datasets."""
    is_compatible: bool
    current_classes: List[str]
    source_classes: List[str]
    needs_remapping: bool
    mapping: Optional[Dict[int, int]]
    message: str


class ClassValidator:
    """
    Validates class definitions between current and source datasets.
    
    Ensures that class names are compatible and creates mappings when needed.
    Specifically designed to handle single "stone" class validation for kidney stone detection.
    """
    
    # Acceptable stone class name variations
    STONE_CLASS_VARIATIONS = {
        'stone',
        'kidney stone',
        'kidney_stone',
        'kidneystone',
        'renal stone',
        'renal_stone',
        'renalstone'
    }
    
    def __init__(self, current_data_yaml: str, source_data_yaml: str):
        """
        Initialize ClassValidator with paths to data.yaml files.
        
        Args:
            current_data_yaml: Path to current dataset's data.yaml
            source_data_yaml: Path to source dataset's data.yaml
        """
        self.current_data_yaml = current_data_yaml
        self.source_data_yaml = source_data_yaml
        
    def parse_classes(self, yaml_path: str) -> List[str]:
        """
        Extract class names from data.yaml file.
        
        Args:
            yaml_path: Path to the data.yaml file
            
        Returns:
            List of class names in order
            
        Raises:
            FileNotFoundError: If yaml_path doesn't exist
            ValueError: If YAML is malformed or missing required fields
        """
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
        
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file {yaml_path}: {e}")
        
        if data is None:
            raise ValueError(f"YAML file {yaml_path} is empty")
        
        # Check for 'names' field (YOLO format)
        if 'names' not in data:
            raise ValueError(f"YAML file {yaml_path} missing required 'names' field")
        
        names = data['names']
        
        # Handle both list and dict formats for names
        if isinstance(names, list):
            return [str(name) for name in names]
        elif isinstance(names, dict):
            # Sort by key to maintain order
            sorted_items = sorted(names.items(), key=lambda x: int(x[0]))
            return [str(value) for _, value in sorted_items]
        else:
            raise ValueError(f"'names' field in {yaml_path} must be a list or dict")
    
    def _is_stone_class(self, class_name: str) -> bool:
        """
        Check if a class name represents a stone class.
        
        Args:
            class_name: The class name to check
            
        Returns:
            True if the class name is a valid stone class variation
        """
        normalized = class_name.lower().strip()
        return normalized in self.STONE_CLASS_VARIATIONS
    
    def validate_compatibility(self) -> ValidationResult:
        """
        Check if classes match or need remapping between datasets.
        
        Returns:
            ValidationResult with compatibility status and mapping if needed
        """
        try:
            current_classes = self.parse_classes(self.current_data_yaml)
            source_classes = self.parse_classes(self.source_data_yaml)
        except (FileNotFoundError, ValueError) as e:
            return ValidationResult(
                is_compatible=False,
                current_classes=[],
                source_classes=[],
                needs_remapping=False,
                mapping=None,
                message=f"Error parsing class definitions: {e}"
            )
        
        # Check for single class in both datasets
        if len(current_classes) != 1:
            return ValidationResult(
                is_compatible=False,
                current_classes=current_classes,
                source_classes=source_classes,
                needs_remapping=False,
                mapping=None,
                message=f"Current dataset must have exactly one class, found {len(current_classes)}"
            )
        
        if len(source_classes) != 1:
            return ValidationResult(
                is_compatible=False,
                current_classes=current_classes,
                source_classes=source_classes,
                needs_remapping=False,
                mapping=None,
                message=f"Source dataset must have exactly one class, found {len(source_classes)}"
            )
        
        # Verify both are stone classes
        if not self._is_stone_class(current_classes[0]):
            return ValidationResult(
                is_compatible=False,
                current_classes=current_classes,
                source_classes=source_classes,
                needs_remapping=False,
                mapping=None,
                message=f"Current dataset class '{current_classes[0]}' is not a recognized stone class"
            )
        
        if not self._is_stone_class(source_classes[0]):
            return ValidationResult(
                is_compatible=False,
                current_classes=current_classes,
                source_classes=source_classes,
                needs_remapping=False,
                mapping=None,
                message=f"Source dataset class '{source_classes[0]}' is not a recognized stone class"
            )
        
        # Check if classes are identical
        if current_classes[0] == source_classes[0]:
            return ValidationResult(
                is_compatible=True,
                current_classes=current_classes,
                source_classes=source_classes,
                needs_remapping=False,
                mapping=None,
                message="Classes match perfectly - no remapping needed"
            )
        
        # Classes are compatible but different - needs remapping
        return ValidationResult(
            is_compatible=True,
            current_classes=current_classes,
            source_classes=source_classes,
            needs_remapping=True,
            mapping={0: 0},  # Both are single class, map source class 0 to target class 0
            message=f"Classes are compatible but different ('{source_classes[0]}' -> '{current_classes[0]}'). Remapping recommended."
        )
    
    def create_class_mapping(self) -> Dict[int, int]:
        """
        Create class_id mapping from source to current dataset.
        
        Returns:
            Dictionary mapping source class_id to target class_id
            
        Raises:
            ValueError: If classes are incompatible
        """
        result = self.validate_compatibility()
        
        if not result.is_compatible:
            raise ValueError(f"Cannot create mapping - classes are incompatible: {result.message}")
        
        if not result.needs_remapping:
            # No remapping needed - return identity mapping
            return {i: i for i in range(len(result.current_classes))}
        
        # Return the mapping from validation result
        return result.mapping
    
    def remap_labels(self, label_dir: str, mapping: Dict[int, int]) -> int:
        """
        Apply class remapping to label files in a directory.
        
        Args:
            label_dir: Directory containing YOLO format label files (.txt)
            mapping: Dictionary mapping source class_id to target class_id
            
        Returns:
            Number of label files processed
            
        Raises:
            FileNotFoundError: If label_dir doesn't exist
            ValueError: If label files are malformed
        """
        if not os.path.exists(label_dir):
            raise FileNotFoundError(f"Label directory not found: {label_dir}")
        
        if not os.path.isdir(label_dir):
            raise ValueError(f"Path is not a directory: {label_dir}")
        
        processed_count = 0
        
        # Process all .txt files in the directory
        for filename in os.listdir(label_dir):
            if not filename.endswith('.txt'):
                continue
            
            label_path = os.path.join(label_dir, filename)
            
            try:
                # Read all lines
                with open(label_path, 'r') as f:
                    lines = f.readlines()
                
                # Remap class IDs
                remapped_lines = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) != 5:
                        raise ValueError(f"Invalid YOLO label format in {label_path}: expected 5 values, got {len(parts)}")
                    
                    # Parse class_id and remap
                    try:
                        class_id = int(parts[0])
                    except ValueError:
                        raise ValueError(f"Invalid class_id in {label_path}: '{parts[0]}' is not an integer")
                    
                    if class_id not in mapping:
                        raise ValueError(f"Class ID {class_id} not found in mapping for {label_path}")
                    
                    # Create remapped line
                    remapped_class_id = mapping[class_id]
                    remapped_line = f"{remapped_class_id} {parts[1]} {parts[2]} {parts[3]} {parts[4]}"
                    remapped_lines.append(remapped_line)
                
                # Write back to file
                with open(label_path, 'w') as f:
                    f.write('\n'.join(remapped_lines))
                    if remapped_lines:  # Add trailing newline if file not empty
                        f.write('\n')
                
                processed_count += 1
                
            except Exception as e:
                raise ValueError(f"Error processing label file {label_path}: {e}")
        
        return processed_count



@dataclass
class FormatReport:
    """Report of image format distribution in a dataset."""
    format_counts: Dict[str, int]  # e.g., {'JPG': 100, 'PNG': 20}
    total_images: int


@dataclass
class ResolutionReport:
    """Report of image resolution distribution in a dataset."""
    resolution_counts: Dict[Tuple[int, int], int]  # e.g., {(512, 512): 100, (1024, 1024): 20}
    total_images: int


@dataclass
class ConsistencyReport:
    """Report of format and resolution consistency against target specifications."""
    target_format: str
    target_resolution: Tuple[int, int]
    format_matches: int
    format_mismatches: int
    resolution_matches: int
    resolution_mismatches: int
    total_images: int
    mismatched_files: List[Dict[str, any]]  # List of files with their issues


class FormatValidator:
    """
    Validates image format and resolution consistency across datasets.
    
    Checks that images conform to target specifications (default: 512x512 JPG)
    and provides recommendations for preprocessing when inconsistencies are found.
    """
    
    def __init__(self, image_dirs: List[str]):
        """
        Initialize FormatValidator with directories to validate.
        
        Args:
            image_dirs: List of directories containing images to validate
        """
        self.image_dirs = image_dirs
        
    def analyze_formats(self) -> FormatReport:
        """
        Analyze image formats (JPG, PNG, etc.) and their distribution.
        
        Returns:
            FormatReport with format counts and total images
            
        Raises:
            FileNotFoundError: If any image directory doesn't exist
        """
        format_counter = Counter()
        total_images = 0
        
        for image_dir in self.image_dirs:
            if not os.path.exists(image_dir):
                raise FileNotFoundError(f"Image directory not found: {image_dir}")
            
            if not os.path.isdir(image_dir):
                continue
            
            # Scan directory for image files
            for filename in os.listdir(image_dir):
                # Check common image extensions
                if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']):
                    continue
                
                image_path = os.path.join(image_dir, filename)
                
                try:
                    with Image.open(image_path) as img:
                        # Get format (e.g., 'JPEG', 'PNG')
                        fmt = img.format
                        if fmt:
                            # Normalize format names
                            if fmt == 'JPEG':
                                fmt = 'JPG'
                            format_counter[fmt] += 1
                            total_images += 1
                except Exception as e:
                    # Skip corrupted or unreadable images
                    print(f"Warning: Could not read image {image_path}: {e}")
                    continue
        
        return FormatReport(
            format_counts=dict(format_counter),
            total_images=total_images
        )
    
    def analyze_resolutions(self) -> ResolutionReport:
        """
        Analyze image resolution distribution.
        
        Returns:
            ResolutionReport with resolution counts and total images
            
        Raises:
            FileNotFoundError: If any image directory doesn't exist
        """
        resolution_counter = Counter()
        total_images = 0
        
        for image_dir in self.image_dirs:
            if not os.path.exists(image_dir):
                raise FileNotFoundError(f"Image directory not found: {image_dir}")
            
            if not os.path.isdir(image_dir):
                continue
            
            # Scan directory for image files
            for filename in os.listdir(image_dir):
                # Check common image extensions
                if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']):
                    continue
                
                image_path = os.path.join(image_dir, filename)
                
                try:
                    with Image.open(image_path) as img:
                        # Get resolution (width, height)
                        resolution = img.size
                        resolution_counter[resolution] += 1
                        total_images += 1
                except Exception as e:
                    # Skip corrupted or unreadable images
                    print(f"Warning: Could not read image {image_path}: {e}")
                    continue
        
        return ResolutionReport(
            resolution_counts=dict(resolution_counter),
            total_images=total_images
        )
    
    def check_consistency(self, target_format: str = "JPG", 
                         target_resolution: Tuple[int, int] = (512, 512)) -> ConsistencyReport:
        """
        Check if images match target specifications.
        
        Args:
            target_format: Expected image format (default: "JPG")
            target_resolution: Expected image resolution as (width, height) (default: (512, 512))
            
        Returns:
            ConsistencyReport with match/mismatch counts and details
            
        Raises:
            FileNotFoundError: If any image directory doesn't exist
        """
        format_matches = 0
        format_mismatches = 0
        resolution_matches = 0
        resolution_mismatches = 0
        total_images = 0
        mismatched_files = []
        
        # Normalize target format
        target_format_normalized = target_format.upper()
        if target_format_normalized == 'JPEG':
            target_format_normalized = 'JPG'
        
        for image_dir in self.image_dirs:
            if not os.path.exists(image_dir):
                raise FileNotFoundError(f"Image directory not found: {image_dir}")
            
            if not os.path.isdir(image_dir):
                continue
            
            # Scan directory for image files
            for filename in os.listdir(image_dir):
                # Check common image extensions
                if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']):
                    continue
                
                image_path = os.path.join(image_dir, filename)
                
                try:
                    with Image.open(image_path) as img:
                        # Get format and resolution
                        fmt = img.format
                        if fmt == 'JPEG':
                            fmt = 'JPG'
                        resolution = img.size
                        
                        # Check format consistency
                        format_match = (fmt == target_format_normalized)
                        if format_match:
                            format_matches += 1
                        else:
                            format_mismatches += 1
                        
                        # Check resolution consistency
                        resolution_match = (resolution == target_resolution)
                        if resolution_match:
                            resolution_matches += 1
                        else:
                            resolution_mismatches += 1
                        
                        # Record mismatches
                        if not format_match or not resolution_match:
                            mismatched_files.append({
                                'file': image_path,
                                'actual_format': fmt,
                                'actual_resolution': resolution,
                                'format_mismatch': not format_match,
                                'resolution_mismatch': not resolution_match
                            })
                        
                        total_images += 1
                        
                except Exception as e:
                    # Skip corrupted or unreadable images
                    print(f"Warning: Could not read image {image_path}: {e}")
                    continue
        
        return ConsistencyReport(
            target_format=target_format_normalized,
            target_resolution=target_resolution,
            format_matches=format_matches,
            format_mismatches=format_mismatches,
            resolution_matches=resolution_matches,
            resolution_mismatches=resolution_mismatches,
            total_images=total_images,
            mismatched_files=mismatched_files
        )
    
    def recommend_preprocessing(self, report: ConsistencyReport) -> List[str]:
        """
        Recommend preprocessing steps for inconsistent images.
        
        Args:
            report: ConsistencyReport from check_consistency()
            
        Returns:
            List of recommended preprocessing actions
        """
        recommendations = []
        
        # Check if any issues exist
        if report.format_mismatches == 0 and report.resolution_mismatches == 0:
            recommendations.append("✓ All images match target specifications - no preprocessing needed")
            return recommendations
        
        # Format mismatch recommendations
        if report.format_mismatches > 0:
            percentage = (report.format_mismatches / report.total_images) * 100
            recommendations.append(
                f"⚠ Format Mismatch: {report.format_mismatches}/{report.total_images} images "
                f"({percentage:.1f}%) are not {report.target_format} format"
            )
            
            # Identify which formats need conversion
            format_types = set()
            for file_info in report.mismatched_files:
                if file_info['format_mismatch']:
                    format_types.add(file_info['actual_format'])
            
            if format_types:
                formats_str = ', '.join(sorted(format_types))
                recommendations.append(
                    f"  → Convert images from {formats_str} to {report.target_format} format"
                )
                recommendations.append(
                    f"  → Recommended tool: PIL/Pillow Image.save() with format='{report.target_format}'"
                )
        
        # Resolution mismatch recommendations
        if report.resolution_mismatches > 0:
            percentage = (report.resolution_mismatches / report.total_images) * 100
            recommendations.append(
                f"⚠ Resolution Mismatch: {report.resolution_mismatches}/{report.total_images} images "
                f"({percentage:.1f}%) are not {report.target_resolution[0]}x{report.target_resolution[1]}"
            )
            
            # Identify resolution ranges
            resolutions = set()
            for file_info in report.mismatched_files:
                if file_info['resolution_mismatch']:
                    resolutions.add(file_info['actual_resolution'])
            
            if resolutions:
                # Show a few example resolutions
                examples = sorted(list(resolutions))[:5]
                examples_str = ', '.join([f"{w}x{h}" for w, h in examples])
                if len(resolutions) > 5:
                    examples_str += f", ... ({len(resolutions)} unique resolutions)"
                
                recommendations.append(f"  → Found resolutions: {examples_str}")
                recommendations.append(
                    f"  → Resize all images to {report.target_resolution[0]}x{report.target_resolution[1]}"
                )
                recommendations.append(
                    f"  → Recommended tool: PIL/Pillow Image.resize() with LANCZOS resampling"
                )
                recommendations.append(
                    f"  → Note: Ensure bounding box coordinates are adjusted after resizing"
                )
        
        # Combination recommendation
        if report.format_mismatches > 0 and report.resolution_mismatches > 0:
            recommendations.append("")
            recommendations.append(
                "💡 Tip: Perform both resize and format conversion in a single preprocessing pass "
                "to avoid double image quality degradation"
            )
        
        return recommendations
