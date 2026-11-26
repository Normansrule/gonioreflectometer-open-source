#!/usr/bin/env bash
# Submission copies of the paper (make paper-submit) -> paper/build/submission/ (git-ignored; nothing is uploaded):
#   opengonio-hardwarex.pdf   HardwareX manuscript with numbered references (the journal's printed style)
#   opengonio-source.zip      LaTeX source, numbered references: .tex + references.bib + generated tables + figures,
#                             no .bbl (arXiv runs biber itself; an uploaded .bbl must match its TeX Live). Upload to
#                             arXiv and to HardwareX (Editorial Manager accepts LaTeX source)
#   graphical_abstract.png    upload separately in Editorial Manager
#   joss/paper.md, paper.bib  JOSS software paper (preview: see below)
# Then prints the readiness report (tools/paper_check.py). Steps: roadmap milestone M50.
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=$( [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3 )
OUT=paper/build/submission
rm -rf "$OUT" && mkdir -p "$OUT/joss"

# 1. HardwareX PDF, numbered references
if command -v latexmk > /dev/null && command -v biber > /dev/null; then
  (cd paper && latexmk -r latexmkrc -outdir=build/submission -auxdir=build/submission -jobname=opengonio-hardwarex \
     -usepretex='\def\ogrefstyle{numeric}' -interaction=nonstopmode -halt-on-error -quiet opengonio.tex \
     > build/submission/latex.log 2>&1) || { tail -30 "$OUT/latex.log"; exit 1; }
  echo "$OUT/opengonio-hardwarex.pdf"
else
  echo "paper-submit: no latexmk/biber: skipped the PDF (sudo apt install latexmk biber texlive-publishers texlive-bibtex-extra texlive-latex-extra)"
fi

# 2. source zip: only what the manuscript reads, numbered style baked in
figs=$(grep -o '\\includegraphics\[[^]]*\]{[^}]*}' paper/opengonio.tex | sed 's/.*{\(.*\)}/figures\/\1/')
SRC="$OUT/source" && mkdir -p "$SRC"
(cd paper && cp --parents references.bib generated/*.tex $figs "../$SRC/")
sed 's/\\providecommand{\\ogrefstyle}{apa}/\\providecommand{\\ogrefstyle}{numeric}/' paper/opengonio.tex > "$SRC/opengonio.tex"
grep -q 'ogrefstyle}{numeric}' "$SRC/opengonio.tex" || { echo "paper-submit: reference-style line not found in opengonio.tex"; exit 1; }
(cd "$SRC" && zip -q -X -r ../opengonio-source.zip .) && rm -rf "$SRC"
echo "$OUT/opengonio-source.zip ($(unzip -l "$OUT/opengonio-source.zip" | tail -1 | awk '{print $2}') files)"

# 3. graphical abstract and JOSS files
[ -f paper/figures/graphical_abstract.png ] && cp paper/figures/graphical_abstract.png "$OUT/" && echo "$OUT/graphical_abstract.png"
"$PY" tools/joss_bib.py > /dev/null
cp paper/joss/paper.md paper/joss/paper.bib "$OUT/joss/"
echo "$OUT/joss/ (preview: docker run --rm -v \"\$PWD/paper/joss\":/data -u \$(id -u):\$(id -g) openjournals/inara -o pdf paper.md)"
echo
"$PY" tools/paper_check.py
