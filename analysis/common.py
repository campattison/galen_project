"""Shared paths, loaders, statistics, formatting and deterministic writers.

Every script in this folder imports from here. Outputs go to analysis/outputs/, or to the
folder named by $ANALYSIS_OUT (verify.py uses this to rerun everything into a scratch folder).

Determinism: no network access, no clocks, fixed seeds where resampling is used, explicit
sort orders, and floats written with six decimals.
"""
import json
import logging
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                                    # the repository
DATA = HERE / 'data'
OUT = Path(os.environ.get('ANALYSIS_OUT', str(HERE / 'outputs')))
OUT.mkdir(parents=True, exist_ok=True)

METRICS = ['BLEU-4', 'chrF++', 'METEOR', 'ROUGE-L', 'BERTScore', 'COMET', 'BLEURT']   # also the column order of the tables
MODEL = {'openai': 'ChatGPT', 'claude': 'Claude', 'gemini': 'Gemini'}
MODELS = ['ChatGPT', 'Claude', 'Gemini']
ROW_MODELS = ['Claude', 'Gemini', 'ChatGPT']          # model order of the rating and per-translation tables
KEYS = ['text', 'chunk', 'model']
LABEL = {'Mix': 'Mix.', 'Comp': 'Comp.'}
RARE_BELOW = 50            # rare = fewer than 50 occurrences in Diorisis
FAIL_BELOW = 87            # Scheme 1: FAIL if TQS < 87
HIGH_PASS_FROM = 95        # HIGH PASS if TQS >= 95
CATASTROPHIC = [8, 10]     # Comp. 8 and 10, excluded in the stratified comparisons
# passage subsets for the Mix.-Comp. comparisons; exclusions apply to Comp. only
STRATA = [('All passages', []), ('Excl. 8, 10', [8, 10]), ('Excl. 3, 8, 10', [3, 8, 10])]
RATING_ABBR = {'HIGH PASS': 'HP', 'LOW PASS': 'LP', 'FAIL': 'F'}

MINUS = '−'


# ------------------------------------------------------------------ loaders
def load_mqm():
    """One row per (text, chunk, model) from the MQM summary sheets in mqm/.
    The sheets hold the same 30 rows twice (two sort orders); we check that the
    copies agree and keep one.

    TQS is the value printed in the sheets (one decimal). We recompute it from the error
    counts, TQS = 100 - APT / word count x 100 (floored at 0), where
    APT = minor + 5 x major + 25 x critical, and check that every printed value is this TQS
    rounded; the unrounded value is kept as TQS_exact."""
    frames = []
    for fn, label in [('MQM SUMMARY TABLES - Comp Summary Sorted.csv', 'Comp'),
                      ('MQM SUMMARY TABLES - Mixtures Summary Sorted.csv', 'Mixtures')]:
        d = pd.read_csv(ROOT / 'mqm' / fn, dtype=str)
        d = d[d['Text'] == label]
        keys = ['Text', 'Chunk', 'Model']
        assert (d.groupby(keys).nunique(dropna=False) <= 1).all().all(), f'conflicting duplicates in {fn}'
        frames.append(d.drop_duplicates(subset=keys))
    d = pd.concat(frames, ignore_index=True)
    num = {c: pd.to_numeric(d[c]) for c in ['Word Count', 'APT', 'TQS', 'Minor', 'Major', 'Critical']}
    assert (num['APT'] == num['Minor'] + 5 * num['Major'] + 25 * num['Critical']).all()
    tqs = (100 - num['APT'] / num['Word Count'] * 100).clip(lower=0)
    assert ((tqs - num['TQS']).abs() <= 0.05 + 1e-9).all(), 'printed TQS is not the rounded TQS'
    out = pd.DataFrame({
        'text': d['Text'].map({'Comp': 'Comp', 'Mixtures': 'Mix'}),
        'chunk': d['Chunk'].astype(int),
        'model': d['Model'].map(MODEL),
        'word_count': num['Word Count'].astype(int),
        'TQS': num['TQS'].values,
        'TQS_exact': tqs.values,
        'rating': d['Final Quality Rating'],          # Scheme 2 (critical error = FAIL)
        'rating_s1': d['Quality Rating'],             # Scheme 1 (TQS alone)
    })
    for src, dst in [('Neutral', 'neutral'), ('Minor', 'minor'), ('Major', 'major'), ('Critical', 'critical'),
                     ('Term.: Total', 'term'), ('Acc.: Total', 'acc'),
                     ('Term.: Accuracy', 'term_acc'), ('Term.: Consistency', 'term_cons'),
                     ('Acc.: Mistranslation', 'acc_mis'), ('Acc.: Overtranslation', 'acc_over'),
                     ('Acc.: Undertranslation', 'acc_under'), ('Acc.: Addition', 'acc_add'),
                     ('Acc.: Omission', 'acc_om')]:
        out[dst] = pd.to_numeric(d[src]).astype(int).values
    assert (out.term == out.term_acc + out.term_cons).all(), 'Terminology subtypes do not sum'
    assert (out.acc == out[['acc_mis', 'acc_over', 'acc_under', 'acc_add', 'acc_om']].sum(axis=1)).all()
    assert len(out) == 60 and out.groupby('text').size().eq(30).all()
    return out.sort_values(['text', 'chunk', 'model']).reset_index(drop=True)


