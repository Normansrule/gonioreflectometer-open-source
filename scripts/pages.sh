#!/usr/bin/env bash
# Turn on the website: GitHub Pages built by .github/workflows/pages.yml from docs/. Safe to re-run.
# Pages needs a public repository (or a paid GitHub plan). This script asks before changing the repository's visibility.
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(dirname "$0")/.."
REPO=$(git remote get-url origin | sed -E 's#\.git$##; s#.*[:/]([^/:]+/[^/]+)$#\1#')
OWNER=${REPO%%/*}; NAME=${REPO#*/}
VIS=$(gh repo view "$REPO" --json visibility -q .visibility)
if [ "$VIS" != "PUBLIC" ]; then
  echo "$REPO is $VIS. Pages on a private repository needs a paid GitHub plan."
  echo "Making it public shows everything in it, and its whole history, to everyone (code, issues, wiki, PARTS.md)."
  read -r -p "Make $REPO public now? [y/N] " a
  if [ "$a" = y ] || [ "$a" = Y ]; then
    gh repo edit "$REPO" --visibility public --accept-visibility-change-consequences
  else
    echo "left $VIS: Pages will only work if your plan allows it on private repositories"
  fi
fi
if gh api "repos/$REPO/pages" >/dev/null 2>&1; then
  gh api -X PUT "repos/$REPO/pages" -f build_type=workflow >/dev/null
else
  gh api -X POST "repos/$REPO/pages" -f build_type=workflow >/dev/null
fi
gh workflow run pages.yml -R "$REPO" --ref main
echo "Pages on: the first deploy takes a minute or two (gh run watch -R $REPO)."
echo "site: https://$(echo "$OWNER" | tr '[:upper:]' '[:lower:]').github.io/$NAME/"
