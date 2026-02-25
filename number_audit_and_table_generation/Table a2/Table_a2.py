"""
reproduce_table_a2.py
Reproduces Table A2: Per-Passage Automated Metric Scores for All 60 LLM Translations
from merged_metrics_tqs.csv + MQM summary tables.

Run from this directory:
    python reproduce_table_a2.py

Outputs:
    table_a2.csv   — raw data for further checks
    table_a2.html  — formatted HTML preview
"""

import pandas as pd

# ── 1. Load data ──────────────────────────────────────────────────────────────

metrics = pd.read_csv("merged_metrics_tqs.csv")

comp_mqm   = pd.read_csv("MQM_SUMMARY_TABLES_Comp_Summary_Sorted.csv")
mix_mqm    = pd.read_csv("MQM_SUMMARY_TABLES_Mixtures_Summary_Sorted.csv")

# Drop stray header rows that crept in during CSV export
for df in [comp_mqm, mix_mqm]:
    df.drop(df[df["Model"] == "Model"].index, inplace=True)

mqm = pd.concat([comp_mqm, mix_mqm], ignore_index=True)

# NOTE: The paper's Table A2 uses "Quality Rating" (Scheme 1), NOT "Final Quality Rating".
# Final Quality Rating can differ (e.g. Mix. Chunk 6 Gemini/ChatGPT = FAIL in Final
# but LOW PASS in Quality Rating / Scheme 1). Using Quality Rating to match the paper.
mqm = mqm[["Text", "Chunk", "Model", "Quality Rating"]].copy()
mqm.columns = ["text", "chunk", "model", "Quality Rating"]
mqm["chunk"] = pd.to_numeric(mqm["chunk"], errors="coerce")
mqm.dropna(subset=["chunk", "model"], inplace=True)
mqm["chunk"] = mqm["chunk"].astype(int)
# Deduplicate – keep first occurrence per text/chunk/model
mqm.drop_duplicates(subset=["text", "chunk", "model"], keep="first", inplace=True)

# ── 2. Normalise metrics df ───────────────────────────────────────────────────

metrics["chunk"] = pd.to_numeric(metrics["chunk"], errors="coerce").astype(int)

# Rename openai → ChatGPT for display
label_map = {"claude": "Claude", "gemini": "Gemini", "openai": "ChatGPT"}
metrics["Model"] = metrics["model"].map(label_map)
mqm["Model"]     = mqm["model"].map(label_map)

# ── 3. Merge ──────────────────────────────────────────────────────────────────

merged = metrics.merge(
    mqm[["text", "chunk", "Model", "Quality Rating"]],
    left_on=["text", "chunk", "Model"],
    right_on=["text", "chunk", "Model"],
    how="left"
)

# ── 4. Abbreviate rating ──────────────────────────────────────────────────────

rating_map = {"HIGH PASS": "HP", "LOW PASS": "LP", "FAIL": "F"}
merged["Rating"] = merged["Quality Rating"].map(rating_map)

# ── 5. Format display columns ─────────────────────────────────────────────────

merged["TQS"]       = merged["TQS"].round(1)
merged["BLEU-4"]    = (merged["BLEU-4"] * 100).round(1).astype(str) + "%"
merged["BERTScore"] = (merged["BERTScore"] * 100).round(1).astype(str) + "%"
merged["COMET"]     = (merged["COMET"] * 100).round(1).astype(str) + "%"

# ── 6. Build display table ────────────────────────────────────────────────────

text_label_map = {"Mixtures": "Mix.", "Comp": "Comp."}
merged["Text"] = merged["text"].map(text_label_map)

table = merged[[
    "Text", "chunk", "Model", "TQS", "BLEU-4", "BERTScore", "COMET", "Rating"
]].rename(columns={"chunk": "Chunk"})

# Sort: Mix. first (chunks 1-10), then Comp. (chunks 1-10), models in fixed order
model_order = {"Claude": 0, "Gemini": 1, "ChatGPT": 2}
text_order  = {"Mix.": 0, "Comp.": 1}
table["_to"] = table["Text"].map(text_order)
table["_mo"] = table["Model"].map(model_order)
table.sort_values(["_to", "Chunk", "_mo"], inplace=True)
table.drop(columns=["_to", "_mo"], inplace=True)

# ── 7. Save outputs ───────────────────────────────────────────────────────────

table.to_csv("table_a2.csv", index=False)
print("Saved table_a2.csv")
print(table.to_string(index=False))

# HTML preview
html = table.to_html(index=False, border=1)
html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Table A2</title>
<style>
  body {{ font-family: Arial, sans-serif; padding: 20px; }}
  h2 {{ font-size: 14px; font-weight: bold; }}
  table {{ border-collapse: collapse; font-size: 12px; }}
  th, td {{ border: 1px solid #999; padding: 4px 10px; text-align: center; }}
  th {{ background: #f0f0f0; font-weight: bold; }}
  td:nth-child(3) {{ text-align: left; }}
  .mix-header td, .comp-header td {{ font-style: italic; font-weight: bold;
                                     background: #f8f8f8; text-align: left; }}
</style>
</head>
<body>
<h2>Table A2. Per-Passage Automated Metric Scores for All 60 LLM Translations</h2>
{html}
<p style="font-size:10px; max-width:700px">
<em>Note:</em> BLEU-4, BERTScore, and COMET scores shown as percentages.
For Mix., multi-reference scores are reported (maximum across Johnston and Singer
and van der Eijk references). For Comp., single expert reference translation used.
TQS and Rating from MQM human evaluation included for comparison.
Rating = Scheme 1 (HP = High Pass, LP = Low Pass, F = Fail).
</p>
</body>
</html>"""

with open("table_a2.html", "w") as f:
    f.write(html)
print("Saved table_a2.html")