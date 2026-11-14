# OpenGonio framework commands. Run `make help`.
# SPDX-License-Identifier: GPL-3.0-or-later
PY := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)
m ?= update

.PHONY: help setup build check test parts cad cad-check cad-zip publish all sim render release done next paper export ci

help:            ## list commands
	@grep -E '^[a-z-]+:.*## ' Makefile | sed 's/:.*## /\t/'

setup:           ## once: .venv with the software, tests and tools
	python3 -m venv .venv
	.venv/bin/pip install -q -e "./software[dev]" pyyaml numpy openpyxl pillow
	@echo "done. optional for 3D parts: .venv/bin/pip install cadquery numpy-stl matplotlib"

build:           ## regenerate checklists, README tables, figures, budgets, 3D index (+ apply PARTS.md decisions)
	$(PY) tools/part_images.py > /dev/null
	$(PY) tools/parts_doc.py
	$(PY) tools/roadmap.py
	$(PY) tools/export_machine.py > /dev/null
	cp software/config/machine.yaml software/src/opengonio/data/machine.yaml   # packaged copy (wheel installs)
	$(PY) tools/bom_check.py
	$(PY) tools/power_budget.py > /dev/null
	$(PY) tools/grblhal_settings.py
	$(PY) tools/optics.py > /dev/null
	$(PY) tools/make_assets.py > /dev/null
	$(PY) tools/wiring.py
	$(PY) tools/build_book.py
	$(PY) tools/explore_graph.py
	$(PY) tools/inside_data.py
	$(PY) tools/site_app.py
	$(PY) tools/cad/index.py
	$(PY) tools/cad/catalog.py
	$(PY) tools/bom_readme.py
	$(PY) tools/refs_bib.py
	$(PY) tools/site_data.py > /dev/null
	mkdir -p software/src/opengonio/app/static/og/fonts   # the app shares the website's tokens, script and fonts
	cp docs/og/og.css docs/og/og.js docs/og/icon.svg docs/og/render-gl.js software/src/opengonio/app/static/og/
	cp docs/og/fonts/* software/src/opengonio/app/static/og/fonts/

parts:           ## regenerate every printed part (STEP + STL) and the parts picture (needs cadquery)
	$(PY) tools/cad/parts.py
	$(PY) tools/cad/deck_map.py
	$(PY) tools/cad/index.py
	$(PY) tools/cad/gallery.py
	$(PY) tools/part_images.py --stl
	$(PY) tools/cad/printability.py
	$(PY) tools/bom_readme.py

cad:             ## dummy models of bought parts (cad/bought), whole-machine assembly STEP, cad/README.md, clash check (needs cadquery)
	$(PY) tools/cad/bought.py > /dev/null
	$(PY) tools/part_images.py --stl
	$(PY) tools/cad/assembly.py
	$(PY) tools/paper_assets.py --figures
	$(PY) tools/exports.py --cad
	$(PY) tools/cad/catalog.py
	$(PY) tools/bom_readme.py
	$(PY) tools/cad/interference.py
	$(PY) tools/site_model.py           # the website's moving four-axis model (docs/og/model/rig.js)

cad-check:       ## interference check of the assembly: shown pose + every axis across its travel (needs cadquery)
	$(PY) tools/cad/interference.py

cad-zip:         ## every STEP (printed + bought + open + assembly) in dist/opengonio-cad.zip, for Onshape import
	mkdir -p dist && rm -f dist/opengonio-cad.zip
	$(PY) -m zipfile -c dist/opengonio-cad.zip cad/README.md cad/bought cad/open cad/assembly $$(ls phases/*/3d/*.step)
	@echo "dist/opengonio-cad.zip ($$(du -h dist/opengonio-cad.zip | cut -f1))"

check:           ## milestones, parts lists, budget, references, links, machine config
	$(PY) tools/check.py

test:            ## software tests
	$(PY) -m pytest -q software

paper:           ## paper/build/opengonio.pdf (LaTeX + biber; skipped if latexmk is missing)
	$(PY) tools/refs_bib.py > /dev/null
	$(PY) tools/paper_assets.py
	@if command -v latexmk > /dev/null && command -v biber > /dev/null; then \
	  cd paper && SOURCE_DATE_EPOCH=$$(git log -1 --format=%ct -- . ':!build' ':!generated' ':!figures' ':!references.bib' ../REFERENCES.md ../tools 2>/dev/null || echo 0) FORCE_SOURCE_DATE=1 latexmk -g -r latexmkrc -interaction=nonstopmode -halt-on-error -quiet opengonio.tex > build.log 2>&1 \
	  && echo "paper/build/opengonio.pdf" || (tail -30 build.log; exit 1); \
	else echo "paper: skipped (sudo apt install latexmk biber texlive-publishers texlive-bibtex-extra texlive-latex-extra)"; fi

export:          ## exports/: Word + Overleaf paper, Zotero refs, Excel BOM, wiki PDF/Word, build book PDF (needs pandoc; see exports/README.md)
	$(PY) tools/exports.py

ci:              ## replay the GitHub checks (clean clone, fresh venv) before pushing; tests HEAD
	bash scripts/ci_local.sh

all: build check test paper export   ## everything before a commit

render:          ## offline graphics pipeline (simulated fit + scan) -> docs/render-data.js, docs/assets/render/
	$(PY) tools/render_assets.py

sim:             ## simulated machine: capture -> verify -> calibrate -> curve, ends with ALL PASS
	$(PY) -m opengonio.cli sim-demo --out data/sim

release:         ## after a stage passes:  make release s=06  (tag v0.6 + 3D files zip on GitHub)
	bash scripts/release.sh "$(s)"

publish: all     ## commit + push + sync GitHub milestones/issues:  make publish m="what changed"
	bash scripts/update.sh "$(m)"

done:            ## a step passed its Verify:  make done id=M05.1  (closes the issue, ticks it everywhere, publishes)
	$(PY) tools/roadmap.py --close "$(id)"
	bash scripts/update.sh "$(id) done"

next:            ## print the next step to do
	@$(PY) -c "import sys; sys.path.insert(0,'tools'); import roadmap, roadmap_svg; st, ms = roadmap.load(); n = roadmap_svg.next_step(ms, roadmap.done_steps()); print(f'{n[1][\"id\"]} {n[1][\"title\"]} ({n[1].get(\"time\",\"\")}) -> phases/{n[0][\"stage\"]}/README.md' if n else 'all done')"
