"""
Analyze the actual duplicate removal to understand the math.
"""

import re
from pathlib import Path
from collections import defaultdict

def parse_duplicate_report():
    """Parse the duplicate report and count unique dataset2 images."""
    
    report_path = Path("verification/logs/duplicate_report.txt")
    
    with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Extract all duplicate pairs
    # Pattern: Dataset 2: <path>
    dataset2_pattern = r'Dataset 2: (.+?)(?:\n|$)'
    dataset2_images = re.findall(dataset2_pattern, content)
    
    # Count unique dataset2 images (these are the ones actually removed)
    unique_dataset2 = set(dataset2_images)
    
    print("=" * 70)
    print("DUPLICATE ANALYSIS")
    print("=" * 70)
    print()
    print(f"Total duplicate PAIRS found: {len(dataset2_images)}")
    print(f"Unique dataset2 images marked for removal: {len(unique_dataset2)}")
    print()
    
    # Also count dataset1 images involved
    dataset1_pattern = r'Dataset 1: (.+?)(?:\n|$)'
    dataset1_images = re.findall(dataset1_pattern, content)
    unique_dataset1 = set(dataset1_images)
    print(f"Unique dataset1 images involved in duplicates: {len(unique_dataset1)}")
    print()
    
    # Show some examples of multi-matching
    dataset1_counts = defaultdict(int)
    dataset2_counts = defaultdict(int)
    
    # Parse pairs
    pairs = []
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        if lines[i].startswith('Dataset 1:'):
            ds1 = lines[i].replace('Dataset 1: ', '').strip()
            if i + 1 < len(lines) and lines[i + 1].startswith('Dataset 2:'):
                ds2 = lines[i + 1].replace('Dataset 2: ', '').strip()
                dataset1_counts[ds1] += 1
                dataset2_counts[ds2] += 1
                pairs.append((ds1, ds2))
        i += 1
    
    # Find images with multiple matches
    multi_match_ds1 = [(img, count) for img, count in dataset1_counts.items() if count > 1]
    multi_match_ds2 = [(img, count) for img, count in dataset2_counts.items() if count > 1]
    
    print(f"Dataset1 images matching multiple dataset2 images: {len(multi_match_ds1)}")
    print(f"Dataset2 images matching multiple dataset1 images: {len(multi_match_ds2)}")
    print()
    
    if multi_match_ds1:
        print("Example: Dataset1 images with multiple matches:")
        for img, count in sorted(multi_match_ds1, key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {Path(img).name}: {count} matches")
    
    return {
        'total_pairs': len(dataset2_images),
        'unique_dataset2_removed': len(unique_dataset2),
        'unique_dataset1_involved': len(unique_dataset1),
        'multi_match_ds1': len(multi_match_ds1),
        'multi_match_ds2': len(multi_match_ds2)
    }

def reconcile_math():
    """Reconcile the math to explain final counts."""
    
    print()
    print("=" * 70)
    print("MATH RECONCILIATION")
    print("=" * 70)
    print()
    
    # Known values
    original_dataset = 1300
    roboflow_preprocessed = 3340
    
    # Analyze duplicates
    stats = parse_duplicate_report()
    
    unique_duplicates_removed = stats['unique_dataset2_removed']
    
    # Calculate expected
    expected_total = original_dataset + roboflow_preprocessed - unique_duplicates_removed
    
    # Actual from data_merged
    actual_train = 2313
    actual_valid = 495
    actual_test = 497
    actual_total = actual_train + actual_valid + actual_test
    
    print("Starting datasets:")
    print(f"  Original dataset (data/):                    {original_dataset:>5} images")
    print(f"  Roboflow (after preprocessing):               {roboflow_preprocessed:>5} images")
    print(f"  ─────────────────────────────────────────────────────")
    print(f"  Combined pool (before dedup):                 {original_dataset + roboflow_preprocessed:>5} images")
    print()
    print("Duplicate detection:")
    print(f"  Total duplicate PAIRS detected:               {stats['total_pairs']:>5} pairs")
    print(f"  Unique dataset2 images to remove:             {unique_duplicates_removed:>5} images")
    print(f"  (One dataset2 image can match multiple dataset1 images,")
    print(f"   creating many pairs but only removing one image)")
    print()
    print("Final calculation:")
    print(f"  Original dataset:                             {original_dataset:>5}")
    print(f"  + Roboflow preprocessed:                      {roboflow_preprocessed:>5}")
    print(f"  - Unique duplicates removed:                  {unique_duplicates_removed:>5}")
    print(f"  ─────────────────────────────────────────────────────")
    print(f"  Expected total:                               {expected_total:>5} images")
    print()
    print("Actual merged dataset:")
    print(f"  Train:                                        {actual_train:>5} images")
    print(f"  Valid:                                        {actual_valid:>5} images")
    print(f"  Test:                                         {actual_test:>5} images")
    print(f"  ─────────────────────────────────────────────────────")
    print(f"  Actual total:                                 {actual_total:>5} images")
    print()
    print(f"Difference: {actual_total - expected_total:+d} images")
    print()
    
    if actual_total == expected_total:
        print("✅ MATH RECONCILES PERFECTLY!")
    else:
        print(f"⚠️  Math discrepancy: {abs(actual_total - expected_total)} images")
        print("   Investigating...")
        
        # Check if it's a rounding issue or filtering issue
        print()
        print("Possible explanations:")
        print("1. Some images may have labels but no corresponding image file")
        print("2. Some images may have image files but no corresponding label")
        print("3. Filtering may have excluded corrupted images")
    
    print()
    print("=" * 70)

if __name__ == '__main__':
    reconcile_math()
