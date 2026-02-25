"""
reproduce_table_a3.py
Reproduces Table A3: Per-Passage MQM Scores for All 60 LLM Translations

Columns: Text | Ch. | Model | TQS | Rating | Crit.? | N | Mi | Ma | Cr

Sources:
    MQM_SUMMARY_TABLES_Comp_Summary_Sorted.csv
    MQM_SUMMARY_TABLES_Mixtures_Summary_Sorted.csv

Run from the folder containing these CSVs:
    python reproduce_table_a3.py

Outputs:
    table_a3.csv    — raw data for audit
    table_a3.html   — formatted HTML preview
"""

import pandas as pd

# ── 1. Load & concatenate ─────────────────────────────────────────────────────

comp = pd.read_csv("MQM_SUMMARY_TABLES_Comp_Summary_Sorted.csv")
mix  = pd.read_csv("MQM_SUMMARY_TABLES_Mixtures_Summary_Sorted.csv")

df = pd.concat([comp, mix], ignore_index=True)

# Drop stray header/blank rows produced by Excel export
df = df[df["Model"].notna()]
df = df[df["Model"] != "Model"]
df = df[df["Chunk"].notna()]

# Deduplicate – the two CSVs overlap; keep first occurrence per Text/Chunk/Model
df["Chunk_num"] = pd.to_numeric(df["Chunk"], errors="coerce")
df.drop_duplicates(subset=["Text", "Chunk_num", "Model"], keep="first", inplace=True)
df.drop(columns=["Chunk_num"], inplace=True)

# ── 2. Normalise types ────────────────────────────────────────────────────────

df["Chunk"] = pd.to_numeric(df["Chunk"], errors="coerce")
df.dropna(subset=["Chunk"], inplace=True)
df["Chunk"] = df["Chunk"].astype(int)

df["TQS"]   = pd.to_numeric(df["TQS"], errors="coerce").round(1)

for col in ["Neutral", "Minor", "Major", "Critical"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# ── 3. Display labels ─────────────────────────────────────────────────────────

model_map = {"claude": "Claude", "gemini": "Gemini", "openai": "ChatGPT"}
df["Model"] = df["Model"].map(model_map).fillna(df["Model"])

text_map  = {"Mixtures": "Mix.", "Comp": "Comp."}
df["Text"] = df["Text"].map(text_map).fillna(df["Text"])

rating_map = {"HIGH PASS": "HP", "LOW PASS": "LP", "FAIL": "F"}
df["Rating"] = df["Quality Rating"].map(rating_map)

# Critical Error? stored as TRUE/FALSE strings or booleans
df["Crit.?"] = df["Critical Error?"].astype(str).str.upper().map(
    {"TRUE": "Yes", "FALSE": "No", "YES": "Yes", "NO": "No"}
).fillna(df["Critical Error?"])

# ── 4. Select & rename display columns ───────────────────────────────────────

table = df[[
    "Text", "Chunk", "Model", "TQS", "Rating", "Crit.?",
    "Neutral", "Minor", "Major", "Critical"
]].rename(columns={
    "Chunk":    "Ch.",
    "Neutral":  "N",
    "Minor":    "Mi",
    "Major":    "Ma",
    "Critical": "Cr",
})

# ── 5. Sort: Mix. chunks 1-10 then Comp. chunks 1-10; Claude/Gemini/ChatGPT ──

text_order  = {"Mix.": 0, "Comp.": 1}
model_order = {"Claude": 0, "Gemini": 1, "ChatGPT": 2}
table["_to"] = table["Text"].map(text_order)
table["_mo"] = table["Model"].map(model_order)
table.sort_values(["_to", "Ch.", "_mo"], inplace=True)
table.drop(columns=["_to", "_mo"], inplace=True)

# ── 6. Save CSV ───────────────────────────────────────────────────────────────

table.to_csv("table_a3.csv", index=False)
print("Saved table_a3.csv")
print(table.to_string(index=False))

# ── 7. Save HTML preview ──────────────────────────────────────────────────────

html_body = table.to_html(index=False, border=1)

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Table A3</title>
<style>
  body {{ font-family: Arial, sans-serif; padding: 20px; }}
  h2   {{ font-size: 14px; font-weight: bold; }}
  table {{ border-collapse: collapse; font-size: 12px; }}
  th, td {{ border: 1px solid #999; padding: 4px 10px; text-align: center; }}
  th   {{ background: #e8e8e8; font-weight: bold; }}
  td:nth-child(3) {{ text-align: left; }}
</style>
</head>
<body>
<h2>Table A3. Per-Passage MQM Scores for All 60 LLM Translations</h2>
{html_body}
<p style="font-size:10px; max-width:760px">
<em>Note:</em> TQS = Translation Quality Score (0–100). Rating under Scheme 1:
HP = High Pass (≥95), LP = Low Pass (87–94), F = Fail (&lt;87).
Crit.? = contains ≥1 critical error. Severity columns:
N = Neutral, Mi = Minor, Ma = Major, Cr = Critical.
</p>
</body>
</html>"""

with open("table_a3.html", "w") as f:
    f.write(html)
print("Saved table_a3.html")