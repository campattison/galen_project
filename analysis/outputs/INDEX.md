# Index of the outputs

Every file in this folder, and the script in `analysis/` that writes it. `run_all.sh` runs the scripts in numerical order; each script reads the data and, where its docstring says so, the outputs of scripts that run before it.

## Tables and figure

| Table | Contents | Script | Files |
|---|---|---|---|
| Table 1 | automated metric scores by text and model: mean (SD) x 100 | `20_table_metric_scores.py` | `table_1.csv`, `table_1_values.csv`, `statistics_20_table_metric_scores.csv` |
| Table 2 | MQM translation quality score (TQS) by text and model: mean, SD, critical errors | `21_table_mqm_scores.py` | `table_2.csv`, `table_2_values.csv`, `statistics_21_table_mqm_scores.csv` |
| Table 3 | TQS of Mix. and of Comp. with passages excluded, and the Mix.-Comp. gap | `22_table_mqm_by_stratum.py` | `table_3.csv`, `table_3_values.csv` |
| Table 4 | Mix.-Comp. gap on each automated metric, with passages excluded; Welch t-test | `23_table_metric_gap.py` | `table_4.csv`, `table_4_values.csv`, `statistics_23_table_metric_gap.csv` |
| Table 5 | correlation of each automated metric with TQS, all 60 translations | `24_table_metric_correlations.py` | `table_5.csv`, `table_5_values.csv`, `statistics_24_table_metric_correlations.csv` |
| Table 6 | quality ratings (Schemes 1 and 2) by text and model | `25_table_ratings_by_model.py` | `table_6.csv`, `table_6_values.csv`, `statistics_25_table_ratings_by_model.csv` |
| Table 7 | pass rates of Mix. and of Comp. with passages excluded | `26_table_ratings_by_stratum.py` | `table_7.csv`, `table_7_values.csv` |
| Table 8 | MQM errors by severity and type, Mix. and Comp. | `27_table_error_types.py` | `table_8.csv`, `table_8_values.csv`, `statistics_27_table_error_types.csv` |
| Table 9 | correlation of passage rarity with passage quality | `28_table_rarity_correlations.py` | `table_9.csv`, `table_9_values.csv` |
| Table 10 | correlation of each automated metric with TQS, by text | `29_table_correlations_by_text.py` | `table_10.csv`, `table_10_values.csv`, `statistics_29_table_correlations_by_text.csv` |
| Figure 1 | TQS of each of the 60 translations (the data of the figure) | `30_figure_tqs.py` | `figure_1.csv`, `statistics_30_figure_tqs.csv` |
| Table SM1 | the 20 passages: location in the editions and length in words | `31_table_dataset.py` | `table_SM1.csv`, `table_SM1_values.csv`, `statistics_31_table_dataset.csv` |
| Table SM2 | automated metric scores of Mix. under four ways of using its two references | `32_table_reference_protocols.py` | `table_SM2.csv`, `table_SM2_values.csv`, `correlations_by_protocol.csv`, `statistics_32_table_reference_protocols.csv` |
| Table SM3 | input length limit of each automated metric and how much of each passage it reads | `33_table_input_limits.py` | `table_SM3.csv`, `cometkiwi_summary.csv`, `statistics_33_table_input_limits.csv` |
| Table SM4 | BLEU-4, BERTScore, COMET, TQS and rating of each of the 60 translations | `34_table_metric_scores_all.py` | `table_SM4.csv`, `table_SM4_values.csv`, `per_translation_scores.csv` |
| Table SM5 | TQS, rating and errors by severity of each of the 60 translations | `35_table_mqm_scores_all.py` | `table_SM5.csv` |
| Table SM6 | for each metric, how many Mix. translations score higher against each reference | `36_table_reference_preferences.py` | `table_SM6.csv`, `table_SM6_values.csv`, `statistics_36_table_reference_preferences.csv` |
| Table SM7 | rarity of the vocabulary of each passage | `37_table_rarity_by_passage.py` | `table_SM7.csv`, `table_SM7_values.csv` |

## Supporting analyses

| Script | What it does | Files |
|---|---|---|
| `01_reference_asymmetry.py` | Two references for Mix., one for Comp.: how Mix. is scored, and what it does to the gap. | `like_for_like_gaps.csv`, `multi_reference_boost.csv`, `mix_per_reference_scores.csv`, `mix_reference_fix.csv`, `statistics_01_reference_asymmetry.csv` |
| `02_surface_similarity.py` | Surface similarity of the LLM translations to the published English translations. | `surface_similarity_by_passage.csv`, `surface_similarity_by_model.csv`, `verbatim_runs.csv`, `statistics_02_surface_similarity.csv` |
| `03_error_composition.py` | Error composition: terminology vs accuracy errors, by group of passages. | `error_composition.csv`, `critical_errors_by_passage.csv`, `statistics_03_error_composition.csv` |
| `04_tqs_thresholds.py` | The TQS rating thresholds: error budgets, and sensitivity to severity weights and cut-offs. | `tqs_error_budget.csv`, `tqs_error_budget_by_severity.csv`, `pass_rates_by_cutoff.csv`, `band_composition.csv`, `severity_weight_sensitivity.csv`, `statistics_04_tqs_thresholds.csv` |
| `05_model_comparisons.py` | Differences between the three models. | `model_tests.csv`, `scheme2_outcomes_comp.csv`, `statistics_05_model_comparisons.csv` |
| `06_generation_metadata.py` | How the translations were generated: dates, attempts, model versions and API parameters. | `generation_metadata.csv`, `api_call_parameters.csv`, `statistics_06_generation_metadata.csv` |
| `07_rarity_measure.py` | The rarity measure, rebuilt and corrected in documented steps from Stanza's output. | `rarity_tokens.csv`, `rarity_by_passage_steps.csv`, `rarity_by_passage_final.csv`, `original_measure_reproduction_check.csv`, `rarity_correction_summary.csv`, `statistics_07_rarity_measure.csv` |
| `08_rarity_stats.py` | Rarity and translation quality. | `rarity_stats_by_step.csv`, `rarity_correlations_by_step.csv`, `rarity_quality_by_passage.csv`, `rarity_vs_error_type.csv`, `notation_check.csv`, `statistics_08_rarity_stats.csv` |
| `09_lemma_check.py` | Hand check of a sample of the repaired lemmas. | `lemma_check_summary.csv`, `statistics_09_lemma_check.csv` |
| `10_rarity_sensitivity.py` | How much could remaining lemma errors move the rarity result? | `rarity_sensitivity.csv`, `statistics_10_rarity_sensitivity.csv` |
| `11_quality_by_group.py` | Translation quality of groups of translations. | `quality_by_group.csv`, `statistics_11_quality_by_group.csv` |
| `99_index.py` | Index of the outputs: which script writes each file (runs last). | `INDEX.md` |

A `_values.csv` file holds the value behind each number in the table beside it, to six decimals (row, column, statistic, value). A `statistics_<script>.csv` file holds the other quantities a script reports (key, value, description). Numbers are written with six decimals, so a p-value below 5e-7 appears as 0.000000.
