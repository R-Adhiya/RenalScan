import os
import cv2
import time
import logging
import numpy as np
from pathlib import Path

from src.detection.predict import StoneDetector
from src.segmentation.segment import StoneSegmenter
from src.measurement.measure import StoneMeasurer, ASSUMED_MM_PER_PIXEL, NON_CLINICAL_DISCLAIMER

# Initialize standard pipeline logger
logger = logging.getLogger("renalscan.pipeline")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class RenalScanPipeline:
    """End-to-End Diagnostic Pipeline chaining Detection -> Segmentation -> Physical Measurement."""
    
    def __init__(self, model_path=None, padding_pct=0.10, mm_per_pixel=ASSUMED_MM_PER_PIXEL):
        """
        Args:
            model_path (str | Path, optional): Path to trained YOLOv8 model weights (.pt).
            padding_pct (float): Fractional padding margin around bounding box crops (default: 0.10).
            mm_per_pixel (float): Literature-based pixel-to-mm conversion factor (default: 0.70).
        """
        project_root = Path(__file__).resolve().parent.parent.parent
        if model_path is None:
            model_path = project_root / "models" / "detection_best.pt"
            
        logger.info("Initializing RenalScanPipeline with weights: %s", model_path)
        self.detector = StoneDetector(model_path=model_path)
        self.segmenter = StoneSegmenter(padding_pct=padding_pct)
        self.measurer = StoneMeasurer(mm_per_pixel=mm_per_pixel)
        self.mm_per_pixel = mm_per_pixel
        logger.info("Pipeline components initialized successfully (mm_per_pixel=%.2f)", mm_per_pixel)

    def analyze(self, image_input, conf_thresh=0.40):
        """Runs the complete Detection -> Segmentation -> Measurement pipeline on a CT image.
        
        Args:
            image_input (str | Path | np.ndarray): Filepath string, Path object, or numpy array.
            conf_thresh (float): Minimum confidence threshold for YOLOv8 detections (default: 0.40).
                                 Detections below this threshold are filtered out.
            
        Returns:
            dict: Structured diagnostic result dictionary containing:
                - 'original_image': np.ndarray (RGB),
                - 'annotated_detection': np.ndarray (RGB image with YOLO bounding boxes),
                - 'annotated_segmentation': np.ndarray (RGB image with cyan/red mask overlays),
                - 'annotated_measurement': np.ndarray (RGB image with cyan/yellow axis vectors),
                - 'stones': list of stone dicts (box, mask, measurements, confidence),
                - 'summary': dict (stone_count, largest_stone_mm, largest_stone_band, has_stones, status_message)
        """
        t_start = time.perf_counter()
        logger.info("Beginning pipeline analysis (conf_thresh=%.2f)...", conf_thresh)
        
        # --- INPUT VALIDATION & NORMALIZATION ---
        if image_input is None:
            logger.error("image_input is None.")
            raise ValueError("Invalid input: image_input cannot be None.")

        if isinstance(image_input, (str, Path)):
            p = Path(image_input)
            if not p.exists():
                logger.error("Image file does not exist: %s", image_input)
                raise FileNotFoundError(f"Image file not found: {image_input}")
            bgr_img = cv2.imread(str(p))
            if bgr_img is None:
                logger.error("Failed to decode image file: %s (file may be corrupted or non-image format)", image_input)
                raise ValueError(f"Could not decode image from '{image_input}'. Please check file integrity.")
            rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        elif isinstance(image_input, np.ndarray):
            if image_input.size == 0 or len(image_input.shape) < 2:
                logger.error("Input numpy array is empty or has invalid shape: %s", getattr(image_input, "shape", None))
                raise ValueError(f"Input image array is empty or has invalid dimensions: shape={getattr(image_input, 'shape', None)}")
                
            # Convert float arrays [0.0, 1.0] to uint8 [0, 255] safely
            if np.issubdtype(image_input.dtype, np.floating):
                logger.info("Converting floating point image array to uint8 [0, 255]")
                if image_input.max() <= 1.0:
                    arr = (np.clip(image_input, 0.0, 1.0) * 255.0).astype(np.uint8)
                else:
                    arr = np.clip(image_input, 0.0, 255.0).astype(np.uint8)
            else:
                arr = image_input.astype(np.uint8)
                
            # Channel normalization
            if len(arr.shape) == 2:
                # 2D grayscale -> RGB
                rgb_img = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
            elif len(arr.shape) == 3:
                c = arr.shape[2]
                if c == 1:
                    rgb_img = cv2.cvtColor(arr[:, :, 0], cv2.COLOR_GRAY2RGB)
                elif c == 3:
                    rgb_img = arr.copy()
                elif c == 4:
                    logger.info("Input has 4 channels (RGBA) — converting to standard 3-channel RGB")
                    rgb_img = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
                else:
                    logger.warning("Input array has %d channels — taking first 3 channels", c)
                    rgb_img = arr[:, :, :3].copy()
            else:
                logger.error("Unsupported array shape: %s", image_input.shape)
                raise ValueError(f"Unsupported image array dimensions: {image_input.shape}")
        else:
            logger.error("Unsupported image_input type: %s", type(image_input).__name__)
            raise TypeError(f"image_input must be a filepath string, Path, or numpy ndarray, got {type(image_input).__name__}")

        # Guard against extreme small dimensions (< 32px)
        h, w = rgb_img.shape[:2]
        if h < 32 or w < 32:
            logger.warning("Input image dimensions (%dx%d) are extremely small. Upscaling to 32x32 for safe pipeline execution.", w, h)
            rgb_img = cv2.resize(rgb_img, (max(32, w), max(32, h)), interpolation=cv2.INTER_NEAREST)

        logger.info("Normalized image ready for analysis: shape=%s, dtype=%s", rgb_img.shape, rgb_img.dtype)

        # 1. RUN DETECTION (YOLOv8)
        logger.info("[Stage 1/3] Detection: Running YOLOv8 stone detector (conf_thresh=%.2f)...", conf_thresh)
        annotated_det_bgr, detections = self.detector.predict(rgb_img, conf_thresh=conf_thresh)
        annotated_det_rgb = cv2.cvtColor(annotated_det_bgr, cv2.COLOR_BGR2RGB)
        logger.info("[Stage 1/3] Detection complete: %d candidate stone bounding box(es) found.", len(detections))
        
        # EDGE CASE 1: No stones detected
        if len(detections) == 0:
            return {
                'original_image': rgb_img,
                'annotated_detection': annotated_det_rgb,
                'annotated_segmentation': rgb_img.copy(),
                'annotated_measurement': rgb_img.copy(),
                'stones': [],
                'summary': {
                    'stone_count': 0,
                    'has_stones': False,
                    'largest_stone_diameter_mm': 0.0,
                    'largest_stone_size_band': "No Stones Detected",
                    'status_message': "No kidney stones detected in this CT scan.",
                    'disclaimer': NON_CLINICAL_DISCLAIMER
                }
            }
            
        # 2. RUN SEGMENTATION (Classical CV Otsu ROI)
        logger.info("[Stage 2/3] Segmentation: Running padded ROI Otsu segmentation on %d detection(s)...", len(detections))
        seg_results = self.segmenter.segment_image_detections(rgb_img, detections)
        logger.info("[Stage 2/3] Segmentation complete: %d contour mask(s) extracted.", len(seg_results))
        
        # 3. RUN MEASUREMENT (Geometric Contour Axis Analysis)
        logger.info("[Stage 3/3] Measurement: Computing physical dimensions and clinical size bands (assumed mm/px=%.2f)...", self.mm_per_pixel)
        measured_results = self.measurer.measure_segmentation_results(seg_results)
        
        # Render Segmentation & Measurement Visual Overlays
        annotated_seg_rgb = rgb_img.copy()
        annotated_meas_rgb = rgb_img.copy()
        
        stones = []
        valid_count = 0
        largest_mm = 0.0
        largest_band = "N/A"
        
        for idx, m in enumerate(measured_results):
            # EDGE CASE 2: Bounding box where segmentation found no bright contour
            if m.get('area_px', 0) <= 0:
                logger.warning("Stone candidate #%d: Segmentation produced 0 area contour. Marking as failed segmentation.", idx + 1)
                stone_info = {
                    'stone_id': idx + 1,
                    'box_xyxy': [round(v, 1) for v in m['box_xyxy']],
                    'confidence': round(m['confidence'], 4),
                    'status': 'Segmentation Failed (No bright ROI contour)',
                    'area_px': 0.0,
                    'major_axis_px': 0.0,
                    'minor_axis_px': 0.0,
                    'estimated_diameter_mm': 0.0,
                    'clinical_size_band': 'N/A'
                }
                stones.append(stone_info)
                continue
                
            valid_count += 1
            mask = m['full_mask']
            
            # Red fill for mask overlay
            red_fill = np.zeros_like(rgb_img)
            red_fill[mask > 0] = [255, 0, 0]
            annotated_seg_rgb = cv2.addWeighted(annotated_seg_rgb, 1.0, red_fill, 0.4, 0)
            
            # Cyan contour boundary
            if m['contour_global'] is not None:
                cv2.drawContours(annotated_seg_rgb, [m['contour_global']], -1, (0, 255, 255), 2)
                
            # Measurement axis lines
            annotated_meas_rgb = self.measurer.draw_measurement_overlay(annotated_meas_rgb, m, draw_text=True)
            
            est_mm = m['estimated_diameter_mm']
            if est_mm > largest_mm:
                largest_mm = est_mm
                largest_band = m['clinical_size_band']
                
            stone_info = {
                'stone_id': idx + 1,
                'box_xyxy': [round(v, 1) for v in m['box_xyxy']],
                'confidence': round(m['confidence'], 4),
                'status': 'Success',
                'full_mask': mask,
                'crop_mask': m['crop_mask'],
                'area_px': m['area_px'],
                'equiv_diameter_px': m['equiv_diameter_px'],
                'major_axis_px': m['major_axis_px'],
                'minor_axis_px': m['minor_axis_px'],
                'aspect_ratio': m['aspect_ratio'],
                'estimated_major_mm': m['estimated_major_mm'],
                'estimated_minor_mm': m['estimated_minor_mm'],
                'estimated_diameter_mm': est_mm,
                'clinical_size_band': m['clinical_size_band'],
                'disclaimer': NON_CLINICAL_DISCLAIMER
            }
            stones.append(stone_info)
            logger.debug("Stone #%d measured: %.2f mm (%s, conf=%.2f)", idx + 1, est_mm, m['clinical_size_band'], m['confidence'])
            
        t_elapsed = time.perf_counter() - t_start
        logger.info("[Stage 3/3] Measurement complete: %d/%d valid stones quantified (largest: %.2f mm, band: %s) in %.3fs.",
                    valid_count, len(stones), largest_mm, largest_band, t_elapsed)
        
        summary = {
            'stone_count': len(stones),
            'valid_segmented_stones': valid_count,
            'has_stones': len(stones) > 0,
            'largest_stone_diameter_mm': round(largest_mm, 2),
            'largest_stone_size_band': largest_band,
            'status_message': f"Detected {len(stones)} stone(s) in CT scan.",
            'disclaimer': NON_CLINICAL_DISCLAIMER
        }
        
        return {
            'original_image': rgb_img,
            'annotated_detection': annotated_det_rgb,
            'annotated_segmentation': annotated_seg_rgb,
            'annotated_measurement': annotated_meas_rgb,
            'stones': stones,
            'summary': summary
        }

def analyze_ct_scan(image_input, conf_thresh=0.40):
    """Utility function to analyze a single CT scan image."""
    pipeline = RenalScanPipeline()
    return pipeline.analyze(image_input, conf_thresh=conf_thresh)
