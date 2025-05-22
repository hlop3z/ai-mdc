#!/bin/bash

set -euo pipefail

ROOT_DIR=".ai_knowledge_base"
TMP_DIR="$(mktemp -d)"
SUMMARY_FILE="$ROOT_DIR/retrospectives/cleanup_$(date +%F).md"

echo "# Cleanup Summary – $(date +%F)" >"$SUMMARY_FILE"
echo "" >>"$SUMMARY_FILE"
echo "## Deleted Files" >>"$SUMMARY_FILE"
echo "" >>"$SUMMARY_FILE"

# Create a map of latest files to preserve (per folder)
declare -A latest_files

find "$ROOT_DIR" -type f -name "*.md" | while read -r file; do
    # Extract metadata
    retain=$(grep -m1 "retain: true" "$file" || true)
    pin=$(grep -m1 "#pin" "$file" || true)
    folder=$(dirname "$file")
    timestamp=$(stat -c %Y "$file")

    key="${folder}"

    if [[ -n "$retain" || -n "$pin" ]]; then
        cp "$file" "$TMP_DIR/$(basename "$file")"
        continue
    fi

    # Track the most recent file per folder
    if [[ -z "${latest_files[$key]:-}" || "$timestamp" -gt "${latest_files[$key]%:*}" ]]; then
        latest_files["$key"]="$timestamp:$file"
    fi
done

# Preserve most recent files
for entry in "${latest_files[@]}"; do
    file="${entry#*:}"
    cp "$file" "$TMP_DIR/$(basename "$file")"
done

# Clear all eligible folders (except README.md and retrospectives)
find "$ROOT_DIR" -mindepth 2 -type f -name "*.md" ! -path "$ROOT_DIR/retrospectives/*" ! -name "README.md" -exec rm -f {} +

# Restore preserved files
cp "$TMP_DIR"/*.md "$ROOT_DIR/"*/ 2>/dev/null || true

# Summarize what was deleted
find "$ROOT_DIR" -mindepth 2 -type f -name "*.md" ! -path "$ROOT_DIR/retrospectives/*" ! -name "README.md" >"$TMP_DIR/after.txt"
comm -23 <(find "$ROOT_DIR" -type f -name "*.md" | sort) <(sort "$TMP_DIR/after.txt") >>"$SUMMARY_FILE"

# Cleanup temp files
rm -rf "$TMP_DIR"

echo "Cleanup complete. Summary written to $SUMMARY_FILE"
