"""33 Table SM3: the input length limit of each automated metric and how much of each passage it reads.

Three of the seven automated metrics cap their input. The table states each metric's cap, how it
encodes its input, how many scored pairs it truncates and how much of the texts it actually reads.
COMET-Kiwi, a reference-free metric, joins candidate and source with the candidate first, so
truncation removes the end of the source.

Inputs: the token counts of every text under each metric's own tokenizer and, for each scored pair,
what each metric keeps (data/token_counts_passages.csv, data/token_counts_pairs.csv; see
data/token_counts_README.md), and the COMET-Kiwi score of each translation (data/comet_kiwi_scores.csv).
Before they are used they are checked: the word counts against the texts in this repository, each
metric's truncation rule re-applied to the raw token counts (the COMET and BERTScore caps, BLEURT's
pair truncation simulated token by token, COMET-Kiwi's joint window), the two files against each
other, and the COMET-Kiwi file's COMET and TQS columns against this package's.

Limits are given in content tokens: COMET caps each segment at 510 tokens including its two special
tokens (508 of content), BERTScore each side at 512 including them (510 of content); the joint
windows of BLEURT-20 and COMET-Kiwi are given whole (512).

Inputs : the three files above, mt_eval/input/*.txt, mt_eval/output/translations/*.json, mqm/ (TQS),
         mt_eval/output/evaluations/*.json (COMET), the values file of the gap table (from 23_table_metric_gap.py)
Outputs: table_SM3.csv (as printed), statistics_33_table_input_limits.csv
"""
import unicodedata

import numpy as np
import pandas as pd
from scipy import stats

from common import (DATA, LABEL, OUT, Statistics, load_mqm, load_texts, load_translations, metric_scores,
                    pearson)
from tables import filename, write_table

STATS = Statistics(__file__)
P = pd.read_csv(DATA / 'token_counts_passages.csv')
Q = pd.read_csv(DATA / 'token_counts_pairs.csv')
K = pd.read_csv(DATA / 'comet_kiwi_scores.csv')
COMET_SEG, BERT_SIDE, JOINT, BLEURT_BUDGET = 508, 510, 512, 509
COMET_MAX = 510          # COMET's per-segment max_length as the library states it (special tokens included)

# ---------------------------------------------------------------- 1. check the files
assert len(P) == 110 and P.role.value_counts().to_dict() == {'hyp': 60, 'ref': 30, 'src': 20}
assert len(Q) == 90 and len(K) == 60
texts, tr = load_texts(), load_translations()
REFS = {'Mix': ['Johnston', 'Singer'], 'Comp': ['Marai']}


def text_of(r):
    if r.role == 'src':
        return texts[r.text][r.chunk]['greek']
    if r.role == 'ref':
        return texts[r.text][r.chunk]['refs'][REFS[r.text].index(r.label)]
    return tr[(r.text, r.chunk, r.label)]['translation']


for r in P.itertuples():                  # word counts: NFC, split at whitespace
    assert len(unicodedata.normalize('NFC', text_of(r)).split()) == r.words, (r.text, r.chunk, r.role, r.label)
assert ((P.xlmr_tokens_with_specials - P.xlmr_tokens) == 2).all()


def count(text, chunk, role, lab, col):
    x = P[(P.text == text) & (P.chunk == chunk) & (P.role == role) & (P.label == lab)][col]
    assert len(x) == 1, (text, chunk, role, lab)
    return int(x.iloc[0])


for r in Q.itertuples():                  # the pairs file repeats the passage counts
    for col, role, lab, pcol in [('xlmr_src', 'src', 'Greek', 'xlmr_tokens'), ('xlmr_hyp', 'hyp', r.model, 'xlmr_tokens'),
                                 ('xlmr_ref', 'ref', r.ref_label, 'xlmr_tokens'), ('roberta_hyp', 'hyp', r.model, 'roberta_tokens'),
                                 ('roberta_ref', 'ref', r.ref_label, 'roberta_tokens'), ('bleurt_hyp', 'hyp', r.model, 'bleurt_sp_tokens'),
                                 ('bleurt_ref', 'ref', r.ref_label, 'bleurt_sp_tokens')]:
        assert getattr(r, col) == count(r.text, r.chunk, role, lab, pcol), (r.text, r.chunk, r.model, col)
