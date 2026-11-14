"""docs/inside.html data: the project's software, tests, firmware, wiring and roadmap, read from the sources.

Writes docs/inside-data.js (window.INSIDE). Nothing here is typed in by hand except the one-line meaning of each hub
command (checked against the firmware: a new command without a line here stops the build). Progress comes from
.github/progress.json (closed GitHub issues), so the page never shows a step as done that isn't closed.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "software" / "src" / "opengonio"
REPO = "https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/"

HUB_COMMANDS = {     # in: what each line does (the firmware is the truth; tools/inside_data.py checks the names match)
    "PING": "Health check. Answers PONG OpenGonio-hub 4 POWER n.",
    "POWER?": "Motor power from the opto module: POWER 1 on, POWER 0 off.",
    "SPEC?": "One AS7341 reading: SPEC #id, then 8 bands, clear and near-infrared counts.",
    "BATT?": "Power monitor (INA219, stage 17): source, volts, amps, watts, Wh used, OK / LOW / CRIT.",
    "SOURCE": "Which supply is in use: WALL, PACK or USBC with its Wh. Kept across restarts.",
    "ENC?": "Optional AS5600 angle encoders: ENC and one angle per I2C pair.",
    "BAND": "Colour LED bank band 0-7 or OFF. Not wired: the bank is blocked (wiring guide section 10).",
    "SHOW": "Text on the optional OLED and status screen: SHOW line 1|line 2|line 3.",
    "SCREEN": "SCREEN ON / OFF: the optional 2 in status screen; saved, and the hub restarts to take or free its pins.",
}
HUB_EVENTS = [
    ("BTN HOME | START | STOP | LIGHT | NEXT | PAUSE", "A key was pressed (debounced, once per press)."),
    ("POWER 0 | 1", "Motor power changed: e-stop, over-travel switch or adapter."),
    ("BATT ...", "Battery state changed; on CRIT the hub also sends BTN PAUSE."),
    ("ERR <message>", "A line it could not handle. Bad input never stops the hub."),
]
WALKS = {"1": "power.html", "2": "power.html", "3": "machine.html", "4": "machine.html", "5": "machine.html",
         "6": "controller.html", "7": "controller.html", "8": "machine.html"}


def first_para(doc: str | None) -> str:
    return re.sub(r"\s+", " ", (doc or "").strip().split("\n\n")[0]).strip()


def first_line(doc: str | None, limit: int = 200) -> str:
    """The first paragraph, cut at a sentence end (or a word) when longer than `limit`."""
    s = first_para(doc)
    if len(s) <= limit:
        return s
    cut = s[:limit]
    end = max(cut.rfind(". "), cut.rfind("; "))
    return cut[:end + 1] if end > 60 else cut.rsplit(" ", 1)[0] + "…"


def internal_imports(tree: ast.Module, mod: str) -> set[str]:
    """Module names inside opengonio that this file imports (relative or absolute)."""
    out, pkg = set(), mod.split(".")
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            if n.level:
                base = pkg[:len(pkg) - n.level] if not mod.endswith("__init__") else pkg[:len(pkg) - n.level + 1]
                name = ".".join(base + ([n.module] if n.module else []))
            else:
                name = n.module or ""
            if not name.startswith("opengonio"):
                continue
            for a in n.names:
                out.add(f"{name}.{a.name}" if (PKG.parent / f"{name}.{a.name}".replace(".", "/")).with_suffix(".py").exists()
                        or (PKG.parent / f"{name}.{a.name}".replace(".", "/")).is_dir() else name)
        elif isinstance(n, ast.Import):
            out |= {a.name for a in n.names if a.name.startswith("opengonio")}
    return {m for m in out if m not in (mod, "opengonio")}


def modules() -> list[dict]:
    out = []
    for f in sorted(PKG.rglob("*.py")):
        if "__pycache__" in f.parts:
            continue
        rel = f.relative_to(PKG.parent)
        mod = ".".join(rel.with_suffix("").parts)
        src = f.read_text(encoding="utf-8")
        tree = ast.parse(src)
        names = []
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and not n.name.startswith("_"):
                names.append({"name": n.name, "kind": "class" if isinstance(n, ast.ClassDef) else "function",
                              "doc": first_line(ast.get_docstring(n)), "line": n.lineno})
        if mod.endswith("__init__") and len(src.strip().splitlines()) < 3:
            continue
        out.append({"module": mod.removesuffix(".__init__"), "path": f"software/src/{rel.as_posix()}",
                    "group": mod.split(".")[1] if mod.count(".") > 1 else "core",
                    "doc": first_para(ast.get_docstring(tree)), "summary": first_line(ast.get_docstring(tree), 140), "lines": sum(1 for l in src.splitlines() if l.strip()),
                    "names": names, "imports": sorted(m.removesuffix(".__init__") for m in internal_imports(tree, mod))})
    return out


def tests(mods: list[dict]) -> list[dict]:
    known = {m["module"] for m in mods}
    out = []
    for f in sorted((ROOT / "software" / "tests").glob("test_*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        uses = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("opengonio"):
                for a in n.names:
                    full = f"{n.module}.{a.name}"
                    uses.add(full if full in known else n.module)
            elif isinstance(n, ast.Import):
                uses |= {a.name for a in n.names if a.name.startswith("opengonio")}
            elif isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "import_module" and n.args and \
                    isinstance(n.args[0], ast.Constant):
                uses.add(f"tools/{n.args[0].value}.py")
        tool_names = {t.stem for t in (ROOT / "tools").glob("*.py")}
        tools_used = set(re.findall(r"tools/(\w+)\.py", f.read_text(encoding="utf-8"))) & tool_names
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                tools_used |= {a.name for a in n.names} & tool_names
            elif isinstance(n, ast.ImportFrom) and n.module in tool_names and not n.level:
                tools_used.add(n.module)
        tools_used = sorted(f"tools/{t}.py" for t in tools_used)
        cases = [{"name": n.name, "says": n.name.removeprefix("test_").replace("_", " "), "doc": first_line(ast.get_docstring(n)),
                  "line": n.lineno}
                 for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
        out.append({"file": f"software/tests/{f.name}", "doc": first_para(ast.get_docstring(tree)), "cases": cases,
                    "covers": sorted(u for u in uses if u in known), "tools": tools_used})
    return out


def tool_list() -> list[dict]:
    make = (ROOT / "Makefile").read_text(encoding="utf-8")
    out = []
    for f in sorted((ROOT / "tools").glob("*.py")):
        doc = ast.get_docstring(ast.parse(f.read_text(encoding="utf-8")))
        out.append({"path": f"tools/{f.name}", "doc": first_line(doc), "in_build": f"tools/{f.name}" in make})
    return out


def hub() -> dict:
    src = (ROOT / "firmware" / "hub" / "main.py").read_text(encoding="utf-8")
    found = set(re.findall(r'parts\[0\] == "([^"]+)"', src)) | ({"SHOW"} if 'startswith("SHOW")' in src else set())
    if found != set(HUB_COMMANDS):
        raise SystemExit(f"tools/inside_data.py: hub commands {sorted(found)} != HUB_COMMANDS {sorted(HUB_COMMANDS)}")
    consts = {}
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1:
            t = n.targets[0]
            try:
                v = ast.literal_eval(n.value)
            except ValueError:
                continue
            if isinstance(t, ast.Name):
                consts[t.id] = v
            elif isinstance(t, ast.Tuple) and all(isinstance(e, ast.Name) for e in t.elts):
                consts.update({e.id: x for e, x in zip(t.elts, v)})
    pins = [{"gpio": v, "use": f"key {k}", "kind": "input"} for k, v in consts["BUTTONS"].items()]
    pins.append({"gpio": consts["SENSE_PIN"], "use": "motor-power sense (opto OUT, low = on)", "kind": "input"})
    pins += [{"gpio": s, "use": f"I2C pair {i + 1} SCL", "kind": "bus"} for i, (s, d) in enumerate(consts["I2C_PAIRS"])]
    pins += [{"gpio": d, "use": f"I2C pair {i + 1} SDA", "kind": "bus"} for i, (s, d) in enumerate(consts["I2C_PAIRS"])]
    pins += [{"gpio": consts["UART_TX"], "use": "UART to the Pi station: TX", "kind": "bus"},
             {"gpio": consts["UART_RX"], "use": "UART to the Pi station: RX", "kind": "bus"}]
    pins += [{"gpio": p, "use": f"colour LED band {i} (reserved, not wired)", "kind": "blocked"} for i, p in enumerate(consts["BAND_PINS"])]
    taken = {p["gpio"] for p in pins}
    pins += [{"gpio": g, "use": f"status screen {n} (SCREEN ON; else an encoder bus)", "kind": "bus"}
             for n, g in consts.get("SCREEN_PINS", {}).items() if g not in taken]
    for p in pins:
        if p["gpio"] in consts.get("SCREEN_PINS", {}).values() and "I2C" in p["use"]:
            p["use"] += " / status screen"
    i2c = [{"addr": f"0x{consts[k]:02X}", "part": part} for k, part in
           (("AS", "AS7341 spectral sensor (optional)"), ("INA", "INA219 power monitor (stage 17)"), ("AS5600", "AS5600 encoders (optional)"))]
    i2c.append({"addr": "0x3C", "part": "SSD1306 OLED (optional)"})
    return {"path": "firmware/hub/main.py", "runtime": "MicroPython " + (ROOT / "firmware/hub/MICROPYTHON_VERSION").read_text().strip(),
            "lines": sum(1 for l in src.splitlines() if l.strip()),
            "commands": [{"cmd": k, "does": v} for k, v in HUB_COMMANDS.items()],
            "events": [{"line": a, "does": b} for a, b in HUB_EVENTS],
            "pins": sorted(pins, key=lambda p: p["gpio"]), "i2c": i2c, "debounce_ms": consts["DEBOUNCE_MS"]}


def grbl() -> dict:
    lines = (ROOT / "firmware" / "grblhal" / "settings.txt").read_text(encoding="utf-8").splitlines()
    axes = {"0": "X", "1": "Y", "2": "Z", "3": "A"}
    per_axis = {"10": "steps per degree", "11": "max rate (deg/min)", "12": "acceleration (deg/s²)", "13": "travel (deg)",
                "14": "motor current (mA)", "15": "microsteps", "21": "hold current (%)"}
    general, axis_rows = [], {a: {"axis": a} for a in axes.values()}
    for l in lines:
        m = re.match(r"\$(\d+)=(\S+)\s*;\s*(.*)", l)
        if not m:
            continue
        num, val, note = m.groups()
        if len(num) == 3 and num[:2] in per_axis and num[2] in axes:
            row = axis_rows[axes[num[2]]]
            row[per_axis[num[:2]]] = val
            if num[:2] == "10":
                row["motor"] = note.split(":")[0].split("=")[-1].strip()
        else:
            general.append({"set": f"${num}={val}", "note": note})
    return {"path": "firmware/grblhal/settings.txt", "board": "BTT SKR Pico V1.0 (RP2040, 4 × TMC2209)",
            "general": general, "axes": list(axis_rows.values()), "columns": list(per_axis.values())}


def wiring() -> list[dict]:
    w = yaml.safe_load((ROOT / "docs" / "wiring.yaml").read_text(encoding="utf-8"))
    out = []
    for g in w["groups"]:
        n = g["title"].split(" · ")[0]
        rows = [r for r in g["rows"] if r[1] != "-"]
        out.append({"title": g["title"], "stage": str(g.get("stage", "")), "wires": len(rows),
                    "checks": len(g.get("checks", [])), "walk": WALKS.get(n), "blocked": "BLOCKED" in str(g.get("intro", ""))})
    return out


def roadmap() -> dict:
    d = yaml.safe_load((ROOT / ".github" / "phases.yml").read_text(encoding="utf-8"))
    prog = json.loads((ROOT / ".github" / "progress.json").read_text(encoding="utf-8"))
    closed = set(prog.get("closed", []))
    stages = []
    for s in d["stages"]:
        ms = []
        for m in (m for m in d["milestones"] if m["stage"] == s["folder"]):
            steps = [{"id": st["id"], "title": st["title"], "time": st.get("time", ""), "verify": st.get("verify") or [],
                      "done": st["id"] in closed} for st in m["steps"]]
            ms.append({"id": m["id"], "title": m["title"], "goal": m.get("goal", ""), "weeks": str(m.get("weeks", "")),
                       "steps": steps})
        stages.append({"folder": s["folder"], "title": s["title"], "milestones": ms,
                       "readme": f"phases/{s['folder']}/README.md"})
    return {"updated": prog.get("updated", ""), "closed": len(closed), "stages": stages}


def main() -> int:
    mods = modules()
    data = {"repo": REPO, "modules": mods, "tests": tests(mods), "tools": tool_list(), "hub": hub(), "grbl": grbl(),
            "wiring": wiring(), "roadmap": roadmap()}
    js = ("// Written by tools/inside_data.py (`make build`) from the sources: do not edit by hand.\n"
          "window.INSIDE = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    out = ROOT / "docs" / "inside-data.js"
    if not out.exists() or out.read_text(encoding="utf-8") != js:
        out.write_text(js, encoding="utf-8")
    n_tests = sum(len(t["cases"]) for t in data["tests"])
    print(f"docs/inside-data.js: {len(mods)} modules, {n_tests} tests, {len(data['hub']['commands'])} hub commands, "
          f"{sum(len(s['milestones']) for s in data['roadmap']['stages'])} milestones")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
