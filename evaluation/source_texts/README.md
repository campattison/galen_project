# Source Texts Directory

This directory contains the Ancient Greek source texts and their reference (gold standard) translations used for evaluation.

## Directory Structure

```
source_texts/
├── greek/                  # Original Ancient Greek texts
│   └── [passage_name].txt  # One file per passage
│
├── gold_standards/         # Reference translations (human experts)
│   └── [passage_name].json # Gold standard with metadata
│
└── README.md              # This file
```

## File Formats

### Greek Text Files (`greek/`)

Plain text files containing Ancient Greek passages:

```
passage_name.txt
─────────────────
Ὅτι μὲν ἐκ θερμοῦ καὶ ψυχροῦ καὶ ξηροῦ καὶ ὑγροῦ...
```

**Naming convention:** `[work_name]_[section].txt`

Examples:
- `on_mixtures_1.1.txt`
- `on_composition_drugs_book1.txt`

### Gold Standard Files (`gold_standards/`)

JSON files with reference translations and metadata:

```json
[
  {
    "chunk_id": "1",
    "passage_name": "On Mixtures 1.1",
    "greek_text": "Ὅτι μὲν ἐκ θερμοῦ...",
    "translation": "That the bodies of animals...",
    "translator": "Singer and van der Eijk (2019)",
    "edition": "Kühn I 509–10, Helmreich",
    "word_count_greek": 217,
    "word_count_english": 265,
    "translation_philosophy": "scholarly, literal",
    "notes": "Published in Cambridge University Press"
  }
]
```

**Required fields:**
- `chunk_id`: Unique identifier
- `greek_text`: Source text
- `translation`: Reference translation
- `translator`: Full name/citation
- `passage_name`: Descriptive title

**Optional fields:**
- `edition`: Critical edition reference
- `word_count_greek`: Length of source
- `word_count_english`: Length of translation
- `translation_philosophy`: Approach (literal/dynamic/scholarly)
- `notes`: Additional context
- `doi`: Academic citation DOI
- `year`: Publication year

## Adding New Passages

### Step 1: Add Greek Text

Create a new file in `greek/`:

```bash
echo "Your Greek text here" > source_texts/greek/new_passage.txt
```

### Step 2: Create Gold Standard

Create corresponding file in `gold_standards/`:

```bash
cat > source_texts/gold_standards/new_passage.json << 'EOF'
[
  {
    "chunk_id": "1",
    "passage_name": "New Passage Title",
    "greek_text": "Your Greek text here",
    "translation": "Professional translation here",
    "translator": "Translator Name (Year)",
    "edition": "Critical edition reference"
  }
]
EOF
```

### Step 3: Validate

Ensure JSON is valid:

```bash
python -m json.tool source_texts/gold_standards/new_passage.json
```

## Gold Standard Provenance

**CRITICAL:** All gold standards must have proper academic provenance.

### Required Documentation

For each translation, document:

1. **Translator credentials**
   - Academic qualifications
   - Institutional affiliation
   - Relevant publications

2. **Publication details**
   - Publisher (university press preferred)
   - Peer review status
   - ISBN/DOI if available

3. **Translation approach**
   - Literal vs. interpretive
   - Target audience (scholarly/general)
   - Editorial philosophy

### Example: Proper Citation

```json
{
  "translator": "P. N. Singer and Philip van der Eijk",
  "year": 2019,
  "publication": "Galen: Psychological Writings",
  "publisher": "Cambridge University Press",
  "isbn": "978-1-107-05493-4",
  "translation_philosophy": "scholarly literal with explanatory notes",
  "translator_credentials": "P.N. Singer: Senior Research Fellow, University of Exeter; Philip van der Eijk: Professor of Greek, Humboldt University",
  "peer_reviewed": true,
  "notes": "Part of Cambridge Galen series, includes facing Greek text"
}
```

## Current Gold Standards

### on_mixtures_1.1.json
- **Source:** Galen, *On Mixtures* (De temperamentis) 1.1
- **Translator:** Singer and van der Eijk (2019)
- **Status:** ✅ Verified scholarly translation

### on_composition_drugs.json
- **Source:** Galen, *On the Composition of Drugs According to Kind*
- **Translator:** James (attributed)
- **Status:** ⚠️ Needs full citation verification

## Quality Control

Before adding a gold standard:

- [ ] Verify translator is recognized authority
- [ ] Confirm publication is peer-reviewed
- [ ] Check translation is complete (no omissions)
- [ ] Ensure text matches critical edition cited
- [ ] Document any known issues or controversies

## Using with Evaluation

Gold standards are automatically loaded during evaluation:

```bash
python scripts/translation_evaluator.py \
    ../outputs/translations.json \
    source_texts/gold_standards/your_passage.json
```

## License and Usage

Each gold standard file should include:

```json
{
  "copyright": "Citation here",
  "usage_rights": "Educational use only / Fair use / Public domain",
  "restrictions": "Any usage restrictions"
}
```

**Default:** Assume educational/research fair use unless otherwise specified.
