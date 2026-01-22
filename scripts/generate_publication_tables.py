#!/usr/bin/env python3
"""
Generate publication-ready tables for the Galen MT evaluation paper.

Tables:
1. Aggregate Automated MT Evaluation Scores
2. Aggregate Human Evaluation Scores (MQM & TQS) - template
3. Reference Translation Effects (Appendix)
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

def load_evaluation(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def format_mean_sd(mean, std, scale=100, decimals=1):
    """Format as 'mean (± std)' with optional scaling."""
    return f"{mean*scale:.{decimals}f} (± {std*scale:.{decimals}f})"

def generate_table1_latex(mix_data, comp_data, output_path):
    """Generate Table 1: Aggregate Automated MT Evaluation Scores (LaTeX)."""
    
    metrics = ['BLEU-4', 'chrF++', 'METEOR', 'ROUGE-L', 'BERTScore', 'COMET']
    models = ['openai', 'claude', 'gemini']  # ChatGPT, Claude, Gemini
    model_labels = {'openai': 'ChatGPT', 'claude': 'Claude', 'gemini': 'Gemini'}
    
    lines = []
    lines.append("% Table 1: Aggregate Automated MT Evaluation Scores")
    lines.append("% Generated: " + datetime.now().strftime('%Y-%m-%d'))
    lines.append("")
    lines.append("\\begin{table*}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{Aggregate Automated MT Evaluation Scores}")
    lines.append("\\label{tab:automated-scores}")
    lines.append("\\small")
    lines.append("\\begin{tabular}{ll" + "c" * len(metrics) + "}")
    lines.append("\\toprule")
    
    # Header row
    header = "\\textbf{Text} & \\textbf{Model} & " + " & ".join([f"\\textbf{{{m}}}" for m in metrics]) + " \\\\"
    lines.append(header)
    lines.append("\\midrule")
    
    # Process each dataset
    for panel_name, data in [("\\textit{Mixtures}", mix_data), ("\\textit{Comp.}", comp_data)]:
        first_row = True
        
        for model in models:
            row_parts = []
            if first_row:
                row_parts.append(panel_name)
                first_row = False
            else:
                row_parts.append("")
            
            row_parts.append(model_labels[model])
            
            for metric in metrics:
                if metric in data['by_model'][model]:
                    m = data['by_model'][model][metric]
                    row_parts.append(format_mean_sd(m['mean'], m['std']))
                else:
                    row_parts.append("N/A")
            
            lines.append(" & ".join(row_parts) + " \\\\")
        
        # Aggregate row
        row_parts = ["", "\\textit{Aggregate}"]
        for metric in metrics:
            all_means = []
            all_stds = []
            for model in models:
                if metric in data['by_model'][model]:
                    all_means.append(data['by_model'][model][metric]['mean'])
                    all_stds.append(data['by_model'][model][metric]['std'])
            if all_means:
                agg_mean = np.mean(all_means)
                agg_std = np.mean(all_stds)  # Average of SDs
                row_parts.append(format_mean_sd(agg_mean, agg_std))
            else:
                row_parts.append("N/A")
        lines.append(" & ".join(row_parts) + " \\\\")
        
        if panel_name == "\\textit{Mixtures}":
            lines.append("\\midrule")
    
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\begin{tablenotes}")
    lines.append("\\small")
    lines.append("\\item Note: All scores reported as mean (± SD) × 100. BLEU-4, chrF++, METEOR use multi-reference evaluation; ROUGE-L, BERTScore, COMET use max-across-references. BLEURT excluded due to technical limitations.")
    lines.append("\\end{tablenotes}")
    lines.append("\\end{table*}")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated: {output_path}")

def generate_table1_markdown(mix_data, comp_data, output_path):
    """Generate Table 1: Aggregate Automated MT Evaluation Scores (Markdown)."""
    
    metrics = ['BLEU-4', 'chrF++', 'METEOR', 'ROUGE-L', 'BERTScore', 'COMET']
    models = ['openai', 'claude', 'gemini']
    model_labels = {'openai': 'ChatGPT', 'claude': 'Claude', 'gemini': 'Gemini'}
    
    lines = []
    lines.append("# Table 1: Aggregate Automated MT Evaluation Scores")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*")
    lines.append("")
    lines.append("**Purpose:** Satisfy requirement for 'standard methods' benchmarking; compare with previous papers.")
    lines.append("")
    
    # Header
    lines.append("| Text | Model | " + " | ".join(metrics) + " |")
    lines.append("|------|-------|" + "|".join(["-------"] * len(metrics)) + "|")
    
    # Process each dataset
    for panel_name, data in [("*Mixtures*", mix_data), ("*Comp.*", comp_data)]:
        first_row = True
        
        for model in models:
            row_parts = []
            if first_row:
                row_parts.append(panel_name)
                first_row = False
            else:
                row_parts.append("")
            
            row_parts.append(model_labels[model])
            
            for metric in metrics:
                if metric in data['by_model'][model]:
                    m = data['by_model'][model][metric]
                    row_parts.append(format_mean_sd(m['mean'], m['std']))
                else:
                    row_parts.append("N/A")
            
            lines.append("| " + " | ".join(row_parts) + " |")
        
        # Aggregate row
        row_parts = ["", "*Aggregate*"]
        for metric in metrics:
            all_means = []
            all_stds = []
            for model in models:
                if metric in data['by_model'][model]:
                    all_means.append(data['by_model'][model][metric]['mean'])
                    all_stds.append(data['by_model'][model][metric]['std'])
            if all_means:
                agg_mean = np.mean(all_means)
                agg_std = np.mean(all_stds)
                row_parts.append(format_mean_sd(agg_mean, agg_std))
            else:
                row_parts.append("N/A")
        lines.append("| " + " | ".join(row_parts) + " |")
    
    lines.append("")
    lines.append("**Note:** All scores reported as mean (± SD) × 100. BLEU-4, chrF++, METEOR use multi-reference evaluation; ROUGE-L, BERTScore, COMET use max-across-references. BLEURT excluded due to technical limitations.")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated: {output_path}")

def generate_table2_template(output_path):
    """Generate Table 2: Human Evaluation Scores template (to be filled in)."""
    
    lines = []
    lines.append("# Table 2: Aggregate Human Evaluation Scores (MQM & TQS)")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*")
    lines.append("")
    lines.append("**Purpose:** Present the 'ground truth' of MT quality established by humans in the loop.")
    lines.append("")
    lines.append("**Status:** TEMPLATE - To be populated after human evaluation is complete.")
    lines.append("")
    
    # Header
    lines.append("| Model | Mix. TQS | Mix. High % | Mix. Low % | Mix. Fail % | Mix. Crit. | Comp. TQS | Comp. High % | Comp. Low % | Comp. Fail % | Comp. Crit. |")
    lines.append("|-------|----------|-------------|------------|-------------|------------|-----------|--------------|-------------|--------------|-------------|")
    
    for model in ['ChatGPT', 'Claude', 'Gemini']:
        lines.append(f"| {model} | — | — | — | — | — | — | — | — | — | — |")
    lines.append("| *Aggregate* | — | — | — | — | — | — | — | — | — | — |")
    
    lines.append("")
    lines.append("**Column definitions:**")
    lines.append("- **TQS**: Translation Quality Score, mean (± SD)")
    lines.append("- **High %**: Percentage of chunks with high-pass quality")
    lines.append("- **Low %**: Percentage of chunks with low-pass quality")
    lines.append("- **Fail %**: Percentage of chunks that failed quality threshold")
    lines.append("- **Crit.**: Count of critical errors identified")
    lines.append("")
    lines.append("**MQM Error Categories to track:**")
    lines.append("- Accuracy: Addition, Omission, Mistranslation, Untranslated")
    lines.append("- Fluency: Grammar, Spelling, Punctuation, Register")
    lines.append("- Terminology: Inconsistent, Wrong term")
    lines.append("- Style: Awkward, Unnatural")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated: {output_path}")

def generate_table2_latex_template(output_path):
    """Generate Table 2 LaTeX template."""
    
    lines = []
    lines.append("% Table 2: Aggregate Human Evaluation Scores (MQM & TQS)")
    lines.append("% Generated: " + datetime.now().strftime('%Y-%m-%d'))
    lines.append("% STATUS: TEMPLATE - To be populated after human evaluation")
    lines.append("")
    lines.append("\\begin{table*}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{Aggregate Human Evaluation Scores}")
    lines.append("\\label{tab:human-scores}")
    lines.append("\\small")
    lines.append("\\begin{tabular}{l|ccccc|ccccc}")
    lines.append("\\toprule")
    lines.append(" & \\multicolumn{5}{c|}{\\textit{Mixtures}} & \\multicolumn{5}{c}{\\textit{Comp.}} \\\\")
    lines.append("\\textbf{Model} & TQS & High\\% & Low\\% & Fail\\% & Crit. & TQS & High\\% & Low\\% & Fail\\% & Crit. \\\\")
    lines.append("\\midrule")
    lines.append("ChatGPT & — & — & — & — & — & — & — & — & — & — \\\\")
    lines.append("Claude & — & — & — & — & — & — & — & — & — & — \\\\")
    lines.append("Gemini & — & — & — & — & — & — & — & — & — & — \\\\")
    lines.append("\\midrule")
    lines.append("\\textit{Aggregate} & — & — & — & — & — & — & — & — & — & — \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table*}")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated: {output_path}")

def generate_appendix_condensed_table(mix_data, comp_data, output_path):
    """Generate a condensed table with only key metrics (for main text if Table 1 is too dense)."""
    
    # Key metrics for main paper
    key_metrics = ['BLEU-4', 'chrF++', 'BERTScore', 'COMET']
    models = ['openai', 'claude', 'gemini']
    model_labels = {'openai': 'ChatGPT', 'claude': 'Claude', 'gemini': 'Gemini'}
    
    lines = []
    lines.append("# Table 1A: Key Automated MT Evaluation Scores (Condensed)")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*")
    lines.append("")
    lines.append("**For main text.** Full metrics (including METEOR, ROUGE-L) in Appendix.")
    lines.append("")
    
    # Header
    lines.append("| Text | Model | " + " | ".join(key_metrics) + " |")
    lines.append("|------|-------|" + "|".join(["-------"] * len(key_metrics)) + "|")
    
    for panel_name, data in [("*Mixtures*", mix_data), ("*Comp.*", comp_data)]:
        first_row = True
        for model in models:
            row_parts = []
            row_parts.append(panel_name if first_row else "")
            first_row = False
            row_parts.append(model_labels[model])
            for metric in key_metrics:
                m = data['by_model'][model][metric]
                row_parts.append(format_mean_sd(m['mean'], m['std']))
            lines.append("| " + " | ".join(row_parts) + " |")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated: {output_path}")

def generate_reference_effects_table(mix_data, comp_data, output_path):
    """Generate Appendix table: Reference Translation Effects."""
    
    lines = []
    lines.append("# Appendix Table: Reference Translation Effects")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*")
    lines.append("")
    lines.append("**Purpose:** Show how scores differ when using Johnston vs van der Eijk as reference.")
    lines.append("")
    lines.append("**Status:** TEMPLATE - Requires per-reference evaluation data.")
    lines.append("")
    lines.append("To generate this table, run evaluations with each reference separately:")
    lines.append("```bash")
    lines.append("# Evaluate against Johnston only")
    lines.append("python pipeline.py evaluate --input input/on_mixtures.txt --reference-subset johnston")
    lines.append("")
    lines.append("# Evaluate against van der Eijk only")
    lines.append("python pipeline.py evaluate --input input/on_mixtures.txt --reference-subset vandereijk")
    lines.append("```")
    lines.append("")
    lines.append("| Model | Metric | Johnston | van der Eijk | Δ (J - vdE) |")
    lines.append("|-------|--------|----------|--------------|-------------|")
    lines.append("| ChatGPT | BLEU-4 | — | — | — |")
    lines.append("| ChatGPT | COMET | — | — | — |")
    lines.append("| Claude | BLEU-4 | — | — | — |")
    lines.append("| Claude | COMET | — | — | — |")
    lines.append("| Gemini | BLEU-4 | — | — | — |")
    lines.append("| Gemini | COMET | — | — | — |")
    lines.append("")
    lines.append("**Interpretation:** A positive Δ indicates the model aligns more closely with Johnston's translation style.")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated: {output_path}")

def generate_csv_for_stats(mix_data, comp_data, output_path):
    """Generate CSV for statistical analysis in R/Python."""
    import csv
    
    metrics = ['BLEU-4', 'chrF++', 'METEOR', 'ROUGE-L', 'BERTScore', 'COMET']
    models = ['openai', 'claude', 'gemini']
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['dataset', 'model', 'metric', 'mean', 'std', 'min', 'max', 'n'])
        
        for dataset_name, data in [('mixtures', mix_data), ('comp', comp_data)]:
            for model in models:
                for metric in metrics:
                    if metric in data['by_model'][model]:
                        m = data['by_model'][model][metric]
                        writer.writerow([
                            dataset_name,
                            model,
                            metric,
                            m['mean'],
                            m['std'],
                            m['min'],
                            m['max'],
                            m['count']
                        ])
    
    print(f"✓ Generated: {output_path}")

def main():
    base_path = Path(__file__).parent.parent
    eval_dir = base_path / 'output' / 'evaluations'
    pub_dir = base_path / 'output' / 'publication_tables'
    pub_dir.mkdir(exist_ok=True)
    
    print("Generating publication tables...")
    print()
    
    # Load evaluation data
    mix_data = load_evaluation(eval_dir / 'on_mixtures_evaluation.json')
    comp_data = load_evaluation(eval_dir / 'on_comp_evaluation.json')
    
    # Generate Table 1: Automated Scores
    print("Table 1: Aggregate Automated MT Evaluation Scores")
    generate_table1_markdown(mix_data, comp_data, pub_dir / 'table1_automated_scores.md')
    generate_table1_latex(mix_data, comp_data, pub_dir / 'table1_automated_scores.tex')
    generate_appendix_condensed_table(mix_data, comp_data, pub_dir / 'table1a_condensed.md')
    print()
    
    # Generate Table 2: Human Evaluation (template)
    print("Table 2: Aggregate Human Evaluation Scores (Template)")
    generate_table2_template(pub_dir / 'table2_human_scores.md')
    generate_table2_latex_template(pub_dir / 'table2_human_scores.tex')
    print()
    
    # Generate Appendix: Reference Effects (template)
    print("Appendix: Reference Translation Effects")
    generate_reference_effects_table(mix_data, comp_data, pub_dir / 'appendix_reference_effects.md')
    print()
    
    # Generate CSV for statistical analysis
    print("Statistical Analysis Data")
    generate_csv_for_stats(mix_data, comp_data, pub_dir / 'scores_for_stats.csv')
    print()
    
    print(f"✓ All publication tables saved to {pub_dir}")

if __name__ == '__main__':
    main()
