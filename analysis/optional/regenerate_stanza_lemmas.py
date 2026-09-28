"""Rerun Stanza on the passages and compare with the two frozen Stanza files in data/ (optional).

data/stanza_lemmas.csv is the frozen Stanza output behind the original measure (20 passages,
read from corpus_metrics/mix.txt and comp.txt, whose Comp. 1 is the preface of book I), and
data/stanza_lemmas_comp1_translated.csv the same for Comp. 1 as translated (passage 1 of
mt_eval/input/on_comp.txt, read with the pipeline's own parser). This script shows how both
were produced and checks that the same Stanza version still produces them:

    pip install stanza==1.11.0
    python analysis/optional/regenerate_stanza_lemmas.py

It writes outputs/optional/stanza_lemmas_regenerated.csv and
outputs/optional/stanza_lemmas_comp1_translated_regenerated.csv (it never overwrites data/, and
verify.py ignores the subfolder) and reports any rows that differ. Stanza downloads its Ancient Greek
model on first use. The Diorisis corpus is not needed: lemma frequencies come from
corpus_metrics/diorisis_frequencies.json.
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'corpus_metrics'))
sys.path.insert(0, str(HERE))
import stanza  # noqa: E402
from rebuild_difficulty_audit import build_diorisis_frequencies, parse_chunks  # noqa: E402
from common import OUT, load_texts  # noqa: E402

if stanza.__version__ != '1.11.0':
    print(f'warning: stanza {stanza.__version__}; the frozen files were made with 1.11.0')
freq, _ = build_diorisis_frequencies(str(ROOT / 'corpus_metrics' / 'Diorisis'),
                                     str(ROOT / 'corpus_metrics' / 'diorisis_frequencies.json'))
stanza.download('grc', verbose=False)
nlp = stanza.Pipeline('grc', processors='tokenize,pos,lemma', verbose=False)
DEST = OUT / 'optional'
DEST.mkdir(exist_ok=True)
HEADER = ['text', 'chunk', 'word_index', 'word', 'upos', 'lemma', 'diorisis_freq', 'counted_in_metric']


def lemmatise(label, n, greek):
    rows, i = [], 0
    for sent in nlp(greek).sentences:
        for word in sent.words:
            rows.append([label, n, i, word.text, word.upos, word.lemma, freq.get(word.lemma, 0), word.upos != 'PUNCT'])
            i += 1
    return rows


def compare(rows, frozen_path, out_name):
    rows = [HEADER] + rows
    with open(DEST / out_name, 'w', newline='', encoding='utf-8') as fh:
        csv.writer(fh, lineterminator='\n').writerows(rows)
    frozen = list(csv.reader(open(frozen_path, encoding='utf-8', newline='')))
    fresh = [[str(c) for c in r] for r in rows]
    diff = [(k, a, b) for k, (a, b) in enumerate(zip(frozen, fresh)) if a != b]
    print(f'{frozen_path.name}: {len(fresh) - 1} rows regenerated, {len(frozen) - 1} frozen; {len(diff)} differing rows'
          + ('' if len(frozen) == len(fresh) else ' (row counts differ)'))
    for k, a, b in diff[:20]:
        print(f'  row {k}: frozen {a} | now {b}')


original = []
for label, fn in [('Mix', 'mix.txt'), ('Comp', 'comp.txt')]:
    for n, greek in sorted(parse_chunks(str(ROOT / 'corpus_metrics' / fn)).items()):
        original += lemmatise(label, n, greek)
compare(original, HERE / 'data' / 'stanza_lemmas.csv', 'stanza_lemmas_regenerated.csv')
compare(lemmatise('Comp', 1, load_texts()['Comp'][1]['greek']),
        HERE / 'data' / 'stanza_lemmas_comp1_translated.csv', 'stanza_lemmas_comp1_translated_regenerated.csv')
