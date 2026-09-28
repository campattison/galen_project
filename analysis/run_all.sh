#!/usr/bin/env bash
# Regenerate every output in analysis/outputs/, in order: the supporting analyses (01-11), the
# tables and the figure (20-37), then the index (99).
# Usage (from anywhere):  bash analysis/run_all.sh
# Uses $PYTHON if set (e.g. PYTHON=.venv/bin/python), otherwise python3. Takes under a minute.
set -euo pipefail
PY="${PYTHON:-python3}"
case "$PY" in */*) PY="$(cd "$(dirname "$PY")" && pwd)/$(basename "$PY")" ;; esac
cd "$(dirname "$0")"
for s in [0-9][0-9]_*.py; do
    echo "== $s"
    "$PY" "$s" > /dev/null
done
echo "Done. Outputs are in $(pwd)/outputs (see outputs/INDEX.md). Check them with: $PY $(pwd)/verify.py"
