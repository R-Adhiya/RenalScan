# RenalScan: AI-Powered Kidney Stone Detection & Measurement

RenalScan is a portfolio project focused on automated kidney stone detection, region segmentation, and dimension estimation using Non-Contrast Computed Tomography (NCCT) images.

---

## 📁 Repository Structure

```
renalscan/
├── data/                  # CT Image dataset (train/valid/test splits & YOLO labels) - Gitignored
├── notebooks/             # Data exploration & validation Jupyter notebooks
├── src/                   # Core modular Python package
│   ├── detection/         # YOLO object detection training & inference modules
│   ├── segmentation/      # Classical CV thresholding & contour extraction modules
│   ├── measurement/       # Bounding box & contour metric calculation modules
│   └── pipeline/          # End-to-end inference pipeline integration
├── models/                # Trained YOLO model weights (.pt) - Gitignored
├── app/                   # Web application interface for model deployment
├── tests/                 # Unit and pipeline tests
├── README.md              # Project documentation & setup instructions
├── .gitignore             # Git exclusion rules for data, models, and virtual environments
└── requirements.txt       # Pinned Python package dependencies
```

---

## ⚠️ Known Project Limitations

1. **Lack of Pixel-Spacing Metadata (Plain JPG CT Images)**:
   - The CT scans in this dataset are standard JPG files without DICOM metadata tags (such as `PixelSpacing` $(mm/pixel)$ or `SliceThickness`).
   - Consequently, size and area measurements derived during the measurement module are **approximate pixel-space metrics** rather than clinically precise millimeter measurements.

2. **Absence of Segmentation Masks**:
   - The dataset provides bounding box annotations (`.txt` in YOLO format) for object detection.
   - Ground-truth segmentation masks are not included. Segmentation in this project uses **classical Computer Vision techniques** (Otsu thresholding, morphological operations, and contour analysis) applied within detected bounding box regions, rather than a supervised deep learning segmentation network (e.g., U-Net or Mask R-CNN).

3. **Resizing CT Images to 512x512**:
   - Images are resized from their original resolution (640x640) to 512x512 pixels to optimize CPU training and inference speed.
   - This trade-off significantly speeds up training while maintaining strong overall detection accuracy for kidney stones, though exceptionally small stones may experience a minor drop in sensitivity.

---

## 📦 Dataset Download & Setup

Dataset Source: [Kaggle Kidney Stone Images Dataset](https://www.kaggle.com/datasets/safurahajiheidari/kidney-stone-images)

### Download Instructions:
1. **Via Kaggle CLI**:
   ```bash
   kaggle datasets download -d safurahajiheidari/kidney-stone-images --unzip -p data/
   ```
2. **Via Web Browser**:
   - Download the `.zip` archive directly from Kaggle.
   - Extract the contents into the `data/` directory.

### Directory Organization:
Ensure your dataset is organized under `data/` as follows:
```
data/
├── data.yaml
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

---

## 🚀 Environment Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   ```
2. **Activate Virtual Environment**:
   - Windows PowerShell:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Linux / macOS:
     ```bash
     source .venv/bin/activate
     ```
3. **Install Pinned Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Verify Imports**:
   ```bash
   python -c "import torch; import cv2; from ultralytics import YOLO; print('Imports Successful!')"
   ```
