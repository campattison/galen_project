# Ancient Greek Translation Evaluator

**Evaluate how well AI models translate Ancient Greek texts.**

This tool compares translations from GPT-5, Claude 4.1, and Gemini 2.5 Pro against professional scholarly translations to see which AI performs best.

---

## 📋 Quick Summary

**What it does:**
1. Takes an Ancient Greek passage
2. Translates it with three leading AI models
3. Compares AI translations to a reference scholarly translation
4. Scores each AI using 12 different metrics
5. Shows you which AI translated best

**What you need:**
- Ancient Greek text
- A professional scholarly translation (called a "gold standard")
- Python installed on your computer

**Time required:**
- Setup: 10 minutes (first time only)
- Per passage: 2-3 minutes

---

## 🚀 Getting Started

### Step 1: Install (First Time Only)

```bash
# Navigate to the evaluation folder
cd evaluation

# Install required software
pip install -r requirements.txt

# Setup the directory structure
./setup_structure.sh
```

### Step 2: Add Your Greek Text

Create a file with your Ancient Greek passage:

```bash
# Create a text file in the greek/ folder
cat > source_texts/greek/my_passage.txt
# Paste your Greek text, then press Ctrl+D
```

### Step 3: Add the Reference Translation

Create a JSON file with the professional translation:

```bash
cat > source_texts/gold_standards/my_passage.json << 'EOF'
[{
  "chunk_id": "1",
  "passage_name": "Title of Passage",
  "greek_text": "Your Greek text here...",
  "translation": "Professional English translation here...",
  "translator": "Scholar's Name (Year)",
  "edition": "Which critical edition you used",
  "publication": "Publisher, book title, etc."
}]
EOF
```

**Important:** The reference translation should be from a recognized scholar or academic press. See `source_texts/README.md` for guidance.

### Step 4: Generate AI Translations

```bash
python3 scripts/translator.py \
    --input source_texts/greek/my_passage.txt \
    --output translations/ \
    --chunking medium
```

This will translate your Greek text using GPT-5, Claude, and Gemini. It takes about 30-60 seconds.

### Step 5: Run the Evaluation

```bash
python3 scripts/translation_evaluator.py \
    translations/my_passage_*.json \
    source_texts/gold_standards/my_passage.json
```

Results appear on screen and save to `outputs/`.

---

## 📖 Understanding the Results

### What You'll See

The evaluation shows three things:

#### 1. Important Warnings ⚠️

```
📊 Metric Averaging:
  Rankings use a simple average. Different metrics might matter more for
  different purposes.

📈 Sample Size:
  Based on 1 passage. You need at least 30 passages for reliable conclusions.

📚 Reference Translations:
  Using one reference. Multiple references are better but harder to get.
```

**Pay attention to these!** They explain limitations of the evaluation.

#### 2. Side-by-Side Comparison 📖

You'll see the actual translations compared:

```
Source (Greek):
  Ὅτι μὲν ἐκ θερμοῦ καὶ ψυχροῦ...

Reference (Scholar Name):
  That the bodies of animals consist of a mixture...

GPT-5:
  That the bodies of animals are blended...

Claude:
  That the bodies of living creatures are compounded...

Gemini:
  That the bodies of animals are composed...
```

This lets you see the **actual differences** between translations.

#### 3. Numerical Scores 📊

```
🏆 Model Rankings:
  1. GEMINI: 0.5828
  2. CLAUDE: 0.5676
  3. OPENAI: 0.5544
```

**What the numbers mean:**
- **0.9-1.0**: Nearly identical to reference
- **0.7-0.9**: Very similar, minor differences
- **0.5-0.7**: Moderately similar
- **Below 0.5**: Significantly different

**Important:** Even professional human translators often score 0.6-0.8 when compared to each other, so don't expect perfect scores!

---

## ⚠️ Important Limitations

### You Need Many Passages

**Problem:** With just 1-3 passages, results are unreliable.

**Why:** Different passages favor different models. Rankings can completely reverse with different passages.

**Solution:** Evaluate at least 30 passages before drawing any conclusions.

**Example from our tests:**
- September evaluation (5 passages): OpenAI wins
- October evaluation (1 passage): Gemini wins
- These contradict each other!

### Single Reference Translation

**Problem:** You're comparing against ONE scholarly translation.

**Why this matters:** There are many valid ways to translate the same Greek text. An AI might produce a correct translation that differs from your reference.

**Better:** Use 2-3 different scholarly translations as references if possible.

### Metric Weighting

**Problem:** The ranking averages 12 different metrics equally.

**Why this matters:** Some metrics might matter more than others for your purpose. Word choice? Sentence structure? Overall meaning?

**Better:** Decide which metrics matter most for your use case.

---

## 📁 What's Where

