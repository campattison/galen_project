"""Rerun every script into a scratch folder and compare the results with the committed outputs.

    python analysis/verify.py

Prints one line per output file and exits with status 1 if anything differs. Files must be
byte-identical, except that numbers may differ in the sixth decimal (floating-point differences
between machines); any such case is reported as "numeric match".
"""
import csv
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = sorted(p.name for p in HERE.glob('[0-9][0-9]_*.py'))


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
    for name in sorted(committed | fresh):
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
    print(f'\n{len(fresh)} files regenerated; {bad} problem(s).')
    print('PASS' if bad == 0 else 'FAIL')
    sys.exit(1 if bad else 0)
