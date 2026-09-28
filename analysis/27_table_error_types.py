"""27 Table 8: MQM errors by severity and by type, Mix. and Comp.

Counts of errors in all 30 translations of each text, with each count's share of that text's
errors, and the ratio of the Comp. share to the Mix. share (computed from unrounded shares).
Every error has both a severity and a type, so both blocks sum to the same total.

Inputs : mqm/MQM SUMMARY TABLES - * Summary Sorted.csv
Outputs: table_8.csv (as printed), table_8_values.csv (six decimals), statistics_27_table_error_types.csv
"""
import pandas as pd

from common import CellValues, Statistics, f_num, f_pct, load_mqm
from tables import write_table

STATS = Statistics(__file__)
V = CellValues()
mq = load_mqm()
SEVERITY = ['neutral', 'minor', 'major', 'critical']
tot = {t: mq[mq.text == t][SEVERITY].sum().sum() for t in ('Mix', 'Comp')}
for t in tot:
    assert tot[t] == mq[mq.text == t][['term', 'acc']].sum().sum(), t
per_tr = {t: tot[t] / len(mq[mq.text == t]) for t in tot}


def ratio(v):
    return f'{v:.1f}×'


rows = [{'': 'Total errors', 'Mix.': str(tot['Mix']), 'Comp.': str(tot['Comp']),
         'Comp./Mix. Ratio': ratio(tot['Comp'] / tot['Mix'])},
        {'': 'Errors per translation', 'Mix.': f_num(per_tr['Mix'], 1), 'Comp.': f_num(per_tr['Comp'], 1),
         'Comp./Mix. Ratio': ratio(per_tr['Comp'] / per_tr['Mix'])}]
for t in ('Mix', 'Comp'):
    V('Total errors', f'{t}.', 'count', tot[t])
    V('Errors per translation', f'{t}.', 'mean', per_tr[t])
V('Total errors', 'Comp./Mix. Ratio', 'ratio', tot['Comp'] / tot['Mix'])
V('Errors per translation', 'Comp./Mix. Ratio', 'ratio', per_tr['Comp'] / per_tr['Mix'])
BLOCKS = [('Severity', [('neutral', 'Neutral'), ('minor', 'Minor'), ('major', 'Major'), ('critical', 'Critical')]),
          ('Error Type', [('term', 'Terminology'), ('acc', 'Accuracy')]),
          ('Terminology Subtypes', [('term_acc', 'Term. Accuracy'), ('term_cons', 'Term. Consistency')]),
          ('Accuracy Subtypes', [('acc_mis', 'Mistranslation'), ('acc_over', 'Overtranslation'),
                                 ('acc_under', 'Undertranslation'), ('acc_add', 'Addition'), ('acc_om', 'Omission')])]
for head, items in BLOCKS:
    rows.append({'': head, 'Mix.': '', 'Comp.': '', 'Comp./Mix. Ratio': ''})
    for col, lab in items:
        n = {t: int(mq[mq.text == t][col].sum()) for t in tot}
        sh = {t: n[t] / tot[t] * 100 for t in tot}
        rows.append({'': lab, 'Mix.': f"{n['Mix']} ({f_pct(sh['Mix'], 1)})", 'Comp.': f"{n['Comp']} ({f_pct(sh['Comp'], 1)})",
                     'Comp./Mix. Ratio': ratio(sh['Comp'] / sh['Mix'])})
        for t in ('Mix', 'Comp'):
            V(lab, f'{t}.', 'count', n[t])
            V(lab, f'{t}.', 'share %', sh[t])
        V(lab, 'Comp./Mix. Ratio', 'ratio', sh['Comp'] / sh['Mix'])
table = pd.DataFrame(rows)
write_table('error_typology', table, V)

STATS.add('errors_total', tot['Mix'] + tot['Comp'], 'errors in both texts together')
STATS.add('errors_comp_over_mix_pct', (tot['Comp'] / tot['Mix'] - 1) * 100, 'how many more errors Comp. has than Mix. (%)')
STATS.save()
print(table.to_string(index=False))