```
evaluation/
├── source_texts/
│   ├── greek/              Your Ancient Greek passages
│   └── gold_standards/     Professional reference translations
│
├── translations/           AI translations (generated automatically)
│
├── outputs/               Evaluation results
│
├── scripts/               The evaluation programs
│   ├── translator.py      Generates AI translations
│   └── translation_evaluator.py  Compares to gold standard
│
├── README.md             This file - start here!
├── WORKFLOW.md           Detailed step-by-step guide
└── AUDIT_REPORT.md       Technical evaluation of methodology
```

---

## 📚 Example: Complete Workflow

Here's a real example with a Galen passage:

```bash
# 1. Your Greek text is in:
source_texts/greek/on_mixtures_1.1.txt

# 2. Your reference translation is in:
source_texts/gold_standards/on_mixtures_1.1.json

# 3. Generate AI translations:
python3 scripts/translator.py \
    --input source_texts/greek/on_mixtures_1.1.txt \
    --output translations/

# 4. Evaluate:
python3 scripts/translation_evaluator.py \
    translations/on_mixtures_1.1_*.json \
    source_texts/gold_standards/on_mixtures_1.1.json

# 5. View results:
cat outputs/evaluation_results_*.json
```

---

## ❓ Common Questions

### How many passages do I need?

**Minimum:** 30 passages for basic statistical validity  
**Better:** 50-100 passages for reliable conclusions  
**Current examples:** Only 1-3 passages (too few!)

### Which AI is best?

**Can't say yet!** Current sample sizes are too small. Need 30+ passages first.

### Can I evaluate other models?

Yes, but you'll need to modify `scripts/translator.py`. The current version supports GPT-5, Claude 4.1, and Gemini 2.5 Pro.

### What if I don't have a reference translation?

You need at least one scholarly reference translation for each passage. Look for:
- Academic press translations (Cambridge, Oxford, Loeb Classical Library)
- Peer-reviewed publications
- Recognized Classical scholars

See `source_texts/README.md` for detailed guidance.

### Can I use my own translation as the reference?

Only if you're a qualified expert. The "gold standard" should be from recognized scholarly sources so the evaluation is objective and credible.

### Where can I find scholarly translations?

- Loeb Classical Library
- Cambridge Classical Texts and Commentaries
- Oxford Classical Texts
- University press publications
- Check with a Classics department for recommendations

---

## 🎓 For Academic Use

If you're using this for research or publication:

1. **Read the technical audit:** See `AUDIT_REPORT.md` for detailed methodology critique
2. **Sample size matters:** You need 30+ passages minimum
3. **Document everything:** Full citations for all gold standards
4. **Add human evaluation:** Have experts evaluate a subset
5. **Run statistical tests:** Use `scripts/statistical_tests.py` (once you have enough data)

See `WORKFLOW.md` for detailed academic workflow.

---

## 🛠️ Troubleshooting

### "No module named X"
```bash
pip install -r requirements.txt
```

### "No gold standard for chunk X"
Make sure the `chunk_id` in your gold standard JSON matches the passage ID from the translator.

### "sacrebleu not available"
```bash
pip install sacrebleu
```
(Or the evaluation will use a fallback implementation and warn you)

### Models aren't ranking as expected
This is normal with small sample sizes! Need 30+ passages for reliable rankings.

---

## 📞 Need Help?

- **Basic usage:** Read `WORKFLOW.md`
- **Gold standards:** Read `source_texts/README.md`
- **Technical details:** Read `AUDIT_REPORT.md`
- **Script documentation:** Read `scripts/README.md`

---

## 📊 What The Evaluation Measures

The tool uses 12 different metrics to compare translations:

| Category | Metrics | What They Measure |
|----------|---------|-------------------|
| **Word Overlap** | ROUGE, BLEU | How many words/phrases match? |
| **Meaning** | METEOR | Are synonyms and word stems considered? |
| **Characters** | chrF | Character-level similarity |
| **Semantics** | SentenceBERT, BERTScore | Overall meaning similarity (AI-based) |

All 12 scores are combined into one overall ranking.

**Why 12 metrics?** Different metrics capture different aspects of translation quality. Using multiple metrics gives a more complete picture than any single score.

---

## ✅ Quick Checklist

Before claiming "Model X is better":

- [ ] Evaluated at least 30 passages
- [ ] Used high-quality scholarly reference translations
- [ ] Documented all reference sources with full citations
- [ ] Reviewed actual translation examples (not just scores)
- [ ] Considered having human experts evaluate a subset
- [ ] Run statistical significance tests
- [ ] Read the methodology warnings

**If you haven't done these, your results are preliminary at best.**

---

## 📄 License & Usage

This evaluation framework is for research and educational use. 

**Important:** If you use this work:
- Cite any gold standard translations appropriately
- Acknowledge the limitations (especially sample size)
- Share your methodology openly
- Consider making your evaluation data available to others

---

**Ready to start?** Follow the Getting Started section above, then see `WORKFLOW.md` for detailed instructions!
