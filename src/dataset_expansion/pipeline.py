"""
Dataset Expansion Pipeline

This module provides the main orchestration pipeline for expanding the RenalScan
training dataset by merging an additional Roboflow dataset. The pipeline ensures
data quality through comprehensive verification, validation, and quality checks.

USAGE:
------
Basic usage with Roboflow API:
    
    python -m src.dataset_expansion.pipeline \\
        --roboflow-api-key YOUR_API_KEY \\
        --source-url "https://universe.roboflow.com/ksd-kefw7/kidney-stone-detection-bltki" \\
        --current-data-dir data \\
        --output-dir data_merged

With custom split ratios:
    
    python -m src.dataset_expansion.pipeline \\
        --roboflow-api-key YOUR_API_KEY \\
        --source-url "https://universe.roboflow.com/ksd-kefw7/kidney-stone-detection-bltki" \\
        --current-data-dir data \\
        --output-dir data_merged \\
        --train-ratio 0.70 \\
        --valid-ratio 0.15 \\
        --test-ratio 0.15

Skip downloading and use existing source dataset:
    
    python -m src.dataset_expansion.pipeline \\
        --current-data-dir data \\
        --source-data-dir downloaded_roboflow_dataset \\
        --output-dir data_merged \\
        --skip-download

PIPELINE STAGES:
----------------
1. Download Stage (Optional)
   - Authenticates with Roboflow API
   - Downloads source dataset in YOLO format
   - Reports download statistics

2. Verification Stage
   - Validates class definitions compatibility
   - Checks image format and resolution consistency
   - Performs quality checks with visual overlays

3. Duplicate Detection Stage
   - Identifies duplicate images using perceptual hashing
   - Reports duplicate pairs and recommendations
   - Filters duplicates from merge pool

4. Merge Stage
   - Combines datasets into unified pool
   - Creates stratified train/valid/test splits (70/15/15)
   - Copies files to output directory structure
   - Updates data.yaml configuration

5. Reporting Stage
   - Generates comprehensive verification report
   - Includes statistics, quality samples, and recommendations
   - Saves report to verification/expansion_report.md

IMPORTANT NOTES:
----------------
- The pipeline DOES NOT automatically retrain the model after merging
- After completion, review the verification report before retraining
- Backup your original data.yaml (automatic backup created)
- Quality check samples saved to verification/quality_samples/
- Execution logs saved to verification/logs/expansion_pipeline.log

REQUIREMENTS:
-------------
- roboflow>=1.1.0 (for API access)
- imagehash>=4.3.1 (for duplicate detection)
- PyYAML>=6.0.1 (for YAML parsing)
- opencv-python (for image operations)
- pillow (for image loading)

OUTPUT STRUCTURE:
-----------------
After successful execution:
    
    data_merged/
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── valid/
    │   ├── images/
    │   └── labels/
    ├── test/
    │   ├── images/
    │   └── labels/
    └── data.yaml

    verification/
    ├── expansion_report.md
    ├── quality_samples/
    │   └── [annotated images]
    └── logs/
        └── expansion_pipeline.log

EXPECTED RESULTS:
-----------------
- Current dataset: ~1,300 images
- Source dataset: ~3,662 images
- Combined total: ~5,000 images (after duplicate removal)
- Train split: ~3,500 images (70%)
- Valid split: ~750 images (15%)
- Test split: ~750 images (15%)

ERROR HANDLING:
---------------
- Network errors: Automatic retry with exponential backoff (max 3 attempts)
- Authentication failures: Clear instructions for obtaining API key
- Invalid formats: Detailed recommendations for preprocessing
- File operation errors: Transactional operations with rollback on failure
- All errors logged to verification/logs/expansion_pipeline.log

NEXT STEPS AFTER PIPELINE COMPLETION:
--------------------------------------
1. Review verification/expansion_report.md
2. Inspect quality samples in verification/quality_samples/
3. Check logs in verification/logs/expansion_pipeline.log
4. If report looks good, retrain model with:
   
   python src/detection/train.py \\
       --data data_merged/data.yaml \\
       --epochs 50 \\
       --batch 16

5. Evaluate retrained model on new test set

EXAMPLES:
---------
See README.md for complete examples and troubleshooting guide.

For Roboflow API key instructions, see:
https://docs.roboflow.com/api-reference/authentication
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any


def setup_logging(log_dir: Path) -> None:
    """
    Configure logging for the pipeline.
    
    Args:
        log_dir: Directory for log files
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "expansion_pipeline.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Dataset Expansion Pipeline for RenalScan',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and merge with default settings
  python -m src.dataset_expansion.pipeline \\
      --roboflow-api-key YOUR_KEY \\
      --source-url "https://universe.roboflow.com/..." \\
      --current-data-dir data \\
      --output-dir data_merged

  # Use existing downloaded dataset
  python -m src.dataset_expansion.pipeline \\
      --current-data-dir data \\
      --source-data-dir roboflow_dataset \\
      --output-dir data_merged \\
      --skip-download

