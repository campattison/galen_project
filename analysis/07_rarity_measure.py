"""07 The rarity measure, rebuilt and corrected in documented steps from Stanza's output.

The original measure (corpus_metrics/rebuild_difficulty_audit.py) lemmatised each passage
with Stanza and counted a lemma as rare if it occurs fewer than 50 times in Diorisis
(absent lemmas included). Checked word by word, that count included numerals, weight
abbreviations and stray symbols, and about one word in eight (13%) carried a Stanza lemma
that matches nothing in Diorisis, so it counted as rare whatever the word was. It also
measured the wrong first passage of Comp.: corpus_metrics/comp.txt opens with the preface of
book I (Ἤδη μοι καὶ πρόσθεν ...), not with the passage the models translated and the annotators
scored (I.2, XIII.367,10-369,1 K.: Περὶ μὲν τῆς τῶν ἁπλῶν φαρμάκων δυνάμεως ..., passage 1 of
mt_eval/input/on_comp.txt). The other 19 passages are the translated ones. This script
rebuilds the measure in documented steps from Stanza's own output:

  step 0   original measure: the original method on Stanza's output for the 20 passages it measured
           (its values in corpus_metrics/passage_difficulty_zipf.csv reproduced to 4 decimals), Comp. 1 = the preface
  step 0b  original method, Comp. 1 as translated: the same method, with Comp. 1 the translated
           passage (Stanza output for it: data/stanza_lemmas_comp1_translated.csv)
  steps 1-3 on the corrected passages, by the rules in rarity.py:
  step 1   notation removed and tokenisation fixed: numerals and symbols dropped,
           weight abbreviations expanded (δραχ. -> δραχμή), words that Stanza split at
           Kühn's ῤῥ re-joined (ἀῤ|ῥενικοῦ -> ἀῤῥενικοῦ)
  step 2   unmatched lemmas repaired: if Stanza's lemma is not in Diorisis, use the same
           lemma with normalised accents/case if Diorisis has it, otherwise the lemma
           Diorisis itself assigns to this word form (most frequent analysis); a word that
           Diorisis does not contain at all stays at frequency 0 and counts as rare
  step 3   hand decisions (final): where Stanza's lemma and Diorisis's lemma for the form
           disagree about rare/common, apply the decision recorded in data/lemma_decisions.csv

Inputs : data/stanza_lemmas.csv (Stanza 1.11.0 output for the passages of the original measure, frozen),
         data/stanza_lemmas_comp1_translated.csv (the same Stanza run on the translated Comp. 1),
         data/diorisis_form_index.json, data/lemma_decisions.csv,
         corpus_metrics/diorisis_frequencies.json,
         corpus_metrics/passage_difficulty_zipf.csv (the original measure's values, for the check)
Outputs: rarity_tokens.csv, rarity_by_passage_steps.csv, rarity_by_passage_final.csv (formatted by
         37_table_rarity_by_passage.py), original_measure_reproduction_check.csv,
         rarity_correction_summary.csv, statistics_07_rarity_measure.csv
"""
import pandas as pd

from common import DATA, RARE_BELOW, ROOT, Statistics, write_csv
from greek import read_stanza_tokens
from rarity import DECISION, F, decide, repair, zipf

STATS = Statistics(__file__)
STANZA = DATA / 'stanza_lemmas.csv'                            # the original run (Comp. 1 = the preface)
STANZA_COMP1 = DATA / 'stanza_lemmas_comp1_translated.csv'     # Comp. 1 as translated and scored


# ---------------------------------------------------------------- step 0: reproduce the original measure
pub = pd.DataFrame(read_stanza_tokens(STANZA, merge=False))
assert (pub.stanza_freq == pub.stanza_lemma.map(lambda l: F.get(l, 0))).all(), 'Stanza CSV vs Diorisis frequencies'
pub['zipf'] = pub.stanza_freq.map(zipf)
g0 = (pub.groupby(['text', 'chunk'])
         .agg(tokens=('stanza_freq', 'size'), rare=('stanza_freq', lambda x: int((x < RARE_BELOW).sum())),
              absent=('stanza_freq', lambda x: int((x == 0).sum())), mean_zipf=('zipf', 'mean'),
              mean_zipf_found=('zipf', lambda x: x[x > 0].mean()))
         .reset_index())
original = (pd.read_csv(ROOT / 'corpus_metrics' / 'passage_difficulty_zipf.csv')
               .drop(columns='chunk').rename(columns={'chunk_num': 'n'}))
chk = g0.merge(original, left_on=['text', 'chunk'], right_on=['text', 'n'])
assert len(chk) == 20
checks = pd.DataFrame({
    'text': chk.text, 'chunk': chk.chunk,
    'tokens': chk.tokens == chk.total_terms, 'rare': chk.rare == chk.rare_terms,
    'absent': chk.absent == chk.not_found_terms,
    'rare ratio': (chk.rare / chk.tokens).round(4) == chk.rare_term_ratio,
    'not-found ratio': (chk.absent / chk.tokens).round(4) == chk.not_found_ratio,
    'avg Zipf': chk.mean_zipf.round(4) == chk.avg_zipf,
    'avg Zipf (found only)': chk.mean_zipf_found.round(4) == chk.avg_zipf_found_only})
