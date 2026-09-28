"""06 How the translations were generated: dates, attempts, model versions and API parameters.

Reads the stored translation records (timestamps, attempts, status, model IDs) and
checks the API calls in mt_eval/src/translator.py for tool or search parameters.

Inputs : mt_eval/output/translations/*_translations.json, mt_eval/src/translator.py
Outputs: generation_metadata.csv, api_call_parameters.csv, statistics_06_generation_metadata.csv
"""
import ast
import re

import pandas as pd

from common import ROOT, Statistics, load_translations, write_csv

STATS = Statistics(__file__)
rows = []
for (text, chunk, model), v in sorted(load_translations().items()):
    meta = ast.literal_eval(v['metadata']) if isinstance(v.get('metadata'), str) else (v.get('metadata') or {})
    rows.append({'text': text, 'chunk': chunk, 'model': model, 'status': v.get('status'),
                 'date': str(v.get('timestamp', ''))[:10], 'attempt': meta.get('attempt'),
                 'model_id': meta.get('model'), 'reasoning_effort': meta.get('reasoning_effort', '')})
g = pd.DataFrame(rows)
write_csv(g, 'generation_metadata.csv')
STATS.add('gen_n', len(g), 'translations stored')
STATS.add('gen_dates', ', '.join(sorted(g.date.unique())), 'generation date(s)')
STATS.add('gen_first_attempt', int((g.attempt == 1).sum()), 'translations produced on the first attempt (one generation per passage per model)')
STATS.add('gen_success', int((g.status == 'success').sum()), 'records with status success')

# ---- API calls: which parameters are passed (and that no tool/search parameter is)
src = (ROOT / 'mt_eval' / 'src' / 'translator.py').read_text(encoding='utf-8')
calls = [('OpenAI (GPT-5)', r'responses\.create\((.*?)\n\s*\)'),
         ('Anthropic (Claude Sonnet 4.5)', r'messages\.create\((.*?)\n\s*\)'),
         ('Google (Gemini 2.5 Pro)', r'generate_content\((.*?)\n\s*\)\n')]
rows = []
for api, pat in calls:
    m = re.search(pat, src, flags=re.S)
    assert m, api
    body = m.group(1)
    params = sorted(set(re.findall(r'(\w+)\s*=', body)))
    line = src[:m.start()].count('\n') + 1
    rows.append({'API': api, 'translator.py line': line, 'parameters passed': ', '.join(params),
                 'tool/search parameter': 'yes' if re.search(r'tools|web_search|google_search|grounding', body) else 'no'})
api = pd.DataFrame(rows)
write_csv(api, 'api_call_parameters.csv')
STATS.add('api_tools_any', int((api['tool/search parameter'] == 'yes').sum()), 'API calls that pass a tool or search parameter')
STATS.save()
print(g.groupby(['model', 'date', 'attempt', 'status']).size()); print(api.to_string(index=False))
