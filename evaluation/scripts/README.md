# Evaluation Scripts

This folder contains the programs that do the actual work.

---

## The Scripts

### `translator.py` - Generate AI Translations

**What it does:** Takes your Greek text and translates it using GPT-5, Claude, and Gemini.

**How to use:**
```bash
python3 translator.py \
    --input ../source_texts/greek/my_passage.txt \
    --output ../translations/
```

**Output:** A JSON file with all three translations

**Time:** 30-60 seconds per passage

---

### `translation_evaluator.py` - Compare Translations

**What it does:** Compares the AI translations to your gold standard and scores them.

**How to use:**
```bash
python3 translation_evaluator.py \
    ../translations/my_passage_*.json \
    ../source_texts/gold_standards/my_passage.json
```

**Output:** 
- Scores shown on screen
- Full results saved to `../outputs/`

**Time:** 10-30 seconds per passage

---

### `statistical_tests.py` - Statistical Analysis

**What it does:** Calculates p-values and confidence intervals for model comparisons.

**When to use:** Only after you have 30+ passages

**How to use:**
```bash
python3 statistical_tests.py ../outputs/evaluation_results_*.json
```

**Note:** With fewer than 30 passages, statistical tests aren't meaningful.

---

### `prepare_texts.py` - Parse Text Files

**What it does:** Converts a text file with Greek + English into separate JSON files.

**How to use:**
```bash
python3 prepare_texts.py ../source_texts/greek_and_translation.txt
```

**When to use:** If you have paired Greek/English texts you want to split up.

---

## Quick Reference

**Most common workflow:**

```bash
# 1. Generate translations
python3 translator.py \
    --input ../source_texts/greek/passage.txt \
    --output ../translations/

# 2. Evaluate
python3 translation_evaluator.py \
    ../translations/passage_*.json \
    ../source_texts/gold_standards/passage.json

# 3. View results
cat ../outputs/evaluation_results_*.json
```

---

## Troubleshooting

### "No module named X"
```bash
cd ..
pip install -r requirements.txt
```

### "API key not found"
The translator needs API keys. See the main project README for setup.

### "No gold standard for chunk X"
Make sure your gold standard JSON has the right `chunk_id` field.

---

## For Developers

### Code Structure

**translator.py:**
- Uses the main project's `main_translator.py` 
- Supports OpenAI GPT-5, Anthropic Claude 4.1, Google Gemini 2.5 Pro
- Parallel translation execution
- Automatic retry on errors

**translation_evaluator.py:**
- 12 NLP metrics (ROUGE, BLEU, METEOR, chrF, SentenceBERT, BERTScore)
- Automatic metric weighting
- JSON + console output
- Full transparency warnings

**statistical_tests.py:**
- Paired t-tests
- Wilcoxon signed-rank tests
- Bootstrap confidence intervals
- Effect size calculations

### Adding New Metrics

Edit `translation_evaluator.py`:

1. Add metric calculation function (e.g., `evaluate_my_metric()`)
2. Call it in `evaluate_single_pair()`
3. Results automatically included in output

See existing metrics as templates.

---

## Technical Details

See the main `AUDIT_REPORT.md` for:
- Metric implementations and validation
- Statistical methodology
- Known limitations
- Best practices

---

**For basic use, you only need `translator.py` and `translation_evaluator.py`!**
