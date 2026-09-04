# Dataset Expansion Pipeline - Quick Start Guide

## Overview

The dataset expansion pipeline merges your current RenalScan dataset with a source dataset from Roboflow, performing comprehensive validation, quality checks, and duplicate detection.

## Prerequisites

1. **Roboflow API Key**: Sign up at https://app.roboflow.com/ and get your API key from Settings → API Keys
2. **Python Dependencies**: All required packages should already be installed from `requirements.txt`

## Basic Usage

### Option 1: Download and Merge from Roboflow

```bash
python -m src.dataset_expansion.pipeline \
    --roboflow-api-key YOUR_API_KEY \
    --source-url "https://universe.roboflow.com/workspace/project" \
    --current-data-dir data \
    --output-dir data_merged
```

### Option 2: Use Pre-Downloaded Dataset

If you've already downloaded a dataset:

```bash
python -m src.dataset_expansion.pipeline \
    --current-data-dir data \
    --source-data-dir path/to/downloaded/dataset \
    --output-dir data_merged \
    --skip-download
```

## What the Pipeline Does

The pipeline runs 5 stages automatically:

1. **Download** (optional): Authenticates with Roboflow and downloads the source dataset
2. **Verification**: 
   - Validates class definitions are compatible
   - Checks image formats and resolutions
   - Creates quality check visualizations (20 sample images)
3. **Duplicate Detection**: Identifies duplicate images using perceptual hashing
4. **Merge**: 
   - Combines datasets excluding duplicates
   - Creates 70/15/15 train/valid/test splits
   - Copies files to output directory
   - Updates data.yaml configuration
5. **Report Generation**: Creates comprehensive markdown report at `verification/expansion_report.md`

## Output Structure

After successful execution:

```
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
├── expansion_report.md          # Comprehensive verification report
├── quality_samples/             # Annotated sample images
│   └── annotated_*.jpg
└── logs/
    ├── expansion_pipeline.log   # Execution logs
    └── duplicate_report.txt     # Duplicate detection details
```

## Advanced Options

### Custom Split Ratios

```bash
python -m src.dataset_expansion.pipeline \
    --roboflow-api-key YOUR_API_KEY \
    --source-url "https://..." \
    --current-data-dir data \
    --output-dir data_merged \
    --train-ratio 0.80 \
    --valid-ratio 0.10 \
    --test-ratio 0.10
```

### Adjust Quality Check Sample Size

```bash
python -m src.dataset_expansion.pipeline \
    --roboflow-api-key YOUR_API_KEY \
    --source-url "https://..." \
    --current-data-dir data \
    --output-dir data_merged \
    --quality-sample-size 30
```

### Adjust Duplicate Detection Sensitivity

```bash
python -m src.dataset_expansion.pipeline \
    --roboflow-api-key YOUR_API_KEY \
    --source-url "https://..." \
    --current-data-dir data \
    --output-dir data_merged \
    --hamming-threshold 3  # Stricter (default is 5)
```

## After Pipeline Completion

1. **Review the Verification Report**: Open `verification/expansion_report.md`
2. **Inspect Quality Samples**: Check `verification/quality_samples/` for annotation quality
3. **Review Logs**: Check `verification/logs/expansion_pipeline.log` for detailed execution logs
4. **Check Statistics**: The report includes:
   - Total images in merged dataset
   - Split distributions (train/valid/test)
   - Duplicate detection results
   - Format validation results
   - Recommendations

## Next Steps: Model Retraining

The pipeline **DOES NOT** automatically retrain your model. After reviewing the verification report:

```bash
# Example retraining command with YOLOv8
yolo detect train \
    data=data_merged/data.yaml \
    model=yolov8n.pt \
    epochs=100 \
    imgsz=512 \
    batch=16
```

Or use your existing training script:

```bash
python src/detection/train.py \
    --data data_merged/data.yaml \
    --epochs 50 \
    --batch 16
```

## Troubleshooting

### Authentication Errors
- Verify your Roboflow API key is correct
- Check you have access to the dataset (public or owned by you)
- Ensure the dataset URL is complete and valid

### Download Failures
- The pipeline retries up to 3 times with exponential backoff
- Check your internet connection
- Verify the dataset exists on Roboflow

### Class Incompatibility
- Both datasets must have single "stone" class (or variations like "kidney_stone")
- Check your current dataset's `data/data.yaml` for class definitions

### Format Issues
- The pipeline will detect format/resolution inconsistencies
- Review the verification report for preprocessing recommendations
- Consider preprocessing images before merging if many mismatches detected

## Getting Help

For detailed documentation, see:
- Pipeline module docstring: `src/dataset_expansion/pipeline.py`
- Design document: `.kiro/specs/dataset-expansion/design.md`
- Requirements: `.kiro/specs/dataset-expansion/requirements.md`

For command-line help:
```bash
python -m src.dataset_expansion.pipeline --help
```
