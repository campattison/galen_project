# Evaluation Workflow Guide

This document explains the complete workflow for evaluating AI translations of Ancient Greek texts, from source text to final evaluation report.

## Overview

```
Greek Text → AI Translation → Gold Standard Comparison → Evaluation Report
```

All necessary components are self-contained within the `evaluation/` folder.

---

## Directory Structure

```
evaluation/
├── source_texts/              # INPUT: Greek texts and gold standards
│   ├── greek/                 # Original Ancient Greek passages
│   └── gold_standards/        # Reference translations (JSON)
│
├── translations/              # INTERMEDIATE: AI-generated translations
│   └── [timestamp]_*.json     # Translation outputs
│
├── outputs/                   # OUTPUT: Evaluation results
│   └── evaluation_results_*.json
│
├── scripts/                   # TOOLS
│   ├── translator.py          # Generate AI translations
│   ├── translation_evaluator.py  # Evaluate translations
│   └── statistical_tests.py   # Statistical analysis
│
└── WORKFLOW.md               # This file
```

---

## Complete Workflow

### Step 1: Prepare Source Text

**Input:** Ancient Greek passage

**Location:** `source_texts/greek/passage_name.txt`

**Example:**
```bash
cat > source_texts/greek/on_mixtures_1.1.txt << 'EOF'
Ὅτι μὲν ἐκ θερμοῦ καὶ ψυχροῦ καὶ ξηροῦ καὶ ὑγροῦ τὰ τῶν ζῴων σώματα κέκραται...
EOF
```

---

### Step 2: Create Gold Standard

**Input:** Professional scholarly translation with full metadata

**Location:** `source_texts/gold_standards/passage_name.json`

**Template:**
```json
[
  {
    "chunk_id": "1",
    "passage_name": "On Mixtures 1.1",
    "greek_text": "Ὅτι μὲν ἐκ θερμοῦ...",
    "translation": "That the bodies of animals consist of a mixture...",
    "translator": "P. N. Singer and Philip van der Eijk (2019)",
    "edition": "Kühn I 509–10, Helmreich",
    "publication": "Galen: Psychological Writings, Cambridge University Press",
    "isbn": "978-1-107-05493-4",
    "translation_philosophy": "scholarly literal with notes",
    "word_count_greek": 217,
    "word_count_english": 265
  }
]
```

**Critical:** Include full provenance (see `source_texts/README.md`)

---

### Step 3: Generate AI Translations

**Script:** `scripts/translator.py`

**Input:** Greek text from Step 1

**Output:** `translations/[timestamp]_[passage].json`

**Command:**
```bash
cd evaluation

# Translate a single passage
python scripts/translator.py \
    --input source_texts/greek/on_mixtures_1.1.txt \
    --output translations/ \
    --chunking medium

# Or translate all passages in greek/ folder
python scripts/translator.py \
    --input-dir source_texts/greek/ \
    --output translations/ \
    --chunking medium
```

**Output file structure:**
```json
{
  "metadata": {
    "source_file": "source_texts/greek/on_mixtures_1.1.txt",
    "processed_at": "2025-10-01T09:13:53",
    "models_used": ["openai", "claude", "gemini"]
  },
  "chunks": [
    {
      "id": "1",
      "content": "Ὅτι μὲν ἐκ θερμοῦ...",
      "openai_translation": "That the bodies of animals...",
      "claude_translation": "That the bodies of living creatures...",
      "gemini_translation": "That the bodies of animals..."
    }
  ]
}
```

---

### Step 4: Run Evaluation

**Script:** `scripts/translation_evaluator.py`

**Input:**
- Translations from Step 3
- Gold standard from Step 2

**Output:** `outputs/evaluation_results_[timestamp].json`

**Command:**
```bash
python scripts/translation_evaluator.py \
    translations/[translation_file].json \
    source_texts/gold_standards/[gold_standard].json \
    -o outputs/evaluation_results.json
```

**What it does:**
1. Loads AI translations and gold standard
2. Compares each AI translation to gold standard using 12 metrics:
   - ROUGE (1, 2, L, LSum)
   - BLEU (1, 2, 3, 4)
   - METEOR
   - chrF
   - SentenceBERT
   - BERTScore
3. Generates comprehensive evaluation report

---

### Step 5: Review Results

**Output file:** `outputs/evaluation_results_[timestamp].json`

**Contents:**
```json
{
  "methodology_notes": {
    "metric_averaging": "WARNING about equal weighting",
    "sample_size_warning": "Based on N passages",
    "single_reference": "Single reference limitation"
  },
  "translation_examples": [
    {
      "chunk_id": "1",
      "source_text": "Ὅτι μὲν ἐκ θερμοῦ...",
      "reference_translation": "That the bodies...",
      "reference_metadata": {
        "translator": "Singer and van der Eijk (2019)"
      },
      "candidate_translations": {
        "openai": "Translation...",
        "claude": "Translation...",
        "gemini": "Translation..."
      }
    }
  ],
  "model_rankings": [
    ["gemini", 0.583],
    ["claude", 0.568],
    ["openai", 0.554]
  ],
  "detailed_scores": { ... }
}
```

**View results:**
```bash
# Pretty print JSON
cat outputs/evaluation_results_[timestamp].json | jq

# Print human-readable summary (already shown during evaluation)
python scripts/translation_evaluator.py \
    translations/[file].json \
    source_texts/gold_standards/[file].json
```

---

### Step 6: Statistical Analysis (Optional)

**Script:** `scripts/statistical_tests.py`

**Requirement:** Minimum n=30 passages for validity

**Command:**
```bash
python scripts/statistical_tests.py \
    outputs/evaluation_results_[timestamp].json \
    -o outputs/statistical_results.json
```

