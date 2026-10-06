"""35 Table SM5: TQS, rating and errors by severity of each of the 60 translations.

From the MQM summary sheets: TQS, the Scheme 1 rating computed from it (HP = HIGH PASS from 95,
LP = LOW PASS from 87, F = FAIL below 87; 25 checks it against the sheets), whether the translation
has a critical error, and its errors of each severity (N = Neutral, Mi = Minor, Ma = Major,
Cr = Critical).

Inputs : mqm/MQM SUMMARY TABLES - * Summary Sorted.csv
Outputs: table_SM5.csv
"""
import pandas as pd

from common import LABEL, RATING_ABBR, ROW_MODELS, f_num, load_mqm, rating_s1
from tables import write_table

mq = load_mqm()
COLS = ['Text', 'Passage', 'Model', 'TQS', 'Rating', 'Crit.?', 'N', 'Mi', 'Ma', 'Cr']
rows = []
for text in ('Mix', 'Comp'):
    rows.append({c: (LABEL[text] if c == 'Text' else '') for c in COLS})      # a row naming the text
    for n in range(1, 11):
        for model in ROW_MODELS:
            r = mq[(mq.text == text) & (mq.chunk == n) & (mq.model == model)].iloc[0]
            rows.append({'Text': '', 'Passage': str(n), 'Model': model,
                         'TQS': f_num(r.TQS, 1), 'Rating': RATING_ABBR[rating_s1(r.TQS)], 'Crit.?': 'Yes' if r.critical else 'No',
                         'N': str(r.neutral), 'Mi': str(r.minor), 'Ma': str(r.major), 'Cr': str(r.critical)})
table = pd.DataFrame(rows, columns=COLS)
write_table('mqm_all60', table)
print(table.head(12).to_string(index=False))
