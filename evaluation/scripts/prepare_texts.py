#!/usr/bin/env python3
"""
Workflow Script: Translate Greek Text and Evaluate Against Gold Standard

This script:
1. Parses greek_and_translation.txt to extract Greek text and gold standards
2. Creates input files for translation
3. Runs translations using main_translator.py
4. Prepares gold standard data for evaluation
5. Runs evaluation comparing AI translations to gold standards
"""

import os
import re
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def parse_greek_and_translation_file(filepath):
    """
    Parse the greek_and_translation.txt file to extract Greek text and translations.
    
    Returns:
        List of dictionaries with structure:
        {
            'passage_name': str,
            'greek_text': str,
            'gold_translation': str,
            'passage_number': int
        }
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    passages = []
    
    # Split by blank lines to get sections
    sections = [s.strip() for s in content.split('\n\n') if s.strip()]
    
    i = 0
    passage_num = 1
    while i < len(sections):
        # Look for passage title (English)
        if i < len(sections):
            title = sections[i]
            
            # Skip if it's Greek text (contains Greek characters)
            if any(ord(c) >= 0x0370 and ord(c) <= 0x03FF for c in title):
                i += 1
                continue
            
            # Next should be English translation
            if i + 1 < len(sections):
                english_translation = sections[i + 1]
                
                # Check if this is actually English (not Greek)
                if not any(ord(c) >= 0x0370 and ord(c) <= 0x03FF for c in english_translation):
                    # Next should be Greek text
                    if i + 2 < len(sections):
                        greek_text = sections[i + 2]
                        
                        # Verify it's Greek
                        if any(ord(c) >= 0x0370 and ord(c) <= 0x03FF for c in greek_text):
                            passages.append({
                                'passage_name': title,
                                'greek_text': greek_text,
                                'gold_translation': english_translation,
                                'passage_number': passage_num
                            })
                            passage_num += 1
                            i += 3
                            continue
        i += 1
    
    return passages


def create_input_file_for_translation(passages, output_path):
    """
    Create a text file with numbered Greek passages for translation.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for passage in passages:
            f.write(f"{passage['passage_number']}.\n")
            f.write(f"{passage['greek_text']}\n\n")
    
    print(f"✓ Created input file: {output_path}")
    print(f"  Contains {len(passages)} passages")


def create_gold_standard_file(passages, output_path):
    """
    Create a JSON file with gold standard translations for evaluation.
    """
    gold_standards = []
    
    for passage in passages:
        gold_standards.append({
            'chunk_id': str(passage['passage_number']),
            'passage_name': passage['passage_name'],
            'greek_text': passage['greek_text'],
            'translation': passage['gold_translation']
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(gold_standards, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created gold standard file: {output_path}")
    print(f"  Contains {len(gold_standards)} reference translations")


def main():
    """Main workflow."""
    print("\n" + "="*70)
    print("GREEK TRANSLATION AND EVALUATION WORKFLOW")
    print("="*70)
    
    # Paths
    project_root = Path(__file__).parent.parent
    source_file = project_root / "evaluation" / "greek_and_translation.txt"
    input_dir = project_root / "texts" / "inputs"
    output_dir = project_root / "outputs"
    eval_dir = project_root / "evaluation"
    
    # Ensure directories exist
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamped filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_file = input_dir / f"galen_passages_{timestamp}.txt"
    gold_file = eval_dir / f"gold_standard_{timestamp}.json"
    
    # Step 1: Parse source file
    print(f"\n📖 Step 1: Parsing {source_file.name}...")
    if not source_file.exists():
        print(f"❌ Error: {source_file} not found!")
        return 1
    
    passages = parse_greek_and_translation_file(source_file)
    
    if not passages:
        print("❌ Error: No passages found in source file!")
        return 1
    
    print(f"✓ Found {len(passages)} passages:")
    for p in passages:
        print(f"  • {p['passage_name']}")
    
    # Step 2: Create input file for translation
    print(f"\n📝 Step 2: Creating input file for translation...")
    create_input_file_for_translation(passages, input_file)
    
    # Step 3: Create gold standard file
    print(f"\n🏆 Step 3: Creating gold standard file...")
    create_gold_standard_file(passages, gold_file)
    
    # Step 4: Instructions for translation
    print(f"\n🤖 Step 4: Run translation")
    print(f"Execute the following command to translate:")
    print(f"\n  python main_translator.py --chunking medium --input-dir texts/inputs --output-dir outputs")
    print(f"\nOr to translate just this file:")
    print(f"  # The translator will process all files in texts/inputs/")
    
    # Step 5: Instructions for evaluation
    print(f"\n📊 Step 5: After translation completes, run evaluation")
    print(f"Execute:")
    print(f"\n  python evaluation/translation_evaluator.py <translation_output_file> {gold_file}")
    print(f"\nExample:")
    print(f"  python evaluation/translation_evaluator.py outputs/galen_passages_{timestamp}_medium_*.json {gold_file}")
    
    print(f"\n" + "="*70)
    print("WORKFLOW PREPARATION COMPLETE")
    print("="*70)
    print(f"\n📁 Files created:")
    print(f"  • Input: {input_file}")
    print(f"  • Gold standard: {gold_file}")
    print(f"\n💡 Next steps:")
    print(f"  1. Run main_translator.py to translate the Greek text")
    print(f"  2. Run translation_evaluator.py to compare AI translations with gold standards")
    print(f"  3. Review evaluation results to see which model performs best\n")
    
    return 0


if __name__ == "__main__":
    exit(main())

