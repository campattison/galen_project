"""
Pearson Correlation Analysis: Terminological Difficulty Predictors vs. Translation Quality
==========================================================================================
Predictors (rows):   rare_term_ratio, not_found_ratio, avg_zipf
Outcomes (columns):  TQS (Comp.), TQS (All), Crit. Error Rate (Comp.), Crit. Error Rate (All)

Two analysis levels:
  1. Passage-level  — values averaged across 3 models per passage (n=10 / 20)
  2. Translation-level — each model–passage pair is one observation (n=30 / 60)
"""

import pandas as pd
import numpy as np
from scipy import stats
import re

# ── File paths ───────────────────────────────────────────────────────────────
METRICS_PATH  = "merged_metrics_tqs.csv"
DIFF_PATH     = "Passage_difficulty_metrics.csv"
MQM_COMP_PATH = "MQM_SUMMARY_TABLES_Comp_Summary_Sorted.csv"
MQM_MIX_PATH  = "MQM_SUMMARY_TABLES_Mixtures_Summary_Sorted.csv"

# ── 1. Load difficulty metrics & parse chunk labels ──────────────────────────
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

PRED_COLS = ["rare_term_ratio", "not_found_ratio", "avg_zipf"]

# ── 2. Load TQS data ────────────────────────────────────────────────────────
tqs = pd.read_csv(METRICS_PATH)

# ── 3. Load MQM (Comp + Mixtures) & extract critical-error flag ─────────────
def load_mqm(path, text_label):
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df = df[df["Text"] == text_label].drop_duplicates(
        subset=["Text", "Chunk", "Model"], keep="first"
    )
    df["critical_count"] = pd.to_numeric(df["Critical"], errors="coerce").fillna(0)
    df = df.rename(columns={"Chunk": "chunk", "Model": "model"})
    df["text"] = text_label
    df["chunk"] = df["chunk"].astype(int)
    return df[["text", "chunk", "model", "critical_count"]]

mqm = pd.concat([
    load_mqm(MQM_COMP_PATH, "Comp"),
    load_mqm(MQM_MIX_PATH, "Mixtures"),
], ignore_index=True)

# ── 4. Build merged datasets ────────────────────────────────────────────────
# Translation-level: one row per model × passage
trans = tqs.merge(diff[["text", "chunk"] + PRED_COLS], on=["text", "chunk"])
trans = trans.merge(mqm, on=["text", "chunk", "model"], how="left")

# Passage-level: means across 3 models
passage = trans.groupby(["text", "chunk"]).agg(
    rare_term_ratio=("rare_term_ratio", "first"),
    not_found_ratio=("not_found_ratio", "first"),
    avg_zipf=("avg_zipf", "first"),
    mean_TQS=("TQS", "mean"),
    crit_rate=("critical_count", "mean"),
).reset_index()

# ── 5. Correlation engine ───────────────────────────────────────────────────
PRED_LABELS = {
    "rare_term_ratio": "Rare Term Ratio",
    "not_found_ratio": "Not-Found Ratio",
    "avg_zipf":        "Mean Zipf Freq.",
}

def pearson_table(datasets, pred_cols, pred_labels):
    """datasets: list of (column_label, dataframe, outcome_col)."""
    r_rows, p_rows = {}, {}
    for dlabel, df, outcol in datasets:
        for pc in pred_cols:
            sub = df.dropna(subset=[pc, outcol])
            plabel = pred_labels[pc]
            if len(sub) < 3:
                r_rows.setdefault(plabel, {})[dlabel] = np.nan
                p_rows.setdefault(plabel, {})[dlabel] = np.nan
            else:
                r, p = stats.pearsonr(sub[pc], sub[outcol])
                r_rows.setdefault(plabel, {})[dlabel] = r
                p_rows.setdefault(plabel, {})[dlabel] = p
    idx = list(pred_labels.values())
    return pd.DataFrame(r_rows).T.reindex(idx), pd.DataFrame(p_rows).T.reindex(idx)

