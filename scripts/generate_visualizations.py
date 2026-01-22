#!/usr/bin/env python3
"""
Generate visualizations for translation evaluation results.
Creates bar charts, heatmaps, and comparison tables.
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11

def load_evaluation(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def plot_model_comparison(data, title, output_path):
    """Bar chart comparing models across all metrics."""
    models = list(data['by_model'].keys())
    metrics = list(data['by_model'][models[0]].keys())
    
    x = np.arange(len(metrics))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#2ecc71', '#3498db', '#e74c3c']  # Green, Blue, Red
    
    for i, model in enumerate(models):
        means = [data['by_model'][model][m]['mean'] for m in metrics]
        stds = [data['by_model'][model][m]['std'] for m in metrics]
        bars = ax.bar(x + i*width, means, width, label=model.upper(), 
                     color=colors[i], alpha=0.85, yerr=stds, capsize=3)
    
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(metrics, rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1.0)
    
    # Add gridlines
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def plot_heatmap(data, title, output_path):
    """Heatmap of model x metric scores."""
    models = list(data['by_model'].keys())
    metrics = list(data['by_model'][models[0]].keys())
    
    # Create matrix
    matrix = np.zeros((len(models), len(metrics)))
    for i, model in enumerate(models):
        for j, metric in enumerate(metrics):
            matrix[i, j] = data['by_model'][model][metric]['mean']
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    
    # Labels
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_yticks(np.arange(len(models)))
    ax.set_xticklabels(metrics, rotation=45, ha='right')
    ax.set_yticklabels([m.upper() for m in models])
    
    # Annotate cells
    for i in range(len(models)):
        for j in range(len(metrics)):
            text = ax.text(j, i, f'{matrix[i, j]:.3f}',
                          ha='center', va='center', color='black', fontsize=10)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Colorbar
    cbar = ax.figure.colorbar(im, ax=ax, shrink=0.8)
    cbar.ax.set_ylabel('Score', rotation=-90, va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def plot_per_chunk_scores(data, title, output_path):
    """Line plot showing score variation across chunks."""
    detailed = data.get('detailed_scores', [])
    if not detailed:
        return
    
    models = sorted(set(d['model_name'] for d in detailed))
    chunks = sorted(set(d['chunk_id'] for d in detailed), key=lambda x: int(x))
    
    # Focus on key metrics
    key_metrics = ['BLEU-4', 'COMET', 'BERTScore']
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    colors = {'claude': '#2ecc71', 'gemini': '#3498db', 'openai': '#e74c3c'}
    
    for ax, metric in zip(axes, key_metrics):
        for model in models:
            scores = []
            for chunk in chunks:
                for d in detailed:
                    if d['chunk_id'] == chunk and d['model_name'] == model:
                        scores.append(d['scores'].get(metric, 0))
                        break
            ax.plot(range(1, len(chunks)+1), scores, 'o-', 
                   label=model.upper(), color=colors[model], linewidth=2, markersize=6)
        
        ax.set_xlabel('Chunk')
        ax.set_ylabel('Score')
        ax.set_title(metric, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.set_xticks(range(1, len(chunks)+1))
        ax.set_ylim(0, 1.0)
        ax.grid(True, linestyle='--', alpha=0.7)
    
    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def plot_overall_rankings(datasets, output_path):
    """Combined bar chart showing rankings across datasets."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    colors = {'claude': '#2ecc71', 'gemini': '#3498db', 'openai': '#e74c3c'}
    
    for ax, (name, data) in zip(axes, datasets.items()):
        rankings = data['overall_rankings']
        models = [r[0] for r in rankings]
        scores = [r[1] for r in rankings]
        
        bars = ax.barh(models, scores, color=[colors[m] for m in models])
        ax.set_xlim(0, 0.8)
        ax.set_xlabel('Average Score')
        ax.set_title(name.replace('_', ' ').title(), fontweight='bold')
        
        # Add score labels
        for bar, score in zip(bars, scores):
            ax.text(score + 0.01, bar.get_y() + bar.get_height()/2,
                   f'{score:.4f}', va='center', fontsize=10)
    
    fig.suptitle('Overall Model Rankings', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def main():
    base_path = Path(__file__).parent.parent
    eval_dir = base_path / 'output' / 'evaluations'
    viz_dir = base_path / 'output' / 'visualizations'
    viz_dir.mkdir(exist_ok=True)
    
    print("Generating visualizations...")
    print()
    
    datasets = {}
    
    # Process each evaluation file
    for eval_file in eval_dir.glob('*_evaluation.json'):
        name = eval_file.stem.replace('_evaluation', '')
        print(f"Processing {name}...")
        
        data = load_evaluation(eval_file)
        datasets[name] = data
        
        # Generate visualizations
        plot_model_comparison(
            data, 
            f'{name.replace("_", " ").title()}: Model Comparison',
            viz_dir / f'{name}_comparison.png'
        )
        
        plot_heatmap(
            data,
            f'{name.replace("_", " ").title()}: Score Heatmap',
            viz_dir / f'{name}_heatmap.png'
        )
        
        plot_per_chunk_scores(
            data,
            f'{name.replace("_", " ").title()}: Per-Chunk Scores',
            viz_dir / f'{name}_per_chunk.png'
        )
        
        print()
    
    # Combined rankings
    if len(datasets) > 1:
        print("Generating combined visualizations...")
        plot_overall_rankings(datasets, viz_dir / 'combined_rankings.png')
    
    print()
    print(f"✓ All visualizations saved to {viz_dir}")

if __name__ == '__main__':
    main()
