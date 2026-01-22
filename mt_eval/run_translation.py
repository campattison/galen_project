#!/usr/bin/env python3
"""
Simple script to translate Greek chunks from input files.
Extracts only Greek text and runs translation.
"""

import re
import sys
import os

# Load environment variables first
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from translator import Translator


def extract_greek_chunks(file_path):
    """Extract Greek text chunks from input file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by "Chunk N" markers
    chunk_pattern = r'(?:^|\n)Chunk\s+(\d+)\s*\n'
    parts = re.split(chunk_pattern, content, flags=re.MULTILINE)
    
    chunks = []
    i = 1
    while i < len(parts) - 1:
        chunk_number = parts[i]
        chunk_content = parts[i + 1]
        
        # Split into paragraphs
        paragraphs = re.split(r'\n\s*\n', chunk_content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # Find Greek paragraph (contains Greek characters)
        greek_pattern = re.compile(r'[α-ωΑ-Ωἀ-ἇἰ-ἷὀ-὇ὐ-ὗὠ-ὧᾀ-ᾇᾐ-ᾗᾠ-ᾧᾰ-ᾱῐ-ῑῠ-ῡ]+')
        
        for para in paragraphs:
            para_clean = re.sub(r'\s+', ' ', para).strip()
            if greek_pattern.search(para_clean):
                chunks.append({
                    'chunk_id': chunk_number,
                    'greek_text': para_clean
                })
                print(f"✓ Extracted Chunk {chunk_number}: {len(para_clean)} chars")
                break
        
        i += 2
    
    return chunks


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_translation.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Extract chunks
    print(f"\nExtracting Greek chunks from {input_file}...")
    chunks = extract_greek_chunks(input_file)
    
    if not chunks:
        print("ERROR: No chunks found!")
        sys.exit(1)
    
    print(f"\nFound {len(chunks)} chunks with Greek text")
    
    # Translate
    print("\nInitializing translator...")
    translator = Translator(models=['openai', 'claude', 'gemini'])
    
    print("\nStarting translation...")
    translations = translator.translate_chunks(chunks, parallel=True)
    
    # Save
    if output_file:
        translator.save_translations(translations, output_file)
    else:
        # Default output location
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f'output/translations/{base_name}_translations.json'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        translator.save_translations(translations, output_file)
    
    # Summary
    total_chunks = len(translations)
    successful = sum(
        1 for chunk_translations in translations.values()
        for translation in chunk_translations.values()
        if translation.status == 'success'
    )
    total_attempts = sum(len(chunk_translations) for chunk_translations in translations.values())
    
    print(f"\n✓ Translation complete!")
    print(f"  Chunks: {total_chunks}")
    print(f"  Success rate: {successful}/{total_attempts} ({100*successful/total_attempts:.1f}%)")
    print(f"  Output: {output_file}")


if __name__ == "__main__":
    main()

