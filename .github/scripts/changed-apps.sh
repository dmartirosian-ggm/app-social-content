#!/usr/bin/env bash
# Prints the apps this push should publish, space separated.
#   - a push that only touches apps/<app>/... publishes just those apps, so branches
#     working on different apps never overwrite each other's files
#   - a push that touches the shared engine, or a manual run, publishes every app
# Usage: changed-apps.sh <event name> <before sha> <default branch>
set -euo pipefail
event="${1:-push}"; before="${2:-}"; default_branch="${3:-main}"

all_apps() {
  for d in apps/*/; do
    if [ -f "${d}clip.py" ] || [ -f "${d}pin.py" ]; then basename "$d"; fi
  done | xargs
}

if [ "$event" != "push" ]; then all_apps; exit 0; fi

base=""
if [ -n "$before" ] && [ -z "${before//0/}" ]; then before=""; fi   # all zeros = new branch
if [ -n "$before" ] && git cat-file -e "${before}^{commit}" 2>/dev/null; then
  base="$before"
else
  base="$(git merge-base "origin/${default_branch}" HEAD 2>/dev/null || true)"
fi
if [ -z "$base" ]; then all_apps; exit 0; fi

changed="$(git diff --name-only "$base" HEAD)"
if grep -qE '^(engine/|requirements\.txt$|\.github/)' <<<"$changed"; then all_apps; exit 0; fi

sed -n 's#^apps/\([^/]*\)/.*#\1#p' <<<"$changed" | sort -u | while read -r app; do
  if [ -f "apps/$app/clip.py" ] || [ -f "apps/$app/pin.py" ]; then echo "$app"; fi
done | xargs
