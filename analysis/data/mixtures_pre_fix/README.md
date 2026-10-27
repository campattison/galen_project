# The Mix. input file before the reference fix

`mt_eval/input/on_mixtures.txt` gives, for each Mix. passage, the Greek text and its two reference
translations (Johnston; Singer and van der Eijk), separated by blank lines. In the version of the
file used for the first evaluation, the blank line between the two translations of passages 2 and 4
was missing. The parser then read each pair as one block, and its heuristic for splitting a long
merged block (`InputParser._try_split_combined_references`) split it at a sentence one sentence away
from the true boundary, so every automated score of Mix. 2 and 4 was computed against slightly wrong
references. The two blank lines were restored and the evaluation was run again.

| File | What it is |
|---|---|
| `on_mixtures.txt` | the input file before the fix (sha256 `07af3ce6…`) |
| `on_mixtures_evaluation.json` | the evaluation file computed from it (sha256 `cb2c8ddf…`) |

The corrected input is `mt_eval/input/on_mixtures.txt` (sha256 `5e6c7c7a…`); `diff -B` between the two
files is empty, i.e. the two blank lines are the whole of the change. The scores of the new evaluation
are in `../mt_eval_scores.csv` and `../mt_eval_scores_per_reference.csv`; `common.load_eval` applies
them and checks that nothing outside Mix. 2 and 4 changes. The evaluation file in the pipeline's output
folder, `mt_eval/output/evaluations/on_mixtures_evaluation.json`, is the one computed after the fix;
`common.load_eval` checks it against the scores in `../mt_eval_scores.csv` and
`../mt_eval_scores_per_reference.csv`.

The English of both input files is not distributed: in this repository each reference paragraph is a
pointer to `mt_eval/input/REFERENCES.md`, which says how to put the translations back. The sha256 values
above are those of the files with the English.

## What changed

`01_reference_asymmetry.py` lists every Mix. score before and after the fix
(`outputs/mix_reference_fix.csv`). In Mix. 2 and 4, 41 of the 42 multi-reference scores (7 metrics ×
6 translations) and 78 of the 84 single-reference scores changed; the exceptions are BLEURT against
Johnston (all six translations) and BLEURT's multi-reference score of one translation, which keeps the
Johnston score. BLEURT reads only the beginning of a long pair of texts, and the part of the Johnston
reference it reads was the same before and after the fix. Everywhere else the scores agree within
1e-6 (the new scores are exported with six decimals).
