"""32 Table SM2: automated metric scores of Mix. under four ways of using its two references.

  Johnston only / Singer and van der Eijk only   each translation scored against that reference alone
  Mean of the two                                the mean of those two scores (the protocol of the
                                                 other metric tables)
  Library multi-reference                        the pipeline's multi-reference score: BLEU-4 pools
                                                 n-gram matches over both references; for the other
                                                 metrics it equals the higher of the two
                                                 single-reference scores (common.metric_scores)
Means x 100 over the 30 Mix. translations (and by model). Also the correlation of each metric
with TQS under each protocol, within Mix. and over all 60 translations (correlations_by_protocol.csv),
and how far the protocol moves the aggregate scores.

Inputs : mt_eval/output/evaluations/*.json, data/mt_eval_scores*.csv (via common), mqm/ summary sheets
Outputs: table_SM2.csv (as printed), table_SM2_values.csv (six decimals), correlations_by_protocol.csv,
         statistics_32_table_reference_protocols.csv
"""
import pandas as pd

from common import (KEYS, METRICS, MODELS, PROTOCOLS, CellValues, Statistics, correlations, f_num,
                    load_mqm, metric_scores, subset, write_csv)
from tables import label, write_table

STATS = Statistics(__file__)
V = CellValues()
tqs = load_mqm()[KEYS + ['TQS']]
S = {p: metric_scores(p) for p in PROTOCOLS}

BLOCKS = [('johnston', 'Johnston only'), ('singer', 'Singer and van der Eijk only'),
          ('mean', f'Mean of the two (as in {label("metric_aggregate")})'), ('multi', 'Library multi-reference')]
rows = []
for p, lab in BLOCKS:
    rows.append({'Model': lab, **{m: '' for m in METRICS}})
    for model in MODELS + ['Aggregate']:
        g = subset(S[p], 'Mix', model)
        row = {'Model': model}
        for m in METRICS:
            row[m] = f_num(g[m].mean() * 100, 1)
            V(f'{lab} {model}', m, 'mean x100', g[m].mean() * 100)
        rows.append(row)
table = pd.DataFrame(rows)
write_table('mix_reference_protocols', table, V)

# ---------------------------------------------------------------- correlations with TQS under each protocol
rows = []
for p in PROTOCOLS:
    for scope, texts in [('Mix', ['Mix']), ('All', ['Mix', 'Comp'])]:
        c = correlations(S[p], tqs, texts)
        for m in METRICS:
            rows.append({'protocol': p, 'scope': scope, 'metric': m, **c[m]})
cbp = pd.DataFrame(rows)
write_csv(cbp, 'correlations_by_protocol.csv')
mixc = cbp[cbp.scope == 'Mix']
allr = cbp[cbp.scope == 'All'].pivot(index='metric', columns='protocol', values='r')
STATS.add('protocol_mix_significant', int((mixc.p < .05).sum()),
          'correlations with TQS within Mix. significant at .05, any metric, any protocol')
STATS.add('protocol_mix_max_abs_r', mixc.r.abs().max(), 'largest |Pearson r| with TQS within Mix., any metric, any protocol')
STATS.add('protocol_mix_min_p', mixc.p.min(), 'smallest p for those correlations')
STATS.add('protocol_bert_highest', bool((allr.idxmax() == 'BERTScore').all()),
          'BERTScore has the highest Pearson r with TQS (all 60) under every protocol')
STATS.add('protocol_bert_r_range', f"{allr.loc['BERTScore'].min():.6f}/{allr.loc['BERTScore'].max():.6f}",
          'lowest / highest Pearson r of BERTScore with TQS (all 60) across the four protocols')

# ---------------------------------------------------------------- how far the protocol moves the aggregate scores
agg = {p: subset(S[p], 'Mix')[METRICS].mean() * 100 for p in PROTOCOLS}
shift = pd.DataFrame({p: (agg[p] - agg['mean']).abs() for p in PROTOCOLS if p != 'mean'}).drop(index='BLEU-4')
where = shift.stack().idxmax()
STATS.add('protocol_shift_other', shift.max().max(),
          f'largest difference from the mean protocol in the Mix. mean x100 of any metric other than BLEU-4 ({where[0]}, {where[1]})')
STATS.save()
print(table.to_string(index=False))
