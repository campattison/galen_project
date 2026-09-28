"""25 Table 6: quality ratings under Schemes 1 and 2, by text and model.

Scheme 1 rates a translation by its TQS alone: HIGH PASS from 95, LOW PASS from 87, FAIL below
87. Scheme 2 also rates FAIL any translation with a critical error. Both are recomputed here and
checked against the ratings recorded in the MQM sheets. Shares are of 10 translations per model
and text (whole per cent), and of 30 per text for the aggregate (one decimal).

Inputs : mqm/MQM SUMMARY TABLES - * Summary Sorted.csv
Outputs: table_6.csv (as printed), table_6_values.csv (six decimals), statistics_25_table_ratings_by_model.csv
"""
import pandas as pd

from common import LABEL, ROW_MODELS, CellValues, Statistics, f_pct, load_mqm, rating_s1
from tables import write_table

STATS = Statistics(__file__)
V = CellValues()
mq = load_mqm()
mq['s1'] = mq.TQS.map(rating_s1)
mq['s2'] = mq.s1.where(mq.critical == 0, 'FAIL')
assert (mq.s1 == mq.rating_s1).all(), 'Scheme 1 in the MQM sheets does not follow from TQS'
assert (mq.s2 == mq.rating).all(), 'Scheme 2 in the MQM sheets does not follow from TQS and critical errors'
RATINGS = [('HIGH PASS', 'High Pass'), ('LOW PASS', 'Low Pass'), ('FAIL', 'Fail')]

rows = []
for text in ('Mix', 'Comp'):
    for model in ROW_MODELS + ['Aggregate']:
        g = mq[mq.text == text] if model == 'Aggregate' else mq[(mq.text == text) & (mq.model == model)]
        nd = 1 if model == 'Aggregate' else 0
        row = {'Text': LABEL[text] if model == ROW_MODELS[0] else '', 'Model': model}
        for scheme in ('s1', 's2'):
            for rating, lab in RATINGS:
                share = (g[scheme] == rating).sum() / len(g) * 100
                col = f'{scheme.upper()} {lab}'
                row[col] = f_pct(share, nd)
                V(f'{LABEL[text]} {model}', col, '%', share)
        rows.append(row)
table = pd.DataFrame(rows)
write_table('ratings_by_model', table, V)

# ---------------------------------------------------------------- pass rates (HIGH PASS + LOW PASS)
for text in ('Mix', 'Comp'):
    for model in ROW_MODELS:
        g = mq[(mq.text == text) & (mq.model == model)]
        for scheme in ('s1', 's2'):
            STATS.add(f'pass_{scheme}_{text}_{model}', (g[scheme] != 'FAIL').mean() * 100,
                      f'{LABEL[text]} {model}: Scheme {scheme[1]} pass rate (%)')
STATS.save()
print(table.to_string(index=False))
