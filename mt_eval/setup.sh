#!/bin/bash
# Setup script for Galen Translation Evaluation Pipeline
# Creates virtual environment and installs dependencies

set -e  # Exit on error

echo "=================================="
echo "Galen Evaluation Setup"
echo "=================================="
echo ""

# Check Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists at ./venv"
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old venv..."
        rm -rf venv
    else
        echo "Keeping existing venv"
    fi
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created at ./venv"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip > /dev/null
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes on first run (downloading packages)..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check for .env file
echo "Checking for API keys configuration..."
if [ -f "../.env" ]; then
    echo "✓ Found .env in project root"
elif [ -f "config/.env" ]; then
    echo "✓ Found .env in config/"
else
    echo "⚠️  No .env file found"
    echo ""
    echo "To configure API keys, either:"
    echo "  1. Copy ../env.example to ../.env (recommended)"
    echo "  2. Copy config/env.example to config/.env"
    echo ""
    echo "Then edit the .env file with your actual API keys:"
    echo "  - OPENAI_API_KEY"
    echo "  - ANTHROPIC_API_KEY"
    echo "  - GOOGLE_API_KEY"
fi
echo ""

echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "To use the pipeline:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the pipeline:"
echo "     python3 pipeline.py input/10_chunks.txt"
echo ""
echo "  3. When done, deactivate the virtual environment:"
echo "     deactivate"
echo ""
echo "Note: Always activate the virtual environment before running the pipeline!"
echo ""

