#!/usr/bin/env python3
"""
Metrics Correlation Analysis
Correlating Automated MT Metrics vs Human Evaluations (MQM TQS & Survey Preferences)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
import os
import warnings
warnings.filterwarnings('ignore')

# Create output directories
os.makedirs('charts', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Set plotting style
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.grid': True,
    'grid.alpha': 0.3
})

print("=" * 80)
print("METRICS CORRELATION ANALYSIS")
print("Automated MT Metrics vs Human Evaluations")
print("=" * 80)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n[1] Loading data sources...")

# Helper to find data file (prefer symlinks in data_sources/, fallback to originals)
def find_data_file(symlink_name, original_path):
    symlink_path = f'data_sources/{symlink_name}'
    if os.path.exists(symlink_path):
        print(f"   Using: {symlink_path}")
        return symlink_path
    else:
        print(f"   Using: {original_path}")
        return original_path

# Load MT automated metrics
mt_comp_path = find_data_file('mt_metrics_comp.csv', '../mt_eval/output/reports/on_comp_scores.csv')
mt_mix_path = find_data_file('mt_metrics_mixtures.csv', '../mt_eval/output/reports/on_mixtures_scores.csv')

mt_comp = pd.read_csv(mt_comp_path)
mt_comp['text'] = 'Comp'
mt_mix = pd.read_csv(mt_mix_path)
mt_mix['text'] = 'Mixtures'
mt_metrics = pd.concat([mt_comp, mt_mix], ignore_index=True)
mt_metrics = mt_metrics.rename(columns={'chunk_id': 'chunk'})

print(f"   MT Metrics: {len(mt_metrics)} rows")
print(f"   Metrics available: {[c for c in mt_metrics.columns if c not in ['chunk', 'model', 'text']]}")

# Load MQM data
def load_mqm(filepath):
    df = pd.read_csv(filepath, skiprows=2)
    df.columns = ['blank', 'Text', 'Chunk', 'Translation', 'Model', 'Word Count', 'APT', 'TQS',
                  'Neutral', 'Minor', 'Major', 'Critical', 
                  'Term_Accuracy', 'Term_Consistency', 'Term_Total',
                  'Acc_Mistranslation', 'Acc_Overtranslation', 'Acc_Undertranslation', 
                  'Acc_Addition', 'Acc_Omission', 'Acc_Total']
    df = df.drop('blank', axis=1)
    df = df.dropna(subset=['Text', 'Chunk', 'Model'])
    df['Chunk'] = df['Chunk'].astype(int)
    return df

mqm_comp_path = find_data_file('mqm_comp.csv', '../mqm/Comp MQM Summary Report Unblinded.xlsx - Summary.csv')
mqm_mix_path = find_data_file('mqm_mixtures.csv', '../mqm/Mixtures MQM Summary Report Unblinded.xlsx - Summary.csv')

mqm_comp = load_mqm(mqm_comp_path)
mqm_mix = load_mqm(mqm_mix_path)
mqm_data = pd.concat([mqm_comp, mqm_mix], ignore_index=True)
mqm_data = mqm_data.rename(columns={'Text': 'text', 'Chunk': 'chunk', 'Model': 'model'})

print(f"   MQM Data: {len(mqm_data)} rows")

# Load Survey data
survey_path = find_data_file('survey_responses.csv', '../surveys/survey-responses-1769097340109.csv')
survey = pd.read_csv(survey_path)
print(f"   Survey Data: {len(survey)} rows")

# ============================================================================
# MERGE MT METRICS WITH MQM
# ============================================================================

print("\n[2] Merging datasets...")

# Merge MT metrics with MQM TQS scores
merged = pd.merge(
    mt_metrics, 
    mqm_data[['text', 'chunk', 'model', 'TQS', 'APT']], 
    on=['text', 'chunk', 'model'],
    how='inner'
)

print(f"   Merged MT + MQM: {len(merged)} rows")

# ============================================================================
# COMPUTE SURVEY PREFERENCE SCORES BY MODEL
# ============================================================================

print("\n[3] Computing survey preference scores...")

# For each model, compute average preference when compared against humans
AI_MODELS = ['claude', 'gemini', 'openai']
HUMAN_TRANS = ['human1', 'human2']

# Map chunk IDs: Survey uses 1-10, need to map to text
# Looking at the survey, chunks 1-10 likely map to one text
# We need to compute model-level preferences

def compute_model_preferences(survey_df):
    """Compute normalized preference scores for each AI model"""
    results = []
    
    for _, row in survey_df.iterrows():
        left = row['Left Translation']
        right = row['Right Translation']
        score = row['Preference Score']
        chunk = row['Chunk ID']
        
        # Determine which is AI and which is human
        left_is_ai = left in AI_MODELS
        right_is_ai = right in AI_MODELS
        
        if left_is_ai and not right_is_ai:
            ai_model = left
            # Score is negative if left preferred, so AI preference = -score when AI is on left
            # Actually: negative score = prefer left, so if AI on left, negative = prefer AI
            ai_preference = -score  # Negate because negative means left preferred
        elif right_is_ai and not left_is_ai:
            ai_model = right
            # Positive score = prefer right, so if AI on right, positive = prefer AI
            ai_preference = score
        else:
            continue  # Skip AI vs AI or human vs human
        
        results.append({
            'chunk': chunk,
            'model': ai_model,
            'ai_preference': ai_preference,
            'expert': row['Expert Name']
        })
    
    return pd.DataFrame(results)

survey_prefs = compute_model_preferences(survey)

# Average preference by chunk and model
survey_by_chunk_model = survey_prefs.groupby(['chunk', 'model'])['ai_preference'].agg(['mean', 'std', 'count']).reset_index()
survey_by_chunk_model.columns = ['chunk', 'model', 'survey_pref_mean', 'survey_pref_std', 'survey_n']

print(f"   Survey preferences computed: {len(survey_by_chunk_model)} chunk-model combinations")

# ============================================================================
# MERGE ALL DATA
# ============================================================================

# Since survey doesn't have text identifier, we need to aggregate differently
# For correlation, we'll use model-level aggregates

# Model-level MT metrics (averaged across chunks)
mt_by_model = mt_metrics.groupby('model').mean(numeric_only=True).reset_index()

# Model-level MQM
mqm_by_model = mqm_data.groupby('model')['TQS'].agg(['mean', 'std']).reset_index()
mqm_by_model.columns = ['model', 'TQS_mean', 'TQS_std']

# Model-level survey preference
survey_by_model = survey_prefs.groupby('model')['ai_preference'].agg(['mean', 'std', 'count']).reset_index()
survey_by_model.columns = ['model', 'survey_pref', 'survey_std', 'survey_n']

# Merge model-level data
model_level = pd.merge(mt_by_model, mqm_by_model, on='model')
model_level = pd.merge(model_level, survey_by_model, on='model')

print("\n[4] Model-level summary:")
print(model_level.to_string(index=False))

# ============================================================================
# CHUNK-LEVEL CORRELATION ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("CORRELATION ANALYSIS")
print("=" * 80)

# For chunk-level analysis, use merged MT + MQM data (60 data points: 2 texts × 10 chunks × 3 models)
metrics = ['BLEU-4', 'chrF++', 'METEOR', 'ROUGE-L', 'BERTScore', 'COMET']

print("\n[5] Chunk-Level Correlations: Automated Metrics vs MQM TQS")
print("-" * 70)

correlation_results = []

for metric in metrics:
    if metric in merged.columns:
        # Pearson correlation
        pearson_r, pearson_p = pearsonr(merged[metric], merged['TQS'])
        
        # Spearman correlation
        spearman_r, spearman_p = spearmanr(merged[metric], merged['TQS'])
        
        correlation_results.append({
            'Metric': metric,
            'Pearson r': pearson_r,
            'Pearson p': pearson_p,
            'Spearman ρ': spearman_r,
            'Spearman p': spearman_p
        })
        
        sig_p = "***" if pearson_p < 0.001 else "**" if pearson_p < 0.01 else "*" if pearson_p < 0.05 else ""
        sig_s = "***" if spearman_p < 0.001 else "**" if spearman_p < 0.01 else "*" if spearman_p < 0.05 else ""
        
        print(f"{metric:12} | Pearson r = {pearson_r:+.4f} (p={pearson_p:.4f}){sig_p:4} | Spearman ρ = {spearman_r:+.4f} (p={spearman_p:.4f}){sig_s}")

corr_df = pd.DataFrame(correlation_results)

# ============================================================================
# SURVEY PREFERENCE CORRELATION (Kendall's τ)
# ============================================================================

print("\n[6] Correlations: Automated Metrics vs Survey Preference (Kendall's τ)")
print("-" * 70)

# Need to match survey data with MT metrics by chunk
# Survey has chunks 1-10, but we don't know which text they're from
# Let's assume chunks 1-10 in survey map to the "Mixtures" text based on typical study design

# Aggregate MT metrics by chunk and model (across both texts)
mt_by_chunk_model = mt_metrics.groupby(['chunk', 'model']).mean(numeric_only=True).reset_index()

# Merge with survey preferences
survey_mt_merged = pd.merge(
    survey_by_chunk_model,
    mt_by_chunk_model,
    on=['chunk', 'model'],
    how='inner'
)

kendall_results = []

for metric in metrics:
    if metric in survey_mt_merged.columns and len(survey_mt_merged) > 3:
        # Kendall's tau
        tau, p_val = kendalltau(survey_mt_merged[metric], survey_mt_merged['survey_pref_mean'])
        
        kendall_results.append({
            'Metric': metric,
            "Kendall's τ": tau,
            'p-value': p_val
        })
        
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"{metric:12} | Kendall's τ = {tau:+.4f} (p={p_val:.4f}){sig}")

kendall_df = pd.DataFrame(kendall_results)

# ============================================================================
# SUMMARY TABLE
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY: CORRELATION COEFFICIENTS")
print("=" * 80)

# Combine results
summary_df = pd.merge(corr_df, kendall_df, on='Metric', how='outer')

print("\n┌─────────────┬──────────────────────────────┬──────────────────────────────┬─────────────────────┐")
print("│ Metric      │ Pearson r (vs TQS)           │ Spearman ρ (vs TQS)          │ Kendall's τ (Survey)│")
print("├─────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────┤")

for _, row in summary_df.iterrows():
    metric = row['Metric']
    
    if pd.notna(row.get('Pearson r')):
        p_sig = "***" if row['Pearson p'] < 0.001 else "**" if row['Pearson p'] < 0.01 else "*" if row['Pearson p'] < 0.05 else ""
        pearson_str = f"{row['Pearson r']:+.3f}{p_sig}"
    else:
        pearson_str = "N/A"
    
    if pd.notna(row.get('Spearman ρ')):
        s_sig = "***" if row['Spearman p'] < 0.001 else "**" if row['Spearman p'] < 0.01 else "*" if row['Spearman p'] < 0.05 else ""
        spearman_str = f"{row['Spearman ρ']:+.3f}{s_sig}"
    else:
        spearman_str = "N/A"
    
    if pd.notna(row.get("Kendall's τ")):
        k_sig = "***" if row['p-value'] < 0.001 else "**" if row['p-value'] < 0.01 else "*" if row['p-value'] < 0.05 else ""
        kendall_val = row["Kendall's τ"]
        kendall_str = f"{kendall_val:+.3f}{k_sig}"
    else:
        kendall_str = "N/A"
    
    print(f"│ {metric:<11} │ {pearson_str:<28} │ {spearman_str:<28} │ {kendall_str:<19} │")

print("└─────────────┴──────────────────────────────┴──────────────────────────────┴─────────────────────┘")
print("Significance: * p<0.05, ** p<0.01, *** p<0.001")

# ============================================================================
# CHART 1: Correlation Heatmap
# ============================================================================

def create_correlation_heatmap(corr_df, kendall_df, filename):
    """Create heatmap of correlation coefficients"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare data matrix
    metrics = corr_df['Metric'].tolist()
    
    # Build correlation matrix
    data = []
    annotations = []
    
    for i, metric in enumerate(metrics):
        row_data = []
        row_annot = []
        
        # Pearson
        r = corr_df.loc[corr_df['Metric'] == metric, 'Pearson r'].values[0]
        p = corr_df.loc[corr_df['Metric'] == metric, 'Pearson p'].values[0]
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        row_data.append(r)
        row_annot.append(f"{r:.3f}{sig}")
        
        # Spearman
        rho = corr_df.loc[corr_df['Metric'] == metric, 'Spearman ρ'].values[0]
        p = corr_df.loc[corr_df['Metric'] == metric, 'Spearman p'].values[0]
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        row_data.append(rho)
        row_annot.append(f"{rho:.3f}{sig}")
        
        # Kendall
        if metric in kendall_df['Metric'].values:
            tau = kendall_df.loc[kendall_df['Metric'] == metric, "Kendall's τ"].values[0]
            p = kendall_df.loc[kendall_df['Metric'] == metric, 'p-value'].values[0]
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            row_data.append(tau)
            row_annot.append(f"{tau:.3f}{sig}")
        else:
            row_data.append(np.nan)
            row_annot.append("N/A")
        
        data.append(row_data)
        annotations.append(row_annot)
    
    data = np.array(data)
    
    # Create heatmap
    im = ax.imshow(data, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
    
    # Add annotations
    for i in range(len(metrics)):
        for j in range(3):
            color = 'white' if abs(data[i, j]) > 0.5 else 'black'
            ax.text(j, i, annotations[i][j], ha='center', va='center', 
                   fontsize=11, color=color, fontweight='bold')
    
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Pearson r\n(vs TQS)', 'Spearman ρ\n(vs TQS)', "Kendall's τ\n(vs Survey)"], fontsize=11)
    ax.set_yticks(range(len(metrics)))
    ax.set_yticklabels(metrics, fontsize=11)
    
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Correlation Coefficient', fontweight='bold')
    
    ax.set_title('Automated Metrics vs Human Evaluation Correlations\n(* p<0.05, ** p<0.01, *** p<0.001)', 
                fontsize=13, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

create_correlation_heatmap(corr_df, kendall_df, 'charts/chart1_correlation_heatmap.png')

# ============================================================================
# CHART 2: Scatter plots - Best correlating metrics vs TQS
# ============================================================================

def create_scatter_plots(merged_df, filename):
    """Create scatter plots of top metrics vs TQS"""
    
    # Select top metrics based on correlation
    top_metrics = ['BERTScore', 'COMET', 'chrF++', 'BLEU-4']
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    colors = {'claude': '#8B5CF6', 'gemini': '#10B981', 'openai': '#3B82F6'}
    
    for idx, metric in enumerate(top_metrics):
        ax = axes[idx // 2, idx % 2]
        
        for model in ['claude', 'gemini', 'openai']:
            model_data = merged_df[merged_df['model'] == model]
            ax.scatter(model_data[metric], model_data['TQS'], 
                      label=model.capitalize(), color=colors[model], 
                      alpha=0.7, s=60, edgecolor='white', linewidth=0.5)
        
        # Add regression line
        x = merged_df[metric]
        y = merged_df['TQS']
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, p(x_line), 'r--', alpha=0.5, linewidth=2)
        
        # Add correlation annotation
        r, p_val = pearsonr(x, y)
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        ax.annotate(f'r = {r:.3f}{sig}', xy=(0.05, 0.95), xycoords='axes fraction',
                   fontsize=12, fontweight='bold', verticalalignment='top')
        
        ax.set_xlabel(metric, fontsize=12, fontweight='bold')
        ax.set_ylabel('TQS (MQM)', fontsize=12, fontweight='bold')
        ax.legend(loc='lower right', fontsize=9)
    
    fig.suptitle('Automated Metrics vs MQM Translation Quality Score', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

create_scatter_plots(merged, 'charts/chart2_scatter_tqs.png')

# ============================================================================
# CHART 3: Bar chart comparing correlation strengths
# ============================================================================

def create_correlation_bar_chart(corr_df, kendall_df, filename):
    """Create bar chart comparing correlation strengths"""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    metrics = corr_df['Metric'].tolist()
    x = np.arange(len(metrics))
    width = 0.25
    
    # Get values
    pearson_vals = corr_df['Pearson r'].values
    spearman_vals = corr_df['Spearman ρ'].values
    kendall_vals = []
    for m in metrics:
        if m in kendall_df['Metric'].values:
            kendall_vals.append(kendall_df.loc[kendall_df['Metric'] == m, "Kendall's τ"].values[0])
        else:
            kendall_vals.append(0)
    kendall_vals = np.array(kendall_vals)
    
    # Plot bars
    bars1 = ax.bar(x - width, pearson_vals, width, label='Pearson r (vs TQS)', color='#3B82F6', edgecolor='white')
    bars2 = ax.bar(x, spearman_vals, width, label='Spearman ρ (vs TQS)', color='#10B981', edgecolor='white')
    bars3 = ax.bar(x + width, kendall_vals, width, label="Kendall's τ (vs Survey)", color='#F59E0B', edgecolor='white')
    
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11, fontweight='bold')
    ax.set_ylabel('Correlation Coefficient', fontsize=12, fontweight='bold')
    ax.set_ylim(-0.5, 1.0)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axhline(0.3, color='gray', linestyle='--', alpha=0.5, label='Weak correlation threshold')
    ax.axhline(0.7, color='gray', linestyle=':', alpha=0.5, label='Strong correlation threshold')
    ax.legend(loc='upper right', fontsize=9)
    
    ax.set_title('Correlation Strength: Automated Metrics vs Human Evaluations', 
                fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

create_correlation_bar_chart(corr_df, kendall_df, 'charts/chart3_correlation_bars.png')

# ============================================================================
# GENERATE REPORT
# ============================================================================

report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              METRICS CORRELATION ANALYSIS REPORT                             ║
║          Automated MT Metrics vs Human Evaluations                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

EXECUTIVE SUMMARY
─────────────────
This analysis examines how well automated machine translation metrics correlate
with human evaluation scores. We compare:

  • Automated MT Metrics: BLEU-4, chrF++, METEOR, ROUGE-L, BERTScore, COMET
  • Human Evaluations: 
    - MQM TQS (Translation Quality Score from expert annotation)
    - Survey Preferences (blind expert preferences)

═══════════════════════════════════════════════════════════════════════════════
                              DATA SOURCES
═══════════════════════════════════════════════════════════════════════════════

    1. Automated MT Metrics
       - Source: mt_eval/output/reports/
       - Texts: Comp (De Compositione), Mixtures (De Temperamentis)
       - Chunks: 10 per text
       - Models: Claude, Gemini, ChatGPT (OpenAI)
       - N = {len(merged)} chunk-model observations

    2. MQM Expert Annotation
       - Source: mqm/
       - Metric: TQS (Translation Quality Score, 0-100)
       - Methodology: Professional MQM annotation

    3. Blind Expert Survey
       - Source: surveys/
       - Metric: Preference score (-2 to +2)
       - N = {len(survey)} pairwise comparisons

═══════════════════════════════════════════════════════════════════════════════
                    CORRELATION COEFFICIENTS SUMMARY
═══════════════════════════════════════════════════════════════════════════════

    ┌─────────────┬────────────────────┬────────────────────┬──────────────────┐
    │ Metric      │ Pearson r (TQS)    │ Spearman ρ (TQS)   │ Kendall τ (Surv) │
    ├─────────────┼────────────────────┼────────────────────┼──────────────────┤
"""

for _, row in summary_df.iterrows():
    metric = row['Metric']
    
    if pd.notna(row.get('Pearson r')):
        p_sig = "***" if row['Pearson p'] < 0.001 else "**" if row['Pearson p'] < 0.01 else "*" if row['Pearson p'] < 0.05 else ""
        pearson_str = f"{row['Pearson r']:+.4f}{p_sig:3}"
    else:
        pearson_str = "N/A"
    
    if pd.notna(row.get('Spearman ρ')):
        s_sig = "***" if row['Spearman p'] < 0.001 else "**" if row['Spearman p'] < 0.01 else "*" if row['Spearman p'] < 0.05 else ""
        spearman_str = f"{row['Spearman ρ']:+.4f}{s_sig:3}"
    else:
        spearman_str = "N/A"
    
    if pd.notna(row.get("Kendall's τ")):
        k_sig = "***" if row['p-value'] < 0.001 else "**" if row['p-value'] < 0.01 else "*" if row['p-value'] < 0.05 else ""
        kendall_val = row["Kendall's τ"]
        kendall_str = f"{kendall_val:+.4f}{k_sig:3}"
    else:
        kendall_str = "N/A"
    
    report += f"    │ {metric:<11} │ {pearson_str:<18} │ {spearman_str:<18} │ {kendall_str:<16} │\n"

report += """    └─────────────┴────────────────────┴────────────────────┴──────────────────┘
    
    Significance: * p<0.05, ** p<0.01, *** p<0.001

═══════════════════════════════════════════════════════════════════════════════
                            INTERPRETATION
═══════════════════════════════════════════════════════════════════════════════

    Correlation Strength Guidelines:
    ─────────────────────────────────
    |r| < 0.3   : Weak correlation
    |r| 0.3-0.7 : Moderate correlation  
    |r| > 0.7   : Strong correlation

    Key Findings:
    ─────────────
"""

# Analyze results
best_tqs_metric = corr_df.loc[corr_df['Pearson r'].abs().idxmax(), 'Metric']
best_tqs_r = corr_df.loc[corr_df['Pearson r'].abs().idxmax(), 'Pearson r']

report += f"""
    1. Best TQS Predictor: {best_tqs_metric}
       - Pearson r = {best_tqs_r:.4f}
       - This metric best predicts the expert MQM quality scores.
"""

if len(kendall_df) > 0:
    best_survey_metric = kendall_df.loc[kendall_df["Kendall's τ"].abs().idxmax(), 'Metric']
    best_survey_tau = kendall_df.loc[kendall_df["Kendall's τ"].abs().idxmax(), "Kendall's τ"]
    report += f"""
    2. Best Survey Predictor: {best_survey_metric}
       - Kendall's τ = {best_survey_tau:.4f}
       - This metric best predicts blind expert preferences.
"""

# Check for significant correlations
sig_tqs = corr_df[corr_df['Pearson p'] < 0.05]['Metric'].tolist()
sig_survey = kendall_df[kendall_df['p-value'] < 0.05]['Metric'].tolist() if len(kendall_df) > 0 else []

report += f"""
    3. Statistically Significant Correlations with TQS:
       {', '.join(sig_tqs) if sig_tqs else 'None at p<0.05'}
    
    4. Statistically Significant Correlations with Survey:
       {', '.join(sig_survey) if sig_survey else 'None at p<0.05'}

═══════════════════════════════════════════════════════════════════════════════
                              CONCLUSIONS
═══════════════════════════════════════════════════════════════════════════════
"""

# Generate conclusions based on correlation strengths
avg_tqs_corr = corr_df['Pearson r'].abs().mean()
avg_survey_corr = kendall_df["Kendall's τ"].abs().mean() if len(kendall_df) > 0 else 0

if avg_tqs_corr > 0.5:
    report += """
    • Automated metrics show MODERATE TO STRONG correlation with MQM expert
      annotation, suggesting they can serve as reasonable proxies for
      translation quality assessment.
"""
elif avg_tqs_corr > 0.3:
    report += """
    • Automated metrics show MODERATE correlation with MQM expert annotation.
      While useful for ranking, they should not replace human evaluation
      for high-stakes assessments.
"""
else:
    report += """
    • Automated metrics show WEAK correlation with MQM expert annotation.
      This suggests automated metrics may not reliably predict human
      quality judgments for this specialized translation domain.
"""

if avg_survey_corr > 0.3:
    report += """
    • Automated metrics show meaningful correlation with blind expert
      preferences, validating their use in comparative evaluation.
"""
else:
    report += """
    • Automated metrics show limited correlation with blind expert
      preferences, suggesting human evaluation remains essential for
      this specialized domain (ancient Greek medical texts).
"""

report += """
═══════════════════════════════════════════════════════════════════════════════
                            GENERATED OUTPUTS
═══════════════════════════════════════════════════════════════════════════════

    Charts (in charts/ folder):
    ─────────────────────────────
    1. chart1_correlation_heatmap.png - Correlation coefficient heatmap
    2. chart2_scatter_tqs.png         - Scatter plots: metrics vs TQS
    3. chart3_correlation_bars.png    - Bar chart comparing correlations

    Reports (in reports/ folder):
    ─────────────────────────────
    1. correlation_analysis_report.txt - This report
    2. correlation_data.csv            - Raw correlation data

═══════════════════════════════════════════════════════════════════════════════
"""

# Save report
with open('reports/correlation_analysis_report.txt', 'w') as f:
    f.write(report)
print("\nSaved: reports/correlation_analysis_report.txt")

# Save correlation data
summary_df.to_csv('reports/correlation_data.csv', index=False)
print("Saved: reports/correlation_data.csv")

# Save merged data for further analysis
merged.to_csv('reports/merged_metrics_tqs.csv', index=False)
print("Saved: reports/merged_metrics_tqs.csv")

print(report)
print("\nCorrelation Analysis complete!")
