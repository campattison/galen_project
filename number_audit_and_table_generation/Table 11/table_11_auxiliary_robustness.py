"""
Robustness Analysis: Rare Term Ratio → Passage-Level TQS (Comp.)
=================================================================
Computes:
  1. Pearson r, R², and bootstrap 95% CI for R²
  2. Trimmed analysis excluding influential passages (chunks 8 & 10)
  3. Spearman rank correlations (all 3 predictors)
  4. Cook's distance for each passage
"""

import pandas as pd
import numpy as np
from scipy import stats
import re

# ── File paths ───────────────────────────────────────────────────────────────
METRICS_PATH  = "merged_metrics_tqs.csv"
DIFF_PATH     = "Passage_difficulty_metrics.csv"

# ── Load & merge ─────────────────────────────────────────────────────────────
diff = pd.read_csv(DIFF_PATH)

def parse_chunk(label):
    m = re.match(r"(Head\d+)_Chunk(\d+)", label)
    if not m:
        return None, None
    text = "Comp" if m.group(1) == "Head224" else "Mixtures"
    return text, int(m.group(2))

diff[["text", "chunk"]] = diff["chunk"].apply(lambda x: pd.Series(parse_chunk(x)))
diff = diff.dropna(subset=["text"])
diff["chunk"] = diff["chunk"].astype(int)

tqs = pd.read_csv(METRICS_PATH)
passage = tqs[tqs["text"] == "Comp"].groupby("chunk")["TQS"].mean().reset_index()
passage.columns = ["chunk", "mean_TQS"]
comp = passage.merge(
    diff[diff["text"] == "Comp"][["chunk", "rare_term_ratio", "not_found_ratio", "avg_zipf"]],
    on="chunk",
).reset_index(drop=True)

PREDS = [
    ("rare_term_ratio", "Rare Term Ratio"),
    ("not_found_ratio", "Not-Found Ratio"),
    ("avg_zipf",        "Mean Zipf Freq."),
]

# ═══════════════════════════════════════════════════════════════════════════════
# 1. PEARSON r, R², BOOTSTRAP 95% CI
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("  1. PEARSON r, R², AND BOOTSTRAP 95% CI FOR R²  (Comp., n=10)")
print("=" * 70)

N_BOOT = 10000
np.random.seed(42)

for col, label in PREDS:
    x = comp[col].values
    y = comp["mean_TQS"].values

    r, p = stats.pearsonr(x, y)
    r2 = r ** 2

    # Bootstrap R²
    r2_boot = []
    for _ in range(N_BOOT):
        idx = np.random.choice(len(x), size=len(x), replace=True)
        xb, yb = x[idx], y[idx]
        if np.std(xb) > 0 and np.std(yb) > 0:
            r2_boot.append(np.corrcoef(xb, yb)[0, 1] ** 2)
    ci_lo, ci_hi = np.percentile(r2_boot, [2.5, 97.5])

    print(f"\n  {label}:")
    print(f"    r  = {r:+.4f},  p = {p:.6f}")
    print(f"    R² = {r2:.4f}   (bootstrap 95% CI: [{ci_lo:.2f}, {ci_hi:.2f}])")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. TRIMMED ANALYSIS (excluding chunks 8 & 10)
# ═══════════════════════════════════════════════════════════════════════════════
EXCLUDE = [8, 10]
trimmed = comp[~comp["chunk"].isin(EXCLUDE)].reset_index(drop=True)

print(f"\n\n{'=' * 70}")
print(f"  2. TRIMMED ANALYSIS  (excluding chunks {EXCLUDE}, n={len(trimmed)})")
print("=" * 70)

for col, label in PREDS:
    r_t, p_t = stats.pearsonr(trimmed[col], trimmed["mean_TQS"])
    print(f"\n  {label}:")
    print(f"    r  = {r_t:+.4f},  p = {p_t:.4f}")
    print(f"    R² = {r_t**2:.4f}")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. SPEARMAN RANK CORRELATIONS
