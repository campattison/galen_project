"""03 Error composition: terminology vs accuracy errors, by group of passages.

From the MQM summary counts: how many errors (and critical errors) fall in each group
of passages, and what share are Terminology errors (the rest are Accuracy errors:
mistranslation, over-/undertranslation, addition, omission).

Inputs : mqm/MQM SUMMARY TABLES - * Summary Sorted.csv
Outputs: error_composition.csv, critical_errors_by_passage.csv, statistics_03_error_composition.csv
"""
import pandas as pd

from common import CATASTROPHIC, Statistics, load_mqm, write_csv

STATS = Statistics(__file__)
mq = load_mqm()
mq['errors'] = mq[['neutral', 'minor', 'major', 'critical']].sum(axis=1)
assert (mq.errors == mq.term + mq.acc).all(), 'every error is either Terminology or Accuracy'

is_cat = (mq.text == 'Comp') & mq.chunk.isin(CATASTROPHIC)
groups = [('Mix. (all 10 passages)', mq.text == 'Mix'),
          ('Comp. (all 10 passages)', mq.text == 'Comp'),
          ('Comp. 8 and 10', is_cat),
          ('Comp. other eight', (mq.text == 'Comp') & ~is_cat)]
rows = []
SUBTYPES = [('term_acc', 'Term.: Accuracy'), ('term_cons', 'Term.: Consistency'),
            ('acc_mis', 'Acc.: Mistranslation'), ('acc_over', 'Acc.: Overtranslation'),
            ('acc_under', 'Acc.: Undertranslation'), ('acc_add', 'Acc.: Addition'), ('acc_om', 'Acc.: Omission')]
for name, mask in groups:
    g = mq[mask]
    rows.append({'group': name, 'errors': int(g.errors.sum()), 'terminology': int(g.term.sum()),
                 'accuracy': int(g.acc.sum()), 'terminology share %': g.term.sum() / g.errors.sum() * 100,
                 'critical': int(g.critical.sum()),
                 **{lab: int(g[col].sum()) for col, lab in SUBTYPES}})
ec = pd.DataFrame(rows)
write_csv(ec, 'error_composition.csv')
E = ec.set_index('group')

cat = E.loc['Comp. 8 and 10']
STATS.add('err_cat_total', int(cat.errors), 'errors in Comp. 8 and 10')
STATS.add('err_cat_term', int(cat.terminology), 'Terminology errors in Comp. 8 and 10')
STATS.add('crit_cat', int(cat.critical), 'critical errors in Comp. 8 and 10')
lower_bound = int(cat.critical) - int(cat.accuracy)
STATS.add('crit_cat_term_min', lower_bound, 'critical errors in Comp. 8 and 10 that must be Terminology (critical minus all Accuracy errors)')
STATS.add('err_cat_acc_excl_omission', int(cat['Acc.: Mistranslation'] + cat['Acc.: Addition'] + cat['Acc.: Overtranslation']
                              + cat['Acc.: Undertranslation']), 'errors of mistranslation, over-/undertranslation or addition in Comp. 8 and 10')
STATS.add('err_cat_breakdown', f"{int(cat['Term.: Accuracy'])}/{int(cat.errors)}", 'Comp. 8 and 10: Terminology-Accuracy errors / all errors (the rest are omissions)')
for name, key in [('Mix. (all 10 passages)', 'mix'), ('Comp. other eight', 'other'),
                  ('Comp. 8 and 10', 'cat'), ('Comp. (all 10 passages)', 'comp')]:
    row = E.loc[name]
    acc_share = row.accuracy / row.errors * 100
    mis_share = row['Acc.: Mistranslation'] / row.errors * 100
    STATS.add(f'acc_share_{key}', acc_share, f'Accuracy share of errors (%), {name}')
    STATS.add(f'mis_share_{key}', mis_share, f'mistranslation share of errors (%), {name}')
oth = E.loc['Comp. other eight']
STATS.add('err_other_mis', int(oth['Acc.: Mistranslation']), 'mistranslation errors in the other eight Comp. passages')
for name, key in [('Comp. 8 and 10', 'cat'), ('Comp. other eight', 'other'), ('Mix. (all 10 passages)', 'mix'),
                  ('Comp. (all 10 passages)', 'comp')]:
    STATS.add(f'term_share_{key}', E.loc[name, 'terminology share %'], f'Terminology share of errors (%), {name}')
STATS.add('crit_comp', int(E.loc['Comp. (all 10 passages)', 'critical']), 'critical errors, Comp.')
STATS.add('crit_mix', int(E.loc['Mix. (all 10 passages)', 'critical']), 'critical errors, Mix.')
STATS.add('crit_other_comp', int(E.loc['Comp. other eight', 'critical']), 'critical errors in the eight other Comp. passages')

by_passage = (mq.groupby(['text', 'chunk'])
                .agg(critical=('critical', 'sum'), errors=('errors', 'sum'), terminology=('term', 'sum'),
                     accuracy=('acc', 'sum'))
                .reset_index())
write_csv(by_passage, 'critical_errors_by_passage.csv')
STATS.save()
print(ec.round(1).to_string(index=False))
