"""23 Table 4: the Mix.-Comp. gap on each automated metric, with Comp. passages excluded.

Gap = (mean Comp. - mean Mix.) / mean Mix. x 100, so a negative gap means Comp. scores lower.
Mix. is scored as in 20 (the mean of its two single-reference scores) and kept whole (30
translations) in every column; the exclusions apply to Comp. only. Significance: Welch's t-test, two-tailed (* p < .05, ** p < .01,
*** p < .001). Effect size: Cohen's d with the pooled SD.

Inputs : mt_eval/output/evaluations/*.json, data/mt_eval_scores*.csv (via common)
Outputs: table_4.csv (as printed), table_4_values.csv (six decimals: gap, Welch p, Cohen's d, the two
         means and the number of Comp. translations of each cell), statistics_23_table_metric_gap.csv
"""
import pandas as pd

from common import METRICS, STRATA, CellValues, Statistics, cohen_d, f_pct, metric_scores, stars, subset, welch_p
from tables import write_table

STATS = Statistics(__file__)
V = CellValues()
sc = metric_scores('mean')

rows = []
for m in METRICS:
    mix = subset(sc, 'Mix')[m]
    row = {'Metric': m}
    for col, excl in STRATA:
        comp = sc[(sc.text == 'Comp') & ~sc.chunk.isin(excl)][m]
        gap = (comp.mean() - mix.mean()) / mix.mean() * 100
        p = welch_p(comp, mix)
        row[col] = f_pct(gap, 1) + stars(p)
        for stat, v in [('gap %', gap), ('Welch p', p), ("Cohen's d", cohen_d(comp, mix)),
                        ('Mix. mean x100', mix.mean() * 100), ('Comp. mean x100', comp.mean() * 100),
                        ('Comp. n', len(comp))]:
            V(m, col, stat, v)
    rows.append(row)
table = pd.DataFrame(rows)
write_table('metric_gap_stratified', table, V)

# ---------------------------------------------------------------- effect sizes and p-values across the table
w = V.frame().pivot_table(index=['row', 'column'], columns='statistic', values='value')
d_all = w.xs('All passages', level='column')["Cohen's d"].abs()
STATS.add('gap_d_all_min', d_all.min(), "smallest |Cohen's d|, all passages")
STATS.add('gap_d_all_max', d_all.max(), "largest |Cohen's d|, all passages")
STATS.add('gap_d_all_min_metric', d_all.idxmin(), "metric with the smallest |Cohen's d|, all passages")
STATS.add('gap_d_any_min', w["Cohen's d"].abs().min(), "smallest |Cohen's d| in any column")
for col, tag in [('All passages', 'all'), ('Excl. 8, 10', 'x810'), ('Excl. 3, 8, 10', 'x3810')]:
    STATS.add(f'gap_p_{tag}_max', w.xs(col, level='column')['Welch p'].max(), f'largest Welch p, {col}')
ns = w[w['Welch p'] >= .05]
STATS.add('gap_ns_cells', len(ns), 'gaps not significant at .05 (' +
          ('; '.join(f'{r} {c}' for r, c in ns.index) or 'none') + ')')
STATS.save()
print(table.to_string(index=False))
