"""36 Table SM6: for each metric, how many Mix. translations score higher against each reference.

Each of the 30 Mix. translations is scored against Johnston and against Singer and van der Eijk
separately; the table counts the translations that score higher against each (no metric scores a
translation equally against both).

Inputs : mt_eval/output/evaluations/*.json, data/mt_eval_scores_per_reference.csv (via common)
Outputs: table_SM6.csv (as printed), table_SM6_values.csv (six decimals), statistics_36_table_reference_preferences.csv
"""
import pandas as pd

from common import CellValues, Statistics, f_pct, load_eval
from tables import write_table

STATS = Statistics(__file__)
V = CellValues()
mix = load_eval().query('text == "Mix"')
ROWS = ['BLEU-4', 'chrF++', 'METEOR', 'ROUGE-L', 'BERTScore', 'BLEURT', 'COMET']

rows = []
for m in ROWS:
    j = int((mix[f'{m}|ref1'] > mix[f'{m}|ref2']).sum())
    s = int((mix[f'{m}|ref2'] > mix[f'{m}|ref1']).sum())
    assert j + s == len(mix) == 30, f'tie in {m}'
    name = 'BLEU' if m == 'BLEU-4' else m
    rows.append({'Metric': name, 'Johnston: Preference': str(j), 'Johnston: %': f_pct(j / 30 * 100, 1),
                 'Singer & v.d.E.: Preference': str(s), 'Singer & v.d.E.: %': f_pct(s / 30 * 100, 1), 'Total': '30'})
    V(name, 'Johnston: Preference', 'count', j)
    V(name, 'Johnston: %', '%', j / 30 * 100)
    V(name, 'Singer & v.d.E.: Preference', 'count', s)
    V(name, 'Singer & v.d.E.: %', '%', s / 30 * 100)
table = pd.DataFrame(rows)
write_table('reference_preferences', table, V)

lexical = [int(r['Johnston: Preference']) for r in rows if r['Metric'] in ('BLEU', 'chrF++', 'METEOR', 'ROUGE-L')]
STATS.add('refpref_lexical_range', f'{min(lexical)}/{max(lexical)}',
          'lowest / highest number of Mix. translations (of 30) scoring higher against Johnston on the four '
          'lexical metrics (BLEU-4, chrF++, METEOR, ROUGE-L)')
STATS.save()
print(table.to_string(index=False))
