import sys
import os
import time
import torch
import cv2
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from perception.perception_bridge import PerceptionEngine
from reasoning.graph_builder import UIGraphBuilder
from reasoning.grounding import ActionGroundingEngine

def test_perception():
    print("\n--- Testing Perception Layer ---")
    try:
        engine = PerceptionEngine()
        data = engine.perceive()
        print(f"PASS: Perceived UI. Layouts: {len(data['layouts'])}, Elements: {len(data['elements'])}, Text: {len(data['text'])}")
        return data
    except Exception as e:
        print(f"FAIL: Perception failed with error: {e}")
        return None

def test_graph_builder(data):
    if not data: return
    print("\n--- Testing Graph Builder ---")
    try:
        builder = UIGraphBuilder()
        graph = builder.build_graph(data)
        print(f"PASS: Built UI Graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges.")
        
        # Check for hierarchical edges
        parents = [e for e in graph.edges(data=True) if e[2].get('relation') == 'parent_of']
        print(f"Hierarchy: Found {len(parents)} containment relationships.")
        return graph
    except Exception as e:
        print(f"FAIL: Graph construction failed with error: {e}")
        return None

def test_grounding(graph):
    if not graph: return
    print("\n--- Testing Grounding Engine ---")
    try:
        grounder = ActionGroundingEngine()
        # Test with a common intent
        intent = "click search"
        node_id, confidence, action = grounder.ground(intent, graph)
        if node_id:
            attr = graph.nodes[node_id]
            print(f"PASS: Grounded '{intent}' to {node_id} ('{attr.get('semantic_label')}') with conf {confidence:.2f}")
        else:
            print("FAIL: No node grounded for intent.")
    except Exception as e:
        print(f"FAIL: Grounding failed with error: {e}")

def run_all_tests():
    data = test_perception()
    graph = test_graph_builder(data)
    test_grounding(graph)

if __name__ == "__main__":
    run_all_tests()
