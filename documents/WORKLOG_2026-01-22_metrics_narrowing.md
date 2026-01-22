# Worklog: Metrics Narrowing and Implementation

**Date:** January 22, 2026  
**Task:** Narrow evaluation metrics to recommended subset and implement missing metrics

---

## Background

Received guidance from colleague to narrow the metrics suite:

> "I'm thinking we will want: BLEU-4 (I don't think we need to report others), chrF++ (I don't think we need to report chrF), METEOR, ROUGE-L, BERTScore (I don't think we need to report SentenceBERT), COMET, and BLEURT."

## Previous State

The evaluator was reporting:
- BLEU-1, BLEU-2, BLEU-3, BLEU-4
- chrF (without word n-grams)
- ROUGE-1, ROUGE-2, ROUGE-L, ROUGE-Lsum
- BERTScore
- SentenceBERT
- COMET
- BLEURT (implemented but not tested)

**Missing:** METEOR

---

## Changes Implemented

### 1. Added METEOR Metric

Implemented `evaluate_meteor()` in `src/evaluator.py`:
- Uses NLTK's `meteor_score` function
- Natively supports multi-reference evaluation (takes the maximum)
- Incorporates stemming, synonyms via WordNet
- Downloads required NLTK data: `wordnet`, `omw-1.4`

```python
def evaluate_meteor(self, hypothesis: str, references: List[str]) -> List[EvaluationScore]:
    """Calculate METEOR score with multi-reference support."""
    from nltk.tokenize import word_tokenize
    meteor_score_func = self.metric_handlers['meteor']
    
    hyp_tokens = word_tokenize(hypothesis.lower())
    ref_tokens_list = [word_tokenize(ref.lower()) for ref in references]
    
    # METEOR natively handles multiple references and takes the max
    score = meteor_score_func(ref_tokens_list, hyp_tokens)
    return [EvaluationScore(metric_name='METEOR', score=score, ...)]
```

### 2. Upgraded chrF to chrF++

Changed chrF initialization to include word bigrams:

```python
# Before
self.metric_handlers['chrf'] = CHRF()

# After
self.metric_handlers['chrf'] = CHRF(word_order=2)  # chrF++ with word bigrams
```

chrF++ extends chrF by including word n-grams, providing better correlation with human judgments.

### 3. Narrowed BLEU to BLEU-4 Only

Removed BLEU-1, BLEU-2, BLEU-3. Now only reports BLEU-4:

```python
# Before: computed all 4 variants
weights_list = [(1.0,0,0,0), (0.5,0.5,0,0), (1/3,1/3,1/3,0), (0.25,0.25,0.25,0.25)]

# After: BLEU-4 only
weights = (0.25, 0.25, 0.25, 0.25)  # Equal weight for 1-4 grams
```

### 4. Narrowed ROUGE to ROUGE-L Only

Removed ROUGE-1, ROUGE-2, ROUGE-Lsum. Now only computes ROUGE-L:

```python
# Before
RougeScorer(['rouge1', 'rouge2', 'rougeL', 'rougeLsum'], ...)

# After
RougeScorer(['rougeL'], ...)
```

### 5. Removed SentenceBERT

- Deleted `evaluate_sentencebert()` method entirely
- Removed from `evaluate_single()` and `evaluate_per_reference()` calls
- Removed `sentence-transformers` from requirements.txt

### 6. Updated Default Metrics

```python
# Before
metrics = ['bleu', 'rouge', 'chrf', 'bertscore', 'sentencebert', 'comet']

# After
metrics = ['bleu', 'chrf', 'meteor', 'rouge', 'bertscore', 'comet']
```

---

## Environment Updates

### Python Upgrade

The virtual environment was built with Python 3.13, but the system only had Python 3.9.6. Installed Python 3.13 via Homebrew:

```bash
brew install python@3.13
```

Recreated the virtual environment:

