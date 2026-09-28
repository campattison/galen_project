"""10 How much could remaining lemma errors move the rarity result?

Three checks on the final measure:
  (a) random errors: the hand check (09) bounds the rate of wrong rare/common calls
      among repaired lemmas at the upper Wilson limit (about 7%). Flip that many
      repaired tokens at random, 2,000 times (numpy default_rng seed 1).
  (b) worst case: spend the same number of errors where they most narrow the gap
      between the catastrophic passages (8, 10) and the rest (greedy, on counts).
  (c) words absent from Diorisis count as rare; suppose half of them were common.

Inputs : outputs/rarity_tokens.csv (07), outputs/lemma_check_summary.csv (09), mqm/
Outputs: rarity_sensitivity.csv, statistics_10_rarity_sensitivity.csv
"""
import numpy as np
import pandas as pd

from common import CATASTROPHIC, OUT, RARE_BELOW, Statistics, load_mqm, passage_quality, pearson, write_csv

STATS = Statistics(__file__)
tok = pd.read_csv(OUT / 'rarity_tokens.csv', dtype=str, keep_default_na=False)
d = tok[tok.included == 'True'].copy()
d['chunk'] = d.chunk.astype(int)
d['f'] = d.freq_final.astype(float).astype(int)
d['rare'] = d.f < RARE_BELOW
d['repaired'] = (d.kind == 'word') & (d.freq_step1.astype(float) == 0) & (d.freq_step2.astype(float) > 0)
d = d.reset_index(drop=True)
q = passage_quality(load_mqm()).set_index(['text', 'chunk'])
comp_chunks = list(range(1, 11))
tqs = q.loc['Comp'].loc[comp_chunks, 'TQS'].values
other = [c for c in comp_chunks if c not in CATASTROPHIC]

check = pd.read_csv(OUT / 'lemma_check_summary.csv')
status_low = float(check.loc[check.check.str.startswith('word correctly classed'), 'Wilson 95% low %'].iloc[0]) / 100
err_rate = 1 - status_low
idx = np.where(d.repaired.values)[0]
k = int(round(err_rate * len(idx)))
comp_mask = (d.text == 'Comp').values
chunk_arr = d.chunk.values


def comp_ratios(rare):
    s = pd.Series(rare[comp_mask]).groupby(chunk_arr[comp_mask]).mean()
    return s.loc[comp_chunks].values


def summarise(ratios):
    r = pearson(ratios, tqs)[0]
    oth = np.array([ratios[c - 1] for c in other])
    rx = pearson(oth, np.array([tqs[c - 1] for c in other]))[0]
    gap = min(ratios[c - 1] for c in CATASTROPHIC) - oth.max()
    return r, rx, gap


base = summarise(comp_ratios(d.rare.values))
rng = np.random.default_rng(1)
sims = []
for _ in range(2000):
    rare = d.rare.values.copy()
    flip = rng.choice(idx, size=k, replace=False)
    rare[flip] = ~rare[flip]
    sims.append(summarise(comp_ratios(rare)))
sims = np.array(sims)

# (b) greedy worst case on passage counts
n = d[d.text == 'Comp'].groupby('chunk').size().loc[comp_chunks].values.astype(float)
rare_n = d[d.text == 'Comp'].groupby('chunk').rare.sum().loc[comp_chunks].values.astype(float)
rep = d[(d.text == 'Comp') & d.repaired]
can_lower = rep[rep.rare].groupby('chunk').size().reindex(comp_chunks, fill_value=0).values.astype(float)
can_raise = rep[~rep.rare].groupby('chunk').size().reindex(comp_chunks, fill_value=0).values.astype(float)
for _ in range(k):
    ratio = rare_n / n
    lo_cat = min(CATASTROPHIC, key=lambda c: (ratio[c - 1], c))
    top = max(ratio[c - 1] for c in other)
    opts = []
    if can_lower[lo_cat - 1] > 0:
        opts.append((1 / n[lo_cat - 1], 'lower', lo_cat))
    for c in other:
        if can_raise[c - 1] > 0:
            gain = max(0.0, (rare_n[c - 1] + 1) / n[c - 1] - top)
            opts.append((gain, 'raise', c))
    gain, act, c = max(opts, key=lambda o: (o[0], o[1] == 'lower', -o[2]))
    if act == 'lower':
        rare_n[c - 1] -= 1
        can_lower[c - 1] -= 1
    else:
        rare_n[c - 1] += 1
        can_raise[c - 1] -= 1
