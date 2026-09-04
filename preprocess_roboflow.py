"""
Preprocess Roboflow dataset to be compatible with our single-class format.
- Remove 'Normal' class (class 0)
- Remap 'Stone' class (class 1) to class 0
- Update data.yaml to single class
"""

import os
import shutil
from pathlib import Path

def preprocess_labels(source_dir, output_dir):
    """Process labels to remove Normal class and remap Stone to class 0."""
    
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    stats = {
        'total_files': 0,
        'files_with_stones': 0,
        'files_normal_only': 0,
        'total_stone_boxes': 0,
        'total_normal_boxes': 0,
        'files_copied_images': 0,
        'files_copied_labels': 0
    }
    
    # Process each split
    for split in ['train', 'valid', 'test']:
        source_images = source_path / split / 'images'
        source_labels = source_path / split / 'labels'
        
        output_images = output_path / split / 'images'
        output_labels = output_path / split / 'labels'
        
        output_images.mkdir(parents=True, exist_ok=True)
        output_labels.mkdir(parents=True, exist_ok=True)
        
        if not source_labels.exists():
            print(f"⚠️  No labels directory found for {split}")
            continue
        
        print(f"\nProcessing {split} split...")
        
        # Process each label file
        for label_file in source_labels.glob('*.txt'):
            stats['total_files'] += 1
            
            # Read original labels
            with open(label_file, 'r') as f:
                lines = f.readlines()
            
            # Filter and remap labels
            new_lines = []
            has_stones = False
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                
                class_id = int(parts[0])
                
                if class_id == 0:  # Normal class - skip
                    stats['total_normal_boxes'] += 1
                elif class_id == 1:  # Stone class - remap to 0
                    stats['total_stone_boxes'] += 1
                    has_stones = True
                    # Remap class 1 -> 0
                    new_line = '0 ' + ' '.join(parts[1:]) + '\n'
                    new_lines.append(new_line)
            
            # Only copy files that have stone annotations
            if has_stones:
                stats['files_with_stones'] += 1
                
                # Write new label file
                output_label = output_labels / label_file.name
                with open(output_label, 'w') as f:
                    f.writelines(new_lines)
                stats['files_copied_labels'] += 1
                
                # Copy corresponding image
                image_name = label_file.stem + '.jpg'
                source_image = source_images / image_name
                
                if source_image.exists():
                    output_image = output_images / image_name
                    shutil.copy2(source_image, output_image)
                    stats['files_copied_images'] += 1
                else:
                    print(f"⚠️  Image not found: {image_name}")
            else:
                stats['files_normal_only'] += 1
    
    return stats

def update_data_yaml(output_dir):
    """Create new data.yaml with single class."""
    
    output_path = Path(output_dir)
    yaml_content = f"""path: {output_path.resolve().as_posix()}
train: train/images
val: valid/images
test: test/images

nc: 1
names: ['Stone']
"""
    
    yaml_file = output_path / 'data.yaml'
    with open(yaml_file, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Created data.yaml at {yaml_file}")

def main():
    print("=" * 70)
    print("PREPROCESSING ROBOFLOW DATASET")
    print("=" * 70)
    print()
    print("Task: Convert 2-class dataset (Normal, Stone) to 1-class (Stone only)")
    print()
    
    source_dir = 'roboflow_dataset'
    output_dir = 'roboflow_dataset_preprocessed'
    
    # Remove output dir if exists
    if Path(output_dir).exists():
        print(f"Removing existing {output_dir}...")
        shutil.rmtree(output_dir)
    
    print(f"Source: {source_dir}")
    print(f"Output: {output_dir}")
    print()
    
    # Process labels
    print("Processing labels and filtering images...")
    stats = preprocess_labels(source_dir, output_dir)
    
    # Update data.yaml
    update_data_yaml(output_dir)
    
    # Print statistics
    print()
    print("=" * 70)
    print("PREPROCESSING STATISTICS")
    print("=" * 70)
    print(f"Total label files processed: {stats['total_files']}")
    print(f"Files with stone annotations: {stats['files_with_stones']}")
    print(f"Files with only 'Normal' (excluded): {stats['files_normal_only']}")
    print(f"Total stone bounding boxes: {stats['total_stone_boxes']}")
    print(f"Total normal boxes (excluded): {stats['total_normal_boxes']}")
    print()
    print(f"Files copied - Images: {stats['files_copied_images']}")
    print(f"Files copied - Labels: {stats['files_copied_labels']}")
    print()
    
    # Count final images per split
    output_path = Path(output_dir)
    for split in ['train', 'valid', 'test']:
        split_images = output_path / split / 'images'
        if split_images.exists():
            count = len(list(split_images.glob('*.jpg')))
            print(f"{split.capitalize()} images: {count}")
    
    print()
    print("=" * 70)
    print("✅ PREPROCESSING COMPLETE")
    print("=" * 70)
    print()
    print(f"Preprocessed dataset ready at: {output_dir}")
    print()

if __name__ == '__main__':
    main()
