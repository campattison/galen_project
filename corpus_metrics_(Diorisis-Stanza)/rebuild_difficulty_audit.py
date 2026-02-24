# -*- coding: utf-8 -*-
"""
Galenic Passage Difficulty Analysis
====================================
Computes corpus-based rarity metrics for chunks of Galen's De compositione
medicamentorum (Comp.) and De temperamentis / De mixtionibus (Mix.) against the
Diorisis Ancient Greek Corpus.

Workflow
--------
1.  Build a lemma-frequency dictionary from the Diorisis XML files.
2.  Parse Greek text chunks from mix.txt and comp.txt.
3.  Lemmatize each chunk with Stanza.
4.  Print the lemmatised form of every chunk.
5.  Compute per-chunk difficulty metrics (Zipf, rare-term ratio, not-found ratio).

Usage
-----
    python galenic_difficulty.py

Adjust the three path constants at the top of main() to match your local layout.
"""

import os
import re
import math
import json
import glob
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import stanza
import pandas as pd


# ──────────────────────────────────────────────────────────────────────────────
# 1.  BUILD DIORISIS FREQUENCY DICTIONARY
# ──────────────────────────────────────────────────────────────────────────────

def build_diorisis_frequencies(diorisis_dir: str, cache_path: str = "diorisis_frequencies.json"):
    """
    Walk every XML file in *diorisis_dir*, extract <lemma entry="…"> attributes,
    count them, and return (freq_dict, corpus_size).

    Results are cached to *cache_path* so subsequent runs skip the XML parsing.
    """
    if os.path.exists(cache_path):
        print(f"  ↳ Loading cached frequencies from {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["frequencies"], data["corpus_size"]

    print(f"  ↳ Scanning Diorisis XMLs in {diorisis_dir} …")
    freq = Counter()
    xml_files = sorted(glob.glob(os.path.join(diorisis_dir, "*.xml")))
    if not xml_files:
        raise FileNotFoundError(f"No .xml files found in {diorisis_dir}")

    for i, xml_path in enumerate(xml_files, 1):
        if i % 50 == 0 or i == len(xml_files):
            print(f"      [{i}/{len(xml_files)}] {os.path.basename(xml_path)}")
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for lemma_el in root.iter("lemma"):
                entry = lemma_el.get("entry")
                if entry:
                    freq[entry] += 1
        except ET.ParseError as e:
            print(f"      ⚠ XML parse error in {os.path.basename(xml_path)}: {e}")

    corpus_size = sum(freq.values())
    freq_dict = dict(freq)

    # Cache for next time
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump({"frequencies": freq_dict, "corpus_size": corpus_size}, f, ensure_ascii=False)
    print(f"  ↳ Cached {len(freq_dict):,} lemma types, {corpus_size:,} tokens → {cache_path}")

    return freq_dict, corpus_size


# ──────────────────────────────────────────────────────────────────────────────
# 2.  PARSE GREEK TEXT CHUNKS
# ──────────────────────────────────────────────────────────────────────────────

def parse_chunks(txt_path: str) -> dict[int, str]:
    """
    Parse a .txt file whose chunks are delimited by headers like:
        --- Chunk N ---
        --- Head 224 (Chunk N) ---
    and optionally followed by a --- Report --- section to strip.

    Returns {chunk_number: greek_text}.
    """
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove report section at the end
    if "--- Report ---" in content:
        content = content.split("--- Report ---")[0]

    # Match both header formats
    # Format 1:  --- Chunk N ---
    # Format 2:  --- Head NNN (Chunk N) ---   (with possible leading junk on line 1)
    chunk_pattern = r'(?:---\s*Chunk\s+(\d+)\s*---)|(?:.*?Head\s+\d+\s*\(Chunk\s+(\d+)\)\s*---)'
    
    chunks = {}
    parts = re.split(chunk_pattern, content)
    
    # re.split with groups: [pre, g1_or_None, g2_or_None, text, g1_or_None, g2_or_None, text, ...]
    i = 1
    while i < len(parts):
        # One of the two capture groups will be non-None
        chunk_num_str = parts[i] if parts[i] is not None else parts[i + 1]
        chunk_text = parts[i + 2] if (i + 2) < len(parts) else ""
        
        if chunk_num_str is not None:
            chunk_num = int(chunk_num_str)
            chunks[chunk_num] = chunk_text.strip()
        i += 3

    return chunks


# ──────────────────────────────────────────────────────────────────────────────
# 3.  STANZA LEMMATISATION
# ──────────────────────────────────────────────────────────────────────────────

def lemmatize_passage(text: str, nlp_pipeline) -> list[str]:
    """Return a list of lemmas (punctuation excluded) using Stanza."""
    doc = nlp_pipeline(text)
    lemmas = []
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.upos == "PUNCT":
                continue
            lemmas.append(word.lemma)
    return lemmas


# ──────────────────────────────────────────────────────────────────────────────
# 4.  DIFFICULTY METRICS
# ──────────────────────────────────────────────────────────────────────────────

def calculate_zipf(freq: int, corpus_size: int) -> float:
    """
    Zipf score = log10(frequency per billion words).

    Higher = more common.  0.0 = not found (maximally rare).
    """
    if freq == 0:
        return 0.0
    return math.log10((freq / corpus_size) * 1e9)


def compute_chunk_metrics(lemmas: list[str],
                          freq_dict: dict,
                          corpus_size: int,
                          rare_threshold: int = 50) -> dict:
    """Compute difficulty metrics for one chunk's lemma list."""
    zipf_scores = []
    rare_terms = []
    not_found_terms = []

    for lemma in lemmas:
        freq = freq_dict.get(lemma, 0)
        z = calculate_zipf(freq, corpus_size)
        zipf_scores.append(z)
        if freq < rare_threshold:
            rare_terms.append(lemma)
        if freq == 0:
            not_found_terms.append(lemma)

    n = len(lemmas)
    found_zipfs = [z for z in zipf_scores if z > 0]

    return {
        "avg_zipf":            sum(zipf_scores) / n if n else 0,
        "avg_zipf_found_only": sum(found_zipfs) / len(found_zipfs) if found_zipfs else 0,
        "min_zipf":            min(zipf_scores) if zipf_scores else 0,
        "rare_term_ratio":     len(rare_terms) / n if n else 0,
        "not_found_ratio":     len(not_found_terms) / n if n else 0,
        "total_terms":         n,
        "rare_terms":          len(rare_terms),
        "not_found_terms":     len(not_found_terms),
    }


# ──────────────────────────────────────────────────────────────────────────────
# 5.  MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    # ── PATHS (adjust to your local layout) ──────────────────────────────────
    DIORISIS_DIR = "Diorisis"        # folder containing Diorisis .xml files
    MIX_PATH     = "mix.txt"         # De temperamentis / Mixtures chunks
    COMP_PATH    = "comp.txt"        # De compositione chunks (Head 224)
    CACHE_PATH   = "diorisis_frequencies.json"
    OUTPUT_CSV   = "passage_difficulty_zipf.csv"
    # ─────────────────────────────────────────────────────────────────────────

    # 1. Frequency dictionary
    print("=" * 60)
    print("STEP 1 — Build / load Diorisis frequency dictionary")
    print("=" * 60)
    freq_dict, corpus_size = build_diorisis_frequencies(DIORISIS_DIR, CACHE_PATH)
    print(f"  Lemma types : {len(freq_dict):,}")
    print(f"  Corpus size : {corpus_size:,} tokens")

    # Quick sanity check
    test_words = ["ὁ", "καί", "λέγω", "θεός", "ἰατρός"]
    print("\n  Zipf scale spot-check:")
    for w in test_words:
        f = freq_dict.get(w, 0)
        z = calculate_zipf(f, corpus_size)
        print(f"    {w:>10s}: freq={f:>8,}  Zipf={z:.2f}")

    # 2. Parse chunks
    print("\n" + "=" * 60)
    print("STEP 2 — Parse Greek text chunks")
    print("=" * 60)
    mix_chunks  = parse_chunks(MIX_PATH)
    comp_chunks = parse_chunks(COMP_PATH)
    print(f"  Mix  chunks: {len(mix_chunks)}  (keys: {sorted(mix_chunks.keys())})")
    print(f"  Comp chunks: {len(comp_chunks)}  (keys: {sorted(comp_chunks.keys())})")

    # 3. Lemmatise
    print("\n" + "=" * 60)
    print("STEP 3 — Lemmatise with Stanza (ancient Greek)")
    print("=" * 60)
    stanza.download("grc", verbose=False)
    nlp = stanza.Pipeline("grc", processors="tokenize,pos,lemma", verbose=False)
    print("  ✓ Stanza pipeline ready\n")

    all_results = []

    for label, chunks in [("Mix", mix_chunks), ("Comp", comp_chunks)]:
        for chunk_num in sorted(chunks.keys()):
            tag = f"{label}_Chunk{chunk_num}"
            greek = chunks[chunk_num]
            print(f"  Lemmatising {tag} ({len(greek):,} chars) …")
            lemmas = lemmatize_passage(greek, nlp)

            # ── Print lemmatised form ────────────────────────────────
            print(f"\n  ── {tag} lemmatised ({len(lemmas)} lemmas) ──")
            print("  " + " ".join(lemmas))
            print()

            # ── Metrics ──────────────────────────────────────────────
            metrics = compute_chunk_metrics(lemmas, freq_dict, corpus_size)
            metrics["chunk"]       = tag
            metrics["text"]        = label
            metrics["chunk_num"]   = chunk_num
            metrics["char_count"]  = len(greek)
            metrics["lemma_count"] = len(lemmas)
            all_results.append(metrics)

    # 4. Build DataFrame & display
    print("\n" + "=" * 60)
    print("STEP 4 — Per-chunk results  (Zipf: higher = more common; 0 = not found)")
    print("=" * 60)

    df = pd.DataFrame(all_results)

    col_order = [
        "chunk", "text", "chunk_num",
        "avg_zipf", "avg_zipf_found_only",
        "rare_term_ratio", "not_found_ratio",
        "total_terms", "rare_terms", "not_found_terms",
        "char_count", "lemma_count",
    ]
    df = df[[c for c in col_order if c in df.columns]]
    df = df.sort_values(["text", "chunk_num"])

    for col in ["avg_zipf", "avg_zipf_found_only", "rare_term_ratio", "not_found_ratio"]:
        df[col] = df[col].round(4)

    print(df.to_string(index=False))

    # 5. Summary by text
    print("\n" + "=" * 60)
    print("SUMMARY BY TEXT")
    print("=" * 60)

    summary = df.groupby("text").agg({
        "avg_zipf":        "mean",
        "rare_term_ratio": "mean",
        "not_found_ratio": "mean",
    }).round(4)
    print(summary)

    print("\nInterpretation:")
    print("  • Lower avg_zipf          → harder (rarer vocabulary pulling down the mean)")
    print("  • Higher rare_term_ratio   → harder (more lemmas with freq < 50 in Diorisis)")
    print("  • Higher not_found_ratio   → harder (more lemmas absent from Diorisis entirely)")


    # 6. Save
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✓ Saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()