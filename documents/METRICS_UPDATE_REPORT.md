# Automated Translation Metrics: Implementation Update Report

**Date:** January 16, 2026  
**Author:** Generated with assistance from AI  
**Version:** 2.0 (Multi-Reference Implementation)

> **Note (January 22, 2026):** The metrics suite has been further narrowed to 6 core metrics:
> BLEU-4, chrF++, METEOR, ROUGE-L, BERTScore, and COMET. SentenceBERT has been removed.
> See `WORKLOG_2026-01-22_metrics_narrowing.md` for details.

---

## Executive Summary

The translation evaluation pipeline has been updated to implement correct multi-reference evaluation methodology. The previous implementation evaluated machine translations against each reference translation separately and then averaged the scores—a practice that is not standard in machine translation evaluation and produces artificially deflated scores. The updated implementation follows established best practices for each metric type.

### Summary of Changes

| Metric | Previous Behavior | New Behavior |
|:-------|:------------------|:-------------|
| **BLEU** | Single reference, averaged | Multi-reference (n-grams checked against ANY reference) |
| **chrF** | Single reference, averaged | Multi-reference (native sacrebleu support) |
| **ROUGE** | Single reference, averaged | Compute per-reference, take MAX |
| **BERTScore** | Single reference, averaged | Compute per-reference, take MAX |
| **SentenceBERT** | Single reference, averaged | Compute per-reference, take MAX |
| **COMET** | Single reference, averaged | Compute per-reference, take MAX |
| **BLEURT** | Single reference, averaged | Compute per-reference, take MAX |

---

## Background

### The Problem

The original evaluator computed scores as follows:

1. For each candidate translation, score against Reference 1
2. For each candidate translation, score against Reference 2
3. Store both scores separately
4. In aggregation, average all scores together

This approach has two significant problems:

1. **Methodologically incorrect**: Multi-reference evaluation metrics are designed to handle multiple references differently. Averaging single-reference scores does not replicate the behavior of proper multi-reference evaluation.

2. **Penalizes translations unfairly**: If one reference translation is stylistically different or lower quality, it drags down the scores for candidates that correctly match the other reference.

### Standard Practice

The machine translation evaluation literature establishes different approaches depending on the metric type:

| Metric Type | Standard Multi-Reference Approach |
|-------------|-----------------------------------|
| **Lexical (BLEU, chrF)** | Pass all references to the scoring function; credit for matching ANY reference |
| **Neural/Semantic (ROUGE, BERTScore, COMET, etc.)** | Compute against each reference individually; take the **maximum** score |

---

## Changes Implemented

### 1. BLEU (Bilingual Evaluation Understudy)

**Previous implementation:**
```python
bleu = sentence_bleu([ref_tokens], hyp_tokens, weights=weights, ...)
# Called separately for each reference, then averaged
```

**Updated implementation:**
```python
ref_tokens_list = [word_tokenize(ref.lower()) for ref in references]
bleu = sentence_bleu(ref_tokens_list, hyp_tokens, weights=weights, ...)
# All references passed at once; BLEU credits n-grams found in ANY reference
```

**Additional fix:** BLEU-3 weights corrected from `(0.33, 0.33, 0.33, 0)` (sum = 0.99) to `(1/3, 1/3, 1/3, 0)` (sum = 1.0).

### 2. chrF (Character n-gram F-score)

**Previous implementation:**
```python
result = chrf_scorer.sentence_score(hypothesis, [reference])
# Called separately for each reference, then averaged
```

**Updated implementation:**
```python
result = chrf_scorer.sentence_score(hypothesis, references)
# All references passed at once; sacrebleu handles multi-reference natively
```

### 3. ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

**Previous implementation:**
```python
rouge_scores = scorer.score(reference, hypothesis)
# Called separately for each reference, then averaged
```

**Updated implementation:**
```python
for reference in references:
    rouge_scores = scorer.score(reference, hypothesis)
    # Track best score per metric
best = max(ref_scores, key=lambda x: x['fmeasure'])
# Return maximum F-measure across all references
```

**Additional fix:** Metric naming corrected from `ROUGE-ROUGE1` to `ROUGE-1`, etc.

### 4. BERTScore

**Previous implementation:**
```python
P, R, F1 = bert_score.score([hypothesis], [reference], ...)
# Called separately for each reference, then averaged
```

**Updated implementation:**
```python
for reference in references:
    P, R, F1 = bert_score.score([hypothesis], [reference], ...)
    if F1 > best_f1:
        best_f1 = F1
# Return maximum F1 across all references
```

### 5. SentenceBERT (Semantic Similarity)

**Previous implementation:**
```python
embeddings = model.encode([hypothesis, reference])
similarity = cosine_similarity(embeddings[0], embeddings[1])
# Called separately for each reference, then averaged
```

**Updated implementation:**
```python
all_texts = [hypothesis] + references
embeddings = model.encode(all_texts)
for ref_embedding in embeddings[1:]:
    similarity = cosine_similarity(embeddings[0], ref_embedding)
    best_similarity = max(best_similarity, similarity)
# Return maximum similarity across all references
```