For more information, see the module docstring.
        """
    )
    
    # Download arguments
    parser.add_argument(
        '--roboflow-api-key',
        type=str,
        help='Roboflow API key for authentication'
    )
    parser.add_argument(
        '--source-url',
        type=str,
        help='Roboflow dataset URL'
    )
    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Skip download stage and use existing source dataset'
    )
    
    # Dataset directories
    parser.add_argument(
        '--current-data-dir',
        type=str,
        required=True,
        help='Path to current dataset directory'
    )
    parser.add_argument(
        '--source-data-dir',
        type=str,
        help='Path to source dataset directory (required if --skip-download)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='Output directory for merged dataset'
    )
    
    # Split ratios
    parser.add_argument(
        '--train-ratio',
        type=float,
        default=0.70,
        help='Train split ratio (default: 0.70)'
    )
    parser.add_argument(
        '--valid-ratio',
        type=float,
        default=0.15,
        help='Validation split ratio (default: 0.15)'
    )
    parser.add_argument(
        '--test-ratio',
        type=float,
        default=0.15,
        help='Test split ratio (default: 0.15)'
    )
    
    # Quality check options
    parser.add_argument(
        '--quality-sample-size',
        type=int,
        default=20,
        help='Number of images to sample for quality check (default: 20)'
    )
    
    # Duplicate detection options
    parser.add_argument(
        '--hamming-threshold',
        type=int,
        default=5,
        help='Hamming distance threshold for duplicate detection (default: 5)'
    )
    
    # Output options
    parser.add_argument(
        '--verification-dir',
        type=str,
        default='verification',
        help='Directory for verification outputs (default: verification)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.skip_download:
        if not args.roboflow_api_key or not args.source_url:
            parser.error('--roboflow-api-key and --source-url are required when not skipping download')
    else:
        if not args.source_data_dir:
            parser.error('--source-data-dir is required when --skip-download is set')
    
    # Validate split ratios
    ratio_sum = args.train_ratio + args.valid_ratio + args.test_ratio
    if abs(ratio_sum - 1.0) > 0.001:
        parser.error(f'Split ratios must sum to 1.0 (got {ratio_sum})')
    
    return args


def run_pipeline(
    current_data_dir: str,
    output_dir: str,
    source_data_dir: Optional[str] = None,
    roboflow_api_key: Optional[str] = None,
    source_url: Optional[str] = None,
    skip_download: bool = False,
    train_ratio: float = 0.70,
    valid_ratio: float = 0.15,
    test_ratio: float = 0.15,
    quality_sample_size: int = 20,
    hamming_threshold: int = 5,
    verification_dir: str = 'verification'
) -> Dict[str, Any]:
    """
    Execute the complete dataset expansion pipeline.
    
    This function orchestrates all pipeline stages in sequence:
    1. Download (optional)
    2. Verification (class validation, format checking, quality checks)
    3. Duplicate detection
    4. Dataset merging
    5. Report generation
    
    Args:
        current_data_dir: Path to current dataset
        output_dir: Output directory for merged dataset
        source_data_dir: Path to source dataset (if skip_download=True)
        roboflow_api_key: Roboflow API key (if skip_download=False)
        source_url: Roboflow dataset URL (if skip_download=False)
        skip_download: Skip download stage
        train_ratio: Training set ratio (default: 0.70)
        valid_ratio: Validation set ratio (default: 0.15)
        test_ratio: Test set ratio (default: 0.15)
        quality_sample_size: Number of images for quality check (default: 20)
        hamming_threshold: Duplicate detection threshold (default: 5)
        verification_dir: Directory for verification outputs
    
    Returns:
        Dictionary containing pipeline results and statistics
    
    Raises:
        ValueError: If arguments are invalid
        RuntimeError: If pipeline stage fails
    
    Note:
        This function DOES NOT trigger model retraining. After successful
        completion, review the verification report before manually retraining.
    """
    from .downloader import RoboflowDownloader
    from .validators import ClassValidator, FormatValidator
    from .quality_checker import QualityChecker
    from .duplicate_detector import DuplicateDetector
    from .merger import DatasetMerger
    from .report_generator import ReportGenerator
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("Dataset Expansion Pipeline Starting")
    logger.info("=" * 70)
    
    # Setup paths
    verification_path = Path(verification_dir)
    quality_samples_dir = verification_path / 'quality_samples'
    quality_samples_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        'stages_completed': [],
        'download_results': None,
        'class_validation': None,
        'format_validation': None,
        'quality_check': None,
        'duplicate_detection': None,
        'merge_results': None,
        'report_path': None
    }
    
    try:
        # Stage 1: Download (if not skipped)
        if not skip_download:
            logger.info("\n[Stage 1/5] Downloading source dataset...")
            downloader = RoboflowDownloader(roboflow_api_key, source_url)
            
            if not downloader.authenticate():
                raise RuntimeError("Failed to authenticate with Roboflow API")
            
            temp_download_dir = source_data_dir if source_data_dir else 'temp_roboflow_download'
            download_result = downloader.download_dataset(temp_download_dir)
            
            if not download_result.success:
                raise RuntimeError(f"Download failed: {download_result.error_message}")
            
            source_data_dir = download_result.download_path
            results['download_results'] = {
                'source_url': source_url,
                'total_images': download_result.total_images,
                'train_images': download_result.train_images,
                'valid_images': download_result.valid_images,
                'test_images': download_result.test_images,
                'status': 'Success'
            }
            logger.info("Download stage completed")
            results['stages_completed'].append('download')
        else:
            logger.info("\n[Stage 1/5] Skipping download (using existing source dataset)")
            results['download_results'] = {'status': 'Skipped', 'source_url': 'N/A'}
            results['stages_completed'].append('download_skipped')
        
        # Stage 2: Verification
        logger.info("\n[Stage 2/5] Running verification checks...")
        
        # Class validation
        current_yaml = os.path.join(current_data_dir, 'data.yaml')
        source_yaml = os.path.join(source_data_dir, 'data.yaml')
        
        class_validator = ClassValidator(current_yaml, source_yaml)
        validation_result = class_validator.validate_compatibility()
        results['class_validation'] = {
            'is_compatible': validation_result.is_compatible,
            'current_classes': validation_result.current_classes,
            'source_classes': validation_result.source_classes,
            'needs_remapping': validation_result.needs_remapping,
            'mapping': validation_result.mapping,
            'message': validation_result.message
        }
        
        if not validation_result.is_compatible:
            raise RuntimeError(f"Class validation failed: {validation_result.message}")
        
        logger.info(f"Class validation: {validation_result.message}")
        
        # Format validation
        image_dirs = []
        for dataset_dir in [current_data_dir, source_data_dir]:
            for split in ['train', 'valid', 'test']:
                img_dir = os.path.join(dataset_dir, split, 'images')
                if os.path.exists(img_dir):
                    image_dirs.append(img_dir)
        
        format_validator = FormatValidator(image_dirs)
        format_report = format_validator.analyze_formats()
        resolution_report = format_validator.analyze_resolutions()
        consistency_report = format_validator.check_consistency()
        recommendations = format_validator.recommend_preprocessing(consistency_report)
        
        results['format_validation'] = {
            'format_report': {
                'format_counts': format_report.format_counts,
                'total_images': format_report.total_images
            },
            'resolution_report': {
                'resolution_counts': resolution_report.resolution_counts,
                'total_images': resolution_report.total_images
            },
            'consistency_report': {
                'target_format': consistency_report.target_format,
                'target_resolution': consistency_report.target_resolution,
                'format_matches': consistency_report.format_matches,
                'format_mismatches': consistency_report.format_mismatches,
                'resolution_matches': consistency_report.resolution_matches,
                'resolution_mismatches': consistency_report.resolution_mismatches,
                'total_images': consistency_report.total_images
            },
            'recommendations': recommendations
        }
        
        logger.info(f"Format validation: {len(recommendations)} recommendations")
        
        # Quality check
        source_train_images = os.path.join(source_data_dir, 'train', 'images')
        source_train_labels = os.path.join(source_data_dir, 'train', 'labels')
        
        if os.path.exists(source_train_images) and os.path.exists(source_train_labels):
            quality_checker = QualityChecker(
                source_train_images,
                source_train_labels,
                validation_result.source_classes
            )
            sampled_images = quality_checker.random_sample(quality_sample_size)
            quality_checker.visualize_annotations(sampled_images, str(quality_samples_dir))
            
            results['quality_check'] = {
                'sample_count': len(sampled_images),
                'output_dir': str(quality_samples_dir),
                'summary': f'Generated {len(sampled_images)} quality visualizations'
            }
            logger.info(f"Quality check: {len(sampled_images)} samples visualized")
        
        logger.info("Verification stage completed")
        results['stages_completed'].append('verification')
        
        # Stage 3: Duplicate Detection
        logger.info("\n[Stage 3/5] Detecting duplicates...")
        
        duplicate_detector = DuplicateDetector(hamming_threshold=hamming_threshold)
        
        # Collect image paths from both datasets
        current_images = []
        source_images = []
        
        for split in ['train', 'valid', 'test']:
            current_img_dir = os.path.join(current_data_dir, split, 'images')
            if os.path.exists(current_img_dir):
                for img_file in os.listdir(current_img_dir):
                    if any(img_file.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        current_images.append(os.path.join(current_img_dir, img_file))
            
            source_img_dir = os.path.join(source_data_dir, split, 'images')
            if os.path.exists(source_img_dir):
                for img_file in os.listdir(source_img_dir):
                    if any(img_file.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        source_images.append(os.path.join(source_img_dir, img_file))
        
        # Find duplicates
        perceptual_duplicates = duplicate_detector.find_duplicates(current_images, source_images)
        filename_duplicates = duplicate_detector.check_filename_duplicates(current_images, source_images)
        
        # Generate duplicate report
        dup_report = duplicate_detector.generate_duplicate_report(
            str(verification_path / 'logs' / 'duplicate_report.txt')
        )
        
        results['duplicate_detection'] = dup_report
        
        # Extract duplicate paths to exclude
        duplicates_to_remove = [dup[1] for dup in perceptual_duplicates]  # Remove from source dataset
        
        logger.info(f"Duplicate detection: {len(duplicates_to_remove)} duplicates found")
        logger.info("Duplicate detection completed")
        results['stages_completed'].append('duplicate_detection')
        
        # Stage 4: Dataset Merging
        logger.info("\n[Stage 4/5] Merging datasets...")
        
        merger = DatasetMerger(
            current_data_dir=current_data_dir,
            source_data_dir=source_data_dir,
            output_data_dir=output_dir,
            duplicates_to_remove=duplicates_to_remove
        )
        
        # Backup original data.yaml
        if os.path.exists(current_yaml):
            merger.backup_original_data_yaml(current_yaml)
        
        # Collect all samples
        all_samples = merger.collect_all_samples()
        
        # Create splits
        splits = merger.stratified_split(
            all_samples,
            ratios=(train_ratio, valid_ratio, test_ratio)
        )
        
        # Copy files to output directory
        merger.copy_files_to_splits(splits, output_dir)
        
        # Update data.yaml
        merger.update_data_yaml(
            output_dir=output_dir,
            class_names=validation_result.current_classes,
            original_yaml_path=current_yaml
        )
        
        # Collect merge statistics
        split_counts = splits.get_counts()
        
        # Count sources
        source_counts = {'current': 0, 'roboflow': 0}
        for sample in all_samples:
            source_counts[sample.source] = source_counts.get(sample.source, 0) + 1
        
        results['merge_results'] = {
            'output_dir': output_dir,
            'splits': split_counts,
            'source_distribution': source_counts
        }
        
        logger.info("Dataset merging completed")
        results['stages_completed'].append('merge')
        
        # Stage 5: Report Generation
        logger.info("\n[Stage 5/5] Generating verification report...")
        
        report_generator = ReportGenerator(results)
        report_path = str(verification_path / 'expansion_report.md')
        report_generator.generate_report(report_path)
        
        results['report_path'] = report_path
        logger.info("Report generation completed")
        results['stages_completed'].append('report')
        
        logger.info("\n" + "=" * 70)
        logger.info("Pipeline completed successfully!")
        logger.info(f"Verification report: {report_path}")
        logger.info(f"Quality samples: {quality_samples_dir}")
        logger.info(f"Logs: {verification_path / 'logs' / 'expansion_pipeline.log'}")
        logger.info("=" * 70)
        logger.info("\nIMPORTANT: Review the verification report before retraining.")
        logger.info("The pipeline does NOT automatically retrain the model.")
        
        return results
        
    except Exception as e:
        logger.error(f"\nPipeline failed at stage: {results['stages_completed'][-1] if results['stages_completed'] else 'initialization'}")
        logger.error(f"Error: {str(e)}")
        raise


def main():
    """
    Main entry point for the dataset expansion pipeline.
    
    Parses command-line arguments, sets up logging, and executes the pipeline.
    """
    args = parse_arguments()
    
    # Setup logging
    verification_path = Path(args.verification_dir)
    setup_logging(verification_path / 'logs')
    
    logger = logging.getLogger(__name__)
    
    try:
        # Run pipeline
        results = run_pipeline(
            current_data_dir=args.current_data_dir,
            output_dir=args.output_dir,
            source_data_dir=args.source_data_dir,
            roboflow_api_key=args.roboflow_api_key,
            source_url=args.source_url,
            skip_download=args.skip_download,
            train_ratio=args.train_ratio,
            valid_ratio=args.valid_ratio,
            test_ratio=args.test_ratio,
            quality_sample_size=args.quality_sample_size,
            hamming_threshold=args.hamming_threshold,
            verification_dir=args.verification_dir
        )
        
        logger.info("\n✓ Pipeline execution completed successfully")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"\n✗ Pipeline execution failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