def rating_s1(tqs):
    """Scheme 1: the rating from TQS alone."""
    return 'HIGH PASS' if tqs >= HIGH_PASS_FROM else 'LOW PASS' if tqs >= FAIL_BELOW else 'FAIL'


EXPORT_COLUMNS = {'bleu4': 'BLEU-4', 'chrfpp': 'chrF++', 'meteor': 'METEOR', 'rougel': 'ROUGE-L',
                  'bertscore': 'BERTScore', 'bleurt': 'BLEURT', 'comet': 'COMET'}   # column names of data/mt_eval_*.csv


def _read_evaluation(path_mix, path_comp):
    rows = []
    for text, path in [('Mix', path_mix), ('Comp', path_comp)]:
        e = json.load(open(path, encoding='utf-8'))
        for d in e['detailed_scores']:
            r = {'text': text, 'chunk': int(d['chunk_id']), 'model': MODEL[d['model_name']]}
            per_ref = d.get('per_reference_scores') or {}
            for m in METRICS:
                r[m] = d['scores'].get(m)
                for k in ('ref1', 'ref2'):
                    if k in per_ref:
                        r[f'{m}|{k}'] = per_ref[k].get(m)
            rows.append(r)
    return pd.DataFrame(rows).sort_values(KEYS).reset_index(drop=True)


def load_eval_before_fix():
    """The automated metric scores as first computed, before the Mix. reference fix
    (data/mixtures_pre_fix/on_mixtures_evaluation.json; Comp. from the pipeline's output)."""
    ev = ROOT / 'mt_eval' / 'output' / 'evaluations'
    return _read_evaluation(DATA / 'mixtures_pre_fix' / 'on_mixtures_evaluation.json', ev / 'on_comp_evaluation.json')


def load_eval():
    """Automated metric scores and, for Mix., the scores against each reference.

    Reads the pipeline's evaluation files (mt_eval/output/evaluations/) and applies the scores
    regenerated after the Mix. reference fix (data/mt_eval_scores.csv and
    data/mt_eval_scores_per_reference.csv; see data/README.md): the input file had lost the
    blank line between the two reference translations of Mix. 2 and 4, so those passages were
    scored against misparsed references. Only Mix. 2 and 4 may change, and this is checked."""
    ev = ROOT / 'mt_eval' / 'output' / 'evaluations'
    ev = _read_evaluation(ev / 'on_mixtures_evaluation.json', ev / 'on_comp_evaluation.json').set_index(KEYS)
    changed = set()
    for fn, cols in [('mt_eval_scores.csv', dict(EXPORT_COLUMNS)),
                     ('mt_eval_scores_per_reference.csv',
                      {f'{c}_johnston': f'{m}|ref1' for c, m in EXPORT_COLUMNS.items()} |
                      {f'{c}_singer_vdeijk': f'{m}|ref2' for c, m in EXPORT_COLUMNS.items()})]:
        fixed = pd.read_csv(DATA / fn)
        fixed['text'] = fixed.text.str.rstrip('.')
        for _, row in fixed.iterrows():
            key = (row.text, int(row.passage), row.model)
            for src, dst in cols.items():
                if dst not in ev.columns or pd.isna(ev.loc[key, dst]):
                    continue
                if abs(row[src] - ev.loc[key, dst]) > 1e-6:
                    changed.add(key[:2])
                ev.loc[key, dst] = float(row[src])
    assert changed <= {('Mix', 2), ('Mix', 4)}, sorted(changed)
    return ev.reset_index()


PROTOCOLS = {
    'mean': 'mean of the two single-reference scores',
    'johnston': 'Johnston only',
    'singer': 'Singer & van der Eijk only',
    'multi': 'multi-reference',
}