### 6. COMET (Crosslingual Optimized Metric for Evaluation of Translation)

**Previous implementation:**
```python
data = [{'src': source, 'mt': hypothesis, 'ref': reference}]
output = model.predict(data, ...)
# Called separately for each reference, then averaged
```

**Updated implementation:**
```python
for reference in references:
    data = [{'src': source, 'mt': hypothesis, 'ref': reference}]
    output = model.predict(data, ...)
    best_score = max(best_score, output['scores'][0])
# Return maximum score across all references (per Unbabel's recommendation)
```

### 7. BLEURT

Updated to follow the same max-across-references pattern as other neural metrics.

---

## Data Structure Changes

### ChunkEvaluation Class

**Previous structure:**
```python
@dataclass
class ChunkEvaluation:
    chunk_id: str
    model_name: str
    reference_id: str  # e.g., "ref1", "ref2"
    scores: List[EvaluationScore]
```

**Updated structure:**
```python
@dataclass
class ChunkEvaluation:
    chunk_id: str
    model_name: str
    scores: List[EvaluationScore]  # Multi-reference scores
    per_reference_scores: Dict  # Individual ref breakdowns preserved
```

### Output JSON Structure

The evaluation output now includes:

```json
{
  "methodology": "multi-reference",
  "methodology_details": {
    "bleu": "multi-reference (n-grams matched against any reference)",
    "chrf": "multi-reference (native support)",
    "rouge": "max across references",
    "bertscore": "max across references",
    "sentencebert": "max across references",
    "comet": "max across references"
  },
  "by_model": { ... },
  "by_metric": { ... },
  "by_reference": { ... },  // Per-reference breakdown preserved
  "detailed_scores": [
    {
      "chunk_id": "1",
      "model_name": "claude",
      "scores": { ... },  // Multi-reference scores
      "per_reference_scores": {
        "ref1": { ... },  // Individual scores vs ref1
        "ref2": { ... }   // Individual scores vs ref2
      }
    }
  ]
}
```

---

## Implications for Results

### Score Changes

With the updated methodology, scores are expected to be **higher** than the previous averaged approach because:

1. Multi-reference BLEU/chrF credit n-grams that match ANY reference
2. Max-based aggregation for neural metrics selects the best-matching reference

This is the correct behavior: a translation that matches one expert reference well should not be penalized for differing from another expert's stylistic choices.

### Comparability

- **Internal comparisons** (between models) remain valid and meaningful
- **External comparisons** to published benchmarks are now possible, as the methodology aligns with standard practice
- **Previous results** have been archived in `output/archive_2026-01-15_pre_multiref/`

### Per-Reference Analysis

The per-reference breakdown is preserved in the output data, enabling continued analysis of:
- Which reference each model's translations align with more closely
- Whether one reference is systematically harder to match
- Stylistic tendencies of different translation models

---

## Files Modified

| File | Changes |
|------|---------|
| `src/evaluator.py` | All metric functions updated for multi-reference; data structures revised |
| `src/reporter.py` | Updated to display methodology and handle new output structure |

## Files Created

| File | Purpose |
|------|---------|
| `documents/METRICS_UPDATE_REPORT.md` | This report |

## Files Archived

| Original Location | Archive Location |
|-------------------|------------------|
| `output/evaluations/*.json` | `output/archive_2026-01-15_pre_multiref/` |
| `output/reports/*` | `output/archive_2026-01-15_pre_multiref/` |

---

## References

1. Papineni, K., et al. (2002). "BLEU: a Method for Automatic Evaluation of Machine Translation." ACL.
2. Popović, M. (2015). "chrF: character n-gram F-score for automatic MT evaluation." WMT.
3. Lin, C.-Y. (2004). "ROUGE: A Package for Automatic Evaluation of Summaries." ACL Workshop.
4. Zhang, T., et al. (2020). "BERTScore: Evaluating Text Generation with BERT." ICLR.
5. Rei, R., et al. (2020). "COMET: A Neural Framework for MT Evaluation." EMNLP.
6. Reimers, N., & Gurevych, I. (2019). "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." EMNLP.

---

## Appendix: Metric Descriptions

### BLEU (Bilingual Evaluation Understudy)
Measures n-gram precision between candidate and reference translations. BLEU-1 through BLEU-4 weight unigrams through 4-grams respectively. Standard in MT evaluation since 2002.

### chrF (Character n-gram F-score)
Character-level metric that computes F-score over character n-grams. More robust to morphological variation than word-level metrics.

### ROUGE (Recall-Oriented Understudy for Gisting Evaluation)
Originally designed for summarization evaluation. ROUGE-1/2 measure unigram/bigram overlap; ROUGE-L measures longest common subsequence.

### BERTScore
Uses contextual embeddings from BERT to compute token-level similarity. More semantically aware than lexical metrics.

### SentenceBERT
Computes sentence-level embeddings and measures cosine similarity. Captures overall semantic similarity rather than token-level matching.

### COMET (Crosslingual Optimized Metric for Evaluation of Translation)
Neural metric trained on human quality judgments. Requires source text in addition to hypothesis and reference. Currently considered state-of-the-art for correlation with human evaluation.
