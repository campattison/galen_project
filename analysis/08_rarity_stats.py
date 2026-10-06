"""08 Rarity and translation quality.

For each step of the rarity measure (07), correlates passage rarity with passage quality (mean
TQS over the three models; total critical errors). For every step it computes Pearson and
Spearman correlations, R^2 with a bootstrap CI (seed 0, 10,000 resamples), Cook's distance, the
correlation without Comp. 8 and 10, and group means. For the final measure it also finds the
rarity below which (almost) no model fails and correlates rarity with each type of error (over
all ten Comp. passages and without 8 and 10). Steps 0 and 0b are the original measure and the
original method with Comp. 1 the translated passage (see 07).

Inputs : outputs/rarity_by_passage_steps.csv (from 07), mqm/ summary sheets
Outputs: rarity_stats_by_step.csv, rarity_correlations_by_step.csv, rarity_quality_by_passage.csv,
         rarity_vs_error_type.csv, statistics_08_rarity_stats.csv
"""
import pandas as pd

from common import (CATASTROPHIC, FAIL_BELOW, OUT, Statistics, bootstrap_r2, cooks_distance, f_r, load_mqm,
                    passage_quality, pearson, spearman, stars, write_csv)

STATS = Statistics(__file__)
steps = pd.read_csv(OUT / 'rarity_by_passage_steps.csv')
mq = load_mqm()
q = passage_quality(mq)
err = mq.groupby(['text', 'chunk']).agg(term=('term', 'sum'), acc=('acc', 'sum')).reset_index()


rows, by_step = [], []
for step, s in steps.groupby('step', sort=True):
    d = s.merge(q, on=['text', 'chunk'])
    c = d[d.text == 'Comp'].sort_values('chunk').reset_index(drop=True)
    cx = c[~c.chunk.isin(CATASTROPHIC)]
    m = d[d.text == 'Mix']
    r, p = pearson(c.rare_ratio, c.TQS)
    rho, prho = spearman(c.rare_ratio, c.TQS)
    rx, px = pearson(cx.rare_ratio, cx.TQS)
    rhox, prhox = spearman(cx.rare_ratio, cx.TQS)
    lo, hi, kept = bootstrap_r2(c.rare_ratio, c.TQS, seed=0)
    D = cooks_distance(c.rare_ratio, c.TQS)
    cat = c[c.chunk.isin(CATASTROPHIC)]
    rows.append({'step': step, 'r Comp': r, 'p': p, 'R2': r * r, 'R2 CI low': lo, 'R2 CI high': hi,
                 'bootstrap resamples kept': kept, 'rho Comp': rho, 'p rho': prho,
                 'Cook D 8': float(D[c.chunk == 8][0]), 'Cook D 10': float(D[c.chunk == 10][0]),
                 'Cook D threshold 4/n': 4 / len(c),
                 'r without 8,10': rx, 'p without': px, 'R2 without': rx * rx, 'rho without 8,10': rhox,
                 'p rho without': prhox, 'r all 20': pearson(d.rare_ratio, d.TQS)[0],
                 'mean ratio Comp': c.rare_ratio.mean(), 'mean ratio Mix': m.rare_ratio.mean(),
                 'ratio 8': float(c.loc[c.chunk == 8, 'rare_ratio'].iloc[0]),
                 'ratio 10': float(c.loc[c.chunk == 10, 'rare_ratio'].iloc[0]),
                 'mean ratio 8,10': cat.rare_ratio.mean(), 'mean ratio other Comp': cx.rare_ratio.mean(),
                 'max ratio other Comp': cx.rare_ratio.max(), 'max ratio Mix': m.rare_ratio.max(),
                 'Comp over Mix multiple': c.rare_ratio.mean() / m.rare_ratio.mean(),
                 'Comp passages above every Mix passage': int((c.rare_ratio > m.rare_ratio.max()).sum()),
                 'mean TQS 8,10': cat.TQS.mean(), 'mean TQS other Comp': cx.TQS.mean()})
    predictors = [('Rare-term ratio', 'rare_ratio'), ('Mean Zipf frequency', 'mean_zipf')]
    for label, col in predictors:
        row = {'step': step, 'predictor': label}
        for tgt, frame, y in [('TQS (Comp.)', c, 'TQS'), ('TQS (All)', d, 'TQS'),
                              ('Critical (Comp.)', c, 'critical'), ('Critical (All)', d, 'critical')]:
            rr, pp = pearson(frame[col], frame[y])
            row[f'{tgt} r'], row[f'{tgt} p'] = rr, pp
            row[f'{tgt} shown'] = f_r(rr) + stars(pp)
        by_step.append(row)
st = pd.DataFrame(rows)
write_csv(st, 'rarity_stats_by_step.csv')
by_step = pd.DataFrame(by_step)
write_csv(by_step, 'rarity_correlations_by_step.csv')