# ═══════════════════════════════════════════════════════════════════════════════
print(f"\n\n{'=' * 70}")
print("  3. SPEARMAN RANK CORRELATIONS  (Comp., n=10)")
print("=" * 70)

for col, label in PREDS:
    rho, p = stats.spearmanr(comp[col], comp["mean_TQS"])
    print(f"\n  {label}:")
    print(f"    rho = {rho:+.4f},  p = {p:.4f}")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. COOK'S DISTANCE  (rare_term_ratio → mean_TQS)
# ═══════════════════════════════════════════════════════════════════════════════
print(f"\n\n{'=' * 70}")
print("  4. COOK'S DISTANCE  (rare_term_ratio → mean TQS)")
print("=" * 70)

x = comp["rare_term_ratio"].values
y = comp["mean_TQS"].values
n = len(x)
p_params = 2  # intercept + slope

X = np.column_stack([np.ones(n), x])
beta = np.linalg.lstsq(X, y, rcond=None)[0]
y_hat = X @ beta
residuals = y - y_hat
mse = np.sum(residuals ** 2) / (n - p_params)

H = X @ np.linalg.inv(X.T @ X) @ X.T
h = np.diag(H)
cooks_d = (residuals ** 2 / (p_params * mse)) * (h / (1 - h) ** 2)

threshold = 4 / n
print(f"\n  {'Chunk':>7}  {'rare_term_ratio':>16}  {'mean_TQS':>9}  {'Cook D':>8}  {'Flag':>12}")
print(f"  {'-'*7}  {'-'*16}  {'-'*9}  {'-'*8}  {'-'*12}")
for i in range(n):
    flag = "INFLUENTIAL" if cooks_d[i] > threshold else ""
    print(f"  {comp.loc[i,'chunk']:7.0f}  {comp.loc[i,'rare_term_ratio']:16.4f}  "
          f"{comp.loc[i,'mean_TQS']:9.2f}  {cooks_d[i]:8.4f}  {flag:>12}")
print(f"\n  Threshold (4/n): {threshold:.2f}")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. EXPORT CSV
# ═══════════════════════════════════════════════════════════════════════════════
rows = []

# R² and bootstrap
np.random.seed(42)
for col, label in PREDS:
    xv = comp[col].values
    yv = comp["mean_TQS"].values
    r_val, p_val = stats.pearsonr(xv, yv)
    r2_val = r_val ** 2
    r2_boot = []
    for _ in range(N_BOOT):
        idx = np.random.choice(len(xv), size=len(xv), replace=True)
        xb, yb = xv[idx], yv[idx]
        if np.std(xb) > 0 and np.std(yb) > 0:
            r2_boot.append(np.corrcoef(xb, yb)[0, 1] ** 2)
    ci_lo, ci_hi = np.percentile(r2_boot, [2.5, 97.5])

    r_t, p_t = stats.pearsonr(trimmed[col], trimmed["mean_TQS"])
    rho, p_s = stats.spearmanr(comp[col], comp["mean_TQS"])

    rows.append({
        "Predictor": label,
        "Pearson_r": round(r_val, 4),
        "Pearson_p": round(p_val, 6),
        "R2": round(r2_val, 4),
        "Bootstrap_CI_lo": round(ci_lo, 2),
        "Bootstrap_CI_hi": round(ci_hi, 2),
        "Trimmed_r": round(r_t, 4),
        "Trimmed_p": round(p_t, 4),
        "Trimmed_R2": round(r_t ** 2, 4),
        "Spearman_rho": round(rho, 4),
        "Spearman_p": round(p_s, 4),
    })

csv_df = pd.DataFrame(rows)
CSV_OUT = "robustness_analysis.csv"
csv_df.to_csv(CSV_OUT, index=False)
print(f"\n\nCSV saved → {CSV_OUT}")