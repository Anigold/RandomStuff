#!/bin/bash

# Define temp files
EXISTING_REQ="requirements.txt"
FROZEN_REQ=".frozen_requirements.tmp"
MERGED_REQ=".merged_requirements.tmp"

# 1. Get up-to-date requirements
echo "🔍 Freezing current environment..."
pip freeze > "$FROZEN_REQ"

# 2. Build associative arrays
declare -A INLINE_MAP   # Holds inline-conditional entries from original
declare -A FROZEN_MAP   # Holds frozen packages

# Extract inline entries from original requirements.txt
while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    name=$(echo "$line" | cut -d= -f1 | tr -d ' ')
    if [[ "$line" == *";"* ]]; then
        INLINE_MAP["$name"]="$line"
    else
        INLINE_MAP["$name"]=""
    fi
done < "$EXISTING_REQ"

# Extract frozen packages
while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    name=$(echo "$line" | cut -d= -f1 | tr -d ' ')
    FROZEN_MAP["$name"]="$line"
done < "$FROZEN_REQ"

# 3. Merge entries (prefer inline entries when available)
> "$MERGED_REQ"
for name in "${!FROZEN_MAP[@]}"; do
    if [[ -n "${INLINE_MAP[$name]}" ]]; then
        echo "${INLINE_MAP[$name]}" >> "$MERGED_REQ"
    else
        echo "${FROZEN_MAP[$name]}" >> "$MERGED_REQ"
    fi
done

# 4. Sort and finalize (optional: sort for cleanliness)
sort "$MERGED_REQ" > "$EXISTING_REQ"

# 5. Clean up
rm -f "$FROZEN_REQ" "$MERGED_REQ"

echo "Merged requirements written to requirements.txt"
