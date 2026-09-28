"""21 Table 2: MQM translation quality score (TQS) by text and model: mean, SD, critical errors.

TQS is the value printed in the MQM summary sheets (common.load_mqm, which recomputes it from
the error counts and checks it). Critical errors = the number of errors of critical severity.

Inputs : mqm/MQM SUMMARY TABLES - * Summary Sorted.csv
Outputs: table_2.csv (as printed), table_2_values.csv (six decimals), statistics_21_table_mqm_scores.csv
"""
import pandas as pd

from common import LABEL, MODELS, CellValues, Statistics, f_num, load_mqm
from tables import write_table

STATS = Statistics(__file__)
V = CellValues()
mq = load_mqm()

rows = []
for text in ('Mix', 'Comp'):
    for model in MODELS + ['Aggregate']:
        g = mq[mq.text == text] if model == 'Aggregate' else mq[(mq.text == text) & (mq.model == model)]
        rows.append({'Text': LABEL[text] if model == MODELS[0] else '', 'Model': model,
                     'TQS Mean': f_num(g.TQS.mean(), 1), 'TQS SD': f_num(g.TQS.std(ddof=1), 1),
                     'Critical Errors': str(int(g.critical.sum()))})
        V(f'{LABEL[text]} {model}', 'TQS Mean', 'mean', g.TQS.mean())
        V(f'{LABEL[text]} {model}', 'TQS SD', 'SD', g.TQS.std(ddof=1))
        V(f'{LABEL[text]} {model}', 'Critical Errors', 'count', int(g.critical.sum()))
table = pd.DataFrame(rows)
write_table('mqm_aggregate', table, V)

mean = mq.groupby(['text', 'model']).TQS.mean()
for text in ('Mix', 'Comp'):
    for other in ('Claude', 'ChatGPT'):
        STATS.add(f'tqs_gemini_minus_{other.lower()}_{text}', mean[(text, 'Gemini')] - mean[(text, other)],
                  f'{LABEL[text]}: mean TQS of Gemini minus mean TQS of {other}')
STATS.save()
print(table.to_string(index=False))
