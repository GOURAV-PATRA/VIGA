import pyautogui
import time

class ExecutionEngine:
    def __init__(self):
        # Fail-safe: moving mouse to corner aborts
        pyautogui.FAILSAFE = True

    def execute(self, action_data):
        """
        Executes an action based on data: 
        {action: 'click'|'type', coordinates: (x, y), text: optional}
        """
        action = action_data.get('action')
        coords = action_data.get('coordinates')
        
        if not coords:
            return False

        x, y = coords
        print(f"Executing {action} at ({x}, {y})")
        
        if action == "click":
            pyautogui.click(x, y)
        elif action == "type":
            pyautogui.click(x, y)
            time.sleep(0.5)
            text = action_data.get('text', "")
            pyautogui.typewrite(text)
        elif action == "double_click":
            pyautogui.doubleClick(x, y)
        
        return True

    def get_center(self, box):
        """
        box: [x1, y1, x2, y2]
        """
        return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2

if __name__ == "__main__":
    executor = ExecutionEngine()
    # executor.execute({'action': 'click', 'coordinates': (100, 100)})
    print("Execution Engine Initialized")
