"""Score the 60 LLM translations with COMET-Kiwi, a reference-free metric (optional).

COMET-Kiwi (Unbabel/wmt22-cometkiwi-da) scores a translation against its source, with no
reference. This script scores each of the 60 translations against its Greek source and records,
beside the score, the token counts of the model's input window, how much of the source the window
holds, reference-based COMET (as in 20_table_metric_scores.py: Mix. the mean of its two
single-reference scores) and TQS. data/comet_kiwi_scores.csv holds the scores of the run described
in data/comet_kiwi_run_info.txt (unbabel-comet 2.2.7, CPU, batch size 8); this script repeats that
run and compares its results with the file.

The input window (unbabel-comet 2.2.7, UnifiedMetric): candidate and source are each tokenized
with XLM-R and capped at 510 tokens including their two special tokens, then joined as
<s> mt </s></s> src </s> and cut to the first 512 positions, so what is lost is the end of the
source. Inputs are NFC-normalised.

Setup, once:
    pip install "unbabel-comet==2.2.7"
    # accept the licence at https://huggingface.co/Unbabel/wmt22-cometkiwi-da (and at
    # https://huggingface.co/FacebookAI/xlm-roberta-large, which it pulls in), then:
    huggingface-cli login

Run:
    python analysis/optional/comet_kiwi.py --dry-run   # a few seconds, no model: checks inputs and wiring
    python analysis/optional/comet_kiwi.py             # CPU, deterministic, roughly 10-20 minutes

Outputs go to analysis/outputs_comet_kiwi/ (never to data/): comet_kiwi_scores.csv and run_info.txt.
"""
import argparse
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from common import DATA, KEYS, load_mqm, load_texts, load_translations, metric_scores  # noqa: E402

MODEL_NAME = 'Unbabel/wmt22-cometkiwi-da'
SEGMENT_MAX = 510        # per-segment cap, special tokens included
WINDOW = 512             # the joint window


def window(n_src, n_mt):
    """What the joint window keeps of a pair, from the token counts with special tokens (as the
    library computes it): (over the window, source content tokens kept, candidate truncated)."""
    src_content = n_src - 2
    hyp_eff, src_eff = min(n_mt, SEGMENT_MAX), min(n_src, SEGMENT_MAX)
    over = hyp_eff + src_eff > WINDOW
    kept = src_content if not over else max(0, min(src_content, WINDOW - (hyp_eff + 1)))
    return over, kept, n_mt > SEGMENT_MAX


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out', type=Path, default=HERE / 'outputs_comet_kiwi', help='output folder')
    ap.add_argument('--gpus', type=int, default=0, help='0 = CPU, deterministic (default)')
    ap.add_argument('--batch-size', type=int, default=8)
    ap.add_argument('--dry-run', action='store_true', help='placeholder scores; checks inputs and outputs only')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    texts, tr = load_texts(), load_translations()
    tqs = load_mqm().set_index(KEYS).TQS
    comet = metric_scores('mean').set_index(KEYS).COMET
    items = [{'text': t, 'chunk': c, 'model': m,
              'src': unicodedata.normalize('NFC', texts[t][c]['greek']),
              'mt': unicodedata.normalize('NFC', tr[(t, c, m)]['translation'])}
             for t in ('Mix', 'Comp') for c in range(1, 11) for m in ('ChatGPT', 'Claude', 'Gemini')]
    assert len(items) == 60 and all(i['src'].strip() and i['mt'].strip() for i in items)

    info = [f'model: {MODEL_NAME}', f'python: {sys.version.split()[0]}', f'gpus: {args.gpus}',
            f'batch size: {args.batch_size}']
    if args.dry_run:
        # NOT a metric: a stand-in so that the rest of the script can be exercised without the model
        scores = [0.5 + 0.2 * np.tanh((len(i['mt']) - len(i['src'])) / 500) for i in items]
        n_src = n_mt = [None] * len(items)
        info.append('DRY RUN: scores are placeholders, not COMET-Kiwi')
    else:
        import torch
        from comet import __version__ as comet_version, download_model, load_from_checkpoint
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True, warn_only=True)
        ckpt = download_model(MODEL_NAME)
        model = load_from_checkpoint(ckpt)
        model.eval()
        tok = model.encoder.tokenizer
        n_src = [len(tok(i['src'])['input_ids']) for i in items]
        n_mt = [len(tok(i['mt'])['input_ids']) for i in items]
        scores = list(model.predict([{'src': i['src'], 'mt': i['mt']} for i in items],
                                    batch_size=args.batch_size, gpus=args.gpus, progress_bar=True).scores)
        info += [f'unbabel-comet: {comet_version}', f'torch: {torch.__version__}', f'checkpoint: {ckpt}',
                 'unicode normalization: NFC (source and hypothesis)']

    df = pd.DataFrame({'text': [i['text'] for i in items], 'chunk': [i['chunk'] for i in items],
                       'model': [i['model'] for i in items],
                       'words_src': [len(i['src'].split()) for i in items], 'words_mt': [len(i['mt'].split()) for i in items],
                       'tokens_src': n_src, 'tokens_mt': n_mt, 'cometkiwi': scores,
                       'COMET (reference-based)': [comet[(i['text'], i['chunk'], i['model'])] for i in items],
                       'TQS': [tqs[(i['text'], i['chunk'], i['model'])] for i in items]})
    if not args.dry_run:
        w = [window(a, b) for a, b in zip(n_src, n_mt)]
        df['over_token_limit'] = [x[0] for x in w]
        df['src_tokens_kept'] = [x[1] for x in w]
        df['src_fraction_kept'] = df.src_tokens_kept / (df.tokens_src - 2)
        df['mt_truncated'] = [x[2] for x in w]
        info.append(f'token limit: {WINDOW}; pairs over it: {int(df.over_token_limit.sum())}; hypothesis truncated too: '
                    f'{int(df.mt_truncated.sum())}; mean fraction of source kept: {df.src_fraction_kept.mean():.3f}')
    df = df.sort_values(['text', 'chunk', 'model'], ascending=[False, True, True])
    df.to_csv(args.out / 'comet_kiwi_scores.csv', index=False, float_format='%.6f', lineterminator='\n')
    (args.out / 'run_info.txt').write_text('\n'.join(info) + '\n', encoding='utf-8')

    # the frozen run
    frozen = pd.read_csv(DATA / 'comet_kiwi_scores.csv')
    new = pd.read_csv(args.out / 'comet_kiwi_scores.csv')
    assert list(frozen[['text', 'chunk', 'model']].itertuples(index=False)) == list(new[['text', 'chunk', 'model']].itertuples(index=False))
    same = ['words_src', 'words_mt', 'COMET (reference-based)', 'TQS']
    if not args.dry_run:
        same += ['tokens_src', 'tokens_mt', 'over_token_limit', 'src_tokens_kept', 'src_fraction_kept', 'mt_truncated']
    for c in same:        # floats to the file's six decimals (reference-based COMET: the scores are exported rounded)
        ok = np.allclose(frozen[c], new[c], atol=1.5e-6, rtol=0) if frozen[c].dtype == float else (frozen[c] == new[c]).all()
        print(f'{c:24} {"same as" if ok else "DIFFERENT FROM"} data/comet_kiwi_scores.csv')
    if not args.dry_run:
        d = (frozen.cometkiwi - new.cometkiwi).abs().max()
        print(f'{"cometkiwi":24} largest difference from data/comet_kiwi_scores.csv: {d:.2e}')
    print(f'written to {args.out}' + ('  (DRY RUN: placeholder scores)' if args.dry_run else ''))


if __name__ == '__main__':
    main()
