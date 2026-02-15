import mss
import numpy as np
import cv2
from PIL import Image

class ScreenCapturer:
    def __init__(self):
        self.sct = mss.mss()

    def capture(self, monitor_number=1):
        """
        Captures the screen and returns a numpy array (BGR).
        """
        monitors = self.sct.monitors
        if monitor_number >= len(monitors):
            monitor_number = 1
        
        monitor = monitors[monitor_number]
        screenshot = self.sct.grab(monitor)
        # Convert to numpy array and remove alpha channel if present
        img = np.array(screenshot)
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def save_capture(self, filename, img=None):
        if img is None:
            img = self.capture()
        cv2.imwrite(filename, img)
        return filename

if __name__ == "__main__":
    capturer = ScreenCapturer()
    path = capturer.save_capture("debug_screenshot.png")
    print(f"Screenshot saved to {path}")
