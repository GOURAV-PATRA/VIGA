from typing import List, Dict, Any, Tuple
import networkx as nx  # type: ignore
import numpy as np

class UIGraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, perception_data):
        self.graph.clear()
        
        # 1. Add Layout Nodes (Containers)
        for i, lay in enumerate(perception_data['layouts']):
            node_id = f"layout_{i}"
            self.graph.add_node(node_id, 
                               type='layout',
                               class_name=lay['class'],
                               box=lay['box'],
                               confidence=lay['confidence'],
                               semantic_label=f"container_{lay['class']}")
            
        # 2. Add Element Nodes (Interaction Units)
        for i, el in enumerate(perception_data['elements']):
            node_id = f"element_{i}"
            self.graph.add_node(node_id,
                               type='element',
                               class_name=el['class'],
                               box=el['box'],
                               confidence=el['confidence'],
                               semantic_label=el.get('semantic_tag', el['class']))
            
        # 3. Add Text Nodes (Semantic Anchors)
        for i, text_item in enumerate(perception_data['text']):
            node_id = f"text_{i}"
            bbox = text_item['box']
            x1, y1 = bbox[0]
            x2, y2 = bbox[2]
            
            self.graph.add_node(node_id,
                               type='text',
                               text=text_item['text'],
                               box=[x1, y1, x2, y2],
                               confidence=text_item['confidence'],
                               semantic_label=text_item['text'])

        self._establish_hierarchy()
        self._add_spatial_relationships()
        return self.graph

    def _establish_hierarchy(self):
        """
        Determines which elements are inside which layouts.
        """
        nodes = list(self.graph.nodes(data=True))
        layouts = [n for n in nodes if n[1]['type'] == 'layout']
        others = [n for n in nodes if n[1]['type'] != 'layout']
        
        for l_id, l_attr in layouts:
            for o_id, o_attr in others:
                if self._is_contained(o_attr['box'], l_attr['box']):  # type: ignore
                    self.graph.add_edge(l_id, o_id, relation='parent_of')

    def _add_spatial_relationships(self, threshold_px=80):
        nodes = list(self.graph.nodes(data=True))
        for i, (id1, attr1) in enumerate(nodes):
            for j, (id2, attr2) in enumerate(nodes):
                if i == j: continue
                if self.graph.has_edge(id1, id2) or self.graph.has_edge(id2, id1):
                    continue
                
                if self._is_near(attr1['box'], attr2['box'], threshold_px):  # type: ignore
                    self.graph.add_edge(id1, id2, relation='near')

    def _is_contained(self, inner: List[float], outer: List[float]) -> bool:
        return (inner[0] >= outer[0] - 5 and inner[1] >= outer[1] - 5 and 
                inner[2] <= outer[2] + 5 and inner[3] <= outer[3] + 5)

    def _is_near(self, box1: List[float], box2: List[float], threshold: float) -> bool:
        c1 = [(box1[0] + box1[2])/2, (box1[1] + box1[3])/2]
        c2 = [(box2[0] + box2[2])/2, (box2[1] + box2[3])/2]
        dist = np.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)
        return bool(dist < threshold)

if __name__ == "__main__":
    # Dummy verification
    builder = UIGraphBuilder()
    dummy_data = {
        'layouts': [{'box': [0, 0, 1000, 1000], 'class': 'form', 'confidence': 0.9}],
        'elements': [{'box': [100, 100, 200, 150], 'class': 'button', 'confidence': 0.85}],
        'text': [{'box': [[110, 110], [190, 110], [190, 140], [110, 140]], 'text': 'Submit', 'confidence': 0.95}]
    }
    graph = builder.build_graph(dummy_data)
    print(f"Nodes: {list(graph.nodes(data=True))}")
    print(f"Edges: {list(graph.edges(data=True))}")
