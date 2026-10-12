# Token counts: how much of each text the automated metrics read

Every text of the evaluation (20 Greek sources, 60 translations, 30 reference translations) counted
with each metric's own tokenizer, and for each scored pair how much of it each metric with an input
limit keeps. Made 24 Sept 2026 from the inputs of the pipeline (`mt_eval/`); nothing was entered by
hand; `../optional/token_counts.py` remakes them. `33_table_input_limits.py` re-applies every rule
below to the raw counts, checks the word counts against the texts, and builds the input-limits table
from these files.

## Files

| File | Rows | Content |
|---|---|---|
| `token_counts_passages.csv` | 110 (20 sources, 60 translations, 30 references) | one row per text: `text` (Mix/Comp), `chunk` (1–10), `role` (src/hyp/ref), `label` (Greek; ChatGPT/Claude/Gemini; Johnston/Singer/Marai), `words`, `xlmr_tokens`, `xlmr_tokens_with_specials`, `roberta_tokens`, `bleurt_sp_tokens` |
| `token_counts_pairs.csv` | 90 (Mix. 10 × 3 × 2, Comp. 10 × 3 × 1) | one row per scored (translation, reference) pair (`model_key` = the model's key in the translation files; `ref_index`, `ref_label` = the reference): the raw counts under each tokenizer and what each metric keeps (below) |

Texts: the Greek sources and references of `mt_eval/input/on_mixtures.txt` and `on_comp.txt`, read with
the pipeline's parser (`mt_eval/src/parser.py`; for Mix., reference 1 = Johnston, reference 2 = Singer
and van der Eijk; for Comp., Marai), and the translations in `mt_eval/output/translations/`.

## Tokenizers

| Column(s) | Tokenizer | Count | Normalisation | Special tokens |
|---|---|---|---|---|
| `xlmr_tokens`, `xlmr_src/hyp/ref` | `XLMRobertaTokenizerFast` for `xlm-roberta-large` (the encoder of `Unbabel/wmt22-comet-da` and `Unbabel/wmt22-cometkiwi-da`), vocabulary 250,002 | `len(tok(text)["input_ids"]) − 2` | NFC (identical counts without it for all 110 texts) | excluded |
| `xlmr_tokens_with_specials` | the same | `len(tok(text)["input_ids"])` | NFC | included (`<s>`, `</s>`) |
| `roberta_tokens`, `roberta_hyp/ref` | `RobertaTokenizer` for `roberta-large` as bert-score 0.3.12 loads it (`bert_score.utils.get_tokenizer("roberta-large", use_fast=False)`) | `len(tok.encode(text.strip(), add_special_tokens=True, add_prefix_space=True, truncation=False)) − 2` | none beyond `strip()` | excluded |
| `bleurt_sp_tokens`, `bleurt_hyp/ref` | the SentencePiece model of BLEURT-20 (`sent_piece.model`, 250,300 pieces) | `len(sp.EncodeAsPieces(text))` | none | none (BLEURT's `[CLS]` and two `[SEP]` are the 3 positions subtracted from 512 below) |
| `words` | — | `len(NFC(text).split())` | NFC | — |

RoBERTa and SentencePiece counts are given for the Greek sources too, for reference only: BERTScore and
BLEURT never read the source. Versions: transformers 4.57.6, tokenizers 0.22.2, sentencepiece 0.2.1,
bert-score 0.3.12 (Python 3.13.11).

## What each metric keeps (pairs file)

Library code: unbabel-comet 2.2.7, bert-score 0.3.12, bleurt 0.0.2.

- **COMET** (`Unbabel/wmt22-comet-da`): source, translation and reference are tokenized separately, each
  truncated to `max_length` = 510 tokens including its own `<s>` and `</s>`, so at most 508 content tokens
  of each segment are read. `comet_{src,hyp,ref}_kept_tokens` = min(508, content tokens);
  `comet_*_kept_frac` = kept / content tokens.
- **COMET-Kiwi** (`Unbabel/wmt22-cometkiwi-da`): translation, then source, each capped as above, joined as
  `<s> mt </s></s> src </s>` and cut to the first 512 positions, so the cut falls in the source. With
  `hyp_ws`, `src_ws` the counts with special tokens: `hyp_eff = min(hyp_ws, 510)`, `src_eff = min(src_ws, 510)`;
  `kiwi_joint_truncated = hyp_eff + src_eff > 512`; `kiwi_src_kept_tokens` = the source's content tokens if
  not truncated, otherwise `max(0, min(src_content, 512 − (hyp_eff + 1)))`;
  `kiwi_src_kept_frac = kiwi_src_kept_tokens / xlmr_src`; `kiwi_hyp_truncated = hyp_ws > 510`, and
  `kiwi_hyp_kept_tokens`, `kiwi_hyp_kept_frac` apply the per-segment cap of 508 content tokens to the translation.
- **BERTScore** (`roberta-large`, `max_length` 512 including the two special tokens): each side keeps
  min(510, content tokens); `bertscore_{hyp,ref}_kept_frac = min(510, n) / n`.
- **BLEURT-20** (`[CLS] ref [SEP] cand [SEP]`, budget 512 − 3 = 509): while reference + candidate > 509,
  one token is removed from the longer of the two (the candidate on ties). `bleurt_{hyp,ref}_kept` are the
  surviving counts, `_frac = kept / n`, `bleurt_pair_total = hyp + ref`, `bleurt_budget` = 509.

## sha256

```
699a66126e05c5fec03a2121fe38caefae1b02517d7774f24245da747344395c  token_counts_passages.csv
880db9bacf2b2f0f8ae82e55113fd4b3fac76b3b6ef9c9d1a68e161e9acdb407  token_counts_pairs.csv
```