# ---------------------------------------------------------------- the statistics of steps 0, 0b and 3
STEP = {'step0': '0 original measure', 'step0b': '0b original method, Comp. 1 as translated', 'final': '3 final'}
LAB = {'step0': 'original measure', 'step0b': 'original method, Comp. 1 as translated', 'final': 'final measure'}
S0, S0B, FIN = (st.set_index('step').loc[STEP[k]] for k in ['step0', 'step0b', 'final'])
for tag, row in [('step0', S0), ('step0b', S0B), ('final', FIN)]:
    lab = LAB[tag]
    STATS.add(f'{tag}_r', row['r Comp'], f'rarity vs TQS, Comp., Pearson r ({lab})')
    STATS.add(f'{tag}_p', row['p'], f'p for that r ({lab})')
    STATS.add(f'{tag}_R2', row['R2'], f'R^2 ({lab})')
    STATS.add(f'{tag}_R2_pct', row['R2'] * 100, f'variance explained, R^2 x 100 ({lab})')
    STATS.add(f'{tag}_R2_ci', f"{row['R2 CI low']:.6f}-{row['R2 CI high']:.6f}", f'bootstrap 95% CI for R^2 ({lab})')
    STATS.add(f'{tag}_rho', row['rho Comp'], f'Spearman rho ({lab})')
    STATS.add(f'{tag}_prho', row['p rho'], f'p for rho ({lab})')
    STATS.add(f'{tag}_D8', row['Cook D 8'], f"Cook's D, passage 8 ({lab})")
    STATS.add(f'{tag}_D10', row['Cook D 10'], f"Cook's D, passage 10 ({lab})")
    STATS.add(f'{tag}_rx', row['r without 8,10'], f'r without 8 and 10 ({lab})')
    STATS.add(f'{tag}_px', row['p without'], f'p without 8 and 10 ({lab})')
    STATS.add(f'{tag}_R2x', row['R2 without'], f'R^2 without 8 and 10 ({lab})')
    STATS.add(f'{tag}_rhox', row['rho without 8,10'], f'rho without 8 and 10 ({lab})')
    STATS.add(f'{tag}_prhox', row['p rho without'], f'p for rho without 8 and 10 ({lab})')
    STATS.add(f'{tag}_mean_comp', row['mean ratio Comp'], f'mean rare-term ratio, Comp. ({lab})')
    STATS.add(f'{tag}_mean_mix', row['mean ratio Mix'], f'mean rare-term ratio, Mix. ({lab})')
    for k, name in [('ratio 8', '8'), ('ratio 10', '10'), ('mean ratio 8,10', '8+10 mean'),
                    ('mean ratio other Comp', 'other Comp. mean'), ('max ratio other Comp', 'other Comp. max'),
                    ('max ratio Mix', 'Mix. max')]:
        STATS.add(f"{tag}_{k.replace(' ', '_').replace(',', '')}", row[k], f'rare-term ratio, {name} ({lab})')
    mult = row['mean ratio 8,10'] / row['mean ratio other Comp']
    STATS.add(f'{tag}_multiple', mult, f'8+10 mean as a multiple of the other Comp. mean ({lab})')
    STATS.add(f'{tag}_comp_over_mix', row['Comp over Mix multiple'], f'Comp. mean rare-term ratio as a multiple of the Mix. mean ({lab})')
    STATS.add(f'{tag}_sep', row['Comp passages above every Mix passage'], f'Comp. passages rarer than every Mix. passage ({lab})')
STATS.add('cook_threshold', FIN['Cook D threshold 4/n'], "Cook's distance threshold 4/n (n = 10)")
STATS.add('tqs_mean_cat', FIN['mean TQS 8,10'], 'mean TQS, Comp. 8 and 10')
STATS.add('tqs_mean_other', FIN['mean TQS other Comp'], 'mean TQS, other Comp. passages')
for tag in ['step0', 'final']:
    for _, r in by_step[by_step.step == STEP[tag]].iterrows():
        pk = {'Rare-term ratio': 'rare', 'Mean Zipf frequency': 'zipf'}[r.predictor]
        for tgt, tk in [('TQS (Comp.)', 'tqs_comp'), ('TQS (All)', 'tqs_all'), ('Critical (Comp.)', 'crit_comp'),
                        ('Critical (All)', 'crit_all')]:
            STATS.add(f'rarity_corr_{tag}_{pk}_{tk}', r[f'{tgt} r'], f'{r.predictor} vs {tgt}, Pearson r ({LAB[tag]})')

