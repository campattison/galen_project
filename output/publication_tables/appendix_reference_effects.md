# Appendix Table: Reference Translation Effects

*Generated: 2026-01-22*

**Purpose:** Show how scores differ when using Johnston vs van der Eijk as reference.

**Status:** TEMPLATE - Requires per-reference evaluation data.

To generate this table, run evaluations with each reference separately:
```bash
# Evaluate against Johnston only
python pipeline.py evaluate --input input/on_mixtures.txt --reference-subset johnston

# Evaluate against van der Eijk only
python pipeline.py evaluate --input input/on_mixtures.txt --reference-subset vandereijk
```

| Model | Metric | Johnston | van der Eijk | Δ (J - vdE) |
|-------|--------|----------|--------------|-------------|
| ChatGPT | BLEU-4 | — | — | — |
| ChatGPT | COMET | — | — | — |
| Claude | BLEU-4 | — | — | — |
| Claude | COMET | — | — | — |
| Gemini | BLEU-4 | — | — | — |
| Gemini | COMET | — | — | — |

**Interpretation:** A positive Δ indicates the model aligns more closely with Johnston's translation style.