# Ancient Greek Translator

Translate Ancient Greek texts using **GPT-5**, **Claude 4.1**, and **Gemini 2.5 Pro**.

## Quick Start

1. **Setup** (one time):
   ```bash
   pip install -r requirements.txt
   cp env.example .env
   # Add your API keys to .env
   ```

2. **Add your Greek texts** to `texts/inputs/` folder

3. **Translate**:
   ```bash
   ./translate_all.sh
   ```

4. **Get results** in `outputs/` folder

## That's it! 🏛️

### Chunking Options
```bash
./translate_all.sh short    # 1-2 sentences (best for evaluation)
./translate_all.sh medium   # Full paragraphs (better for context)
```

### File Structure
```
📁 texts/inputs/    ← Put your .txt files here
📁 outputs/         ← Translations appear here  
📄 translate_all.sh ← Run this script
📄 main_translator.py ← Core engine
📄 requirements.txt ← Dependencies
📄 env.example      ← API key template
```

### API Keys Needed
- `OPENAI_API_KEY` (for GPT-5)
- `ANTHROPIC_API_KEY` (for Claude 4.1)  
- `GOOGLE_API_KEY` (for Gemini 2.5 Pro)

### Features
- **No artificial limits** - Full-length translations
- **Smart chunking** - Handles sentences or paragraphs
- **Parallel processing** - All three models at once
- **Success analytics** - Track what works
- **Clean outputs** - Timestamped JSON files

---

**Need help?** Check the `archive/` folder for detailed docs and examples.