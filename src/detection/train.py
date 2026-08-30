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

def find_data_yaml(project_root):
    """Dynamically locates data.yaml across current working directory and project root."""
    candidates = [
        project_root / "data" / "data.yaml",
        Path.cwd() / "data" / "data.yaml",
        Path.cwd() / "data.yaml",
        project_root / "data.yaml",
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    # If not found, return target data/data.yaml path
    target = project_root / "data" / "data.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    return target

def setup_data_yaml(data_yaml_path):
    """Rewrites data.yaml with absolute path of the data folder for seamless cross-platform execution."""
    data_dir = data_yaml_path.parent
    yaml_content = (
        f"path: {data_dir.as_posix()}\n"
        "train: train/images\n"
        "val: valid/images\n"
        "test: test/images\n\n"
        "nc: 1\n"
        "names: ['Kidney Stone']\n"
    )
    with open(data_yaml_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    return data_yaml_path

def verify_dataset_images_exist(data_yaml_path):
    """Checks whether train/images contains CT scan images. If missing, automatically downloads via kagglehub."""
    data_dir = data_yaml_path.parent
    train_img_dir = data_dir / "train" / "images"
    images = list(train_img_dir.glob("*.jpg")) + list(train_img_dir.glob("*.png")) + list(train_img_dir.glob("*.jpeg"))
    
    if len(images) == 0:
        print("\n" + "=" * 65)
        print("⚡ AUTO-DOWNLOADING DATASET via kagglehub...")
        print("=" * 65)
        try:
            import kagglehub
            downloaded_path = Path(kagglehub.dataset_download('safurahajiheidari/kidney-stone-images'))
            print(f"Downloaded Kaggle dataset to: {downloaded_path}")
            
            for item in downloaded_path.iterdir():
                dest = data_dir / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            print(f"✅ Successfully auto-extracted dataset into {data_dir}!")
        except Exception as e:
            print(f"⚠️ Automatic dataset download failed: {e}")
            print("Please upload data.zip to Google Colab and run: !unzip -o -q data.zip -d data/")
            raise e

def train_yolo(epochs=10, imgsz=512, batch=16, patience=10, device=None, is_sanity=False):
    """Trains YOLOv8 model for kidney stone detection and evaluates on held-out test set."""
    project_root = Path(__file__).resolve().parent.parent.parent
    
    # Dynamically resolve data.yaml
    data_yaml_path = find_data_yaml(project_root)
    setup_data_yaml(data_yaml_path)
    verify_dataset_images_exist(data_yaml_path)
    
    models_dir = project_root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Auto-detect CUDA GPU if device is not explicitly specified
    if device is None or device == "":
        if torch.cuda.is_available():
            device = "0"
            print("🚀 CUDA GPU Detected! Running training on GPU (device '0').")
        else:
            device = "cpu"
            print("⚠️ WARNING: CUDA GPU not detected. Falling back to CPU.")
            print("   (If running on Google Colab, ensure Runtime -> Change runtime type is set to T4 GPU).")
    elif device == "0" or device == "cuda" or device == "cuda:0":
        if not torch.cuda.is_available():
            print(f"⚠️ WARNING: GPU '{device}' requested but PyTorch CUDA is not available. Falling back to CPU.")
            device = "cpu"
        else:
            device = "0"
            print("🚀 Running training on GPU (device '0').")
        
    print("=" * 65)
    print(f"Starting YOLOv8 {'Sanity Run' if is_sanity else 'Full Training'}")
    print(f"Config: Data={data_yaml_path} | Epochs={epochs} | ImgSize={imgsz} | Batch={batch} | Device={device}")
    print("=" * 65)
    
    # Initialize YOLOv8 Nano model pretrained on COCO
    model = YOLO("yolov8n.pt")
    
    start_time = time.time()
    
    # Run training
    results = model.train(
        data=str(data_yaml_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        patience=patience,
        device=device,
        workers=2,
        project=str(project_root / "runs" / "detect"),
        name="train_run" if not is_sanity else "sanity_run",
        exist_ok=True,
        verbose=True
    )
    
    elapsed_seconds = time.time() - start_time
    avg_sec_per_epoch = elapsed_seconds / epochs if epochs > 0 else 0
    print(f"\nTraining completed in {elapsed_seconds:.2f} seconds ({avg_sec_per_epoch:.2f} sec/epoch)")
    
    # Copy best weights to models/detection_best.pt
    run_dir = project_root / "runs" / "detect" / ("sanity_run" if is_sanity else "train_run")
    best_weights = run_dir / "weights" / "best.pt"
    target_best_weights = models_dir / "detection_best.pt"
    
    if best_weights.exists():
        shutil.copy(best_weights, target_best_weights)
        print(f"Saved best model weights to: {target_best_weights}")
    
    # Held-out Test Set Evaluation
    print("\n" + "=" * 65)
    print("RUNNING HELD-OUT TEST SET EVALUATION (split='test')...")
    print("=" * 65)
    
    # Load best trained model for evaluation
    best_model = YOLO(str(target_best_weights if target_best_weights.exists() else best_weights))
    test_metrics = best_model.val(data=str(data_yaml_path), split="test", imgsz=imgsz, device=device)
    
    precision = float(test_metrics.box.mp)
    recall = float(test_metrics.box.mr)
    map50 = float(test_metrics.box.map50)
    map50_95 = float(test_metrics.box.map)
    
    metrics_summary = (
        "=====================================================\n"
        "RENALSCAN YOLOv8 DETECTION — HELD-OUT TEST METRICS\n"
        "=====================================================\n"
        f"Evaluation Split : Held-Out Test Set (data/test)\n"
        f"Image Resolution : {imgsz}x{imgsz} px\n"
        f"Total Epochs     : {epochs}\n"
        f"Device Used      : {device}\n"
        f"Training Time    : {elapsed_seconds:.2f} sec ({avg_sec_per_epoch:.2f} s/epoch)\n"
        "-----------------------------------------------------\n"
        f"Precision (P)    : {precision:.4f} ({precision * 100:.2f}%)\n"
        f"Recall (R)       : {recall:.4f} ({recall * 100:.2f}%)\n"
        f"mAP@0.50         : {map50:.4f} ({map50 * 100:.2f}%)\n"
        f"mAP@0.50:0.95    : {map50_95:.4f} ({map50_95 * 100:.2f}%)\n"
        "=====================================================\n"
    )
    
    print("\n" + metrics_summary)
    
    metrics_file = models_dir / "test_metrics.txt"
    with open(metrics_file, "w", encoding="utf-8") as f:
        f.write(metrics_summary)
    print(f"Saved test set evaluation metrics to: {metrics_file}")
    
    return {
        'elapsed_seconds': elapsed_seconds,
        'avg_sec_per_epoch': avg_sec_per_epoch,
        'precision': precision,
        'recall': recall,
        'map50': map50,
        'map50_95': map50_95
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8 on RenalScan dataset")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=512, help="Image resolution size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--patience", type=int, default=10, help="Early stopping patience")
    parser.add_argument("--device", type=str, default=None, help="Device to run on (e.g. '0', 'cpu', 'cuda')")
    parser.add_argument("--sanity", action="store_true", help="Flag for fast sanity run")
    args = parser.parse_args()
    
    train_yolo(
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=args.patience,
        device=args.device,
        is_sanity=args.sanity
    )
