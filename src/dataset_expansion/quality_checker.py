"""
Quality checker for visual validation of dataset annotations.

This module provides the QualityChecker class for randomly sampling images
from a dataset and creating visual overlays with bounding box annotations
to verify label quality.
"""

import os
import random
from typing import List, Tuple
from dataclasses import dataclass
import cv2
import numpy as np


@dataclass
class BBox:
    """
    Bounding box in YOLO format.
    
    Attributes:
        class_id: Class identifier (integer)
        center_x: Normalized center x coordinate [0, 1]
        center_y: Normalized center y coordinate [0, 1]
        width: Normalized width [0, 1]
        height: Normalized height [0, 1]
    """
    class_id: int
    center_x: float
    center_y: float
    width: float
    height: float
    
    def to_pixel_coords(self, img_width: int, img_height: int) -> Tuple[int, int, int, int]:
        """
        Convert normalized YOLO coordinates to pixel coordinates.
        
        Args:
            img_width: Image width in pixels
            img_height: Image height in pixels
            
        Returns:
            Tuple of (x1, y1, x2, y2) in pixel coordinates
            where (x1, y1) is top-left and (x2, y2) is bottom-right
        """
        # Convert from normalized to pixel coordinates
        center_x_px = self.center_x * img_width
        center_y_px = self.center_y * img_height
        width_px = self.width * img_width
        height_px = self.height * img_height
        
        # Convert from center format to corner format
        x1 = int(center_x_px - width_px / 2)
        y1 = int(center_y_px - height_px / 2)
        x2 = int(center_x_px + width_px / 2)
        y2 = int(center_y_px + height_px / 2)
        
        # Clamp to image boundaries
        x1 = max(0, min(x1, img_width - 1))
        y1 = max(0, min(y1, img_height - 1))
        x2 = max(0, min(x2, img_width - 1))
        y2 = max(0, min(y2, img_height - 1))
        
        return (x1, y1, x2, y2)


