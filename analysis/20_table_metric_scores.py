"""20 Table 1: automated metric scores by text and model, mean (SD) x 100.

Each translation is scored against one reference at a time. A Mix. translation's score is the
mean of its scores against the two references (Johnston; Singer and van der Eijk), so that Mix.
and Comp. (one reference) are scored alike (common.metric_scores('mean')).

Inputs : mt_eval/output/evaluations/*.json, data/mt_eval_scores*.csv (via common)
Outputs: table_1.csv (as printed), table_1_values.csv (six decimals), statistics_20_table_metric_scores.csv
"""
import pandas as pd

from common import LABEL, METRICS, MODELS, CellValues, Statistics, f_mean_sd, metric_scores, subset
from tables import write_table

STATS = Statistics(__file__)
V = CellValues()
sc = metric_scores('mean')

rows = []
for text in ('Mix', 'Comp'):
    for model in MODELS + ['Aggregate']:
        g = subset(sc, text, model)
        row = {'Text': LABEL[text] if model == MODELS[0] else '', 'Model': model}
        for m in METRICS:
            mean, sd = g[m].mean() * 100, g[m].std(ddof=1) * 100
            row[m] = f_mean_sd(mean, sd)
            V(f'{LABEL[text]} {model}', m, 'mean x100', mean)
            V(f'{LABEL[text]} {model}', m, 'SD x100', sd)
        rows.append(row)
table = pd.DataFrame(rows)
write_table('metric_aggregate', table, V)

# ---------------------------------------------------------------- the models compared
for text in ('Mix', 'Comp'):
    def mean(model, m):
        return V.get(f'{LABEL[text]} {model}', m, 'mean x100')
    first = [m for m in METRICS if max(MODELS, key=lambda mo: mean(mo, m)) == 'Gemini']
    order = [m for m in METRICS if mean('Gemini', m) > mean('Claude', m) > mean('ChatGPT', m)]
    STATS.add(f'metric_gemini_highest_{text}', len(first),
              f'{LABEL[text]}: metrics (of 7) on which Gemini has the highest mean ({", ".join(first)})')
    STATS.add(f'metric_order_gcc_{text}', len(order),
              f'{LABEL[text]}: metrics (of 7) whose means order Gemini > Claude > ChatGPT ({", ".join(order)})')
STATS.save()
print(table.to_string(index=False))
