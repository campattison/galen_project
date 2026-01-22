#!/usr/bin/env python3
"""
Generate a detailed side-by-side report showing:
- Source Greek text
- Reference translations
- Model translations
- Evaluation scores per chunk

For validation and transparency purposes.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_input_file(filepath):
    """Parse input file to extract chunks with Greek and references."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chunks = {}
    # Split by "Chunk N"
    parts = re.split(r'Chunk\s+(\d+)', content)
    
    for i in range(1, len(parts), 2):
        chunk_id = parts[i]
        chunk_content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in chunk_content.split('\n\n') if p.strip()]
        
        if paragraphs:
            # First paragraph is Greek (contains Greek characters)
            greek = paragraphs[0] if any('\u0370' <= c <= '\u03ff' or '\u1f00' <= c <= '\u1fff' for c in paragraphs[0]) else ""
            # Remaining are reference translations
            refs = [p for p in paragraphs[1:] if p and not any('\u0370' <= c <= '\u03ff' for c in p[:50])]
            
            chunks[chunk_id] = {
                'greek': greek,
                'references': refs
            }
    
    return chunks

def truncate_text(text, max_len=500):
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."

def generate_markdown_report(input_file, translations_file, evaluation_file, output_file):
    """Generate a comprehensive Markdown report."""
    
    # Load data
    chunks = parse_input_file(input_file)
    translations = load_json(translations_file)
    evaluation = load_json(evaluation_file)
    
    # Get detailed scores
    detailed_scores = {
        (d['chunk_id'], d['model_name']): d['scores']
        for d in evaluation.get('detailed_scores', [])
    }
    
    lines = []
    
    # Header
    name = Path(input_file).stem
    lines.append(f"# Translation Evaluation: {name.replace('_', ' ').title()}")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("This document provides a side-by-side comparison of translations and their evaluation scores for validation and transparency.")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append("### Overall Rankings")
    lines.append("")
    lines.append("| Rank | Model | Score |")
    lines.append("|------|-------|-------|")
    for i, (model, score) in enumerate(evaluation['overall_rankings'], 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "")
        lines.append(f"| {medal} {i} | {model.upper()} | {score:.4f} |")
    lines.append("")
    
    # Methodology
    lines.append("### Methodology")
    lines.append("")
    lines.append("- **BLEU-4, chrF++, METEOR**: Multi-reference (n-grams matched against ANY reference)")
    lines.append("- **ROUGE-L, BERTScore, COMET**: Max score across references")
    lines.append("")
    
    # Per-chunk details
    lines.append("---")
    lines.append("")
    lines.append("## Chunk-by-Chunk Analysis")
    lines.append("")
    
    for chunk_id in sorted(chunks.keys(), key=int):
        chunk_data = chunks[chunk_id]
        
        lines.append(f"### Chunk {chunk_id}")
        lines.append("")
        
        # Greek source
        lines.append("#### Source (Greek)")
        lines.append("")
        lines.append(f"> {truncate_text(chunk_data['greek'], 800)}")
        lines.append("")
        
        # Reference translations
        lines.append("#### Reference Translations")
        lines.append("")
        for i, ref in enumerate(chunk_data['references'], 1):
            lines.append(f"**Reference {i}:**")
            lines.append(f"> {truncate_text(ref, 600)}")
            lines.append("")
        
        # Model translations with scores
        lines.append("#### Model Translations & Scores")
        lines.append("")
        
        if chunk_id in translations:
            for model in ['claude', 'gemini', 'openai']:
                if model in translations[chunk_id]:
                    trans_data = translations[chunk_id][model]
                    translation = trans_data.get('translation', '')
                    scores = detailed_scores.get((chunk_id, model), {})
                    
                    lines.append(f"**{model.upper()}**")
                    lines.append("")
                    lines.append(f"> {truncate_text(translation, 600)}")
                    lines.append("")
                    
                    # Score table
                    if scores:
                        lines.append("| Metric | Score |")
                        lines.append("|--------|-------|")
                        for metric in ['BLEU-4', 'chrF++', 'METEOR', 'ROUGE-L', 'BERTScore', 'COMET']:
                            if metric in scores:
                                lines.append(f"| {metric} | {scores[metric]:.4f} |")
                        lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated: {output_file}")

def generate_csv_scores(evaluation_file, output_file):
    """Generate a CSV of all scores for spreadsheet analysis."""
    import csv
    
    evaluation = load_json(evaluation_file)
    detailed = evaluation.get('detailed_scores', [])
    
    if not detailed:
        return
    
    # Get all metrics
    metrics = list(detailed[0]['scores'].keys())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['chunk_id', 'model'] + metrics)
        
        # Data rows
        for d in sorted(detailed, key=lambda x: (int(x['chunk_id']), x['model_name'])):
            row = [d['chunk_id'], d['model_name']]
            row.extend([d['scores'].get(m, '') for m in metrics])
            writer.writerow(row)
    
    print(f"✓ Generated: {output_file}")

def main():
    base_path = Path(__file__).parent.parent
    input_dir = base_path / 'input'
    trans_dir = base_path / 'output' / 'translations'
    eval_dir = base_path / 'output' / 'evaluations'
    report_dir = base_path / 'output' / 'reports'
    
    report_dir.mkdir(exist_ok=True)
    
    print("Generating side-by-side reports...")
    print()
    
    # Process each dataset
    datasets = [
        ('on_mixtures', 'on_mixtures.txt', 'on_mixtures_translations.json', 'on_mixtures_evaluation.json'),
        ('on_comp', 'on_comp.txt', 'on_comp_translations.json', 'on_comp_evaluation.json'),
    ]
    
    for name, input_name, trans_name, eval_name in datasets:
        input_file = input_dir / input_name
        trans_file = trans_dir / trans_name
        eval_file = eval_dir / eval_name
        
        if not all(f.exists() for f in [input_file, trans_file, eval_file]):
            print(f"Skipping {name}: missing files")
            continue
        
        print(f"Processing {name}...")
        
        # Generate Markdown report
        generate_markdown_report(
            input_file,
            trans_file,
            eval_file,
            report_dir / f'{name}_sidebyside.md'
        )
        
        # Generate CSV
        generate_csv_scores(
            eval_file,
            report_dir / f'{name}_scores.csv'
        )
        
        print()
    
    print(f"✓ All reports saved to {report_dir}")

if __name__ == '__main__':
    main()
