# Galen Translation Evaluation Pipeline

A streamlined system for translating Ancient Greek texts and evaluating translation quality using state-of-the-art NLP metrics.

## 🎯 What This Does

1. **Parses** your input document (Greek + reference translations)
2. **Translates** Greek text using 3 AI models (OpenAI GPT, Claude, Gemini)
3. **Evaluates** translations against references using 6 metric families
4. **Reports** clear, actionable results

## 📁 Project Structure

```
galen_eval/
├── input/              # Place your input documents here
├── output/            
│   ├── translations/   # Raw translation outputs
│   ├── evaluations/    # Evaluation scores
│   └── reports/        # Human-readable reports
├── src/               
│   ├── parser.py       # Parse input documents
│   ├── translator.py   # Call translation APIs
│   ├── evaluator.py    # Run evaluation metrics
│   └── reporter.py     # Generate reports
├── config/
│   └── .env            # API keys (not in git)
├── requirements.txt
├── pipeline.py         # Main workflow script
└── README.md          # This file
```

## 🚀 Quick Start

### 1. Setup (one time)

```bash
cd galen_eval

# Run setup script (creates venv, installs dependencies)
./setup.sh

# The pipeline will look for .env in project root (../.env) or config/.env
# Make sure your .env file has your API keys
```

### 2. Run Pipeline

```bash
# Activate virtual environment
source venv/bin/activate

# Run the full pipeline
python3 pipeline.py input/10_chunks.txt

# When done
deactivate
```

This will:
- Parse the document
- Get translations from all 3 APIs
- Evaluate against both reference translations
- Generate a comprehensive report

## 📊 Evaluation Metrics

### Lexical Metrics (word/character level)
- **BLEU-4** - N-gram precision (4-gram)
- **chrF++** - Character n-gram F-score with word bigrams
- **METEOR** - Incorporates stemming and synonyms
- **ROUGE-L** - Longest common subsequence

### Neural/Semantic Metrics (meaning level)
- **BERTScore** - Contextual word embeddings
- **COMET** - Neural MT evaluation (requires source text)
- **BLEURT** - Learned evaluation metric (Linux only)

## 📋 Input Format

Your input file should have chunks with this structure:

```
Chunk 1

[Greek text]

[Reference Translation 1]

[Reference Translation 2]

Chunk 2

[Greek text]

[Reference Translation 1]

[Reference Translation 2]

...
```

The parser automatically:
- Identifies chunks
- Extracts Greek text (lines with Greek characters)
- Extracts reference translations (English lines)
- Associates each chunk's translations

## 📤 Output

### 1. Translations JSON (`output/translations/`)
```json
{
  "chunk_1": {
    "greek": "...",
    "openai": "...",
    "claude": "...",
    "gemini": "..."
  }
}
```

### 2. Evaluation JSON (`output/evaluations/`)
```json
{
  "chunk_1": {
    "vs_reference_1": {
      "openai": {"BLEU-4": 0.45, ...},
      "claude": {"BLEU-4": 0.52, ...},
      "gemini": {"BLEU-4": 0.48, ...}
    },
    "vs_reference_2": {...}
  }
}
```

### 3. Summary Report (`output/reports/`)
Clear, human-readable summary with:
- Overall model rankings
- Best model per metric
- Statistical summaries
- Example translations

## ⚙️ Configuration

Edit `pipeline.py` to customize:
- Which models to use
- Which metrics to compute
- Parallel processing options
- Output verbosity

## 💡 Tips

- **For best results**: Keep chunks to 1-2 sentences (parser handles this)
- **Multiple references**: Evaluating against 2 references increases reliability
- **GPU recommended**: For neural metrics (BERTScore, COMET)
- **Rate limits**: Pipeline includes delays to respect API limits

## 📚 Requirements

- Python 3.8+
- API keys for: OpenAI, Anthropic (Claude), Google (Gemini)
- ~2GB disk space for evaluation models
- GPU optional but recommended for neural metrics

