"""Rerun every script into a scratch folder and compare the results with the committed outputs.

    python analysis/verify.py

Prints one line per output file and exits with status 1 if anything differs. Files must be
byte-identical, except that numbers may differ in the sixth decimal (floating-point differences
between machines); any such case is reported as "numeric match".

The saved files that need the reference English of Mix. (the outputs of 02_surface_similarity.py, and
the token counts in data/ that optional/token_counts.py makes from the same texts) are also checked
against the SHA-256 checksums below on every run ("checksum"): run_all.sh rewrites the outputs of 02,
so a rebuilt on_mixtures.txt whose English is not the English used would otherwise pass. The English is
not distributed (mt_eval/input/REFERENCES.md); without it, 02 writes nothing and its outputs are not
recomputed.
"""
import csv
import hashlib
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = sorted(p.name for p in HERE.glob('[0-9][0-9]_*.py'))
SAVED_WITHOUT_REFERENCES = {   # SHA-256 of the saved files that need the reference English of Mix.
    'outputs/surface_similarity_by_passage.csv': 'd90409b4e7ea1d23f6a865c93e437c1c2fcacbd24ce51c47a16bcc08054268cd',
    'outputs/surface_similarity_by_model.csv': '3753edc2d0b4576c6bc75502501ee7c8d2f7ca9d454e69a4035d49e1bd5e6170',
    'outputs/verbatim_runs.csv': 'd9cfb31ea2bc75b14cc705d52a25172ef776d10977faad99f34ae29068a85d89',
    'outputs/statistics_02_surface_similarity.csv': 'd364e3ef17a7b51a10961c0de037b57c26460ce104899bc3ce7ddcd985873847',
    'data/token_counts_passages.csv': '699a66126e05c5fec03a2121fe38caefae1b02517d7774f24245da747344395c',
    'data/token_counts_pairs.csv': '880db9bacf2b2f0f8ae82e55113fd4b3fac76b3b6ef9c9d1a68e161e9acdb407',
}


def cells_match(a, b, tol=2e-6):
    if a == b:
        return True
    try:
        return abs(float(a) - float(b)) <= tol
    except ValueError:
        return False


def numeric_match(x, y):
    if x.endswith('.csv'):
        A = list(csv.reader(io.StringIO(Path(x).read_text(encoding='utf-8'))))
        B = list(csv.reader(io.StringIO(Path(y).read_text(encoding='utf-8'))))
    else:
        A = [line.split() for line in Path(x).read_text(encoding='utf-8').splitlines()]
        B = [line.split() for line in Path(y).read_text(encoding='utf-8').splitlines()]
    if len(A) != len(B):
        return False
    return all(len(ra) == len(rb) and all(cells_match(u.strip(',"'), v.strip(',"')) for u, v in zip(ra, rb))
               for ra, rb in zip(A, B))


sys.path.insert(0, str(HERE))
from common import load_texts, mix_references_present  # noqa: E402

REFERENCES = mix_references_present(load_texts())
CHECKED = set() if REFERENCES else {Path(k).name for k in SAVED_WITHOUT_REFERENCES if k.startswith('outputs/')}

with tempfile.TemporaryDirectory() as tmp:
    env = dict(os.environ, ANALYSIS_OUT=tmp)
    for s in SCRIPTS:
        r = subprocess.run([sys.executable, str(HERE / s)], cwd=HERE, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            print(f'FAILED to run {s}:\n{r.stderr}')
            sys.exit(1)
    committed = {p.name for p in (HERE / 'outputs').iterdir() if p.is_file()}
    fresh = {p.name for p in Path(tmp).iterdir() if p.is_file()}
    bad = 0
    for name in sorted((committed | fresh) - CHECKED):
        if name not in fresh or name not in committed:
            print(f'MISSING   {name} ({"not regenerated" if name not in fresh else "not committed"})')
            bad += 1
            continue
        a, b = (HERE / 'outputs' / name).read_bytes(), (Path(tmp) / name).read_bytes()
        if a == b:
            print(f'identical {name}')
        elif numeric_match(str(HERE / 'outputs' / name), str(Path(tmp) / name)):
            print(f'numeric match (within 2e-6) {name}')
        else:
            print(f'DIFFERENT {name}')
            bad += 1
    for rel, digest in SAVED_WITHOUT_REFERENCES.items():     # on every run, with or without the English
        if not (HERE / rel).is_file():
            print(f'MISSING   {rel}')
            bad += 1
        elif hashlib.sha256((HERE / rel).read_bytes()).hexdigest() == digest:
            print(f'checksum  {rel}' + ('' if REFERENCES else ' (saved; the reference English of Mix. is not distributed)'))
        else:
            print(f'DIFFERENT {rel} (not the stored SHA-256' + (
                '; if run_all.sh rewrote it from a rebuilt on_mixtures.txt, that English is not the English used: '
                'check the file with mt_eval/input/check_references.py)' if REFERENCES else ')'))
            bad += 1
    print(f'\n{len(fresh)} files regenerated; {len(SAVED_WITHOUT_REFERENCES)} saved files checked against their '
          f'SHA-256; {bad} problem(s).')
    print('PASS' if bad == 0 else 'FAIL')
    sys.exit(1 if bad else 0)
