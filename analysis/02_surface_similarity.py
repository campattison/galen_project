"""02 Surface similarity of the LLM translations to the published English translations.

Are the LLM translations of Mix. closer to the two published English translations
than those translations are to each other? Sentence BLEU (sacreBLEU, effective order,
as in the pipeline) per passage, plus the longest run of identical words shared with
a reference.

Inputs : mt_eval/input/*.txt (references), mt_eval/output/translations/*_translations.json
Outputs: surface_similarity_by_passage.csv, surface_similarity_by_model.csv, verbatim_runs.csv,
         statistics_02_surface_similarity.csv
"""
import re
from difflib import SequenceMatcher

import numpy as np
import pandas as pd
from sacrebleu.metrics import BLEU
from scipy import stats

from common import MODELS, Statistics, load_texts, load_translations, write_csv

STATS = Statistics(__file__)
tx, tr = load_texts(), load_translations()
mt = {k: v['translation'] for k, v in tr.items()}
bleu = BLEU(effective_order=True)
sb = lambda hyp, ref: bleu.sentence_score(hyp, [ref]).score

rows = []
for ch in range(1, 11):
    J, S = tx['Mix'][ch]['refs']          # Johnston (Loeb), Singer & van der Eijk
    M = tx['Comp'][ch]['refs'][0]         # Marai (Comp., unpublished when the models were trained)
    rows.append({'chunk': ch,
                 'Singer vs Johnston (ref)': sb(S, J),
                 'Johnston vs Singer (ref)': sb(J, S),
                 'LLMs vs Johnston (mean of 3)': np.mean([sb(mt[('Mix', ch, m)], J) for m in MODELS]),
                 'LLMs vs Singer (mean of 3)': np.mean([sb(mt[('Mix', ch, m)], S) for m in MODELS]),
                 'LLMs vs Marai, Comp. (mean of 3)': np.mean([sb(mt[('Comp', ch, m)], M) for m in MODELS])})
s = pd.DataFrame(rows)
write_csv(s, 'surface_similarity_by_passage.csv')
means = s.drop(columns='chunk').mean()
for col, key in [('Singer vs Johnston (ref)', 'hh_s_vs_j'), ('Johnston vs Singer (ref)', 'hh_j_vs_s'),
                 ('LLMs vs Johnston (mean of 3)', 'llm_vs_j'), ('LLMs vs Singer (mean of 3)', 'llm_vs_s'),
                 ('LLMs vs Marai, Comp. (mean of 3)', 'llm_vs_marai')]:
    STATS.add(f'surface_{key}', means[col], f'mean sentence BLEU, {col}')
rows = []
for m in MODELS:
    rows.append({'model': m,
                 'vs Johnston': np.mean([sb(mt[('Mix', ch, m)], tx['Mix'][ch]['refs'][0]) for ch in range(1, 11)]),
                 'vs Singer & van der Eijk': np.mean([sb(mt[('Mix', ch, m)], tx['Mix'][ch]['refs'][1]) for ch in range(1, 11)])})
bym = pd.DataFrame(rows)
write_csv(bym, 'surface_similarity_by_model.csv')
for _, r in bym.iterrows():
    STATS.add(f'surface_{r.model}_j_s', f"{r['vs Johnston']:.6f}/{r['vs Singer & van der Eijk']:.6f}", f'mean sentence BLEU of {r.model} against Johnston / Singer & van der Eijk (Mix.)')
base_j = s['Singer vs Johnston (ref)'].mean()
STATS.add('surface_models_above_hh_j', int((bym['vs Johnston'] > base_j).sum()), 'models whose mean BLEU against Johnston exceeds that of the Singer & van der Eijk translation against Johnston')
STATS.add('surface_all_models_closer_j', int((bym['vs Johnston'] > bym['vs Singer & van der Eijk']).sum()), 'models whose Mix. output is closer (BLEU) to Johnston than to Singer & van der Eijk')
for a_col, b_col, key in [('LLMs vs Johnston (mean of 3)', 'Singer vs Johnston (ref)', 'j'),
                          ('LLMs vs Singer (mean of 3)', 'Johnston vs Singer (ref)', 's')]:
    diff = (s[a_col] - s[b_col]).mean()
    p = float(stats.wilcoxon(s[a_col], s[b_col]).pvalue)
    STATS.add(f'surface_diff_{key}', diff, f'{a_col} minus the other human translation against the same reference (BLEU points)')
    STATS.add(f'surface_p_{key}', p, 'Wilcoxon signed-rank p over the 10 passages')

