"""09 Hand check of a sample of the repaired lemmas.

A random sample of 50 repaired lemmas (25 Mix., 25 Comp.; numpy default_rng seed 2026) was
checked by hand (J. Zainaldin, 18 Sept 2026): is the corrected lemma the right dictionary word,
and is the word correctly classed as rare or common? This script redraws the sample from the
seed, to show that it is the same 50 words, and reports the accuracy with Wilson 95% intervals.

The sampling frame: the 449 word tokens of data/stanza_lemmas.csv (whose Comp. 1 is the preface)
whose Stanza lemma matches nothing in Diorisis and which step 2 of rarity.py repairs, words
re-joined at ῤῥ (never repaired) and forms elided with a keraia (the ὑπ΄ of Comp. 9) excluded.
3 of the 25 Comp. words come from the preface, which the final measure does not include; they
are counted separately.

Inputs : data/lemma_check_sample.csv, data/stanza_lemmas.csv (via rarity.py)
Outputs: lemma_check_summary.csv, statistics_09_lemma_check.csv
"""
import numpy as np
import pandas as pd

from common import DATA, Statistics, wilson, write_csv
from greek import KERAIA, read_stanza_tokens
from rarity import repair

STATS = Statistics(__file__)
sample = pd.read_csv(DATA / 'lemma_check_sample.csv', dtype=str, keep_default_na=False)

# the sampling frame: data/stanza_lemmas.csv (Comp. 1 = the preface), steps 1-2
tok = pd.DataFrame([repair(t) for t in read_stanza_tokens(DATA / 'stanza_lemmas.csv', merge=True)])
w = tok[(tok.kind == 'word') & ~tok.merged]
frame = w[(w.stanza_freq == 0) & (w.freq_step2 > 0) & ~w.word.str[-1].isin(list(KERAIA))]
assert len(frame) == 449, len(frame)
rng = np.random.default_rng(2026)
drawn = pd.concat([g.iloc[rng.choice(len(g), 25, replace=False)] for _, g in frame.groupby('text')])
drawn = drawn.assign(c=drawn.chunk.astype(int), i=drawn.word_index.astype(int)).sort_values(['text', 'c', 'i'])
same = (list(zip(drawn.text, drawn.c, drawn.i, drawn.word)) ==
        list(zip(sample.text, sample.chunk.astype(int), sample.word_index.astype(int), sample.word)))
assert same, 'the recorded sample is not the one the seed produces'
assert (drawn.freq_step2.astype(float).astype(int).values == sample.diorisis_count.astype(int).values).all()

rows = []
for col, what in [('lemma_correct', 'corrected lemma is the right dictionary word'),
                  ('status_correct', 'word correctly classed as rare or common')]:
    k, n = int((sample[col] == 'Y').sum()), len(sample)
    lo, hi = wilson(k, n)
    rows.append({'check': what, 'correct': k, 'checked': n, 'share %': k / n * 100, 'Wilson 95% low %': lo * 100,
                 'Wilson 95% high %': hi * 100})
    key = col.split('_')[0]
    STATS.add(f'check_{key}_k', k, f'hand check: {what}')
    STATS.add(f'check_{key}_pct', k / n * 100, f'share (%): {what}')
    STATS.add(f'check_{key}_ci', f'{lo * 100:.6f}-{hi * 100:.6f}', 'Wilson 95% CI of that share (%)')
write_csv(pd.DataFrame(rows), 'lemma_check_summary.csv')
STATS.add('check_frame', len(frame), 'repaired tokens the sample was drawn from')
pre = sample[(sample.text == 'Comp') & (sample.chunk == '1')]
STATS.add('check_preface_words', len(pre), 'checked words drawn from the preface, which the final measure does not include')
k_in = int(((sample.status_correct == 'Y') & ~sample.index.isin(pre.index)).sum())
STATS.add('check_status_k_final', k_in, 'checked words in the final measure correctly classed as rare or common')
STATS.save()
print(pd.DataFrame(rows).round(1).to_string(index=False))
