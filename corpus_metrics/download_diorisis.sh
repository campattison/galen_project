#!/usr/bin/env bash
# Download the Diorisis Ancient Greek Corpus (CC BY 4.0)
#
# Vatri, A., & McGillivray, B. (2018). The Diorisis Ancient Greek Corpus.
# figshare. Dataset. https://doi.org/10.6084/m9.figshare.6187256.v1
#
# The corpus is required by rebuild_difficulty_audit.py to compute
# lemma-frequency-based difficulty metrics for Galen's passages.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$SCRIPT_DIR/Diorisis"
ZIP_URL="https://ndownloader.figshare.com/files/11296247"
ZIP_FILE="$SCRIPT_DIR/Diorisis.zip"

if [ -d "$TARGET_DIR" ] && [ "$(ls "$TARGET_DIR"/*.xml 2>/dev/null | wc -l)" -gt 800 ]; then
    echo "Diorisis corpus already present ($TARGET_DIR). Skipping download."
    exit 0
fi

echo "Downloading Diorisis Ancient Greek Corpus (~185 MB)..."
curl -L -o "$ZIP_FILE" "$ZIP_URL"

echo "Extracting..."
unzip -q -o "$ZIP_FILE" -d "$SCRIPT_DIR"

# Verify
XML_COUNT=$(ls "$TARGET_DIR"/*.xml 2>/dev/null | wc -l | tr -d ' ')
echo "Extracted $XML_COUNT XML files to $TARGET_DIR"

if [ "$XML_COUNT" -lt 800 ]; then
    echo "WARNING: Expected ~820 XML files, got $XML_COUNT. Check the download."
    exit 1
fi

# Clean up zip
rm -f "$ZIP_FILE"
echo "Done. Diorisis corpus ready."
