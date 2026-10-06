"""04 The TQS rating thresholds as error budgets.

TQS = 100 - (1 x minor + 5 x major + 25 x critical) / words x 100, floored at 0, where words is the
word count of the English translation scored (214-347 words), not of the Greek passage (200-233).

  - the error budget: the most minor, major or critical errors a translation of the shortest and
    of the longest length can carry and stay in each band, and the count at which it FAILs;
  - which errors put the translations below HIGH PASS in this dataset.

Inputs : mqm/MQM SUMMARY TABLES - * Summary Sorted.csv
Outputs: tqs_error_budget.csv, tqs_error_budget_by_severity.csv, band_composition.csv,
         statistics_04_tqs_thresholds.csv
"""
import numpy as np
import pandas as pd

from common import FAIL_BELOW, HIGH_PASS_FROM, Statistics, load_mqm, write_csv

STATS = Statistics(__file__)
mq = load_mqm()
wc = mq.word_count
one, two = 100 - 2500 / wc, 100 - 5000 / wc
budget = pd.DataFrame([{'MT words min': int(wc.min()), 'MT words max': int(wc.max()),
                        'TQS with one critical error, min': one.min(), 'TQS with one critical error, max': one.max(),
                        'TQS with two critical errors, max': two.max()}])
write_csv(budget, 'tqs_error_budget.csv')
STATS.add('wc_min', int(wc.min()), 'shortest English translation in words (the denominator of TQS)')
STATS.add('wc_max', int(wc.max()), 'longest English translation in words (the denominator of TQS)')
STATS.add('tqs_one_crit_min', one.min(), 'TQS with a single critical error and nothing else: lowest')
STATS.add('tqs_one_crit_max', one.max(), 'TQS with a single critical error and nothing else: highest')
STATS.add('tqs_two_crit_max', two.max(), 'TQS with two critical errors: highest possible')

# ---------------------------------------------------------------- the bands as error budgets
# A band is a ceiling on APT: TQS >= t means APT <= (100 - t)/100 x words. Restated in errors of one
# kind, at the shortest and the longest output, that ceiling is what the band actually asks for.
WEIGHTS = [('minor', 1), ('major', 5), ('critical', 25)]
rows = []
for band, thr in [('HIGH PASS', HIGH_PASS_FROM), ('LOW PASS or better', FAIL_BELOW)]:
    for name, w in WEIGHTS:
        lo, hi = ((100 - thr) / 100 * wc.min() // w, (100 - thr) / 100 * wc.max() // w)
        rows.append({'band': f'{band} (TQS >= {thr})', 'error type': name,
                     'most it can carry, shortest output': int(lo), 'most it can carry, longest output': int(hi)})
        STATS.add(f'budget_{band.split()[0].lower()}_{name}', int(lo), f'most {name} errors the shortest translation can carry and stay {band}')
        STATS.add(f'budget_{band.split()[0].lower()}_{name}_longest', int(hi), 'the same, longest translation')
eb = pd.DataFrame(rows)
write_csv(eb, 'tqs_error_budget_by_severity.csv')
# FAIL begins one error beyond the LOW PASS budget
for name, w in WEIGHTS:
    lo = int((100 - FAIL_BELOW) / 100 * wc.min() // w) + 1
    hi = int((100 - FAIL_BELOW) / 100 * wc.max() // w) + 1
    assert 100 - (lo - 1) * w / wc.min() * 100 >= FAIL_BELOW > 100 - lo * w / wc.min() * 100
    STATS.add(f'fail_at_{name}', lo, f'{name} errors at which the shortest translation first FAILs')
    STATS.add(f'fail_at_{name}_longest', hi, 'the same, longest translation')

# ---------------------------------------------------------------- what puts a translation below HIGH PASS here
mq['band'] = np.where(mq.TQS >= HIGH_PASS_FROM, 'HIGH PASS',
                      np.where(mq.TQS >= FAIL_BELOW, 'LOW PASS', 'FAIL'))
comp = (mq.groupby(['text', 'band']).size().unstack(fill_value=0)
          .reindex(columns=['HIGH PASS', 'LOW PASS', 'FAIL'], fill_value=0).reset_index())
write_csv(comp, 'band_composition.csv')
below = mq[mq.band != 'HIGH PASS']
no_crit = below[below.critical == 0]
STATS.add('below_hp', len(below), 'translations below HIGH PASS')
STATS.add('below_hp_no_crit', len(no_crit), 'translations below HIGH PASS with no critical error (demoted by major and minor errors alone)')
STATS.add('below_hp_no_crit_majors', f'{no_crit.major.min()}-{no_crit.major.max()}', 'fewest-most major errors among those translations')
fails = mq[mq.band == 'FAIL']
STATS.add('fail_n', len(fails), 'translations that FAIL under Scheme 1')
STATS.add('fail_no_crit', int((fails.critical == 0).sum()), 'translations that FAIL under Scheme 1 with no critical error')
s2 = np.where(mq.critical > 0, 'FAIL', mq.band)
STATS.add('scheme_disagreements', int((s2 != mq.band).sum()), 'translations the two schemes rate differently (all LOW PASS under 1, FAIL under 2)')

STATS.save()
print(budget.round(1).to_string(index=False))
