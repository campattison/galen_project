"""37 Table SM7: the rarity of the vocabulary of each passage (final measure, from 07).

Words = the word tokens the measure counts in the passage (numerals and editorial symbols
excluded; weight abbreviations counted as the words they abbreviate). Avg. Zipf = the mean
Zipf-scaled Diorisis frequency of those words, 0 for a word absent from Diorisis. Rare ratio = the
share of words whose lemma occurs fewer than 50 times in Diorisis or is absent from it; Rare = the
number of those words. Mean = the mean over the ten passages of each text.

Inputs : outputs/rarity_by_passage_final.csv (from 07)
Outputs: table_SM7.csv (as printed), table_SM7_values.csv (six decimals)
"""
import pandas as pd

from common import OUT, CellValues, f_pct
from tables import write_table

V = CellValues()
rar = pd.read_csv(OUT / 'rarity_by_passage_final.csv')
assert len(rar) == 20
COLS = ['Text', 'Ch.', 'Words', 'Avg. Zipf', 'Rare Ratio', 'Rare']
rows, means = [], []                                  # the two means together at the foot
for text in ['Mix.', 'Comp.']:
    g = rar[rar.Text == text]
    rows.append({'Text': text, 'Ch.': '', 'Words': '', 'Avg. Zipf': '', 'Rare Ratio': '', 'Rare': ''})
    for _, r in g.iterrows():
        rows.append({'Text': '', 'Ch.': str(int(r.Passage)), 'Words': str(int(r.Words)),
                     'Avg. Zipf': f"{r['Mean Zipf']:.2f}", 'Rare Ratio': f_pct(r['Rare-term ratio'] * 100, 1),
                     'Rare': str(int(r['Rare words']))})
        V(f'{text} {int(r.Passage)}', 'Avg. Zipf', 'mean', r['Mean Zipf'])
        V(f'{text} {int(r.Passage)}', 'Rare Ratio', '%', r['Rare-term ratio'] * 100)
    means.append({'Text': text, 'Ch.': 'Mean', 'Words': '—', 'Avg. Zipf': f"{g['Mean Zipf'].mean():.2f}",
                  'Rare Ratio': f_pct(g['Rare-term ratio'].mean() * 100, 1), 'Rare': '—'})
    V(f'{text} Mean', 'Avg. Zipf', 'mean', g['Mean Zipf'].mean())
    V(f'{text} Mean', 'Rare Ratio', '%', g['Rare-term ratio'].mean() * 100)
rows.append({c: '' for c in COLS})                    # a blank row before the means
table = pd.DataFrame(rows + means, columns=COLS)
assert len(table) == 25, len(table)                   # 2 block rows + 20 passages + blank + 2 means
write_table('rarity_by_passage', table, V)
print(table.to_string(index=False))
