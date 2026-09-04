"""
Comprehensive Model Evaluation Script for RenalScan YOLOv8
Generates detailed metrics on the test dataset.
"""
import os
import time
from pathlib import Path
from ultralytics import YOLO
import torch

def evaluate_model():
    """Run comprehensive evaluation on test set and display all metrics."""
    
    print("=" * 70)
    print("RENALSCAN YOLOV8 MODEL EVALUATION")
    print("=" * 70)
    
    # Check if model exists
    model_path = Path("models/detection_best.pt")
    if not model_path.exists():
        print(f"❌ ERROR: Model not found at {model_path}")
        print("Please train the model first using: python src/detection/train.py")
        return
    
    print(f"\n📦 Loading model from: {model_path}")
    model = YOLO(str(model_path))
    print("✅ Model loaded successfully")
    
    # Check dataset
    data_yaml = Path("data/data.yaml")
    if not data_yaml.exists():
        print(f"❌ ERROR: Dataset configuration not found at {data_yaml}")
        return
    
    print(f"📊 Dataset configuration: {data_yaml}")
    
    # Device detection
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"🖥️  Device: {device.upper()}")
    
    print("\n" + "=" * 70)
    print("RUNNING EVALUATION ON TEST SET...")
    print("=" * 70)
    
    start_time = time.time()
    
    # Run validation on test split
    metrics = model.val(
        data=str(data_yaml),
        split='test',
        imgsz=512,
        device=device,
        verbose=True
    )
    
    elapsed = time.time() - start_time
    
    # Extract metrics
    box_metrics = metrics.box
    precision = float(box_metrics.mp)  # mean precision
    recall = float(box_metrics.mr)     # mean recall
    map50 = float(box_metrics.map50)   # mAP@0.5
    map50_95 = float(box_metrics.map)  # mAP@0.5:0.95
    
    # Additional metrics
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print("\n" + "=" * 70)
    print("📊 EVALUATION RESULTS")
    print("=" * 70)
    print(f"\n{'Metric':<25} {'Value':<15} {'Percentage'}")
    print("-" * 70)
    print(f"{'Precision (P)':<25} {precision:.4f}{'':<10} {precision * 100:.2f}%")
    print(f"{'Recall (R)':<25} {recall:.4f}{'':<10} {recall * 100:.2f}%")
    print(f"{'F1 Score':<25} {f1_score:.4f}{'':<10} {f1_score * 100:.2f}%")
    print(f"{'mAP@0.50':<25} {map50:.4f}{'':<10} {map50 * 100:.2f}%")
    print(f"{'mAP@0.50:0.95':<25} {map50_95:.4f}{'':<10} {map50_95 * 100:.2f}%")
    print("-" * 70)
    print(f"{'Evaluation Time':<25} {elapsed:.2f} seconds")
    print("=" * 70)
    
    # Interpretation
    print("\n" + "=" * 70)
    print("📋 METRICS INTERPRETATION")
    print("=" * 70)
    print(f"""
• Precision ({precision * 100:.2f}%): Of all predicted kidney stones, {precision * 100:.1f}% were correct
  {'✅ Good - Low false positive rate' if precision > 0.8 else '⚠️  Consider tuning confidence threshold'}

• Recall ({recall * 100:.2f}%): The model detected {recall * 100:.1f}% of all actual kidney stones
  {'✅ Good - Most stones detected' if recall > 0.8 else '⚠️  Some stones may be missed'}

• F1 Score ({f1_score * 100:.2f}%): Balanced measure of precision and recall
  {'✅ Strong overall performance' if f1_score > 0.75 else '⚠️  Room for improvement'}

• mAP@0.50 ({map50 * 100:.2f}%): Detection accuracy at 50% IoU threshold
  {'✅ Excellent detection quality' if map50 > 0.8 else '✅ Good detection quality' if map50 > 0.7 else '⚠️  Consider additional training'}

• mAP@0.50:0.95 ({map50_95 * 100:.2f}%): Average precision across IoU thresholds (0.5 to 0.95)
  {'✅ Precise bounding boxes' if map50_95 > 0.5 else '⚠️  Bounding box localization could improve'}
    """)
    print("=" * 70)
    
    # Save detailed report
    report_path = Path("models/evaluation_report.txt")
    with open(report_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("RENALSCAN YOLOV8 MODEL - COMPREHENSIVE EVALUATION REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Model Path: {model_path}\n")
        f.write(f"Dataset: {data_yaml}\n")
        f.write(f"Test Split: data/test\n")
        f.write(f"Image Size: 512x512 pixels\n")
        f.write(f"Device: {device}\n")
        f.write(f"Evaluation Time: {elapsed:.2f} seconds\n\n")
        f.write("-" * 70 + "\n")
        f.write("METRICS SUMMARY\n")
        f.write("-" * 70 + "\n")
        f.write(f"Precision:        {precision:.4f} ({precision * 100:.2f}%)\n")
        f.write(f"Recall:           {recall:.4f} ({recall * 100:.2f}%)\n")
        f.write(f"F1 Score:         {f1_score:.4f} ({f1_score * 100:.2f}%)\n")
        f.write(f"mAP@0.50:         {map50:.4f} ({map50 * 100:.2f}%)\n")
        f.write(f"mAP@0.50:0.95:    {map50_95:.4f} ({map50_95 * 100:.2f}%)\n")
        f.write("=" * 70 + "\n")
    
    print(f"\n💾 Detailed report saved to: {report_path}")
    print("\n✅ Evaluation complete!")
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'map50': map50,
        'map50_95': map50_95,
        'elapsed_time': elapsed
    }

if __name__ == "__main__":
    try:
        evaluate_model()
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluation interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR during evaluation: {e}")
        import traceback
        traceback.print_exc()
