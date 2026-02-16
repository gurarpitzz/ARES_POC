![GitHub stars](https://img.shields.io/github/stars/gurarpitzz/ARES_POC)
![GitHub license](https://img.shields.io/github/license/gurarpitzz/ARES_POC)
# ARES_POC (Autonomous Real-time Evaluation System Proof) — Research Verification Engine

ARES_POC is a mathematically grounded misinformation verification system.  
Unlike LLM-based fact checkers, ARES computes truth using a deterministic evidence functional:

$$
Truth'(C) = \frac{\sum_{i=1}^{M} S(C,E_i)\cdot N(C,E_i)\cdot W(E_i)}{\sum_{i=1}^{M} S(C,E_i)}
$$


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
---

## Web Interface Preview (ARES_UI)

ARES also includes a research-grade visualization interface for inspecting the mathematical verification process.

### Overall Interface

![ARES UI Overview](assets/ui_input.png)

---

### Verdict Dashboard

The verdict panel shows the final decision along with the computed Truth Score and Confidence derived from the functional.

![Verdict Panel](assets/ui_verdict.png)

---

### Mathematical Evidence Trace

Every evidence passage contributing to the verdict is shown with:

- Semantic Similarity \(S(C,E)\)
- Entailment Score \(N(C,E)\)
- Source Weight \(W(E)\)
- Individual Contribution to Truth'

This ensures full transparency of the decision process.

![Evidence Trace](assets/ui_trace.png)

---

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
