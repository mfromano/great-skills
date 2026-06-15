#!/usr/bin/env bash
# Hook script: regenerate README.md and push when a SKILL.md is written.
set -euo pipefail

SKILLS_DIR="/Users/mromano/.claude/skills"

# Read hook JSON from stdin and extract tool_input.file_path
HOOK_JSON=$(cat)
FILE_PATH=$(python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
print(d.get('tool_input', {}).get('file_path', ''))
" <<< "$HOOK_JSON")

# Only act on SKILL.md files written directly inside a skill subdirectory
case "$FILE_PATH" in
  "$SKILLS_DIR"/*/SKILL.md) ;;
  *) exit 0 ;;
esac

python3 "$SKILLS_DIR/scripts/generate-readme.py"

cd "$SKILLS_DIR"
git add README.md

# Nothing changed → done
git diff --cached --quiet && exit 0

SKILL_NAME=$(basename "$(dirname "$FILE_PATH")")
git commit -m "docs: auto-update README after adding $SKILL_NAME"
git push origin HEAD
