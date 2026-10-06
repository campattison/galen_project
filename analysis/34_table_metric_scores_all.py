"""34 Table SM4: BLEU-4, BERTScore, COMET, TQS and rating of each of the 60 translations.

Metric scores x 100 with Mix. scored as in 20 (the mean of its two single-reference scores);
TQS from the MQM sheets and the Scheme 1 rating from TQS (HP = HIGH PASS, LP = LOW PASS, F = FAIL).
Scores are rounded with numpy.round (half to even on the value x 100). Also every score of every
translation on all seven metrics, under each reference protocol for Mix. (per_translation_scores.csv).

Inputs : mt_eval/output/evaluations/*.json, data/mt_eval_scores*.csv (via common), mqm/ summary sheets
Outputs: table_SM4.csv (as printed), table_SM4_values.csv (six decimals), per_translation_scores.csv
"""
import numpy as np
import pandas as pd

from common import (KEYS, LABEL, METRICS, RATING_ABBR, ROW_MODELS, CellValues, load_mqm, metric_scores,
                    rating_s1, write_csv)
from tables import write_table

V = CellValues()
mq = load_mqm()
assert (mq.TQS.map(rating_s1) == mq.rating_s1).all(), 'Scheme 1 rating does not follow from the printed TQS'
sc = metric_scores('mean')
SHOWN = ['BLEU-4', 'BERTScore', 'COMET']

d = sc.merge(mq[KEYS + ['TQS']], on=KEYS, validate='1:1').set_index(KEYS)
rows = []
for text in ['Mix', 'Comp']:
    rows.append({'Text': LABEL[text], 'Passage': '', 'Model': '', 'TQS': '', 'BLEU-4': '', 'BERTScore': '',
                 'COMET': '', 'Rating (Scheme 1)': ''})
    for chunk in range(1, 11):
        for model in ROW_MODELS:
            r = d.loc[(text, chunk, model)]
            rows.append({'Text': '', 'Passage': str(chunk), 'Model': model, 'TQS': f'{np.round(r.TQS, 1):.1f}',
                         **{m: f'{np.round(r[m] * 100, 1):.1f}%' for m in SHOWN},
                         'Rating (Scheme 1)': RATING_ABBR[rating_s1(r.TQS)]})
            V(f'{LABEL[text]} {chunk} {model}', 'TQS', 'value', r.TQS)
            for m in SHOWN:
                V(f'{LABEL[text]} {chunk} {model}', m, 'x100', r[m] * 100)
table = pd.DataFrame(rows)
write_table('metric_scores_all60', table, V)

# ---------------------------------------------------------------- every score of every translation
S = {p: metric_scores(p) for p in ('johnston', 'singer', 'multi')}
assert all((S[p][KEYS].values == mq[KEYS].values).all() for p in S) and (sc[KEYS].values == mq[KEYS].values).all()
per = mq[KEYS + ['TQS', 'TQS_exact', 'rating_s1', 'rating']].rename(
    columns={'TQS': 'TQS (MQM sheet)', 'TQS_exact': 'TQS unrounded', 'rating_s1': 'Scheme 1', 'rating': 'Scheme 2'})
is_mix = sc.text == 'Mix'
for m in METRICS:
    per[m] = sc[m].values
    for p, lab in [('johnston', 'vs Johnston'), ('singer', 'vs Singer & vdE'), ('multi', 'multi-reference')]:
        per[f'{m} {lab}'] = S[p][m].where(is_mix).values
write_csv(per, 'per_translation_scores.csv')
print(table.head(12).to_string(index=False))
