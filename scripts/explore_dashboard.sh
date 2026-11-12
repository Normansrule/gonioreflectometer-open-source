#!/usr/bin/env bash
# Rebuild the map viewer in docs/explore/ from Understand-Anything (MIT, https://github.com/Egonex-AI/Understand-Anything).
# The graph it shows is docs/explore/knowledge-graph.json, made by tools/explore_graph.py (`make build`); this script
# only rebuilds the viewer itself, which rarely changes.
#   bash scripts/explore_dashboard.sh /path/to/Understand-Anything     (a clone or an unzipped download)
# Needs Node 20+ and pnpm. SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
SRC="${1:?path to an Understand-Anything checkout}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
cp -r "$SRC/understand-anything-plugin" "$WORK/plugin"
cd "$WORK/plugin"
pnpm install --frozen-lockfile --ignore-scripts
(cd packages/core && pnpm run build)
cd packages/dashboard
npx tsc -b
npx vite build --config vite.config.demo.ts --base ./ --outDir "$WORK/dist"
OUT="$ROOT/docs/explore"
find "$OUT" -mindepth 1 ! -name '*.json' -delete
cp -r "$WORK/dist/assets" "$WORK/dist/favicon.svg" "$OUT/"
cp "$SRC/LICENSE" "$OUT/LICENSE-understand-anything.txt"
# no third-party font requests: the site keeps its fonts local, so drop the Google Fonts links
python3 - "$WORK/dist/index.html" "$OUT/index.html" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
s = re.sub(r'\s*<link rel="preconnect"[^>]*/>', "", s)
s = re.sub(r'\s*<link\s+href="https://fonts\.googleapis\.com[^>]*/>', "", s, flags=re.S)
s = s.replace("<title>Understand Anything</title>", "<title>OpenGonio project map</title>\n    <meta name=\"description\" "
              "content=\"The OpenGonio project as a clickable map: big ideas, build stages, firmware, software, tools and "
              "docs, with a guided tour in plain words. Drawn with Understand-Anything (MIT).\">")
open(sys.argv[2], "w", encoding="utf-8").write(s)
PY
rm -rf "$WORK"
echo "docs/explore/ rebuilt; run make build to refresh knowledge-graph.json"
