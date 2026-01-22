# Galen Translation Evaluation - Project Summary

## Overview

This is a **clean, modern, streamlined** translation evaluation system designed specifically for Ancient Greek texts (especially Galen's medical works).

### What It Does

Takes a document like `10_chunks.txt` containing:
- Greek text chunks
- Reference translations (1-2 per chunk)

Then automatically:
1. **Parses** the input to extract Greek text and reference translations
2. **Translates** the Greek using 3 state-of-the-art AI models
3. **Evaluates** translations using 6+ machine translation metrics
4. **Reports** results in human-readable and machine-readable formats

## Key Features

### ✅ Clean Architecture
- **Modular design**: Each component (parser, translator, evaluator, reporter) is independent
- **Easy to extend**: Add new models or metrics without touching other code
- **Well-documented**: Clear docstrings and comments throughout

### ✅ Comprehensive Evaluation
Uses industry-standard MT evaluation metrics:
- **BLEU-4**: N-gram precision (4-gram)
- **chrF++**: Character n-gram F-score with word bigrams
- **METEOR**: Incorporates stemming and synonyms
- **ROUGE-L**: Longest common subsequence
- **BERTScore**: Neural contextual embeddings
- **COMET**: Neural reference-based metric (requires source)

### ✅ Multiple AI Models
- **OpenAI GPT-4o**: Latest GPT model
- **Anthropic Claude Sonnet**: Latest Claude
- **Google Gemini 2.0 Flash**: Latest Gemini

### ✅ Flexible & Configurable
- Choose which models to use
- Choose which metrics to compute
- GPU support for faster neural metrics
- Parallel translation for speed
- Multiple output formats (JSON, CSV, TXT)

### ✅ Clear Output
- **Summary report**: Quick overview of model rankings
- **Detailed report**: Full results with translation examples
- **CSV export**: For further analysis in spreadsheets
- **JSON output**: For programmatic access

## Project Structure

```
galen_eval/
├── input/                    # Place input documents here
│   └── 10_chunks.txt        # Example input (already included)
│
├── output/                   # All outputs go here
│   ├── translations/        # Raw translation JSON files
│   ├── evaluations/         # Evaluation scores JSON files
│   └── reports/             # Human-readable reports (TXT, CSV)
│
├── src/                      # Source code modules
│   ├── parser.py            # Parse input documents
│   ├── translator.py        # Call translation APIs
│   ├── evaluator.py         # Compute evaluation metrics
│   └── reporter.py          # Generate reports
│
├── config/                   # Configuration
│   └── env.example          # Example API key configuration
│
├── pipeline.py               # Main script - runs everything
├── requirements.txt          # Python dependencies
├── README.md                 # Full documentation
├── QUICKSTART.md             # 5-minute quick start guide
└── PROJECT_SUMMARY.md        # This file
```

## Usage

### Simple Usage (One Command)

```bash
python pipeline.py input/10_chunks.txt
```

This runs the complete pipeline and generates all outputs.

### Advanced Usage

```bash
# Use specific models
python pipeline.py input/10_chunks.txt --models openai claude

# Use specific metrics (fast metrics only)
python pipeline.py input/10_chunks.txt --metrics bleu rouge chrf

# Enable GPU
python pipeline.py input/10_chunks.txt --gpu

# Parallel translation (faster)
python pipeline.py input/10_chunks.txt --parallel
```

### Individual Components

Each component can also be run independently:

```bash
# Parse only
python src/parser.py input/10_chunks.txt --validate

# Translate only
python src/translator.py input/10_chunks.txt -o output/translations/my_trans.json

# Evaluate only (requires existing translations)
python src/evaluator.py input/10_chunks.txt output/translations/my_trans.json

# Generate report only (requires existing evaluations)
python src/reporter.py output/evaluations/my_eval.json --detailed
```

## Design Decisions

### 1. **Separation of Concerns**
Each module has one responsibility:
- Parser: Understand input format
- Translator: Call APIs
- Evaluator: Compute metrics
- Reporter: Present results

### 2. **Fail Gracefully**
- Missing API keys? Skip that model, use others
- Metric library not installed? Skip that metric, use others
- API error? Log it, continue with other models

### 3. **Multiple Reference Translations**
Unlike many MT evaluation systems that use only one reference, this evaluates against ALL provided references, giving more robust scores.

### 4. **Clear Output**
Results are presented in multiple formats:
- **Human-readable**: Text reports with clear rankings and examples
- **Machine-readable**: JSON with complete data
- **Analysis-ready**: CSV for spreadsheets and statistical tools

### 5. **No Black Boxes**
- All intermediate results are saved
- You can inspect translations before evaluation
- You can re-evaluate without re-translating
- Full traceability of what was evaluated

## Comparison to Old System

| Aspect | Old System | New System |
|--------|-----------|------------|
| **Structure** | Scattered across archive/ folders | Clean, focused galen_eval/ folder |
| **Workflow** | Multiple scripts, unclear order | Single pipeline.py entry point |
| **Documentation** | Spread across multiple READMEs | QUICKSTART.md + README.md |
| **Modularity** | Tightly coupled | Independent, reusable modules |
| **Input parsing** | Manual, error-prone | Automatic, validated |
| **Output** | JSON dumps only | JSON + TXT reports + CSV |
| **Error handling** | Crashes on errors | Graceful degradation |
| **Testing** | No easy way to test components | Each module independently testable |

## Metrics Cost Analysis

**All metrics are FREE and open-source!**

| Metric | Cost | Download Size | Notes |
|--------|------|---------------|-------|
| BLEU-4 | Free | ~10MB (NLTK data) | Lexical, 4-gram |
| chrF++ | Free | ~1MB | Character + word n-grams |
| METEOR | Free | ~50MB (WordNet) | Includes synonyms/stems |
| ROUGE-L | Free | ~5MB | Longest common subsequence |
| BERTScore | Free | ~500MB (models) | Neural, GPU helpful |
| COMET | Free | ~1.5GB (model) | Neural, requires source |

**Only cost**: API calls for translation
- OpenAI: ~$0.10 per 10 chunks (varies by model)
- Claude: ~$0.15 per 10 chunks (varies by model)
- Gemini: ~$0.05 per 10 chunks (varies by model)

Evaluation metrics themselves are completely free.

## Future Enhancements

Possible extensions (not implemented yet):
- [ ] Support for more translation models (DeepL, Bing, etc.)
- [ ] Support for more evaluation metrics (TER, WER, etc.)
- [ ] Batch processing of multiple input files
- [ ] Interactive web interface
- [ ] Caching of translations to avoid re-translating
- [ ] Statistical significance testing between models
- [ ] Fine-grained error analysis (by chunk characteristics)
- [ ] Integration with translation memory systems

## Dependencies

**Core requirements** (always needed):
- openai, anthropic, google-genai (API clients)
- nltk, sacrebleu, rouge-score (fast metrics)
- python-dotenv (configuration)

**Optional requirements** (for neural metrics):
- bert-score (BERTScore)
- bleurt (BLEURT - large download)
- unbabel-comet (COMET - large download)

**GPU acceleration** (optional):
- torch with CUDA support

All dependencies are listed in `requirements.txt` with clear comments about which are optional.

## License & Attribution

This is a research tool for evaluating Ancient Greek translations.

**Metrics implementations**:
- BLEU-4, METEOR: NLTK project
- chrF++: sacrebleu (Popović 2017)
- ROUGE-L: Google Research
- BERTScore: Zhang et al. (ICLR 2020)
- COMET: Rei et al. (EMNLP 2020)

**Translation models**:
- OpenAI GPT-4o
- Anthropic Claude Sonnet
- Google Gemini

## Contact & Support

For issues or questions about this system:
1. Check QUICKSTART.md for common issues
2. Check README.md for detailed documentation
3. Test individual components to isolate problems

## Summary

This is a **production-ready, research-grade** translation evaluation system that:
- ✅ Works out of the box with minimal setup
- ✅ Handles your existing data format (10_chunks.txt)
- ✅ Uses state-of-the-art models and metrics
- ✅ Produces clear, actionable results
- ✅ Is easy to understand, modify, and extend

**One command to rule them all:**
```bash
python pipeline.py input/10_chunks.txt
```

That's it! 🎉
