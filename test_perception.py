import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from perception.perception_bridge import PerceptionEngine

def main():
    print("Initializing VIGA Perception Engine...")
    engine = PerceptionEngine()
    
    print("Capturing and processing screen...")
    data = engine.perceive()
    
    print("\n--- Perception Results ---")
    print(f"Elements detected: {len(data['detections'])}")
    print(f"Text segments found: {len(data['text'])}")
    
    if data['text']:
        print("\nTop 5 text segments:")
        for res in data['text'][:5]:
            print(f"- {res['text']} (conf: {res['confidence']:.2f})")

if __name__ == "__main__":
    main()
