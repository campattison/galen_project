"""26 Table 7: pass rates of Mix. and of Comp. with passages excluded, and the Mix.-Comp. gap.

Pass rate = the share of translations rated HIGH PASS or LOW PASS, under Scheme 1 (TQS alone)
and Scheme 2 (FAIL for any critical error). Exclusions apply to Comp. only; Mix. includes all
passages in every row. Gap = Mix. pass rate minus Comp. pass rate, in percentage points.

Inputs : mqm/MQM SUMMARY TABLES - * Summary Sorted.csv
Outputs: table_7.csv (as printed), table_7_values.csv (six decimals)
"""
import pandas as pd

from common import CATASTROPHIC, CellValues, f_pct, load_mqm, rating_s1
from tables import write_table

V = CellValues()
mq = load_mqm()
mq['s1'] = mq.TQS.map(rating_s1)
mq['s2'] = mq.s1.where(mq.critical == 0, 'FAIL')
MIX, COMP = mq[mq.text == 'Mix'], mq[mq.text == 'Comp']


def pass_rate(g, scheme):
    return (g[scheme] != 'FAIL').mean() * 100


rows = [{'Stratification': 'Mix. (all passages)', 'Scheme 1 Pass Rate': f_pct(pass_rate(MIX, 's1'), 1),
         'Scheme 2 Pass Rate': f_pct(pass_rate(MIX, 's2'), 1), 'Scheme 1 Gap': '—', 'Scheme 2 Gap': '—'}]
for scheme in ('s1', 's2'):
    V('Mix. (all passages)', f'Scheme {scheme[1]} Pass Rate', '%', pass_rate(MIX, scheme))
for lab, g in [('Comp. (all passages)', COMP),
               ('Comp. (excl. 8, 10)', COMP[~COMP.chunk.isin(CATASTROPHIC)]),
               ('Comp. (excl. 3, 8, 10)', COMP[~COMP.chunk.isin([3] + CATASTROPHIC)])]:
    row = {'Stratification': lab}
    for scheme in ('s1', 's2'):
        rate, gap = pass_rate(g, scheme), pass_rate(MIX, scheme) - pass_rate(g, scheme)
        row[f'Scheme {scheme[1]} Pass Rate'] = f_pct(rate, 1)
        row[f'Scheme {scheme[1]} Gap'] = f_pct(gap, 1)
        V(lab, f'Scheme {scheme[1]} Pass Rate', '%', rate)
        V(lab, f'Scheme {scheme[1]} Gap', 'points', gap)
    rows.append(row)
table = pd.DataFrame(rows, columns=['Stratification', 'Scheme 1 Pass Rate', 'Scheme 2 Pass Rate', 'Scheme 1 Gap',
                                    'Scheme 2 Gap'])
write_table('ratings_stratified', table, V)
print(table.to_string(index=False))
