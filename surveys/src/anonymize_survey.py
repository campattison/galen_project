#!/usr/bin/env python3
"""
Anonymize survey data by replacing expert names with anonymous IDs
Run this script from the surveys/ directory.
"""

import pandas as pd
import hashlib
import os

# Find the most recent survey responses file
input_file = 'survey-responses-1769101081971.csv'
if not os.path.exists(input_file):
    # Fallback to any survey-responses file
    import glob
    files = glob.glob('survey-responses-*.csv')
    if files:
        input_file = sorted(files)[-1]  # Most recent
    else:
        raise FileNotFoundError("No survey-responses CSV found")

print(f"Input file: {input_file}")

# Load the original data
df = pd.read_csv(input_file)

print(f"Original data: {len(df)} rows, {df['Expert Name'].nunique()} unique experts")

# Create anonymous expert mapping
unique_experts = df['Expert Name'].unique()
expert_mapping = {name: f"Expert_{i+1:02d}" for i, name in enumerate(sorted(unique_experts))}

# Create anonymous response IDs (hash the original to maintain consistency)
def anonymize_id(original_id):
    return hashlib.sha256(original_id.encode()).hexdigest()[:16]

# Apply anonymization
df_anon = df.copy()

# Replace expert names
df_anon['Expert Name'] = df_anon['Expert Name'].map(expert_mapping)

# Replace response IDs with hashed versions
df_anon['ID'] = df_anon['ID'].apply(anonymize_id)

# Remove "Other Expertise (Specify)" as it may be identifying
df_anon['Other Expertise (Specify)'] = ''

# Save anonymized version
output_file = 'survey-responses-anonymized.csv'
df_anon.to_csv(output_file, index=False)

print(f"\nAnonymized data saved to: {output_file}")
print(f"Expert mapping (for internal reference only):")
for original, anon in sorted(expert_mapping.items(), key=lambda x: x[1]):
    print(f"  {anon}: {original}")

# Save mapping to a separate file (keep this private!)
mapping_df = pd.DataFrame([
    {'Anonymous ID': anon, 'Original Name': orig} 
    for orig, anon in expert_mapping.items()
])
mapping_df.to_csv('expert_mapping_PRIVATE.csv', index=False)
print(f"\nExpert mapping saved to: expert_mapping_PRIVATE.csv (DO NOT SHARE)")

# Create/update .gitignore to protect private files
gitignore_entries = [
    "# Private data - DO NOT COMMIT",
    "survey-responses-*.csv",
    "!survey-responses-anonymized.csv",
    "expert_mapping_PRIVATE.csv",
    ""
]

gitignore_path = '.gitignore'
existing_content = ""
if os.path.exists(gitignore_path):
    with open(gitignore_path, 'r') as f:
        existing_content = f.read()

# Only add if not already present
if "expert_mapping_PRIVATE.csv" not in existing_content:
    with open(gitignore_path, 'a') as f:
        if existing_content and not existing_content.endswith('\n'):
            f.write('\n')
        f.write('\n'.join(gitignore_entries))
    print(f"\n.gitignore updated to protect private files")
else:
    print(f"\n.gitignore already configured")

print(f"""
Done! For GitHub:
  - survey-responses-anonymized.csv  (SAFE to commit)
  - survey-responses-*.csv           (IGNORED - contains names)
  - expert_mapping_PRIVATE.csv       (IGNORED - contains mapping)
""")