def metric_scores(protocol='mean'):
    """Automated metric scores (0-1 scale), one row per translation (60 rows).

    Comp. has one reference, so its scores are the same under every protocol. For Mix.:
      'johnston' / 'singer'  scored against that reference alone (ref1 / ref2 in the evaluation files);
      'mean'                 the mean of those two scores (the protocol of the tables);
      'multi'                the pipeline's multi-reference score (mt_eval/src/evaluator.py): BLEU-4
                             pools n-gram matches over both references; chrF++ and METEOR take the
                             better reference themselves; for ROUGE-L, BERTScore, COMET and BLEURT the
                             pipeline keeps the higher of the two single-reference scores."""
    ev = load_eval()
    out = ev[KEYS].copy()
    mix = ev.text == 'Mix'
    for m in METRICS:
        r1, r2 = ev[f'{m}|ref1'], ev[f'{m}|ref2']
        v = {'multi': ev[m], 'johnston': r1, 'singer': r2, 'mean': (r1 + r2) / 2}[protocol]
        out[m] = v.where(mix, ev[m]).astype(float)
    assert out[METRICS].notna().all().all() and len(out) == 60
    return out


def subset(sc, text, model=None):
    """Rows of one text, and of one model unless model is None or 'Aggregate'."""
    g = sc[sc.text == text]
    return g if model in (None, 'Aggregate') else g[g.model == model]


def correlations(sc, tqs, texts):
    """Pearson and Spearman correlation of each metric with TQS over the given texts."""
    d = sc.merge(tqs, on=KEYS, validate='1:1')
    d = d[d.text.isin(texts)]
    out = {}
    for m in METRICS:
        r, p = pearson(d[m], d.TQS)
        rho, prho = spearman(d[m], d.TQS)
        out[m] = {'n': len(d), 'r': r, 'p': p, 'rho': rho, 'p_rho': prho}
    return out


def correlation_order(sc, tqs):
    """The metrics ordered by their Pearson correlation with TQS over all 60 translations."""
    c = correlations(sc, tqs, ['Mix', 'Comp'])
    return sorted(METRICS, key=lambda m: -c[m]['r'])


def load_texts():
    """Greek source and reference translations, parsed with the pipeline's own parser.
    Mix. refs: [Johnston (Loeb), Singer & van der Eijk]; Comp.: [Marai]."""
    sys.path.insert(0, str(ROOT / 'mt_eval' / 'src'))
    logging.disable(logging.CRITICAL)
    from parser import InputParser  # noqa: E402  (repository module)
    p = InputParser()
    out = {}
    for text, fn in [('Mix', 'on_mixtures.txt'), ('Comp', 'on_comp.txt')]:
        out[text] = {int(c.chunk_id): {'greek': c.greek_text, 'refs': c.reference_translations}
                     for c in p.parse_file(str(ROOT / 'mt_eval' / 'input' / fn))}
    return out


def load_translations():
    """{(text, chunk, model): record} from the translation files."""
    out = {}
    for text, fn in [('Mix', 'on_mixtures_translations.json'), ('Comp', 'on_comp_translations.json')]:
        t = json.load(open(ROOT / 'mt_eval' / 'output' / 'translations' / fn, encoding='utf-8'))
        for ch, mods in t.items():
            for m, v in mods.items():
                out[(text, int(ch), MODEL[m])] = v
    return out


def passage_quality(mq):
    """Per passage: mean TQS over the three models, total critical errors, and
    Scheme 1 / Scheme 2 FAIL counts."""
    g = mq.assign(s1_fail=mq.TQS < FAIL_BELOW, s2_fail=(mq.TQS < FAIL_BELOW) | (mq.critical > 0))
    return (g.groupby(['text', 'chunk'])
             .agg(TQS=('TQS', 'mean'), critical=('critical', 'sum'),
                  s1_fails=('s1_fail', 'sum'), s2_fails=('s2_fail', 'sum'))
             .reset_index())


# ------------------------------------------------------------------ statistics
def pearson(x, y):
    r, p = stats.pearsonr(np.asarray(x, float), np.asarray(y, float))
    return float(r), float(p)


def spearman(x, y):
    r, p = stats.spearmanr(np.asarray(x, float), np.asarray(y, float))
    return float(r), float(p)


def welch_p(a, b):
    """Welch's t-test (unequal variances), two-tailed."""
    return float(stats.ttest_ind(np.asarray(a, float), np.asarray(b, float), equal_var=False).pvalue)


