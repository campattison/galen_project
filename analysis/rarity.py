"""The rules of the corrected rarity measure, shared by 07 (which builds the measure) and
09 (which redraws the hand-checked sample from its sampling frame).

  step 1  notation removed and tokenisation fixed: numerals and symbols dropped, weight
          abbreviations expanded (δραχ. -> δραχμή), words that Stanza split at Kühn's ῤῥ
          re-joined (read_stanza_tokens in greek.py does the re-joining)
  step 2  unmatched lemmas repaired: if Stanza's lemma is not in Diorisis, use the same lemma
          with normalised accents/case if Diorisis has it, otherwise the lemma Diorisis itself
          assigns to this word form (most frequent analysis); a word that Diorisis does not
          contain at all stays at frequency 0 and counts as rare
  step 3  hand decisions: where Stanza's lemma and Diorisis's lemma for the form disagree about
          rare/common, the decision recorded in data/lemma_decisions.csv

Nothing here is random, and no step depends on set or dict iteration order.
"""
import json
import math
from collections import defaultdict

import pandas as pd

from common import DATA, RARE_BELOW, ROOT
from greek import ABBREVIATIONS, bare, lookup_key, norm_lemma

F = json.load(open(ROOT / 'corpus_metrics' / 'diorisis_frequencies.json', encoding='utf-8'))
F, NTOK = F['frequencies'], F['corpus_size']
IDX = json.load(open(DATA / 'diorisis_form_index.json', encoding='utf-8'))
DEC = pd.read_csv(DATA / 'lemma_decisions.csv', keep_default_na=False)
DECISION = dict(zip(DEC.word, DEC.final_lemma))


def zipf(f):
    return 0.0 if f == 0 else math.log10(f / NTOK * 1e9)


F_NORM, F_REP = defaultdict(int), {}
for lemma in sorted(F):
    k = norm_lemma(lemma)
    F_NORM[k] += F[lemma]
    if k not in F_REP or F[lemma] > F[F_REP[k]]:
        F_REP[k] = lemma


def diorisis_lemma(word):
    """Lemma Diorisis most often assigns to this form (exact key, then bare letters)."""
    key = lookup_key(word)
    for table, k in (('form', key), ('bare', bare(key))):
        cands = IDX[table].get(k)
        if cands:
            lemma = sorted(cands.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            return lemma, F.get(lemma, 0)
    return '', 0


def repair(t):
    """Steps 1 and 2 for one token from greek.read_stanza_tokens(merge=True)."""
    r = {k: t[k] for k in ('text', 'chunk', 'word_index', 'word', 'kind', 'merged', 'stanza_lemma', 'stanza_freq')}
    r.update(included=t['kind'] in ('word', 'abbreviation'), lemma='', source='', freq_step1=None,
             freq_step2=None, freq_final=None, diorisis_form_lemma='', diorisis_form_freq=None, disagreement=False)
    if r['included']:
        if t['kind'] == 'abbreviation':
            lemma = ABBREVIATIONS[t['word']]
            assert F.get(lemma, 0) > 0, lemma
            r.update(lemma=lemma, source='abbreviation expanded', freq_step1=F[lemma])
        else:
            r.update(lemma=t['stanza_lemma'], source='Stanza lemma', freq_step1=t['stanza_freq'])
            dl, df = diorisis_lemma(t['word'])
            r.update(diorisis_form_lemma=dl, diorisis_form_freq=df)
        # step 2: repair lemmas that match nothing in Diorisis
        r['freq_step2'] = r['freq_step1']
        if t['kind'] == 'word' and r['freq_step1'] == 0:
            k = norm_lemma(t['stanza_lemma'])
            if not t['merged'] and F_NORM.get(k, 0) > 0:
                r.update(lemma=F_REP[k], source='Stanza lemma, accents/case normalised', freq_step2=F_NORM[k])
            elif r['diorisis_form_freq']:
                r.update(lemma=r['diorisis_form_lemma'], source='Diorisis lemma for this form', freq_step2=r['diorisis_form_freq'])
            else:
                r.update(lemma='', source='word absent from Diorisis', freq_step2=0)
        r['freq_final'] = r['freq_step2']
    return r


def disagrees(r):
    """Stanza's lemma and Diorisis's lemma for the form disagree about rare/common."""
    return bool(r['source'] == 'Stanza lemma' and r['diorisis_form_lemma']
                and norm_lemma(r['diorisis_form_lemma']) != norm_lemma(r['stanza_lemma'])
                and (r['freq_step1'] < RARE_BELOW) != (r['diorisis_form_freq'] < RARE_BELOW))


def decide(r):
    """Step 3 for one repaired token: apply the recorded hand decision where the two disagree."""
    if disagrees(r):
        assert r['word'] in DECISION, f"no decision recorded for {r['word']}"
        final = DECISION[r['word']]
        r.update(disagreement=True, lemma=final, source='hand decision', freq_final=F[final])
    return r
