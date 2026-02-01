from transformers import pipeline
from typing import List, Dict

class EntailmentOperator:
    def __init__(self, model_name: str = 'facebook/bart-large-mnli'):
        # Using the zero-shot-classification pipeline as it's a common wrapper for MNLI
        # or we can use raw SequenceClassification. Let's use raw for "mathematical" precision.
        self.nli_pipeline = pipeline("text-classification", model=model_name, device=-1) # CPU for reproducibility in small env

    def compute(self, claim: str, evidence: str) -> int:
        """
        N(C, E_i) = {+1 (Entailment), 0 (Neutral), -1 (Contradiction)}
        """
        if not evidence.strip() or not claim.strip():
            return 0
            
        try:
            # Verbose logging for debugging the IndexError: 0
            if len(evidence) < 5 or len(claim) < 5:
                return 0
                
            # Correct MNLI format: premise=evidence, hypothesis=claim
            # Using list of dicts for more robust pipeline processing
            result = self.nli_pipeline(
                [{"text": evidence[:1000], "text_pair": claim[:200]}]
            )
            
            if not result or not result[0]:
                return 0
                
            prediction = result[0]
            label = prediction['label'].lower()
            
            if 'entailment' in label:
                return 1
            elif 'contradiction' in label:
                return -1
            else:
                return 0
        except Exception as e:
            import traceback
            print(f"[ERROR] Entailment calculation failed: {e}")
            traceback.print_exc()
            return 0

if __name__ == "__main__":
    eo = EntailmentOperator()
    c = "The moon is made of cheese."
    e1 = "The moon is composed of volcanic rock." # Contradiction
    e2 = "People like to eat cheese." # Neutral
    e3 = "Satellite data shows the moon is made of cheddar." # Entailment (hypothetically)
    
    print(f"E1: {eo.compute(c, e1)}")
    print(f"E2: {eo.compute(c, e2)}")
    print(f"E3: {eo.compute(c, e3)}")
