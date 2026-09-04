"""
Test script for DatasetMerger checkpoint verification.

Creates two small sample datasets (20 images each) and tests the merge operation.
Verifies output directory structure and file counts.
"""

import os
import shutil
import sys
from pathlib import Path
from PIL import Image
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dataset_expansion.merger import DatasetMerger, Sample, DatasetSplits


def create_sample_image(path: str, size=(512, 512)):
    """Create a simple test image."""
    # Create random colored image
    img_array = (random.random() * 255 * np.ones((size[1], size[0], 3))).astype('uint8')
    img = Image.fromarray(img_array, 'RGB')
    img.save(path)


def create_sample_label(path: str, num_boxes=1):
    """Create a simple YOLO format label file."""
    with open(path, 'w') as f:
        for _ in range(num_boxes):
            # Format: class_id center_x center_y width height (normalized)
            class_id = 0
            cx = random.uniform(0.3, 0.7)
            cy = random.uniform(0.3, 0.7)
            w = random.uniform(0.1, 0.3)
            h = random.uniform(0.1, 0.3)
            f.write(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")


def create_test_dataset(base_dir: str, name: str, num_images: int = 20):
    """
    Create a test dataset with train/valid/test splits.
    
    Args:
        base_dir: Base directory for test datasets
        name: Name of the dataset (e.g., "current" or "source")
        num_images: Total number of images to create
    """
    dataset_dir = os.path.join(base_dir, name)
    
    # Create directory structure
    for split in ['train', 'valid', 'test']:
        os.makedirs(os.path.join(dataset_dir, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(dataset_dir, split, 'labels'), exist_ok=True)
    
    # Distribute images: 70% train, 15% valid, 15% test
    train_count = int(num_images * 0.7)
    valid_count = int(num_images * 0.15)
    test_count = num_images - train_count - valid_count
    
    splits_config = [
        ('train', train_count),
        ('valid', valid_count),
        ('test', test_count)
    ]
    
    img_id = 0
    for split_name, count in splits_config:
        images_dir = os.path.join(dataset_dir, split_name, 'images')
        labels_dir = os.path.join(dataset_dir, split_name, 'labels')
        
        for i in range(count):
            img_filename = f"{name}_{split_name}_{img_id:04d}.jpg"
            label_filename = f"{name}_{split_name}_{img_id:04d}.txt"
            
            img_path = os.path.join(images_dir, img_filename)
            label_path = os.path.join(labels_dir, label_filename)
            
            # Create dummy image and label
            create_sample_image(img_path)
            create_sample_label(label_path, num_boxes=random.randint(1, 3))
            
            img_id += 1
    
    # Create data.yaml
    data_yaml = {
        'path': os.path.abspath(dataset_dir),
        'train': 'train/images',
        'val': 'valid/images',
        'test': 'test/images',
        'nc': 1,
        'names': ['stone']
    }
    
    import yaml
    with open(os.path.join(dataset_dir, 'data.yaml'), 'w') as f:
        yaml.dump(data_yaml, f, default_flow_style=False)
    
    print(f"Created {name} dataset:")
    print(f"  Train: {train_count} images")
    print(f"  Valid: {valid_count} images")
    print(f"  Test: {test_count} images")
    print(f"  Total: {num_images} images")
    
    return dataset_dir


def verify_directory_structure(output_dir: str):
    """Verify the output directory has proper YOLO structure."""
    required_dirs = [
        'train/images',
        'train/labels',
        'valid/images',
        'valid/labels',
        'test/images',
        'test/labels'
    ]
    
    print("\n=== Verifying Directory Structure ===")
    all_exist = True
    for dir_path in required_dirs:
        full_path = os.path.join(output_dir, dir_path)
        exists = os.path.exists(full_path)
        status = "✓" if exists else "✗"
        print(f"  {status} {dir_path}")
        if not exists:
            all_exist = False
    
    return all_exist


def count_files(directory: str, extension: str = None):
    """Count files in a directory."""
    if not os.path.exists(directory):
        return 0
    
    files = os.listdir(directory)
    if extension:
        files = [f for f in files if f.endswith(extension)]
    return len(files)


def verify_file_counts(output_dir: str, expected_total: int):
    """Verify file counts in each split."""
    print("\n=== Verifying File Counts ===")
    
    splits = ['train', 'valid', 'test']
    total_images = 0
    total_labels = 0
    
    for split in splits:
        images_dir = os.path.join(output_dir, split, 'images')
        labels_dir = os.path.join(output_dir, split, 'labels')
        
        img_count = count_files(images_dir, '.jpg')
        label_count = count_files(labels_dir, '.txt')
        
        total_images += img_count
        total_labels += label_count
        
        # Check that images and labels match
        match_status = "✓" if img_count == label_count else "✗"
        print(f"  {split}:")
        print(f"    Images: {img_count}")
        print(f"    Labels: {label_count}")
        print(f"    Match: {match_status}")
    
    print(f"\n  Total Images: {total_images}")
    print(f"  Total Labels: {total_labels}")
    print(f"  Expected: {expected_total}")
    
    # Verify totals
    success = (total_images == expected_total and 
               total_labels == expected_total and
               total_images == total_labels)
    
    return success


def verify_data_yaml(output_dir: str):
    """Verify data.yaml was created and is valid."""
    print("\n=== Verifying data.yaml ===")
    
    yaml_path = os.path.join(output_dir, 'data.yaml')
    
    if not os.path.exists(yaml_path):
        print("  ✗ data.yaml not found")
        return False
    
    print("  ✓ data.yaml exists")
    
    import yaml
    try:
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        required_fields = ['path', 'train', 'val', 'test', 'nc', 'names']
        all_present = True
        
        for field in required_fields:
            present = field in config
            status = "✓" if present else "✗"
            print(f"  {status} {field}: {config.get(field, 'MISSING')}")
            if not present:
                all_present = False
        
        return all_present
    
    except Exception as e:
        print(f"  ✗ Error reading data.yaml: {e}")
        return False


def main():
    """Run merger checkpoint tests."""
    print("=" * 60)
    print("DatasetMerger Checkpoint Test")
    print("=" * 60)
    
    # Setup test directories
    test_base = "verification/test_merge"
    if os.path.exists(test_base):
        shutil.rmtree(test_base)
    os.makedirs(test_base, exist_ok=True)
    
    try:
        # Create two test datasets (20 images each)
        print("\n### Creating Test Datasets ###\n")
        current_dir = create_test_dataset(test_base, "current", num_images=20)
        source_dir = create_test_dataset(test_base, "source", num_images=20)
        
        # Create output directory
        output_dir = os.path.join(test_base, "merged")
        
        # Initialize merger
        print("\n### Initializing DatasetMerger ###\n")
        merger = DatasetMerger(
            current_data_dir=current_dir,
            source_data_dir=source_dir,
            output_data_dir=output_dir,
            duplicates_to_remove=[]
        )
        
        # Test: Collect all samples
        print("### Collecting Samples ###\n")
        samples = merger.collect_all_samples()
        expected_samples = 40  # 20 + 20
        print(f"\nCollected: {len(samples)} samples")
        print(f"Expected: {expected_samples} samples")
        assert len(samples) == expected_samples, f"Expected {expected_samples} samples, got {len(samples)}"
        print("✓ Sample collection passed")
        
        # Test: Create splits
        print("\n### Creating Splits ###\n")
        splits = merger.stratified_split(samples, ratios=(0.70, 0.15, 0.15))
        counts = splits.get_counts()
        print(f"\nSplit counts: {counts}")
        
        # Verify split totals
        assert counts['total'] == expected_samples, "Split total doesn't match sample count"
        print("✓ Split creation passed")
        
        # Test: Copy files to splits
        print("\n### Copying Files ###\n")
        merger.copy_files_to_splits(splits, output_dir)
        print("✓ File copying completed")
        
        # Test: Update data.yaml
        print("\n### Updating data.yaml ###\n")
        merger.update_data_yaml(
            output_dir=output_dir,
            class_names=['stone'],
            original_yaml_path=os.path.join(current_dir, 'data.yaml')
        )
        print("✓ data.yaml update completed")
        
        # Verification phase
        print("\n" + "=" * 60)
        print("VERIFICATION PHASE")
        print("=" * 60)
        
        # Verify directory structure
        structure_ok = verify_directory_structure(output_dir)
        
        # Verify file counts
        counts_ok = verify_file_counts(output_dir, expected_samples)
        
        # Verify data.yaml
        yaml_ok = verify_data_yaml(output_dir)
        
        # Final results
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        
        results = {
            "Directory Structure": structure_ok,
            "File Counts": counts_ok,
            "data.yaml Configuration": yaml_ok
        }
        
        all_passed = all(results.values())
        
        for test_name, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {test_name}")
        
        print("\n" + "=" * 60)
        if all_passed:
            print("✓ ALL TESTS PASSED")
            print("=" * 60)
            print("\nThe DatasetMerger component is working correctly.")
            print(f"Test output saved to: {test_base}")
            return 0
        else:
            print("✗ SOME TESTS FAILED")
            print("=" * 60)
            return 1
    
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import numpy as np
    sys.exit(main())
