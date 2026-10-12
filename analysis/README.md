# Analyses: from the data to the tables

This folder computes, from the data in this repository, every table and figure of the paper and the
other statistics the paper reports from these data (counts made by hand from the annotations are not
computed here). It contains:

- the analysis scripts, one per question (`01`–`11`), and one script per table or figure (`20`–`37`);
- `data/`, the frozen inputs that are not part of the translation pipeline (see `data/README.md`);
- `outputs/`, everything the scripts write, committed so that it can be read without running anything.

To find out how the numbers in a table were produced, look the table up in `outputs/INDEX.md`: it names
the script that writes it and the files it writes. The script is short, reads the data directly (the MQM
sheets in `mqm/`, the scores in `mt_eval/output/evaluations/`, the texts in `mt_eval/input/`) or, where its
docstring says so, the output of a script that runs before it, and prints the table when run on its own.

## Run and check

Python 3.10 or later:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r analysis/requirements.txt
bash analysis/run_all.sh        # regenerates outputs/ (under a minute)
python analysis/verify.py       # reruns everything into a scratch folder and compares with outputs/
```

`verify.py` should end with `PASS`. The scripts read only files in this repository, use no network and fix
every random seed, so the outputs are the same on every run (on another machine, floating-point arithmetic
can differ in the sixth decimal, which `verify.py` allows and reports). A single script can be run on its
own (`python analysis/23_table_metric_gap.py`), once the scripts it reads from have run.

## What the scripts write

| File | Contents |
|---|---|
| `table_<n>.csv`, `figure_1.csv` | the table as printed: every cell as it appears in the paper |
| `table_<n>_values.csv` | the value behind each number in the table, before the table rounds it (`row`, `column`, `statistic`, `value`), and for the Mix.–Comp. gap table also the Welch p, Cohen's d and means behind each gap |
| `statistics_<script>.csv` | the other quantities a script reports (`key`, `value`, `description`): counts, ranges, differences, test results |
| other `.csv` files | the intermediate tables of each analysis, listed in `outputs/INDEX.md` |

Numbers are written with six decimals (so a p-value below 5e-7 appears as 0.000000); percentages and
scores "x 100" are on the scale the tables use. Table numbers are set in `tables.py`, which also names each
table's file.

## The scripts

| Scripts | What they do |
|---|---|
| `01_reference_asymmetry.py` | Mix. has two references and Comp. one: scores Mix. against each reference and as the mean of the two, and recomputes the Mix.–Comp. gap under each way of scoring |
| `02_surface_similarity.py` | how close the LLM translations are to the published English translations (sentence BLEU; longest shared runs of words) |
| `03_error_composition.py` | terminology and accuracy errors by group of passages |
| `04_tqs_thresholds.py` | what the TQS rating thresholds mean in errors per translation |
| `05_model_comparisons.py` | differences between the three models (Friedman, Wilcoxon, Brown–Forsythe) |
| `06_generation_metadata.py` | how the translations were generated: dates, attempts, model versions, API parameters |
| `07_rarity_measure.py` – `10_rarity_sensitivity.py` | the rarity measure of each passage's vocabulary, rebuilt step by step from Stanza's output (07); its correlation with translation quality (08); the hand check of the repaired lemmas (09); how far remaining lemma errors could move the result (10) |
| `11_quality_by_group.py` | TQS and pass rates of groups of translations (each text; Comp. 8 and 10 against the other Comp. passages; Comp. without 3, 8 and 10) |
| `20_…py` – `37_…py` | one script per table or figure; `outputs/INDEX.md` lists them with their tables |
| `99_index.py` | writes `outputs/INDEX.md` and checks that every output file is accounted for |

`common.py` holds what the scripts share: the loaders of the MQM sheets, the metric scores and the texts,
the statistical tests and the number formats. `greek.py` and `rarity.py` hold the rules of the rarity measure.

## Conventions

- **Mix. and its two references.** Every metric scores a translation against one reference at a time; a Mix.
  translation's score is the mean of its scores against Johnston and against Singer and van der Eijk, so
  that Mix. and Comp. (one reference) are scored alike (`common.metric_scores`). The pipeline's
  multi-reference scores (BLEU-4 pooled over both references; for the other metrics the higher of the two
  single-reference scores) are kept for comparison (`32_table_reference_protocols.py`).
- **Automated scores** are those of the evaluation files in `mt_eval/output/evaluations/`, with Mix. 2 and 4
  rescored after a fix to the input file (see `data/mixtures_pre_fix/README.md`; `common.load_eval`).
- **TQS** is the value printed in the MQM summary sheets in `mqm/`; `common.load_mqm` recomputes it from the
  error counts (TQS = 100 − (minor + 5 × major + 25 × critical) / words × 100, floored at 0, where words is the
  word count of the translation) and checks every value.
  Ratings: Scheme 1 from TQS alone (HIGH PASS from 95, LOW PASS from 87, FAIL below); Scheme 2 is FAIL for
  any translation with a critical error.
- **Passage subsets.** Comparisons of Mix. with Comp. exclude Comp. passages only (8 and 10; 3, 8 and 10; for
  TQS also 8, 10 and ChatGPT's translation of 3); Mix. is always kept whole.

## Optional scripts

`optional/` holds scripts that regenerate frozen inputs or draw the figure. They need software or data that
`run_all.sh` does not (listed in `requirements.txt`) and write only to `outputs/optional/` or
`outputs_comet_kiwi/`, never to `data/`:

- `regenerate_stanza_lemmas.py` reruns Stanza 1.11.0 and compares with the frozen Stanza output;
- `build_diorisis_form_index.py` rebuilds the Diorisis form index from the corpus;
- `comet_kiwi.py` rescores the translations with COMET-Kiwi and compares with the frozen scores;
- `token_counts.py` recounts the texts with each metric's tokenizer and compares with the frozen token counts;
- `render_figure1.py` draws Figure 1 from `outputs/figure_1.csv`.
