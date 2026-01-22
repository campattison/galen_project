#!/usr/bin/env python3
"""
Analysis of Greek Translation Survey Data
Comparing AI (Claude, Gemini, ChatGPT/OpenAI) vs Human (Johnston, Singer-van der Eijk) translations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set style for academic publication
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['figure.dpi'] = 150

# Load data
df = pd.read_csv('survey-responses-1769097340109.csv')

# Define source categories
AI_MODELS = ['claude', 'gemini', 'openai']
HUMAN_TRANSLATORS = ['human1', 'human2']

# Map to display names
MODEL_NAMES = {
    'claude': 'Claude',
    'gemini': 'Gemini', 
    'openai': 'ChatGPT',
    'human1': 'Johnston',      # Assumption: human1 = Johnston
    'human2': 'Singer-van der Eijk'  # Assumption: human2 = Singer-van der Eijk
}

# Reverse mapping
NAME_TO_CODE = {v: k for k, v in MODEL_NAMES.items()}

def get_comparison_type(left, right):
    """Determine the type of comparison"""
    left_is_ai = left in AI_MODELS
    right_is_ai = right in AI_MODELS
    
    if left_is_ai and not right_is_ai:
        return 'ai_vs_human'
    elif not left_is_ai and right_is_ai:
        return 'human_vs_ai'
    elif left_is_ai and right_is_ai:
        return 'ai_vs_ai'
    else:
        return 'human_vs_human'

def normalize_preference(row):
    """
    Convert position-relative preference to source-centric preference.
    Returns a dict with the preference score FOR each source in the comparison.
    Positive = preferred, Negative = not preferred
    """
    left = row['Left Translation']
    right = row['Right Translation']
    score = row['Preference Score']
    
    # Score is negative if left preferred, positive if right preferred
    # So left_preference = -score, right_preference = +score
    left_pref = -score
    right_pref = score
    
    return {left: left_pref, right: right_pref}

# Process each comparison to extract AI vs Human preferences
results = []

for idx, row in df.iterrows():
    left = row['Left Translation']
    right = row['Right Translation']
    score = row['Preference Score']
    expert = row['Expert Name']
    chunk_id = row['Chunk ID']
    
    comp_type = get_comparison_type(left, right)
    prefs = normalize_preference(row)
    
    # For AI vs Human comparisons
    if comp_type in ['ai_vs_human', 'human_vs_ai']:
        ai_model = left if left in AI_MODELS else right
        human_trans = right if right in HUMAN_TRANSLATORS else left
        
        # Get preference for AI (positive = AI preferred, negative = human preferred)
        ai_preference = prefs[ai_model]
        
        results.append({
            'expert': expert,
            'chunk_id': chunk_id,
            'ai_model': ai_model,
            'human_translator': human_trans,
            'ai_preference': ai_preference,  # Positive means AI was preferred
            'comparison_type': 'ai_vs_human',
            'original_score': score,
            'left': left,
            'right': right
        })
    
    # For AI vs AI comparisons
    elif comp_type == 'ai_vs_ai':
        results.append({
            'expert': expert,
            'chunk_id': chunk_id,
            'ai_model': left,
            'opponent': right,
            'preference': prefs[left],
            'comparison_type': 'ai_vs_ai',
            'original_score': score,
            'left': left,
            'right': right
        })

results_df = pd.DataFrame(results)

# ============================================================================
# ANALYSIS 1: LLM vs Human Translation Preferences
# ============================================================================

print("=" * 80)
print("SURVEY ANALYSIS: AI vs HUMAN TRANSLATION OF ANCIENT GREEK (GALEN)")
print("=" * 80)
print()

# Filter to AI vs Human comparisons only
ai_human_df = results_df[results_df['comparison_type'] == 'ai_vs_human'].copy()

print(f"Total AI vs Human comparisons: {len(ai_human_df)}")
print(f"Unique experts: {ai_human_df['expert'].nunique()}")
print(f"Unique text chunks: {ai_human_df['chunk_id'].nunique()}")
print()

# Convert preference to Likert categories
def pref_to_likert(pref):
    """Convert normalized preference score to Likert category relative to HUMAN preference"""
    # pref is AI preference, so negate to get human preference
    human_pref = -pref
    if human_pref == 2:
        return 'Strongly Prefer Human'
    elif human_pref == 1:
        return 'Somewhat Prefer Human'
    elif human_pref == 0:
        return 'Neutral'
    elif human_pref == -1:
        return 'Somewhat Prefer AI'
    else:  # -2
        return 'Strongly Prefer AI'

ai_human_df['likert_category'] = ai_human_df['ai_preference'].apply(pref_to_likert)

# Order for display
likert_order = ['Strongly Prefer Human', 'Somewhat Prefer Human', 'Neutral', 
                'Somewhat Prefer AI', 'Strongly Prefer AI']

# ============================================================================
# Create crosstabs by model and human translator
# ============================================================================

def create_likert_table(data, model_col='ai_model', group_by=None):
    """Create Likert distribution table"""
    if group_by:
        grouped = data.groupby([model_col, group_by, 'likert_category']).size().unstack(fill_value=0)
    else:
        grouped = data.groupby([model_col, 'likert_category']).size().unstack(fill_value=0)
    
    # Ensure all columns exist
    for col in likert_order:
        if col not in grouped.columns:
            grouped[col] = 0
    
    return grouped[likert_order]

# Aggregate table (all human translators combined)
aggregate_table = create_likert_table(ai_human_df)

# By human translator
johnston_data = ai_human_df[ai_human_df['human_translator'] == 'human1']
singer_data = ai_human_df[ai_human_df['human_translator'] == 'human2']

johnston_table = create_likert_table(johnston_data)
singer_table = create_likert_table(singer_data)

print("AGGREGATE RESULTS (All Human Translators)")
print("-" * 60)
print(aggregate_table)
print()

print("VS JOHNSTON (human1)")
print("-" * 60)
print(johnston_table)
print()

print("VS SINGER-VAN DER EIJK (human2)")
print("-" * 60)
print(singer_table)
print()

# ============================================================================
# Statistics by model
# ============================================================================

print("SUMMARY STATISTICS BY AI MODEL")
print("-" * 60)

for model in AI_MODELS:
    model_data = ai_human_df[ai_human_df['ai_model'] == model]
    
    # Human preference score (negative of AI preference)
    human_scores = -model_data['ai_preference']
    
    n = len(model_data)
    mean_pref = human_scores.mean()
    std_pref = human_scores.std()
    
    # Win rates
    human_wins = (human_scores > 0).sum()
    ai_wins = (human_scores < 0).sum()
    ties = (human_scores == 0).sum()
    
    print(f"\n{MODEL_NAMES[model]}:")
    print(f"  N comparisons: {n}")
    print(f"  Mean human preference: {mean_pref:.3f} (scale: -2 to +2)")
    print(f"  Std: {std_pref:.3f}")
    print(f"  Human preferred: {human_wins} ({100*human_wins/n:.1f}%)")
    print(f"  AI preferred: {ai_wins} ({100*ai_wins/n:.1f}%)")
    print(f"  Neutral: {ties} ({100*ties/n:.1f}%)")
    
    # One-sample t-test against 0 (no preference)
    t_stat, p_val = stats.ttest_1samp(human_scores, 0)
    print(f"  One-sample t-test (vs. neutral): t={t_stat:.3f}, p={p_val:.4f}")

# ============================================================================
# CHART 1: Stacked Bar Chart - LLM vs Human Translation
# ============================================================================

def create_stacked_bar_chart(tables_dict, title, filename):
    """Create stacked bar chart with tabs for different human translators"""
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
    
    colors = {
        'Strongly Prefer Human': '#1a5f7a',
        'Somewhat Prefer Human': '#57a0c9',
        'Neutral': '#cccccc',
        'Somewhat Prefer AI': '#e88b57',
        'Strongly Prefer AI': '#c44e3d'
    }
    
    model_order = ['claude', 'gemini', 'openai']
    model_labels = [MODEL_NAMES[m] for m in model_order]
    
    subtitles = ['Aggregate', 'vs Johnston', 'vs Singer-van der Eijk']
    
    for ax_idx, (subtitle, table) in enumerate(zip(subtitles, tables_dict.values())):
        ax = axes[ax_idx]
        
        # Normalize to percentages
        table_pct = table.div(table.sum(axis=1), axis=0) * 100
        
        # Reorder rows
        table_pct = table_pct.reindex([m for m in model_order if m in table_pct.index])
        
        # Plot stacked bars
        bottom = np.zeros(len(table_pct))
        
        for cat in likert_order:
            if cat in table_pct.columns:
                values = table_pct[cat].values
                bars = ax.barh(range(len(table_pct)), values, left=bottom, 
                              label=cat, color=colors[cat], edgecolor='white', linewidth=0.5)
                bottom += values
        
        ax.set_yticks(range(len(table_pct)))
        ax.set_yticklabels([MODEL_NAMES[m] for m in table_pct.index])
        ax.set_xlabel('Percentage of Responses')
        ax.set_title(subtitle, fontweight='bold')
        ax.set_xlim(0, 100)
        ax.axvline(50, color='black', linestyle='--', alpha=0.3, linewidth=1)
        
        # Add count annotations
        for i, model in enumerate(table_pct.index):
            n = table.loc[model].sum()
            ax.annotate(f'n={int(n)}', xy=(102, i), va='center', fontsize=9)
    
    # Legend
    handles = [mpatches.Patch(color=colors[cat], label=cat) for cat in likert_order]
    fig.legend(handles=handles, loc='lower center', ncol=5, bbox_to_anchor=(0.5, -0.05))
    
    fig.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

tables = {
    'Aggregate': aggregate_table,
    'Johnston': johnston_table,
    'Singer': singer_table
}

create_stacked_bar_chart(tables, 
    'Survey Results: LLM vs Human Translation Preference',
    'chart1_llm_vs_human_preference.png')

# ============================================================================
# CHART 1B: Win Rate Visualization
# ============================================================================

def create_win_rate_chart(data, filename):
    """Create win rate stacked bar chart"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    model_order = ['claude', 'gemini', 'openai']
    
    win_rates = []
    for model in model_order:
        model_data = data[data['ai_model'] == model]
        human_scores = -model_data['ai_preference']
        
        n = len(model_data)
        human_wins = (human_scores > 0).sum() / n * 100
        ai_wins = (human_scores < 0).sum() / n * 100
        ties = (human_scores == 0).sum() / n * 100
        
        win_rates.append({
            'model': MODEL_NAMES[model],
            'Human Wins': human_wins,
            'Tie': ties,
            'AI Wins': ai_wins
        })
    
    win_df = pd.DataFrame(win_rates)
    
    colors = ['#1a5f7a', '#cccccc', '#c44e3d']
    categories = ['Human Wins', 'Tie', 'AI Wins']
    
    bottom = np.zeros(len(win_df))
    for i, cat in enumerate(categories):
        ax.barh(range(len(win_df)), win_df[cat], left=bottom, 
               label=cat, color=colors[i], edgecolor='white', linewidth=0.5)
        bottom += win_df[cat].values
    
    ax.set_yticks(range(len(win_df)))
    ax.set_yticklabels(win_df['model'])
    ax.set_xlabel('Percentage of Comparisons')
    ax.set_xlim(0, 100)
    ax.axvline(50, color='black', linestyle='--', alpha=0.5, linewidth=1)
    ax.legend(loc='lower right')
    ax.set_title('Win Rate: Human vs AI Translation', fontsize=14, fontweight='bold')
    
    # Add percentage labels
    for i, row in win_df.iterrows():
        cumsum = 0
        for cat in categories:
            val = row[cat]
            if val > 8:  # Only show label if segment is large enough
                ax.text(cumsum + val/2, i, f'{val:.0f}%', 
                       ha='center', va='center', fontsize=10, color='white', fontweight='bold')
            cumsum += val
    
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

