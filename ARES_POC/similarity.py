from sentence_transformers import SentenceTransformer, util
import torch
from typing import List, Dict

_MODEL_CACHE = {}

class SimilarityFilter:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', threshold: float = 0.6):
        if model_name not in _MODEL_CACHE:
            _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
        self.model = _MODEL_CACHE[model_name]
        self.threshold = threshold

    def rank(self, claim: str, passages: List[Dict[str, str]], m: int = 5) -> List[Dict[str, str]]:
        """
        Top-M selection operator: E* = TopM(S(C, E_i))
        Ranks all passages by similarity and selects top M.
        """
        if not passages:
            return []
            
        claim_embedding = self.model.encode(claim, convert_to_tensor=True)
        passage_texts = [p['text'] for p in passages]
        passage_embeddings = self.model.encode(passage_texts, convert_to_tensor=True)
        
        cosine_scores = util.cos_sim(claim_embedding, passage_embeddings)[0]
        
        scored_passages = []
        for i, score in enumerate(cosine_scores):
            p = passages[i].copy()
            p['similarity_score'] = score.item()
            scored_passages.append(p)
                
        # Sort by similarity score descending
        scored_passages.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Select top M
        return scored_passages[:m]

if __name__ == "__main__":
    sf = SimilarityFilter()
    c = "The moon is made of green cheese."
    ps = [
        {'text': "The moon is a natural satellite of Earth."},
        {'text': "Cheese is a dairy product."},
        {'text': "NASA missions have confirmed the moon is rocks."}
    ]
    ranked = sf.rank(c, ps, m=2)
    for f in ranked:
        print(f"Score: {f['similarity_score']:.4f} | Text: {f['text']}")
