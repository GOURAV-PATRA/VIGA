from perception.screen_capture import ScreenCapturer
from perception.detector import UIDetector
from perception.ocr import TextRecognizer
import cv2

class PerceptionEngine:
    def __init__(self):
        self.capturer = ScreenCapturer()
        self.detector = UIDetector()
        self.recognizer = TextRecognizer()

    def perceive(self):
        """
        Captures screen, detects layout & atomic elements, and recognizes text.
        Returns a dictionary with all visual data.
        """
        img = self.capturer.capture()
        detections = self.detector.detect(img)
        text_results = self.recognizer.recognize(img)
        
        return {
            'image': img,
            'layouts': detections['layouts'],
            'elements': detections['elements'],
            'text': text_results
        }

    def get_annotated_frame(self, data):
        img = data['image'].copy()
        
        # Draw Layouts (Blue)
        for lay in data['layouts']:
            x1, y1, x2, y2 = map(int, lay['box'])
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
        # Draw Elements (Green)
        for el in data['elements']:
            x1, y1, x2, y2 = map(int, el['box'])
            label = el.get('semantic_tag', el['class'])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.putText(img, label, (x1, y2 + 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
        # Draw text (Red)
        for res in data['text']:
            bbox = res['box']
            p1 = tuple(map(int, bbox[0]))
            p2 = tuple(map(int, bbox[2]))
            cv2.rectangle(img, p1, p2, (0, 0, 255), 1)
            
        return img

if __name__ == "__main__":
    engine = PerceptionEngine()
    data = engine.perceive()
    print(f"Detected {len(data['detections'])} elements and {len(data['text'])} text blocks.")
    
    annotated = engine.get_annotated_frame(data)
    cv2.imwrite("perception_debug.png", annotated)
    print("Saved perception_debug.png")
