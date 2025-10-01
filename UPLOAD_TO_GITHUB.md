# 🚀 Upload to GitHub - Quick Guide

**3 simple steps to get your project on GitHub**

---

## ⚡ Super Quick Method

```bash
# 1. Run the setup script
cd "/Users/cameronpattison/Desktop/Galen Project"
./setup_github.sh

# 2. Create repo on GitHub (https://github.com/new)
#    Name it: galen-translation-evaluation

# 3. Connect and push
git remote add origin https://github.com/YOUR_USERNAME/galen-translation-evaluation.git
git push -u origin main
```

**Done!** Your project is on GitHub.

---

## 📋 Step-by-Step (If You Want Details)

### Step 1: Prepare Locally

```bash
cd "/Users/cameronpattison/Desktop/Galen Project"

# Run the automated setup
./setup_github.sh

# This will:
# - Initialize git
# - Add all files (excluding secrets)
# - Create initial commit
# - Verify .env is not included
```

### Step 2: Create GitHub Repository

1. **Go to:** https://github.com/new
2. **Repository name:** `galen-translation-evaluation`
3. **Description:** "Evaluation framework for AI translation of Ancient Greek texts"
4. **Public or Private:** Your choice
5. **DON'T** check "Add a README file" (we already have one)
6. **Click:** "Create repository"

### Step 3: Connect and Upload

GitHub will show you commands. Use these:

```bash
# Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/galen-translation-evaluation.git

# Push your code
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

---

## ✅ Verify It Worked

1. Go to: `https://github.com/YOUR_USERNAME/galen-translation-evaluation`
2. You should see:
   - ✅ README.md displayed
   - ✅ All your folders (evaluation, texts, outputs, etc.)
   - ✅ Documentation files
   - ❌ NO .env file (good!)

---

## 🔐 Security Check

Before sharing your repository URL, verify:

```bash
# Check that .env is ignored
git ls-files | grep .env

# Should show NOTHING
# If it shows .env, STOP and run:
# git rm --cached .env
# git commit -m "Remove .env"
```

---

## 📝 After Uploading

### Make it Look Professional

**Add topics on GitHub:**
1. Go to your repo on GitHub
2. Click ⚙️ next to "About"
3. Add topics: `ancient-greek`, `translation`, `nlp`, `evaluation`, `ai`

**Add description:**
- "Evaluate GPT-5, Claude, and Gemini on Ancient Greek translation"

### Add a License (Optional)

If you want others to use your work:

```bash
# Download MIT License
curl https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt > LICENSE

# Add year and your name
sed -i '' 's/\[year\]/2025/g' LICENSE
sed -i '' 's/\[fullname\]/Your Name/g' LICENSE

# Commit and push
git add LICENSE
git commit -m "Add MIT License"
git push
```

---

## 🔄 Making Changes Later

After you've uploaded, when you make changes:

```bash
# See what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "Describe what you changed"

# Push to GitHub
git push
```

---

## ❓ Common Issues

### "Permission denied (publickey)"

**Solution:** Use HTTPS URL instead of SSH, or set up SSH keys

```bash
# Use HTTPS (asks for password/token)
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### "Authentication failed"

**Solution:** GitHub requires Personal Access Token now

1. Go to: GitHub → Settings → Developer settings → Personal access tokens → Generate new token
2. Give it "repo" permissions
3. Copy the token
4. Use token as password when git asks

### "Already exists"

**Solution:** Your local git is confused

```bash
# Remove existing remote
git remote remove origin

# Add it again with correct URL
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

---

## 📖 Full Details

For complete documentation, see **`GITHUB_SETUP.md`**

---

## 🎯 What Gets Uploaded

### ✅ Included:
- All documentation (README, WORKFLOW, AUDIT_REPORT, etc.)
- All Python scripts
- Greek source texts
- Gold standard translations  
- AI translations
- Evaluation results
- Example outputs
- Setup scripts
- Requirements files

### ❌ Excluded (by .gitignore):
- `.env` (your API keys) 🔒
- `venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `.DS_Store` (macOS files)
- Log files

---

**Ready? Run `./setup_github.sh` and follow the prompts!**

