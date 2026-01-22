#!/bin/bash
# Create symlinks to original data sources for transparency

cd "$(dirname "$0")"

mkdir -p data_sources
cd data_sources

# MQM data
ln -sf "../../mqm/Comp MQM Summary Report Unblinded.xlsx - Summary.csv" "mqm_comp.csv"
ln -sf "../../mqm/Mixtures MQM Summary Report Unblinded.xlsx - Summary.csv" "mqm_mixtures.csv"

# Survey data (use anonymized version for sharing)
ln -sf "../../surveys/survey-responses-anonymized.csv" "survey_responses.csv"

# MT automated metrics
ln -sf "../../mt_eval/output/reports/on_comp_scores.csv" "mt_metrics_comp.csv"
ln -sf "../../mt_eval/output/reports/on_mixtures_scores.csv" "mt_metrics_mixtures.csv"

echo "Data source symlinks created in data_sources/:"
ls -la

echo ""
echo "These symlinks point to the original files. If the originals change,"
echo "the linked files will automatically reflect those changes."