for side in ('src', 'hyp', 'ref'):        # COMET: each segment capped separately
    kept = Q[f'xlmr_{side}'].clip(upper=COMET_SEG)
    assert (kept == Q[f'comet_{side}_kept_tokens']).all()
    assert np.allclose(kept / Q[f'xlmr_{side}'], Q[f'comet_{side}_kept_frac'], atol=1e-12, rtol=0)
for side in ('hyp', 'ref'):               # BERTScore: each side capped separately
    kept = Q[f'roberta_{side}'].clip(upper=BERT_SIDE)
    assert (kept == Q[f'bertscore_{side}_kept']).all()
    assert np.allclose(kept / Q[f'roberta_{side}'], Q[f'bertscore_{side}_kept_frac'], atol=1e-12, rtol=0)
for r in Q.itertuples():
    a, b = r.bleurt_ref, r.bleurt_hyp     # BLEURT: [CLS] ref [SEP] cand [SEP]; pop the longer, the candidate on ties
    while a + b > BLEURT_BUDGET:
        if a > b:
            a -= 1
        else:
            b -= 1
    assert (a, b) == (r.bleurt_ref_kept, r.bleurt_hyp_kept) and r.bleurt_pair_total == r.bleurt_ref + r.bleurt_hyp
    hyp_eff, src_eff = min(r.xlmr_hyp + 2, COMET_MAX), min(r.xlmr_src + 2, COMET_MAX)   # COMET-Kiwi: <s> mt </s></s> src </s>
    cut = hyp_eff + src_eff > JOINT
    kept = r.xlmr_src if not cut else max(0, min(r.xlmr_src, JOINT - (hyp_eff + 1)))
    assert cut == r.kiwi_joint_truncated and kept == r.kiwi_src_kept_tokens
    assert abs(kept / r.xlmr_src - r.kiwi_src_kept_frac) < 1e-12 and (r.xlmr_hyp + 2 > COMET_MAX) == r.kiwi_hyp_truncated

kiwi = Q.drop_duplicates(['text', 'chunk', 'model']).merge(K, on=['text', 'chunk', 'model'], validate='1:1')
assert len(kiwi) == 60
assert ((kiwi.tokens_src == kiwi.xlmr_src + 2) & (kiwi.tokens_mt == kiwi.xlmr_hyp + 2)).all()
assert ((kiwi.src_tokens_kept == kiwi.kiwi_src_kept_tokens) & (kiwi.mt_truncated == kiwi.kiwi_hyp_truncated)).all()
assert (kiwi.over_token_limit == kiwi.kiwi_joint_truncated).all()
assert np.allclose(kiwi.src_fraction_kept, kiwi.kiwi_src_kept_frac, atol=1e-6, rtol=0)
mq = load_mqm()
comet = metric_scores('mean')[['text', 'chunk', 'model', 'COMET']]
kiwi = kiwi.merge(mq[['text', 'chunk', 'model', 'TQS']], on=['text', 'chunk', 'model'], suffixes=('_file', ''))
kiwi = kiwi.merge(comet, on=['text', 'chunk', 'model'])
assert (kiwi.TQS_file == kiwi.TQS).all(), 'the COMET-Kiwi file has other TQS values'
# the file rounds to six decimals: up to half a unit in the last place, plus floating-point noise
assert np.allclose(kiwi['COMET (reference-based)'], kiwi.COMET, atol=1e-6, rtol=0), 'its COMET is not the protocol of 20'

# ---------------------------------------------------------------- 2. the table
src = Q.drop_duplicates(['text', 'chunk'])            # one row per passage for the Greek source
pct = lambda v: f'{v * 100:.0f}%'                     # noqa: E731
n_pairs = {t: int((Q.text == t).sum()) for t in ('Mix', 'Comp')}
n_trans = {t: int((kiwi.text == t).sum()) for t in ('Mix', 'Comp')}


def cut_count(frame, cond):
    return {t: int(cond(frame[frame.text == t]).sum()) for t in ('Mix', 'Comp')}


def span(a, b):
    a, b = pct(a), pct(b)
    return a if a == b else f'{a[:-1]}–{b}'


