#!/usr/bin/env python3
"""docs/explore/knowledge-graph.json: the whole project as a map a newcomer can click through (run by `make build`).

    python tools/explore_graph.py

The map is drawn by the Understand-Anything dashboard (MIT, docs/explore/, rebuilt by scripts/explore_dashboard.sh).
Everything in it comes from the repo: module and tool docstrings, stage titles and goals (.github/phases.yml), page
descriptions, wiki first lines, Python imports. Only the big-idea nodes, the data-flow edges between the sources of truth
and the tools, and the guided tour are written here, in plain words. No dates or commit hashes: output is reproducible.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "explore" / "knowledge-graph.json"
SW = ROOT / "software" / "src" / "opengonio"

# ---- big ideas, in plain words (the tour starts here)
IDEAS = {
    "brdf": ("What the machine measures",
             "How bright a material looks from every direction of light and view: its BRDF (bidirectional reflectance "
             "distribution function). Shiny plastic flashes where light bounces like a mirror; matte paint looks the same "
             "from everywhere. The machine records that pattern so a game engine or renderer can copy the real material."),
    "angles": ("Angles, not pictures",
               "The camera stays fixed. The lamp swings on an arm (motor M4); the sample table turns (M3), tilts (M2) and "
               "spins (M1). Each pose is a pair of angles: where the light comes from and where the camera sees from."),
    "run": ("One measurement, start to finish",
            "A plan lists the poses. The machine homes, moves to each pose, switches the lamp on and takes a bracket of "
            "photos. Everything is saved in a run folder with a manifest; `verify` checks it, `curve` turns pixels into "
            "numbers and `fit` finds the matching game material."),
    "calibration": ("Making the numbers true",
                    "A mirror finds where zero degrees really is. A dark frame removes the camera's own noise. A white "
                    "reference turns brightness into reflectance. Every run keeps a copy of the calibration it used."),
    "safety": ("Safety comes first",
               "One 24 V line runs through the e-stop and an over-travel switch. Pressing the e-stop cuts motor power in "
               "hardware; a small opto module tells the hub, which pauses the run and makes the machine home again."),
    "build": ("Built from modules, no solder",
              "Printed black ABS parts, M2 screws, plug-in electronic modules, screw terminals and lever connectors. No "
              "soldering, drilling, sawing or crimping. Parts come from Digi-Key, Amazon or Adafruit."),
    "truth": ("Edit one file, everything follows",
              "A few hand-edited files (parts lists, wiring, build steps, CAD) are the sources of truth. Tools regenerate "
              "the README tables, diagrams, build book, website and paper from them; `make check` proves they agree."),
}

# ---- where a file's own first line is too short to explain it
OVERRIDES = {
    "software/src/opengonio/cli.py": "The `opengonio` command: connect, home, move, capture a plan, verify a run, draw its "
                                     "curve, fit a material, run the simulator or open the control app.",
    "wiki/src/Repository-map.md": "Where everything lives in the repository: one folder per stage, the software, firmware, "
                                  "tools, website and paper, and which files are generated.",
    "wiki/src/Home.md": "The wiki's front page: what the machine measures, how it is built and where to go next.",
    "wiki/src/How-it-works.md": "How light, sample and camera angles combine into one measurement, explained with the "
                                "equations behind it.",
    "wiki/src/Theory.md": "The physics: what a BRDF is, the reflection equation, and the material models the software fits.",
    "wiki/src/Calibration.md": "How the machine finds its true zero angle, removes camera noise and turns brightness into "
                               "reflectance, and how often to repeat it.",
    "wiki/src/Build-guide.md": "The whole build in order, from setting up the repo and choosing parts to the last stage.",
    "wiki/src/Commands.md": "Every command you type, with what it does: setup, build, checks, capture, the simulator, the app.",
    "wiki/src/Test-materials.md": "The samples to measure first (mirror, white PTFE, matte paper, plastic) and what each "
                                  "result should look like.",
    "wiki/src/Machine.md": "The machine's layout: where the cameras sit, how each axis moves and how far.",
    "wiki/src/Hardware.md": "Every electrical connection and module: power, motor board, hub, lamp, USB.",
    "wiki/src/Software.md": "The Python software on the laptop: motion, camera, runs, checks, fitting and the control app.",
    "wiki/src/CAD.md": "The 3D models: printed parts, bought parts and the checks that nothing collides as the axes move.",
    "wiki/src/Extend.md": "How to change or add to the project: edit the source files, rebuild, check.",
    "wiki/src/Paper.md": "The research paper written from this project, and how it is built.",
    "wiki/src/3D-scanning.md": "Using the same machine as a 3D scanner: photos from known angles become a 3D model.",
    "wiki/src/Tools-and-joins.md": "The tools you need and how parts join without soldering, drilling or crimping.",
}

# ---- who reads what, who writes what (CLAUDE.md, "Sources of truth")
FLOWS = [
    ("file:tools/bom_readme.py", "reads_from", "config:phases/01-power/bom.csv", "parts lists → README tables"),
    ("file:tools/bom_readme.py", "writes_to", "document:README.md", ""),
    ("file:tools/bom_check.py", "validates", "config:phases/01-power/bom.csv", "stores, prices, budget cap"),
    ("file:tools/wiring.py", "reads_from", "config:docs/wiring.yaml", ""),
    ("file:tools/wiring.py", "writes_to", "document:docs/wiring.html", "diagrams and the wiring data"),
    ("file:tools/wiring.py", "writes_to", "document:README.md", "Wiring section"),
    ("file:tools/build_book.py", "reads_from", "config:docs/assembly.yaml", ""),
    ("file:tools/build_book.py", "writes_to", "document:docs/build.html", ""),
    ("file:tools/roadmap.py", "reads_from", "config:.github/phases.yml", "steps → stage checklists"),
    ("file:tools/refs_bib.py", "reads_from", "document:REFERENCES.md", ""),
    ("file:tools/refs_bib.py", "writes_to", "document:paper/opengonio.tex", "bibliography"),
    ("file:tools/site_data.py", "writes_to", "document:docs/index.html", "the numbers on the website"),
    ("file:tools/check.py", "validates", "config:docs/wiring.yaml", "pins match the hub firmware"),
    ("file:tools/check.py", "validates", "config:.github/phases.yml", ""),
    ("file:tools/explore_graph.py", "writes_to", "document:docs/explore/index.html", "this map"),
    ("file:software/src/opengonio/gantry/hub.py", "depends_on", "file:firmware/hub/main.py", "serial lines both sides agree on"),
    ("file:software/src/opengonio/gantry/fluidnc.py", "depends_on", "config:firmware/grblhal/settings.txt", "grblHAL on the SKR Pico"),
    ("document:docs/power.html", "documents", "module:phases/01-power", "wire the power, step by step"),
    ("document:docs/controller.html", "documents", "module:phases/02-controller", "wire the controller, step by step"),
]
IDEA_LINKS = {
    "brdf": ["file:software/src/opengonio/brdf/models.py", "file:software/src/opengonio/fit.py", "document:wiki/src/Theory.md"],
    "angles": ["file:software/src/opengonio/gantry/kinematics.py", "file:software/src/opengonio/plans/inplane.py",
               "file:software/src/opengonio/plans/hemisphere.py", "document:wiki/src/How-it-works.md"],
    "run": ["file:software/src/opengonio/cli.py", "file:software/src/opengonio/runrecord.py",
            "file:software/src/opengonio/verify.py", "file:software/src/opengonio/camera/uvc.py"],
    "calibration": ["file:software/src/opengonio/calibration.py", "file:software/src/opengonio/sim.py",
                    "module:phases/07-calibrate", "document:wiki/src/Calibration.md"],
    "safety": ["module:phases/01-power", "file:software/src/opengonio/gantry/safety.py",
               "file:software/src/opengonio/gantry/panel.py", "file:firmware/hub/main.py", "document:docs/power.html"],
    "build": ["module:phases/03-frame", "file:tools/cad/parts.py", "document:docs/build.html", "document:wiki/src/Tools-and-joins.md"],
    "truth": ["file:tools/check.py", "config:.github/phases.yml", "config:docs/wiring.yaml", "document:wiki/src/Repository-map.md"],
}
TOUR = [
    ("What this machine is", "A desk-sized instrument that measures how materials reflect light, printed and built from "
     "modules. Start with the two big ideas, then open the README.", ["concept:brdf", "concept:angles", "document:README.md"]),
    ("How one measurement happens", "A plan becomes poses, the machine moves and photographs, and a run folder keeps "
     "everything. Click each file to read what it does.", ["concept:run", "file:software/src/opengonio/plans/inplane.py",
     "file:software/src/opengonio/gantry/gantry.py", "file:software/src/opengonio/camera/uvc.py",
     "file:software/src/opengonio/runrecord.py", "file:software/src/opengonio/verify.py"]),
    ("Making the numbers true", "Calibration turns pictures into trustworthy numbers. The simulator rehearses the whole "
     "chain with no hardware.", ["concept:calibration", "file:software/src/opengonio/calibration.py",
     "file:software/src/opengonio/sim.py", "module:phases/07-calibrate"]),
    ("Built in small stages", "Each stage adds one working piece and ends with a check: power, controller, frame, light "
     "arm, table, camera and light, calibration.", ["concept:build"] + [f"module:phases/{s}" for s in
     ("00-plan", "01-power", "02-controller", "03-frame", "04-light-arm", "05-table", "06-camera-light")]),
    ("Power and safety first", "The first wires are the power and the e-stop. The walkthrough shows each wire on a drawing "
     "of the bench.", ["concept:safety", "module:phases/01-power", "document:docs/power.html",
     "file:software/src/opengonio/gantry/safety.py"]),
    ("Two small computers", "A motor board (SKR Pico, grblHAL) moves the axes; an ESP32-S3 hub reads the buttons and "
     "sensors. The laptop talks to both over USB.", ["file:firmware/hub/main.py", "config:firmware/grblhal/settings.txt",
     "file:software/src/opengonio/gantry/hub.py", "file:software/src/opengonio/gantry/fluidnc.py", "document:docs/controller.html"]),
    ("Driving it", "The same code runs behind the command line, the control app in the browser and the standalone station.",
     ["file:software/src/opengonio/cli.py", "file:software/src/opengonio/app/server.py", "file:software/src/opengonio/station.py"]),
    ("One source, many outputs", "Change a parts list or a wire in one file; the tools rebuild the README, diagrams, "
     "website and paper, and the checks prove they agree.", ["concept:truth", "config:.github/phases.yml",
     "config:docs/wiring.yaml", "file:tools/wiring.py", "file:tools/check.py"]),
    ("Beyond materials: 3D scans", "The same machine photographs an object from known angles and builds a 3D model of it.",
     [f"module:phases/{s}" for s in ("11-scan-capture", "12-scan-mesh", "13-object-material")] +
     ["file:software/src/opengonio/scan/run.py", "file:software/src/opengonio/scan/process.py"]),
]


# ---- how things happen, as flows of steps (the dashboard's Domain view)
DOMAINS = [
    ("measuring", "Measuring materials", "Turning a flat sample into numbers a renderer can use: calibrate once, then "
     "measure, check and fit.", [
        ("calibrate", "Calibrate the machine", "opengonio calibrate", [
            ("Home every axis", "The machine drives each axis to its home switch so every angle starts from a known place.",
             "software/src/opengonio/gantry/gantry.py"),
            ("Find true zero with a mirror", "A mirror sweep shows where the angle really is zero; the offset is saved.",
             "software/src/opengonio/calibration.py"),
            ("Measure the camera's darkness", "A photo with the lamp off records the camera's own noise, to subtract later.",
             "software/src/opengonio/calibration.py"),
            ("Measure a white reference", "A known white sample turns brightness into true reflectance.",
             "software/src/opengonio/calibration.py"),
        ]),
        ("measure", "Measure a sample", "opengonio capture", [
            ("Choose a plan", "A list of light and camera angles to visit.", "software/src/opengonio/plans/inplane.py"),
            ("Move, light and photograph", "At each pose the lamp comes on and the camera takes a bracket of exposures.",
             "software/src/opengonio/camera/uvc.py"),
            ("Save a run folder", "Images plus a manifest of every setting, so the run can be checked later.",
             "software/src/opengonio/runrecord.py"),
            ("Check the run", "`opengonio verify` checks the run is complete, the data valid and the lamp steady, and gives PASS or FAIL.",
             "software/src/opengonio/verify.py"),
            ("Draw the curve", "`opengonio curve` turns the pixels into brightness against angle.", "software/src/opengonio/cli.py"),
        ]),
        ("fit", "Fit a game material", "opengonio fit", [
            ("Read the curve", "The measured brightness at each angle.", "software/src/opengonio/fit.py"),
            ("Fit a material model", "Find the base colour, roughness and metalness that reproduce the curve.",
             "software/src/opengonio/brdf/models.py"),
            ("Save the result", "fit.json for the game engine and a chart to compare by eye.", "software/src/opengonio/plot.py"),
        ]),
    ]),
    ("building", "Building the machine", "Each stage adds one working piece and ends with a check before the next.", [
        ("power", "Power and safety", "manual", [
            ("Wire the power", "Adapter, jack, e-stop, over-travel switch and the two lever connectors.", "docs/power.html"),
            ("Check with the power off", "Meter checks: no short, e-stop and switch open the line.", "phases/01-power/README.md"),
            ("First power-on", "About 24 V on the motor line; the e-stop drops it to zero.", "phases/01-power/README.md"),
        ]),
        ("controller", "Bring up the controller", "manual", [
            ("Connect both boards", "Motor board and hub to the laptop over USB.", "docs/controller.html"),
            ("Flash the motor board", "grblHAL on the SKR Pico, with the machine's settings.", "firmware/grblhal/settings.txt"),
            ("Flash the hub", "MicroPython firmware on the ESP32-S3.", "firmware/hub/main.py"),
            ("Bench motor, keys, power sense", "One motor turns, each key prints its name, the e-stop is seen.",
             "docs/controller.html"),
        ]),
        ("axes", "Add the axes", "manual", [
            ("Frame", "Printed deck tiles bolted together.", "phases/03-frame/README.md"),
            ("Light arm", "The lamp's arm on its ring drive, homing on a switch.", "phases/04-light-arm/README.md"),
            ("Table", "The sample table turns.", "phases/05-table/README.md"),
            ("Camera and light", "Camera fixed, lamp on its driver.", "phases/06-camera-light/README.md"),
            ("Tilt and spin", "Two more axes: angles out of the plane, and samples that look different along and across.", "phases/08-tilt/README.md"),
        ]),
    ]),
    ("scanning", "3D scanning", "The same machine photographs an object from known angles and builds a 3D model.", [
        ("scan", "Scan an object", "opengonio scan", [
            ("Plan rings of views", "Positions all around the object.", "software/src/opengonio/scan/plan.py"),
            ("Photograph every view", "Known poses, so no guessing where the camera was.", "software/src/opengonio/scan/run.py"),
            ("Build the model", "Silhouettes, shading and photogrammetry make the 3D shape.", "software/src/opengonio/scan/process.py"),
        ]),
    ]),
]


def domain_graph(project: dict) -> dict:
    slug = lambda t: re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    nodes, edges = [], []
    for did, dname, dsum, flows in DOMAINS:
        nodes.append({"id": f"domain:{did}", "type": "domain", "name": dname, "summary": dsum, "tags": [], "complexity": "moderate"})
        for fid, fname, entry, steps in flows:
            nodes.append({"id": f"flow:{fid}", "type": "flow", "name": fname, "summary": f"{fname}: {len(steps)} steps.",
                          "tags": [], "complexity": "simple" if len(steps) < 4 else "moderate",
                          "domainMeta": {"entryPoint": entry, "entryType": "manual" if entry == "manual" else "cli"}})
            edges.append({"source": f"domain:{did}", "target": f"flow:{fid}", "type": "contains_flow", "direction": "forward", "weight": 1.0})
            for i, (sname, ssum, path) in enumerate(steps, 1):
                assert (ROOT / path).exists(), path
                sid = f"step:{fid}:{slug(sname)}"
                nodes.append({"id": sid, "type": "step", "name": sname, "summary": ssum, "tags": [], "complexity": "simple",
                              "filePath": path})
                edges.append({"source": f"flow:{fid}", "target": sid, "type": "flow_step", "direction": "forward",
                              "weight": round(i / (len(steps) + 1), 2)})
    for a, b, desc in (("building", "measuring", "a built and calibrated machine is what measures"),
                       ("measuring", "scanning", "the same axes and camera, used to photograph objects")):
        edges.append({"source": f"domain:{a}", "target": f"domain:{b}", "type": "cross_domain", "direction": "forward",
                      "description": desc, "weight": 0.6})
    return {"version": "1.0.0", "project": project, "nodes": nodes, "edges": edges, "layers": [], "tour": []}


def first_line(text: str) -> str:
    text = re.sub(r"\[[A-Z]+\d+\]|\[@[^\]]+\]", "", text or "").strip()
    line = " ".join(text.split("\n\n")[0].split())
    return line[:400]


def complexity(path: Path) -> str:
    n = sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))
    return "simple" if n < 150 else "moderate" if n < 450 else "complex"


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def main() -> None:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    layers: dict[str, list[str]] = {k: [] for k in ("ideas", "stages", "firmware", "software", "tools", "docs")}

    def node(nid, ntype, name, summary, tags, layer, path=None, cx="simple"):
        nodes[nid] = {"id": nid, "type": ntype, "name": name, "summary": summary or name, "tags": tags, "complexity": cx}
        if path:
            nodes[nid]["filePath"] = path
        layers[layer].append(nid)

    def edge(s, t, etype, desc="", w=0.6):
        if s in nodes and t in nodes and s != t:
            edges.append({"source": s, "target": t, "type": etype, "direction": "forward", "description": desc, "weight": w})

    for key, (name, text) in IDEAS.items():
        node(f"concept:{key}", "concept", name, text, ["start here"], "ideas")

    # stages: title, safety note and milestone goals from .github/phases.yml; parts lists beside them
    ph = yaml.safe_load((ROOT / ".github" / "phases.yml").read_text(encoding="utf-8"))
    goals: dict[str, list[str]] = {}
    for m in ph["milestones"]:
        goals.setdefault(m["stage"], []).append(m["goal"])
    for st in ph["stages"]:
        folder = st["folder"]
        g = goals.get(folder, [])
        summary = f"Stage {folder[:2]}: {st['title']}. " + " ".join(g[:3])
        if st.get("safety"):
            summary += f" Safety: {st['safety']}"
        nid = f"module:phases/{folder}"
        node(nid, "module", f"{folder[:2]} · {st['title']}", summary, ["stage", f"{len(g)} milestones"], "stages",
             f"phases/{folder}/README.md", "simple" if len(g) < 3 else "moderate")
        bom = ROOT / "phases" / folder / "bom.csv"
        if bom.is_file():
            rows = max(0, sum(1 for _ in bom.open(encoding="utf-8")) - 1)
            bid = f"config:phases/{folder}/bom.csv"
            node(bid, "config", f"Parts, stage {folder[:2]}", f"{rows} parts for stage {folder[:2]}: store, price, "
                 "the spec each part must meet. A source of truth for the README tables and the budget.",
                 ["parts list"], "stages", rel(bom))
            edge(nid, bid, "contains", "its parts list", 0.8)
    stage_ids = [f"module:phases/{s['folder']}" for s in ph["stages"]]
    for a, b in zip(stage_ids, stage_ids[1:]):
        edge(a, b, "depends_on", "comes before", 0.3)

    # firmware
    hub = ROOT / "firmware" / "hub" / "main.py"
    node("file:firmware/hub/main.py", "file", "Hub firmware (ESP32-S3)", first_line(ast.get_docstring(ast.parse(hub.read_text())) or "")
         or "MicroPython on the ESP32-S3: keypads, motor-power sense, sensors, OLED; talks to the laptop over USB serial.",
         ["firmware", "MicroPython"], "firmware", rel(hub), complexity(hub))
    node("config:firmware/grblhal/settings.txt", "config", "Motor board settings (grblHAL)",
         "The settings sent to grblHAL on the SKR Pico: steps per degree, speeds, homing, soft limits.",
         ["firmware", "grblHAL"], "firmware", "firmware/grblhal/settings.txt")

    # software modules: docstrings and imports
    mods = sorted(p for p in SW.rglob("*.py") if "__pycache__" not in p.parts)
    modname = {}
    for p in mods:
        tree = ast.parse(p.read_text(encoding="utf-8"))
        r = rel(p)
        sub = p.relative_to(SW).parts[0] if len(p.relative_to(SW).parts) > 1 else "core"
        name = p.name if p.name != "__init__.py" else f"{p.parent.name} (package)"
        node(f"file:{r}", "file", name, OVERRIDES.get(r) or first_line(ast.get_docstring(tree) or ""), ["software", sub], "software", r,
             complexity(p))
        dotted = ".".join(("opengonio",) + p.relative_to(SW).with_suffix("").parts).removesuffix(".__init__")
        modname[dotted] = f"file:{r}"
        for c in tree.body:
            if isinstance(c, ast.ClassDef) and ast.get_docstring(c) and not c.name.startswith("_"):
                cid = f"class:{r}:{c.name}"
                node(cid, "class", c.name, first_line(ast.get_docstring(c)), ["software", sub], "software", r)
                nodes[cid]["lineRange"] = [c.lineno, c.end_lineno or c.lineno]
                edge(f"file:{r}", cid, "contains", "", 0.5)
    for p in mods:
        r = rel(p)
        pkg = ".".join(("opengonio",) + p.relative_to(SW).parent.parts)
        for n in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(n, ast.ImportFrom):
                base = n.module or ""
                if n.level:
                    parts = pkg.split(".")
                    base = ".".join(parts[: len(parts) - n.level + 1] + ([base] if base else []))
                for cand in [base] + [f"{base}.{a.name}" for a in n.names]:
                    if cand in modname:
                        edge(f"file:{r}", modname[cand], "imports", "", 0.5)

    # tools: docstrings
    for p in sorted((ROOT / "tools").glob("*.py")) + [ROOT / "tools" / "cad" / "parts.py"]:
        d = first_line(ast.get_docstring(ast.parse(p.read_text(encoding="utf-8"))) or "")
        node(f"file:{rel(p)}", "file", p.name, d, ["tool"], "tools", rel(p), complexity(p))
    for path, name, text in (
        (".github/phases.yml", "Build steps", "Every stage, milestone and step with its checks: the source of the stage "
         "checklists and the progress on the website."),
        ("docs/wiring.yaml", "Wiring", "Every wire, pin by pin. The source of the wiring guide, the diagrams, the README "
         "Wiring section and both bench walkthroughs."),
        ("docs/assembly.yaml", "Assembly steps", "The order parts go together: the source of the build book."),
        ("software/config/machine.yaml", "Machine description", "Axes, limits, homing, lights and camera as data; the "
         "software reads it and the stages switch axes on as they are built."),
    ):
        node(f"config:{path}", "config", name, text, ["source of truth"], "tools", path)

    # documents: pages, wiki, paper
    for p in sorted((ROOT / "docs").glob("*.html")):
        t = p.read_text(encoding="utf-8")
        m = re.search(r'<meta name="description" content="([^"]*)"', t)
        title = re.search(r"<title>([^<]*)</title>", t)
        node(f"document:{rel(p)}", "document", title.group(1) if title else p.name, m.group(1) if m else "", ["website"],
             "docs", rel(p))
    node("document:docs/explore/index.html", "document", "This map", "The project as a clickable map, drawn from the repo "
         "by tools/explore_graph.py.", ["website"], "docs", "docs/explore/index.html")
    for p in sorted((ROOT / "wiki" / "src").glob("*.md")):
        if p.name.startswith("_"):
            continue
        body = re.sub(r"```.*?```", "", p.read_text(encoding="utf-8"), flags=re.S)
        lines = [ln for ln in body.splitlines() if len(ln.split()) > 6 and not ln.startswith(("#", "|", "!", "<", ">", "-", "**", "*", "$"))]
        summary = OVERRIDES.get(rel(p)) or first_line(re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", lines[0]) if lines else "")
        node(f"document:{rel(p)}", "document", f"Wiki: {p.stem.replace('-', ' ')}", summary, ["wiki"], "docs", rel(p))
    for path, name, text in (
        ("README.md", "README", "Start here: what the machine is, the parts lists, the build table and the quick commands."),
        ("REFERENCES.md", "References", "Every paper, datasheet and product page the design relies on; the source of the "
         "paper's bibliography."),
        ("paper/opengonio.tex", "Research paper", "The design written up for journal submission, with figures and "
         "evaluation plan; built to paper/build/opengonio.pdf."),
        ("DESIGN.md", "Design system", "Colours, type and components shared by the website and the control app."),
    ):
        node(f"document:{path}", "document", name, text, ["docs"], "docs", path)

    for key, targets in IDEA_LINKS.items():
        for t in targets:
            edge(f"concept:{key}", t, "related", "", 0.7)
    for s, etype, t, desc in FLOWS:
        edge(s, t, etype, desc, 0.8)

    tour = []
    for i, (title, text, ids) in enumerate(TOUR, 1):
        ids = [x for x in ids if x in nodes]
        tour.append({"order": i, "title": title, "description": text, "nodeIds": ids})
    names = {"ideas": ("Big ideas (start here)", "The few ideas that make the rest make sense."),
             "stages": ("Build stages and parts", "The machine built one working piece at a time, with its parts lists."),
             "firmware": ("Machine firmware", "What runs on the motor board and the hub."),
             "software": ("Laptop software", "Planning, moving, capturing, checking and fitting, in Python."),
             "tools": ("Sources of truth and tools", "The hand-edited files and the tools that rebuild everything from them."),
             "docs": ("Website, wiki and paper", "Everything written for readers and builders.")}
    graph = {
        "version": "1.0.0",
        "kind": "codebase",
        "project": {"name": "OpenGonio (Open Source Gonioreflectometer)", "languages": ["python", "javascript", "html", "css"],
                    "frameworks": ["grblHAL", "MicroPython", "CadQuery", "pytest"],
                    "description": "A printable, modular instrument that measures how materials reflect light, with the "
                                   "software, firmware, build guide, website and paper in one repository.",
                    "analyzedAt": "2026-11-10T00:00:00Z", "gitCommitHash": ""},
        "nodes": list(nodes.values()),
        "edges": edges,
        "layers": [{"id": f"layer:{k}", "name": names[k][0], "description": names[k][1], "nodeIds": v} for k, v in layers.items()],
        "tour": tour,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(graph, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    side = {"domain-graph.json": domain_graph(graph["project"]),
            "meta.json": {"lastAnalyzedAt": graph["project"]["analyzedAt"], "gitCommitHash": "", "version": "1.0.0",
                          "analyzedFiles": len(nodes)},
            "config.json": {"autoUpdate": False, "outputLanguage": "en"},
            "diff-overlay.json": {"changedNodeIds": [], "affectedNodeIds": []}}
    for name, data in side.items():
        (OUT.parent / name).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{rel(OUT)}: {len(nodes)} nodes, {len(edges)} edges, {len(tour)} tour steps")


if __name__ == "__main__":
    main()