create_win_rate_chart(ai_human_df, 'chart1b_win_rate.png')

# ============================================================================
# CHART 2: Head-to-Head Model Comparison
# ============================================================================

print("\n" + "=" * 80)
print("HEAD-TO-HEAD MODEL COMPARISONS")
print("=" * 80)

# Get pairwise comparisons between AI and Human, compute relative performance
def compute_pairwise_stats(data):
    """Compute pairwise win rates between all sources"""
    
    sources = AI_MODELS + HUMAN_TRANSLATORS
    results = {}
    
    # For each pair, find comparisons where they faced each other
    for i, s1 in enumerate(sources):
        for s2 in sources[i+1:]:
            # Find rows where these two faced off
            mask = ((data['Left Translation'] == s1) & (data['Right Translation'] == s2)) | \
                   ((data['Left Translation'] == s2) & (data['Right Translation'] == s1))
            
            comparisons = data[mask]
            
            if len(comparisons) == 0:
                continue
            
            # Calculate wins for s1
            s1_wins = 0
            s2_wins = 0
            ties = 0
            
            for _, row in comparisons.iterrows():
                left = row['Left Translation']
                right = row['Right Translation']
                score = row['Preference Score']
                left_pref = -score
                right_pref = score
                prefs = {left: left_pref, right: right_pref}
                
                if prefs[s1] > prefs[s2]:
                    s1_wins += 1
                elif prefs[s2] > prefs[s1]:
                    s2_wins += 1
                else:
                    ties += 1
            
            n = len(comparisons)
            
            # Binomial test for significance
            if s1_wins + s2_wins > 0:
                # Test if s1's win rate differs from 50%
                result = stats.binomtest(s1_wins, s1_wins + s2_wins, 0.5, alternative='two-sided')
                p_value = result.pvalue
            else:
                p_value = 1.0
            
            results[(s1, s2)] = {
                's1_wins': s1_wins,
                's2_wins': s2_wins,
                'ties': ties,
                'n': n,
                'p_value': p_value,
                's1_rate': s1_wins / (s1_wins + s2_wins) if (s1_wins + s2_wins) > 0 else 0.5
            }
    
    return results

