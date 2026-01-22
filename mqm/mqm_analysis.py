#!/usr/bin/env python3
"""
MQM (Multidimensional Quality Metrics) Analysis
Comparing AI translations of Galen's Greek medical texts
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

# Create output directories
os.makedirs('charts', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Set style - clean academic look
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.labelsize': 13,
    'axes.titlesize': 15,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--'
})

# Load and clean data
def load_mqm_data(filepath):
    df = pd.read_csv(filepath, skiprows=2)
    # Clean column names
    df.columns = ['blank', 'Text', 'Chunk', 'Translation', 'Model', 'Word Count', 'APT', 'TQS',
                  'Neutral', 'Minor', 'Major', 'Critical', 
                  'Term_Accuracy', 'Term_Consistency', 'Term_Total',
                  'Acc_Mistranslation', 'Acc_Overtranslation', 'Acc_Undertranslation', 
                  'Acc_Addition', 'Acc_Omission', 'Acc_Total']
    df = df.drop('blank', axis=1)
    # Remove empty rows
    df = df.dropna(subset=['Text', 'Chunk', 'Model'])
    df['Chunk'] = df['Chunk'].astype(int)
    return df

# Load both datasets
comp_df = load_mqm_data('Comp MQM Summary Report Unblinded.xlsx - Summary.csv')
mix_df = load_mqm_data('Mixtures MQM Summary Report Unblinded.xlsx - Summary.csv')

# Combine
df = pd.concat([comp_df, mix_df], ignore_index=True)

# Model display names
MODEL_NAMES = {
    'claude': 'Claude',
    'gemini': 'Gemini',
    'openai': 'ChatGPT'
}

# Colors for models
MODEL_COLORS = {
    'claude': '#8B5CF6',  # Purple
    'gemini': '#10B981',  # Green
    'openai': '#3B82F6'   # Blue
}

print("=" * 80)
print("MQM ANALYSIS: AI TRANSLATION QUALITY OF GALEN'S GREEK MEDICAL TEXTS")
print("=" * 80)

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "=" * 80)
print("DATASET SUMMARY")
print("=" * 80)

print(f"\nTotal evaluations: {len(df)}")
print(f"Texts evaluated: {df['Text'].unique()}")
print(f"Chunks per text: {df['Chunk'].nunique()}")
print(f"Models: {df['Model'].unique()}")

# ============================================================================
# TQS BY MODEL (AGGREGATE)
# ============================================================================

print("\n" + "-" * 60)
print("TQS SCORES BY MODEL (Aggregate)")
print("-" * 60)

model_stats = df.groupby('Model')['TQS'].agg(['mean', 'std', 'min', 'max', 'count'])
model_stats = model_stats.sort_values('mean', ascending=False)

for model, row in model_stats.iterrows():
    print(f"\n{MODEL_NAMES[model]}:")
    print(f"  Mean TQS: {row['mean']:.2f}")
    print(f"  Std Dev:  {row['std']:.2f}")
    print(f"  Range:    {row['min']:.2f} - {row['max']:.2f}")
    print(f"  N:        {int(row['count'])}")

# ============================================================================
# TQS BY MODEL AND TEXT
# ============================================================================

print("\n" + "-" * 60)
print("TQS SCORES BY MODEL AND TEXT")
print("-" * 60)

for text in ['Comp', 'Mixtures']:
    print(f"\n{text}:")
    text_df = df[df['Text'] == text]
    text_stats = text_df.groupby('Model')['TQS'].agg(['mean', 'std'])
    text_stats = text_stats.sort_values('mean', ascending=False)
    for model, row in text_stats.iterrows():
        print(f"  {MODEL_NAMES[model]:10} Mean: {row['mean']:6.2f}  Std: {row['std']:6.2f}")

# ============================================================================
# TQS BY CHUNK (DETAILED)
# ============================================================================

print("\n" + "-" * 60)
print("TQS SCORES BY CHUNK")
print("-" * 60)

for text in ['Comp', 'Mixtures']:
    print(f"\n{text}:")
    print(f"{'Chunk':>6} | {'Claude':>10} | {'Gemini':>10} | {'ChatGPT':>10} | {'Best':>10}")
    print("-" * 60)
    
    text_df = df[df['Text'] == text]
    
    for chunk in sorted(text_df['Chunk'].unique()):
        chunk_df = text_df[text_df['Chunk'] == chunk]
        scores = {}
        for _, row in chunk_df.iterrows():
            scores[row['Model']] = row['TQS']
        
        best_model = max(scores, key=scores.get)
        
        print(f"{chunk:>6} | {scores.get('claude', 0):>10.2f} | {scores.get('gemini', 0):>10.2f} | {scores.get('openai', 0):>10.2f} | {MODEL_NAMES[best_model]:>10}")

# ============================================================================
# ERROR ANALYSIS
# ============================================================================

print("\n" + "-" * 60)
print("ERROR ANALYSIS BY MODEL")
print("-" * 60)

error_cols = ['Neutral', 'Minor', 'Major', 'Critical']
error_stats = df.groupby('Model')[error_cols].sum()

print("\nTotal Errors by Severity:")
print(error_stats)

print("\nMean Errors per Chunk:")
error_means = df.groupby('Model')[error_cols].mean()
print(error_means.round(2))

# ============================================================================
# CHART 1: TQS by Model (Box Plot)
# ============================================================================

def create_tqs_boxplot(data, filename):
    fig, ax = plt.subplots(figsize=(9, 6))
    
    models = ['claude', 'gemini', 'openai']
    positions = [0, 1, 2]
    
    box_data = [data[data['Model'] == m]['TQS'].values for m in models]
    
    bp = ax.boxplot(box_data, positions=positions, widths=0.5, patch_artist=True,
                    medianprops=dict(color='black', linewidth=2),
                    whiskerprops=dict(linewidth=1.5),
                    capprops=dict(linewidth=1.5))
    
    for patch, model in zip(bp['boxes'], models):
        patch.set_facecolor(MODEL_COLORS[model])
        patch.set_alpha(0.8)
        patch.set_edgecolor('black')
        patch.set_linewidth(1.5)
    
    # Add individual points with jitter
    np.random.seed(42)
    for i, model in enumerate(models):
        y = data[data['Model'] == model]['TQS'].values
        x = np.random.normal(i, 0.08, size=len(y))
        ax.scatter(x, y, alpha=0.7, color=MODEL_COLORS[model], 
                  edgecolor='black', linewidth=0.5, s=60, zorder=5)
    
    ax.set_xticks(positions)
    ax.set_xticklabels([MODEL_NAMES[m] for m in models], fontsize=13, fontweight='bold')
    ax.set_ylabel('Translation Quality Score (TQS)', fontsize=13)
    ax.set_ylim(-5, 110)
    ax.axhline(50, color='#d62828', linestyle='--', alpha=0.5, linewidth=1.5, label='50% threshold')
    
    # Add mean annotations with better positioning
    for i, model in enumerate(models):
        mean_val = data[data['Model'] == model]['TQS'].mean()
        ax.annotate(f'Mean: {mean_val:.1f}', xy=(i, 105), ha='center',
                   fontsize=11, fontweight='bold', color=MODEL_COLORS[model])
    
    ax.set_title('Translation Quality Score (TQS) Distribution by AI Model', 
                fontsize=15, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

create_tqs_boxplot(df, 'charts/chart1_tqs_boxplot.png')

# ============================================================================
# CHART 2: TQS by Chunk and Model (Heatmap)
# ============================================================================

def create_tqs_heatmap(data, filename):
    fig, axes = plt.subplots(1, 2, figsize=(12, 10), gridspec_kw={'wspace': 0.3})
    
    for ax_idx, text in enumerate(['Comp', 'Mixtures']):
        ax = axes[ax_idx]
        text_df = data[data['Text'] == text]
        
        # Create pivot table
        pivot = text_df.pivot(index='Chunk', columns='Model', values='TQS')
        pivot = pivot[['claude', 'gemini', 'openai']]  # Reorder columns
        
        # Create heatmap
        im = ax.imshow(pivot.values, cmap='RdYlGn', vmin=0, vmax=100, aspect=0.6)
        
        # Add text annotations
        for i in range(len(pivot)):
            for j in range(len(pivot.columns)):
                val = pivot.iloc[i, j]
                text_color = 'white' if val < 35 or val > 85 else 'black'
                ax.text(j, i, f'{val:.1f}', ha='center', va='center', 
                       fontsize=11, color=text_color, fontweight='bold')
        
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([MODEL_NAMES[m] for m in pivot.columns], fontsize=12, fontweight='bold')
        ax.set_yticks(range(len(pivot)))
        ax.set_yticklabels([f'Chunk {c}' for c in pivot.index], fontsize=11)
        ax.set_title(f'{text}', fontsize=14, fontweight='bold', pad=10)
        
        # Add gridlines
        ax.set_xticks(np.arange(-0.5, len(pivot.columns), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(pivot), 1), minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=2)
        ax.tick_params(which='minor', size=0)
    
    # Add colorbar on the right side with proper spacing
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('TQS (Translation Quality Score)', fontweight='bold', fontsize=12)
    cbar.set_ticks([0, 25, 50, 75, 100])
    cbar.set_ticklabels(['0\n(Poor)', '25', '50', '75', '100\n(Perfect)'])
    
    fig.suptitle('Translation Quality Score by Chunk and Model\n(Green = High Quality, Red = Low Quality)', 
                fontsize=15, fontweight='bold', y=0.98)
    
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

create_tqs_heatmap(df, 'charts/chart2_tqs_heatmap.png')

# ============================================================================
# CHART 3: TQS Line Plot by Chunk
# ============================================================================

def create_tqs_lineplot(data, filename):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    for ax_idx, text in enumerate(['Comp', 'Mixtures']):
        ax = axes[ax_idx]
        text_df = data[data['Text'] == text]
        
        for model in ['claude', 'gemini', 'openai']:
            model_df = text_df[text_df['Model'] == model].sort_values('Chunk')
            ax.plot(model_df['Chunk'], model_df['TQS'], 
                   marker='o', linewidth=2.5, markersize=9,
                   label=MODEL_NAMES[model], color=MODEL_COLORS[model],
                   markeredgecolor='white', markeredgewidth=1.5)
        
        ax.set_xlabel('Chunk Number', fontsize=12, fontweight='bold')
        ax.set_ylabel('Translation Quality Score (TQS)', fontsize=12, fontweight='bold')
        ax.set_title(f'{text}', fontsize=14, fontweight='bold', pad=10)
        ax.set_ylim(-5, 110)
        ax.set_xticks(range(1, 11))
        ax.axhline(50, color='#d62828', linestyle='--', alpha=0.5, linewidth=1.5)
        ax.axhspan(0, 50, alpha=0.1, color='red', label='Below threshold')
        ax.legend(loc='lower left', framealpha=0.9, fontsize=10)
    
    fig.suptitle('TQS Performance Across Text Chunks', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

create_tqs_lineplot(df, 'charts/chart3_tqs_lineplot.png')

# ============================================================================
# CHART 4: Error Breakdown by Model
# ============================================================================

def create_error_chart(data, filename):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Chart 1: Error severity (stacked bar)
    ax1 = axes[0]
    error_cols = ['Neutral', 'Minor', 'Major', 'Critical']
    error_colors = ['#90be6d', '#f9c74f', '#f8961e', '#d62828']
    
    models = ['claude', 'gemini', 'openai']
    x = np.arange(len(models))
    width = 0.6
    
    bottom = np.zeros(len(models))
    for col, color in zip(error_cols, error_colors):
        values = np.array([data[data['Model'] == m][col].sum() for m in models])
        ax1.bar(x, values, width, label=col, color=color, bottom=bottom, edgecolor='white', linewidth=1)
        bottom += values
    
    ax1.set_xticks(x)
    ax1.set_xticklabels([MODEL_NAMES[m] for m in models], fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Error Count', fontsize=12, fontweight='bold')
    ax1.set_title('Errors by Severity', fontsize=14, fontweight='bold', pad=10)
    ax1.legend(loc='upper right', framealpha=0.9)
    
    # Add total annotations
    for i, m in enumerate(models):
        total = sum(data[data['Model'] == m][col].sum() for col in error_cols)
        ax1.annotate(f'Total: {int(total)}', xy=(i, total + 2), ha='center', fontsize=10, fontweight='bold')
    
    # Chart 2: Error categories (grouped bar)
    ax2 = axes[1]
    cat_cols = ['Term_Total', 'Acc_Total']
    cat_labels = ['Terminology', 'Accuracy']
    cat_colors = ['#457b9d', '#e63946']
    
    width = 0.35
    for i, (col, label, color) in enumerate(zip(cat_cols, cat_labels, cat_colors)):
        values = [data[data['Model'] == m][col].sum() for m in models]
        bars = ax2.bar(x + (i - 0.5) * width, values, width, label=label, color=color, 
                      edgecolor='white', linewidth=1)
        # Add value labels
        for bar, val in zip(bars, values):
            ax2.annotate(f'{int(val)}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax2.set_xticks(x)
    ax2.set_xticklabels([MODEL_NAMES[m] for m in models], fontsize=12, fontweight='bold')
    ax2.set_ylabel('Total Error Count', fontsize=12, fontweight='bold')
    ax2.set_title('Errors by Category', fontsize=14, fontweight='bold', pad=10)
    ax2.legend(loc='upper right', framealpha=0.9)
    
    fig.suptitle('Error Analysis by AI Model', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

create_error_chart(df, 'charts/chart4_error_breakdown.png')

# ============================================================================
# STATISTICAL COMPARISONS
# ============================================================================

print("\n" + "=" * 80)
print("STATISTICAL COMPARISONS")
print("=" * 80)

models = ['claude', 'gemini', 'openai']

print("\nPairwise t-tests on TQS scores:")
print("-" * 50)

for i, m1 in enumerate(models):
    for m2 in models[i+1:]:
        scores1 = df[df['Model'] == m1]['TQS']
        scores2 = df[df['Model'] == m2]['TQS']
        
        t_stat, p_val = stats.ttest_ind(scores1, scores2)
        
        diff = scores1.mean() - scores2.mean()
        winner = MODEL_NAMES[m1] if diff > 0 else MODEL_NAMES[m2]
        
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        
        print(f"\n{MODEL_NAMES[m1]} vs {MODEL_NAMES[m2]}:")
        print(f"  Mean difference: {abs(diff):.2f} (favors {winner})")
        print(f"  t-statistic: {t_stat:.3f}")
        print(f"  p-value: {p_val:.4f} {sig}")

# ANOVA
print("\n" + "-" * 50)
print("One-way ANOVA:")
groups = [df[df['Model'] == m]['TQS'].values for m in models]
f_stat, p_val = stats.f_oneway(*groups)
print(f"  F-statistic: {f_stat:.3f}")
print(f"  p-value: {p_val:.4f}")

# ============================================================================
# MODEL RANKINGS BY CHUNK
# ============================================================================

print("\n" + "=" * 80)
print("MODEL RANKINGS BY CHUNK")
print("=" * 80)

win_counts = {m: 0 for m in models}
tie_counts = 0

for text in ['Comp', 'Mixtures']:
    text_df = df[df['Text'] == text]
    for chunk in text_df['Chunk'].unique():
        chunk_df = text_df[text_df['Chunk'] == chunk]
        scores = {row['Model']: row['TQS'] for _, row in chunk_df.iterrows()}
        max_score = max(scores.values())
        winners = [m for m, s in scores.items() if s == max_score]
        
        if len(winners) == 1:
            win_counts[winners[0]] += 1
        else:
            tie_counts += 1

print("\nChunks where each model had highest TQS:")
for model in sorted(win_counts, key=win_counts.get, reverse=True):
    print(f"  {MODEL_NAMES[model]}: {win_counts[model]} chunks")
print(f"  Ties: {tie_counts} chunks")

# ============================================================================
# GENERATE HUMAN-READABLE REPORT
# ============================================================================

# Calculate additional statistics for the report
overall_mean = df['TQS'].mean()
overall_std = df['TQS'].std()

# Identify problematic chunks (TQS < 70 for any model)
problem_chunks = []
for text in ['Comp', 'Mixtures']:
    text_df = df[df['Text'] == text]
    for chunk in text_df['Chunk'].unique():
        chunk_df = text_df[text_df['Chunk'] == chunk]
        min_tqs = chunk_df['TQS'].min()
        if min_tqs < 70:
            problem_chunks.append((text, chunk, min_tqs))

report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     MQM ANALYSIS REPORT: AI TRANSLATION QUALITY OF GALEN'S MEDICAL TEXTS     ║
╚══════════════════════════════════════════════════════════════════════════════╝

EXECUTIVE SUMMARY
─────────────────
This report presents a Multidimensional Quality Metrics (MQM) analysis of AI 
translations of Galen's ancient Greek medical texts. Three leading AI models 
were evaluated: Claude (Anthropic), Gemini (Google), and ChatGPT (OpenAI).

Key Metrics:
• TQS (Translation Quality Score): 0-100 scale where higher = better quality
• APT (Accumulated Penalty Total): Sum of weighted error penalties
• Error categories: Neutral, Minor, Major, Critical severity levels

═══════════════════════════════════════════════════════════════════════════════
                              DATASET OVERVIEW
═══════════════════════════════════════════════════════════════════════════════

    Source Texts:        {', '.join(df['Text'].unique())}
    Chunks per Text:     {df['Chunk'].nunique()}
    Total Evaluations:   {len(df)}
    Overall Mean TQS:    {overall_mean:.2f}
    Overall Std Dev:     {overall_std:.2f}

═══════════════════════════════════════════════════════════════════════════════
                           1. OVERALL MODEL RANKINGS
═══════════════════════════════════════════════════════════════════════════════

    ┌─────────────┬──────────┬──────────┬─────────────────┐
    │ Model       │ Mean TQS │ Std Dev  │ Range           │
    ├─────────────┼──────────┼──────────┼─────────────────┤
"""

