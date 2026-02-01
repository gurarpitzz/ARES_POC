# ARES_POC — Research Verification Engine

ARES_POC is a mathematically grounded misinformation verification system.  
Unlike LLM-based fact checkers, ARES computes truth using a deterministic evidence functional:

\[
Truth'(C) = \frac{\sum S(C,E)\cdot N(C,E)\cdot W(E)}{\sum S(C,E)}
\]

This repository is the Proof-of-Concept implementation accompanying the research manuscript.

---

## What ARES Does

Given a claim C, ARES:

1. Retrieves evidence passages (R)
2. Selects Top-M semantically relevant passages (S)
3. Evaluates entailment / contradiction (N)
4. Applies source credibility priors (W)
5. Computes a reproducible truth score

---

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run single claim verification

```bash
py main.py "The Earth orbits the Sun" --k 10 --m 5
```

### Run benchmark evaluation

```bash
py evaluate.py --dataset liar --samples 20
```

---

## File → Mathematical Operator Mapping

| File | Operator | Role |
|-----|-----|-----|
| retriever.py | R(C) | Evidence retrieval |
| similarity.py | S(C,E) | Top-M ranking |
| entailment.py | N(C,E) | Logical validation |
| credibility.py | W(E) | Source prior |
| verifier.py | V(C) | Truth functional |

---

## Determinism

ARES uses a local `cache/` to ensure that the same claim with same parameters always produces the same truth score.

---

## Research Integrity

ARES does not generate answers.  
It derives verdicts strictly from discovered evidence.

---

## License

MIT License