# ---------------------------------------------------------------- longest verbatim word run
tok = lambda x: re.findall(r'[a-z0-9]+', x.lower())


def longest_run(a, b):
    """Length of the longest run of identical words, and the words themselves."""
    A, B = tok(a), tok(b)
    m = SequenceMatcher(None, A, B, autojunk=False).find_longest_match(0, len(A), 0, len(B))
    return m.size, ' '.join(A[m.a:m.a + m.size])


rows = []
for ch in range(1, 11):
    J, S = tx['Mix'][ch]['refs']
    n, words = longest_run(S, J)
    rows.append({'comparison': 'human-human (Mix.)', 'chunk': ch, 'model': '', 'reference': 'Singer vs Johnston',
                 'longest run (words)': n, 'shared words': words})
    for m in MODELS:
        for ref_name, ref in [('Johnston', J), ('Singer & van der Eijk', S)]:
            n, words = longest_run(mt[('Mix', ch, m)], ref)
            rows.append({'comparison': 'LLM vs published (Mix.)', 'chunk': ch, 'model': m, 'reference': ref_name,
                         'longest run (words)': n, 'shared words': words})
        n, words = longest_run(mt[('Comp', ch, m)], tx['Comp'][ch]['refs'][0])
        rows.append({'comparison': 'LLM vs unpublished reference (Comp.)', 'chunk': ch, 'model': m,
                     'reference': 'Marai', 'longest run (words)': n, 'shared words': words})
v = pd.DataFrame(rows)
write_csv(v, 'verbatim_runs.csv')
for comp_name, key in [('human-human (Mix.)', 'hh'), ('LLM vs published (Mix.)', 'llm_pub'),
                       ('LLM vs unpublished reference (Comp.)', 'llm_comp')]:
    g = v[v.comparison == comp_name]['longest run (words)']
    STATS.add(f'verbatim_{key}_mean', g.mean(), f'longest shared word run, {comp_name}: mean')
    STATS.add(f'verbatim_{key}_max', int(g.max()), f'longest shared word run, {comp_name}: maximum')
pub = v[v.comparison == 'LLM vs published (Mix.)']
for ref_name, key in [('Johnston', 'j'), ('Singer & van der Eijk', 's')]:
    g = pub[pub.reference == ref_name]['longest run (words)']
    STATS.add(f'verbatim_{key}_mean', g.mean(), f'longest shared word run, LLM vs {ref_name}: mean')
    STATS.add(f'verbatim_{key}_max', int(g.max()), f'longest shared word run, LLM vs {ref_name}: maximum')
hh_max = int(v[v.comparison == 'human-human (Mix.)']['longest run (words)'].max())
comp_max = int(v[v.comparison == 'LLM vs unpublished reference (Comp.)']['longest run (words)'].max())
over_hh = int((pub['longest run (words)'] > hh_max).sum())
over_comp = int((pub['longest run (words)'] > comp_max).sum())
STATS.add('verbatim_pub_over_hh_max', over_hh, f'LLM-published runs longer than the longest run between the two human translations ({hh_max} words)')
STATS.add('verbatim_pub_over_comp_max', over_comp, f'LLM-published runs longer than the longest LLM run with the unpublished Comp. reference ({comp_max} words)')
ctop = (v[v.comparison == 'LLM vs unpublished reference (Comp.)']
        .sort_values(['longest run (words)', 'chunk', 'model'], ascending=[False, True, True], kind='mergesort').iloc[0])
STATS.add('verbatim_comp_max_where', f'Comp. {ctop.chunk}, {ctop.model}', 'where the longest LLM run with the unpublished Comp. reference occurs')
top = (v[v.comparison == 'LLM vs published (Mix.)']
       .sort_values(['longest run (words)', 'chunk', 'model', 'reference'],
                    ascending=[False, True, True, True], kind='mergesort').iloc[0])
STATS.add('verbatim_max_where', f"Mix. {top.chunk}, {top.model} vs {top.reference}", 'where the longest LLM-published run occurs')
STATS.save()
print(s.round(1).to_string(index=False)); print(means.round(1).to_string())
print(v.groupby('comparison')['longest run (words)'].agg(['mean', 'max', 'size']))