bert_cut = cut_count(Q, lambda d: (d.bertscore_hyp_kept_frac < 1) | (d.bertscore_ref_kept_frac < 1))
bert_q = Q[(Q.bertscore_hyp_kept_frac < 1) | (Q.bertscore_ref_kept_frac < 1)]
assert set(zip(bert_q.text, bert_q.chunk)) == {('Comp', 8), ('Comp', 10)}
bref = bert_q.drop_duplicates('chunk').set_index('chunk').bertscore_ref_kept_frac
bhyp = bert_q.bertscore_hyp_kept_frac.min()
bhyp_who = bert_q.loc[bert_q.bertscore_hyp_kept_frac.idxmin()]
comet_src_cut = cut_count(Q, lambda d: d.comet_src_kept_frac < 1)
comet_eng_cut = cut_count(Q, lambda d: (d.comet_hyp_kept_frac < 1) | (d.comet_ref_kept_frac < 1))
eng = Q[(Q.comet_hyp_kept_frac < 1) | (Q.comet_ref_kept_frac < 1)]
assert set(zip(eng.text, eng.chunk)) == {('Comp', 8), ('Comp', 10)}
hyp_cut = eng[eng.comet_hyp_kept_frac < 1].drop_duplicates(['chunk', 'model'])
cat_pairs = Q[(Q.text == 'Comp') & Q.chunk.isin([8, 10])]
assert len(cat_pairs) == 6 and (cat_pairs.comet_ref_kept_frac < 1).all(), 'COMET does not cut the reference in every Comp. 8 and 10 pair'
ref_cut = cat_pairs.drop_duplicates('chunk').comet_ref_kept_frac    # the one reference of Comp. 8 and of Comp. 10
cs = {t: src[src.text == t].comet_src_kept_frac for t in ('Mix', 'Comp')}
bl_cut = cut_count(Q, lambda d: (d.bleurt_hyp_kept_frac < 1) | (d.bleurt_ref_kept_frac < 1))
bl = {t: (Q[Q.text == t].bleurt_ref_kept_frac.mean(), Q[Q.text == t].bleurt_hyp_kept_frac.mean()) for t in ('Mix', 'Comp')}
worst = Q.assign(w=Q[['bleurt_hyp_kept_frac', 'bleurt_ref_kept_frac']].min(axis=1)).sort_values('w').iloc[0]
kc = {t: kiwi[kiwi.text == t] for t in ('Mix', 'Comp')}
kiwi_cut = cut_count(kiwi, lambda d: d.kiwi_joint_truncated)
one_tok = kiwi[kiwi.kiwi_src_kept_tokens == 1]
assert set(one_tok.text) == {'Comp'}
mix_lo, mix_hi = sorted(bl['Mix'])
comp_lo, comp_hi = sorted(bl['Comp'])
rows = [
    {'Metric': 'BLEU-4, chrF++, METEOR, ROUGE-L', 'Input limit': 'none', 'How the input is encoded': 'no length limit',
     'Mix. pairs truncated': f"0 of {n_pairs['Mix']}", 'Comp. pairs truncated': f"0 of {n_pairs['Comp']}",
     'What the metric reads': 'all of every passage'},
    {'Metric': 'BERTScore', 'Input limit': f'{BERT_SIDE} per side', 'How the input is encoded': 'candidate and reference embedded separately',
     'Mix. pairs truncated': f"{bert_cut['Mix']} of {n_pairs['Mix']}", 'Comp. pairs truncated': f"{bert_cut['Comp']} of {n_pairs['Comp']}",
     'What the metric reads': f'Comp. 8 and 10 only: reference {pct(bref[8])} (8), {pct(bref[10])} (10); longest hypothesis {pct(bhyp)}'},
    {'Metric': 'COMET (wmt22-comet-da)', 'Input limit': f'{COMET_SEG} per segment',
     'How the input is encoded': 'source, candidate and reference embedded separately',
     'Mix. pairs truncated': f"{comet_src_cut['Mix']} of {n_pairs['Mix']} (Greek source)",
     'Comp. pairs truncated': f"{comet_src_cut['Comp']} of {n_pairs['Comp']} (Greek source); {comet_eng_cut['Comp']} of {n_pairs['Comp']} (English)",
     'What the metric reads': (f"Greek: {pct(cs['Mix'].mean())} mean, {pct(cs['Mix'].min())} min (Mix.); {pct(cs['Comp'].mean())} mean, "
                               f"{pct(cs['Comp'].min())} min (Comp.); Comp. 8 and 10: reference ({span(ref_cut.min(), ref_cut.max())}) "
                               f"and {len(hyp_cut)} of 6 candidates ({span(hyp_cut.comet_hyp_kept_frac.min(), hyp_cut.comet_hyp_kept_frac.max())}) also cut")},
    {'Metric': 'BLEURT-20', 'Input limit': f'{JOINT} joint',
     'How the input is encoded': 'reference and candidate concatenated; the longer side truncated until the pair fits',
     'Mix. pairs truncated': f"{bl_cut['Mix']} of {n_pairs['Mix']}", 'Comp. pairs truncated': f"{bl_cut['Comp']} of {n_pairs['Comp']}",
     'What the metric reads': (f"both sides: {span(mix_lo, mix_hi)} (Mix.), {span(comp_lo, comp_hi)} (Comp.), "
                               f"{pct(worst.w)} at worst ({LABEL[worst.text]} {worst.chunk}, {worst.model})")},
    {'Metric': 'COMET-Kiwi (wmt22-cometkiwi-da)', 'Input limit': f'{JOINT} joint',
     'How the input is encoded': 'candidate and source concatenated, candidate first; the Greek tail discarded',
     'Mix. pairs truncated': f"{kiwi_cut['Mix']} of {n_trans['Mix']}", 'Comp. pairs truncated': f"{kiwi_cut['Comp']} of {n_trans['Comp']}",
     'What the metric reads': (f"Greek: {pct(kc['Mix'].kiwi_src_kept_frac.mean())} (Mix.), {pct(kc['Comp'].kiwi_src_kept_frac.mean())} "
                               f"(Comp.); one token in {len(one_tok)} Comp. pairs")},
]
table = pd.DataFrame(rows)
write_table('metric_input_limits', table)

