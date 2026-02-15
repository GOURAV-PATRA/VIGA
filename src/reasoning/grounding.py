from sentence_transformers import SentenceTransformer, util
import torch

class ActionGroundingEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def ground(self, intent, ui_graph):
        """
        Matches intent to the most relevant node in the UI Graph using 
        multimodal attributes (text, type, hierarchy).
        """
        nodes = list(ui_graph.nodes(data=True))
        if not nodes:
            return None, 0.0, None

        # Prepare augmented candidates
        candidates = []
        node_ids = []
        
        for node_id, attr in nodes:
            # Augment label with context (e.g., "Login text inside container_form")
            # This implements the structural reasoning part of the grounding problem
            base_label = attr.get('semantic_label', attr.get('text', attr.get('class_name', "")))
            
            # Find parent context
            parents = [p for p, c, d in ui_graph.in_edges(node_id, data=True) if d.get('relation') == 'parent_of']
            parent_context = ""
            if parents:
                p_attr = ui_graph.nodes[parents[0]]
                parent_context = f" inside {p_attr.get('semantic_label', p_attr.get('class_name', 'container'))}"
            
            augmented_label = f"{base_label}{parent_context}"
            candidates.append(augmented_label)
            node_ids.append(node_id)

        # Encode and calculate similarity
        intent_embedding = self.model.encode(intent, convert_to_tensor=True)
        candidate_embeddings = self.model.encode(candidates, convert_to_tensor=True)
        
        cos_scores = util.cos_sim(intent_embedding, candidate_embeddings)[0]
        best_idx = torch.argmax(cos_scores).item()
        
        best_node_id = node_ids[best_idx]
        confidence = float(cos_scores[best_idx])
        
        # Action inference logic
        action_type = self._infer_action(intent, ui_graph.nodes[best_node_id])
            
        return best_node_id, confidence, action_type

    def _infer_action(self, intent, target_node):
        intent_low = intent.lower()
        if "type" in intent_low or "input" in intent_low:
            return "type"
        if "double" in intent_low:
            return "double_click"
        # Fallback based on element type
        if target_node.get('class_name') in ['input', 'text_area']:
            return "type"
        return "click"

if __name__ == "__main__":
    import networkx as nx
    g = nx.DiGraph()
    g.add_node("n1", type="text", text="Login Button", box=[10,10,50,50])
    g.add_node("n2", type="text", text="Username Input", box=[10,100,50,150])
    
    grounder = ActionGroundingEngine()
    node, conf, action = grounder.ground("click login", g)
    print(f"Goal: 'click login' -> Node: {node}, Conf: {conf:.2f}, Action: {action}")
