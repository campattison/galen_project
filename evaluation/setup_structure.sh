#!/bin/bash
# Setup evaluation directory structure
# This script organizes existing files into the new transparent structure

set -e  # Exit on error

EVAL_DIR="/Users/cameronpattison/Desktop/Galen Project/evaluation"
cd "$EVAL_DIR"

echo "Setting up evaluation directory structure..."
echo ""

# Create directories
echo "Creating directories..."
mkdir -p source_texts/greek
mkdir -p source_texts/gold_standards
mkdir -p translations
mkdir -p outputs
mkdir -p scripts

echo "✓ Directories created"
echo ""

# Gold standards are already in the right place
echo "Gold standards status:"
ls -1 source_texts/gold_standards/ | sed 's/^/  ✓ /'
echo ""

# Check for existing Greek texts
echo "Looking for Greek source texts..."
if [ -f "source_texts/greek_and_translation.txt" ]; then
    echo "  ℹ Found source_texts/greek_and_translation.txt"
    echo "  → This contains paired Greek/English texts"
    echo "  → Gold standards already extracted to gold_standards/"
    echo "  → Greek texts should be extracted to source_texts/greek/"
    echo ""
    echo "  To extract Greek texts:"
    echo "    python scripts/prepare_texts.py source_texts/greek_and_translation.txt"
fi
echo ""

# Copy evaluation outputs to outputs/ folder
echo "Organizing existing evaluation results..."
if [ -d "../evaluation/outputs" ] && [ "$(ls -A ../evaluation/outputs 2>/dev/null)" ]; then
    echo "  Found evaluation results in evaluation/outputs/"
    ls -1 ../evaluation/outputs/*.json 2>/dev/null | while read f; do
        base=$(basename "$f")
        if [ ! -f "outputs/$base" ]; then
            cp "$f" "outputs/$base"
            echo "  ✓ Copied $base"
        fi
    done
fi
echo ""

# Create example Greek text file from gold standard
echo "Creating example Greek text files..."
for gold in source_texts/gold_standards/*.json; do
    base=$(basename "$gold" .json)
    greek_file="source_texts/greek/${base}.txt"
    
    if [ ! -f "$greek_file" ]; then
        # Extract Greek text from gold standard
        python3 << EOF
import json
import sys

try:
    with open('$gold', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list) and len(data) > 0:
        greek_text = data[0].get('greek_text', '')
        if greek_text:
            with open('$greek_file', 'w', encoding='utf-8') as f:
                f.write(greek_text)
            print(f"  ✓ Created $base.txt from gold standard")
        else:
            print(f"  ⚠ No greek_text in $base")
    else:
        print(f"  ⚠ Unexpected format in $base")
except Exception as e:
    print(f"  ✗ Error processing $base: {e}")
EOF
    else
        echo "  ✓ $base.txt already exists"
    fi
done
echo ""

# Create .gitkeep files for empty directories
touch translations/.gitkeep
touch outputs/.gitkeep

echo "Directory structure setup complete!"
echo ""
echo "Current structure:"
echo "evaluation/"
echo "├── source_texts/"
echo "│   ├── greek/           $(ls -1 source_texts/greek/*.txt 2>/dev/null | wc -l | xargs echo -n) Greek text file(s)"
echo "│   └── gold_standards/  $(ls -1 source_texts/gold_standards/*.json 2>/dev/null | wc -l | xargs echo -n) gold standard(s)"
echo "├── translations/        $(ls -1 translations/*.json 2>/dev/null | wc -l | xargs echo -n) translation file(s)"
echo "├── outputs/             $(ls -1 outputs/*.json 2>/dev/null | wc -l | xargs echo -n) evaluation result(s)"
echo "└── scripts/             $(ls -1 scripts/*.py 2>/dev/null | wc -l | xargs echo -n) script(s)"
echo ""
echo "Next steps:"
echo "1. Review source_texts/README.md for gold standard requirements"
echo "2. Review WORKFLOW.md for complete evaluation process"
echo "3. Generate new translations:"
echo "   python scripts/translator.py --input-dir source_texts/greek/ --output translations/"
echo "4. Run evaluations:"
echo "   python scripts/translation_evaluator.py translations/[file].json source_texts/gold_standards/[file].json"
echo ""

