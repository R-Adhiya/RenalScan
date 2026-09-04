"""
Enhanced Training Script for RenalScan v2
- Uses YOLOv8s (upgraded from YOLOv8n)
- Trains on merged dataset (3,305 images)
- Enhanced augmentation for better recall
- Saves to test_metrics_v2.txt
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

def train_yolo_v2(
    data_yaml='data_merged/data.yaml',
    model='yolov8s.pt',
    epochs=100,
    imgsz=512,
    batch=16,
    patiene augmentation to better detect small stones
    - Moderate rotation and translation for positional variance
    - Higher mosaic probability for learning multi-scale features
    """
    project_root = Path(__file__).resolve().parent
    
    # Use merged dataset
    data_yaml_path = project_root / "data_merged" / "data.yaml"
    
    if not data_yaml_path.exists():
        raise FileNotFoundError(
            f"Merged dataset not found at {data_yaml_path}. "
            "Please run the dataset expansion pipeline first."
        )
    
    models_dir = project_root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Auto-detect device
    if device is None or device == "":
        if torch.cuda.is_available():
            device = "0"
            print("🚀 CUDA GPU Detected! Running training on GPU (device '0').")
        else:
            device = "cpu"
            print("⚠️  WARNING: CUDA GPU not detected. Training on CPU will be slow.")
            print("   Consider using Google Colab with T4 GPU for faster training.")
    
    print("=" * 70)
    print("YOLOV8S ENHANCED TRAINING - VERSION 2")
    print("=" * 70)
    print(f"Model: YOLOv8s (Small) - Upgraded from YOLOv8n")
    print(f"Dataset: {data_yaml_path}")
    print(f"Images: 3,305 (2.5x increase from v1)")
    print(f"Epochs: {epochs} (with patience={patience})")
    print(f"Image Size: {imgsz}x{imgsz}")
    print(f"Batch: {batch}")
    print(f"Device: {device}")
    print("=" * 70)
    print()
    print("Enhanced Augmentation Strategy:")
    print("  • hsv_h: 0.015 → Color hue variation")
    print("  • hsv_s: 0.7 → Saturation variation (higher)")
    print("  • hsv_v: 0.4 → Brightness/value variation (higher)")
    print("  • degrees: 15 → Rotation augmentation")
    print("  • translate: 0.2 → Translation augmentation")
    print("  • scale: 0.7 → Scale variation for small stones (higher)")
    print("  • mosaic: 1.0 → Always use mosaic augmentation")
    print("  • mixup: 0.1 → Mix two images occasionally")
    print("=" * 70)
    print()
    
    # Initialize YOLOv8 Small model (larger than nano)
    print("Loading YOLOv8s pretrained weights...")
    model = YOLO("yolov8s.pt")
    print("✅ YOLOv8s model loaded")
    print()
    
    start_time = time.time()
    
    # Run training with enhanced augmentation
    print("Starting training...")
    results = model.train(
        data=str(data_yaml_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        patience=patience,
        device=device,
        workers=2,
        project=str(project_root / "runs" / "detect"),
        name="train_v2_enhanced",
        exist_ok=True,
        verbose=True,
        
        # Enhanced augmentation parameters
        # These are specifically tuned to improve recall on kidney stones
        hsv_h=0.015,      # Slight hue variation
        hsv_s=0.7,        # Higher saturation variation (stones vary in CT density)
        hsv_v=0.4,        # Higher brightness variation (help with contrast differences)
        degrees=15,       # Moderate rotation
        translate=0.2,    # Moderate translation
        scale=0.7,        # Higher scale variation (important for small stones!)
        shear=2,          # Slight shear transformation
        perspective=0.0,  # No perspective (medical images are orthogonal)
        flipud=0.0,       # No vertical flip (CT scans have consistent orientation)
        fliplr=0.5,       # Horizontal flip OK (left/right kidney symmetry)
        mosaic=1.0,       # Always use mosaic (learns multi-scale features)
        mixup=0.1,        # Occasional mixup for robustness
        copy_paste=0.0,   # No copy-paste (preserve medical image realism)
        
        # Optimizer settings
        optimizer='AdamW',  # AdamW generally works well
        lr0=0.001,         # Initial learning rate
        lrf=0.01,          # Final learning rate (1% of initial)
        momentum=0.937,    # SGD momentum
        weight_decay=0.0005,  # L2 regularization
        warmup_epochs=3,   # Warmup period
        warmup_momentum=0.8,  # Warmup momentum
        
        # Loss weights (default usually fine, but can tune if needed)
        box=7.5,           # Box loss weight
        cls=0.5,           # Class loss weight
        dfl=1.5,           # Distribution focal loss weight
        
        # Other settings
        cos_lr=True,       # Cosine learning rate scheduler
        close_mosaic=10,   # Disable mosaic in last 10 epochs for stability
    )
    
    elapsed_seconds = time.time() - start_time
    avg_sec_per_epoch = elapsed_seconds / epochs if epochs > 0 else 0
    print(f"\n✅ Training completed in {elapsed_seconds:.2f} seconds ({avg_sec_per_epoch:.2f} sec/epoch)")
    
    # Copy best weights to models/detection_best_v2.pt
    run_dir = project_root / "runs" / "detect" / "train_v2_enhanced"
    best_weights = run_dir / "weights" / "best.pt"
    target_best_weights = models_dir / "detection_best_v2.pt"
    
    if best_weights.exists():
        shutil.copy(best_weights, target_best_weights)
        print(f"✅ Saved best model weights to: {target_best_weights}")
    else:
        print(f"⚠️  Warning: Best weights not found at {best_weights}")
        return None
    
    # Held-out Test Set Evaluation
    print("\n" + "=" * 70)
    print("RUNNING HELD-OUT TEST SET EVALUATION (split='test')...")
    print("=" * 70)
    print()
    
    # Load best trained model for evaluation
    print("Loading best model for evaluation...")
    best_model = YOLO(str(target_best_weights))
    print("Running validation on test set...")
    test_metrics = best_model.val(data=str(data_yaml_path), split="test", imgsz=imgsz, device=device)
    
    # Extract metrics
    precision = float(test_metrics.box.mp)
    recall = float(test_metrics.box.mr)
    map50 = float(test_metrics.box.map50)
    map50_95 = float(test_metrics.box.map)
    
    # Calculate F1 score
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    metrics_summary = (
        "=====================================================\n"
        "RENALSCAN YOLOv8S DETECTION — HELD-OUT TEST METRICS (V2)\n"
        "=====================================================\n"
        f"Model Version    : V2 (YOLOv8s with enhanced augmentation)\n"
        f"Dataset          : Merged dataset (3,305 images)\n"
        f"Evaluation Split : Held-Out Test Set (data_merged/test)\n"
        f"Test Set Size    : 497 images\n"
        f"Image Resolution : {imgsz}x{imgsz} px\n"
        f"Total Epochs     : {epochs}\n"
        f"Device Used      : {device}\n"
        f"Training Time    : {elapsed_seconds:.2f} sec ({avg_sec_per_epoch:.2f} s/epoch)\n"
        "-----------------------------------------------------\n"
        f"Precision (P)    : {precision:.4f} ({precision * 100:.2f}%)\n"
        f"Recall (R)       : {recall:.4f} ({recall * 100:.2f}%)\n"
        f"F1 Score         : {f1_score:.4f} ({f1_score * 100:.2f}%)\n"
        f"mAP@0.50         : {map50:.4f} ({map50 * 100:.2f}%)\n"
        f"mAP@0.50:0.95    : {map50_95:.4f} ({map50_95 * 100:.2f}%)\n"
        "=====================================================\n"
        "\n"
        "COMPARISON WITH V1 (YOLOv8n on 1,300 images):\n"
        "-----------------------------------------------------\n"
        "V1 Precision:  0.8480 (84.80%)\n"
        "V2 Precision:  {:.4f} ({:.2f}%) → {:+.2f}%\n"
        "\n"
        "V1 Recall:     0.6964 (69.64%)\n"
        "V2 Recall:     {:.4f} ({:.2f}%) → {:+.2f}%\n"
        "\n"
        "V1 F1 Score:   0.7648 (76.48%)\n"
        "V2 F1 Score:   {:.4f} ({:.2f}%) → {:+.2f}%\n"
        "\n"
        "V1 mAP@0.50:   0.7303 (73.03%)\n"
        "V2 mAP@0.50:   {:.4f} ({:.2f}%) → {:+.2f}%\n"
        "\n"
        "V1 mAP@0.50:0.95: 0.3182 (31.82%)\n"
        "V2 mAP@0.50:0.95: {:.4f} ({:.2f}%) → {:+.2f}%\n"
        "=====================================================\n"
    ).format(
        precision, precision * 100, (precision - 0.8480) * 100,
        recall, recall * 100, (recall - 0.6964) * 100,
        f1_score, f1_score * 100, (f1_score - 0.7648) * 100,
        map50, map50 * 100, (map50 - 0.7303) * 100,
        map50_95, map50_95 * 100, (map50_95 - 0.3182) * 100
    )
    
    print("\n" + metrics_summary)
    
    # Save to test_metrics_v2.txt (preserve original test_metrics.txt)
    metrics_file_v2 = models_dir / "test_metrics_v2.txt"
    with open(metrics_file_v2, "w", encoding="utf-8") as f:
        f.write(metrics_summary)
    print(f"✅ Saved test set evaluation metrics to: {metrics_file_v2}")
    print(f"📊 Original v1 metrics preserved at: {models_dir / 'test_metrics.txt'}")
    
    return {
        'elapsed_seconds': elapsed_seconds,
        'avg_sec_per_epoch': avg_sec_per_epoch,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'map50': map50,
        'map50_95': map50_95,
        'precision_improvement': (precision - 0.8480) * 100,
        'recall_improvement': (recall - 0.6964) * 100,
        'f1_improvement': (f1_score - 0.7648) * 100,
        'map50_improvement': (map50 - 0.7303) * 100,
        'map50_95_improvement': (map50_95 - 0.3182) * 100
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8s on merged dataset with enhanced augmentation")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs (default: 100)")
    parser.add_argument("--imgsz", type=int, default=512, help="Image resolution size (default: 512)")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (default: 16)")
    parser.add_argument("--patience", type=int, default=10, help="Early stopping patience (default: 10)")
    parser.add_argument("--device", type=str, default=None, help="Device to run on (e.g. '0', 'cpu', 'cuda')")
    args = parser.parse_args()
    
    try:
        results = train_yolo_v2(
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            patience=args.patience,
            device=args.device
        )
        
        if results:
            print("\n" + "=" * 70)
            print("🎉 TRAINING COMPLETE!")
            print("=" * 70)
            print(f"\n📈 Performance Improvements vs V1:")
            print(f"  Precision: {results['precision_improvement']:+.2f}%")
            print(f"  Recall:    {results['recall_improvement']:+.2f}%")
            print(f"  F1 Score:  {results['f1_improvement']:+.2f}%")
            print(f"  mAP@0.50:  {results['map50_improvement']:+.2f}%")
            print()
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
