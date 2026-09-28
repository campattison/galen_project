"""11 Translation quality of groups of translations.

Mean TQS, its SD, pass rates and critical errors for groups of translations that the comparisons
between Mix. and Comp. use: each text, Comp. 8 and 10 against the other eight Comp. passages,
and Comp. without passages 3, 8 and 10 (or without 8, 10 and ChatGPT's translation of 3), each
also by model; and the mean COMET score of Comp. 8 and 10 against that of the other Comp. passages.

Inputs : mqm/ summary sheets, mt_eval/output/evaluations/*.json (COMET; via common)
Outputs: quality_by_group.csv, statistics_11_quality_by_group.csv
"""
import pandas as pd

from common import CATASTROPHIC, FAIL_BELOW, MODELS, Statistics, load_mqm, metric_scores, write_csv

STATS = Statistics(__file__)
mq = load_mqm()

# ---------------------------------------------------------------- mean TQS and pass rates by group
cat = (mq.text == 'Comp') & mq.chunk.isin(CATASTROPHIC)
groups = [('Mix.', mq.text == 'Mix'), ('Comp.', mq.text == 'Comp'), ('Comp. 8 and 10', cat),
          ('Comp. other eight', (mq.text == 'Comp') & ~cat),
          ('Comp. excluding 3, 8, 10', (mq.text == 'Comp') & ~mq.chunk.isin([3, 8, 10])),
          # passage 3 dropped for ChatGPT only
          ('Comp. excluding 8, 10 and ChatGPT on 3',
           (mq.text == 'Comp') & ~mq.chunk.isin(CATASTROPHIC) & ~((mq.chunk == 3) & (mq.model == 'ChatGPT')))]
rows = []
for name, mask in groups:
    g = mq[mask]
    row = {'group': name, 'translations': len(g), 'mean TQS': g.TQS.mean(), 'SD TQS': g.TQS.std(ddof=1),
           'Scheme 1 pass %': (g.TQS >= FAIL_BELOW).mean() * 100,
           'Scheme 2 pass %': ((g.TQS >= FAIL_BELOW) & (g.critical == 0)).mean() * 100,
           'critical errors': int(g.critical.sum())}
    for m in MODELS:
        row[f'mean TQS {m}'] = g[g.model == m].TQS.mean()
    rows.append(row)
qg = pd.DataFrame(rows)
write_csv(qg, 'quality_by_group.csv')
Q = qg.set_index('group')
STATS.add('tqs_mix', Q.loc['Mix.', 'mean TQS'], 'mean TQS, Mix.')
STATS.add('tqs_mix_sd', Q.loc['Mix.', 'SD TQS'], 'SD of TQS, Mix.')
STATS.add('tqs_comp', Q.loc['Comp.', 'mean TQS'], 'mean TQS, Comp.')
STATS.add('tqs_comp_sd', Q.loc['Comp.', 'SD TQS'], 'SD of TQS, Comp.')
gap = Q.loc['Comp. other eight', 'mean TQS'] - Q.loc['Comp. 8 and 10', 'mean TQS']
STATS.add('tqs_gap_cat', gap, 'mean TQS of the other eight Comp. passages minus that of Comp. 8 and 10')
diff = Q.loc['Mix.', 'mean TQS'] - Q.loc['Comp. other eight', 'mean TQS']
STATS.add('tqs_mix_minus_ordinary', diff, 'mean TQS of Mix. minus that of the other eight Comp. passages (all models)')
per_model = [Q.loc['Mix.', f'mean TQS {m}'] - Q.loc['Comp. other eight', f'mean TQS {m}'] for m in MODELS]
STATS.add('tqs_mix_minus_ordinary_models', ', '.join(f'{m} {v:.1f}' for m, v in zip(MODELS, per_model)),
          'the same difference, by model')
diff3 = Q.loc['Mix.', 'mean TQS'] - Q.loc['Comp. excluding 3, 8, 10', 'mean TQS']
STATS.add('tqs_mix_minus_x3810', diff3, 'mean TQS of Mix. minus that of Comp. excluding 3, 8, 10')
diff_c3 = Q.loc['Mix.', 'mean TQS'] - Q.loc['Comp. excluding 8, 10 and ChatGPT on 3', 'mean TQS']
STATS.add('tqs_mix_minus_x810c3', diff_c3, 'mean TQS of Mix. minus that of Comp. excluding 8, 10 and ChatGPT on passage 3')
STATS.add('tqs_x810c3_sd', Q.loc['Comp. excluding 8, 10 and ChatGPT on 3', 'SD TQS'], 'SD of TQS for that subset')
for name, key in [('Comp. other eight', 'other8'), ('Comp. excluding 3, 8, 10', 'x3810'),
                  ('Comp. excluding 8, 10 and ChatGPT on 3', 'x810c3')]:
    STATS.add(f'tqs_{key}', Q.loc[name, 'mean TQS'], f'mean TQS, {name}')
    STATS.add(f's1_pass_{key}', Q.loc[name, 'Scheme 1 pass %'], f'Scheme 1 pass rate, {name}')
share = mq[(mq.text == 'Comp') & mq.chunk.isin([3, 8, 10])].critical.sum() / mq[mq.text == 'Comp'].critical.sum() * 100
STATS.add('crit_share_3810', share, 'share of the critical errors in Comp. that fall in passages 3, 8 and 10 (%)')
c8 = mq[(mq.text == 'Comp') & (mq.chunk == 8)].TQS
STATS.add('comp8_tqs_range', f'{c8.min()}-{c8.max()}', 'Comp. 8: lowest and highest TQS of the three models')

# ---------------------------------------------------------------- COMET on Comp. 8 and 10 and on the rest
# (Comp. has one reference, so its scores are the same under every reference protocol)
comp = metric_scores('mean').query('text == "Comp"')
c_other = comp[~comp.chunk.isin(CATASTROPHIC)].COMET.mean() * 100
c_cat = comp[comp.chunk.isin(CATASTROPHIC)].COMET.mean() * 100
STATS.add('comet_other', c_other, 'mean COMET x100, the other eight Comp. passages')
STATS.add('comet_cat', c_cat, 'mean COMET x100, Comp. 8 and 10')
STATS.add('comet_dip_points', c_other - c_cat, 'the difference, in points')
STATS.add('comet_dip_pct', (c_other - c_cat) / c_other * 100, 'the same difference relative to the other passages (%)')
STATS.save()
print(qg.round(1).to_string(index=False))
