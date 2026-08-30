import math
import cv2
import numpy as np

# Literature-based abdominal CT pixel spacing constant
# Standard abdominal CT scans typically cover a Field of View (FOV) of ~350-400mm across a 512x512 matrix.
# FOV 360mm / 512px = 0.703 mm/pixel. We adopt 0.70 mm/px as a reasonable literature-based baseline constant.
ASSUMED_MM_PER_PIXEL = 0.70
NON_CLINICAL_DISCLAIMER = "Estimated, non-clinical value (assumed 0.70 mm/px). Not for diagnostic or surgical decisions."

def classify_stone_size_band(diameter_mm):
    """Classifies estimated stone diameter (mm) into standard clinical urological treatment bands.
    
    Bands:
    - < 4mm: Small (High spontaneous passage likelihood ~80%)
    - 4 - 6mm: Medium (Moderate passage likelihood ~50%, conservative management / MET)
    - 6 - 10mm: Large (Low spontaneous passage likelihood ~20%, intervention often required)
    - > 10mm: Very Large (Surgical intervention indicated — ESWL / URS / PCNL)
    """
    if diameter_mm < 4.0:
        return "<4mm (Small - High passage likelihood)"
    elif 4.0 <= diameter_mm < 6.0:
        return "4-6mm (Medium - Moderate passage likelihood)"
    elif 6.0 <= diameter_mm <= 10.0:
        return "6-10mm (Large - Low passage likelihood)"
    else:
        return ">10mm (Very Large - Surgical intervention indicated)"

