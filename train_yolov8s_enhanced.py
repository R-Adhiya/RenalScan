"""
YOLOv8s Training Script for Merged Dataset with Enhanced Augmentation

This script trains YOLOv8s (Small variant) on the merged 3,305-image dataset
with enhanced augmentation to improve recall performance.

Key improvements:
- YOLOv8s instead of YOLOv8n (more capacity for larger dataset)
- Enhanced augmentation (brightness, contrast, scale) to help recall
- Training on merged dataset (3,305 images)
- Early stopping with patience=10
- Saves results to test_metrics_v2.txt (preserves original for comparison)
"""

import argparse
import os
import shutil
import time
from pathlib import Path
import torch

# Optimize PyTorch CPU thread allocation
num_cpus = os.cpu_count() or 4
torch.set_num_threads(num_cpus)

from ultralytics import YOLO, settings


def train_yolov8s_enhanced(
    data_yaml='data_merged/data.yaml',
    epochs=100,
    imgsz=512,
    batch=16,
    patience=10,
    device=None
):
    """
    Train YOLOv8s on merged dataset with enhanced augmentation.
    
    Args:
        data_yaml: Path to merged dataset configuration
        epochs: Maximum training epochs (early stopping may end sooner)
        imgsz: Image size for training
        batch: Batch size
        patience: Early stopping patience
        device: Device to train on (auto-detected if None)
    """
    
    project_root = Path(__file__).resolve().parent
    models_dir = project_root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    settings.update({'datasets_dir': str(project_root)})
    
    # Check if merged dataset exists
    data_yaml_path = project_root / data_yaml
    if not data_yaml_path.exists():
        raise FileNotFoundError(
            f"Merged dataset not found at {data_yaml_path}. "
            "Please run dataset expansion pipeline first."
        )
    
    # Auto-detect device
    if device is None or device == "":
        if torch.cuda.is_available():
            device = "0"
            print("🚀 CUDA GPU Detected! Running training on GPU (device '0').")
        else:
            device = "cpu"
            print("⚠️  WARNING: CUDA GPU not detected. Training on CPU.")
            print("   Training on CPU will be significantly slower.")
    
    print("=" * 70)
    print("YOLOV8S TRAINING ON MERGED DATASET")
    print("=" * 70)
    print(f"Model:       YOLOv8s (Small variant)")
    print(f"Dataset:     {data_yaml_path}")
    print(f"Images:      3,305 total (2,313 train / 495 valid / 497 test)")
    print(f"Epochs:      {epochs} (with early stopping patience={patience})")
    print(f"Image Size:  {imgsz}x{imgsz}")
    print(f"Batch Size:  {batch}")
    print(f"Device:      {device}")
    print(f"Augmentation: Enhanced (see config below)")
    print("=" * 70)
    print()
    
    # Initialize YOLOv8s model
    print("Loading YOLOv8s pretrained weights...")
    model = YOLO("yolov8s.pt")
    print("✅ Model loaded")
    print()
    
    start_time = time.time()
    
    print("Starting training with enhanced augmentation...")
    print()
    
    # Enhanced augmentation parameters to improve recall
    # The original model had precision=84.80% but recall=69.64%
    # These augmentations help the model detect more stones (improve recall)
    results = model.train(
        data=str(data_yaml_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        patience=patience,
        device=device,
        workers=2,
        
        # Enhanced augmentation parameters
        # These help expose the model to more variations, improving recall
        hsv_h=0.015,      # Hue augmentation (color variation)
        hsv_s=0.7,        # Saturation augmentation
        hsv_v=0.4,        # Brightness/value augmentation (increased from default 0.4)
        degrees=5.0,      # Rotation augmentation (slight rotation)
        translate=0.1,    # Translation augmentation
        scale=0.5,        # Scale augmentation (helps with small stones)
        fliplr=0.5,       # Horizontal flip probability
        mosaic=1.0,       # Mosaic augmentation (combines 4 images)
        mixup=0.0,        # Mixup augmentation (disabled for medical images)
        
        # Training hyperparameters
        optimizer='auto',  # Auto-select optimizer
        lr0=0.01,         # Initial learning rate
        lrf=0.01,         # Final learning rate (lr0 * lrf)
        momentum=0.937,   # SGD momentum
        weight_decay=0.0005,  # Weight decay
        warmup_epochs=3.0,    # Warmup epochs
        warmup_momentum=0.8,  # Warmup momentum
        
        # Output settings
        project=str(project_root / "runs" / "detect"),
        name="train_yolov8s_merged",
        exist_ok=True,
        verbose=True,
        save=True,
        save_period=-1,  # Save only best and last
        plots=True
    )
    
    elapsed_seconds = time.time() - start_time
    actual_epochs = len(results.results_dict.get('train/box_loss', [epochs]))
    avg_sec_per_epoch = elapsed_seconds / actual_epochs if actual_epochs > 0 else 0
    
    print()
    print("=" * 70)
    print(f"Training completed in {elapsed_seconds:.2f} seconds")
    print(f"Actual epochs: {actual_epochs} ({avg_sec_per_epoch:.2f} sec/epoch)")
    print("=" * 70)
    print()
    
    # Copy best weights
    run_dir = project_root / "runs" / "detect" / "train_yolov8s_merged"
    best_weights = run_dir / "weights" / "best.pt"
    target_best_weights = models_dir / "detection_best_v2.pt"
    
    if best_weights.exists():
        shutil.copy(best_weights, target_best_weights)
        print(f"✅ Saved best model weights to: {target_best_weights}")
    else:
        print("⚠️  Best weights not found")
    
    # Held-out Test Set Evaluation
    print()
    print("=" * 70)
    print("EVALUATING ON HELD-OUT TEST SET...")
    print("=" * 70)
    print()
    
    # Load best trained model for evaluation
    best_model = YOLO(str(target_best_weights if target_best_weights.exists() else best_weights))
    test_metrics = best_model.val(
        data=str(data_yaml_path),
        split="test",
        imgsz=imgsz,
        device=device,
        verbose=True
    )
    
    # Extract metrics
    precision = float(test_metrics.box.mp)
    recall = float(test_metrics.box.mr)
    map50 = float(test_metrics.box.map50)
    map50_95 = float(test_metrics.box.map)
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Format results
    metrics_summary = (
        "=" * 70 + "\n"
        "RENALSCAN YOLOv8S — MERGED DATASET TEST METRICS (V2)\n"
        "=" * 70 + "\n"
        f"Model Version    : YOLOv8s (Small variant)\n"
        f"Dataset          : Merged dataset (3,305 images)\n"
        f"Evaluation Split : Held-Out Test Set (data_merged/test)\n"
        f"Image Resolution : {imgsz}x{imgsz} px\n"
        f"Total Epochs     : {actual_epochs}\n"
        f"Device Used      : {device}\n"
        f"Training Time    : {elapsed_seconds:.2f} sec ({avg_sec_per_epoch:.2f} s/epoch)\n"
        "-" * 70 + "\n"
        "METRICS\n"
        "-" * 70 + "\n"
        f"Precision (P)    : {precision:.4f} ({precision * 100:.2f}%)\n"
        f"Recall (R)       : {recall:.4f} ({recall * 100:.2f}%)\n"
        f"F1 Score         : {f1_score:.4f} ({f1_score * 100:.2f}%)\n"
        f"mAP@0.50         : {map50:.4f} ({map50 * 100:.2f}%)\n"
        f"mAP@0.50:0.95    : {map50_95:.4f} ({map50_95 * 100:.2f}%)\n"
        "=" * 70 + "\n"
        "\n"
        "COMPARISON WITH V1 (Original 1,300 images, YOLOv8n)\n"
        "-" * 70 + "\n"
        "V1 Metrics (from test_metrics.txt):\n"
        "  Precision:     84.80%\n"
        "  Recall:        69.64%\n"
        "  F1 Score:      76.48%\n"
        "  mAP@0.50:      73.03%\n"
        "  mAP@0.50:0.95: 31.82%\n"
        "\n"
        "V2 Metrics (current):\n"
        f"  Precision:     {precision * 100:.2f}%\n"
        f"  Recall:        {recall * 100:.2f}%\n"
        f"  F1 Score:      {f1_score * 100:.2f}%\n"
        f"  mAP@0.50:      {map50 * 100:.2f}%\n"
        f"  mAP@0.50:0.95: {map50_95 * 100:.2f}%\n"
        "\n"
        "Changes:\n"
        f"  Precision:     {(precision - 0.8480) * 100:+.2f}%\n"
        f"  Recall:        {(recall - 0.6964) * 100:+.2f}%\n"
        f"  F1 Score:      {(f1_score - 0.7648) * 100:+.2f}%\n"
        f"  mAP@0.50:      {(map50 - 0.7303) * 100:+.2f}%\n"
        f"  mAP@0.50:0.95: {(map50_95 - 0.3182) * 100:+.2f}%\n"
        "=" * 70 + "\n"
    )
    
    print()
    print(metrics_summary)
    
    # Save to test_metrics_v2.txt
    metrics_file = models_dir / "test_metrics_v2.txt"
    with open(metrics_file, "w", encoding="utf-8") as f:
        f.write(metrics_summary)
    
    print(f"✅ Saved test set evaluation metrics to: {metrics_file}")
    print()
    print("=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review metrics in models/test_metrics_v2.txt")
    print("2. Compare with original metrics in models/test_metrics.txt")
    print("3. Check training curves in runs/detect/train_yolov8s_merged/")
    print()
    
    return {
        'elapsed_seconds': elapsed_seconds,
        'actual_epochs': actual_epochs,
        'avg_sec_per_epoch': avg_sec_per_epoch,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'map50': map50,
        'map50_95': map50_95
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train YOLOv8s on merged dataset with enhanced augmentation"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data_merged/data.yaml",
        help="Path to merged dataset YAML file"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Maximum number of training epochs (default: 100)"
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=512,
        help="Image size for training (default: 512)"
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Batch size (default: 16)"
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=10,
        help="Early stopping patience (default: 10)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device to train on (e.g. '0', 'cpu', 'cuda')"
    )
    
    args = parser.parse_args()
    
    try:
        train_yolov8s_enhanced(
            data_yaml=args.data,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            patience=args.patience,
            device=args.device
        )
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
