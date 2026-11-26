# Paper

Three publications, one source of truth each. PDF: [build/opengonio.pdf](build/opengonio.pdf). Steps: roadmap milestone **M50** (`.github/phases.yml`, stage 16-release).

| Order | Venue | What | Source | Waits for |
|---|---|---|---|---|
| 1 | arXiv (physics.ins-det, cross-list cs.GR) | preprint of the hardware article | `opengonio.tex` | Zenodo DOI, validation table, endorsement |
| 2 | *HardwareX* (Elsevier) | peer-reviewed hardware article | `opengonio.tex` | same, plus graphical abstract |
| 3 | Journal of Open Source Software (JOSS) | software paper for `opengonio` | `joss/paper.md` | real measurements for the research impact statement |

## Files

| File | What | Edit? |
|---|---|---|
| `opengonio.tex` | manuscript (HardwareX sections, `elsarticle` class) | yes |
| `submission.yaml` | venue rules, required sections, archive DOI, ORCID | yes |
| `results.yaml` | validation rows V1–V14: criterion, roadmap step, measured value (`null` until measured) | yes, only with measured values |
| `joss/paper.md` | JOSS paper (750–1750 words) | yes |
| `joss/paper.bib` | cited entries only (`tools/joss_bib.py`) | no |
| `references.bib` | from [REFERENCES.md](../REFERENCES.md) (`tools/refs_bib.py`) | no |
| `generated/` | specifications, design files, bill of materials, validation tables, numbers (`tools/paper_assets.py`) | no |
| `figures/` | assembly render, diagrams (`make cad`), graphical abstract (`tools/paper_assets.py --figures`) | no |
| `apa.csl` | APA 7th edition style for the wiki bibliography (CSL project, CC BY-SA 3.0) | no |
| `build/` | output; only `opengonio.pdf` is committed | no |

Also: [CITATION.cff](../CITATION.cff) (version synced from `opengonio.__version__` by `make build`), [CONTRIBUTING.md](../CONTRIBUTING.md) (JOSS asks for community guidelines).

## Commands

| Command | Does |
|---|---|
| `make paper` | builds `build/opengonio.pdf` (APA 7 citations, as in the wiki) |
| `make paper-check` | readiness report: structure, "N of 14 measured", every `[TBD]`, DOI, ORCID |
| `make paper-submit` | `build/submission/`: HardwareX PDF with numbered references, `opengonio-source.zip` (arXiv and HardwareX upload, no `.bbl`), graphical abstract, JOSS files |
| `make check` | runs `tools/paper_check.py --strict`: fails only on structural errors (missing section, AI declaration out of place, unknown roadmap step), never on `[TBD]`s |

Needs `latexmk`, `biber`, `texlive-publishers`, `texlive-bibtex-extra`, `texlive-latex-extra`. JOSS preview: Docker image `openjournals/inara` (command printed by `make paper-submit`).

## Rules

- A value goes into `results.yaml` only after it was measured and recorded in that step's `design.md` → Results. A failed criterion is reported, not dropped.
- Unknowns stay red `\tbd{…}` in LaTeX and `[TBD]` in Markdown; `make paper-check` lists them.
- AI declaration: last section before the references (Elsevier policy); author confirms tools and scope before submission.
- Venue rules change: before each submission re-read the guide linked in `submission.yaml` → `sources` and update the file.

## Author steps (cannot be automated)

1. Zenodo: sign in with GitHub, switch the repository on, tag a release → DOI into `submission.yaml`.
2. ORCID iD into `submission.yaml`.
3. Measurements M18–M44 → `results.yaml`.
4. Confirm the AI declaration text and acknowledgements.
5. arXiv endorsement (physics.ins-det), then submit in the order above.
