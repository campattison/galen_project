"""
correlation_analysis.py
-----------------------
Computes Pearson r and Spearman rho (with 95% confidence intervals and exact
p-values) between each automated translation metric and the expert TQS scores.

Analysis is done IN AGGREGATE across all 60 observations (20 passages x 3 models).

Outputs a CSV where:
  - Rows   = each evaluation metric (BLEU-4, chrF++, METEOR, etc.)
  - Columns = Pearson r, Pearson CI lower/upper, Pearson p-value,
              Spearman rho, Spearman CI lower/upper, Spearman p-value

Dependencies: pandas, scipy, numpy
Install with: pip install pandas scipy numpy
"""

import numpy as np
import pandas as pd
from scipy import stats

# ── 1. LOAD DATA ─────────────────────────────────────────────────────────────

# Assumes the CSV is in the same folder as this script (AI_audit).
df = pd.read_csv("merged_metrics_tqs.csv")

# The automated metrics we want to evaluate
metrics = ["BLEU-4", "chrF++", "METEOR", "ROUGE-L", "BERTScore", "BLEURT", "COMET"]

# The ground-truth quality score we're correlating against
target = "TQS"

# ── 2. CONFIDENCE INTERVAL HELPER ────────────────────────────────────────────

def pearson_ci(r, n, alpha=0.05):
    """
    95% CI for Pearson r via Fisher's z-transformation.

    r is bounded [-1, 1], so we can't assume normality directly.
    Fisher's z = arctanh(r) is approximately normal with SE = 1/sqrt(n-3),
    allowing us to build a CI in z-space then convert back.
    """
    z      = np.arctanh(r)
    se     = 1.0 / np.sqrt(n - 3)
    z_crit = stats.norm.ppf(1 - alpha / 2)   # 1.96 for 95%

    r_lo = np.tanh(z - z_crit * se)
    r_hi = np.tanh(z + z_crit * se)
    return r_lo, r_hi


def spearman_ci(rho, n, alpha=0.05):
    """
    95% CI for Spearman rho using the same Fisher z-transformation.
    Standard approximation; valid for n >= 20.
    """
    return pearson_ci(rho, n, alpha)


def fmt_p(p):
    """
    Format a p-value as a plain decimal string — never scientific notation.

    - p < 1e-9  → reported as '< 0.000000001' (avoids rounding to flat zero)
    - otherwise → printed with up to 10 significant decimal digits,
                  trailing zeros stripped, so e.g. 0.00034203 stays readable.
    """
    if p < 1e-9:
        return "< 0.000000001"
    # f-string with 10 decimal places, then strip trailing zeros after the dot
    formatted = f"{p:.10f}".rstrip("0").rstrip(".")
    return formatted


# ── 3. RUN CORRELATIONS ───────────────────────────────────────────────────────

n = len(df)   # should be 60
results = []

for metric in metrics:
    x = df[metric].values
    y = df[target].values

    # --- Pearson r -----------------------------------------------------------
    r,   p_r   = stats.pearsonr(x, y)
    r_lo, r_hi = pearson_ci(r, n)

    # --- Spearman rho --------------------------------------------------------
    rho, p_rho     = stats.spearmanr(x, y)
    rho_lo, rho_hi = spearman_ci(rho, n)

    results.append({
        "Metric":            metric,

        # Pearson block — CI split into two columns so Excel reads them cleanly
        "Pearson_r":         round(r, 4),
        "Pearson_CI_lower":  round(r_lo, 4),
        "Pearson_CI_upper":  round(r_hi, 4),
        "Pearson_p":         fmt_p(p_r),

        # Spearman block
        "Spearman_rho":      round(rho, 4),
        "Spearman_CI_lower": round(rho_lo, 4),
        "Spearman_CI_upper": round(rho_hi, 4),
        "Spearman_p":        fmt_p(p_rho),
    })

# ── 4. BUILD OUTPUT DATAFRAME ─────────────────────────────────────────────────

out = pd.DataFrame(results, columns=[
    "Metric",
    "Pearson_r",
    "Pearson_CI_lower",
    "Pearson_CI_upper",
    "Pearson_p",
    "Spearman_rho",
    "Spearman_CI_lower",
    "Spearman_CI_upper",
    "Spearman_p",
])

# ── 5. SAVE & DISPLAY ─────────────────────────────────────────────────────────

output_path = "metric_correlations_with_CI.csv"
out.to_csv(output_path, index=False)

print(f"Results saved to: {output_path}")
print(f"N (total observations) = {n}\n")
print(out.to_string(index=False))