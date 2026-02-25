"""
text_delta_analysis.py
----------------------
For each metric, calculates the relative % drop from Mixtures to Comp,
aggregated across all models, with independent samples t-tests and Cohen's d.

Delta = ((Comp_mean - Mix_mean) / Mix_mean) * 100

Test: independent samples t-test (two-tailed), df = n_comp + n_mix - 2 = 58.
Comp and Mixtures passages are independently sampled; chunk numbering does
not imply any pairing between text types.

Cohen's d (independent) = (Comp_mean - Mix_mean) / pooled_SD

Three conditions:
  1. All passages (chunks 1-10)
  2. Excluding chunks 8 and 10
  3. Excluding chunks 3, 8, and 10

Dependencies: pandas, numpy, scipy
Install with: pip install pandas numpy scipy
"""

import numpy as np
import pandas as pd
from scipy import stats

# ── 1. LOAD DATA ──────────────────────────────────────────────────────────────

df = pd.read_csv("merged_metrics_tqs.csv")

metrics = ["BLEU-4", "chrF++", "METEOR", "ROUGE-L", "BERTScore", "BLEURT", "COMET"]

# ── 2. DEFINE CONDITIONS ──────────────────────────────────────────────────────

conditions = [
    ("All passages",           []),
    ("Excl. chunks 8 & 10",    [8, 10]),
    ("Excl. chunks 3, 8 & 10", [3, 8, 10]),
]

# ── 3. COMPUTE STATS FOR ONE CONDITION ───────────────────────────────────────

def pooled_sd(a, b):
    """
    Pooled standard deviation for two independent groups.
    Formula: sqrt(((n1-1)*s1^2 + (n2-1)*s2^2) / (n1+n2-2))
    """
    n1, s1 = len(a), a.std(ddof=1)
    n2, s2 = len(b), b.std(ddof=1)
    return np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))


def compute_stats(data, exclude_chunks):
    """
    For each metric, computes:
      - relative % drop (Comp relative to Mixtures baseline)
      - independent samples t-statistic, df, and p-value (two-tailed)
      - Cohen's d using pooled SD
    """
    subset = data[~data["chunk"].isin(exclude_chunks)]

    comp_vals_all = subset[subset["text"] == "Comp"]
    mix_vals_all  = subset[subset["text"] == "Mixtures"]

    results = {}
    for metric in metrics:
        comp_vals = comp_vals_all[metric].values
        mix_vals  = mix_vals_all[metric].values

        # Relative % drop from Mix baseline
        comp_mean = comp_vals.mean()
        mix_mean  = mix_vals.mean()
        delta = ((comp_mean - mix_mean) / mix_mean) * 100

        # Independent samples t-test (two-tailed, equal variance not assumed)
        t_stat, p_val = stats.ttest_ind(comp_vals, mix_vals, equal_var=False)
        df_val = len(comp_vals) + len(mix_vals) - 2

        # Cohen's d with pooled SD
        psd = pooled_sd(comp_vals, mix_vals)
        cohens_d = (comp_mean - mix_mean) / psd

        results[metric] = {
            "delta":    round(delta, 2),
            "t":        round(t_stat, 3),
            "df":       df_val,
            "p":        round(p_val, 6),
            "cohens_d": round(cohens_d, 3),
        }

    return results

# ── 4. BUILD OUTPUT ───────────────────────────────────────────────────────────

rows = []
for metric in metrics:
    row = {"Metric": metric}
    for label, exclude in conditions:
        s = compute_stats(df, exclude)[metric]
        prefix = label.replace("Excl. chunks ", "Excl.").replace(" & ", "_").replace(", ", "_").replace(" ", "_")
        row[f"{prefix}__delta_%"]  = s["delta"]
        row[f"{prefix}__t"]        = s["t"]
        row[f"{prefix}__df"]       = s["df"]
        row[f"{prefix}__p"]        = s["p"]
        row[f"{prefix}__cohens_d"] = s["cohens_d"]
    rows.append(row)

out = pd.DataFrame(rows)

# ── 5. SAVE & DISPLAY ─────────────────────────────────────────────────────────

output_path = "metric_text_deltas.csv"
out.to_csv(output_path, index=False)

print(f"Results saved to: {output_path}")
print(f"\nDelta = ((Comp_mean - Mix_mean) / Mix_mean) x 100")
print(f"Negative = Comp scores lower than Mixtures")
print(f"Independent samples t-test: two-tailed, Welch's (equal variance not assumed)")
print(f"Cohen's d: (Comp_mean - Mix_mean) / pooled SD\n")

for label, exclude in conditions:
    prefix = label.replace("Excl. chunks ", "Excl.").replace(" & ", "_").replace(", ", "_").replace(" ", "_")
    cols = ["Metric", f"{prefix}__delta_%", f"{prefix}__t", f"{prefix}__df", f"{prefix}__p", f"{prefix}__cohens_d"]
    print(f"── {label} ──")
    print(out[cols].rename(columns=lambda c: c.replace(f"{prefix}__", "")).to_string(index=False))
    print()