for model, row in model_stats.iterrows():
    report += f"    │ {MODEL_NAMES[model]:<11} │ {row['mean']:>8.2f} │ {row['std']:>8.2f} │ {row['min']:>6.1f} - {row['max']:<6.1f} │\n"

report += """    └─────────────┴──────────┴──────────┴─────────────────┘

Interpretation: """

# Determine the ranking
ranked_models = model_stats.sort_values('mean', ascending=False).index.tolist()
report += f"{MODEL_NAMES[ranked_models[0]]} achieves the highest mean TQS, followed by "
report += f"{MODEL_NAMES[ranked_models[1]]} and {MODEL_NAMES[ranked_models[2]]}.\n"

report += """
═══════════════════════════════════════════════════════════════════════════════
                          2. PERFORMANCE BY SOURCE TEXT
═══════════════════════════════════════════════════════════════════════════════
"""

for text in ['Comp', 'Mixtures']:
    report += f"\n    {text} (De Compositione / On Mixtures):\n"
    report += "    ─────────────────────────────────────\n"
    text_df = df[df['Text'] == text]
    text_stats = text_df.groupby('Model')['TQS'].agg(['mean', 'std'])
    text_stats = text_stats.sort_values('mean', ascending=False)
    for model, row in text_stats.iterrows():
        bar_len = int(row['mean'] / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        report += f"    {MODEL_NAMES[model]:<10} │{bar}│ {row['mean']:.1f} (±{row['std']:.1f})\n"

report += """
═══════════════════════════════════════════════════════════════════════════════
                        3. CHUNK-BY-CHUNK TQS BREAKDOWN
═══════════════════════════════════════════════════════════════════════════════
"""

for text in ['Comp', 'Mixtures']:
    report += f"\n    {text}:\n"
    report += "    ┌────────┬──────────┬──────────┬──────────┬────────────┐\n"
    report += "    │ Chunk  │  Claude  │  Gemini  │ ChatGPT  │   Winner   │\n"
    report += "    ├────────┼──────────┼──────────┼──────────┼────────────┤\n"
    
    text_df = df[df['Text'] == text]
    
    for chunk in sorted(text_df['Chunk'].unique()):
        chunk_df = text_df[text_df['Chunk'] == chunk]
        scores = {row['Model']: row['TQS'] for _, row in chunk_df.iterrows()}
        best_model = max(scores, key=scores.get)
        
        # Mark low scores
        c_score = scores.get('claude', 0)
        g_score = scores.get('gemini', 0)
        o_score = scores.get('openai', 0)
        
        c_str = f"{c_score:>6.1f}{'*' if c_score < 70 else ' '}"
        g_str = f"{g_score:>6.1f}{'*' if g_score < 70 else ' '}"
        o_str = f"{o_score:>6.1f}{'*' if o_score < 70 else ' '}"
        
        report += f"    │   {chunk:<4} │ {c_str}  │ {g_str}  │ {o_str}  │ {MODEL_NAMES[best_model]:<10} │\n"
    
    report += "    └────────┴──────────┴──────────┴──────────┴────────────┘\n"
    report += "    (* indicates TQS below 70 - potential quality concern)\n"

report += """
═══════════════════════════════════════════════════════════════════════════════
                             4. MODEL WIN COUNTS
═══════════════════════════════════════════════════════════════════════════════

    Number of chunks where each model achieved the highest TQS:
"""

for model in sorted(win_counts, key=win_counts.get, reverse=True):
    pct = win_counts[model] / 20 * 100
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    report += f"    {MODEL_NAMES[model]:<10} │{bar}│ {win_counts[model]} chunks ({pct:.0f}%)\n"
if tie_counts > 0:
    report += f"    Ties: {tie_counts} chunks\n"

report += """
═══════════════════════════════════════════════════════════════════════════════
                              5. ERROR ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

    Total Errors by Severity (across all 20 chunks):

    ┌─────────────┬──────────┬────────┬────────┬──────────┬─────────┐
    │ Model       │ Neutral  │ Minor  │ Major  │ Critical │  TOTAL  │
    ├─────────────┼──────────┼────────┼────────┼──────────┼─────────┤
"""

for model in models:
    m_df = df[df['Model'] == model]
    n = m_df['Neutral'].sum()
    mi = m_df['Minor'].sum()
    ma = m_df['Major'].sum()
    cr = m_df['Critical'].sum()
    tot = n + mi + ma + cr
    report += f"    │ {MODEL_NAMES[model]:<11} │ {n:>8.0f} │ {mi:>6.0f} │ {ma:>6.0f} │ {cr:>8.0f} │ {tot:>7.0f} │\n"

report += """    └─────────────┴──────────┴────────┴────────┴──────────┴─────────┘

    Error Categories:
    
    ┌─────────────┬─────────────────┬──────────────┐
    │ Model       │ Terminology     │ Accuracy     │
    ├─────────────┼─────────────────┼──────────────┤
"""

for model in models:
    m_df = df[df['Model'] == model]
    term = m_df['Term_Total'].sum()
    acc = m_df['Acc_Total'].sum()
    report += f"    │ {MODEL_NAMES[model]:<11} │ {term:>15.0f} │ {acc:>12.0f} │\n"

report += """    └─────────────┴─────────────────┴──────────────┘
"""

report += """
═══════════════════════════════════════════════════════════════════════════════
                          6. STATISTICAL COMPARISONS
═══════════════════════════════════════════════════════════════════════════════
"""

for i, m1 in enumerate(models):
    for m2 in models[i+1:]:
        scores1 = df[df['Model'] == m1]['TQS']
        scores2 = df[df['Model'] == m2]['TQS']
        t_stat, p_val = stats.ttest_ind(scores1, scores2)
        diff = scores1.mean() - scores2.mean()
        winner = MODEL_NAMES[m1] if diff > 0 else MODEL_NAMES[m2]
        
        if p_val < 0.001:
            sig = "★★★ Highly significant (p < 0.001)"
        elif p_val < 0.01:
            sig = "★★ Very significant (p < 0.01)"
        elif p_val < 0.05:
            sig = "★ Significant (p < 0.05)"
        else:
            sig = "Not statistically significant"
        
        report += f"""
    {MODEL_NAMES[m1]} vs {MODEL_NAMES[m2]}:
    ──────────────────────────────
    • Mean difference: {abs(diff):.2f} points (favors {winner})
    • t-statistic: {t_stat:.3f}
    • p-value: {p_val:.4f}
    • Result: {sig}
"""

if problem_chunks:
    report += """
═══════════════════════════════════════════════════════════════════════════════
                         7. CHUNKS REQUIRING ATTENTION
═══════════════════════════════════════════════════════════════════════════════

    The following chunks had at least one model score below 70 (potential issues):
"""
    for text, chunk, min_tqs in sorted(problem_chunks, key=lambda x: x[2]):
        report += f"    • {text} Chunk {chunk}: lowest TQS = {min_tqs:.1f}\n"

report += """
═══════════════════════════════════════════════════════════════════════════════
                              GENERATED OUTPUTS
═══════════════════════════════════════════════════════════════════════════════

    Charts (in charts/ folder):
    ─────────────────────────────
    1. chart1_tqs_boxplot.png    - TQS distribution by model
    2. chart2_tqs_heatmap.png    - Chunk-by-chunk TQS heatmap
    3. chart3_tqs_lineplot.png   - TQS trajectory across chunks
    4. chart4_error_breakdown.png - Error analysis by severity/category

    Reports (in reports/ folder):
    ─────────────────────────────
    1. mqm_analysis_report.txt   - This report

═══════════════════════════════════════════════════════════════════════════════
"""

with open('reports/mqm_analysis_report.txt', 'w') as f:
    f.write(report)
print("\nSaved: reports/mqm_analysis_report.txt")

print(report)
print("\nMQM Analysis complete!")
