# 👋 Welcome to the Ancient Greek Translation Evaluator

**This tool helps you see which AI translates Ancient Greek best.**

---

## ⚡ Ultra-Quick Start

```bash
# 1. Install (first time only)
pip install -r requirements.txt
./setup_structure.sh

# 2. Put your Greek text here:
source_texts/greek/my_passage.txt

# 3. Put a scholarly translation here:
source_texts/gold_standards/my_passage.json

# 4. Run translation
python3 scripts/translator.py \
    --input source_texts/greek/my_passage.txt \
    --output translations/

# 5. Run evaluation  
python3 scripts/translation_evaluator.py \
    translations/my_passage_*.json \
    source_texts/gold_standards/my_passage.json
```

**Done!** Results appear on screen and save to `outputs/`.

---

## 📚 Where to Read Next

**New to this?**  
→ Read **`README.md`** - Written in plain English, explains everything

**Want step-by-step details?**  
→ Read **`WORKFLOW.md`** - Detailed walkthrough with examples

**Need to know if this is rigorous?**  
→ Read **`AUDIT_REPORT.md`** - Technical methodology review

**Just want a quick overview?**  
→ Read **`SUMMARY.md`** - One-page summary

**Lost and need to find something?**  
→ Read **`DIRECTORY_GUIDE.txt`** - Map of what's where

---

## ⚠️ Most Important Things to Know

1. **You need 30+ passages for reliable results**  
   (Currently only have 1-3 examples)

2. **Use professional scholarly translations as references**  
   (Not your own translations unless you're an expert)

3. **Check the warnings in every report**  
   (They explain what the scores mean and don't mean)

4. **Scores 0.6-0.8 are normal**  
   (Even experts differ; perfect scores are rare)

5. **Multiple metrics are used**  
   (12 different ways of measuring translation quality)

---

## 🎯 What This Actually Does

```
Your Greek Text
      ↓
   Translate with GPT-5, Claude, Gemini
      ↓
   Compare to scholarly reference
      ↓
   Score using 12 metrics
      ↓
   Show which AI did best
```

**Time:** 2-3 minutes per passage  
**Cost:** Minimal (a few cents per passage in API calls)  
**Output:** Scores + side-by-side comparison you can read

---

## 📂 What's in This Folder

```
evaluation/
├── README.md ← Full guide (start here!)
├── SUMMARY.md ← Quick overview
├── WORKFLOW.md ← Detailed steps
├── AUDIT_REPORT.md ← Technical review
├── source_texts/ ← Your Greek + references
├── translations/ ← AI translations (auto-generated)
├── outputs/ ← Results
└── scripts/ ← The programs
```

---

## ❓ Quick Questions

**Q: Do I need to know Python?**  
A: No, just copy the commands shown in README.md

**Q: Do I need API keys?**  
A: Yes, for OpenAI, Anthropic, and Google (see main project README)

**Q: How much does it cost?**  
A: About $0.02-0.10 per passage (varies by length)

**Q: Can I trust the results?**  
A: With 1-3 passages? No. With 30+? Yes. See AUDIT_REPORT.md.

**Q: Which AI is best overall?**  
A: Can't say yet - need more data!

---

## 🚀 Ready to Start?

**Go read [`README.md`](README.md) now!**

It explains:
- How to install
- How to add your passages
- How to run evaluations
- How to read the results
- What the limitations are
- Where to get help

Everything is written in plain language.

---

*This is a research tool. Results are preliminary until you have 30+ passages. Always check the methodology warnings!*

