"""31 Table SM1: the 20 passages, their location in the editions and their length in words.

Words are counted in the Greek text as given to the models (mt_eval/input/*.txt, read with the
pipeline's own parser): every word written in Greek letters counts, numerals written with letters
(ιβ΄) included; chapter numbers (16., VI.) and the sign ♃ that opens a recipe do not. Words are
split at spaces and at punctuation, so a comma with no space after it (Comp. 4,
προτραπήσεσθαι,γνῶναι) still separates two words. The average is rounded half up on its exact
value. The length of each whole work is the sum of the ten division totals in the report at the
foot of corpus_metrics/mix.txt and comp.txt, which the extraction procedure wrote.

Inputs : mt_eval/input/*.txt, data/passage_locations.csv, corpus_metrics/mix.txt, corpus_metrics/comp.txt
Outputs: table_SM1.csv (as printed), table_SM1_values.csv (six decimals), statistics_31_table_dataset.csv
"""
import re
import unicodedata
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

from common import DATA, LABEL, ROOT, CellValues, Statistics, load_texts
from greek import has_greek_letter
from tables import write_table

STATS = Statistics(__file__)
V = CellValues()
WORD = re.compile(r"[^\s,.;:·;()\[\]⟨⟩<>\"“”‘«»—–-]+")


def words(greek):
    return [w for w in WORD.findall(unicodedata.normalize('NFC', greek)) if has_greek_letter(w)]


texts = load_texts()
loc = pd.read_csv(DATA / 'passage_locations.csv', dtype=str)
rows, counts = [], []
for text in ('Mix', 'Comp'):
    for n in range(1, 11):
        w = len(words(texts[text][n]['greek']))
        counts.append(w)
        where = loc[(loc.text == text) & (loc.passage == str(n))].location
        assert len(where) == 1, (text, n)
        rows.append({'Work': LABEL[text] if n == 1 else '', 'Passage': str(n), 'Location': where.iloc[0], 'Words': str(w)})
        V(f'{LABEL[text]} {n}', 'Words', 'count', w)
# an average of whole numbers can end exactly in 5 (4,407 / 20 = 220.35): round half up, on the exact value
avg = Decimal(sum(counts)) / Decimal(len(counts))
rows.append({'Work': '', 'Passage': '', 'Location': 'Average Word Count', 'Words': str(avg.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))})
V('Average Word Count', 'Words', 'mean', float(avg))
table = pd.DataFrame(rows)
write_table('dataset', table, V)

for text, fn in (('Mix', 'mix.txt'), ('Comp', 'comp.txt')):
    report = (ROOT / 'corpus_metrics' / fn).read_text(encoding='utf-8').split('--- Report ---')[1]
    totals = [int(t) for t in re.findall(r'total=(\d+)', report)]
    assert len(totals) == 10, (fn, totals)
    STATS.add(f'work_words_{text}', sum(totals), f'{LABEL[text]}: words in the whole work (every token with a letter, '
              'numerals included)')
STATS.save()
print(table.to_string(index=False))
