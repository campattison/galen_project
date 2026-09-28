"""01 Two references for Mix., one for Comp.: how Mix. is scored, and what it does to the gap.

Mix. has two reference translations (Johnston; Singer and van der Eijk) and Comp. one (Marai).
The pipeline's multi-reference score of a Mix. translation uses both at once: BLEU-4 pools n-gram
matches over both references, and for the other metrics the score equals the higher of the two
single-reference scores (chrF++ and METEOR take the better reference themselves; for ROUGE-L,
BERTScore, COMET and BLEURT mt_eval/src/evaluator.py takes the maximum). This script scores Mix.
like for like with Comp. (against one reference at a time, and as the mean of those two scores)
and recomputes the gap, (mean Comp. - mean Mix.) / mean Mix. x 100, under each protocol, with
Comp. passages excluded as in the gap table (Mix. is kept whole in every column).

It also checks the multi-reference scores against the means and SDs exported with them, and lists
every Mix. score before and after the reference fix, marking those that changed (see
data/mixtures_pre_fix/README.md).

Inputs : mt_eval/output/evaluations/*.json, data/mt_eval_scores*.csv, data/mt_eval_aggregates.csv,
         data/mixtures_pre_fix/on_mixtures_evaluation.json
Outputs: like_for_like_gaps.csv, multi_reference_boost.csv, mix_per_reference_scores.csv,
         mix_reference_fix.csv, statistics_01_reference_asymmetry.csv
"""
import numpy as np
import pandas as pd

from common import (DATA, EXPORT_COLUMNS, KEYS, METRICS, Statistics, cohen_d, load_eval, load_eval_before_fix, metric_scores,
                    welch_p, write_csv)

STATS = Statistics(__file__)
ev = load_eval()

# The multi-reference scores reproduce the means and SDs exported with them (data/mt_eval_aggregates.csv).
# Tolerance 1e-6: the export rounds to six decimals.
multi = metric_scores('multi')
agg = pd.read_csv(DATA / 'mt_eval_aggregates.csv')
agg['text'] = agg.text.str.rstrip('.')
for _, r in agg.iterrows():
    g = multi[multi.text == r.text]
    g = g if r.model == 'Aggregate' else g[g.model == r.model]
    assert len(g) == r.n, (r.text, r.model)
    for c, m in EXPORT_COLUMNS.items():
        assert abs(g[m].mean() - r[f'{c}_mean']) < 1e-6, ('mean', r.text, r.model, m)
        assert abs(g[m].std(ddof=1) - r[f'{c}_sd']) < 1e-6, ('sd', r.text, r.model, m)

mix, comp = ev[ev.text == 'Mix'].reset_index(drop=True), ev[ev.text == 'Comp'].reset_index(drop=True)
EXCL = {'all': [], 'excl 8,10': [8, 10], 'excl 3,8,10': [3, 8, 10]}
VARIANTS = {'both references (multi-reference)': lambda m: mix[m],
            'Johnston only': lambda m: mix[f'{m}|ref1'],
            'Singer & van der Eijk only': lambda m: mix[f'{m}|ref2'],
            'mean of the two single-reference scores': lambda m: (mix[f'{m}|ref1'] + mix[f'{m}|ref2']) / 2}

# ---------------------------------------------------------------- how much two references raise a score
rows = []
for m in METRICS:
    best_single = np.maximum(mix[f'{m}|ref1'], mix[f'{m}|ref2'])
    diff = (mix[m] - best_single) * 100
    rows.append({'metric': m, 'items': len(mix), 'multi-reference > best single reference': int((diff > 1e-9).sum()),
                 'multi-reference = best single reference': int((diff.abs() <= 1e-9).sum()),
                 'mean excess (points)': diff.mean()})
boost = pd.DataFrame(rows)
write_csv(boost, 'multi_reference_boost.csv')
b = boost.set_index('metric').loc['BLEU-4']
STATS.add('bleu_boost_items', int(b['multi-reference > best single reference']),
      'Mix. translations whose multi-reference BLEU-4 exceeds the better single-reference BLEU-4 (of 30)')
STATS.add('bleu_boost_points', b['mean excess (points)'],
      'mean excess of multi-reference BLEU-4 x 100 over the better single-reference BLEU-4 x 100, Mix.')