# ---------------------------------------------------------------- where failures begin (final measure)
fin = steps[steps.step == '3 final'].merge(q, on=['text', 'chunk'])
by_models = (mq.assign(s1=mq.TQS < FAIL_BELOW, s2=(mq.TQS < FAIL_BELOW) | (mq.critical > 0))
               .groupby(['text', 'chunk'])
               .apply(lambda g: pd.Series({'Scheme 1 FAIL': ', '.join(g[g.s1].model) or '-',
                                           'Scheme 2 FAIL': ', '.join(f'{m} ({t:.1f})' for m, t in zip(g[g.s2].model, g[g.s2].TQS)) or '-'}),
                      include_groups=False)
               .reset_index())
fin = fin.merge(by_models, on=['text', 'chunk'])
fin = fin.sort_values(['text', 'rare_ratio', 'chunk'], kind='mergesort').reset_index(drop=True)
write_csv(fin[['text', 'chunk', 'tokens', 'rare', 'rare_ratio', 'mean_zipf', 'TQS', 'critical', 's1_fails', 's2_fails',
               'Scheme 1 FAIL', 'Scheme 2 FAIL']], 'rarity_quality_by_passage.csv')
c = fin[fin.text == 'Comp'].reset_index(drop=True)
# Walk up the Comp. passages in order of rarity for as long as no model fails under Scheme 1 and at
# most one translation in all fails under Scheme 2.
k, s2 = 0, 0
while k < len(c) and c.s1_fails[k] == 0 and s2 + c.s2_fails[k] <= 1:
    s2 += c.s2_fails[k]
    k += 1
held, nxt = c.iloc[:k], c.iloc[k]
STATS.add('low_rarity_passages', ', '.join(map(str, sorted(held.chunk))),
          'Comp. passages, taken from the lowest rarity up, with no Scheme 1 FAIL and at most one Scheme 2 FAIL '
          'in total (in passage order)')
STATS.add('low_rarity_max', held.rare_ratio.max(), 'highest rare-term ratio among them')
STATS.add('low_rarity_next', nxt.rare_ratio, f'rare-term ratio of the next passage (Comp. {nxt.chunk}), where that no longer holds')
STATS.add('low_rarity_s2_fails', '; '.join(f'{r.chunk}: {r["Scheme 2 FAIL"]}' for _, r in held.iterrows() if r.s2_fails),
          'the Scheme 2 FAIL among those passages (passage: model (TQS))')
gap_lo = c[~c.chunk.isin(CATASTROPHIC)].rare_ratio.max()
gap_hi = c[c.chunk.isin(CATASTROPHIC)].rare_ratio.min()
STATS.add('rarity_gap_low', gap_lo, 'highest rare-term ratio of any Comp. passage other than 8 and 10')
STATS.add('rarity_gap_high', gap_hi, 'lower rare-term ratio of Comp. 8 and 10')

# ---------------------------------------------------------------- rarity vs error type
# over all ten Comp. passages, and over the eight without Comp. 8 and 10
e = fin[fin.text == 'Comp'].merge(err, on=['text', 'chunk'])
rows = []
for scope, sub, sfx, slab in [('Comp. (all)', e, '', 'Comp. passages'),
                              ('Comp. (excl. 8, 10)', e[~e.chunk.isin(CATASTROPHIC)], '_x810', 'Comp. passages other than 8 and 10')]:
    for col, lab in [('term', 'Terminology errors'), ('acc', 'Accuracy errors')]:
        rr, pp = pearson(sub.rare_ratio, sub[col])
        rh, ph = spearman(sub.rare_ratio, sub[col])
        rows.append({'passages': scope, 'n': len(sub), 'errors': lab, 'r': rr, 'p': pp, 'rho': rh, 'p rho': ph})
        STATS.add(f'err_{col}_r{sfx}', rr, f'{slab}: rarity vs {lab}, Pearson r')
        STATS.add(f'err_{col}_rho{sfx}', rh, f'{slab}: rarity vs {lab}, Spearman rho')
        STATS.add(f'err_{col}_p{sfx}', pp, f'p for the Pearson r, rarity vs {lab} ({slab})' if sfx else f'p for the Pearson r, rarity vs {lab}')
        STATS.add(f'err_{col}_prho{sfx}', ph, f'p for the Spearman rho, rarity vs {lab} ({slab})' if sfx else f'p for the Spearman rho, rarity vs {lab}')
write_csv(pd.DataFrame(rows), 'rarity_vs_error_type.csv')

STATS.save()
show = st.set_index('step')[['r Comp', 'R2', 'R2 CI low', 'R2 CI high', 'rho Comp', 'p rho', 'Cook D 8', 'Cook D 10',
                             'r without 8,10', 'p without', 'mean ratio Comp', 'mean ratio Mix', 'ratio 8', 'ratio 10',
                             'max ratio other Comp']].T
print(show.round(3).to_string())
print(by_step[['step', 'predictor'] + [c for c in by_step.columns if c.endswith('shown')]].to_string(index=False))
print(c[['chunk', 'rare_ratio', 'TQS', 's1_fails', 's2_fails', 'Scheme 2 FAIL']].round(3).to_string(index=False))