def pooled_sd(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    n1, n2 = len(a), len(b)
    return float(np.sqrt(((n1 - 1) * a.std(ddof=1) ** 2 + (n2 - 1) * b.std(ddof=1) ** 2) / (n1 + n2 - 2)))


def cohen_d(a, b):
    """(mean a - mean b) / pooled SD."""
    return (float(np.mean(np.asarray(a, float))) - float(np.mean(np.asarray(b, float)))) / pooled_sd(a, b)


def fisher_ci(r, n):
    """95% CI for a correlation via Fisher's z."""
    z, se, q = np.arctanh(r), 1 / np.sqrt(n - 3), stats.norm.ppf(0.975)
    return float(np.tanh(z - q * se)), float(np.tanh(z + q * se))


def wilson(k, n, z=1.96):
    """Wilson score interval for a proportion k/n."""
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d


def cooks_distance(x, y):
    """Cook's D for simple OLS y ~ x."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    X = np.column_stack([np.ones(len(x)), x])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    e = y - X @ b
    mse = e @ e / (len(x) - 2)
    h = np.diag(X @ np.linalg.inv(X.T @ X) @ X.T)
    return (e ** 2 / (2 * mse)) * (h / (1 - h) ** 2)


def bootstrap_r2(x, y, seed=0, n_boot=10000):
    """Percentile 95% CI for R^2 of y ~ x, resampling passages with replacement.
    Resamples in which x has no variance are skipped."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        i = rng.integers(0, len(x), len(x))
        if np.std(x[i]) > 0:
            vals.append(stats.pearsonr(x[i], y[i])[0] ** 2)
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi), len(vals)


# ------------------------------------------------------------------ number formats of the tables
def f_r(v, nd=2):
    """Correlation: -.95 (minus sign, no leading zero), +.95 for positive values."""
    s = f'{abs(v):.{nd}f}'.lstrip('0') if abs(v) < 1 else f'{abs(v):.{nd}f}'
    return (MINUS if v < 0 and float(s) != 0 else ('+' if v > 0 else '')) + s


def f_r_plain(v, nd=2):
    """Correlation without the plus sign: .95, -.95."""
    s = f_r(v, nd)
    return s[1:] if s.startswith('+') else s


def f_p(p):
    """p-value: .003, < .001."""
    if p < 0.001:
        return '< .001'
    return f'{p:.3f}'.lstrip('0')


def f_pct(v, nd=1):
    """Percentage with a minus sign: -48.7%."""
    return (MINUS if v < 0 else '') + f'{abs(v):.{nd}f}%'


def f_num(v, nd=1):
    """Number with a minus sign: -2.1."""
    return (MINUS if v < 0 else '') + f'{abs(v):.{nd}f}'


def stars(p):
    return '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''


def f_r_table(r, p=None, nd=2):
    """Correlation in a table cell: +0.75*** (sign, leading zero, significance mark)."""
    s = f'{abs(r):.{nd}f}'
    sign = '' if float(s) == 0 else (MINUS if r < 0 else '+')
    return sign + s + ('' if p is None else stars(p))


def f_ci(lo, hi, nd=2):
    return f'[{f_r_plain(lo, nd)}, {f_r_plain(hi, nd)}]'


def f_mean_sd(mean, sd, nd=1):
    return f'{f_num(mean, nd)} (± {sd:.{nd}f})'


# ------------------------------------------------------------------ writers
def _cell(v):
    if v is None or v is pd.NA:
        return ''
    if isinstance(v, (bool, np.bool_)):
        return 'True' if v else 'False'
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, (float, np.floating)):
        if v != v:
            return ''
        if abs(v) < 5e-7:
            v = 0.0
        return f'{float(v):.6f}'
    return str(v)


def write_csv(df, name):
    """UTF-8, LF line endings, floats with six decimals, row order as given."""
    df = df.copy()
    for c in df.columns:
        df[c] = [_cell(v) for v in df[c].tolist()]
    df.to_csv(OUT / name, index=False, lineterminator='\n', encoding='utf-8')


def write_text(lines, name):
    with open(OUT / name, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lines).rstrip('\n') + '\n')


class Statistics:
    """The statistics a script reports besides its tables: one row per quantity, with a key, the
    value and what it is. Saved as outputs/statistics_<script>.csv."""

    def __init__(self, script):
        self.script = Path(script).stem
        self.rows = []

    def add(self, key, value, description):
        assert not any(r['key'] == key for r in self.rows), key
        self.rows.append({'key': key, 'value': value, 'description': description})
        return value

    def save(self):
        write_csv(pd.DataFrame(self.rows, columns=['key', 'value', 'description'], dtype=object),
                  f'statistics_{self.script}.csv')


class CellValues:
    """The value behind each number of a table before the table rounds it (long format: row, column,
    statistic, value), saved next to the table as <table file>_values.csv, to six decimals."""

    def __init__(self):
        self.rows = []

    def __call__(self, row, column, statistic, value):
        self.rows.append({'row': row, 'column': column, 'statistic': statistic, 'value': float(value)})

    def frame(self):
        return pd.DataFrame(self.rows, columns=['row', 'column', 'statistic', 'value'])

    def get(self, row, column, statistic):
        d = self.frame()
        x = d[(d.row == row) & (d.column == column) & (d.statistic == statistic)].value
        assert len(x) == 1, (row, column, statistic)
        return float(x.iloc[0])