# ---------------------------------------------------------------- the gap under each protocol
rows = []
for m in METRICS:
    for vname, fn in VARIANTS.items():
        mv = fn(m)
        r = {'metric': m, 'Mix. scored against': vname, 'Mix. mean x100': mv.mean() * 100,
             'Comp. mean x100': comp[m].mean() * 100}
        for sname, excl in EXCL.items():
            c = comp[~comp.chunk.isin(excl)][m]
            r[f'gap % ({sname})'] = (c.mean() - mv.mean()) / mv.mean() * 100
            r[f'Welch p ({sname})'] = welch_p(c, mv)
        r['Cohen d (all)'] = cohen_d(comp[m], mv)
        rows.append(r)
lfl = pd.DataFrame(rows)
write_csv(lfl, 'like_for_like_gaps.csv')

L = lfl.set_index(['metric', 'Mix. scored against'])
short = {'both references (multi-reference)': 'pooled', 'Johnston only': 'johnston',
         'Singer & van der Eijk only': 'singer', 'mean of the two single-reference scores': 'mean'}
for vname, k in short.items():
    row = L.loc[('BLEU-4', vname)]
    STATS.add(f'bleu_mix_{k}', row['Mix. mean x100'], f'Mix. mean BLEU-4 x 100, {vname}')
    for sname in EXCL:
        tag = sname.replace('excl ', 'x').replace(',', '')
        STATS.add(f'bleu_gap_{k}_{tag}', row[f'gap % ({sname})'],
              f'gap in BLEU-4, (mean Comp. - mean Mix.) / mean Mix. x 100, Mix. {vname}, Comp. {sname}')
        STATS.add(f'bleu_p_{k}_{tag}', row[f'Welch p ({sname})'], 'Welch p for that gap')
STATS.add('bleu_comp', L.loc[('BLEU-4', 'Johnston only')]['Comp. mean x100'], 'Comp. mean BLEU-4 x 100 (one reference)')
for m in METRICS[1:]:
    multi_gap = L.loc[(m, 'both references (multi-reference)')]['gap % (all)']
    mean_gap = L.loc[(m, 'mean of the two single-reference scores')]['gap % (all)']
    STATS.add(f'gap_all_{m}_multiref', multi_gap, f'{m}: gap (%), Mix. scored multi-reference, all passages')
    STATS.add(f'gap_all_{m}_mean', mean_gap, f'{m}: gap (%), Mix. scored as the mean of its two single-reference scores, all passages')
single = pd.concat([mix['BLEU-4|ref1'], mix['BLEU-4|ref2']]) * 100
STATS.add('bleu_single_ref_range', f'{single.min():.6f}/{single.max():.6f}',
      'lowest / highest BLEU-4 x 100 of a Mix. translation against a single reference')

# ---------------------------------------------------------------- scores against each reference
for m in METRICS:
    mix[f'{m}|mean'] = (mix[f'{m}|ref1'] + mix[f'{m}|ref2']) / 2
per = mix[KEYS + [c for m in METRICS for c in (m, f'{m}|ref1', f'{m}|ref2', f'{m}|mean')]].copy()
per = per.rename(columns=lambda c: c.replace('|ref1', ' (Johnston)').replace('|ref2', ' (Singer & vdE)')
                 .replace('|mean', ' (mean of single refs)') if '|' in c else
                 (c + ' (multi-reference)' if c in METRICS else c))
write_csv(per, 'mix_per_reference_scores.csv')

# ---------------------------------------------------------------- the reference fix, score by score
before = load_eval_before_fix().set_index(KEYS)
after = ev.set_index(KEYS)
cols = [c for c in after.columns if c in METRICS or '|' in c]
rows = []
for key in after.index:
    for c in cols:
        a, b = before.loc[key, c], after.loc[key, c]
        if pd.isna(a) and pd.isna(b):
            continue
        rows.append({'text': key[0], 'chunk': key[1], 'model': key[2],
                     'score': c.replace('|ref1', ' vs Johnston').replace('|ref2', ' vs Singer & vdE'),
                     'before fix': a, 'after fix': b, 'changed': abs(a - b) > 1e-6})
fix = pd.DataFrame(rows)
assert set(zip(fix[fix.changed].text, fix[fix.changed].chunk)) == {('Mix', 2), ('Mix', 4)}
write_csv(fix[fix.text == 'Mix'].reset_index(drop=True), 'mix_reference_fix.csv')
STATS.add('fix_scores_changed', int(fix.changed.sum()), 'Mix. scores (all metrics, each reference and multi-reference) changed by the reference fix')

STATS.save()
print(lfl[lfl.metric == 'BLEU-4'].round(2).to_string(index=False))
print(boost.round(2).to_string(index=False))
