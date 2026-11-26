# Paper

Four publications from [paper/]({{REPO}}/paper); plan and rules in [paper/README.md]({{REPO}}/paper/README.md), steps in roadmap milestone M50.

| Order | Venue | What | Source |
|---|---|---|---|
| 1 | arXiv | preprint | `paper/opengonio.tex` |
| 2 | *HardwareX* (Elsevier) | peer-reviewed hardware article | `paper/opengonio.tex` |
| 3 | Journal of Open Source Software (JOSS) | software paper | `paper/joss/paper.md` |
| 4 | *Virtual Reality* (Springer) | AR / VR training tool and two-headset comparison (draft; no results yet) | `paper/xr/opengonio-xr.tex`, [XR training](XR-training.md) |

- PDF: [paper/build/opengonio.pdf]({{REPO}}/paper/build/opengonio.pdf), rebuilt by `make paper` on every change; citations APA 7 here, numbered in the HardwareX copy (`make paper-submit`).
- Validation table: rows V1–V14 in `paper/results.yaml`, each tied to a roadmap step; empty until measured. `make paper-check` shows what is still missing.
- Archive: every release goes to Zenodo for a DOI ([CITATION.cff]({{REPO}}/CITATION.cff) gives the citation).
- Edit elsewhere: [Word]({{REPO}}/exports/paper/opengonio.docx) · [Overleaf zip]({{REPO}}/exports/paper/opengonio-overleaf.zip) · references for [Zotero]({{REPO}}/exports/references); copy edits back into `paper/opengonio.tex`.