class QualityChecker:
    """
    Visual validation of annotation quality through random sampling.
    
    Samples random images from a dataset and creates visualization overlays
    with bounding boxes to enable manual quality verification.
    """
    
    def __init__(self, image_dir: str, label_dir: str, class_names: List[str]):
        """
        Initialize QualityChecker with dataset directories.
        
        Args:
            image_dir: Directory containing images
            label_dir: Directory containing YOLO format label files
            class_names: List of class names in order (index = class_id)
            
        Raises:
            FileNotFoundError: If image_dir or label_dir doesn't exist
            ValueError: If class_names is empty
        """
        if not os.path.exists(image_dir):
            raise FileNotFoundError(f"Image directory not found: {image_dir}")
        if not os.path.exists(label_dir):
            raise FileNotFoundError(f"Label directory not found: {label_dir}")
        if not class_names:
            raise ValueError("class_names cannot be empty")
        
        self.image_dir = image_dir
        self.label_dir = label_dir
        self.class_names = class_names
        
    def random_sample(self, n_samples: int = 20) -> List[str]:
        """
        Randomly sample n images from the dataset.
        
        Follows the constraint: sample size = min(N, n_samples) where N is
        the total number of images in the dataset.
        
        Args:
            n_samples: Target number of samples (default: 20)
            
        Returns:
            List of image filenames (not full paths) that were sampled
            
        Raises:
            ValueError: If n_samples is less than 1
        """
        if n_samples < 1:
            raise ValueError("n_samples must be at least 1")
        
        # Get all image files
        all_files = []
        for filename in os.listdir(self.image_dir):
            # Check for common image extensions
            if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp']):
                all_files.append(filename)
        
        # Apply min(N, n_samples) constraint
        actual_sample_size = min(len(all_files), n_samples)
        
        # Return empty list if no images found
        if actual_sample_size == 0:
            return []
        
        # Randomly sample without replacement
        sampled_files = random.sample(all_files, actual_sample_size)
        
        return sampled_files
    
    def parse_yolo_label(self, label_path: str) -> List[BBox]:
        """
        Parse YOLO format label file into BBox objects.
        
        YOLO format: Each line contains:
        <class_id> <center_x> <center_y> <width> <height>
        All coordinates are normalized [0, 1]
        
        Args:
            label_path: Path to the YOLO format label file (.txt)
            
        Returns:
            List of BBox objects parsed from the file
            Empty list if file doesn't exist or is empty
            
        Raises:
            ValueError: If label file is malformed
        """
        if not os.path.exists(label_path):
            # Return empty list for missing labels (image without annotations)
            return []
        
        bboxes = []
        
        try:
            with open(label_path, 'r') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Parse line
                parts = line.split()
                if len(parts) != 5:
                    raise ValueError(
                        f"Invalid YOLO format at line {line_num} in {label_path}: "
                        f"expected 5 values, got {len(parts)}"
                    )
                
                try:
                    class_id = int(parts[0])
                    center_x = float(parts[1])
                    center_y = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                except ValueError as e:
                    raise ValueError(
                        f"Invalid value at line {line_num} in {label_path}: {e}"
                    )
                
                # Validate ranges (allow slight tolerance for floating point)
                if not (0 <= center_x <= 1):
                    raise ValueError(
                        f"center_x out of range at line {line_num} in {label_path}: {center_x}"
                    )
                if not (0 <= center_y <= 1):
                    raise ValueError(
                        f"center_y out of range at line {line_num} in {label_path}: {center_y}"
                    )
                if not (0 <= width <= 1):
                    raise ValueError(
                        f"width out of range at line {line_num} in {label_path}: {width}"
                    )
                if not (0 <= height <= 1):
                    raise ValueError(
                        f"height out of range at line {line_num} in {label_path}: {height}"
                    )
                
                bbox = BBox(
                    class_id=class_id,
                    center_x=center_x,
                    center_y=center_y,
                    width=width,
                    height=height
                )
                bboxes.append(bbox)
        
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            else:
                raise ValueError(f"Error reading label file {label_path}: {e}")
        
        return bboxes
    
    def draw_bbox(self, image: np.ndarray, bbox: BBox, 
                  class_name: str, color: Tuple[int, int, int]) -> np.ndarray:
        """
        Draw bounding box with label on image.
        
        Args:
            image: Input image as numpy array (BGR format)
            bbox: BBox object with normalized coordinates
            class_name: Name of the class to display as label
            color: BGR color tuple for the box and text
            
        Returns:
            Image with bounding box drawn (same array, modified in place)
        """
        img_height, img_width = image.shape[:2]
        
        # Convert to pixel coordinates
        x1, y1, x2, y2 = bbox.to_pixel_coords(img_width, img_height)
        
        # Draw rectangle
        thickness = max(1, int(min(img_width, img_height) / 200))  # Scale thickness with image size
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
        
        # Prepare label text
        label = f"{class_name}"
        
        # Calculate text size for background
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.4, min(img_width, img_height) / 1000)  # Scale font with image size
        font_thickness = max(1, int(font_scale * 2))
        (text_width, text_height), baseline = cv2.getTextSize(
            label, font, font_scale, font_thickness
        )
        
        # Draw text background rectangle
        bg_y1 = max(0, y1 - text_height - baseline - 4)
        bg_y2 = y1
        bg_x2 = min(img_width, x1 + text_width + 4)
        cv2.rectangle(image, (x1, bg_y1), (bg_x2, bg_y2), color, -1)
        
        # Draw text
        text_y = max(text_height, y1 - baseline - 2)
        cv2.putText(
            image, label, (x1 + 2, text_y), 
            font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA
        )
        
        return image
    
    def visualize_annotations(self, image_paths: List[str], output_dir: str) -> None:
        """
        Create bbox overlay visualizations for sampled images.
        
        For each image in image_paths:
        1. Load the image
        2. Parse corresponding label file
        3. Draw bounding boxes with class labels
        4. Save visualization to output_dir
        
        Args:
            image_paths: List of image filenames (not full paths) to visualize
            output_dir: Directory to save visualization images
            
        Raises:
            FileNotFoundError: If output_dir parent doesn't exist
            ValueError: If image cannot be read or label parsing fails
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Color palette for bounding boxes (BGR format)
        colors = [
            (0, 255, 0),      # Green
            (255, 0, 0),      # Blue
            (0, 0, 255),      # Red
            (255, 255, 0),    # Cyan
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Yellow
            (128, 0, 128),    # Purple
            (255, 165, 0),    # Orange
        ]
        
        for image_filename in image_paths:
            # Construct full paths
            image_path = os.path.join(self.image_dir, image_filename)
            
            # Get label filename (replace image extension with .txt)
            label_filename = os.path.splitext(image_filename)[0] + '.txt'
            label_path = os.path.join(self.label_dir, label_filename)
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to read image: {image_path}")
            
            # Parse labels
            bboxes = self.parse_yolo_label(label_path)
            
            # Draw each bounding box
            for bbox in bboxes:
                # Get class name
                if bbox.class_id < len(self.class_names):
                    class_name = self.class_names[bbox.class_id]
                else:
                    class_name = f"Class_{bbox.class_id}"
                
                # Get color (cycle through palette)
                color = colors[bbox.class_id % len(colors)]
                
                # Draw bbox
                self.draw_bbox(image, bbox, class_name, color)
            
            # Save visualization
            output_filename = f"annotated_{image_filename}"
            output_path = os.path.join(output_dir, output_filename)
            
            success = cv2.imwrite(output_path, image)
            if not success:
                raise ValueError(f"Failed to save visualization: {output_path}")
