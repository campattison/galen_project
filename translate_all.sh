#!/bin/bash

# Ancient Greek Translator - Ultra Simple Interface

echo "🏛️  Ancient Greek Translator"
echo "═══════════════════════════"

# Show help
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo ""
    echo "Usage: $0 [short|medium]"
    echo ""
    echo "  short   - 1-2 sentences per chunk (default)"
    echo "  medium  - full paragraphs per chunk"
    echo ""
    echo "Add your .txt files to texts/inputs/ folder first!"
    exit 0
fi

# Set chunking mode
CHUNKING="short"
if [[ "$1" == "medium" ]]; then
    CHUNKING="medium"
fi

echo "📝 Mode: $CHUNKING chunking"
echo ""

# Check for virtual environment
if [[ ! -f "venv/bin/activate" ]]; then
    echo "Setting up virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check for .env file
if [[ ! -f ".env" ]]; then
    echo "⚠️  No .env file found!"
    echo "Copy env.example to .env and add your API keys:"
    echo "  cp env.example .env"
    echo ""
fi

# Check for input files
if ! ls texts/inputs/*.txt 1> /dev/null 2>&1; then
    echo "❌ No .txt files found in texts/inputs/"
    echo "Add your Ancient Greek text files there first!"
    exit 1
fi

# Run translator
echo "🚀 Translating..."
python main_translator.py --chunking "$CHUNKING"

if [[ $? -eq 0 ]]; then
    echo ""
    echo "✅ Done! Check outputs/ folder for results"
else
    echo ""
    echo "❌ Translation failed - check the error messages above"
    exit 1
fi