#!/usr/bin/env python3
"""Is the paper ready to submit? Checks every venue in paper/submission.yaml.

    python tools/paper_check.py           readiness report (exit 0; blockers are listed, not failures)
    python tools/paper_check.py --strict  exit 1 on structural errors only (run by `make check`)
    python tools/paper_check.py --sync    CITATION.cff version = opengonio.__version__, JOSS paper.bib (run by `make build`)

Structural errors (fixable now, so they fail `make check`): a required section or specifications row missing, the AI
declaration not directly above the references, paper/results.yaml rows that name an unknown roadmap step, JOSS
paper.md out of its word range or missing a section, CITATION.cff out of step with the package version.
Blockers (need the machine or the author): [TBD] markers, unmeasured validation rows, no archive DOI, ORCID.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def short(s: str, n: int = 110) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


def step_ids() -> set[str]:
    y = yaml.safe_load((ROOT / ".github" / "phases.yml").read_text(encoding="utf-8"))
    return {s["id"] for m in y["milestones"] for s in m["steps"]}


def tex_sections(tex: str) -> list[str]:
    return [re.sub(r"\\label\{[^}]*\}", "", s).strip() for s in re.findall(r"\\section\*?\{([^}]*)\}", tex)]


def md_sections(md: str) -> list[str]:
    body = md.split("\n---\n", 1)[-1] if md.startswith("---") else md
    return [h.strip() for h in re.findall(r"^#\s+(.+)$", body, re.M)]


def md_words(md: str) -> int:
    body = md.split("\n---\n", 1)[-1] if md.startswith("---") else md
    body = re.sub(r"^#\s+References\s*$.*", "", body, flags=re.M | re.S)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)|\[@[^\]]*\]|<!--.*?-->", " ", body, flags=re.S)
    return len(re.findall(r"[A-Za-z0-9][\w'’.-]*", body))


def hardwarex(v: dict, sub: dict, errs: list, blocks: list) -> None:
    tex = (ROOT / v["manuscript"]).read_text(encoding="utf-8")
    have = tex_sections(tex)
    for s in v["sections"]:
        if s not in have:
            errs.append(f"hardwarex: section '{s}' missing from {v['manuscript']}")
    ai = "Declaration of generative AI and AI-assisted technologies in the writing process"
    if ai in have and not re.search(re.escape(ai) + r"\}.*?\\printbibliography", tex, re.S) or \
            ai in have and re.search(re.escape(ai) + r"\}.*?\\section", tex.split("\\printbibliography")[0], re.S):
        errs.append("hardwarex: the AI declaration must be the last section, directly above the references")
    specs = (PAPER / "generated" / "specs.tex").read_text(encoding="utf-8")
    for r in v["spec_rows"]:
        if not re.search(rf"^{re.escape(r)} &", specs, re.M):
            errs.append(f"hardwarex: specifications row '{r}' missing (tools/paper_assets.py)")
    for t in sorted(set(re.findall(r"\\tbd\{((?:[^{}]|\{[^{}]*\})*)\}", tex))):
        blocks.append(f"hardwarex: [TBD] {short(t)}")
    if not (sub.get("archive") or {}).get("zenodo_doi"):
        blocks.append("hardwarex: no archive DOI yet (M50.1): set archive.zenodo_doi in paper/submission.yaml")
    if not (PAPER / "figures" / "graphical_abstract.png").is_file():
        blocks.append("hardwarex: paper/figures/graphical_abstract.png missing (python tools/paper_assets.py --figures)")


def results(errs: list, blocks: list) -> None:
    ids = step_ids()
    seen = set()
    for r in yaml.safe_load((PAPER / "results.yaml").read_text(encoding="utf-8")):
        for k in ("id", "group", "what", "step", "criterion"):
            if not r.get(k):
                errs.append(f"results.yaml: {r.get('id', '?')} needs '{k}'")
        if r.get("id") in seen:
            errs.append(f"results.yaml: {r['id']} used twice")
        seen.add(r.get("id"))
        if r.get("step") not in ids:
            errs.append(f"results.yaml: {r.get('id')} names unknown roadmap step {r.get('step')}")
        if r.get("value") is None:
            blocks.append(f"validation: {r['id']} {r['what']} (step {r['step']})")


def joss(v: dict, errs: list, blocks: list) -> None:
    p = ROOT / v["manuscript"]
    if not p.is_file():
        errs.append(f"joss: {v['manuscript']} missing")
        return
    md = p.read_text(encoding="utf-8")
    have = md_sections(md)
    for s in v["sections"]:
        if s not in have:
            errs.append(f"joss: section '# {s}' missing from {v['manuscript']}")
    n, (lo, hi) = md_words(md), v["words"]
    if not lo <= n <= hi:
        errs.append(f"joss: paper.md has {n} words; JOSS asks {lo}-{hi}")
    meta = yaml.safe_load(md.split("---")[1]) if md.startswith("---") else {}
    for k in ("title", "tags", "authors", "affiliations", "date", "bibliography"):
        if k not in meta:
            errs.append(f"joss: paper.md front matter needs '{k}'")
    if not (p.parent / meta.get("bibliography", "paper.bib")).is_file():
        errs.append("joss: paper.bib missing (python tools/joss_bib.py)")
    for t in sorted(set(re.findall(r"\[TBD:?\s*([^\]]*)\]", md))):
        blocks.append(f"joss: [TBD] {short(t)}")
    if not (ROOT / "CONTRIBUTING.md").is_file():
        errs.append("joss: CONTRIBUTING.md (community guidelines) missing")


def citation(errs: list, blocks: list, sub: dict) -> None:
    sys.path.insert(0, str(ROOT / "software" / "src"))
    from opengonio import __version__
    c = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    if str(c.get("version")) != __version__:
        errs.append(f"CITATION.cff: version {c.get('version')} != opengonio {__version__}")
    if c.get("repository-code") != (sub.get("archive") or {}).get("repository"):
        errs.append("CITATION.cff: repository-code differs from paper/submission.yaml archive.repository")
    if not (sub.get("author") or {}).get("orcid"):
        blocks.append("author: ORCID iD not set (paper/submission.yaml author.orcid; journals ask for it)")


def sync() -> int:
    sys.path.insert(0, str(ROOT / "software" / "src"))
    from opengonio import __version__
    cff = ROOT / "CITATION.cff"
    text = cff.read_text(encoding="utf-8")
    new = re.sub(r'^version: ".*"$', f'version: "{__version__}"', text, flags=re.M)
    if new != text:
        cff.write_text(new, encoding="utf-8")
        print(f"CITATION.cff: version {__version__}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="exit 1 on structural errors (blockers never fail)")
    ap.add_argument("--sync", action="store_true", help="copy the package version into CITATION.cff")
    a = ap.parse_args()
    if a.sync:
        return sync()
    sub = yaml.safe_load((PAPER / "submission.yaml").read_text(encoding="utf-8"))
    errs: list[str] = []
    blocks: list[str] = []
    for v in sorted(sub["venues"], key=lambda v: v["order"]):
        {"hardwarex": hardwarex, "joss": lambda v, s, e, b: joss(v, e, b), "arxiv": lambda *x: None}[v["id"]](v, sub, errs, blocks)
    results(errs, blocks)
    citation(errs, blocks, sub)
    if a.strict:
        for e in errs:
            print("paper:", e)
        return 1 if errs else 0
    print("Paper readiness (paper/submission.yaml)\n")
    print("Structural: " + ("OK" if not errs else f"{len(errs)} to fix"))
    for e in errs:
        print("  ✗", e)
    val = [b for b in blocks if b.startswith("validation:")]
    other = [b for b in blocks if not b.startswith("validation:")]
    total = len(yaml.safe_load((PAPER / "results.yaml").read_text(encoding="utf-8")))
    print(f"\nValidation: {total - len(val)} of {total} measured")
    for b in val:
        print("  ·", b.split(": ", 1)[1])
    print(f"\nOther blockers: {len(other)}")
    for b in other:
        print("  ·", b)
    print("\nReady to submit: " + ("yes" if not errs and not blocks else "not yet") + " (steps: roadmap milestone M50)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
