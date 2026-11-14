# Rules for AI agents working in this repo

## After every change
**Never commit, amend, reset, tag or push.** Every commit in this repo is made by the owner. Leave changes uncommitted
(including `paper/build/opengonio.pdf` and `exports/`) and hand them over; the owner commits and pushes
(`bash scripts/update.sh "msg"`).

1. `make all` (build, checks, tests, paper, exports). Fix failures before handing over.
2. CAD changed: `make parts` and/or `make cad` first (STEP/STL, pictures, clash check, paper figures).
3. CI replay without committing here: copy the working tree to a scratch folder, commit there (throwaway), run `make ci`
   in that copy; fix the real files until it passes.

## Sources of truth (edit these; the rest is generated)
- Parts: `phases/*/bom.csv` → README Electronics / Mechanical / Printed / Tools tables (groups in `tools/bom_readme.py`), PARTS.md, budget, paper tables.
- References: `REFERENCES.md` → `paper/references.bib`, wiki Bibliography + appendices, README list.
- Steps: `.github/phases.yml` → stage checklists, issues.
- Wiki text: `wiki/src/*.md` → `wiki/*.md` (`make build`); publish with `bash scripts/publish_wiki.sh`.
- Geometry: `tools/cad/parts.py`, `tools/cad/bought.py`.
- Wiring: `docs/wiring.yaml` → README Wiring section, `docs/assets/wiring.svg` and one animated diagram per section in `docs/assets/wiring/` (`tools/wiring.py`; `make check` compares pins with `firmware/hub/main.py`).
- Website and app look: `docs/og/og.css` (tokens; DESIGN.md explains them) → copied into `software/src/opengonio/app/static/og/` by `make build`; website numbers come from `docs/site-data.js` (`tools/site_data.py`) and `docs/og/sim-examples.js` (`tools/make_assets.py`). Pictures: `tools/site_pictures.py`, README screenshots: `tools/readme_screens.py` (run by hand). Render page data: `tools/render_assets.py` (`make render`, by hand) → `docs/render-data.js`, `docs/assets/render/`.

## Writing
- Fewest words that stay precise. Tables and lists over prose.
- Write acronyms out once, with the short form in parentheses.
- Citations: APA 7 in wiki and paper (`[@ID]` in wiki sources, `\parencite{ID}` in LaTeX). Stage docs keep `[ID]`.
- Never invent links, part numbers, prices or results; mark unknowns `[TBD]`.

## Constraints
- Parts from Digi-Key, Amazon or Adafruit only (`make build` fails otherwise); cheapest that meets the spec; prices checked on the store page.
- No soldering, drilling, sawing or crimping. Printed parts: black ABS, enclosed printer.
- Built from printed parts, M2 screws and electronic modules: M2 for every printed join and module mount (pilots `M2_TAP`); M3 only into the NEMA 17 faces, M8 bolts as axles. No plywood, no extrusion, no breadboard, no loose chips. New deck mounts get a `PLACE` entry in `tools/cad/parts.py`.
- A carrier circuit board is a future option: keep `pcb/README.md` in step with the module wiring.
- Budget cap: `HARD_CAP` in `tools/bom_check.py`.

## Other software
- Never edit `exports/` by hand; edit the source named in `exports/README.md`.
- Edits made in Word, Google Docs or Overleaf go back into `paper/opengonio.tex` (or `wiki/src/`) by hand.
- README: only what a builder needs first (parts, build table, quick commands); details go in `wiki/src/`.
