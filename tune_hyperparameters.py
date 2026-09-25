"""
RenalScan — Phase A, Step 1: Hyperparameter Tuning Script
Systematic hyperparameter search using Ultralytics Genetic Algorithm (model.tune)
for YOLOv8s on the merged 3,305-image dataset (data_merged/).
"""

import argparse
import os
import sys
import time
from pathlib import Path
import yaml
import torch

from ultralytics import YOLO, settings


def run_hyperparameter_tuning(
    data_yaml="data_merged/data.yaml",
    epochs=15,
    iterations=12,
    batch=16,
    imgsz=512,
    device=None,
    model_name="yolov8s.pt"
):
    project_root = Path(__file__).resolve().parent
    data_yaml_path = project_root / data_yaml
    settings.update({"datasets_dir": str(project_root)})

    if not data_yaml_path.exists():
        raise FileNotFoundError(
            f"Dataset configuration not found at: {data_yaml_path}. "
            "Please ensure data_merged.zip is extracted."
        )

    # Determine Device
    if device is None or device == "":
        device = "0" if torch.cuda.is_available() else "cpu"

    print("=" * 75)
    print("RENALSCAN — PHASE A, STEP 1: HYPERPARAMETER TUNING (YOLOv8s)")
    print("=" * 75)
    print(f"Base Architecture : {model_name}")
    print(f"Dataset Config    : {data_yaml_path}")
    print(f"Image Resolution  : {imgsz}x{imgsz}")
    print(f"Batch Size        : {batch}")
    print(f"Trial Epochs      : {epochs} epochs per trial")
    print(f"Tuning Iterations : {iterations} genetic mutation iterations")
    print(f"Target Hardware   : Device '{device}'")
    print(f"Search Scope      : lr0, lrf, momentum, weight_decay, augmentations")
    print("=" * 75)
    print()

    # Time Estimation
    est_sec_per_epoch = 55.0  # Approx 50-60s on Nvidia T4 GPU
    est_total_minutes = (epochs * iterations * est_sec_per_epoch) / 60.0
    est_total_hours = est_total_minutes / 60.0
    print(f"⏱️ Estimated Search Duration: ~{est_total_minutes:.1f} minutes ({est_total_hours:.2f} GPU-hours) on T4 GPU.")
    print("=" * 75)
    print()

    start_time = time.time()
    model = YOLO(model_name)

    print("Starting Ultralytics genetic hyperparameter tuning search...")
    print("Results and fitness will be logged per iteration to runs/detect/tune/")
    print()

    tune_results = model.tune(
        data=str(data_yaml_path),
        epochs=epochs,
        iterations=iterations,
        batch=batch,
        imgsz=imgsz,
        device=device,
        plots=True,
        save=True,
        val=True
    )

    elapsed_time = time.time() - start_time
    print()
    print("=" * 75)
    print(f"✅ HYPERPARAMETER SEARCH COMPLETED in {elapsed_time/60.0:.2f} minutes")
    print("=" * 75)

    # Locate and print best hyperparameters
    tune_dir = project_root / "runs" / "detect" / "tune"
    best_hyp_yaml = tune_dir / "best_hyperparameters.yaml"
    tune_csv = tune_dir / "tune_fitness.csv"

    if best_hyp_yaml.exists():
        with open(best_hyp_yaml, "r") as f:
            best_hyp = yaml.safe_load(f)

        print("\n🏆 OPTIMAL HYPERPARAMETERS DISCOVERED (Step 1 Complete):")
        print("-" * 55)
        for k, v in best_hyp.items():
            print(f"  {k:<20}: {v}")
        print("-" * 55)

        # Save summary to models directory
        models_dir = project_root / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        summary_path = models_dir / "tuning_summary.txt"

        with open(summary_path, "w") as sf:
            sf.write("RENALSCAN HYPERPARAMETER TUNING SUMMARY (PHASE A, STEP 1)\n")
            sf.write("=" * 60 + "\n")
            sf.write(f"Timestamp        : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            sf.write(f"Search Duration  : {elapsed_time/60.0:.2f} minutes\n")
            sf.write(f"Trials           : {iterations} iterations x {epochs} epochs\n")
            sf.write(f"Best Config Path : {best_hyp_yaml}\n")
            sf.write("=" * 60 + "\n\n")
            sf.write("BEST HYPERPARAMETERS:\n")
            sf.write(yaml.dump(best_hyp, default_flow_style=False))

        print(f"\n📄 Tuning summary saved to: {summary_path}")
        print("🛑 STOP: Inspect the best hyperparameters above before triggering full training (Step 2).")

    return tune_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RenalScan YOLOv8s Hyperparameter Tuning")
    parser.add_argument("--data", type=str, default="data_merged/data.yaml", help="Path to data.yaml")
    parser.add_argument("--epochs", type=int, default=15, help="Epochs per tuning trial (default: 15)")
    parser.add_argument("--iterations", type=int, default=12, help="Number of genetic search iterations (default: 12)")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (default: 16)")
    parser.add_argument("--imgsz", type=int, default=512, help="Image resolution (default: 512)")
    parser.add_argument("--device", type=str, default=None, help="Device (e.g. '0' or 'cpu')")
    parser.add_argument("--model", type=str, default="yolov8s.pt", help="Base model weights")

    args = parser.parse_args()
    run_hyperparameter_tuning(
        data_yaml=args.data,
        epochs=args.epochs,
        iterations=args.iterations,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        model_name=args.model
    )
