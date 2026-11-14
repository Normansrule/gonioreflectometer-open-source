#!/usr/bin/env python3
"""One health check for the whole repo: `make check` (or `python tools/check.py`).

Checks: milestones file, parts lists + budget, reference IDs, internal links, machine + calibration config, wiring pins,
simulator numbers (docs/machine.js) = machine.yaml.
Prints one line per problem and exits 1 if there are any.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "software" / "src"))
import bom_check  # noqa: E402

STEP_KEYS = {"id", "title", "do", "verify", "record"}
OPTIONAL_KEYS = {"time", "wait", "needs", "fail"}


def check_phases() -> list[str]:
    y = yaml.safe_load((ROOT / ".github/phases.yml").read_text(encoding="utf-8"))
    errs, folders = [], [s["folder"] for s in y["stages"]]
    for i, f in enumerate(folders):
        if not f.startswith(f"{i:02d}-"):
            errs.append(f"phases.yml: stage {f} should start with {i:02d}-")
        if not (ROOT / "phases" / f).is_dir():
            errs.append(f"phases.yml: folder phases/{f} missing (run: python tools/new.py stage …)")
    ids = [m["id"] for m in y["milestones"]]
    for d in sorted({i for i in ids if ids.count(i) > 1}):
        errs.append(f"phases.yml: milestone ID {d} used twice")
    order = [folders.index(m["stage"]) for m in y["milestones"] if m["stage"] in folders]
    if order != sorted(order):
        errs.append("phases.yml: milestones are not in stage order")
    for m in y["milestones"]:
        if not re.fullmatch(r"M\d{2,}", m["id"]):
            errs.append(f"phases.yml: bad milestone ID {m['id']} (use M<number>)")
        if m["stage"] not in folders:
            errs.append(f"phases.yml: {m['id']} stage {m['stage']} unknown")
        for k, s in enumerate(m["steps"], 1):
            if s.get("id") != f"{m['id']}.{k}":
                errs.append(f"phases.yml: step {s.get('id')} should be {m['id']}.{k}")
            missing = STEP_KEYS - set(s)
            if missing:
                errs.append(f"phases.yml: {s.get('id')} missing {sorted(missing)}")
            elif not s["do"] or not s["verify"]:
                errs.append(f"phases.yml: {s['id']} needs at least one Do and one Verify line")
            extra = set(s) - STEP_KEYS - OPTIONAL_KEYS
            if extra:
                errs.append(f"phases.yml: {s.get('id')} unknown keys {sorted(extra)} (allowed: {sorted(STEP_KEYS | OPTIONAL_KEYS)})")
            if "time" in s and not re.fullmatch(r"\d+(\.\d+)? (min|h)", str(s["time"])):
                errs.append(f"phases.yml: {s.get('id')} time '{s['time']}' must look like '45 min' or '1.5 h'")
            mid = re.search(r"make done id=(M[\d.]+)", str(s.get("record", "")))
            if mid and mid.group(1) != s.get("id"):
                errs.append(f"phases.yml: {s.get('id')} record says `make done id={mid.group(1)}`")
            if any("TODO" in str(x) for x in s.get("do", []) + s.get("verify", []) + s.get("fail", []) + s.get("needs", [])):
                errs.append(f"phases.yml: {s.get('id')} still has TODO lines")
    return errs


def check_bom() -> list[str]:
    boms = bom_check.load()
    errs = bom_check.validate(boms)
    total = sum(v["buy"] for v in bom_check.totals(boms).values())
    if total > bom_check.HARD_CAP:
        errs.append(f"budget: ${total:.2f} is over ${bom_check.HARD_CAP:.0f}")
    return errs


def md_files():
    for f in ROOT.rglob("*.md"):
        if not ({".git", ".venv", "vendor", "node_modules"} & set(f.parts)) and "papers/personal" not in str(f):
            yield f


def check_refs_and_links() -> list[str]:
    known = set(re.findall(r"^\|\s*\*\*([A-Z]\d+)\*\*", (ROOT / "REFERENCES.md").read_text(encoding="utf-8"), re.M))
    errs = []
    for f in md_files():
        t = f.read_text(encoding="utf-8")
        rel = f.relative_to(ROOT)
        if rel.parts[:2] == ("wiki", "src"):          # templates: {{REPO}} and wiki pages resolve after tools/refs_bib.py
            continue
        if f.name != "REFERENCES.md" and f != ROOT / "README.md":
            for r in sorted(set(re.findall(r"\[([A-Z]\d{1,3})\](?!\()", t)) - known):
                errs.append(f"{rel}: cites [{r}], not in REFERENCES.md")
        for link in re.findall(r"\]\(([^)\s]+)\)", t) + re.findall(r'src="([^"]+)"', t):
            path = link.split("#")[0].split("?")[0]
            if path and not link.startswith(("http", "mailto")) and not (f.parent / path).exists():
                errs.append(f"{rel}: broken link {link}")
    return errs


BAD_MACROS = ("\\operatorname", "\\DeclareMathOperator", "\\newcommand", "\\def", "\\renewcommand")


def check_math_and_parts() -> list[str]:
    """GitHub refuses some TeX macros ("The following macros are not allowed"); PARTS.md status words must be known."""
    errs = []
    for f in list(md_files()) + [ROOT / "docs" / "index.html", ROOT / "docs" / "lab.html"]:
        t = f.read_text(encoding="utf-8")
        for mac in BAD_MACROS:
            if mac in t:
                errs.append(f"{f.relative_to(ROOT)}: {mac} is not allowed on GitHub (use \\mathrm{{...}})")
    doc = ROOT / "PARTS.md"
    if doc.exists():
        import parts_doc
        for n, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            m = re.match(r"^- \[[ xX]\] \*\*([A-Z]{3}-\d+[a-z]?)\*\*.*?status:\s*(\S*)", line)
            if m and m.group(2) not in parts_doc.STATUSES:
                errs.append(f"PARTS.md line {n}: {m.group(1)} status '{m.group(2)}' unknown (use {' / '.join(parts_doc.STATUSES)})")
    return errs


def check_config() -> list[str]:
    errs = []
    try:
        from opengonio.gantry.config import load_config
        load_config()
    except Exception as exc:                       # noqa: BLE001
        errs.append(f"software/config/machine.yaml: {exc}")
    try:
        from opengonio.calibration import load_calibration
        load_calibration().offsets
    except Exception as exc:                       # noqa: BLE001
        errs.append(f"software/config/calibration.yaml: {exc}")
    try:
        import export_machine
        if (ROOT / "docs/machine.js").read_text(encoding="utf-8") != export_machine.text():
            errs.append("docs/machine.js differs from machine.yaml: run `make` (the simulator would show other numbers)")
    except FileNotFoundError:
        errs.append("docs/machine.js missing: run `make`")
    return errs


def check_wiring() -> list[str]:
    import wiring
    return wiring.check()


def check_build_book() -> list[str]:
    """docs/assembly.yaml: every CAD part in exactly one step, every checklist ref and line exists, build-book.js current."""
    import build_book
    data, errs = build_book.build()
    out = ROOT / "docs" / "build-book.js"
    if not errs and (not out.exists() or json.loads(out.read_text(encoding="utf-8").split("window.BOOK = ", 1)[1].rstrip(";\n")) != data):
        errs.append("docs/build-book.js is out of date (run `make build`)")
    return errs


def check_site() -> list[str]:
    """Website and control app: every local src/href resolves, and the app's copy of docs/og matches the original."""
    errs = []
    app = ROOT / "software" / "src" / "opengonio" / "app" / "static"
    for page in (ROOT / "docs" / "index.html", ROOT / "docs" / "lab.html", ROOT / "docs" / "wiring.html",
                 ROOT / "docs" / "power.html", ROOT / "docs" / "controller.html", ROOT / "docs" / "machine.html", ROOT / "docs" / "addons.html", ROOT / "docs" / "render.html", ROOT / "docs" / "inside.html", ROOT / "docs" / "app" / "index.html", ROOT / "docs" / "build.html", app / "index.html"):
        for ref in re.findall(r'(?:src|href)="([^"#?]+)', page.read_text(encoding="utf-8")):
            if re.match(r"^(https?:|mailto:|data:)", ref) or ref.startswith("/api/"):
                continue
            if not (page.parent / ref).exists():
                errs.append(f"{page.relative_to(ROOT)}: missing {ref}")
    for f in (ROOT / "docs" / "og").rglob("*"):
        rel = f.relative_to(ROOT / "docs" / "og")
        if f.is_file() and (rel.parts[0] == "fonts" or f.name in ("og.css", "og.js", "icon.svg", "render-gl.js")):
            twin = app / "og" / rel
            if not twin.exists() or twin.read_bytes() != f.read_bytes():
                errs.append(f"{twin.relative_to(ROOT)} differs from docs/og/{rel} (run `make build`)")
    import json
    guide = json.loads((ROOT / "docs" / "wiring-guide.js").read_text(encoding="utf-8").split("window.WIRING = ", 1)[1].strip().rstrip(";"))
    have = {(w["from"]["part"], w["from"]["pin"], w["to"]["part"], w["to"]["pin"])
            for g in guide["groups"] for w in g["wires"] if w.get("from") and w.get("to")}
    for walk in sorted((ROOT / "docs" / "og").glob("walk-*.js")):     # bench walkthroughs draw rows of wiring.yaml
        for st in json.loads(walk.read_text(encoding="utf-8").split("/*STEPS*/", 1)[1].split("/*END*/", 1)[0]):
            if st["type"] == "wire" and tuple(st["from"] + st["to"]) not in have:
                errs.append(f"docs/og/{walk.name}: '{st['title']}' is no longer a row in docs/wiring.yaml")
    rig = ROOT / "docs" / "og" / "model" / "rig.js"                 # the moving model must use today's axes and travel
    if rig.exists():
        import json
        sys.path.insert(0, str(ROOT / "tools" / "cad"))
        import poses
        from opengonio.gantry.config import load_config
        head = rig.read_text(encoding="utf-8").split("window.RIG = ", 1)[1].split(";\n", 1)[0]
        meta = json.loads(head)
        want = {k: {"point": list(pt), "dir": list(d), "moves": sorted(m)} for k, (pt, d, _, m) in poses.AXES.items()}
        if meta["axes"] != want or meta["shown"] != poses.SHOWN:
            errs.append("docs/og/model/rig.js axes differ from tools/cad/poses.py (run tools/site_model.py)")
        if meta["ranges"] != {k: [a.min_deg, a.max_deg] for k, a in load_config().axes.items()}:
            errs.append("docs/og/model/rig.js axis travel differs from machine.yaml (run tools/site_model.py)")
    return errs


def main() -> int:
    groups = {"milestones": check_phases, "parts + budget": check_bom, "references + links": check_refs_and_links,
              "machine config + simulator": check_config, "math macros + PARTS.md": check_math_and_parts,
              "wiring (docs/wiring.yaml vs firmware)": check_wiring, "build book (docs/assembly.yaml)": check_build_book,
              "website + app files": check_site}
    bad = 0
    for name, fn in groups.items():
        errs = fn()
        bad += len(errs)
        print(f"{'OK ' if not errs else 'ERR'} {name}" + ("" if not errs else f" ({len(errs)})"))
        for e in errs:
            print("    " + e)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
