from typing import List, Dict, Any, Tuple, cast
import easyocr  # type: ignore
import numpy as np
import cv2  # type: ignore

class TextRecognizer:
    def __init__(self, languages=['en']):
        self.reader = easyocr.Reader(languages)

    def recognize(self, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Extracts text and coordinates from the image.
        Returns a list of results: [{'box': [[x,y],...], 'text': str, 'conf': float}]
        """
        # EasyOCR returns list of (bbox, text, confidence)
        results = self.reader.readtext(img)
        formatted_results = []
        for (bbox, text, conf) in results:
            formatted_results.append({
                'box': bbox,
                'text': str(text),
                'confidence': float(conf)
            })
        return formatted_results

    def get_text_center(self, bbox):
        """
        Calculates the center of a bbox returned by EasyOCR.
        Bbox format: [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        """
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        center_x = sum(xs) / len(xs)
        center_y = sum(ys) / len(ys)
        return (center_x, center_y)

if __name__ == "__main__":
    import sys
    import os
    # Add root to path for local execution
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from perception.screen_capture import ScreenCapturer  # type: ignore
    
    capturer = ScreenCapturer()
    img = capturer.capture()
    
    recognizer = TextRecognizer()
    results = recognizer.recognize(img)
    
    print(f"Recognized {len(results)} text segments.")
    results_slice = results[:5]  # type: ignore
    for res in results_slice:
        print(f"Text: {res['text']} @ {res['box']}")
