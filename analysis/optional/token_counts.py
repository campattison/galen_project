"""Count every text under each metric's tokenizer and what each metric keeps of it (optional).

Per-passage and per-pair token counts for the 20 Greek sources, 60 translations and 30 references,
under every tokenizer the automated metrics actually use, plus per-metric survival (what fraction of
each text the metric saw after its own truncation mechanism). data/token_counts_passages.csv and
data/token_counts_pairs.csv hold the counts used by 33_table_input_limits.py; this script rebuilds
them from mt_eval/input/*.txt (via mt_eval/src/parser.py) and the translation JSONs in
mt_eval/output/translations/, and compares its files with them byte for byte.

Tokenizer paths reproduced (each verified against the installed library source):
  XLM-R   XLMRobertaTokenizerFast("xlm-roberta-large"), text NFC-normalised (as the COMET-Kiwi token
          accounting of comet_kiwi.py does). `xlmr_tokens_with_specials` = len(input_ids)
          incl. <s> </s>; `xlmr_tokens` = that minus 2.
  RoBERTa bert_score.utils.get_tokenizer("roberta-large", use_fast=False) -> slow RobertaTokenizer;
          tok.encode(text.strip(), add_special_tokens=True, add_prefix_space=True, truncation=False) minus 2
          (bert_score.utils.sent_encode without its max_length cap). No unicode normalisation (bert-score does none).
  BLEURT  sentencepiece EncodeAsPieces(text) with BLEURT-20/sent_piece.model, raw text, no strip, no normalisation
          (bleurt.lib.tokenizers.SentencePieceTokenizer.tokenize).

Survival mechanisms (all from library source: unbabel-comet 2.2.7, bert-score 0.3.12, bleurt 0.0.2):
  COMET (wmt22-comet-da, RegressionMetric): src, mt, ref tokenized SEPARATELY, each with
          truncation=True, max_length=max_positions-2 = 510 tokens INCLUDING that segment's <s></s>
          (comet/models/regression/regression_metric.py:201-203 -> comet/encoders/base.py:218-224)
          -> at most 508 content tokens per segment. Computed here by calling the tokenizer with that
          truncation, not by formula. comet_*_kept_frac = kept content / content.
  COMET-Kiwi (wmt22-cometkiwi-da, UnifiedMetric): mt and src each capped as above, then joined
          <s> mt </s></s> src </s> and hard-cut to 512 (comet/encoders/base.py:296-312)
          -> src content kept = 512 - (min(hyp_ws,510) + 1) (identical to `window` in comet_kiwi.py).
  BERTScore (roberta-large): each side independently truncated to model_max_length 512 incl. specials
          -> 510 content tokens per side.
  BLEURT-20: reference and candidate pieces balanced by encoding._truncate_seq_pair to 509 = 512 - 3
          (bleurt/encoding.py:45-54): pop from the end of the longer side (candidate on ties) until
          ref + cand <= 509.

Setup, once:
    pip install "transformers==4.57.6" "bert-score==0.3.12" "sentencepiece==0.2.1"
    # (with them: tokenizers 0.22.2, torch 2.10.0 CPU; run with Python 3.13.11)
    # the xlm-roberta-large and roberta-large tokenizers must be in the Hugging Face cache; the
    # script runs offline (HF_HUB_OFFLINE=1 unless set), so fetch them once, e.g.
    HF_HUB_OFFLINE=0 python -c "from transformers import AutoTokenizer as A; A.from_pretrained('xlm-roberta-large'); A.from_pretrained('roberta-large')"
    # the BLEURT-20 SentencePiece model: unzip https://storage.googleapis.com/bleurt-oss-21/BLEURT-20.zip
    # into mt_eval/models/ (or set BLEURT_SENTPIECE to its sent_piece.model; bleurt_config.json is
    # read from the same folder)

Run:
    python analysis/optional/token_counts.py    # a few seconds

Outputs go to analysis/outputs/optional/ (never to data/): token_counts_passages.csv and
token_counts_pairs.csv. Exit status 0 only if both are byte-identical to the files in data/.

The reference English of Mix. is not distributed (mt_eval/input/REFERENCES.md). Without it the script
prints a line beginning SKIPPED: and exits 0 without counting; the files in data/ stand, and verify.py
checks their checksums. A partly rebuilt on_mixtures.txt stops it with an error naming the passages.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import sys
import unicodedata
import warnings
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent.parent          # analysis/
REPO = Path(os.environ.get("GALEN_REPO") or Path(__file__).resolve().parents[2])
MT = REPO / "mt_eval"
DATA = HERE / "data"
BLEURT_SENTPIECE = Path(os.environ.get("BLEURT_SENTPIECE") or MT / "models" / "BLEURT-20" / "sent_piece.model")

TEXTS = [("Mix", "on_mixtures", ["Johnston", "Singer"]), ("Comp", "on_comp", ["Marai"])]
MODELS = [("openai", "ChatGPT"), ("claude", "Claude"), ("gemini", "Gemini")]
MAX_POS = 512                 # XLM-R / RoBERTa positions
COMET_SEG_MAX = MAX_POS - 2   # 510 incl. the segment's own <s> </s> (comet/encoders/base.py prepare_sample)
BERT_CONTENT_CAP = MAX_POS - 2  # 510 content tokens per side (bert_score sent_encode, max_length=512 incl. specials)
FILES = ["token_counts_passages.csv", "token_counts_pairs.csv"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def compare(fresh, frozen):
    """Byte comparison; on a difference, print the differing cells."""
    if fresh.read_bytes() == frozen.read_bytes():
        print(f"{fresh.name}: byte-identical to data/{frozen.name}")
        return True
    a = list(csv.reader(open(frozen, encoding="utf-8", newline="")))
    b = list(csv.reader(open(fresh, encoding="utf-8", newline="")))
    print(f"{fresh.name}: DIFFERENT FROM data/{frozen.name} ({len(b)} vs {len(a)} lines)")
    n = 0
    for i, (ra, rb) in enumerate(zip(a, b)):
        for j, (x, y) in enumerate(zip(ra, rb)):
            if x != y and n < 50:
                n += 1
                print(f"  line {i + 1}, column {a[0][j] if j < len(a[0]) else j}: data {x!r} | now {y!r}")
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=HERE / "outputs" / "optional", help="output folder")
    args = ap.parse_args()

    sys.path.insert(0, str(MT / "src"))
    import logging
    logging.disable(logging.CRITICAL)
    from parser import REFERENCES_NOT_DISTRIBUTED, InputParser, references_missing

    try:
        if references_missing(InputParser().parse_file(str(MT / "input" / "on_mixtures.txt")), "on_mixtures.txt"):
            print(REFERENCES_NOT_DISTRIBUTED.format(name="on_mixtures.txt"))
            sys.exit(0)
    except ValueError as e:
        sys.exit(str(e))

    if not BLEURT_SENTPIECE.is_file():
        sys.exit(f"BLEURT-20 SentencePiece model not found at {BLEURT_SENTPIECE}.\n"
                 "Download https://storage.googleapis.com/bleurt-oss-21/BLEURT-20.zip, unzip it into "
                 "mt_eval/models/, or set BLEURT_SENTPIECE to the path of its sent_piece.model.")

    # --- tokenizers -----------------------------------------------------------------------------
    import bert_score
    import sentencepiece as spm
    import transformers
    from bert_score.utils import get_tokenizer
    from transformers import RobertaTokenizer, XLMRobertaTokenizerFast

    xlmr = XLMRobertaTokenizerFast.from_pretrained("xlm-roberta-large", local_files_only=True)
    assert xlmr.model_max_length == 512 and xlmr.vocab_size == 250002, (xlmr.model_max_length, xlmr.vocab_size)
    rob = get_tokenizer("roberta-large", False)  # bert_score.score default use_fast_tokenizer=False
    assert isinstance(rob, RobertaTokenizer) and rob.model_max_length == 512, type(rob)
    sp = spm.SentencePieceProcessor()
    sp.Load(str(BLEURT_SENTPIECE))
    BLEURT_MAX = json.load(open(BLEURT_SENTPIECE.parent / "bleurt_config.json"))["max_seq_length"]
    assert BLEURT_MAX == 512 and sp.GetPieceSize() == 250300
    BLEURT_BUDGET = BLEURT_MAX - 3  # 509: [CLS] ref [SEP] cand [SEP]

    def nfc(s): return unicodedata.normalize("NFC", s)
    def n_words(s): return len(nfc(s).split())
    def xlmr_ws(s): return len(xlmr(nfc(s))["input_ids"])                       # with <s> </s>
    def xlmr_ws_raw(s): return len(xlmr(s)["input_ids"])                        # un-normalised, for the NFC check

    def comet_seg_kept(s):  # content tokens that survive the per-segment cap, by calling the tokenizer as comet does
        return len(xlmr(nfc(s), truncation=True, max_length=COMET_SEG_MAX)["input_ids"]) - 2

    def rob_n(s): return len(rob.encode(s.strip(), add_special_tokens=True, add_prefix_space=True, truncation=False)) - 2
    def bleurt_n(s): return len(sp.EncodeAsPieces(s))

    def bleurt_trunc_pair(nr, nc, max_len=BLEURT_BUDGET):  # mirrors bleurt/encoding.py _truncate_seq_pair
        while nr + nc > max_len:
            if nr > nc:
                nr -= 1
            else:
                nc -= 1
        return nr, nc

    # --- load the corpus exactly as the pipeline does -------------------------------------------
    passages, pairs, nfc_diffs = [], [], []
    for text, name, ref_labels in TEXTS:
        chunks = InputParser().parse_file(str(MT / "input" / f"{name}.txt"))
        trans = json.load(open(MT / "output" / "translations" / f"{name}_translations.json", encoding="utf-8"))
        assert [c.chunk_id for c in chunks] == [str(i) for i in range(1, 11)], [c.chunk_id for c in chunks]
        for c in chunks:
            ch = int(c.chunk_id)
            assert len(c.reference_translations) == len(ref_labels), (text, ch, len(c.reference_translations))
            items = [("src", "Greek", c.greek_text)]
            items += [("hyp", lab, trans[c.chunk_id][key]["translation"]) for key, lab in MODELS]
            items += [("ref", lab, r) for lab, r in zip(ref_labels, c.reference_translations)]
            counts = {}
            for role, label, s in items:
                ws = xlmr_ws(s)
                if ws != xlmr_ws_raw(s):
                    nfc_diffs.append((text, ch, role, label, ws, xlmr_ws_raw(s)))
                rec = dict(text=text, chunk=ch, role=role, label=label, words=n_words(s),
                           xlmr_tokens=ws - 2, xlmr_tokens_with_specials=ws,
                           roberta_tokens=rob_n(s), bleurt_sp_tokens=bleurt_n(s))
                rec["_comet_kept"] = comet_seg_kept(s)
                passages.append(rec)
                counts[(role, label)] = rec
            src = counts[("src", "Greek")]
            for key, mlab in MODELS:
                hyp = counts[("hyp", mlab)]
                for ri, rlab in enumerate(ref_labels, 1):
                    ref = counts[("ref", rlab)]
                    # COMET-Kiwi joint window (as `window` in comet_kiwi.py)
                    hyp_eff, src_eff = min(hyp["xlmr_tokens_with_specials"], COMET_SEG_MAX), min(src["xlmr_tokens_with_specials"], COMET_SEG_MAX)
                    truncated = hyp_eff + src_eff > MAX_POS
                    src_content = src["xlmr_tokens"]
                    kiwi_src_kept = src_content if not truncated else max(0, min(src_content, MAX_POS - (hyp_eff + 1)))
                    # BERTScore: each side independently to 510 content tokens
                    bs_hyp_kept, bs_ref_kept = min(BERT_CONTENT_CAP, hyp["roberta_tokens"]), min(BERT_CONTENT_CAP, ref["roberta_tokens"])
                    # BLEURT-20: balanced pair truncation to 509
                    bl_ref_kept, bl_hyp_kept = bleurt_trunc_pair(ref["bleurt_sp_tokens"], hyp["bleurt_sp_tokens"])
                    pairs.append(dict(
                        text=text, chunk=ch, model=mlab, model_key=key, ref_index=ri, ref_label=rlab,
                        xlmr_src=src_content, xlmr_hyp=hyp["xlmr_tokens"], xlmr_ref=ref["xlmr_tokens"],
                        roberta_hyp=hyp["roberta_tokens"], roberta_ref=ref["roberta_tokens"],
                        bleurt_hyp=hyp["bleurt_sp_tokens"], bleurt_ref=ref["bleurt_sp_tokens"],
                        comet_src_kept_tokens=src["_comet_kept"], comet_hyp_kept_tokens=hyp["_comet_kept"], comet_ref_kept_tokens=ref["_comet_kept"],
                        comet_src_kept_frac=src["_comet_kept"] / src_content,
                        comet_hyp_kept_frac=hyp["_comet_kept"] / hyp["xlmr_tokens"],
                        comet_ref_kept_frac=ref["_comet_kept"] / ref["xlmr_tokens"],
                        kiwi_hyp_kept_tokens=hyp["_comet_kept"], kiwi_hyp_kept_frac=hyp["_comet_kept"] / hyp["xlmr_tokens"],
                        kiwi_hyp_truncated=hyp["xlmr_tokens_with_specials"] > COMET_SEG_MAX,
                        kiwi_src_kept_tokens=kiwi_src_kept, kiwi_src_kept_frac=kiwi_src_kept / src_content,
                        kiwi_joint_truncated=truncated,
                        bertscore_hyp_kept=bs_hyp_kept, bertscore_ref_kept=bs_ref_kept,
                        bertscore_hyp_kept_frac=bs_hyp_kept / hyp["roberta_tokens"], bertscore_ref_kept_frac=bs_ref_kept / ref["roberta_tokens"],
                        bleurt_hyp_kept=bl_hyp_kept, bleurt_ref_kept=bl_ref_kept,
                        bleurt_hyp_kept_frac=bl_hyp_kept / hyp["bleurt_sp_tokens"], bleurt_ref_kept_frac=bl_ref_kept / ref["bleurt_sp_tokens"],
                        bleurt_pair_total=hyp["bleurt_sp_tokens"] + ref["bleurt_sp_tokens"], bleurt_budget=BLEURT_BUDGET))
    assert len(passages) == 110 and len(pairs) == 90, (len(passages), len(pairs))
    for p in passages:
        p.pop("_comet_kept")

    # --- write ----------------------------------------------------------------------------------
    args.out.mkdir(parents=True, exist_ok=True)

    def write(fn, rows):
        path = args.out / fn
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        return path
    p_pass, p_pair = write(FILES[0], passages), write(FILES[1], pairs)

    # --- provenance -----------------------------------------------------------------------------
    hub = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"

    def snap(model):
        ref = (hub / f"models--{model}" / "refs" / "main").read_text().strip()
        d = hub / f"models--{model}" / "snapshots" / ref
        return dict(snapshot=ref, files={f.name: sha(f) for f in sorted(d.iterdir()) if f.name in ("sentencepiece.bpe.model", "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt")})
    prov = dict(python=platform.python_version(), transformers=transformers.__version__, tokenizers=__import__("tokenizers").__version__,
                sentencepiece=spm.__version__, bert_score=bert_score.__version__,
                xlm_roberta_large=snap("xlm-roberta-large"), roberta_large=snap("roberta-large"),
                bleurt_sent_piece_model_sha256=sha(BLEURT_SENTPIECE), bleurt_max_seq_length=BLEURT_MAX,
                xlmr_class=type(xlmr).__name__, roberta_class=type(rob).__name__, nfc_vs_raw_xlmr_count_differences=nfc_diffs)
    print(json.dumps(prov, indent=1))
    print(f"passages rows: {len(passages)}  pairs rows: {len(pairs)}")
    print(f"sha256 {p_pass.name}: {sha(p_pass)}")
    print(f"sha256 {p_pair.name}: {sha(p_pair)}")
    pass_by = {(p["text"], p["chunk"], p["role"], p["label"]): p for p in passages}
    by_key = {(r["text"], r["chunk"], r["model_key"], r["ref_index"]): r for r in pairs}
    for k in [("Comp", 8, "ref", "Marai"), ("Comp", 10, "ref", "Marai")]:
        p = pass_by[k]
        m = by_key[(k[0], k[1], "openai", 1)]
        print(f"{k[0]} {k[1]} {k[3]} reference: xlmr content {p['xlmr_tokens']}, with specials {p['xlmr_tokens_with_specials']}; "
              f"COMET kept {m['comet_ref_kept_tokens']}/{p['xlmr_tokens']} = {m['comet_ref_kept_frac']:.4f}")

    # --- the frozen files -----------------------------------------------------------------------
    ok = [compare(args.out / fn, DATA / fn) for fn in FILES]
    print(f"{'PASS' if all(ok) else 'FAIL'}: {sum(ok)} of {len(FILES)} files byte-identical to data/ "
          f"({', '.join(FILES)}); written to {args.out}")
    sys.exit(0 if all(ok) else 1)


if __name__ == "__main__":
    main()
