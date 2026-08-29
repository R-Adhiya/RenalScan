import cv2
import numpy as np

class StoneSegmenter:
    """Classical Computer Vision Kidney Stone ROI Segmentation Engine."""
    
    def __init__(self, padding_pct=0.10, min_area=5):
        """
        Args:
            padding_pct (float): Fractional padding margin around YOLO bounding box (e.g. 0.10 for 10%).
            min_area (int): Minimum contour area in pixels to be considered a valid stone candidate.
        """
        self.padding_pct = padding_pct
        self.min_area = min_area

    def segment_roi(self, image, bbox):
        """Segments the kidney stone within a single bounding box ROI using Classical CV.
        
        Pipeline:
        1. Crop ROI with 10% padding margin.
        2. Convert crop to grayscale.
        3. Apply Otsu's adaptive thresholding to separate bright CT stone ROI from tissue.
        4. Apply morphological opening (noise removal) and closing (hole filling).
        5. Extract the largest high-intensity contour inside the ROI crop.
        6. Remap local mask coordinates back to original image space.
        
        Args:
            image (np.ndarray): Input CT image array (H, W, C) or (H, W).
            bbox (list/tuple): Bounding box coordinates [x1, y1, x2, y2].
            
        Returns:
            dict: {
                'full_mask': np.ndarray (H, W) uint8 binary mask (0 or 255),
                'crop_mask': np.ndarray local crop uint8 mask,
                'contour_global': np.ndarray contour points shifted to full image space,
                'area_px': float contour area in pixels,
                'bbox_padded': [x1_pad, y1_pad, x2_pad, y2_pad]
            }
        """
        if len(image.shape) == 3:
            h_img, w_img, _ = image.shape
            gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            h_img, w_img = image.shape
            gray_img = image.copy()
            
        x1, y1, x2, y2 = map(int, bbox)
        
        # 1. Padded Crop
        w_box = x2 - x1
        h_box = y2 - y1
        pad_w = int(w_box * self.padding_pct)
        pad_h = int(h_box * self.padding_pct)
        
        x1_pad = max(0, x1 - pad_w)
        y1_pad = max(0, y1 - pad_h)
        x2_pad = min(w_img, x2 + pad_w)
        y2_pad = min(h_img, y2 + pad_h)
        
        crop_gray = gray_img[y1_pad:y2_pad, x1_pad:x2_pad]
        crop_h, crop_w = crop_gray.shape
        
        full_mask = np.zeros((h_img, w_img), dtype=np.uint8)
        crop_mask = np.zeros((crop_h, crop_w), dtype=np.uint8)
        
        if crop_h == 0 or crop_w == 0:
            return {
                'full_mask': full_mask,
                'crop_mask': crop_mask,
                'contour_global': None,
                'area_px': 0.0,
                'bbox_padded': [x1_pad, y1_pad, x2_pad, y2_pad]
            }
            
        # 2 & 3. Otsu Thresholding
        # High CT intensity = bright kidney stone relative to soft tissue
        _, otsu_thresh = cv2.threshold(crop_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 4. Morphological Cleaning
        # Opening (ellipse 3x3) eliminates isolated high-intensity pixel noise
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        clean_open = cv2.morphologyEx(otsu_thresh, cv2.MORPH_OPEN, kernel_open)
        
        # Closing (ellipse 5x5) closes internal voids within stone core
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        clean_mask = cv2.morphologyEx(clean_open, cv2.MORPH_CLOSE, kernel_close)
        
        # 5. Extract Largest Contour
        # ASSUMPTION: The largest high-intensity contour inside the padded ROI crop
        # corresponds to the kidney stone. This assumption can fail if bright calcifications,
        # stents, or adjacent cortical bone fragments fall inside the ROI bounding box.
        contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        largest_contour = None
        max_area = 0.0
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > max_area and area >= self.min_area:
                max_area = area
                largest_contour = cnt
                
        contour_global = None
        if largest_contour is not None:
            # Draw local mask
            cv2.drawContours(crop_mask, [largest_contour], -1, 255, thickness=cv2.FILLED)
            
            # 6. Map coordinates back to full image space
            full_mask[y1_pad:y2_pad, x1_pad:x2_pad] = crop_mask
            
            # Shift contour points to global coordinates
            contour_global = largest_contour.copy()
            contour_global[:, 0, 0] += x1_pad
            contour_global[:, 0, 1] += y1_pad
            
        return {
            'full_mask': full_mask,
            'crop_mask': crop_mask,
            'contour_global': contour_global,
            'area_px': max_area,
            'bbox_padded': [x1_pad, y1_pad, x2_pad, y2_pad]
        }

    def segment_image_detections(self, image, detections):
        """Segments all detected bounding boxes for a single image.
        
        Args:
            image (np.ndarray): CT scan image.
            detections (list[dict]): List of detection dictionaries from StoneDetector.predict().
            
        Returns:
            list[dict]: List of segmentation result dictionaries per detected bounding box.
        """
        results = []
        for det in detections:
            bbox = det['box_xyxy']
            seg_info = self.segment_roi(image, bbox)
            seg_info['class_name'] = det.get('class_name', 'Kidney Stone')
            seg_info['confidence'] = det.get('confidence', 0.0)
            seg_info['box_xyxy'] = bbox
            results.append(seg_info)
        return results

def segment_stone(image, bbox, padding_pct=0.10):
    """Utility function to segment a single stone bounding box."""
    segmenter = StoneSegmenter(padding_pct=padding_pct)
    return segmenter.segment_roi(image, bbox)
