"""99 Index of the outputs: which script writes each file (runs last).

Reads the docstring of every script (its first line and its "Outputs" list) and writes
outputs/INDEX.md: the tables and the figure, in the order of tables.py, with the script and the
files of each, then the supporting analyses. It also checks that the index is complete: every
file in outputs/ is listed by exactly one script, every listed file exists, and each table
script names its table as tables.py numbers it.

Inputs : the scripts in this folder, tables.py
Outputs: INDEX.md
"""
import ast
import re
from pathlib import Path

from common import OUT, load_texts, mix_references_present, write_text
from tables import TABLES, filename, label

HERE = Path(__file__).resolve().parent
FILE = re.compile(r'\b[\w\-]+\.(?:csv|md)\b')


def docstring(script):
    return ast.get_docstring(ast.parse((HERE / script).read_text(encoding='utf-8')))


def outputs(doc):
    part = doc.split('Outputs:', 1)[1]
    return FILE.findall(part)


scripts = sorted(p.name for p in HERE.glob('[0-9][0-9]_*.py'))
listed = {}
for s in scripts:
    for f in outputs(docstring(s)):
        assert f not in listed, f'{f} is listed by {listed[f]} and {s}'
        listed[f] = s
present = {p.name for p in OUT.iterdir() if p.is_file()} | {'INDEX.md'}
if not mix_references_present(load_texts()):   # 02 cannot rerun without the Mix. references: its saved outputs stand
    present |= {f for f, s in listed.items() if s == '02_surface_similarity.py' and (HERE / 'outputs' / f).is_file()}
assert set(listed) == present, (sorted(set(listed) - present), sorted(present - set(listed)))

lines = ['# Index of the outputs', '',
         'Every file in this folder, and the script in `analysis/` that writes it. `run_all.sh` runs the '
         'scripts in numerical order; each script reads the data and, where its docstring says so, the '
         'outputs of scripts that run before it.', '',
         '## Tables and figure', '',
         '| Table | Contents | Script | Files |', '|---|---|---|---|']
for name, (number, script, contents) in TABLES.items():
    first = docstring(script).splitlines()[0]
    assert first.startswith(f'{script[:2]} {number}:') or first.startswith(f'{script[:2]} {number} (data):'), (script, first)
    files = [f for f, s in listed.items() if s == script]
    assert filename(name) in files, (script, filename(name))
    lines.append(f'| {label(name)} | {contents} | `{script}` | ' + ', '.join(f'`{f}`' for f in files) + ' |')
lines += ['', '## Supporting analyses', '', '| Script | What it does | Files |', '|---|---|---|']
table_scripts = {script for _, script, _ in TABLES.values()}
for s in scripts:
    if s in table_scripts:
        continue
    first = docstring(s).splitlines()[0]
    what = first.split(' ', 1)[1]
    files = [f for f, sc in listed.items() if sc == s]
    lines.append(f'| `{s}` | {what} | ' + ', '.join(f'`{f}`' for f in files) + ' |')
lines += ['', 'A `_values.csv` file holds the value behind each number in the table beside it, to six decimals '
          '(row, column, statistic, value). A `statistics_<script>.csv` file holds the other quantities a script '
          'reports (key, value, description). Numbers are written with six decimals, so a p-value below 5e-7 '
          'appears as 0.000000.']
write_text(lines, 'INDEX.md')
print('\n'.join(lines))
