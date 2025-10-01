# Ancient Greek Translation Evaluation System

A web-based interface for experts to evaluate and rank AI translations of ancient Greek texts.

## Overview

This system allows classical scholars and ancient Greek experts to evaluate translations from multiple AI models in a blind evaluation format. Experts rank translations without knowing which model produced them, ensuring unbiased assessment.

## Features

### Expert Interface
- **Credentials Collection**: Captures expert qualifications and experience
- **Blind Evaluation**: Model labels and quality scores are hidden
- **Drag-and-Drop Ranking**: Intuitive interface for ranking translations
- **Progress Tracking**: Shows evaluation progress and remaining chunks
- **Session Management**: Tracks expert sessions and time spent

### Data Processing
- **Translation Cleaning**: Removes markdown headers and escape sequences
- **Filtering**: Only shows chunks with complete translations from all models
- **Storage**: Evaluations saved locally and can be exported

### Analysis Tools
- **Results Export**: Download individual expert results as JSON
- **Aggregation Script**: Combine multiple expert evaluations
- **Statistical Analysis**: Agreement metrics and ranking analysis

## Setup

1. **Start the web server**:
   ```bash
   cd website
   python3 -m http.server 8000
   ```

2. **Open in browser**: Navigate to `http://localhost:8000`

3. **Expert workflow**:
   - Enter credentials (name, institution, specialization)
   - Evaluate chunks by ranking translations (best to worst)
   - Skip difficult chunks if needed
   - Download results when complete

## Data Format

### Input Data
The system loads from `data/galen_test_chunk_multi_model_claude_gemini_openai_20250929_150101.json` containing:
- Original Greek text chunks
- Translations from OpenAI, Claude, and Gemini
- Translation status and metadata

### Expert Results
Each expert's results are exported as JSON with:
- Expert credentials and qualifications
- Session metadata and timing
- Individual chunk rankings
- Chunk content and translations evaluated

## Scripts

### Translation Cleaning
```bash
python3 scripts/clean_translations.py input_file.json [--backup]
```
Removes markdown headers, escape sequences, and formatting artifacts from translations.

### Results Collection
```bash
python3 scripts/collect_evaluations.py expert1.json expert2.json ... -o reports/
```
Aggregates multiple expert evaluations and generates analysis reports:
- Expert summary (CSV)
- All evaluations (CSV) 
- Model comparison (CSV)
- Statistical analysis (JSON)

## Data Quality

### Filtering Criteria
- Only chunks with successful translations from all three models
- Filters out error cases and incomplete translations
- Currently shows 51 of 130 total chunks (39.2%)

### Cleaning Process
- Removes "# Translation" headers
- Converts escape sequences to proper formatting
- Normalizes whitespace and line breaks
- Preserves paragraph structure

## Expert Credentials

Required fields:
- Full name
- Institution/Organization  
- Title/Position

Optional fields:
- Specialization in Ancient Greek
- Years of experience
- Email (for results sharing)

## Privacy & Storage

- Evaluations stored locally in browser localStorage
- No automatic server uploads
- Expert controls data export and sharing
- Session IDs prevent data mixing between experts

## Analysis Features

The aggregation script provides:
- **Model Rankings**: Average rank for each AI model
- **Expert Agreement**: How often experts agree on rankings  
- **Completion Statistics**: Evaluation counts per expert
- **Time Analysis**: Time spent per chunk/session

## Technical Details

- **Frontend**: Vanilla JavaScript with Sortable.js for drag-and-drop
- **Storage**: localStorage for client-side persistence
- **Export**: JSON format for interoperability
- **Analysis**: Python with pandas for statistical analysis

## For Developers

Key files:
- `js/app.js` - Main evaluation interface logic
- `scripts/clean_translations.py` - Data preprocessing
- `scripts/collect_evaluations.py` - Results aggregation
- `css/styles.css` - Interface styling

The system is designed to be:
- **Lightweight**: No database or server dependencies
- **Portable**: Runs on any web server
- **Extensible**: Easy to modify for different texts or models
- **Reliable**: Client-side storage prevents data loss