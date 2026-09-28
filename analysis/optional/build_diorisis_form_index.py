"""Rebuild data/diorisis_form_index.json from the Diorisis XML files (optional).

The corrected rarity measure looks up each Galenic word form in Diorisis to find the
lemma Diorisis assigns it. This script records, for every form that occurs in the passages
(data/stanza_lemmas.csv and data/stanza_lemmas_comp1_translated.csv), how often Diorisis files it
under each lemma, once keyed by canonical Beta Code and once by the bare letters. The file in data/ was built
with this script; rerun it to check that file (it needs the corpus: corpus_metrics/download_diorisis.sh).
By default it writes outputs/optional/diorisis_form_index.json and reports whether it is identical to the
file in data/; give an output path to write elsewhere.

    python optional/build_diorisis_form_index.py [path/to/Diorisis] [output.json] [diorisis_frequencies.json]

(defaults: corpus_metrics/Diorisis, outputs/optional/diorisis_form_index.json, corpus_metrics/diorisis_frequencies.json)

Deterministic: files are read in sorted order and the JSON is written with sorted keys.
It also recounts all lemma tokens and checks them against corpus_metrics/diorisis_frequencies.json.
"""
import glob
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from greek import bare, canon_beta, needed_keys, read_stanza_tokens  # noqa: E402

ROOT = HERE.parent
dio_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'corpus_metrics' / 'Diorisis'
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'outputs' / 'optional' / 'diorisis_form_index.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
freq_path = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / 'corpus_metrics' / 'diorisis_frequencies.json'
files = sorted(glob.glob(str(dio_dir / '*.xml')))
assert len(files) > 800, f'expected ~820 Diorisis XML files in {dio_dir}, found {len(files)}'

tokens = (read_stanza_tokens(HERE / 'data' / 'stanza_lemmas.csv')
          + read_stanza_tokens(HERE / 'data' / 'stanza_lemmas_comp1_translated.csv'))
need_full, need_bare = needed_keys(tokens)
need_full, need_bare = set(need_full), set(need_bare)
word_re = re.compile(r'<word form="([^"]*)"')
lemma_re = re.compile(r'<lemma [^>]*entry="([^"]*)"')
by_form, by_bare, lemma_total, memo = defaultdict(Counter), defaultdict(Counter), Counter(), {}
for path in files:
    form = None
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            m = word_re.search(line)
            if m:
                raw = m.group(1).replace('&quot;', '"').replace('&amp;', '&')
                form = memo.get(raw)
                if form is None:
                    form = memo[raw] = canon_beta(raw)
                continue
            m = lemma_re.search(line)
            if m and m.group(1):
                entry = m.group(1)
                lemma_total[entry] += 1
                if form is None:
                    continue
                if form in need_full:
                    by_form[form][entry] += 1
                b = bare(form)
                if b in need_bare:
                    by_bare[b][entry] += 1

ref = json.load(open(freq_path, encoding='utf-8'))
same = dict(lemma_total) == ref['frequencies'] and sum(lemma_total.values()) == ref['corpus_size']
print(f'{len(files)} files; {sum(lemma_total.values()):,} lemma tokens; {len(lemma_total):,} lemma types; '
      f'matches corpus_metrics/diorisis_frequencies.json: {same}')
out = {'about': 'Diorisis lemma counts for the word forms of data/stanza_lemmas.csv and '
                'data/stanza_lemmas_comp1_translated.csv, keyed by canonical '
                'Beta Code ("form") and by bare letters ("bare"). Built by optional/build_diorisis_form_index.py.',
       'diorisis_files': len(files),
       'form': {k: dict(sorted(v.items())) for k, v in sorted(by_form.items())},
       'bare': {k: dict(sorted(v.items())) for k, v in sorted(by_bare.items())}}
with open(out_path, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=0, sort_keys=True)
    fh.write('\n')
print(f"forms indexed: {len(out['form'])} (of {len(need_full)} needed); bare keys: {len(out['bare'])}")
frozen = HERE / 'data' / 'diorisis_form_index.json'
if out_path.resolve() != frozen.resolve():
    print('identical to data/diorisis_form_index.json:', out_path.read_bytes() == frozen.read_bytes())
