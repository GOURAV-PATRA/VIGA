from typing import List, Dict, Any, Union, cast
from ultralytics import YOLO  # type: ignore
import cv2  # type: ignore
import numpy as np
import torch  # type: ignore
from transformers import CLIPProcessor, CLIPModel  # type: ignore

class UIDetector:
    def __init__(self, atomic_model='yolov8n.pt', layout_model='yolov8n.pt'):
        """
        Initializes a hierarchical detector.
        Layout Model: For containers (forms, panels, toolbars).
        Atomic Model: For primitives (buttons, inputs, icons).
        """
        # In a real scenario, these would be custom fine-tuned models
        self.atomic_model = YOLO(atomic_model)
        self.layout_model = YOLO(layout_model)
        
        # Load CLIP for icon semantics
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model.to(self.device)

    def detect(self, img: np.ndarray) -> Dict[str, List[Dict[str, Any]]]:
        """
        Performs hierarchical detection.
        Returns {'layouts': [...], 'elements': [...]}
        """
        layout_results = self.layout_model(img, verbose=False)
        atomic_results = self.atomic_model(img, verbose=False)
        
        layouts = self._process_results(layout_results, "layout")
        elements = self._process_results(atomic_results, "element")
        
        # Semantic enrichment for icons
        for el in elements:
            if el['class'] in ['icon', 'image'] or el['confidence'] < 0.6:
                el['semantic_tag'] = self._get_icon_semantics(img, el['box'])
        
        return {
            'layouts': layouts,
            'elements': elements
        }

    def _process_results(self, results: Any, group: str) -> List[Dict[str, Any]]:
        processed = []
        for result in results:
            if not hasattr(result, 'boxes'):
                continue
            for box in result.boxes:
                coords = box.xyxy[0].tolist()
                cls_id = int(box.cls[0])
                cls_name = str(result.names[cls_id])
                processed.append({
                    'group': group,
                    'box': coords,
                    'confidence': float(box.conf[0]),
                    'class': cls_name
                })
        return processed

    def _get_icon_semantics(self, img, box):
        """
        Uses CLIP to understand icon semantics when labels are missing.
        """
        x1, y1, x2, y2 = map(int, box)
        crop = img[y1:y2, x1:x2]
        if crop.size == 0: return "unknown"
        
        labels = ["settings gear", "trash delete", "search magnifier", "user profile", "home", "plus add"]
        inputs = self.clip_processor(text=labels, images=crop, return_tensors="pt", padding=True).to(self.device)
        
        with torch.no_grad():
            outputs = self.clip_model(**inputs)
        
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)
        best_label = labels[probs.argmax().item()]
        
        return best_label

    def draw_detections(self, img, detections):
        annotated_img = img.copy()
        # Draw Layouts (Blue)
        for lay in detections['layouts']:
            x1, y1, x2, y2 = map(int, lay['box'])
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            cv2.putText(annotated_img, f"L:{lay['class']}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                        
        # Draw Elements (Green)
        for el in detections['elements']:
            x1, y1, x2, y2 = map(int, el['box'])
            label = el.get('semantic_tag', el['class'])
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.putText(annotated_img, f"E:{label}", (x1, y1 + 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                        
        return annotated_img

if __name__ == "__main__":
    # Local import for testing
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from perception.screen_capture import ScreenCapturer  # type: ignore
    
    capturer = ScreenCapturer()
    img = capturer.capture()
    
    detector = UIDetector()
    detections = detector.detect(img)
    
    print(f"Detected {len(detections['elements'])} elements and {len(detections['layouts'])} layout containers.")
    elements_slice = detections['elements'][:5]  # type: ignore
    for det in elements_slice:
        print(det)
    
    annotated = detector.draw_detections(img, detections)
    cv2.imwrite("detections_debug.png", annotated)