**What it does:**
- Paired t-tests between models
- Wilcoxon signed-rank tests
- Bootstrap confidence intervals
- Effect size calculations

**Note:** Only meaningful with adequate sample size (n≥30)

---

## Example: Complete Evaluation

```bash
# 1. Navigate to evaluation folder
cd evaluation

# 2. Ensure Greek text exists
cat source_texts/greek/on_mixtures_1.1.txt

# 3. Ensure gold standard exists with full provenance
cat source_texts/gold_standards/on_mixtures_1.1.json

# 4. Generate AI translations
python scripts/translator.py \
    --input source_texts/greek/on_mixtures_1.1.txt \
    --output translations/ \
    --chunking medium

# Output: translations/on_mixtures_1.1_medium_20251001_143022.json

# 5. Run evaluation
python scripts/translation_evaluator.py \
    translations/on_mixtures_1.1_medium_20251001_143022.json \
    source_texts/gold_standards/on_mixtures_1.1.json

# Output: 
# - Console: Summary with warnings and translation examples
# - File: outputs/evaluation_results_20251001_143045.json

# 6. Review results
cat outputs/evaluation_results_20251001_143045.json | jq .methodology_notes
cat outputs/evaluation_results_20251001_143045.json | jq .translation_examples[0]
cat outputs/evaluation_results_20251001_143045.json | jq .model_rankings
```

---

## Translation Process Transparency

### What Gets Translated

**Source:** `source_texts/greek/[passage].txt` - Plain Ancient Greek text

### How Translation Works

**Script:** `scripts/translator.py` uses these models with identical prompts:

```python
"""You are an expert translator of Ancient Greek, specializing in classical texts 
including philosophical, medical, and literary works.

Please translate this Ancient Greek text:

**Text {chunk_id}:**
{text}

Guidelines:
- Provide a clear, accurate English translation
- Maintain the meaning, structure, and style of the original Greek
- Use appropriate terminology for the subject matter
- Preserve the logical flow and argumentation
- Include brief explanatory notes in [brackets] for technical terms if helpful
- Aim for accuracy while ensuring natural English

Translate only the Greek text provided. Do not add commentary beyond the translation itself."""
```

**Models:**
- OpenAI: `gpt-5` (via Responses API)
- Anthropic: `claude-sonnet-4-5-20250929`
- Google: `gemini-2.5-pro`

**Parameters:**
- Temperature: 0.3 (low variability)
- Max tokens: 8000 (unrestricted)
- No artificial length limits

### Where Translations Are Stored

**Primary location:** `evaluation/translations/`

**Backup location:** `../outputs/` (main project folder)

**Format:** JSON with full metadata

---

## Evaluation Report Components

### 1. Methodology Notes (Top of Report)

Warnings about:
- Metric averaging assumptions
- Sample size limitations
- Single reference translation

### 2. Translation Examples

Shows first 3 passages:
- Source Greek text
- Reference translation (with attribution)
- All AI translations side-by-side

### 3. Evaluation Results

- Overall model rankings
- Per-metric scores
- Statistical details (mean, std, min, max)

### 4. Raw Data

Full JSON output includes:
- All individual scores
- Implementation details (which chrF used)
- Complete translation examples
- Source file references

---

## Quality Control Checklist

Before running evaluation:

- [ ] Greek text is accurate and complete
- [ ] Gold standard has full bibliographic citation
- [ ] Translator credentials are documented
- [ ] Translation philosophy is specified
- [ ] JSON validates (use `python -m json.tool file.json`)

After running evaluation:

- [ ] Check methodology warnings in output
- [ ] Review translation examples for quality
- [ ] Verify chrF implementation (should be "sacrebleu")
- [ ] Note sample size in interpretation
- [ ] Consider running statistical tests (if n≥30)

---

## Troubleshooting

### "No gold standard for chunk X"
- Ensure chunk IDs match between translation and gold standard files
- Check JSON structure in both files

### "sacrebleu not available"
- Install: `pip install sacrebleu>=2.3.0`
- Or accept fallback chrF implementation (marked in output)

### "Failed to read file"
- Check file paths are correct
- Ensure files are UTF-8 encoded
- Validate JSON structure

### Low/contradictory scores
- Check sample size (need n≥30 for reliability)
- Review translation examples for quality
- Verify gold standard quality
- Consider passage difficulty

---

## Best Practices

### 1. Sample Size
- Minimum 30 passages for basic validity
- 50-100 passages for publication quality
- Include diverse text types and difficulty levels

### 2. Gold Standards
- Use peer-reviewed scholarly translations
- Document full provenance
- Consider multiple references per passage

### 3. Interpretation
- Always report confidence intervals (when n≥30)
- Note sample size limitations
- Acknowledge metric averaging assumptions
- Don't over-interpret small differences

### 4. Transparency
- Include translation examples in reports
- Document all parameters and choices
- Make data available for review
- Report negative results

---

## Quick Reference

```bash
# Full workflow in one go
cd evaluation

# Generate translations
python scripts/translator.py \
    --input-dir source_texts/greek/ \
    --output translations/

# Evaluate (run for each passage)
for gold in source_texts/gold_standards/*.json; do
    base=$(basename $gold .json)
    trans=$(ls -t translations/${base}*.json | head -1)
    python scripts/translation_evaluator.py "$trans" "$gold"
done

# View latest results
cat outputs/evaluation_results_*.json | jq .model_rankings
```

---

## Further Reading

- `source_texts/README.md` - Gold standard requirements
- `scripts/README.md` - Script documentation
- `AUDIT_REPORT.md` - Methodology critique
- `../README.md` - Main project overview

