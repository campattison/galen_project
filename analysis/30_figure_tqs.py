"""30 Figure 1 (data): TQS of each of the 60 translations, by text, passage and model.

The TQS of each translation as printed in the MQM sheets (one decimal); the figure shows Comp. in
the left panel and Mix. in the right, passages as rows and models as columns, on a red-yellow-green
scale from 0 to 100. optional/render_figure1.py draws it from this file.

Inputs : mqm/MQM SUMMARY TABLES - * Summary Sorted.csv
Outputs: figure_1.csv, statistics_30_figure_tqs.csv
"""
import pandas as pd

from common import CATASTROPHIC, LABEL, ROW_MODELS, Statistics, f_num, load_mqm
from tables import write_table

STATS = Statistics(__file__)
mq = load_mqm()
tqs = mq.set_index(['text', 'chunk', 'model']).TQS
fig = pd.DataFrame([{'Text': LABEL[text], 'Passage': str(n), **{m: f_num(tqs[(text, n, m)], 1) for m in ROW_MODELS}}
                    for text in ('Comp', 'Mix') for n in range(1, 11)])      # Comp. is the left panel
write_table('tqs_heatmap', fig)

STATS.add('tqs_mix_min', mq[mq.text == 'Mix'].TQS.min(), 'lowest TQS of any Mix. translation')
STATS.add('tqs_catastrophic_max', mq[(mq.text == 'Comp') & mq.chunk.isin(CATASTROPHIC)].TQS.max(),
          'highest TQS of any translation of Comp. 8 or 10')
for n in range(1, 11):
    STATS.add(f'tqs_passage_Comp{n}', mq[(mq.text == 'Comp') & (mq.chunk == n)].TQS.mean(),
              f'Comp. {n}: mean TQS of the three translations')
STATS.save()
print(fig.to_string(index=False))