pairwise = compute_pairwise_stats(df)

print("\nPairwise Comparison Results (excluding ties):")
print("-" * 70)
print(f"{'Matchup':<35} {'Winner':<15} {'Rate':<10} {'p-value':<10}")
print("-" * 70)

for (s1, s2), stats_dict in sorted(pairwise.items()):
    n1, n2 = stats_dict['s1_wins'], stats_dict['s2_wins']
    ties = stats_dict['ties']
    p = stats_dict['p_value']
    
    if n1 > n2:
        winner = MODEL_NAMES[s1]
        rate = n1 / (n1 + n2) * 100 if (n1 + n2) > 0 else 50
    elif n2 > n1:
        winner = MODEL_NAMES[s2]
        rate = n2 / (n1 + n2) * 100 if (n1 + n2) > 0 else 50
    else:
        winner = "Tie"
        rate = 50
    
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    
    matchup = f"{MODEL_NAMES[s1]} vs {MODEL_NAMES[s2]}"
    print(f"{matchup:<35} {winner:<15} {rate:>5.1f}%     {p:.4f} {sig}")
    print(f"   ({n1}-{n2}-{ties}, n={stats_dict['n']})")

# Create heatmap for head-to-head (AI vs Human only)
def create_head_to_head_chart(pairwise, filename):
    """Create head-to-head comparison chart - AI models vs Human translators only"""
    
    # Only show AI (rows) vs Human (columns) since that's what was actually compared
    ai_models = ['claude', 'gemini', 'openai']
    human_trans = ['human1', 'human2']
    
    ai_labels = [MODEL_NAMES[m] for m in ai_models]
    human_labels = [MODEL_NAMES[h] for h in human_trans]
    
    n_ai = len(ai_models)
    n_human = len(human_trans)
    
    # Create matrix: rows = AI, columns = Human
    matrix = np.full((n_ai, n_human), np.nan)
    annotations = [['' for _ in range(n_human)] for _ in range(n_ai)]
    
    for i, ai in enumerate(ai_models):
        for j, human in enumerate(human_trans):
            # Find the comparison (may be stored as (ai, human) or (human, ai))
            if (ai, human) in pairwise:
                stats_dict = pairwise[(ai, human)]
                # AI win rate against human
                win_rate = stats_dict['s1_rate'] * 100
                p = stats_dict['p_value']
                ai_wins = stats_dict['s1_wins']
                human_wins = stats_dict['s2_wins']
                ties = stats_dict['ties']
            elif (human, ai) in pairwise:
                stats_dict = pairwise[(human, ai)]
                # AI win rate against human
                win_rate = (1 - stats_dict['s1_rate']) * 100
                p = stats_dict['p_value']
                ai_wins = stats_dict['s2_wins']
                human_wins = stats_dict['s1_wins']
                ties = stats_dict['ties']
            else:
                continue
            
            matrix[i, j] = win_rate
            sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
            annotations[i][j] = f'{win_rate:.0f}%{sig}\n({ai_wins}-{human_wins}-{ties})'
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Custom colormap: blue for AI winning (>50%), red for human winning (<50%)
    from matplotlib.colors import LinearSegmentedColormap
    colors_map = ['#1a5f7a', '#f5f5f5', '#c44e3d']  # Human wins (blue) - Neutral - AI wins (red)
    cmap = LinearSegmentedColormap.from_list('win_rate', colors_map)
    
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=100, aspect='auto')
    
    # Add annotations
    for i in range(n_ai):
        for j in range(n_human):
            if annotations[i][j]:
                text_color = 'white' if (matrix[i,j] < 30 or matrix[i,j] > 70) else 'black'
                ax.text(j, i, annotations[i][j], ha='center', va='center', 
                       fontsize=11, color=text_color, fontweight='bold')
    
    ax.set_xticks(range(n_human))
    ax.set_yticks(range(n_ai))
    ax.set_xticklabels(human_labels, fontsize=12)
    ax.set_yticklabels(ai_labels, fontsize=12)
    
    ax.set_xlabel('Human Translator', fontweight='bold', fontsize=12)
    ax.set_ylabel('AI Model', fontweight='bold', fontsize=12)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('AI Win Rate (%)', fontweight='bold')
    cbar.set_ticks([0, 25, 50, 75, 100])
    cbar.set_ticklabels(['0%\n(Human wins)', '25%', '50%\n(Tied)', '75%', '100%\n(AI wins)'])
    
    ax.set_title('Head-to-Head: AI Model vs Human Translator\n(AI win rate, excluding ties; W-L-T shown)\n* p<0.05, ** p<0.01, *** p<0.001', 
                fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

create_head_to_head_chart(pairwise, 'chart2_head_to_head.png')

# ============================================================================
# CHART 3: Overall Model Rankings
# ============================================================================

def compute_overall_scores(data):
    """Compute overall scores for each source based on all comparisons"""
    
    sources = AI_MODELS + HUMAN_TRANSLATORS
    scores = {s: {'total_pref': 0, 'n': 0, 'wins': 0, 'losses': 0} for s in sources}
    
    for _, row in data.iterrows():
        left = row['Left Translation']
        right = row['Right Translation']
        score = row['Preference Score']
        left_pref = -score
        right_pref = score
        prefs = {left: left_pref, right: right_pref}
        
        for source in [left, right]:
            if source in sources:
                scores[source]['total_pref'] += prefs[source]
                scores[source]['n'] += 1
                if prefs[source] > 0:
                    scores[source]['wins'] += 1
                elif prefs[source] < 0:
                    scores[source]['losses'] += 1
    
    return scores

overall = compute_overall_scores(df)

print("\n" + "=" * 80)
print("OVERALL MODEL RANKINGS")
print("=" * 80)

ranking_data = []
for source, stats_dict in overall.items():
    avg_pref = stats_dict['total_pref'] / stats_dict['n'] if stats_dict['n'] > 0 else 0
    win_rate = stats_dict['wins'] / stats_dict['n'] * 100 if stats_dict['n'] > 0 else 0
    ranking_data.append({
        'Source': MODEL_NAMES[source],
        'code': source,
        'Avg Preference': avg_pref,
        'Win Rate': win_rate,
        'Wins': stats_dict['wins'],
        'Losses': stats_dict['losses'],
        'Ties': stats_dict['n'] - stats_dict['wins'] - stats_dict['losses'],
        'N': stats_dict['n']
    })

ranking_df = pd.DataFrame(ranking_data).sort_values('Avg Preference', ascending=False)

print("\nRanked by Average Preference Score:")
print(ranking_df[['Source', 'Avg Preference', 'Win Rate', 'Wins', 'Losses', 'Ties', 'N']].to_string(index=False))

# Create ranking bar chart
def create_ranking_chart(ranking_df, filename):
    """Create overall ranking bar chart"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Sort by average preference
    df_sorted = ranking_df.sort_values('Avg Preference', ascending=True)
    
    # Color by type
    colors = ['#2ecc71' if s in HUMAN_TRANSLATORS else '#e74c3c' for s in df_sorted['code']]
    
    # Chart 1: Average Preference
    bars1 = ax1.barh(range(len(df_sorted)), df_sorted['Avg Preference'], color=colors, edgecolor='white')
    ax1.set_yticks(range(len(df_sorted)))
    ax1.set_yticklabels(df_sorted['Source'])
    ax1.set_xlabel('Average Preference Score')
    ax1.set_title('Average Preference Score by Source\n(Higher = More Preferred)', fontweight='bold')
    ax1.axvline(0, color='black', linewidth=1)
    
    for i, (idx, row) in enumerate(df_sorted.iterrows()):
        ax1.annotate(f'{row["Avg Preference"]:.2f}', 
                    xy=(row['Avg Preference'] + 0.02, i), 
                    va='center', fontsize=10)
    
    # Chart 2: Win Rate
    df_sorted2 = ranking_df.sort_values('Win Rate', ascending=True)
    colors2 = ['#2ecc71' if s in HUMAN_TRANSLATORS else '#e74c3c' for s in df_sorted2['code']]
    
    bars2 = ax2.barh(range(len(df_sorted2)), df_sorted2['Win Rate'], color=colors2, edgecolor='white')
    ax2.set_yticks(range(len(df_sorted2)))
    ax2.set_yticklabels(df_sorted2['Source'])
    ax2.set_xlabel('Win Rate (%)')
    ax2.set_title('Win Rate by Source\n(% of comparisons where source was preferred)', fontweight='bold')
    ax2.axvline(50, color='black', linestyle='--', alpha=0.5, linewidth=1)
    
    for i, (idx, row) in enumerate(df_sorted2.iterrows()):
        ax2.annotate(f'{row["Win Rate"]:.1f}%', 
                    xy=(row['Win Rate'] + 1, i), 
                    va='center', fontsize=10)
    
    # Legend
    human_patch = mpatches.Patch(color='#2ecc71', label='Human')
    ai_patch = mpatches.Patch(color='#e74c3c', label='AI')
    fig.legend(handles=[human_patch, ai_patch], loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.02))
    
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close()
    print(f"Saved: {filename}")

create_ranking_chart(ranking_df, 'chart3_overall_ranking.png')

# ============================================================================
# Generate Human-Readable Report
# ============================================================================

report = """
================================================================================
SURVEY ANALYSIS REPORT: AI vs HUMAN TRANSLATION OF GALEN'S GREEK MEDICAL TEXTS
================================================================================

STUDY OVERVIEW
--------------
This analysis examines survey responses comparing translations of Galen's ancient 
Greek medical texts. Experts evaluated pairs of translations in a blinded comparison,
rating their preference on a 5-point Likert scale (-2 to +2).

METHODOLOGY
-----------
- Participants compared pairs of translations without knowing which was AI or human
- Each comparison showed two translations (Left vs Right) in randomized order
- Preference scores: -2 (Strongly prefer left) to +2 (Strongly prefer right)
- Scores were normalized to be source-centric (not position-dependent)

TRANSLATION SOURCES
-------------------
AI Models:
  - Claude (Anthropic)
  - Gemini (Google)
  - ChatGPT (OpenAI)

Human Translators:
  - human1 (assumed: Johnston)
  - human2 (assumed: Singer-van der Eijk)

Note: The mapping of human1/human2 to specific translators should be verified 
against the original study design.

================================================================================
KEY FINDINGS
================================================================================

"""

# Add statistics to report
report += f"""
1. DATASET SUMMARY
------------------
- Total survey responses: {len(df)}
- Unique expert reviewers: {df['Expert Name'].nunique()}
- Text chunks evaluated: {df['Chunk ID'].nunique()}
- AI vs Human comparisons: {len(ai_human_df)}

2. OVERALL TRANSLATION QUALITY RANKINGS
---------------------------------------
(Ranked by average preference score across all comparisons)

"""

for _, row in ranking_df.iterrows():
    source_type = "HUMAN" if row['code'] in HUMAN_TRANSLATORS else "AI"
    report += f"  {row['Source']:25} [{source_type}]: Avg={row['Avg Preference']:+.2f}, WinRate={row['Win Rate']:.1f}%\n"

report += f"""

3. AI MODEL PERFORMANCE VS HUMAN TRANSLATIONS
---------------------------------------------
When AI translations were directly compared with human translations:

"""

for model in AI_MODELS:
    model_data = ai_human_df[ai_human_df['ai_model'] == model]
    human_scores = -model_data['ai_preference']
    n = len(model_data)
    mean_pref = human_scores.mean()
    human_wins = (human_scores > 0).sum()
    ai_wins = (human_scores < 0).sum()
    ties = (human_scores == 0).sum()
    
    t_stat, p_val = stats.ttest_1samp(human_scores, 0)
    
    report += f"""
{MODEL_NAMES[model]}:
  - Comparisons with human translations: {n}
  - Mean preference toward human: {mean_pref:+.3f}
  - Human preferred: {human_wins} times ({100*human_wins/n:.1f}%)
  - AI preferred: {ai_wins} times ({100*ai_wins/n:.1f}%)
  - Neutral: {ties} times ({100*ties/n:.1f}%)
  - Statistical test (vs neutral): t={t_stat:.2f}, p={p_val:.4f}
    {'→ Humans significantly preferred' if p_val < 0.05 and mean_pref > 0 else '→ No significant difference' if p_val >= 0.05 else '→ AI significantly preferred'}
"""

report += """

4. HEAD-TO-HEAD STATISTICAL COMPARISONS
---------------------------------------
Pairwise comparisons showing which source was preferred (excluding neutral ratings):

"""

for (s1, s2), stats_dict in sorted(pairwise.items()):
    n1, n2 = stats_dict['s1_wins'], stats_dict['s2_wins']
    ties = stats_dict['ties']
    p = stats_dict['p_value']
    
    if n1 > n2:
        winner = MODEL_NAMES[s1]
        loser = MODEL_NAMES[s2]
        rate = n1 / (n1 + n2) * 100 if (n1 + n2) > 0 else 50
    elif n2 > n1:
        winner = MODEL_NAMES[s2]
        loser = MODEL_NAMES[s1]
        rate = n2 / (n1 + n2) * 100 if (n1 + n2) > 0 else 50
    else:
        winner = "Tie"
        loser = ""
        rate = 50
    
    sig = "Highly significant (p<0.001)" if p < 0.001 else "Very significant (p<0.01)" if p < 0.01 else "Significant (p<0.05)" if p < 0.05 else "Not significant"
    
    report += f"""
{MODEL_NAMES[s1]} vs {MODEL_NAMES[s2]}:
  - Record: {n1}-{n2}-{ties} (W-L-T, n={stats_dict['n']})
  - Winner: {winner} ({rate:.1f}% win rate)
  - p-value: {p:.4f} ({sig})
"""

report += """

5. INTERPRETATION NOTES
-----------------------
• Higher average preference scores indicate the translation was more frequently 
  preferred by experts.
• Win rate represents the percentage of non-neutral comparisons where the source
  was preferred.
• Statistical significance was tested using binomial tests (head-to-head) and 
  one-sample t-tests (vs neutral).
• The blinded design controls for bias, as reviewers did not know which 
  translation was human or AI-generated.

================================================================================
GENERATED FILES
================================================================================
1. chart1_llm_vs_human_preference.png - Likert distribution by AI model
2. chart1b_win_rate.png - Win rate comparison (Human vs AI)
3. chart2_head_to_head.png - Pairwise comparison matrix
4. chart3_overall_ranking.png - Overall model rankings

================================================================================
"""

# Save report
with open('analysis_report.txt', 'w') as f:
    f.write(report)
print("\nSaved: analysis_report.txt")

print(report)
print("\nAnalysis complete!")
