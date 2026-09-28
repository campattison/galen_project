"""24 Table 5: correlation of each automated metric with TQS over all 60 translations.

Pearson r and Spearman rho, each with a 95% confidence interval by Fisher's z-transformation and a
two-tailed p-value; Mix. scored as in 20 (the mean of its two single-reference scores). Metrics are
ordered by Pearson r, highest first.

Inputs : mt_eval/output/evaluations/*.json, data/mt_eval_scores*.csv (via common), mqm/ summary sheets
Outputs: table_5.csv (as printed), table_5_values.csv (six decimals), statistics_24_table_metric_correlations.csv
"""
import pandas as pd

from common import (KEYS, CellValues, Statistics, correlation_order, correlations, f_ci, f_p, f_r_table, fisher_ci,
                    load_mqm, metric_scores)
from tables import write_table

STATS = Statistics(__file__)
V = CellValues()
tqs = load_mqm()[KEYS + ['TQS']]
sc = metric_scores('mean')
c = correlations(sc, tqs, ['Mix', 'Comp'])
order = correlation_order(sc, tqs)

rows = []
for m in order:
    x = c[m]
    lo, hi = fisher_ci(x['r'], x['n'])
    lo2, hi2 = fisher_ci(x['rho'], x['n'])
    rows.append({'Metric': m,
                 'Pearson r [95% CI]': f"{f_r_table(x['r'], x['p'])} {f_ci(lo, hi)}",
                 'p (Pearson)': f_p(x['p']),
                 'Spearman rho [95% CI]': f"{f_r_table(x['rho'], x['p_rho'])} {f_ci(lo2, hi2)}",
                 'p (Spearman)': f_p(x['p_rho'])})
    for col, stat, v in [('Pearson r [95% CI]', 'r', x['r']), ('Pearson r [95% CI]', 'CI low', lo),
                         ('Pearson r [95% CI]', 'CI high', hi), ('p (Pearson)', 'p', x['p']),
                         ('Spearman rho [95% CI]', 'rho', x['rho']), ('Spearman rho [95% CI]', 'CI low', lo2),
                         ('Spearman rho [95% CI]', 'CI high', hi2), ('p (Spearman)', 'p', x['p_rho'])]:
        V(m, col, stat, v)
table = pd.DataFrame(rows)
write_table('metric_tqs_correlations', table, V)

# ---------------------------------------------------------------- the metrics compared
w = pd.DataFrame({'r': {m: c[m]['r'] for m in c}, 'rho': {m: c[m]['rho'] for m in c}})
STATS.add('corr_order', ', '.join(order), 'metrics by Pearson r with TQS, highest first')
STATS.add('corr_rho_below_r', int((w.rho < w.r).sum()), 'metrics (of 7) whose Spearman rho is below their Pearson r')
STATS.add('corr_largest_r_minus_rho', (w.r - w.rho).idxmax(), 'metric with the largest difference between Pearson r and Spearman rho')
STATS.add('corr_best_rho', w.rho.idxmax(), 'metric with the highest Spearman rho')
mid = order[1:5]
STATS.add('corr_mid_range', f'{w.r[mid].min():.6f}/{w.r[mid].max():.6f}',
          f'lowest / highest Pearson r of the metrics ranked second to fifth ({", ".join(mid)})')
STATS.save()
print(table.to_string(index=False))
