#!/usr/bin/env python3
"""
Blind translations: create a blinded copy of model outputs.
- Keeps chunk order unchanged
- Rotates the model order per chunk to prevent tracking across chunks
- Removes all labels/identifiers from blinded output
- Writes a key mapping per chunk indicating the model order used

Usage:
  python blind_translations.py <input_json> <output_blinded_json> [--seed 42]
"""

import json
import os
import sys
import random
import argparse
from typing import List, Dict


def main():
    parser = argparse.ArgumentParser(description="Create a blinded copy of translations")
    parser.add_argument('input_json', help='Input translations JSON (from translator.save_translations)')
    parser.add_argument('output_json', help='Output blinded JSON path')
    parser.add_argument('--seed', type=int, default=42, help='RNG seed for reproducibility')
    parser.add_argument('--write_key', default=None, help='Optional path to write the key mapping JSON')
    args = parser.parse_args()

    random.seed(args.seed)

    # Load translations
    with open(args.input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Determine models present from the first chunk
    first_chunk_id = next(iter(data.keys()))
    models_in_data: List[str] = list(data[first_chunk_id].keys())
    models_in_data.sort()

    # Create a base permutation (random) then rotate per chunk index
    base_perm = models_in_data[:]
    random.shuffle(base_perm)

    # Build blinded structure: keep chunk order; for each chunk, produce ordered list of entries by permuted_models
    blinded_output: Dict[str, List[Dict]] = {}
    key_per_chunk: Dict[str, List[str]] = {}
    sorted_chunk_ids = sorted(data.keys(), key=lambda x: int(x) if x.isdigit() else x)
    for idx, chunk_id in enumerate(sorted_chunk_ids):
        model_translations = data[chunk_id]
        # Rotate the base permutation by idx
        k = idx % len(base_perm)
        order = base_perm[k:] + base_perm[:k]
        entries: List[Dict] = []
        for model in order:
            if model not in model_translations:
                continue
            tr = model_translations[model]
            # No labels in blinded output
            entries.append({
                'translation': tr.get('translation', ''),
                'raw_response': tr.get('raw_response', ''),
                'status': tr.get('status', ''),
                'timestamp': tr.get('timestamp', ''),
            })
        blinded_output[chunk_id] = entries
        key_per_chunk[chunk_id] = order

    # Write blinded JSON
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(blinded_output, f, ensure_ascii=False, indent=2)

    # Key mapping
    key_path = args.write_key
    if key_path is None:
        base, _ = os.path.splitext(args.output_json)
        key_path = base + "_key.json"

    key_obj = {
        'models_in_data': models_in_data,
        'base_permutation': base_perm,
        'order_per_chunk': key_per_chunk,
        'seed': args.seed,
        'source': os.path.abspath(args.input_json)
    }
    with open(key_path, 'w', encoding='utf-8') as f:
        json.dump(key_obj, f, ensure_ascii=False, indent=2)

    print(f"✓ Blinded output written to: {args.output_json}")
    print(f"  Key mapping written to: {key_path}")


if __name__ == '__main__':
    main()
