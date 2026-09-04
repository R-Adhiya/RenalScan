"""
Enhanced YOLOv8s Training Script for Merged Dataset
Uses YOLOv8s (small) model with enhanced augmentation to improve recall.
Saves results to test_metrics_v2.txt for comparison with baseline.
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

from ultralytics import YOLO

def train_yolov8s_enhanced(
    data_yaml='data_merged/data.yaml',
    epochs=100,
    imgsz=512,
    batch=16,
    patience=10,
    device=None
):
    """
    Train YOLOv8s with enhanced augmentation on merged dataset.
    
    Enhancements:
    - YOLOv8s instead of YOLOv8n (more capacity)
    - Stronger augmentation (brightness, contrast, scale) to improve recall
    - Early stopping with patience=10
    - Saves to test_metrics_v2.txt (preserves original for comparison)
    """
    project_root = Path(__file__).resolve().parent
    
    # Resolve data.yaml path
    data_yaml_path = project_root / data_yaml
    if not data_yaml_path.exists():
        raise FileNotFoundError(f"data.yaml not found: {data_yaml_path}")
    
    models_dir = project_root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Auto-detect device
    if device is None or device == "":
        if torch.cuda.is_available():
            device = "0"
            print("🚀 CUDA GPU Detected! Running training on GPU.")
        else:
            device = "cpu"
            print("⚠️  WARNING: No GPU detected. Training on CPU (this will be slow).")
    
    print("=" * 70)
    print("YOLOV8S ENHANCED TRAINING - MERGED DATASET")
    print("=" * 70)
    print(f"Model: YOLOv8s (small - upgraded from nano)")
    print(f"Data: {data_yaml_path}")
    print(f"Epochs: {epochs}")
    print(f"Image Size: {imgsz}")
    print(f"Batch: {batch}")
    print(f"Device: {device}")
    print(f"Early Stopping Patience: {patience}")
    print()
    print("Enhanced Augmentation:")
    print("  - hsv_h: 0.015 (hue variation)")
    print("  - hsv_s: 0.7 (saturation boost)")
    print("  - hsv_v: 0.4 (brightness/contrast jitter)")
    print("  - degrees: 5.0 (mild rotation)")
    print("  - translate: 0.1 (position variation)")
    print("  - scale: 0.3 (zoom for small stones)")
    print("  - flipud: 0.05 (vertical flip)")
    print("=" * 70)
    print()
    
    # Initialize YOLOv8s model
    print("Loading YOLOv8s pretrained weights...")
    model = YOLO("yolov8s.pt")
    
    start_time = time.time()
    
    # Train with enhanced augmentation
    results = model.train(
        data=str(data_yaml_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        patience=patience,
        device=device,
        workers=2,
        project=str(project_root / "runs" / "detect"),
        name="yolov8s_merged_enhanced",
        exist_ok=True,
        verbose=True,
        # Enhanced augmentation parameters
        hsv_h=0.015,  # Hue variation
        hsv_s=0.7,    # Saturation boost
        hsv_v=0.4,    # Brightness/contrast jitter (helps with recall)
        degrees=5.0,  # Mild rotation
        translate=0.1, # Position variation
        scale=0.3,    # Scale/zoom (helps detect small stones)
        flipud=0.05,  # Vertical flip
        # Keep other augmentations at defaults
        fliplr=0.5,   # Horizontal flip (default)
        mosaic=1.0,   # Mosaic augmentation
        mixup=0.0,    # No mixup
    )
    
    elapsed_seconds = time.time() - start_time
    avg_sec_per_epoch = elapsed_seconds / epochs if epochs > 0 else 0
    
    print()
    print("=" * 70)
    print(f"Training completed in {elapsed_seconds:.2f} seconds ({avg_sec_per_epoch:.2f} s/epoch)")
    print("=" * 70)
    print()
    
    # Copy best weights
    run_dir = project_root / "runs" / "detect" / "yolov8s_merged_enhanced"
    best_weights = run_dir / "weights" / "best.pt"
    target_best_weights = models_dir / "detection_best_v2.pt"
    
    if best_weights.exists():
        shutil.copy(best_weights, target_best_weights)
        print(f"✅ Saved best model weights to: {target_best_weights}")
    else:
        print("⚠️  Warning: best.pt not found, using last.pt")
        last_weights = run_dir / "weights" / "last.pt"
        if last_weights.exists():
            shutil.copy(last_weights, target_best_weights)
    
    # Held-out Test Set Evaluation
    print()
    print("=" * 70)
    print("RUNNING HELD-OUT TEST SET EVALUATION")
    print("=" * 70)
    print()
    
    best_model = YOLO(str(target_best_weights))
    test_metrics = best_model.val(
        data=str(data_yaml_path),
        split="test",
        imgsz=imgsz,
        device=device
    )
    
    # Extract metrics
    precision = float(test_metrics.box.mp)
    recall = float(test_metrics.box.mr)
    map50 = float(test_metrics.box.map50)
    map50_95 = float(test_metrics.box.map)
    
    # Calculate F1 score
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Create metrics summary
    metrics_summary = (
        "=" * 70 + "\n"
        "RENALSCAN YOLOv8S — MERGED DATASET TEST METRICS (V2)\n"
        "=" * 70 + "\n"
        f"Model: YOLOv8s (Small)\n"
        f"Training Dataset: Merged (3,305 images)\n"
        f"Test Split: data_merged/test (497 images)\n"
        f"Image Resolution: {imgsz}x{imgsz} px\n"
        f"Total Epochs Trained: {epochs}\n"
        f"Device Used: {device}\n"
        f"Training Time: {elapsed_seconds:.2f} sec ({avg_sec_per_epoch:.2f} s/epoch)\n"
        "-" * 70 + "\n"
        f"Precision (P):    {precision:.4f} ({precision * 100:.2f}%)\n"
        f"Recall (R):       {recall:.4f} ({recall * 100:.2f}%)\n"
        f"F1 Score:         {f1_score:.4f} ({f1_score * 100:.2f}%)\n"
        f"mAP@0.50:         {map50:.4f} ({map50 * 100:.2f}%)\n"
        f"mAP@0.50:0.95:    {map50_95:.4f} ({map50_95 * 100:.2f}%)\n"
        "=" * 70 + "\n"
        "\nCOMPARISON WITH BASELINE (v1):\n"
        "-" * 70 + "\n"
        "See models/test_metrics.txt for baseline metrics:\n"
        "  - Model: YOLOv8n (Nano)\n"
        "  - Dataset: Original (1,300 images)\n"
        "  - Baseline Recall: 69.64%\n"
        "\nV2 Improvements:\n"
        f"  - Model Size: Nano → Small (+capacity)\n"
        f"  - Dataset: 1,300 → 3,305 images (+154%)\n"
        f"  - Augmentation: Enhanced (focus on recall)\n"
        "=" * 70 + "\n"
    )
    
    print()
    print(metrics_summary)
    
    # Save to test_metrics_v2.txt
    metrics_file = models_dir / "test_metrics_v2.txt"
    with open(metrics_file, "w", encoding="utf-8") as f:
        f.write(metrics_summary)
    
    print(f"✅ Saved V2 test metrics to: {metrics_file}")
    print(f"📊 Original metrics preserved at: models/test_metrics.txt")
    print()
    
    return {
        'elapsed_seconds': elapsed_seconds,
        'avg_sec_per_epoch': avg_sec_per_epoch,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'map50': map50,
        'map50_95': map50_95
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train YOLOv8s with enhanced augmentation on merged dataset"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data_merged/data.yaml",
        help="Path to data.yaml (default: data_merged/data.yaml)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of training epochs (default: 100)"
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=512,
        help="Image resolution (default: 512)"
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
        help="Device (e.g., '0', 'cpu', 'cuda')"
    )
    
    args = parser.parse_args()
    
    train_yolov8s_enhanced(
        data_yaml=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=args.patience,
        device=args.device
    )
