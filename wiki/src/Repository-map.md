# Repository map

```
README.md            this guide
CLAUDE.md            rules for AI agents: update + build + commit the PDF after every change
PARTS.md             your working parts list: decisions, paid, notes (edit on GitHub)
Makefile             make help · setup · build · parts · cad · cad-check · cad-zip · check · test · paper · export · ci · all · sim · next · done · release · publish
REFERENCES.md        487 sources (also listed below)
phases/NN-name/      one folder per stage
  README.md          checklist: Do / Verify / Record (generated)
  design.md          how it is built (wiring, dimensions, notes)
  research.md        why (requirements, methods)
  bom.csv            parts to buy, prices, links
  test.csv           test log you fill in
  3d/                printed parts: .step (Onshape) + .stl (slicer)
cad/                README.md (model per part) · PRINT.md (print list) · bought/ dummies · open/ open models · assembly/ whole machine · vendor/ (local)
pcb/                 carrier circuit board: reference spec for a future version (README.md)
firmware/            grblHAL settings (SKR Pico) · FluidNC config (ESP32-board option) · MicroPython hub (ESP32-S3)
software/            opengonio: control, capture, calibration, simulator, scanning
  config/            machine.yaml (built) · calibration.yaml (measured)
tools/               check.py (health) · new.py (add things) · roadmap, BOM, figures, CAD parts, deck map, export_machine
scripts/             controller.sh · hub.sh · e4.sh · station.sh · publish.sh · update.sh · release.sh · get_papers.sh · get_cad.sh
docs/                interactive simulator (index.html, machine.js, plan.js) + figures (assets/, assets/steps/NN.svg)
exports/             Word, Overleaf, Zotero, Excel, wiki PDF, glTF copies (generated; see exports/README.md)
paper/               HardwareX manuscript: opengonio.tex · references.bib (generated) · build/opengonio.pdf
wiki/                explanations, Bibliography (APA), Appendices A–F · src/ = sources · scripts/publish_wiki.sh
papers/              PDFs: open/ (committed) · personal/ (local only)
data/                measurement jobs: manifest.json, curve.csv, spectral.csv (images stay local; data/sim/ not committed)
.github/phases.yml   stages + milestones (source of every checklist and issue)
.github/progress.json  closed steps, pulled from GitHub by `make done` / `make publish`
```
