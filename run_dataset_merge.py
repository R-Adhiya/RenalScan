"""
Interactive Dataset Merge Script
This script guides you through merging the Roboflow dataset with your current dataset.
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 70)
    print("DATASET EXPANSION - INTERACTIVE MERGE")
    print("=" * 70)
    print()
    print("This script will merge the Roboflow kidney stone dataset with your")
    print("current dataset (1,300 images) to create a larger training set.")
    print()
    print("Source: https://universe.roboflow.com/ksd-kefw7/kidney-stone-detection-bltki")
    print("Expected source images: ~3,662")
    print("Expected total after merge: ~4,900+ (after duplicate removal)")
    print()
    print("=" * 70)
    print()
    
    # Step 1: Get API key
    print("Step 1: Roboflow API Key")
    print("-" * 70)
    print("Please obtain your API key from: https://app.roboflow.com/")
    print("Navigate to: Settings → API Keys")
    print()
    
    api_key = input("Enter your Roboflow API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print()
        print("⚠️  No API key provided.")
        print()
        print("Alternative options:")
        print("1. Download the dataset manually from Roboflow")
        print("2. Run the pipeline with --skip-download flag")
        print()
        print("Manual download command:")
        print("  Visit: https://universe.roboflow.com/ksd-kefw7/kidney-stone-detection-bltki")
        print("  Download in YOLO format")
        print("  Extract to a local directory")
        print()
        print("Then run:")
        print("  python -m src.dataset_expansion.pipeline \\")
        print("      --current-data-dir data \\")
        print("      --source-data-dir <path_to_downloaded_dataset> \\")
        print("      --output-dir data_merged \\")
        print("      --skip-download")
        print()
        sys.exit(0)
    
    # Step 2: Confirm settings
    print()
    print("Step 2: Merge Configuration")
    print("-" * 70)
    print(f"Current dataset: data/ (1,300 images)")
    print(f"Source URL: https://universe.roboflow.com/ksd-kefw7/kidney-stone-detection-bltki")
    print(f"Output directory: data_merged/")
    print(f"Split ratios: 70% train / 15% valid / 15% test")
    print(f"Quality samples: 20 images")
    print(f"Duplicate threshold: 5 (Hamming distance)")
    print()
    
    proceed = input("Proceed with these settings? (y/n): ").strip().lower()
    
    if proceed != 'y':
        print("\n❌ Merge cancelled by user")
        sys.exit(0)
    
    # Step 3: Run the pipeline
    print()
    print("Step 3: Running Merge Pipeline")
    print("-" * 70)
    print()
    
    # Save API key to environment for subprocess
    os.environ['ROBOFLOW_API_KEY'] = api_key
    
    # Run the pipeline
    cmd = [
        sys.executable, '-m', 'src.dataset_expansion.pipeline',
        '--roboflow-api-key', api_key,
        '--source-url', 'https://universe.roboflow.com/ksd-kefw7/kidney-stone-detection-bltki',
        '--current-data-dir', 'data',
        '--output-dir', 'data_merged',
        '--train-ratio', '0.70',
        '--valid-ratio', '0.15',
        '--test-ratio', '0.15',
        '--quality-sample-size', '20',
        '--hamming-threshold', '5'
    ]
    
    print("Executing pipeline...")
    print(" ".join(cmd))
    print()
    
    import subprocess
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print()
        print("=" * 70)
        print("✅ MERGE COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("📊 Next Steps:")
        print("1. Review: verification/expansion_report.md")
        print("2. Inspect: verification/quality_samples/")
        print("3. Check logs: verification/logs/expansion_pipeline.log")
        print()
        print("Once reviewed, you can retrain with:")
        print("  python src/detection/train.py --data data_merged/data.yaml --epochs 100")
        print()
    else:
        print()
        print("=" * 70)
        print("❌ MERGE FAILED")
        print("=" * 70)
        print()
        print("Check logs at: verification/logs/expansion_pipeline.log")
        print()
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Merge cancelled by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
