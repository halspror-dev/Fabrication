#!/usr/bin/env bash
# PreToolUse hook: run check3d.py before any `git push`; block the push if it fails.
cmd=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')
echo "$cmd" | grep -Eq '\bgit\b[^;&|]*\bpush\b' || exit 0
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}/drawing-scripts" || { echo "check3d hook: drawing-scripts not found" >&2; exit 2; }
if ! out=$(python3 check3d.py templates.py 2>&1); then
  printf 'Push blocked: check3d.py failed.\n%s\n' "$(echo "$out" | tail -15)" >&2
  exit 2
fi
if ! out=$(python3 v096_3d.py check 2>&1); then
  printf 'Push blocked: v096_3d.py check failed.\n%s\n' "$(echo "$out" | tail -15)" >&2
  exit 2
fi
