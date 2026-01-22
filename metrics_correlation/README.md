# Metrics Correlation Analysis

This folder contains the analysis correlating automated MT metrics with human evaluations.

## Setup

1. **Create data source symlinks** (for transparency):
   ```bash
   chmod +x setup_data_links.sh
   ./setup_data_links.sh
   ```

2. **Run the analysis**:
   ```bash
   MPLBACKEND=Agg python3 correlation_analysis.py
   ```

## Data Sources

The analysis draws from three evaluation approaches:

| Source | Location | Description |
|--------|----------|-------------|
| **MQM** | `../mqm/` | Expert MQM annotation with TQS scores |
| **Survey** | `../surveys/` | Blind expert preference comparisons |
| **MT Metrics** | `../mt_eval/output/reports/` | Automated metrics (BLEU, chrF++, BERTScore, COMET, etc.) |

After running `setup_data_links.sh`, symlinks to these files appear in `data_sources/`:

```
data_sources/
├── mqm_comp.csv          → ../mqm/Comp MQM Summary Report...
├── mqm_mixtures.csv      → ../mqm/Mixtures MQM Summary Report...
├── survey_responses.csv  → ../surveys/survey-responses-...
├── mt_metrics_comp.csv   → ../mt_eval/output/reports/on_comp_scores.csv
└── mt_metrics_mixtures.csv → ../mt_eval/output/reports/on_mixtures_scores.csv
```

## Outputs

After running the analysis:

```
metrics_correlation/
├── charts/
│   ├── chart1_correlation_heatmap.png   # Correlation coefficient matrix
│   ├── chart2_scatter_tqs.png           # Scatter plots: metrics vs TQS
│   └── chart3_correlation_bars.png      # Bar chart comparing correlations
├── reports/
│   ├── correlation_analysis_report.txt  # Human-readable report
│   ├── correlation_data.csv             # Raw correlation coefficients
│   └── merged_metrics_tqs.csv           # Combined dataset
└── data_sources/                        # Symlinks to original data
```

## Metrics Analyzed

| Metric | Type | Description |
|--------|------|-------------|
| BLEU-4 | N-gram | Precision-based, 4-gram |
| chrF++ | Character | Character n-gram F-score with word bigrams |
| METEOR | Alignment | Includes synonyms and stems |
| ROUGE-L | Sequence | Longest common subsequence |
| BERTScore | Neural | BERT-based semantic similarity |
| COMET | Neural | Trained on human judgments |

## Correlation Methods

- **Pearson r**: Linear correlation with TQS
- **Spearman ρ**: Rank correlation with TQS  
- **Kendall's τ**: Rank correlation with survey preferences (robust to ties)
