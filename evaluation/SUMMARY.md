# Evaluation Framework Summary

**Last Updated:** October 1, 2025

---

## What This Is

A tool to evaluate how well AI models (GPT-5, Claude 4.1, Gemini 2.5 Pro) translate Ancient Greek by comparing their translations to professional scholarly translations.

---

## Current Status

### ✅ What Works
- Clean, transparent evaluation pipeline
- 12 different metrics for scoring translations
- Automatic warnings about methodology limitations
- Side-by-side translation comparisons
- Self-contained directory structure

### ⚠️ What's Needed
- **More passages** (have 3, need 30+ for valid conclusions)
- Complete citations for reference translations
- Human expert evaluation
- Statistical significance testing (requires more passages first)

---

## Documentation Guide

### Start Here 👉
**`README.md`** - Non-technical guide for using the evaluation tool

### For Detailed Instructions
**`WORKFLOW.md`** - Step-by-step workflow from Greek text to results

### For Technical Review
**`AUDIT_REPORT.md`** - Independent methodology audit with checklist

### For Specific Topics
- **`source_texts/README.md`** - Gold standard requirements and provenance
- **`scripts/README.md`** - What each script does
- **`outputs/`** - Evaluation results are saved here

---

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Translate
python3 scripts/translator.py \
    --input source_texts/greek/passage.txt \
    --output translations/

# 3. Evaluate
python3 scripts/translation_evaluator.py \
    translations/passage_*.json \
    source_texts/gold_standards/passage.json
```

---

## File Organization

```
evaluation/
├── 📘 Documentation (Read these!)
│   ├── README.md          Start here
│   ├── WORKFLOW.md        Detailed guide
│   └── AUDIT_REPORT.md    Technical audit
│
├── 📂 Your Data
│   ├── source_texts/
│   │   ├── greek/         Your Greek texts
│   │   └── gold_standards/ Reference translations
│   ├── translations/      AI translations (generated)
│   └── outputs/          Results
│
└── 🛠️ Programs
    └── scripts/          The actual evaluation programs
```

---

## Important Reminders

1. **Sample size matters**: Need 30+ passages for reliable results
2. **Gold standards need citations**: Document translator credentials
3. **Multiple metrics**: Don't rely on just one score
4. **Human evaluation**: Automatic metrics have limitations
5. **Check the warnings**: Read the methodology notes in every report

---

## Next Steps

**To improve this evaluation:**

1. **Priority 1:** Gather 30+ passages with gold standards
2. **Priority 2:** Document full citations for all references  
3. **Priority 3:** Have experts evaluate a subset
4. **Priority 4:** Run statistical tests

See `AUDIT_REPORT.md` for detailed recommendations.

---

**Questions?** Check README.md first, then WORKFLOW.md for details.

