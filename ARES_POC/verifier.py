# This module implements the verification functional:
# Truth'(C) = Σ S(C,E)·N(C,E)·W(E) / Σ S(C,E)
# as defined in the ARES_POC research specification.

import math
from typing import List, Dict
from retriever import Retriever
from similarity import SimilarityFilter
from entailment import EntailmentOperator
from credibility import CredibilityWeight

class Verifier:
    def __init__(self, k: int = 10, m: int = 5, mode: str = "web"):
        self.m = m
        self.retriever = Retriever(k=k, mode=mode)
        self.similarity = SimilarityFilter()
        self.entailment = EntailmentOperator()
        self.credibility = CredibilityWeight()

    def verify(self, claim: str, local_data: List[Dict] = None) -> Dict:
        """
        V(C) = f(R(C), TopM S(C,E), N(C,E), W(E))
        Full pipeline: Retrieval -> Ranking -> Entailment -> Aggregation.
        """
        # -------------------------------
        # Step 1 — Evidence Retrieval R(C)
        # -------------------------------
        raw_passages = self.retriever.retrieve(claim, local_data)
        return self.verify_with_evidence(claim, raw_passages)

    def verify_with_evidence(self, claim: str, evidence_passages: List[Dict[str, str]]) -> Dict:
        """
        V(C) = f(TopM S(C,E), N(C,E), W(E))
        Isolates the verification functional by using provided evidence.
        Used for gold-standard benchmarks (e.g., FEVER).
        """
        # -------------------------------
        # Step 2 — Similarity Ranking S(C,E) & Top-M selection
        # -------------------------------
        print(f"[DEBUG] Retrieved {len(evidence_passages)} raw passages from R(C)")
        top_passages = self.similarity.rank(claim, evidence_passages, m=self.m)
        m_actual = len(top_passages)
        
        if m_actual == 0:
            return {
                "claim": claim,
                "truth_score": 0.0,
                "confidence": 0.0,
                "verdict": "UNCERTAIN",
                "evidence_count": 0
            }

        # -------------------------------
        # Step 3, 4, 5 — Entailment N, Credibility W, and Weighted Aggregation
        # Integrated Truth Functional: Σ (S * N * W) / Σ S
        # -------------------------------
        numerator = 0.0
        denominator = 0.0
        trace = []
        
        for p in top_passages:
            s_i = p['similarity_score']
            n_i = self.entailment.compute(claim, p['text'])
            w_i = self.credibility.calculate(p.get('url', 'http://internal.wiki'))
            
            numerator += (s_i * n_i * w_i)
            denominator += s_i
            
            trace.append({
                "source": p.get('url', 'internal'),
                "text": p['text'][:100] + "...",
                "similarity": s_i,
                "entailment": n_i,
                "weight": w_i,
                "contribution": s_i * n_i * w_i
            })

        truth_prime = numerator / denominator if denominator > 0 else 0.0
        
        # -------------------------------
        # Step 6 — Confidence Conf(C) = |Truth'| * log(1 + M)
        # -------------------------------
        confidence = abs(truth_prime) * math.log(1 + m_actual)
        
        # -------------------------------
        # Step 7 — Verdict function
        # -------------------------------
        if truth_prime > 0.4:
            verdict = "VERIFIED"
        elif truth_prime < -0.4:
            verdict = "MISINFORMATION"
        else:
            verdict = "UNCERTAIN"
            
        return {
            "claim": claim,
            "truth_score": truth_prime,
            "confidence": confidence,
            "verdict": verdict,
            "evidence_count": m_actual,
            "trace": trace
        }

if __name__ == "__main__":
    # Internal research trace test
    v = Verifier(k=5, m=3)
    res = v.verify("The Earth orbits the Sun.")
    import json
    print(json.dumps(res, indent=2))
