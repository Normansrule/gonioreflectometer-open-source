#!/usr/bin/env python3
"""Wiring tables and diagram from docs/wiring.yaml (the source of truth for every connection).

    python tools/wiring.py            # README "Wiring" block, docs/assets/wiring.svg, docs/assets/wiring/wiring-NN.svg,
                                      # docs/wiring-guide.js (the step-by-step guide page docs/wiring.html)
    python tools/wiring.py --check    # pins vs firmware/hub/main.py, SKR Pico map, machine.yaml; header pins used twice

Pin maps: SKR Pico V1.0 maker pin diagram [C12]; ESP32-S3-DevKitC-1 v1.1 user guide, headers J1/J3 [R86];
Raspberry Pi 40-pin header [H51].
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "wiring.yaml"
README = ROOT / "README.md"
SVG = ROOT / "docs" / "assets" / "wiring.svg"
HUB_FW = ROOT / "firmware" / "hub" / "main.py"
MACHINE = ROOT / "software" / "config" / "machine.yaml"
START, END = "<!-- wiring:start -->", "<!-- wiring:end -->"

# ---- pin maps -------------------------------------------------------------------------------------------------
MOTOR = ["2B", "1B", "1A", "2A"]
SKR_REF = r"(?:SKR:)?\b(X|Y|Z1|Z2|E|X-STOP|Y-STOP|Z-STOP|E0-STOP|RGB|HE|HB|FAN[123]|POWER)\.([A-Za-z0-9/+-]+)"
SKR = {**{p: MOTOR for p in ("X", "Y", "Z1", "Z2", "E")},
       "X-STOP": ["IO4", "GND", "5V"], "Y-STOP": ["IO3", "GND", "5V"], "Z-STOP": ["IO25", "GND", "5V"],
       "E0-STOP": ["IO16", "GND", "5V"], "RGB": ["GND", "IO24", "5V"],
       "HE": ["IO23", "12/24V"], "HB": ["IO21", "12/24V"], "FAN1": ["IO17", "12/24V"], "FAN2": ["IO18", "12/24V"],
       "FAN3": ["IO20", "12/24V"], "POWER": ["GND", "12/24V"], "USB-C": []}
STOP_AXIS = {"X-STOP": "X", "Y-STOP": "Y", "Z-STOP": "Z", "E0-STOP": "A"}   # grblHAL limit inputs [R85]
J1 = ["3V3", "3V3", "RST", "4", "5", "6", "7", "15", "16", "17", "18", "8", "3", "46", "9", "10", "11", "12", "13", "14",
      "5V", "G"]
J3 = ["G", "TX", "RX", "1", "2", "42", "41", "40", "39", "38", "37", "36", "35", "0", "45", "48", "47", "21", "20", "19",
      "G", "G"]
HEADER = {"J1": J1, "J3": J3}
PI = {2: "5V", 4: "5V", 6: "GND", 8: "GPIO14 TXD", 10: "GPIO15 RXD", 14: "GND"}


def load() -> dict:
    return yaml.safe_load(SRC.read_text(encoding="utf-8"))


def hub_label(j: str, n: int) -> str:
    name = HEADER[j][n - 1]
    return f"GPIO{name}" if name.isdigit() else {"G": "GND"}.get(name, name)


def skr_label(port: str, pins: str) -> str:
    labels = SKR.get(port, [])
    if pins in labels:
        return pins
    m = re.fullmatch(r"(\d+)(?:-(\d+))?", pins)
    if not labels or not m:
        return ""
    lo, hi = int(m[1]), int(m[2] or m[1])
    return " ".join(labels[lo - 1:hi]) if 1 <= lo <= hi <= len(labels) else ""


def annotate(end: str, parts: dict) -> str:
    """'HUB:J1-4' -> '**ESP32-S3 hub (CTL-02)** · J1-4 (GPIO4)'; extra references inside the text are annotated too."""
    if end == "-":
        return "—"
    part, _, rest = end.partition(":")
    name = parts.get(part, part)

    def hub(m):
        return f"{m[1]}-{m[2]} ({hub_label(m[1], int(m[2]))})"

    def skr(m):
        lab = skr_label(m[1], m[2])
        pin = f"pins {m[2].replace('-', '–')}" if re.fullmatch(r"\d+-\d+", m[2]) else (f"pin {m[2]}" if m[2].isdigit() else m[2])
        return f"{m[1]} {pin}" + (f" ({lab})" if lab and lab != m[2] else "")

    if part == "PI":
        rest = re.sub(r"\b(\d+)\b", lambda m: f"pin {m[1]} ({PI.get(int(m[1]), '?')})", rest)
    rest = re.sub(r"\bJ([13])-(\d+)\b", lambda m: hub(("", "J" + m[1], m[2])), rest)
    rest = re.sub(SKR_REF, skr, rest) if part in ("SKR", "SPLICE") else rest
    rest = rest.replace("SKR:", "SKR Pico ")
    return f"**{name}** · {rest}" if rest else f"**{name}**"


# ---- README block ---------------------------------------------------------------------------------------------
def pin_usage(w: dict) -> dict[str, list[str]]:
    """Header pin ('J1-4', 'PI-8') -> what uses it (one entry per row)."""
    use: dict[str, list[str]] = {}
    for g in w["groups"]:
        for r in g["rows"]:
            src, dst = r[0], r[1]
            for end, other in ((src, dst), (dst, src)):
                part = end.partition(":")[0]
                other_part = other.partition(":")[0]
                who = w["parts"].get(other_part, other_part).split(" (")[0]
                if part == "HUB":
                    for j, n in re.findall(r"J([13])-(\d+)", end):
                        use.setdefault(f"J{j}-{n}", []).append(who + (" (blocked)" if g.get("blocked") else ""))
                elif part == "PI":
                    for n in re.findall(r"\b(\d+)\b", end.partition(":")[2]):
                        use.setdefault(f"PI-{n}", []).append(who)
    return use


def header_table(w: dict) -> str:
    use = pin_usage(w)
    extra = {**{k: f"*{v}*" for k, v in w.get("hub_pins", {}).get("reserved", {}).items()},
             **{k: f"*{v}*" for k, v in w.get("hub_pins", {}).get("shared", {}).items()},
             **{k: f"avoid: {v}" for k, v in w.get("hub_pins", {}).get("avoid", {}).items()}}
    for k, v in extra.items():
        use.setdefault(k, [v])
    rows = ["| J1 pin | Label | Used by | | J3 pin | Label | Used by |", "|---:|---|---|---|---:|---|---|"]
    for n in range(1, 23):
        a, b = f"J1-{n}", f"J3-{n}"
        ua = " / ".join(dict.fromkeys(use.get(a, []))) or "·"
        ub = " / ".join(dict.fromkeys(use.get(b, []))) or "·"
        rows.append(f"| {n} | {hub_label('J1', n)} | {ua} | | {n} | {hub_label('J3', n)} | {ub} |")
    return "\n".join(rows)


SKR_PORTS = [("X", "motor socket, XH 4-pin"), ("Y", "motor socket, XH 4-pin"), ("Z1", "motor socket, XH 4-pin"),
             ("Z2", "second socket on the Z driver"), ("E", "motor socket, XH 4-pin"), ("X-STOP", "IO4 · GND · 5V"),
             ("Y-STOP", "IO3 · GND · 5V"), ("Z-STOP", "IO25 · GND · 5V"), ("E0-STOP", "IO16 · GND · 5V"),
             ("HE", "MOSFET output: IO23 (switched −) · 12/24V"), ("HB", "MOSFET output: IO21 (switched −) · 12/24V"), ("FAN1", "IO17 (switched −) · 12/24V"),
             ("FAN2", "IO18 · 12/24V"), ("FAN3", "IO20 · 12/24V"), ("RGB", "GND · IO24 · 5V"),
             ("POWER", "screw terminal: GND · 12/24V"), ("USB-C", "data to the laptop")]


def skr_table(w: dict) -> str:
    use: dict[str, list[str]] = {}
    for g in w["groups"]:
        for r in g["rows"]:
            for end, other in ((r[0], r[1]), (r[1], r[0])):
                if end.partition(":")[0] not in ("SKR", "SPLICE"):
                    continue
                who = w["parts"].get(other.partition(":")[0], other).split(" (")[0]
                if end.partition(":")[0] == "SPLICE":
                    who = w["parts"]["M1"].split(" (")[0] + " (spliced)"
                ports = [p for p, _ in re.findall(SKR_REF, end)] or (["USB-C"] if "USB-C" in end else [])
                for p in ports:
                    use.setdefault(p, []).append(who + (" (blocked)" if g.get("blocked") else ""))
    rows = ["| Port | Pins | Used by |", "|---|---|---|"]
    rows += [f"| {p} | {pins} | {' / '.join(dict.fromkeys(use.get(p, []))) or '·'} |" for p, pins in SKR_PORTS]
    return "\n".join(rows)


def readme_block(w: dict) -> str:
    out = ['<img src="docs/assets/wiring.svg" width="100%" alt="Wiring overview">', "",
           "Every connection, pin by pin. No solder, no crimps: screw terminals, lever connectors (WAGO 221), "
           "plug-in leads and jumper wires. Source: [`docs/wiring.yaml`](docs/wiring.yaml) "
           "(`make build` writes this section; `make check` compares it with the firmware). "
           "**Press the e-stop and unplug the wall adapter before touching any terminal.** "
           "Step by step with pictures: [wiring guide](docs/wiring.html); the first wires drawn as the parts sit on the bench: "
           "[power wiring walkthrough](docs/power.html), then the [controller walkthrough](docs/controller.html), "
           "then the [machine walkthrough](docs/machine.html) and the [hub add-ons](docs/addons.html).", ""]
    toc = " · ".join(f"[{g['title'].split(' · ', 1)[1]}](#{anchor(g['title'])})" for g in w["groups"])
    out += [f"**Jump to:** {toc} · [SKR Pico port map](#skr-pico-port-map) · [ESP32-S3 header map](#esp32-s3-header-map)", ""]
    for g in w["groups"]:
        out.append(f"### {g['title']}")
        out.append("")
        out.append(f"*Stage {g['stage']}.* " + " ".join(g.get("intro", "").split()))
        out.append("")
        n = w["groups"].index(g) + 1
        out.append(f'<img src="docs/assets/wiring/{group_file(n).name}" width="100%" alt="{g["title"]}: pin-by-pin diagram">')
        out.append("")
        out.append("| # | From | To | Wire | Notes |")
        out.append("|---:|---|---|---|---|")
        for i, r in enumerate(g["rows"], 1):
            frm, to, wire, note = (r + ["", ""])[:4]
            out.append(f"| {i} | {annotate(frm, w['parts'])} | {annotate(to, w['parts'])} | {wire} | {note} |")
        out.append("")
        if g.get("checks"):
            out.append("**Check:** " + " · ".join(g["checks"]))
            out.append("")
    out += ["### SKR Pico port map", "",
            "Ports as named on the board; pins in the maker pin diagram's order [C12]. `·` = free.", "", skr_table(w), ""]
    out += ["### ESP32-S3 header map", "",
            "Pin numbers as in Espressif's user guide (J1 on one long edge, J3 on the other). `·` = free; *italic* = kept "
            "free for an optional part the firmware already supports; *avoid* = strapping, console, USB or memory pins.", "",
            header_table(w), ""]
    return "\n".join(out)


def anchor(title: str) -> str:
    """GitHub heading anchor: lower case, drop everything but letters, digits, '_', '-' and spaces, spaces -> '-'."""
    return re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")


def write_readme(block: str) -> None:
    t = README.read_text(encoding="utf-8")
    if START not in t:
        raise SystemExit(f"README.md has no {START} marker")
    head, rest = t.split(START, 1)
    README.write_text(f"{head}{START}\n{block}\n{END}{rest.split(END, 1)[1]}", encoding="utf-8")


# ---- diagram --------------------------------------------------------------------------------------------------
BG, PANEL, LINE, TXT, MUTED = "#0d1117", "#161b22", "#30363d", "#f0f6fc", "#8b949e"
ORANGE, BLUE, GREEN, PURPLE, YELLOW, RED = "#f0883e", "#58a6ff", "#3fb950", "#bc8cff", "#e3b341", "#f85149"
FONT = "Segoe UI,Helvetica,Arial,sans-serif"


def _box(x, y, w, h, title, lines=(), col=BLUE):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{PANEL}" stroke="{col}" stroke-width="2"/>'
    s += f'<text x="{x + 12}" y="{y + 22}" fill="{TXT}" font-size="14" font-weight="600">{title}</text>'
    for i, ln in enumerate(lines):
        s += f'<text x="{x + 12}" y="{y + 42 + 16 * i}" fill="{MUTED}" font-size="11.5">{ln}</text>'
    return s


def _wire(pts, col, label="", lx=None, ly=None, dash=""):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    s = (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.4" stroke-dasharray="8 5">'
         f'<animate attributeName="stroke-dashoffset" from="26" to="0" dur="1.2s" repeatCount="indefinite"/></path>')
    if label:
        x, y = (lx, ly) if lx is not None else pts[len(pts) // 2]
        s += f'<text x="{x}" y="{y}" fill="{col}" font-size="11" text-anchor="middle">{label}</text>'
    return s


def svg() -> str:
    b = f'<text x="24" y="34" fill="{TXT}" font-size="18" font-weight="600">Wiring overview</text>'
    b += (f'<text x="24" y="54" fill="{MUTED}" font-size="12">Red: 18–24 V motor power · grey: ground · blue: motor '
          f'cables · green: home switches · purple: 3.3 V logic · yellow: USB. Pin-by-pin tables below.</text>')
    # power chain (left)
    b += _box(24, 84, 230, 76, "Power (01)", ["24 V 3 A wall adapter", "screw-terminal jack on the power plate"], GREEN)
    b += _box(24, 186, 230, 48, "E-stop box (NC contact)", [], ORANGE)
    b += _box(24, 260, 230, 48, "Limit switch (over-travel)", [], ORANGE)
    b += _wire([(139, 160), (139, 186)], RED)
    b += _wire([(139, 234), (139, 260)], RED)
    # motors (top) + SKR Pico (centre)
    for i, m in enumerate(("M4 arm", "M3 table", "M2 tilt", "M1 spin*")):
        x = 300 + i * 81
        b += _box(x, 84, 76, 44, m, [], BLUE)
        b += _wire([(x + 38, 128), (x + 38, 170)], BLUE)
    b += f'<text x="300" y="78" fill="{MUTED}" font-size="11">* bare leads spliced to a spare 5-pack cable</text>'
    b += _box(300, 170, 320, 214, "SKR Pico V1.0 (grblHAL)", [
        "X · Y · Z1 · E   motor sockets (XH 4-pin)", "X/Y/Z/E0-STOP  home switches (XH 3-pin)",
        "HE (IO23)  lamp driver −Vin · M62 P4", "HB (IO21)  reserved: colour bank BLOCKED",
        "FAN1 (IO17)  optional fan", "POWER  12/24 V screw terminal", "USB-C  → laptop"], PURPLE)
    b += _wire([(139, 308), (139, 340), (300, 340)], RED, "motor power +", 222, 332)
    b += _wire([(254, 122), (276, 122), (276, 356), (300, 356)], MUTED)
    b += _box(644, 84, 200, 60, "4 optical endstops", ["S · G · V → *-STOP pins 1 · 2 · 3"], GREEN)
    b += _wire([(744, 144), (744, 158), (606, 158), (606, 170)], GREEN)
    # lamp
    b += _box(660, 190, 212, 60, "Lamp driver NLDD-350HW", ["+Vin ← HE+ · −Vin → HE−"], YELLOW)
    b += _wire([(620, 220), (660, 220)], RED)
    b += _box(660, 276, 212, 44, "COB lamp (06)", [], YELLOW)
    b += _wire([(766, 250), (766, 276)], RED)
    # hub
    b += _box(900, 84, 280, 60, "Opto module PC817", ["24 V in → motor-power sense out"], GREEN)
    b += _wire([(620, 368), (886, 368), (886, 114), (900, 114)], RED, "MOT+ / MOT−", 760, 362)
    b += _box(900, 190, 280, 194, "ESP32-S3 hub (MicroPython)", [
        "J1-4…7  keypad A: HOME START STOP LIGHT", "J1-8, 9  keypad B: NEXT, PAUSE",
        "J1-10  opto OUT (motor-power sense)", "J3-4, 5  I2C SDA, SCL (optional)",
        "J3-16, 17  UART to the Pi (optional)", "USB  → laptop"], PURPLE)
    b += _wire([(1040, 144), (1040, 190)], PURPLE)
    b += _box(1200, 190, 92, 60, "Keypads", ["2 × 1×4"], BLUE)
    b += _wire([(1180, 220), (1200, 220)], PURPLE)
    # laptop + USB (bottom)
    b += _box(300, 430, 880, 46, "Laptop (Ubuntu / WSL): 3 USB ports", [], YELLOW)
    b += _wire([(460, 384), (460, 430)], YELLOW, "USB-C", 488, 412)
    b += _wire([(1040, 384), (1040, 430)], YELLOW, "USB", 1060, 412)
    b += _box(24, 420, 230, 56, "Camera (06)", ["USB → laptop"], YELLOW)
    b += _wire([(254, 448), (300, 448)], YELLOW)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1316 500" font-family="{FONT}">\n'
            f'<rect width="1316" height="500" rx="14" fill="{BG}"/>\n{b}\n</svg>\n')


# ---- one animated pin-by-pin diagram per group ------------------------------------------------------------------
GROUP_DIR = ROOT / "docs" / "assets" / "wiring"
GUIDE = ROOT / "docs" / "wiring-guide.js"
KIND_KEY = {"18–24 V": "power", "ground / − side": "ground", "limit-switch wire (+24 V line)": "switch", "3.3 / 5 V": "logic",
            "signal": "signal", "motor": "motor", "home switch": "home", "USB": "usb", "reserved": "reserved"}
GREY, ORANGE2, SWITCH = "#8b949e", "#ffa657", "#ff9e9e"


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pin_text(end: str, parts: dict) -> str:
    """Plain pin label for a diagram: the annotated end without the part name or markdown."""
    t = annotate(end, parts)
    t = t.split("** · ", 1)[1] if "** · " in t else ""
    return t.replace("`", "").replace("**", "")


def wire_colour(r: list, blocked: bool, parts: dict | None = None) -> tuple[str, str]:
    """(colour, kind) of one row, from the wire text and the pin names."""
    frm, to, wire = r[0], r[1], r[2].lower()
    pins = " ".join(pin_text(e, parts or {}) if e != "-" else "" for e in (frm, to))
    if blocked:
        return GREY, "reserved"
    if {"OT", "OTA", "OTB"} & {frm.split(":")[0], to.split(":")[0]}:
        return SWITCH, "limit-switch wire (+24 V line)"
    if "usb" in wire or "USB" in pins:
        return YELLOW, "USB"
    if frm.split(":")[0] in ("M1", "M2", "M3", "M4", "SPLICE") or "5-pack" in wire or "same cable" in wire:
        return BLUE, "motor"
    if "ctl-06" in wire:
        return GREEN, "home switch"
    ends = {frm.split(":")[0], to.split(":")[0]}
    if any(k in pins for k in ("GND", "−", "common", "black")) or "black" in wire or ends & {"MOT-", "GND", "HGND"}:
        return GREY, "ground / − side"
    if ends & {"MOT+", "JACK", "ADAPTER"} or any(k in pins for k in (
            "12/24V", "+Vin", "+Vo", "OUT +", "IN +", "IN+", "lead A", "lead B", "NC", "COM")):
        return RED, "18–24 V"
    if any(k in pins for k in ("3V3", "5V", "VCC", "VIN")):
        return ORANGE2, "3.3 / 5 V"
    if "red" in pins.lower() or "red" in wire:
        return RED, "18–24 V"
    return PURPLE, "signal"


def layout(g: dict, parts: dict) -> dict:
    """Boxes, pins and wire paths of one group: shared by the README diagrams and the step-by-step guide page."""
    rows, blocked = g["rows"], bool(g.get("blocked"))
    node = lambda e: e.partition(":")[0]                      # noqa: E731
    order: list[str] = []
    pins: dict[str, list[str]] = {}
    for r in rows:
        for e in r[:2]:
            if e == "-":
                continue
            n, t = node(e), pin_text(e, parts)
            if n not in order:
                order.append(n)
            pins.setdefault(n, [])
            if t not in pins[n]:
                pins[n].append(t)
    col = {n: 0 for n in order}
    for _ in order:                                          # longest-path layering: wires always run left to right
        for r in rows:
            if r[1] != "-":
                col[node(r[1])] = max(col[node(r[1])], col[node(r[0])] + 1)
    ncol = max(col.values()) + 1
    TITLE_W, PIN_W, ROW, HEAD, GAP_X, GAP_Y, TOP, LANE = 7.6, 6.3, 21, 30, 150, 18, 78, 12
    width = {c: 0.0 for c in range(ncol)}
    for n in order:
        name = parts.get(n, n)
        w = max(len(name) * TITLE_W, max([len(p) for p in pins[n]] + [4]) * PIN_W) + 30
        width[col[n]] = max(width[col[n]], w)
    xs, x = {}, 28.0
    for c in range(ncol):
        xs[c] = x
        x += width[c] + GAP_X
    total_w = max(int(x - GAP_X + 28), 1000)
    heights = {n: HEAD + ROW * len(pins[n]) + 8 for n in order}
    col_h = {c: sum(heights[n] + GAP_Y for n in order if col[n] == c) - GAP_Y for c in range(ncol)}
    tallest = max(col_h.values())
    pos, y_at = {}, {c: (tallest - col_h[c]) / 2 for c in range(ncol)}
    for n in order:
        c = col[n]
        pos[n] = [xs[c], y_at[c], width[c], heights[n]]
        y_at[c] += heights[n] + GAP_Y

    def pin_xy(e, side):
        n = node(e)
        x0, y0, w, _ = pos[n]
        i = pins[n].index(pin_text(e, parts))
        return (x0 + (w if side == "out" else 0), y0 + HEAD + ROW * i + ROW / 2 + 2)

    # wires that skip a column run in lanes above or below the boxes, so no wire crosses a box
    skips = {"top": [], "bottom": []}
    for i, r in enumerate(rows, 1):
        if r[1] == "-" or col[node(r[1])] - col[node(r[0])] < 2:
            continue
        mid_cols = range(col[node(r[0])] + 1, col[node(r[1])])
        boxes = [pos[n] for n in order if col[n] in mid_cols]
        centre = (min(b_[1] for b_ in boxes) + max(b_[1] + b_[3] for b_ in boxes)) / 2
        (y1, y2) = (pin_xy(r[0], "out")[1], pin_xy(r[1], "in")[1])
        skips["top" if (y1 + y2) / 2 < centre else "bottom"].append((i, y1))
    shift = TOP + (len(skips["top"]) * LANE + 16 if skips["top"] else 0)
    for n in order:
        pos[n][1] += shift
    bottom = max(p_[1] + p_[3] for p_ in pos.values())
    route: dict[int, tuple] = {}
    for side, items in skips.items():
        items.sort(key=lambda t: t[1], reverse=(side == "bottom"))       # inner lane = pin nearest the lane side
        for j, (i, _) in enumerate(items):
            depth = len(items) - 1 - j
            ly = (shift - 16 - depth * LANE) if side == "top" else (bottom + 16 + depth * LANE)
            route[i] = (j, ly)
    total_h = int(bottom + (len(skips["bottom"]) * LANE + 16 if skips["bottom"] else 0) + 50)
    out_k: dict[int, int] = {}
    in_k: dict[int, int] = {}
    wires = []
    for i, r in enumerate(rows, 1):
        colr, kind = wire_colour(r, blocked, parts)
        x1, y1 = pin_xy(r[0], "out")
        w = {"n": i, "row": r, "colour": colr, "kind": kind, "a": (x1, y1), "pin_a": (node(r[0]), pin_text(r[0], parts))}
        if r[1] == "-":
            wires.append(w)
            continue
        x2, y2 = pin_xy(r[1], "in")
        if i in route:
            j, ly = route[i]
            cf, ct = col[node(r[0])], col[node(r[1])]
            ka, kb = out_k.get(cf, 0), in_k.get(ct, 0)
            out_k[cf], in_k[ct] = ka + 1, kb + 1
            xa, xb = x1 + 18 + ka * 9, x2 - 18 - kb * 9
            d = f"M{x1:.0f},{y1:.0f} H{xa:.0f} V{ly:.0f} H{xb:.0f} V{y2:.0f} H{x2:.0f}"
            mx, my = (xa + xb) / 2 + ((j % 3) - 1) * 30, ly
        else:
            dx = (x2 - x1) / 2
            d = f"M{x1:.0f},{y1:.0f} C{x1 + dx:.0f},{y1:.0f} {x2 - dx:.0f},{y2:.0f} {x2:.0f},{y2:.0f}"
            t = (0.5, 0.32, 0.68)[i % 3]                      # stagger the row badges so neighbours don't overlap
            mx = (1 - t) ** 3 * x1 + 3 * (1 - t) ** 2 * t * (x1 + dx) + 3 * (1 - t) * t ** 2 * (x2 - dx) + t ** 3 * x2
            my = (1 - t) ** 3 * y1 + 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t ** 2 * y2 + t ** 3 * y2
        w.update(d=d, b=(x2, y2), badge=(mx, my), pin_b=(node(r[1]), pin_text(r[1], parts)))
        wires.append(w)
    return {"order": order, "pos": pos, "pins": pins, "wires": wires, "w": total_w, "h": total_h,
            "blocked": blocked, "ROW": ROW, "HEAD": HEAD}


def group_svg(g: dict, parts: dict) -> tuple[str, int]:
    L = layout(g, parts)
    blocked, total_w, total_h = L["blocked"], L["w"], L["h"]
    b = [f'<text x="28" y="34" fill="{TXT}" font-size="18" font-weight="600">{esc(g["title"])}</text>',
         f'<text x="28" y="56" fill="{MUTED}" font-size="12">Stage {esc(g["stage"])} · each line is one wire, from the '
         f'left pin to the right pin; the number matches the table row below.</text>']
    if blocked:
        b.append(f'<text x="{total_w - 28}" y="34" fill="{RED}" font-size="15" font-weight="700" text-anchor="end">'
                 f'BLOCKED: do not wire or power</text>')
    # boxes and pins
    for n in L["order"]:
        x0, y0, w, h = L["pos"][n]
        b.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}" rx="9" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>')
        b.append(f'<text x="{x0 + 12:.0f}" y="{y0 + 20:.0f}" fill="{TXT}" font-size="13" font-weight="600">{esc(parts.get(n, n))}</text>')
        for i, p in enumerate(L["pins"][n]):
            py = y0 + L["HEAD"] + L["ROW"] * i + L["ROW"] / 2 + 2
            b.append(f'<rect x="{x0 + 6:.0f}" y="{py - 9:.0f}" width="{w - 12:.0f}" height="18" rx="4" fill="{BG}"/>')
            b.append(f'<text x="{x0 + 14:.0f}" y="{py + 4:.0f}" fill="{TXT}" font-size="11.5">{esc(p)}</text>')
    # wires
    kinds = {}
    for wr in L["wires"]:
        i, colr, kind = wr["n"], wr["colour"], wr["kind"]
        kinds[kind] = colr
        x1, y1 = wr["a"]
        if "d" not in wr:
            b.append(f'<text x="{x1 - 12:.0f}" y="{y1 + 4:.0f}" fill="{MUTED}" font-size="11" text-anchor="end">'
                     f'not connected ({i})</text>')
            b.append(f'<circle cx="{x1:.0f}" cy="{y1:.0f}" r="4" fill="{BG}" stroke="{GREY}" stroke-width="1.5"/>')
            continue
        d, (x2, y2), (mx, my) = wr["d"], wr["b"], wr["badge"]
        if blocked:
            b.append(f'<path d="{d}" fill="none" stroke="{colr}" stroke-width="2" stroke-dasharray="4 6" opacity="0.7"/>')
        else:
            b.append(f'<path d="{d}" fill="none" stroke="{colr}" stroke-width="2.4" stroke-linejoin="round" stroke-dasharray="9 5" opacity="0.95">'
                     f'<animate attributeName="stroke-dashoffset" from="28" to="0" dur="1.3s" repeatCount="indefinite"/></path>')
            b.append(f'<circle r="3.6" fill="{TXT}"><animateMotion dur="2.6s" begin="{(i % 9) * 0.29:.2f}s" '
                     f'repeatCount="indefinite" path="{d}"/></circle>')
        for (px, py) in ((x1, y1), (x2, y2)):
            b.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="4.5" fill="{colr}" stroke="{BG}" stroke-width="1.5"/>')
        b.append(f'<circle cx="{mx:.0f}" cy="{my:.0f}" r="9" fill="{BG}" stroke="{colr}" stroke-width="1.5"/>'
                 f'<text x="{mx:.0f}" y="{my + 4:.0f}" fill="{TXT}" font-size="10" text-anchor="middle">{i}</text>')
    # legend
    lx = 28
    for kind, colr in kinds.items():
        b.append(f'<line x1="{lx}" y1="{total_h - 18}" x2="{lx + 22}" y2="{total_h - 18}" stroke="{colr}" stroke-width="3"/>'
                 f'<text x="{lx + 28}" y="{total_h - 14}" fill="{MUTED}" font-size="11.5">{kind}</text>')
        lx += 40 + len(kind) * 7
    svg_txt = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" font-family="{FONT}">\n'
               f'<rect width="{total_w}" height="{total_h}" rx="14" fill="{BG}"/>\n' + "\n".join(b) + "\n</svg>\n")
    return svg_txt, total_w


def group_file(i: int) -> Path:
    return GROUP_DIR / f"wiring-{i:02d}.svg"


def write_group_svgs(w: dict) -> dict[int, int]:
    GROUP_DIR.mkdir(parents=True, exist_ok=True)
    widths = {}
    for i, g in enumerate(w["groups"], 1):
        txt, widths[i] = group_svg(g, w["parts"])
        group_file(i).write_text(txt, encoding="utf-8")
    for f in GROUP_DIR.glob("wiring-*.svg"):                  # drop diagrams of removed groups
        if int(f.stem.split("-")[1]) > len(w["groups"]):
            f.unlink()
    return widths


# ---- step-by-step guide data (docs/wiring.html reads it) ---------------------------------------------------------
BOM_ID = re.compile(r"\b[A-Z]{3}-\d{2}\b")
BOM_WORDS = [(re.compile(r"WAGO|lever connector", re.I), "PWR-20"), (re.compile(r"\bM-F\b|male.female", re.I), "CTL-07"),
             (re.compile(r"18 AWG"), "PWR-15"), (re.compile(r"CTL-06 lead|JST-XH", re.I), "CTL-06")]


def bom_rows() -> dict:
    """Every bom.csv row by ID (part name, link, supplier, unit price, status) for the walkthrough buy lists."""
    import csv
    out = {}
    for f in sorted((ROOT / "phases").glob("*/bom.csv")):
        for r in csv.DictReader(f.open(encoding="utf-8")):
            out[r["ID"]] = {"part": r["Part"], "link": r["Link"] if r["Link"].startswith("http") else "", "supplier": r["Supplier"],
                            "unit": r["Unit USD"], "type": r["Type"], "status": r["Status"],
                            "tbd": "[TBD]" in r["Price"] + r["Part number"] + r["Notes"]}
    return out


def bom_ids(text: str, known: dict) -> list[str]:
    ids = [i for i in BOM_ID.findall(text) if i in known]
    ids += [i for rx, i in BOM_WORDS if rx.search(text) and i in known]
    return list(dict.fromkeys(ids))


def md_html(s: str) -> str:
    """The little markdown wiring.yaml uses (**bold**, `code`) -> HTML, escaped."""
    s = esc(" ".join(str(s).split()))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def guide_data(w: dict) -> dict:
    groups, known = [], bom_rows()
    used: set[str] = set()
    for g in w["groups"]:
        L = layout(g, w["parts"])
        boxes = [{"id": n, "name": w["parts"].get(n, n), "x": round(L["pos"][n][0]), "y": round(L["pos"][n][1]),
                  "w": round(L["pos"][n][2]), "h": round(L["pos"][n][3]), "pins": L["pins"][n]} for n in L["order"]]
        wires = []
        for wr in L["wires"]:
            frm, to, wire, note = (wr["row"] + ["", ""])[:4]
            item = {"n": wr["n"], "kind": KIND_KEY.get(wr["kind"], "signal"), "label": wr["kind"],
                    "from": {"part": w["parts"].get(wr["pin_a"][0], wr["pin_a"][0]), "pin": wr["pin_a"][1]},
                    "wire": md_html(wire), "note": md_html(note), "a": [round(v) for v in wr["a"]]}
            item["ids"] = bom_ids(" ".join([w["parts"].get(wr["pin_a"][0], ""), w["parts"].get(wr["pin_b"][0], "") if wr.get("pin_b") else "", wire]), known)
            used.update(item["ids"])
            if "d" in wr:
                item.update(to={"part": w["parts"].get(wr["pin_b"][0], wr["pin_b"][0]), "pin": wr["pin_b"][1]},
                            d=wr["d"], b=[round(v) for v in wr["b"]], badge=[round(v) for v in wr["badge"]])
            wires.append(item)
        xs = [b["x"] for b in boxes] + [b["x"] + b["w"] for b in boxes]
        ys = [b["y"] for b in boxes] + [b["y"] + b["h"] for b in boxes]
        for wr in L["wires"]:
            xs.append(wr["a"][0]); ys.append(wr["a"][1])
            for cmd, args in re.findall(r"([MHVC])([^MHVC]*)", wr.get("d", "")):
                nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", args)]
                (xs if cmd == "H" else ys if cmd == "V" else xs).extend(nums if cmd in "HV" else nums[0::2])
                if cmd in "MC":
                    ys.extend(nums[1::2])
        pad = 24
        view = [round(min(xs) - pad - 70), round(min(ys) - pad), round(max(xs) - min(xs) + 2 * pad + 70), round(max(ys) - min(ys) + 2 * pad)]
        groups.append({"title": g["title"], "stage": str(g["stage"]), "intro": md_html(g.get("intro", "")),
                       "checks": [md_html(c) for c in g.get("checks", [])], "blocked": L["blocked"], "view": view,
                       "w": L["w"], "h": L["h"], "head": L["HEAD"], "row": L["ROW"], "boxes": boxes, "wires": wires})
    used.update(bom_ids(" ".join(w["parts"].values()), known))
    for f in sorted((ROOT / "docs" / "og").glob("walk-*.js")):                 # parts named in the walkthrough steps
        used.update(i for i in BOM_ID.findall(f.read_text(encoding="utf-8")) if i in known)
    return {"note": "Generated by tools/wiring.py from docs/wiring.yaml (`make build`): do not edit by hand.", "groups": groups,
            "buy": {i: known[i] for i in sorted(used)}}


def write_guide(w: dict) -> None:
    import json
    GUIDE.write_text("// Written by tools/wiring.py from docs/wiring.yaml (`make build`): do not edit by hand.\nwindow.WIRING = "
                     + json.dumps(guide_data(w), ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


# ---- checks ---------------------------------------------------------------------------------------------------
def firmware_pins() -> dict:
    tree = ast.parse(HUB_FW.read_text(encoding="utf-8"))
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in ("BUTTONS", "SENSE_PIN", "BAND_PINS", "I2C_PAIRS", "SCREEN_PINS"):
                    out[t.id] = ast.literal_eval(node.value)
                elif isinstance(t, ast.Tuple) and [e.id for e in t.elts] == ["UART_TX", "UART_RX"]:
                    out["UART_TX"], out["UART_RX"] = ast.literal_eval(node.value)
    return out


def hub_gpios(end: str) -> list[int]:
    return [int(hub_label("J" + j, int(n))[4:]) for j, n in re.findall(r"J([13])-(\d+)", end)
            if hub_label("J" + j, int(n)).startswith("GPIO")]


def check(w: dict | None = None) -> list[str]:
    w = w or load()
    errs: list[str] = []
    rows = [(g, r) for g in w["groups"] for r in g["rows"]]
    for g, r in rows:
        if len(r) != 4:
            errs.append(f"wiring.yaml: row {r} needs [from, to, wire, note]")
            continue
        for end in r[:2]:
            part = end.partition(":")[0]
            if end != "-" and part not in w["parts"]:
                errs.append(f"wiring.yaml: unknown part '{part}' in {end}")
            for j, n in re.findall(r"J([13])-(\d+)", end):
                if not 1 <= int(n) <= 22:
                    errs.append(f"wiring.yaml: no header pin J{j}-{n}")
            for port, pins in re.findall(SKR_REF, end):
                if part in ("SKR", "SPLICE") and not skr_label(port, pins):
                    errs.append(f"wiring.yaml: SKR Pico {port} has no pin '{pins}'")
            if part == "PI":
                for n in re.findall(r"\b(\d+)\b", end.partition(":")[2]):
                    if int(n) not in PI:
                        errs.append(f"wiring.yaml: Pi pin {n} not in the pin map")
    # one jumper per header pin (alternatives may share their partner's pins)
    alt = w.get("alternatives", {})
    seen: dict[str, str] = {}
    for g, r in rows:
        ends = [e for e in r[:2] if e != "-"]
        others = [e.partition(":")[0] for e in ends if not e.startswith(("HUB:", "PI:"))]
        grp = alt.get(others[0], others[0]) if others else ""
        owner = grp if grp in alt.values() else f"{r[0]} → {r[1]}"      # alternatives share pins; any other row owns its pins
        for e in ends:
            pins = [f"J{j}-{n}" for j, n in re.findall(r"J([13])-(\d+)", e)] if e.startswith("HUB:") else \
                [f"PI-{n}" for n in re.findall(r"\b(\d+)\b", e.partition(":")[2])] if e.startswith("PI:") else []
            for p in pins:
                if seen.get(p, owner) != owner:
                    errs.append(f"wiring.yaml: header pin {p} used twice ({seen[p]} and {owner})")
                seen.setdefault(p, owner)
    for p, why in w.get("hub_pins", {}).get("avoid", {}).items():
        if p in seen:
            errs.append(f"wiring.yaml: header pin {p} is wired but should be avoided ({why})")
    for p, why in w.get("hub_pins", {}).get("reserved", {}).items():
        if p in seen:
            errs.append(f"wiring.yaml: header pin {p} is reserved for {why}")
    # firmware pins
    fw = firmware_pins()
    notes = {r[3].split(" ")[0]: r for _, r in rows if r[1].startswith("HUB:")}
    for name, gpio in fw.get("BUTTONS", {}).items():
        r = notes.get(name)
        if not r:
            errs.append(f"wiring.yaml: no keypad row for button {name}")
        elif hub_gpios(r[1]) != [gpio]:
            errs.append(f"wiring.yaml: {name} on GPIO {hub_gpios(r[1])}, firmware says {gpio}")
    by_from = {r[0]: r for _, r in rows}
    if "OPTO:OUT" in by_from and hub_gpios(by_from["OPTO:OUT"][1]) != [fw.get("SENSE_PIN")]:
        errs.append(f"wiring.yaml: opto OUT not on firmware SENSE_PIN {fw.get('SENSE_PIN')}")
    scl, sda = fw.get("I2C_PAIRS", [(None, None)])[0]
    for key, want in (("SPEC:SCL (yellow)", scl), ("SPEC:SDA (blue)", sda)):
        if key in by_from and hub_gpios(by_from[key][1]) != [want]:
            errs.append(f"wiring.yaml: {key} not on firmware GPIO {want}")
    uart = {"PI:8": fw.get("UART_RX"), "PI:10": fw.get("UART_TX")}
    for key, want in uart.items():
        if key in by_from and hub_gpios(by_from[key][1]) != [want]:
            errs.append(f"wiring.yaml: {key} not on hub GPIO {want} (firmware UART)")
    hp = w.get("hub_pins", {})
    enc = sorted(int(hub_label(p[:2], int(p[3:]))[4:]) for p in {**hp.get("reserved", {}), **hp.get("shared", {})})
    if enc != sorted(g for pair in fw.get("I2C_PAIRS", [])[1:] for g in pair):
        errs.append(f"wiring.yaml: reserved + shared encoder pins {enc} != firmware I2C_PAIRS[1:]")
    screen = {"TFT:CLK": "SCK", "TFT:DIN": "MOSI", "TFT:DC": "DC", "TFT:CS": "CS"}     # status screen vs firmware SCREEN_PINS
    for key, name in screen.items():
        want = fw.get("SCREEN_PINS", {}).get(name)
        if key in by_from and hub_gpios(by_from[key][1]) != [want]:
            errs.append(f"wiring.yaml: {key} not on firmware SCREEN_PINS {name} = GPIO {want}")
    shared = sorted(int(hub_label(p[:2], int(p[3:]))[4:]) for p in hp.get("shared", {}))
    if shared and shared != sorted(fw.get("SCREEN_PINS", {}).values()):
        errs.append(f"wiring.yaml: shared pins {shared} != firmware SCREEN_PINS")
    bank = [g_ for _, r in rows if r[0].startswith("BANK:band") for g_ in hub_gpios(r[1])]
    if bank and bank != fw.get("BAND_PINS"):
        errs.append(f"wiring.yaml: reserved LED-bank pins {bank} != firmware {fw.get('BAND_PINS')}")
    # SKR Pico home inputs and light outputs
    stops = {r[1].split(":")[1].split(".")[0]: r for _, r in rows if "-STOP" in r[1]}
    for port, axis in STOP_AXIS.items():
        if port in stops and f"Pn:{axis}" not in stops[port][3]:
            errs.append(f"wiring.yaml: {port} note should name its grblHAL limit `Pn:{axis}`")
    lights = yaml.safe_load(MACHINE.read_text(encoding="utf-8"))["lights"]
    lamp = [r for _, r in rows if r[0] == "LAMPDRV:−Vin"]
    if lamp and f"P{lights['white']['output']}" not in lamp[0][3]:
        errs.append(f"wiring.yaml: lamp row should name output P{lights['white']['output']} (machine.yaml lights.white)")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    w = load()
    errs = check(w)
    if a.check:
        for e in errs:
            print(e)
        print("wiring: OK" if not errs else f"wiring: {len(errs)} problem(s)")
        return 1 if errs else 0
    if errs:
        print("\n".join(errs))
        return 1
    write_readme(readme_block(w))
    SVG.write_text(svg(), encoding="utf-8")
    write_group_svgs(w)
    write_guide(w)
    n = sum(len(g["rows"]) for g in w["groups"])
    print(f"README.md wiring: {n} connections in {len(w['groups'])} groups; docs/assets/wiring.svg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
