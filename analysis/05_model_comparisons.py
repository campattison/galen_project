"""05 Differences between the three models.

Friedman tests across the three models (passages as blocks), pairwise Wilcoxon
signed-rank tests (unadjusted), a Brown-Forsythe test of equal spread, and Scheme 2
outcomes per model on Comp.

Inputs : mqm/MQM SUMMARY TABLES - * Summary Sorted.csv
Outputs: model_tests.csv, scheme2_outcomes_comp.csv, statistics_05_model_comparisons.csv
"""
import pandas as pd
from scipy import stats

from common import FAIL_BELOW, HIGH_PASS_FROM, MODELS, Statistics, load_mqm, write_csv

STATS = Statistics(__file__)
mq = load_mqm()
PAIRS = [('Claude', 'ChatGPT'), ('Gemini', 'ChatGPT'), ('Gemini', 'Claude')]
rows = []
for scope, g in [('Mix', mq[mq.text == 'Mix']), ('Comp', mq[mq.text == 'Comp']), ('All', mq)]:
    w = g.pivot_table(index=['text', 'chunk'], columns='model', values='TQS').sort_index()
    wx = g.pivot_table(index=['text', 'chunk'], columns='model', values='TQS_exact').sort_index()
    r = {'scope': scope, 'passages': len(w),
         'Friedman p': float(stats.friedmanchisquare(*[w[m] for m in MODELS]).pvalue),
         # the printed (one-decimal) TQS ties ChatGPT and Gemini on Mix. 7 (97.51 vs 97.48 unrounded)
         'Friedman p, unrounded TQS': float(stats.friedmanchisquare(*[wx[m] for m in MODELS]).pvalue),
         'Brown-Forsythe p': float(stats.levene(*[g[g.model == m].TQS for m in MODELS], center='median').pvalue)}
    for a, b in PAIRS:
        r[f'Wilcoxon p {a} vs {b}'] = float(stats.wilcoxon(w[a], w[b]).pvalue)
        r[f'mean TQS {a} - {b}'] = float((w[a] - w[b]).mean())
    rows.append(r)
mt = pd.DataFrame(rows)
write_csv(mt, 'model_tests.csv')
M = mt.set_index('scope')
for scope in ['Mix', 'Comp', 'All']:
    STATS.add(f'friedman_{scope}', M.loc[scope, 'Friedman p'], f'Friedman p across models, {scope}')
    STATS.add(f'friedman_{scope}_unrounded', M.loc[scope, 'Friedman p, unrounded TQS'], f'Friedman p across models, {scope}, using unrounded TQS (robustness check)')
for a, b in PAIRS:
    p = M.loc['All', f'Wilcoxon p {a} vs {b}']
    STATS.add(f'wilcoxon_all_{a}_{b}', p, f'Wilcoxon p, {a} vs {b}, all 20 passages (unadjusted)')
STATS.add('bf_comp', M.loc['Comp', 'Brown-Forsythe p'], 'Brown-Forsythe p for equal TQS spread across models, Comp.')

c = mq[mq.text == 'Comp']
rows = []
for m in MODELS:
    g = c[c.model == m]
    fail = (g.TQS < FAIL_BELOW) | (g.critical > 0)
    hp = (g.TQS >= HIGH_PASS_FROM) & ~fail
    rows.append({'model': m, 'HIGH PASS': int(hp.sum()), 'LOW PASS': int((~fail & ~hp).sum()),
                 'FAIL': int(fail.sum()), 'FAIL %': fail.mean() * 100,
                 'Scheme 1 FAIL': int((g.TQS < FAIL_BELOW).sum())})
s2 = pd.DataFrame(rows)
write_csv(s2, 'scheme2_outcomes_comp.csv')
for _, r in s2.iterrows():
    STATS.add(f's2_comp_{r.model}', f"{r['HIGH PASS']}/{r['LOW PASS']}/{r.FAIL}", f'{r.model}, Comp., Scheme 2: HIGH PASS / LOW PASS / FAIL')
    STATS.add(f's2_comp_fail_pct_{r.model}', r['FAIL %'], f'{r.model}, Comp., Scheme 2 FAIL rate (%)')
STATS.save()
print(mt.round(3).to_string(index=False)); print(s2.to_string(index=False))
