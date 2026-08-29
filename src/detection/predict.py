from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

class StoneDetector:
    """YOLOv8 Kidney Stone Detector Inference Wrapper."""
    
    def __init__(self, model_path=None):
        if model_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            model_path = project_root / "models" / "detection_best.pt"
            if not model_path.exists():
                # Fallback to runs directory if models/ does not exist yet
                model_path = project_root / "runs" / "detect" / "train_run" / "weights" / "best.pt"
        
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Trained model weights not found at: {self.model_path}")
        
        self.model = YOLO(str(self.model_path))
        print(f"Loaded StoneDetector weights from: {self.model_path}")

    def predict(self, image_input, conf_thresh=0.25, imgsz=512):
        """Runs detection on an image path or numpy array.
        
        Returns:
            annotated_image (np.ndarray): Image with bounding boxes and labels overlaid.
            detections (list[dict]): Extracted bounding box dictionary list.
        """
        if isinstance(image_input, (str, Path)):
            img = cv2.imread(str(image_input))
            if img is None:
                raise ValueError(f"Could not load image from path: {image_input}")
        elif isinstance(image_input, np.ndarray):
            img = image_input.copy()
        else:
            raise TypeError("image_input must be a file path string, Path object, or numpy ndarray")
        
        results = self.model.predict(source=img, conf=conf_thresh, imgsz=imgsz, device="cpu", verbose=False)
        result = results[0]
        
        detections = []
        annotated_img = result.plot() # Ultralytics annotated plot (BGR)
        
        boxes = result.boxes
        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                xyxy = box.xyxy[0].cpu().numpy().tolist()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = self.model.names.get(cls_id, f"Class {cls_id}")
                
                detections.append({
                    'class_name': cls_name,
                    'class_id': cls_id,
                    'confidence': conf,
                    'box_xyxy': [int(v) for v in xyxy], # [x1, y1, x2, y2]
                    'box_xywh': [float(v) for v in box.xywh[0].cpu().numpy()]
                })
        
        return annotated_img, detections

def predict_single_image(image_path, model_path=None, conf_thresh=0.25):
    """Utility function to load detector and run inference on one image."""
    detector = StoneDetector(model_path=model_path)
    return detector.predict(image_path, conf_thresh=conf_thresh)
