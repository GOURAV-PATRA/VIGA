from typing import List, Dict, Any, Optional, cast
import sys
import os
import time

# Add src to path if not already there
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if src_path not in sys.path:
    sys.path.append(src_path)

from perception.perception_bridge import PerceptionEngine  # type: ignore
from reasoning.graph_builder import UIGraphBuilder  # type: ignore
from reasoning.grounding import ActionGroundingEngine  # type: ignore
from execution.executor import ExecutionEngine  # type: ignore
from utils.temporal import TemporalManager  # type: ignore

class VIGAAgent:
    def __init__(self):
        print("Initializing VIGA (Advanced Architecture)...")
        self.perception = PerceptionEngine()
        self.graph_builder = UIGraphBuilder()
        self.grounder = ActionGroundingEngine()
        self.executor = ExecutionEngine()
        self.temporal = TemporalManager()

    def run_command(self, user_intent: str) -> bool:
        try:
            print(f"\n[Goal] {user_intent}")
            
            # 1. Perception
            start_time = float(time.time())
            print("[1/4] Perceiving UI (Hierarchical + CLIP)...")
            raw_data = self.perception.perceive()
            
            # 2. Temporal Smoothing
            print("      Applying temporal stability...")
            data = self.temporal.update(raw_data)
            
            # 3. Reasoning - Hierarchical Graph Construction
            print("[2/4] Constructing Hierarchical UI Graph...")
            graph = self.graph_builder.build_graph(data)
            
            # 4. Reasoning - Multimodal Grounding
            print("[3/4] Grounding intent to structured scene...")
            node_id, confidence, action_type = self.grounder.ground(user_intent, graph)
            
            duration = (float(time.time()) - start_time) * 1000
            print(f"      Pipeline Latency: {duration:.2f}ms")

            if node_id and confidence > 0.35:
                attr = graph.nodes[node_id]
                coords = self.executor.get_center(attr['box'])
                
                # Find context for logging
                parents = [p for p, c, d in graph.in_edges(node_id, data=True) if d.get('relation') == 'parent_of']
                context = ""
                if parents:
                    p_node = graph.nodes[parents[0]]
                    context = f" in {p_node.get('semantic_label', 'container')}"
                
                print(f"      Matched: '{attr.get('semantic_label', 'element')}'{context} (Conf: {confidence:.2f})")
                
                # 5. Execution
                print(f"[4/4] Grounded Action: {action_type} at {coords}...")
                # Simulation mode
                # self.executor.execute({'action': action_type, 'coordinates': coords})
                print("      Action simulation successful.")
                return True
            else:
                print("      FAILED: Could not find a reliable semantic match in the UI scene.")
                return False
        except Exception as e:
            print(f"      CRITICAL ERROR in agent loop: {e}")
            return False

def main() -> None:
    agent = VIGAAgent()
    
    # Cast to list to satisfy certain linters for slicing
    args = cast(List[str], sys.argv)
    if len(args) > 1:
        intent = " ".join(args[1:])  # type: ignore
    else:
        intent = "click the Windows Start button" # Default example
        
    agent.run_command(intent)

if __name__ == "__main__":
    main()
