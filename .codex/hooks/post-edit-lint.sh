#!/usr/bin/env bash
# Post-edit hook. Runs fast checks on changed files.
# Exit non-zero to block the edit. Keep the total runtime under 5 seconds.
set -euo pipefail

changed="$( { git diff --name-only --cached || true; git diff --name-only || true; } | sort -u )"
if [ -z "$changed" ]; then
  exit 0
fi

fail=0

for f in $changed; do
  [ -f "$f" ] || continue
  case "$f" in
    *.ts|*.tsx)
      npx --no-install prettier --check "$f" || fail=1
      ;;
    *.py)
      python -m ruff check "$f" || fail=1
      ;;
    *.json)
      python -c 'import json,sys; json.load(open(sys.argv[1], encoding="utf-8"))' "$f" || fail=1
      ;;
    *.yaml|*.yml)
      python -c 'import sys,yaml; yaml.safe_load(open(sys.argv[1], encoding="utf-8"))' "$f" || fail=1
      ;;
    *.sh)
      bash -n "$f" || fail=1
      ;;
  esac
done

if [ "$fail" -ne 0 ]; then
  echo "post-edit-lint: checks failed" >&2
  exit 1
fi

exit 0