class StoneMeasurer:
    """Quantitative Physical Dimension Measurement Engine for Segmented Kidney Stones."""
    
    def __init__(self, mm_per_pixel=ASSUMED_MM_PER_PIXEL):
        """
        Args:
            mm_per_pixel (float): Literature-based approximate pixel-to-mm conversion factor.
        """
        self.mm_per_pixel = mm_per_pixel

    def measure_contour(self, contour):
        """Calculates geometric pixel measurements and estimated mm dimensions from a stone contour.
        
        Args:
            contour (np.ndarray): OpenCV contour points array.
            
        Returns:
            dict: {
                'area_px': float total mask pixel area (px²),
                'equiv_diameter_px': float equivalent circular diameter (px),
                'major_axis_px': float longest diameter in pixels (px),
                'minor_axis_px': float shortest orthogonal diameter in pixels (px),
                'aspect_ratio': float major / minor axis ratio,
                'estimated_major_mm': float estimated major axis (mm, non-clinical),
                'estimated_minor_mm': float estimated minor axis (mm, non-clinical),
                'estimated_diameter_mm': float estimated equivalent diameter (mm, non-clinical),
                'clinical_size_band': str urological size band classification,
                'disclaimer': str non-clinical estimation disclaimer,
                'centroid_xy': (xc, yc) center coordinates,
                'major_axis_line': ((x1, y1), (x2, y2)),
                'minor_axis_line': ((x1, y1), (x2, y2))
            }
        """
        if contour is None or len(contour) == 0:
            return self._empty_measurement()

        # 1. Area & Centroid Calculation
        area_px = float(cv2.contourArea(contour))
        if area_px <= 0:
            return self._empty_measurement()

        M = cv2.moments(contour)
        if M["m00"] != 0:
            xc = int(M["m10"] / M["m00"])
            yc = int(M["m01"] / M["m00"])
        else:
            xc, yc = 0, 0
            
        # 2. Equivalent Circular Diameter: d = 2 * sqrt(Area / pi)
        equiv_diameter_px = float(2.0 * math.sqrt(area_px / math.pi))

        # 3. Minimum Area Rotated Bounding Rectangle & Fitted Ellipse
        rect = cv2.minAreaRect(contour)
        (center_x, center_y), (dim_w, dim_h), angle = rect
        
        d1, d2 = dim_w, dim_h
        major_axis_px = max(d1, d2)
        minor_axis_px = min(d1, d2)
        
        # Fallback to fitted ellipse if contour has >= 5 points for smoother axis estimation
        if len(contour) >= 5:
            try:
                (ellipse_center, (ellipse_d1, ellipse_d2), ellipse_angle) = cv2.fitEllipse(contour)
                major_axis_px = max(ellipse_d1, ellipse_d2)
                minor_axis_px = min(ellipse_d1, ellipse_d2)
                angle = ellipse_angle if ellipse_d1 < ellipse_d2 else ellipse_angle + 90
            except Exception:
                pass
                
        aspect_ratio = float(major_axis_px / minor_axis_px) if minor_axis_px > 0 else 1.0

        # 4. Approximate mm Conversions & Clinical Size Banding
        # ESTIMATED, NON-CLINICAL VALUES (assumed FOV constant = 0.70 mm/px)
        est_major_mm = major_axis_px * self.mm_per_pixel
        est_minor_mm = minor_axis_px * self.mm_per_pixel
        est_diameter_mm = equiv_diameter_px * self.mm_per_pixel
        size_band = classify_stone_size_band(est_diameter_mm)

        # 5. Calculate Endpoints for Major and Minor Axis Line Visualizations
        rad_maj = math.radians(angle)
        rad_min = math.radians(angle + 90)
        
        half_maj = major_axis_px / 2.0
        half_min = minor_axis_px / 2.0
        
        maj_p1 = (int(xc - half_maj * math.cos(rad_maj)), int(yc - half_maj * math.sin(rad_maj)))
        maj_p2 = (int(xc + half_maj * math.cos(rad_maj)), int(yc + half_maj * math.sin(rad_maj)))
        
        min_p1 = (int(xc - half_min * math.cos(rad_min)), int(yc - half_min * math.sin(rad_min)))
        min_p2 = (int(xc + half_min * math.cos(rad_min)), int(yc + half_min * math.sin(rad_min)))

        return {
            'area_px': round(area_px, 2),
            'equiv_diameter_px': round(equiv_diameter_px, 2),
            'major_axis_px': round(major_axis_px, 2),
            'minor_axis_px': round(minor_axis_px, 2),
            'aspect_ratio': round(aspect_ratio, 2),
            'estimated_major_mm': round(est_major_mm, 2),
            'estimated_minor_mm': round(est_minor_mm, 2),
            'estimated_diameter_mm': round(est_diameter_mm, 2),
            'clinical_size_band': size_band,
            'disclaimer': NON_CLINICAL_DISCLAIMER,
            'centroid_xy': (xc, yc),
            'major_axis_line': (maj_p1, maj_p2),
            'minor_axis_line': (min_p1, min_p2)
        }

    def measure_segmentation_results(self, seg_results):
        """Measures dimensions for a list of segmentation result dicts.
        
        Args:
            seg_results (list[dict]): Segmentation output from StoneSegmenter.segment_image_detections().
            
        Returns:
            list[dict]: List of combined segmentation + measurement dicts.
        """
        measured_results = []
        for seg in seg_results:
            cnt = seg.get('contour_global')
            measurements = self.measure_contour(cnt)
            combined = {**seg, **measurements}
            measured_results.append(combined)
        return measured_results

    def draw_measurement_overlay(self, image, measurements, draw_text=True):
        """Draws Major Axis (Cyan) and Minor Axis (Yellow) lines and estimated mm labels on CT image.
        
        Args:
            image (np.ndarray): Input CT image array (RGB or BGR).
            measurements (dict): Measurement dictionary from measure_contour().
            draw_text (bool): Whether to annotate text labels.
            
        Returns:
            np.ndarray: Image array with measurement lines drawn.
        """
        annotated = image.copy()
        if measurements is None or measurements.get('area_px', 0) <= 0:
            return annotated
            
        maj_p1, maj_p2 = measurements['major_axis_line']
        min_p1, min_p2 = measurements['minor_axis_line']
        xc, yc = measurements['centroid_xy']
        
        # Cyan line for Major Axis
        cv2.line(annotated, maj_p1, maj_p2, (0, 255, 255), 2, cv2.LINE_AA)
        
        # Yellow line for Minor Axis
        cv2.line(annotated, min_p1, min_p2, (255, 255, 0), 2, cv2.LINE_AA)
        
        # Red dot for Centroid
        cv2.circle(annotated, (xc, yc), 3, (255, 0, 0), -1)
        
        if draw_text:
            maj_px = measurements['major_axis_px']
            min_px = measurements['minor_axis_px']
            est_mm = measurements['estimated_diameter_mm']
            band = measurements['clinical_size_band'].split(' ')[0] # Short band string
            
            label_line1 = f"Maj: {maj_px}px | Min: {min_px}px"
            label_line2 = f"Est: {est_mm}mm* [{band}] (*Non-Clinical)"
            
            cv2.putText(annotated, label_line1, (max(5, xc - 70), max(15, yc - 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(annotated, label_line2, (max(5, xc - 70), max(15, yc - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1, cv2.LINE_AA)
                        
        return annotated

    def _empty_measurement(self):
        return {
            'area_px': 0.0,
            'equiv_diameter_px': 0.0,
            'major_axis_px': 0.0,
            'minor_axis_px': 0.0,
            'aspect_ratio': 0.0,
            'estimated_major_mm': 0.0,
            'estimated_minor_mm': 0.0,
            'estimated_diameter_mm': 0.0,
            'clinical_size_band': "N/A",
            'disclaimer': NON_CLINICAL_DISCLAIMER,
            'centroid_xy': (0, 0),
            'major_axis_line': ((0, 0), (0, 0)),
            'minor_axis_line': ((0, 0), (0, 0))
        }

def measure_stone(contour, mm_per_pixel=ASSUMED_MM_PER_PIXEL):
    """Utility function to measure a single stone contour."""
    measurer = StoneMeasurer(mm_per_pixel=mm_per_pixel)
    return measurer.measure_contour(contour)
