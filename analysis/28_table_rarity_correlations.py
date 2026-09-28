"""28 Table 9: correlation of the rarity of a passage's vocabulary with the quality of its translations.

Pearson r between each rarity measure of a passage (final measure, from 07) and the quality of
its three translations: their mean TQS and their total number of critical errors, over the ten
Comp. passages and over all 20 passages (* p < .05, ** p < .01, *** p < .001).
  Rare term ratio         the share of a passage's words whose lemma occurs fewer than 50 times
                          in Diorisis or does not occur in it
  Average Zipf frequency  the mean Zipf-scaled Diorisis frequency of those words (0 if absent)

Inputs : outputs/rarity_by_passage_final.csv (from 07), mqm/ summary sheets
Outputs: table_9.csv (as printed), table_9_values.csv (six decimals)
"""
import pandas as pd

from common import OUT, CellValues, f_r, load_mqm, passage_quality, pearson, stars
from tables import write_table

V = CellValues()
rar = pd.read_csv(OUT / 'rarity_by_passage_final.csv')
d = (rar.assign(text=rar.Text.str.rstrip('.'), chunk=rar.Passage)
        .merge(passage_quality(load_mqm()), on=['text', 'chunk'], validate='1:1'))
assert len(d) == 20
comp = d[d.text == 'Comp']

rows = []
for label, col in [('Rare term ratio', 'Rare-term ratio'), ('Average Zipf frequency', 'Mean Zipf')]:
    row = {'Predictor': label}
    for target, frame, y in [('TQS (Comp.)', comp, 'TQS'), ('TQS (All)', d, 'TQS'),
                             ('Critical (Comp.)', comp, 'critical'), ('Critical (All)', d, 'critical')]:
        r, p = pearson(frame[col], frame[y])
        row[target] = f_r(r) + stars(p)
        V(label, target, 'r', r)
        V(label, target, 'p', p)
    rows.append(row)
table = pd.DataFrame(rows)
write_table('rarity_correlations', table, V)
print(table.to_string(index=False))