# ---------------------------------------------------------------- 3. the figures in the table's cells, before rounding
STATS.add('cap_bertscore', BERT_SIDE, 'BERTScore: tokens of content kept on each side (512 with its two special tokens)')
STATS.add('cap_comet', COMET_SEG, 'COMET: tokens of content kept in each segment (510 with its two special tokens)')
STATS.add('cap_joint', JOINT, 'BLEURT-20 and COMET-Kiwi: the joint window, special tokens included')
for t in ('Mix', 'Comp'):
    STATS.add(f'comet_greek_mean_{t}', cs[t].mean(), f'{LABEL[t]}: share of the Greek source COMET reads, mean over passages')
    STATS.add(f'comet_greek_min_{t}', cs[t].min(), f'{LABEL[t]}: the same, lowest passage')
    lo, hi = sorted(bl[t])
    STATS.add(f'bleurt_share_{t}', f'{lo:.6f}/{hi:.6f}', f'{LABEL[t]}: share of each side BLEURT reads (lower / higher of the '
              'reference mean and the candidate mean)')
x3810 = src[(src.text == 'Comp') & ~src.chunk.isin([3, 8, 10])].comet_src_kept_frac
STATS.add('comet_greek_mean_Comp_x3810', x3810.mean(), 'Comp. without passages 3, 8 and 10: share of the Greek source COMET reads, mean')
STATS.add('bleurt_worst', worst.w, f'smallest share of a side BLEURT reads ({LABEL[worst.text]} {worst.chunk}, {worst.model})')
STATS.add('bleurt_pairs_cut', sum(bl_cut.values()), f'pairs BLEURT truncates (of {len(Q)})')
for c in (8, 10):
    STATS.add(f'bert_ref_kept_{c}', bref[c], f'Comp. {c}: share of the reference BERTScore reads')
    r = eng[(eng.chunk == c)].iloc[0]
    STATS.add(f'comet_ref_kept_{c}', r.comet_ref_kept_frac,
              f'Comp. {c}: share of the reference COMET reads ({r.xlmr_ref} XLM-R tokens, {COMET_SEG} kept)')
STATS.add('bert_hyp_kept_min', bhyp, f'smallest share of a candidate BERTScore reads (the longest candidate: '
          f'{LABEL[bhyp_who.text]} {bhyp_who.chunk}, {bhyp_who.model})')