```bash
rm -rf venv
/opt/homebrew/bin/python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### BLEURT Installation

BLEURT is not available via pip; must be installed from GitHub:

```bash
pip install git+https://github.com/google-research/bleurt.git
```

Downloaded BLEURT-20 checkpoint:

```bash
# Downloaded from https://storage.googleapis.com/bleurt-oss-21/BLEURT-20.zip
# Extracted to galen_eval/BLEURT-20/
```

### BLEURT macOS Issue

BLEURT has a TensorFlow threading issue on macOS (Apple Silicon):

```
libc++abi: terminating due to uncaught exception of type std::__1::system_error: 
mutex lock failed: Invalid argument
```

**Decision:** Excluded BLEURT from default metrics on macOS. Can be added on Linux systems.

---

## Files Modified

| File | Changes |
|------|---------|
| `src/evaluator.py` | Added METEOR, upgraded chrF→chrF++, narrowed BLEU/ROUGE, removed SentenceBERT |
| `pipeline.py` | Updated CLI metric choices and defaults |
| `requirements.txt` | Removed sentence-transformers, updated comments |

---

## Final Metrics Suite

| Metric | Type | Multi-Reference Approach | Status |
|--------|------|-------------------------|--------|
| **BLEU-4** | Lexical | Pass all refs; credit for matching ANY | ✓ Working |
| **chrF++** | Lexical | Native multi-ref support | ✓ Working |
| **METEOR** | Lexical | Native multi-ref (takes max) | ✓ Working |
| **ROUGE-L** | Lexical | Max across references | ✓ Working |
| **BERTScore** | Neural | Max across references | ✓ Working |
| **COMET** | Neural | Max across references | ✓ Working |
| **BLEURT** | Neural | Max across references | ⚠️ macOS issues |

---

## Test Results

```
Default metrics: ['bleu', 'chrf', 'meteor', 'rouge', 'bertscore', 'comet']

Evaluation results:
  BLEU-4: 0.5154
  chrF++: 0.7030
  METEOR: 0.8757
  ROUGE-L: 0.7692
  BERTScore: 0.9813
  COMET: 0.8910

✓ All requested metrics operational
```

---

## Usage

```bash
# Activate environment
cd galen_eval
source venv/bin/activate

# Run with default metrics (6 metrics, excludes BLEURT on macOS)
python pipeline.py input/your_file.txt

# Explicitly specify metrics
python pipeline.py input/your_file.txt --metrics bleu chrf meteor rouge bertscore comet

# On Linux, can add BLEURT
python pipeline.py input/your_file.txt --metrics bleu chrf meteor rouge bertscore comet bleurt
```

---

## Notes

1. **Dependency conflicts:** COMET requires numpy<2.0 and protobuf<5.0, but BLEURT/TensorFlow requires numpy 2.x and protobuf 6.x. Despite pip warnings, COMET functions correctly.

2. **BLEURT checkpoint:** Set `BLEURT_CHECKPOINT` environment variable if checkpoint is not in default location:
   ```bash
   export BLEURT_CHECKPOINT="/path/to/BLEURT-20"
   ```

3. **GPU acceleration:** Use `--gpu` flag for faster BERTScore and COMET evaluation on CUDA-enabled systems.

---

## Update: SacreBLEU Switch (January 22, 2026)

Following code review feedback, BLEU-4 implementation was switched from NLTK to SacreBLEU for improved reproducibility:

**Rationale:**
- SacreBLEU provides standardized tokenization
- Results are reproducible and comparable to published benchmarks
- Consistent with chrF++ (already using SacreBLEU)

**Change:**
```python
# Before (NLTK)
from nltk.translate.bleu_score import sentence_bleu
bleu = sentence_bleu(ref_tokens_list, hyp_tokens, weights=weights, smoothing_function=smoothing)

# After (SacreBLEU)
from sacrebleu.metrics import BLEU
bleu_scorer = BLEU(effective_order=True)
result = bleu_scorer.sentence_score(hypothesis, references)
score = result.score / 100  # Normalize to 0-1
```

**Impact:** BLEU scores are now slightly different due to different tokenization. Previous results archived to `output/archive_2026-01-22_pre_sacrebleu/`.
