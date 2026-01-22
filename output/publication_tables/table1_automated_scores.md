# Table 1: Aggregate Automated MT Evaluation Scores

*Generated: 2026-01-22*

**Purpose:** Satisfy requirement for 'standard methods' benchmarking; compare with previous papers.

| Text | Model | BLEU-4 | chrF++ | METEOR | ROUGE-L | BERTScore | COMET |
|------|-------|-------|-------|-------|-------|-------|-------|
| *Mixtures* | ChatGPT | 31.4 (± 5.8) | 53.4 (± 3.5) | 46.4 (± 5.1) | 50.9 (± 5.0) | 91.0 (± 1.1) | 79.9 (± 1.8) |
|  | Claude | 34.2 (± 5.9) | 55.4 (± 3.2) | 48.5 (± 3.2) | 55.3 (± 5.3) | 91.6 (± 0.9) | 79.8 (± 2.0) |
|  | Gemini | 34.2 (± 4.7) | 57.0 (± 2.7) | 50.0 (± 3.7) | 56.0 (± 4.6) | 91.5 (± 1.0) | 80.7 (± 1.7) |
|  | *Aggregate* | 33.3 (± 5.5) | 55.3 (± 3.1) | 48.3 (± 4.0) | 54.1 (± 5.0) | 91.4 (± 1.0) | 80.1 (± 1.8) |
| *Comp.* | ChatGPT | 15.7 (± 5.1) | 47.4 (± 5.0) | 40.1 (± 6.4) | 45.7 (± 5.9) | 89.1 (± 2.0) | 75.1 (± 3.8) |
|  | Claude | 16.7 (± 4.5) | 49.4 (± 2.3) | 42.9 (± 4.2) | 47.8 (± 2.6) | 89.7 (± 1.5) | 76.5 (± 2.2) |
|  | Gemini | 19.0 (± 3.8) | 51.2 (± 2.9) | 44.4 (± 4.5) | 47.8 (± 3.7) | 89.9 (± 1.3) | 77.3 (± 2.2) |
|  | *Aggregate* | 17.1 (± 4.4) | 49.3 (± 3.4) | 42.5 (± 5.0) | 47.1 (± 4.0) | 89.5 (± 1.6) | 76.3 (± 2.7) |

**Note:** All scores reported as mean (± SD) × 100. BLEU-4, chrF++, METEOR use multi-reference evaluation; ROUGE-L, BERTScore, COMET use max-across-references. BLEURT excluded due to technical limitations.