worst = summarise(rare_n / n)
worst_top2 = sorted(comp_chunks, key=lambda c: -(rare_n / n)[c - 1])[:2]

# (c) half of the absent words common
g = d[d.text == 'Comp'].groupby('chunk').agg(tokens=('f', 'size'), rare=('rare', 'sum'), absent=('f', lambda x: int((x == 0).sum())))
adj = ((g.rare - 0.5 * g.absent) / g.tokens).loc[comp_chunks].values
half = summarise(adj)

rows = [{'scenario': 'final measure', 'errors': 0, 'r Comp': base[0], 'r without 8,10': base[1], 'gap (lower of 8/10 minus highest other)': base[2]},
        {'scenario': f'random: {k} of {len(idx)} repaired tokens flipped, 2.5th percentile', 'errors': k,
         'r Comp': np.percentile(sims[:, 0], 2.5), 'r without 8,10': np.percentile(sims[:, 1], 2.5), 'gap (lower of 8/10 minus highest other)': np.percentile(sims[:, 2], 2.5)},
        {'scenario': f'random: {k} of {len(idx)} repaired tokens flipped, 97.5th percentile', 'errors': k,
         'r Comp': np.percentile(sims[:, 0], 97.5), 'r without 8,10': np.percentile(sims[:, 1], 97.5), 'gap (lower of 8/10 minus highest other)': np.percentile(sims[:, 2], 97.5)},
        {'scenario': 'random: smallest gap in 2,000 runs', 'errors': k, 'r Comp': np.nan, 'r without 8,10': np.nan,
         'gap (lower of 8/10 minus highest other)': sims[:, 2].min()},
        {'scenario': f'worst case: {k} errors placed to narrow the gap', 'errors': k, 'r Comp': worst[0], 'r without 8,10': worst[1],
         'gap (lower of 8/10 minus highest other)': worst[2]},
        {'scenario': 'half of the words absent from Diorisis counted common', 'errors': int(g.absent.sum()),
         'r Comp': half[0], 'r without 8,10': half[1], 'gap (lower of 8/10 minus highest other)': half[2]}]
res = pd.DataFrame(rows)
write_csv(res, 'rarity_sensitivity.csv')
STATS.add('sens_error_rate', err_rate * 100, 'upper 95% bound on wrong rare/common calls among repaired lemmas (%)')
STATS.add('sens_k', k, 'errors simulated')
STATS.add('sens_r_lo', np.percentile(sims[:, 0], 2.5), 'random errors: r (2.5th percentile)')
STATS.add('sens_r_hi', np.percentile(sims[:, 0], 97.5), 'random errors: r (97.5th percentile)')
STATS.add('sens_gap_min', sims[:, 2].min(), 'random errors: smallest gap between 8/10 and the rest in 2,000 runs')
STATS.add('sens_top2_share', float((sims[:, 2] > 0).mean() * 100), 'random runs in which 8 and 10 remain the two rarest (%)')
STATS.add('sens_worst_r', worst[0], 'worst case: r')
STATS.add('sens_worst_gap', worst[2], 'worst case: gap')
STATS.add('sens_worst_top2', ', '.join(map(str, sorted(worst_top2))), 'worst case: two rarest passages')
STATS.add('sens_absent_tokens', int(g.absent.sum()), 'Comp. tokens counted rare only because the word is absent from Diorisis')
STATS.add('sens_half_8', adj[7], 'half-absent scenario: Comp. 8')
STATS.add('sens_half_10', adj[9], 'half-absent scenario: Comp. 10')
STATS.add('sens_half_other_max', max(adj[c - 1] for c in other), 'half-absent scenario: highest other Comp.')
STATS.save()
print(res.round(3).to_string(index=False))
