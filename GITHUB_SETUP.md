# GitHub Setup Guide

This guide walks you through uploading this project to GitHub.

---

## Step 1: Create GitHub Repository

1. Go to https://github.com
2. Click the **"+"** button (top right) → **"New repository"**
3. Fill in:
   - **Repository name**: `galen-translation-evaluation` (or your choice)
   - **Description**: "Evaluation framework for AI translation of Ancient Greek texts"
   - **Visibility**: 
     - ✅ **Public** - if you want to share with others
     - ⚠️ **Private** - if you want to keep it private
   - **DON'T** initialize with README (we already have one)
4. Click **"Create repository"**
5. **Copy the repository URL** (looks like: `https://github.com/username/galen-translation-evaluation.git`)

---

## Step 2: Initialize Git (First Time Only)

Open Terminal and run these commands:

```bash
# Navigate to your project
cd "/Users/cameronpattison/Desktop/Galen Project"

# Initialize git (if not already done)
git init

# Configure your identity (if you haven't already)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

---

## Step 3: Add Your Files

```bash
# Add all files (gitignore will exclude secrets)
git add .

# Check what will be committed (verify .env is NOT listed)
git status

# Commit your changes
git commit -m "Initial commit: Ancient Greek translation evaluation framework"
```

**Important:** Check the output of `git status`. Make sure `.env` and other secrets are **NOT** listed!

---

## Step 4: Connect to GitHub

```bash
# Add your GitHub repository as remote
# Replace YOUR_USERNAME and YOUR_REPO with your actual GitHub info
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Verify the remote was added
git remote -v
```

---

## Step 5: Push to GitHub

```bash
# Push your code to GitHub
git push -u origin main

# If you get an error about "master" vs "main", try:
git branch -M main
git push -u origin main
```

---

## Step 6: Verify on GitHub

1. Go to your repository URL on GitHub
2. You should see all your files!
3. Check that `.env` is **NOT** there (should be excluded by `.gitignore`)

---

## What Gets Uploaded

✅ **Included:**
- All Python scripts
- Documentation (README, WORKFLOW, AUDIT_REPORT, etc.)
- Greek source texts
- Gold standard translations
- AI-generated translations
- Evaluation results
- Setup scripts
- Requirements files

❌ **Excluded (by .gitignore):**
- `.env` file (API keys)
- `venv/` folder (Python virtual environment)
- `__pycache__/` (Python cache files)
- `.DS_Store` (macOS system files)
- Log files
- Temporary files

---

## Future Updates

After making changes, upload them with:

```bash
# Add your changes
git add .

# Commit with a message
git commit -m "Description of what you changed"

# Push to GitHub
git push
```

---

## Common Issues

### "fatal: not a git repository"
**Solution:** Run `git init` first

### ".env file is being tracked"
**Solution:** 
```bash
# Remove it from git (keeps local file)
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from tracking"

# Make sure .gitignore includes .env
```

### "authentication failed"
**Solution:** GitHub now requires a Personal Access Token instead of password
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with "repo" permissions
3. Use token as password when pushing

**Better:** Set up SSH keys (see GitHub's documentation)

---

## Making Your Repo Look Professional

### Add Topics/Tags on GitHub

On your repository page, click "⚙️ Settings" → Add topics:
- `ancient-greek`
- `translation`
- `nlp`
- `evaluation`
- `gpt`
- `claude`
- `gemini`

### Add a License

If you want others to use your code:

```bash
# Choose a license at: https://choosealicense.com/
# Common choice: MIT License

# Add LICENSE file, then:
git add LICENSE
git commit -m "Add MIT License"
git push
```

### Add Repository Description

On GitHub repository page, click "⚙️" next to "About" and add:
- Description: "Evaluate AI translation quality for Ancient Greek texts"
- Website: (if you make one)
- Topics: (as listed above)

---

## Recommended Repository Structure on GitHub

Your repo will look like this:

```
galen-translation-evaluation/
├── README.md                    ← Shows first on GitHub
├── evaluation/
│   ├── README.md               ← Evaluation docs
│   ├── source_texts/
│   ├── outputs/
│   └── scripts/
├── main_translator.py
├── requirements.txt
└── .gitignore                  ← Protects your secrets
```

---

## Sharing Your Work

Once uploaded, share your repository URL:
- `https://github.com/YOUR_USERNAME/galen-translation-evaluation`

Others can:
1. View your code and documentation
2. See your evaluation results
3. Clone your repo: `git clone https://github.com/YOUR_USERNAME/galen-translation-evaluation.git`
4. Suggest improvements via Pull Requests

---

## Security Checklist

Before pushing, verify:

- [ ] `.env` file is in `.gitignore`
- [ ] No API keys in any code files
- [ ] No passwords in commit messages
- [ ] Run `git status` - verify no secrets listed
- [ ] Check `git log` - no sensitive info in previous commits

If you accidentally committed secrets:
1. **Don't panic**
2. Immediately revoke/regenerate those API keys
3. Use `git filter-branch` or BFG Repo-Cleaner to remove from history
4. Force push (only if repository is new/private)

---

## Questions?

**Q: Can I make the repo private later?**  
A: Yes! GitHub Settings → Danger Zone → Change visibility

**Q: Should I include the venv folder?**  
A: No, it's excluded by .gitignore. Others run `pip install -r requirements.txt` to recreate it.

**Q: Should I include evaluation results?**  
A: Yes! They're part of your research. Just make sure no API keys are in them.

**Q: What if I have large files (>100MB)?**  
A: Use Git LFS (Large File Storage) or exclude them and provide download links.

---

**Ready?** Follow the steps above to upload your project to GitHub! 🚀

