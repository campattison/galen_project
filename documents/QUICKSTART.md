# Quick Start Guide

Get up and running with the Galen Translation Evaluation Pipeline in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- API keys for OpenAI, Anthropic (Claude), and Google (Gemini)

## Step 1: Run Setup Script

```bash
cd galen_eval
./setup.sh
```

This will:
- Create a virtual environment in `venv/`
- Install all dependencies
- Check for your API keys

**Manual setup (if you prefer):**
```bash
cd galen_eval
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Note: For the full suite of metrics including BLEURT and COMET, uncomment those lines in `requirements.txt` and install. These require downloading large models (~1-2GB).

## Step 2: Configure API Keys

The pipeline will automatically look for `.env` in your project root (recommended) or in `config/.env`.

**Option 1: Use project root .env (recommended)**
```bash
# Already exists in your repo! Just make sure it has your API keys
nano ../.env  # Edit the .env file one level up
```

**Option 2: Use local config/.env**
```bash
# Copy the example config
cp config/env.example config/.env

# Edit config/.env and add your API keys
nano config/.env
```

Make sure your `.env` file has these values:
```
OPENAI_API_KEY=sk-...your_key...
ANTHROPIC_API_KEY=sk-ant-...your_key...
GOOGLE_API_KEY=...your_key...
```

## Step 3: Prepare Your Input

The input file should have this structure:

```
Chunk 1

[Greek text paragraph]

[Reference translation 1]

[Reference translation 2]

Chunk 2

[Greek text paragraph]

[Reference translation 1]

[Reference translation 2]

...
```

Your `10_chunks.txt` file is already in the correct format! It's in the `input/` folder.

## Step 4: Run the Pipeline

**First, activate the virtual environment:**
```bash
source venv/bin/activate
```

**Then run the pipeline:**
```bash
python3 pipeline.py input/10_chunks_clean.txt
```

**When done:**
```bash
deactivate  # Exit the virtual environment
```

That's it! The pipeline will:
1. ✅ Parse your input (extract Greek text and references)
2. ✅ Translate with OpenAI, Claude, and Gemini
3. ✅ Evaluate against both reference translations
4. ✅ Generate comprehensive reports

## Step 5: View Results

After the pipeline completes, you'll find:

```
output/
├── translations/
│   └── 10_chunks_translations_TIMESTAMP.json
├── evaluations/
│   └── 10_chunks_evaluation_TIMESTAMP.json
└── reports/
    ├── 10_chunks_summary_TIMESTAMP.txt      # Quick overview
    ├── 10_chunks_detailed_TIMESTAMP.txt     # Full details with examples
    └── 10_chunks_scores_TIMESTAMP.csv       # Data for analysis
```

**View the summary report:**
```bash
cat output/reports/10_chunks_summary_*.txt
```

## Customization Options

**Remember to activate the virtual environment first:**
```bash
source venv/bin/activate
```

### Use specific models only
```bash
python3 pipeline.py input/10_chunks.txt --models openai claude
```

### Use fast metrics only (skip neural metrics)
```bash
python3 pipeline.py input/10_chunks.txt --metrics bleu rouge chrf
```

### Enable GPU for faster neural metrics
```bash
python3 pipeline.py input/10_chunks.txt --gpu
```

### Parallel translation (faster but more API load)
```bash
python3 pipeline.py input/10_chunks.txt --parallel
```

## Understanding the Results

### Overall Rankings
Shows which model performs best on average across all metrics:
```
🥇 1. GEMINI:  0.5435
🥈 2. CLAUDE:  0.5271
🥉 3. OPENAI:  0.5054
```

### Best Model Per Metric
Shows which model excels at each specific metric:
```
BLEU-4         → GEMINI     (0.2648)
chrF++         → GEMINI     (0.6621)
METEOR         → CLAUDE     (0.5234)
ROUGE-L        → CLAUDE     (0.6844)
BERTScore      → CLAUDE     (0.8654)
COMET          → GEMINI     (0.8910)
```

### Detailed Scores
Per-model, per-metric statistics with mean, standard deviation, min, and max.

## Troubleshooting

### "No models available"
- Check that your API keys are correctly set in your `.env` file (project root or `config/.env`)
- Make sure the keys don't have the placeholder text
- Make sure you activated the virtual environment: `source venv/bin/activate`

### "Module not found" errors
Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

Then reinstall if needed:
```bash
pip install -r requirements.txt
```

### "NLTK not available"
```bash
source venv/bin/activate
pip install nltk
```

### "rouge-score not available"
```bash
source venv/bin/activate
pip install rouge-score
```

### "BERTScore calculation failed"
This usually happens the first time - BERTScore needs to download models. Wait for the download to complete, or install manually:
```bash
source venv/bin/activate
pip install bert-score
```

### Rate limits or API errors
- Add `--parallel` flag for faster completion (but be aware of rate limits)
- Wait a moment and re-run - translations are cached

## Next Steps

- **Analyze in spreadsheet**: Open the CSV file in Excel/Google Sheets
- **Compare passages**: Read the detailed report to see specific translation examples
- **Run more texts**: Process additional Greek texts by adding them to `input/`
- **Add BLEURT (Linux)**: On Linux systems, you can add `bleurt` to your metrics for an additional learned metric

## Getting Help

If you encounter issues:

1. **Check the logs**: The pipeline prints detailed progress information
2. **Verify virtual environment**: Make sure you ran `source venv/bin/activate`
3. **Test components individually**: 
   ```bash
   source venv/bin/activate
   
   # Test parser only
   python3 src/parser.py input/10_chunks.txt --validate
   
   # Test translator only
   python3 src/translator.py input/10_chunks.txt --models openai
   ```
4. **Verify input format**: Make sure your input file matches the expected structure

## Tips for Best Results

1. **Multiple references**: The pipeline evaluates against all reference translations you provide, giving more robust scores
2. **Chunk size**: The parser automatically handles this, but 1-3 sentences per chunk works best
3. **GPU usage**: If you have a GPU, use `--gpu` for 3-5x faster neural metric computation
4. **Default metrics**: The 6 default metrics (BLEU-4, chrF++, METEOR, ROUGE-L, BERTScore, COMET) provide comprehensive coverage

Happy evaluating! 🎉
