"""The tables and the figure of the paper: their numbers, the script that computes each, and the
file each is written to.

A table's file is named after its number (Table 4 -> outputs/table_4.csv, Table SM3 ->
outputs/table_SM3.csv), so a reader finds it under the number the paper gives it. The numbers are
set here; scripts refer to a table by its name (the keys below), and each table script's docstring
repeats its number and file names, which 99_index.py checks against this list.
"""
from common import write_csv

TABLES = {
    # name: (number, script, contents)
    'metric_aggregate': ('Table 1', '20_table_metric_scores.py',
                         'automated metric scores by text and model: mean (SD) x 100'),
    'mqm_aggregate': ('Table 2', '21_table_mqm_scores.py',
                      'MQM translation quality score (TQS) by text and model: mean, SD, critical errors'),
    'mqm_stratified': ('Table 3', '22_table_mqm_by_stratum.py',
                       'TQS of Mix. and of Comp. with passages excluded, and the Mix.-Comp. gap'),
    'metric_gap_stratified': ('Table 4', '23_table_metric_gap.py',
                              'Mix.-Comp. gap on each automated metric, with passages excluded; Welch t-test'),
    'metric_tqs_correlations': ('Table 5', '24_table_metric_correlations.py',
                                'correlation of each automated metric with TQS, all 60 translations'),
    'ratings_by_model': ('Table 6', '25_table_ratings_by_model.py',
                         'quality ratings (Schemes 1 and 2) by text and model'),
    'ratings_stratified': ('Table 7', '26_table_ratings_by_stratum.py',
                           'pass rates of Mix. and of Comp. with passages excluded'),
    'error_typology': ('Table 8', '27_table_error_types.py',
                       'MQM errors by severity and type, Mix. and Comp.'),
    'rarity_correlations': ('Table 9', '28_table_rarity_correlations.py',
                            'correlation of passage rarity with passage quality'),
    'metric_tqs_correlations_by_text': ('Table 10', '29_table_correlations_by_text.py',
                                        'correlation of each automated metric with TQS, by text'),
    'tqs_heatmap': ('Figure 1', '30_figure_tqs.py',
                    'TQS of each of the 60 translations (the data of the figure)'),
    'dataset': ('Table SM1', '31_table_dataset.py',
                'the 20 passages: location in the editions and length in words'),
    'mix_reference_protocols': ('Table SM2', '32_table_reference_protocols.py',
                                'automated metric scores of Mix. under four ways of using its two references'),
    'metric_input_limits': ('Table SM3', '33_table_input_limits.py',
                            'input length limit of each automated metric and how much of each passage it reads'),
    'metric_scores_all60': ('Table SM4', '34_table_metric_scores_all.py',
                            'BLEU-4, BERTScore, COMET, TQS and rating of each of the 60 translations'),
    'mqm_all60': ('Table SM5', '35_table_mqm_scores_all.py',
                  'TQS, rating and errors by severity of each of the 60 translations'),
    'reference_preferences': ('Table SM6', '36_table_reference_preferences.py',
                              'for each metric, how many Mix. translations score higher against each reference'),
    'rarity_by_passage': ('Table SM7', '37_table_rarity_by_passage.py',
                          'rarity of the vocabulary of each passage'),
}


def label(name):
    return TABLES[name][0]


def filename(name, suffix=''):
    """'Table SM4' -> 'table_SM4.csv', 'Figure 1' -> 'figure_1.csv'."""
    kind, num = label(name).split(' ')
    return f'{kind.lower()}_{num}{suffix}.csv'


def write_table(name, df, values=None):
    """Write a table exactly as printed (every cell as it appears in the paper) and, if given,
    the values behind its numbers before rounding (a CellValues) next to it."""
    write_csv(df, filename(name))
    if values is not None:
        write_csv(values.frame(), filename(name, '_values'))
