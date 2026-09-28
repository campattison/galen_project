"""29 Table 10: correlation of each automated metric with TQS, within each text and combined.

Pearson r and Spearman rho over the 30 translations of Mix., the 30 of Comp., and all 60, with
Mix. scored as in 20 (the mean of its two single-reference scores); * p < .05, ** p < .01,
*** p < .001, two-tailed. Metrics in the order of 24 (Pearson r over all 60, highest first).

Inputs : mt_eval/output/evaluations/*.json, data/mt_eval_scores*.csv (via common), mqm/ summary sheets
Outputs: table_10.csv (as printed), table_10_values.csv (six decimals), statistics_29_table_correlations_by_text.csv
"""
import pandas as pd

from common import (KEYS, METRICS, CellValues, Statistics, correlation_order, correlations, f_r_table, load_mqm,
                    metric_scores)
from tables import write_table

STATS = Statistics(__file__)
V = CellValues()
tqs = load_mqm()[KEYS + ['TQS']]
sc = metric_scores('mean')
BY_TEXT = [('Mix. (n=30)', ['Mix']), ('Comp. (n=30)', ['Comp']), ('Combined (n=60)', ['Mix', 'Comp'])]
cs = {lab: correlations(sc, tqs, texts) for lab, texts in BY_TEXT}

rows = []
for m in correlation_order(sc, tqs):
    row = {'Metric': m}
    for method, rk, pk in [('Pearson', 'r', 'p'), ('Spearman', 'rho', 'p_rho')]:
        for lab, _ in BY_TEXT:
            x = cs[lab][m]
            row[f'{method}: {lab}'] = f_r_table(x[rk], x[pk])
            V(m, f'{method}: {lab}', rk, x[rk])
            V(m, f'{method}: {lab}', pk, x[pk])
    rows.append(row)
table = pd.DataFrame(rows)
write_table('metric_tqs_correlations_by_text', table, V)

# ---------------------------------------------------------------- significance within each text
for lab, texts in BY_TEXT[:2]:
    tag = texts[0]
    x = cs[lab]
    sig_p = [m for m in METRICS if x[m]['p'] < .05]
    sig_s = [m for m in METRICS if x[m]['p_rho'] < .05]
    STATS.add(f'corr_{tag}_sig_pearson', len(sig_p), f'{lab}: metrics with p < .05, Pearson ({", ".join(sig_p) or "none"})')
    STATS.add(f'corr_{tag}_sig_spearman', len(sig_s), f'{lab}: metrics with p < .05, Spearman ({", ".join(sig_s) or "none"})')
    STATS.add(f'corr_{tag}_max_abs_r', max(abs(x[m]['r']) for m in METRICS), f'{lab}: largest |Pearson r|')
    STATS.add(f'corr_{tag}_min_p', min(x[m]['p'] for m in METRICS), f'{lab}: smallest p, Pearson')
STATS.save()
print(table.to_string(index=False))
