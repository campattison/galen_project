"""22 Table 3: TQS of Mix. and of Comp. with passages excluded, and the Mix.-Comp. gap.

Exclusions apply to Comp. only: all passages; without passages 8 and 10 (on which every model
failed); without 3, 8 and 10; and without 8, 10 and ChatGPT's translation of passage 3.
Gap = mean TQS of Mix. minus mean TQS of the Comp. subset.

Inputs : mqm/MQM SUMMARY TABLES - * Summary Sorted.csv
Outputs: table_3.csv (as printed), table_3_values.csv (six decimals)
"""
import pandas as pd

from common import CATASTROPHIC, CellValues, f_num, load_mqm
from tables import write_table

V = CellValues()
mq = load_mqm()
MIX, COMP = mq[mq.text == 'Mix'], mq[mq.text == 'Comp']

mix_mean = MIX.TQS.mean()
rows = [{'Stratification': 'Mix. (all passages)', 'TQS Mean': f_num(mix_mean, 1), 'TQS SD': f_num(MIX.TQS.std(ddof=1), 1),
         'Gap vs. Mix.': '—'}]
V('Mix. (all passages)', 'TQS Mean', 'mean', mix_mean)
V('Mix. (all passages)', 'TQS SD', 'SD', MIX.TQS.std(ddof=1))
subsets = [('Comp. (all passages)', COMP),
           ('Comp. (excl. 8, 10)', COMP[~COMP.chunk.isin(CATASTROPHIC)]),
           ('Comp. (excl. 3, 8, 10)', COMP[~COMP.chunk.isin([3] + CATASTROPHIC)]),
           ('Comp. (excl. 8, 10, and ChatGPT on 3)',
            COMP[~COMP.chunk.isin(CATASTROPHIC) & ~((COMP.chunk == 3) & (COMP.model == 'ChatGPT'))])]
for lab, g in subsets:
    rows.append({'Stratification': lab, 'TQS Mean': f_num(g.TQS.mean(), 1), 'TQS SD': f_num(g.TQS.std(ddof=1), 1),
                 'Gap vs. Mix.': f_num(mix_mean - g.TQS.mean(), 1)})
    V(lab, 'TQS Mean', 'mean', g.TQS.mean())
    V(lab, 'TQS SD', 'SD', g.TQS.std(ddof=1))
    V(lab, 'Gap vs. Mix.', 'points', mix_mean - g.TQS.mean())
table = pd.DataFrame(rows)
write_table('mqm_stratified', table, V)
print(table.to_string(index=False))
