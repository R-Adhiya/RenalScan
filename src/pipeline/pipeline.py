import os
import cv2
import numpy as np
from pathlib import Path

from src.detection.predict import StoneDetector
from src.segmentation.segment import StoneSegmenter
from src.measurement.measure import StoneMeasurer, ASSUMED_MM_PER_PIXEL, NON_CLINICAL_DISCLAIMER

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
            
        self.detector = StoneDetector(model_path=model_path)
        self.segmenter = StoneSegmenter(padding_pct=padding_pct)
        self.measurer = StoneMeasurer(mm_per_pixel=mm_per_pixel)
        self.mm_per_pixel = mm_per_pixel

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
        # Load & normalize image input to RGB numpy array
        if isinstance(image_input, (str, Path)):
            bgr_img = cv2.imread(str(image_input))
            if bgr_img is None:
                raise FileNotFoundError(f"Could not read image from path: {image_input}")
            rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        elif isinstance(image_input, np.ndarray):
            if len(image_input.shape) == 2:
                rgb_img = cv2.cvtColor(image_input, cv2.COLOR_GRAY2RGB)
            elif image_input.shape[2] == 3:
                rgb_img = image_input.copy()
            else:
                rgb_img = image_input.copy()
        else:
            raise ValueError("image_input must be a filepath string, Path, or numpy array.")
            
        # 1. RUN DETECTION (YOLOv8)
        # Default conf_thresh = 0.40 to filter out low-confidence false positives
        annotated_det_bgr, detections = self.detector.predict(rgb_img, conf_thresh=conf_thresh)
        annotated_det_rgb = cv2.cvtColor(annotated_det_bgr, cv2.COLOR_BGR2RGB)
        
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
        seg_results = self.segmenter.segment_image_detections(rgb_img, detections)
        
        # 3. RUN MEASUREMENT (Geometric Contour Axis Analysis)
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
