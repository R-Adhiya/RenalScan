"""
Manual test script for QualityChecker component.

This script tests the QualityChecker with actual images from the current dataset.
"""

import os
import sys
from src.dataset_expansion.quality_checker import QualityChecker

def main():
    print("=" * 60)
    print("Manual QualityChecker Test")
    print("=" * 60)
    print()
    
    # Configuration
    image_dir = "data/train/images"
    label_dir = "data/train/labels"
    class_names = ["Kidney Stone"]
    output_dir = "verification/quality_samples"
    n_samples = 5  # Test with 5 samples
    
    # Check directories exist
    if not os.path.exists(image_dir):
        print(f"ERROR: Image directory not found: {image_dir}")
        return 1
    
    if not os.path.exists(label_dir):
        print(f"ERROR: Label directory not found: {label_dir}")
        return 1
    
    print(f"Image directory: {image_dir}")
    print(f"Label directory: {label_dir}")
    print(f"Class names: {class_names}")
    print(f"Output directory: {output_dir}")
    print(f"Sample size: {n_samples}")
    print()
    
    try:
        # Initialize QualityChecker
        print("Initializing QualityChecker...")
        qc = QualityChecker(image_dir, label_dir, class_names)
        print("✓ QualityChecker initialized successfully")
        print()
        
        # Sample random images
        print(f"Sampling {n_samples} random images...")
        sampled_images = qc.random_sample(n_samples)
        print(f"✓ Sampled {len(sampled_images)} images:")
        for i, img in enumerate(sampled_images, 1):
            print(f"  {i}. {img}")
        print()
        
        # Test label parsing on first sample
        if sampled_images:
            test_image = sampled_images[0]
            label_filename = os.path.splitext(test_image)[0] + '.txt'
            label_path = os.path.join(label_dir, label_filename)
            
            print(f"Testing label parsing for: {test_image}")
            print(f"Label file: {label_filename}")
            
            bboxes = qc.parse_yolo_label(label_path)
            print(f"✓ Parsed {len(bboxes)} bounding boxes")
            
            if bboxes:
                print("  First bbox details:")
                bbox = bboxes[0]
                print(f"    Class ID: {bbox.class_id}")
                print(f"    Center: ({bbox.center_x:.4f}, {bbox.center_y:.4f})")
                print(f"    Size: {bbox.width:.4f} x {bbox.height:.4f}")
            print()
        
        # Create visualizations
        print(f"Creating visualizations in {output_dir}...")
        qc.visualize_annotations(sampled_images, output_dir)
        print(f"✓ Visualizations saved successfully")
        print()
        
        # Verify output files
        print("Verifying output files...")
        output_files = [f for f in os.listdir(output_dir) if f.startswith('annotated_')]
        print(f"✓ Created {len(output_files)} visualization files:")
        for i, f in enumerate(output_files, 1):
            file_path = os.path.join(output_dir, f)
            file_size = os.path.getsize(file_path)
            print(f"  {i}. {f} ({file_size:,} bytes)")
        print()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print(f"Check the visualization images in: {output_dir}")
        print()
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