write_csv(checks, 'original_measure_reproduction_check.csv')
exact = bool(checks.drop(columns=['text', 'chunk']).all().all())
assert exact, 'Stanza output no longer reproduces the original measure'

# ---------------------------------------------------------------- step 0b: the translated Comp. 1
def corrected_passages(merge):
    """Stanza tokens for the 20 passages the models translated: the original run for 19 of
    them, and data/stanza_lemmas_comp1_translated.csv in place of the preface as Comp. 1."""
    frozen = read_stanza_tokens(STANZA, merge=merge)
    comp1 = read_stanza_tokens(STANZA_COMP1, merge=merge)
    assert {(t['text'], t['chunk']) for t in comp1} == {('Comp', 1)}
    at = [i for i, t in enumerate(frozen) if (t['text'], t['chunk']) == ('Comp', 1)]
    assert at == list(range(at[0], at[-1] + 1)), 'Comp. 1 is not one block in the original run'
    return frozen[:at[0]] + comp1 + frozen[at[-1] + 1:]


pub_b = pd.DataFrame(corrected_passages(merge=False))
assert (pub_b.stanza_freq == pub_b.stanza_lemma.map(lambda l: F.get(l, 0))).all(), 'Stanza CSV vs Diorisis frequencies'
n_preface, n_translated = int(((pub.text == 'Comp') & (pub.chunk == 1)).sum()), int(((pub_b.text == 'Comp') & (pub_b.chunk == 1)).sum())

# ---------------------------------------------------------------- steps 1-3 (rules in rarity.py)
tok = pd.DataFrame([decide(repair(t)) for t in corrected_passages(merge=True)])
used = set(tok[tok.disagreement].word)
assert used <= set(DECISION), f'no decision recorded for {sorted(used - set(DECISION))}'
# decisions recorded for words that occur only in the preface (the old Comp. 1) are kept in
# data/lemma_decisions.csv for the record, and listed here
DEC_UNUSED = sorted(set(DECISION) - used)
preface = set(pub[(pub.text == 'Comp') & (pub.chunk == 1)].word)
assert set(DEC_UNUSED) <= preface and not set(DEC_UNUSED) & set(tok.word), \
    f'recorded decisions unused for another reason than the preface: {sorted(set(DEC_UNUSED) - preface)}'
inc = tok[tok.included].copy()
for col in ['freq_step1', 'freq_step2', 'freq_final']:
    inc[col] = inc[col].astype(int)
tok.loc[tok.included, 'rare_final'] = inc.freq_final < RARE_BELOW
tok.loc[tok.included, 'zipf_final'] = inc.freq_final.map(zipf)
for col in ['freq_step1', 'freq_step2', 'freq_final', 'diorisis_form_freq']:
    tok[col] = tok[col].astype('Int64')
write_csv(tok, 'rarity_tokens.csv')

# ---------------------------------------------------------------- per passage, per step
def summarise(freqs, frame, step):
    d = frame.assign(f=freqs)
    g = (d.groupby(['text', 'chunk'])
           .agg(tokens=('f', 'size'), rare=('f', lambda x: int((x < RARE_BELOW).sum())),
                absent=('f', lambda x: int((x == 0).sum())), mean_zipf=('f', lambda x: sum(map(zipf, x)) / len(x)))
           .reset_index())
    g['rare_ratio'] = g.rare / g.tokens
    g.insert(0, 'step', step)
    return g[['step', 'text', 'chunk', 'tokens', 'rare', 'rare_ratio', 'absent', 'mean_zipf']]


steps = pd.concat([summarise(pub.stanza_freq, pub, '0 original measure'),
                   summarise(pub_b.stanza_freq, pub_b, '0b original method, Comp. 1 as translated'),
                   summarise(inc.freq_step1, inc, '1 notation removed'),
                   summarise(inc.freq_step2, inc, '2 unmatched lemmas repaired'),
                   summarise(inc.freq_final, inc, '3 final')], ignore_index=True)
steps = steps.sort_values(['step', 'text', 'chunk'], kind='mergesort').reset_index(drop=True)
write_csv(steps, 'rarity_by_passage_steps.csv')
final = steps[steps.step == '3 final']
by_passage = pd.DataFrame({'Text': final.text.map({'Comp': 'Comp.', 'Mix': 'Mix.'}), 'Passage': final.chunk,
                           'Words': final.tokens, 'Rare words': final.rare, 'Rare-term ratio': final.rare_ratio,
                           'Mean Zipf': final.mean_zipf})
by_passage = by_passage.sort_values(['Text', 'Passage'], ascending=[False, True], kind='mergesort')
write_csv(by_passage, 'rarity_by_passage_final.csv')

