"""
Enhanced YOLOv8s Training on Merged Dataset (v2)

Training Configuration:
- Model: YOLOv8s (upgraded from YOLOv8n for better capacity)
- Dataset: data_merged/ (3,305 images)
- Enhanced augmentation for improved recall
- Early stopping with patience=10
- Results saved to models/test_metrics_v2.txt
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
    data_yaml='data_merged/data.y