STATS.add('comet_hyp_cut', len(hyp_cut), 'Comp. 8 and 10 candidates COMET truncates (of 6)')
STATS.add('comet_hyp_kept_range', f"{hyp_cut.comet_hyp_kept_frac.min():.6f}/{hyp_cut.comet_hyp_kept_frac.max():.6f}",
          'lowest / highest share of those candidates COMET reads')

# ---------------------------------------------------------------- 4. the gap table on untruncated input
# The cells of the gap table (23) computed on input no metric truncated: the four metrics
# without a limit in every column, and BERTScore in the two columns that exclude Comp. 8 and 10.
UNCAPPED = {'BLEU-4', 'chrF++', 'METEOR', 'ROUGE-L'}
assert bert_cut['Mix'] == 0 and set(bert_q.chunk) == {8, 10}     # BERTScore reads all of every other passage
gv = pd.read_csv(OUT / filename('metric_gap_stratified', '_values'))
gp = gv[gv.statistic == 'Welch p']
clean = gp[gp.row.isin(UNCAPPED) | ((gp.row == 'BERTScore') & gp.column.str.startswith('Excl'))]
STATS.add('gap_cells_untruncated', len(clean), f'cells of the gap table (of {len(gp)}) computed on input no metric truncated')
STATS.add('gap_cells_untruncated_significant', int((clean.value < .05).sum()), 'of those, the gaps significant at .05 (Welch)')

# ---------------------------------------------------------------- 5. COMET-Kiwi
joint = kiwi.xlmr_hyp + kiwi.xlmr_src + 4                     # <s> mt </s></s> src </s>
STATS.add('kiwi_joint_range', f'{joint.min()}/{joint.max()}',
          f'lowest / highest joint candidate + source length in XLM-R tokens, against a {JOINT}-token window')
STATS.add('kiwi_pairs_cut', int(kiwi.kiwi_joint_truncated.sum()), 'translation-source pairs over the window (of 60)')
for t in ('Mix', 'Comp'):
    STATS.add(f'kiwi_keep_{t.lower()}', kc[t].kiwi_src_kept_frac.mean(), f'share of the Greek source COMET-Kiwi reads, {LABEL[t]} mean')
STATS.add('kiwi_one_token', len(one_tok),
          f"pairs in which a single Greek token survives ({', '.join(f'Comp. {r.chunk} {r.model}' for r in one_tok.itertuples())})")
mean = {t: kc[t].cometkiwi.mean() for t in ('Mix', 'Comp')}
kiwi_gap = (mean['Comp'] - mean['Mix']) / mean['Mix'] * 100
cm = {t: kc[t].COMET.mean() for t in ('Mix', 'Comp')}
comet_gap = (cm['Comp'] - cm['Mix']) / cm['Mix'] * 100
STATS.add('kiwi_gap', kiwi_gap, 'gap on COMET-Kiwi, (mean Comp. - mean Mix.) / mean Mix. x 100, all passages')
STATS.add('kiwi_comet_gap', comet_gap, 'the same gap on reference-based COMET, the same translations')
r_share = pearson(kiwi.cometkiwi, kiwi.kiwi_src_kept_frac)[0]
r_tqs = pearson(kiwi.cometkiwi, kiwi.TQS)[0]
r_st = pearson(kiwi.kiwi_src_kept_frac, kiwi.TQS)[0]
partial = (r_tqs - r_share * r_st) / np.sqrt((1 - r_share ** 2) * (1 - r_st ** 2))
t_stat = partial * np.sqrt((len(kiwi) - 3) / (1 - partial ** 2))
p_partial = 2 * stats.t.sf(abs(t_stat), len(kiwi) - 3)
STATS.add('kiwi_r_share', r_share, 'COMET-Kiwi vs the share of the Greek it read, Pearson r (60 translations)')
STATS.add('kiwi_r_tqs', r_tqs, 'COMET-Kiwi vs TQS, Pearson r (60 translations)')
STATS.add('kiwi_partial_r', partial, 'COMET-Kiwi vs TQS with the share read held constant, partial r (60 translations)')
STATS.add('kiwi_partial_p', p_partial, 'p for that partial r (df = 57)')

STATS.save()
print(table.to_string(index=False))
