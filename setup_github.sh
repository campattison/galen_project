#!/bin/bash
# Quick GitHub Setup Script
# This prepares your project for upload to GitHub

set -e  # Exit on error

echo "================================================"
echo "  GitHub Setup for Galen Translation Project"
echo "================================================"
echo ""

# Step 1: Initialize git
echo "Step 1: Initializing git repository..."
git init
git branch -M main
echo "✅ Git initialized"
echo ""

# Step 2: Check for secrets
echo "Step 2: Checking for sensitive files..."
if [ -f ".env" ]; then
    echo "✅ .env file found - will be excluded by .gitignore"
else
    echo "⚠️  No .env file found (that's okay if you don't have API keys)"
fi
echo ""

# Step 3: Configure git (if not already configured)
echo "Step 3: Checking git configuration..."
if ! git config user.name > /dev/null 2>&1; then
    echo "❓ Git user.name not set"
    echo "   Run: git config --global user.name \"Your Name\""
else
    echo "✅ Git user: $(git config user.name)"
fi

if ! git config user.email > /dev/null 2>&1; then
    echo "❓ Git user.email not set"
    echo "   Run: git config --global user.email \"your.email@example.com\""
else
    echo "✅ Git email: $(git config user.email)"
fi
echo ""

# Step 4: Add files
echo "Step 4: Adding files to git..."
git add .
echo "✅ Files added"
echo ""

# Step 5: Show what will be committed
echo "Step 5: Files to be committed (verify .env is NOT here!):"
echo "-----------------------------------------------------------"
git status --short | head -20
if [ $(git status --short | wc -l) -gt 20 ]; then
    echo "... and $(( $(git status --short | wc -l) - 20 )) more files"
fi
echo ""

# Check if .env is being tracked
if git ls-files | grep -q "\.env$"; then
    echo "❌ ERROR: .env file is being tracked!"
    echo "   This should not happen. Run: git rm --cached .env"
    exit 1
else
    echo "✅ .env file is NOT being tracked (good!)"
fi
echo ""

# Step 6: Create initial commit
echo "Step 6: Creating initial commit..."
git commit -m "Initial commit: Ancient Greek translation evaluation framework

- Complete evaluation framework with GPT-5, Claude 4.1, Gemini 2.5 Pro
- 12 NLP metrics (ROUGE, BLEU, METEOR, chrF, SentenceBERT, BERTScore)
- Transparent methodology with warnings
- Sample evaluations and gold standards included
- Full documentation for technical and non-technical users"

echo "✅ Initial commit created"
echo ""

echo "================================================"
echo "  Setup Complete! Next Steps:"
echo "================================================"
echo ""
echo "1. Create a repository on GitHub:"
echo "   → Go to https://github.com/new"
echo "   → Name: galen-translation-evaluation"
echo "   → Don't initialize with README"
echo "   → Create repository"
echo ""
echo "2. Copy your repository URL from GitHub"
echo ""
echo "3. Run these commands:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "   git push -u origin main"
echo ""
echo "That's it! Your project will be on GitHub."
echo ""
echo "For detailed instructions, see GITHUB_SETUP.md"
echo ""