# ── 6. Define outcome sets ──────────────────────────────────────────────────
p_comp = passage[passage["text"] == "Comp"]
p_all  = passage
t_comp = trans[trans["text"] == "Comp"]
t_all  = trans

passage_outcomes = [
    ("TQS (Comp.)",              p_comp, "mean_TQS"),
    ("TQS (All)",                p_all,  "mean_TQS"),
    ("Crit. Rate (Comp.)",       p_comp, "crit_rate"),
    ("Crit. Rate (All)",         p_all,  "crit_rate"),
]

trans_outcomes = [
    ("TQS (Comp.)",              t_comp, "TQS"),
    ("TQS (All)",                t_all,  "TQS"),
    ("Crit. Rate (Comp.)",       t_comp, "critical_count"),
    ("Crit. Rate (All)",         t_all,  "critical_count"),
]

# ── 7. Print results ────────────────────────────────────────────────────────
def sig(p):
    if pd.isna(p):   return ""
    if p < 0.001:    return "***"
    if p < 0.01:     return "**"
    if p < 0.05:     return "*"
    return ""

def print_block(title, ns_str, r_df, p_df):
    w = 90
    print(f"\n{'=' * w}")
    print(f"  {title}")
    print(f"  {ns_str}")
    print(f"{'=' * w}")

    print("\n  Pearson r:")
    print(r_df.to_string(float_format=lambda x: f"{x:+.4f}" if not pd.isna(x) else "   N/A"))

    print("\n  p-values:")
    print(p_df.to_string(float_format=lambda x: f"{x:.4f}" if not pd.isna(x) else "   N/A"))

    # Combined display
    comb = pd.DataFrame(index=r_df.index, columns=r_df.columns, dtype=object)
    for col in r_df.columns:
        for idx in r_df.index:
            rv, pv = r_df.loc[idx, col], p_df.loc[idx, col]
            if pd.isna(rv):
                comb.loc[idx, col] = "     N/A"
            else:
                comb.loc[idx, col] = f"{rv:+.4f} (p={pv:.4f}){sig(pv)}"
    print("\n  Combined  r (p-value):")
    print(comb.to_string())
    print()


# ─── Passage-level ───────────────────────────────────────────────────────────
r1, p1 = pearson_table(passage_outcomes, PRED_COLS, PRED_LABELS)
print_block(
    "PASSAGE-LEVEL CORRELATIONS  (means across 3 models per passage)",
    f"Comp. n = {len(p_comp)} passages  |  All n = {len(p_all)} passages",
    r1, p1,
)

# ─── Translation-level ──────────────────────────────────────────────────────
r2, p2 = pearson_table(trans_outcomes, PRED_COLS, PRED_LABELS)
print_block(
    "TRANSLATION-LEVEL CORRELATIONS  (each model x passage = 1 obs.)",
    f"Comp. n = {len(t_comp)} translations  |  All n = {len(t_all)} translations",
    r2, p2,
)

print("Significance: * p<.05  ** p<.01  *** p<.001")

# ── 8. Export CSV ────────────────────────────────────────────────────────────
def to_csv_block(r_df, p_df, level_label):
    """Build a long-format DataFrame with r, p, and significance."""
    rows = []
    for pred in r_df.index:
        for outcome in r_df.columns:
            rv = r_df.loc[pred, outcome]
            pv = p_df.loc[pred, outcome]
            rows.append({
                "Level": level_label,
                "Predictor": pred,
                "Outcome": outcome,
                "Pearson_r": round(rv, 4) if not pd.isna(rv) else None,
                "p_value": round(pv, 4) if not pd.isna(pv) else None,
                "Sig": sig(pv),
            })
    return pd.DataFrame(rows)

csv_df = pd.concat([
    to_csv_block(r1, p1, "Passage"),
    to_csv_block(r2, p2, "Translation"),
], ignore_index=True)

CSV_OUT = "table_11_correlations.csv"
csv_df.to_csv(CSV_OUT, index=False)
print(f"\nCSV saved → {CSV_OUT}")