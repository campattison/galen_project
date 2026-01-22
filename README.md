# Evaluating AI Translation of Ancient Greek Medical Texts

A comparative evaluation of large language model (LLM) translations of Galen's ancient Greek medical texts against professional human translations.

## Overview

This project evaluates translations from three LLMs (Claude, Gemini, ChatGPT) using multiple evaluation methodologies:

1. **Blind Expert Survey** - Classicists and medical historians compared translations without knowing their source
2. **MQM Annotation** - Professional Multidimensional Quality Metrics scoring
3. **Automated MT Metrics** - BLEU, chrF++, BERTScore, COMET, and others

The source texts are excerpts from Galen's *De Temperamentis* (On Mixtures) and *De Compositione Medicamentorum* (On the Composition of Drugs).

## Key Findings

### AI vs Human Translation Quality

In blind expert comparisons, AI translations were generally preferred over human translations:

| Source | Mean Preference | Win Rate |
|--------|-----------------|----------|
| Gemini | +0.36 | 56.9% |
| ChatGPT | +0.33 | 47.3% |
| Claude | +0.21 | 49.1% |
| Human (Singer-van der Eijk) | -0.01 | 36.3% |
| Human (Johnston) | -0.63 | 20.3% |

### Automated Metrics vs Human Judgment

| Metric | Correlation with MQM (Pearson r) | Correlation with Survey (Kendall τ) |
|--------|----------------------------------|-------------------------------------|
| BERTScore | 0.753*** | -0.010 |
| COMET | 0.605*** | +0.010 |
| chrF++ | 0.530*** | +0.045 |
| BLEU-4 | 0.447*** | 0.000 |

**Key insight:** Automated metrics correlate well with formal quality annotation but fail to predict expert preferences in blind comparisons (no metric achieved significance). This validates the continued need for human evaluation in specialized translation domains.

## Repository Structure

```
.
├── surveys/                    # Blind expert preference survey
│   ├── src/
│   │   └── analysis.py
│   ├── charts/                 # Generated visualizations
│   ├── reports/
│   └── survey-responses-anonymized.csv
│
├── mqm/                        # MQM quality annotation analysis
│   ├── mqm_analysis.py
│   ├── charts/
│   ├── reports/
│   └── *.csv                   # MQM data exports
│
├── metrics_correlation/        # Correlation analysis
│   ├── correlation_analysis.py
│   ├── data_sources/           # Symlinks to source data
│   ├── charts/
│   └── reports/
│
├── mt_eval/                    # MT evaluation pipeline
│   ├── src/
│   ├── input/                  # Source Greek texts
│   └── output/
│       ├── translations/
│       ├── evaluations/
│       └── reports/
│
└── WORKLOG_2026-01-22_analysis.md
```

## Running the Analyses

### Requirements

```bash
pip install pandas numpy matplotlib scipy
```

### Survey Analysis

```bash
cd surveys
python3 src/analysis.py
```

Generates preference distributions, win rates, and head-to-head comparisons.

### MQM Analysis

```bash
cd mqm
MPLBACKEND=Agg python3 mqm_analysis.py
```

Generates TQS distributions, chunk-by-chunk heatmaps, and error breakdowns.

### Metrics Correlation

```bash
cd metrics_correlation

# Set up data source symlinks (optional, for transparency)
chmod +x setup_data_links.sh
./setup_data_links.sh

# Run analysis
MPLBACKEND=Agg python3 correlation_analysis.py
```

Computes Pearson, Spearman, and Kendall correlations between automated metrics and human evaluations.

## Data

### Survey Data
- **Format:** CSV with anonymized expert IDs
- **Fields:** Chunk ID, Preference Score (-2 to +2), Left/Right Translation sources, Expert comments
- **Note:** Original data with expert names is excluded from this repository

### MQM Data
- **Format:** CSV exports from MQM annotation spreadsheets
- **Metrics:** TQS (Translation Quality Score), error counts by severity (Neutral, Minor, Major, Critical)

### Automated Metrics
- **Computed using:** SacreBLEU, BERTScore, COMET
- **Reference translations:** Johnston (1997), Singer & van der Eijk

## Source Texts

| Text | Description | Chunks |
|------|-------------|--------|
| *De Temperamentis* | On Mixtures/Temperaments | 10 |
| *De Compositione Medicamentorum* | On the Composition of Drugs | 10 |

## Models Evaluated

| Model | Provider | Version |
|-------|----------|---------|
| Claude | Anthropic | Claude 3.5 Sonnet |
| Gemini | Google | Gemini 1.5 Pro |
| ChatGPT | OpenAI | GPT-4 |

## Human Reference Translations

1. **Johnston** - I. Johnston, *Galen: On Temperaments* (1997)
2. **Singer-van der Eijk** - P.N. Singer & P.J. van der Eijk, *Galen: Works on Human Nature* (2018)

## Citation

If you use this data or methodology, please cite:

```
[Citation information to be added]
```

## License

[License information to be added]

## Acknowledgments

We thank the classicists and medical historians who participated in the blind evaluation survey.