# ---------------------------------------------------------------- what each correction did
words = tok[tok.kind == 'word']
unmatched = words[words.freq_step1 == 0]
summary = [
    ('tokens counted in the original measure', len(pub)),
    ('Comp. 1: the preface replaced by the translated passage (tokens before -> after)', f'{n_preface} -> {n_translated}'),
    ('tokens counted by the original method on the translated passages', len(pub_b)),
    ('numerals removed (e.g. ι΄, ιβ΄)', int((tok.kind == 'numeral').sum())),
    ('symbols removed (no Greek letter: Latin numerals, stray ano teleia)', int((tok.kind == 'symbol').sum())),
    ('weight abbreviations expanded to their lemma', int((tok.kind == 'abbreviation').sum())),
    ('words split by Stanza at ῤῥ, re-joined (tokens before -> after)', f"{2 * int(tok.merged.sum())} -> {int(tok.merged.sum())}"),
    ('word tokens in the corrected measure', len(words)),
    ("words whose Stanza lemma matches nothing in Diorisis", len(unmatched)),
    ('  repaired by normalising accents/case of the Stanza lemma',
     int((unmatched.source == 'Stanza lemma, accents/case normalised').sum())),
    ('  repaired with the lemma Diorisis assigns to the form', int((unmatched.source == 'Diorisis lemma for this form').sum())),
    ('  word absent from Diorisis (kept, counted as rare)', int((unmatched.source == 'word absent from Diorisis').sum())),
    ('tokens where Stanza and Diorisis disagree about rare/common (hand decisions)', int(tok.disagreement.sum())),
    ('  distinct words decided by hand', len(used)),
    ('  decisions recorded for words only in the preface (not used)', len(DEC_UNUSED)),
    ('tokens in the final measure', len(inc)),
    ('  counted rare', int((inc.freq_final < RARE_BELOW).sum())),
    ('  of which absent from Diorisis', int((inc.freq_final == 0).sum())),
]
write_csv(pd.DataFrame(summary, columns=['correction', 'tokens']), 'rarity_correction_summary.csv')
S = dict(summary)
notation = S['numerals removed (e.g. ι΄, ιβ΄)'] + S['symbols removed (no Greek letter: Latin numerals, stray ano teleia)'] + \
    S['weight abbreviations expanded to their lemma']
STATS.add('tokens_original', len(pub), 'tokens counted in the original measure')
STATS.add('comp1_tokens_preface', n_preface, 'Comp. 1 tokens in the original measure (the preface, I.1)')
STATS.add('comp1_tokens_translated', n_translated, 'Comp. 1 tokens by the original method on the translated passage (I.2)')
STATS.add('decisions_unused', '; '.join(DEC_UNUSED), 'recorded hand decisions for words that occur only in the preface')
STATS.add('notation_tokens', notation, 'numerals, symbols and abbreviations counted as words in the original measure')
STATS.add('numerals', S['numerals removed (e.g. ι΄, ιβ΄)'], 'numerals removed')
STATS.add('symbols', S['symbols removed (no Greek letter: Latin numerals, stray ano teleia)'], 'symbols removed')
dropped = S['numerals removed (e.g. ι΄, ιβ΄)'] + S['symbols removed (no Greek letter: Latin numerals, stray ano teleia)']
STATS.add('notation_dropped', dropped, 'numerals and symbols dropped (the abbreviations are kept)')
STATS.add('abbreviations', S['weight abbreviations expanded to their lemma'], 'weight abbreviations expanded to their lemma and counted as words')
ab = tok[tok.kind == 'abbreviation']
pairs = ', '.join(f'{w}. = {lm}' for w, lm in sorted(set(zip(ab.word, ab.lemma))))   # δραχ. as printed
STATS.add('abbreviation_pairs', pairs, 'the weight abbreviations as printed, and the words they abbreviate')
STATS.add('abbreviation_forms', '; '.join(f'{w} = {lm}' for w, lm in sorted(set(zip(ab.word, ab.lemma)))), 'the weight abbreviations and the lemmas they are counted as')
STATS.add('split_words', int(tok.merged.sum()), 'words Stanza split at ῤῥ (re-joined)')
STATS.add('unmatched_tokens', len(unmatched), "word tokens whose Stanza lemma matches nothing in Diorisis")
share = len(unmatched) / len(words) * 100
STATS.add('unmatched_share', share, 'share of word tokens with an unmatched Stanza lemma (%)')
repaired = len(unmatched) - S['  word absent from Diorisis (kept, counted as rare)']
STATS.add('repaired_tokens', repaired, 'unmatched lemmas repaired (normalised or Diorisis form lemma)')
STATS.add('disagreement_tokens', int(tok.disagreement.sum()), 'tokens decided by hand')
STATS.add('disagreement_words', len(used), 'words decided by hand')
for t in ['Comp', 'Mix']:
    d = inc[inc.text == t]
    STATS.add(f'absent_{t}', int((d.freq_final == 0).sum()), f'{t}: final tokens absent from Diorisis (counted as rare)')
    STATS.add(f'tokens_{t}', len(d), f'{t}: tokens in the final measure')
STATS.add('absent_total', int((inc.freq_final == 0).sum()), 'final tokens absent from Diorisis, both texts')
STATS.save()
print(pd.DataFrame(summary, columns=['correction', 'tokens']).to_string(index=False))
print(final.round(3).to_string(index=False))
