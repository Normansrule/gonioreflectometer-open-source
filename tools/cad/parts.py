#!/usr/bin/env python3
"""Starter geometry for every printed part (CadQuery). Writes STEP (edit in Onshape) + STL (slice) into phases/NN/3d/.

    pip install cadquery          # once
    python tools/cad/parts.py     # all parts;  --only CAL-06a  for one

These are v0 starting points: dimensions come from the docs and datasheets, not from your measured parts.
Measure, edit the PARAMETERS below (or import the STEP into Onshape), print one, check, then commit.
SPDX-License-Identifier: CERN-OHL-S-2.0
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stepio  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

# ---------------- PARAMETERS (mm) ----------------
CLEAR = 0.2                       # print clearance; set from the tolerance coupon (M03)
# One screw size everywhere: M2 socket head (FRM-06). Only the NEMA 17 motor faces keep M3 (the motors' own thread)
# and the axles keep M8 bolts. No wood, no extrusion, no T-nuts: every join is printed part + M2 screw.
M2 = 2.4                          # M2 clearance hole
M2_TAP = 1.7                      # M2 screw self-taps into ABS (no heat-set inserts, no soldering iron); set from the coupon (M03)
M2_HEAD, M2_NUT = 4.4, 4.4        # socket-head counterbore; nut across flats + clearance (1.6 mm thick nut, 1.8 mm trap)
M3, M8 = 3.4, 8.5                 # M3: NEMA 17 faces only; M8: axle bolts
OG40 = 40.0                       # interface: 4 x M2 on a 40 mm square + 6.2 mm locator
BEARING_608 = (22.0 + CLEAR, 7.0)  # OD, width
NEMA17_HOLES, NEMA17_BOSS = 31.0, 22.5
GT2_PITCH = 2.0


def og40_holes(wp: cq.Workplane) -> cq.Workplane:
    h = OG40 / 2
    return wp.pushPoints([(h, h), (-h, h), (h, -h), (-h, -h)]).hole(M2).faces(">Z").workplane().hole(6.2)


# ---------------- 00 plan ----------------
def tolerance_coupon():
    """M2 self-tap holes 1.5-1.9 and 608 pockets 22.0-22.4: pick what fits, set CLEAR / M2_TAP."""
    p = cq.Workplane("XY").box(100, 60, 8, centered=(False, False, False))
    for i, d in enumerate((1.5, 1.6, 1.7, 1.8, 1.9)):
        p = p.cut(cq.Workplane("XY").circle(d / 2).extrude(8).translate((12 + 19 * i, 10, 0)))
        p = p.cut(cq.Workplane("XY").box(1, 2 + i, 1, centered=(True, False, False)).translate((12 + 19 * i, 15, 7)))
    for i, d in enumerate((22.0, 22.2, 22.4)):
        p = p.cut(cq.Workplane("XY").circle(d / 2).extrude(7.1).translate((18 + 32 * i, 40, 0.9)))
    return p


# ---------------- 01 power ----------------
PLATE = (130.0, 110.0, 4.0)        # power plate L x W x thickness, on the SE deck tile (POWER_XY)
JACK = (32.0, 14.0, 13.0)          # PWR-30 screw-terminal DC jack (ESTIMATE: measure on arrival, change here)
JACK_AT = (40.0, 15.0)             # jack centre: round plug in from +X (the deck edge), screw terminals toward -X
ESTOP_BOX = (71.0, 71.0)           # PWR-28 e-stop station: 2.8 x 2.8 x 3.4 in overall (listing copy [P64]); measure, change here
ESTOP_BOX_AT = (-25.0, 0.0)        # station centre; sits in a 2 mm rim on double-sided tape
DIN_W = 6.2                        # Phoenix UT / PLC module width on a rail (kept for later add-ons)


def din_stub(n: int = 1, wall_h: float = 14.0) -> cq.Workplane:
    """Printed 35 x 7.5 mm top-hat rail stub for n 6.2 mm modules (rail along X), with end walls that hold them.
    Replaces a metal DIN rail: nothing to cut. Base on z = 0."""
    L = n * DIN_W + 2 * CLEAR
    hat = cq.Workplane("XY").box(L, 27.0, 6.5, centered=(True, True, False))
    hat = hat.union(cq.Workplane("XY").box(L, 35.0, 1.0, centered=(True, True, False)).translate((0, 0, 6.5)))
    for sx in (-1, 1):
        hat = hat.union(cq.Workplane("XY").box(3.0, 35.0, wall_h, centered=(True, True, False)).translate((sx * (L / 2 + 1.5), 0, 0)))
    return hat


def power_plate():
    """Holds the screw-terminal jack (PWR-30) in a frame and the e-stop box (PWR-28) in a low rim; the wall adapter stays
    outside the machine. Four M2 x 12 through counterbored holes into the SE tile's pilots (same pattern as before)."""
    L, W, t = PLATE
    h = OG40 / 2
    p = (cq.Workplane("XY").box(L, W, t, centered=(True, True, False)).faces(">Z").workplane()
         .pushPoints([(h, h), (-h, h), (h, -h), (-h, -h)]).cboreHole(M2, M2_HEAD, 1.8))
    ex, ey = ESTOP_BOX[0] + 2 * CLEAR + 1.0, ESTOP_BOX[1] + 2 * CLEAR + 1.0
    rim = cq.Workplane("XY").rect(ex + 4, ey + 4).extrude(2.0).cut(cq.Workplane("XY").rect(ex, ey).extrude(2.0))
    p = p.union(rim.translate((ESTOP_BOX_AT[0], ESTOP_BOX_AT[1], t)))
    jx, jy = JACK[0] + 2 * CLEAR, JACK[1] + 2 * CLEAR + 0.6
    for sy in (-1, 1):                                                                                   # jack frame: two side walls,
        p = p.union(cq.Workplane("XY").box(jx - 6, 3.0, 8.0, centered=(True, True, False))                 # ends open for the plug and
                    .translate((JACK_AT[0], JACK_AT[1] + sy * (jy / 2 + 1.5), t)))                         # the screw terminals
    return p


# ---------------- 02 controller ----------------
def button_panel():
    """Two 1x4 membrane keypads [C9] in 0.6 mm locating recesses (adhesive back) + tail slots + OLED window."""
    p = cq.Workplane("XY").box(160, 60, 3, centered=(True, True, False))
    for x in (-38, 38):                                                                                  # 70 x 20 keypads (CTL-05)
        p = p.cut(cq.Workplane("XY").rect(70 + CLEAR, 20 + CLEAR).extrude(0.6).translate((x - 8, -10, 2.4)))
        p = p.cut(cq.Workplane("XY").rect(12, 2.5).extrude(3).translate((x - 8, -21.5, 0)))             # tail through
    p = p.cut(cq.Workplane("XY").rect(26, 15).extrude(3).translate((55, 12, 0)))                       # OLED [H52]
    p = p.faces(">Z").workplane().pushPoints([(75, -25), (-75, -25), (75, 25), (-75, 25)]).hole(M2)
    return p


SKR_AT = (-50.0, 0.0)             # CTL-01 BTT SKR Pico centre, turned 180 deg so its USB-C faces the -X tray edge
SKR_HOLES = [(-19.0, sy * 24.5) for sy in (-1, 1)] + [(39.0, sy * 24.5) for sy in (-1, 1)]   # 58 x 49 (maker STEP, turned)
SKR_STANDOFF = 6.0                # board 6 mm above the tray floor: clear of its underside parts
ESP = (62.74, 25.4)               # CTL-02 ESP32-S3-DevKitC-1, Espressif board [P65]; clones run to ~69 x 26: measure, change here
ESP_AT = (55.0, -40.0)            # USB end toward +X (tray edge); module end toward -X
ESP_PED = 6.0                     # pedestal under the module can: board upside down, header pins UP for the jumpers
OPTO_MOD = (66.0, 16.5)           # PWR-10 PC817 24 V module, 66 x 16.5 x 12 mm (listing); screw terminals both ends
LED_DRV = (32.1, 20.5)            # LSR-02 MEAN WELL NLDD-350HW, 32.1 x 20.5 x 12.5 mm [L27]; five 100 mm wire leads, taped in


def _pocket(w: float, h: float, wall: float, height: float, at: tuple[float, float]) -> cq.Workplane:
    """Locating frame for a module held by double-sided tape (TLS-09): no holes needed in the module."""
    o = cq.Workplane("XY").rect(w + CLEAR + 2 * wall, h + CLEAR + 2 * wall).extrude(height)
    return o.cut(cq.Workplane("XY").rect(w + CLEAR, h + CLEAR).extrude(height)).translate((at[0], at[1], 3))


def controller_tray():
    """Base for the SKR Pico, the ESP32-S3 hub and two modules: the PC817 opto module (motion-power sense, screw
    terminals) and the LED driver (wire leads, double-sided tape). No breadboard. SKR Pico holes from the maker STEP [C12]:
    4 x 2.7 mm on 58 x 49 mm, M2 x 8 + washer into 1.7 mm pilots on 6 mm standoffs. The ESP32-S3 board lies upside down
    in a locating frame on a pedestal under its module can (double-sided foam tape), so its header pins point up and the
    female jumpers plug in from above; the USB end faces an opening at +X. Corners: M2 x 12 into the deck pilots."""
    t = cq.Workplane("XY").box(200, 130, 3, centered=(True, True, False))
    t = t.union(_pocket(*OPTO_MOD, 1.6, 3, (47, 40))).union(_pocket(*LED_DRV, 1.6, 4, (40, 5)))
    t = t.cut(cq.Workplane("XY").rect(40, 36).extrude(3).translate((SKR_AT[0] + 10, SKR_AT[1], 0)))  # window under the SKR Pico
    for x, y in SKR_HOLES:
        x, y = SKR_AT[0] + x, SKR_AT[1] + y
        t = t.union(cq.Workplane("XY").circle(3.5).extrude(3 + SKR_STANDOFF).translate((x, y, 0)))
        t = t.cut(cq.Workplane("XY").circle(M2_TAP / 2).extrude(3 + SKR_STANDOFF).translate((x, y, 3)))
    ex, ey = ESP_AT
    t = t.union(_pocket(*ESP, 1.6, 12, ESP_AT))                                                       # locating frame
    t = t.union(cq.Workplane("XY").rect(22, ESP[1] - 6).extrude(ESP_PED).translate((ex - ESP[0] / 2 + 13, ey, 3)))   # pedestal
    t = t.cut(cq.Workplane("XY").rect(4, 16).extrude(12).translate((ex + ESP[0] / 2 + 1.5, ey, 3)))  # USB-C opening
    t = t.union(_wago_pockets())                                                                     # MOT+, MOT-, keypad GND, spare
    for x, y in TRAY_HOLES:                                                                         # 6 mm corner bosses
        t = t.union(cq.Workplane("XY").circle(5).extrude(6).translate((x, y, 0)))
        t = t.cut(cq.Workplane("XY").circle(M2 / 2).extrude(6).translate((x, y, 0)))
    return t


TRAY_HOLES = [(sx * 92, sy * 57) for sx in (-1, 1) for sy in (-1, 1)]
# PWR-20 WAGO lever connectors (sizes from distributor data [P63]): width x depth x height, wires go in along the depth.
WAGO_221 = {2: (13.1, 18.7, 8.3), 3: (18.7, 18.6, 8.3), 5: (30.0, 18.8, 8.6)}
# Four pockets along the tray's south edge, under the SKR Pico's edge, openings facing -Y (the deck runs come in there):
# MOT+, MOT- and keypad GND (221-413 each) and one spare. 3 walls, 5 mm high: levers stay free, entries stay open.
WAGO_CELL, WAGO_WALL, WAGO_POCKETS = (18.9, 18.8), 1.2, [(-74.0 + 20.1 * k, -47.0) for k in range(4)]


def _wago_pockets() -> cq.Workplane:
    cw, cd = WAGO_CELL
    w = WAGO_WALL
    out = None
    for x, y in WAGO_POCKETS:
        c = cq.Workplane("XY").box(cw + 2 * w, cd + w, 5, centered=(True, False, False)).translate((x, y - cd / 2, 3))
        c = c.cut(cq.Workplane("XY").box(cw, cd, 5, centered=(True, False, False)).translate((x, y - cd / 2, 3)))
        out = c if out is None else out.union(c)
    return out


# ---------------- 03 frame: printed deck, printed bars, M2 throughout ----------------
# The deck replaces plywood: 3 x 3 tiles of 200 mm, black ABS, 24 mm deep (2 mm skin, 3 mm walls, 12 mm ribs),
# bolted edge to edge with M2 x 10 + nuts. Every part that stands on the deck screws into a pilot boss whose position
# is fixed here (PLACE), so there is nothing to measure or mark; a 40 mm grid of spare pilots takes endstops, switches
# and cable clips. Origin: deck top under the zero point; +X toward the camera.
DECK_TILE, DECK_N, DECK_H = 200.0, 3, 24.0
DECK_SKIN, DECK_WALL, DECK_RIB, RIB_H = 2.0, 3.0, 2.0, 12.0     # walls carry the deck; ribs only stiffen the skin
DECK_HALF = DECK_TILE * DECK_N / 2                                # 300: deck 600 x 600
DECK_RIBS = (-DECK_TILE / 6, DECK_TILE / 6)                       # ribs at +-33.3 in each tile, both ways
SEAM_BOLTS, SEAM_Z = (-DECK_TILE / 3, 0.0, DECK_TILE / 3), 16.0   # 3 x M2 x 10 per tile edge, 16 mm below the top
BOSS_DEPTH, GRID_DEPTH, GRID_PITCH = 12.0, 8.0, 40.0

SADDLES_X = (237.0, 278.0)
POWER_XY, TRAY_XY = (220.0, -220.0), (-200.0, 220.0)
RING_SCREW_R, RING_SCREW_A = 163.0, (5.0, 75.0)                   # 2 per ring-scale segment, clear of the seams


def _polar(r: float, a: float) -> tuple[float, float]:
    return r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
TILE_NAMES = ["SW", "S", "SE", "W", "C", "E", "NW", "N", "NE"]     # i (x) and j (y) from -1 to 1; +x = east = camera


def deck_tile_k(k: int):
    """Tile k of TILE_NAMES (0 = SW ... 8 = NE)."""
    return deck_tile(k % 3 - 1, k // 3 - 1)


def deck_tile(i: int, j: int):
    """One 200 mm deck tile, in print orientation: the skin (the deck top) on the bed, walls and ribs up, no supports.
    Pilot bosses (M2 self-tap) at every PLACE point inside it, a 40 mm grid of spare pilots, and 3 M2 clearance holes
    in each wall that meets a neighbour. Local x = -world x (the tile is flipped to print), local y = world y."""
    cx, cy = DECK_TILE * i, DECK_TILE * j
    h = DECK_TILE / 2
    loc = lambda x, y: (-(x - cx), y - cy)
    t = cq.Workplane("XY").box(DECK_TILE, DECK_TILE, DECK_SKIN, centered=(True, True, False))
    walls = cq.Workplane("XY").rect(DECK_TILE, DECK_TILE).rect(DECK_TILE - 2 * DECK_WALL, DECK_TILE - 2 * DECK_WALL).extrude(DECK_H)
    t = t.union(walls)
    for r in DECK_RIBS:
        t = t.union(cq.Workplane("XY").box(DECK_RIB, DECK_TILE - 1, RIB_H, centered=(True, True, False)).translate((r, 0, 0)))
        t = t.union(cq.Workplane("XY").box(DECK_TILE - 1, DECK_RIB, RIB_H, centered=(True, True, False)).translate((0, r, 0)))
    mine = [loc(x, y) for pts in PLACE.values() for x, y in pts if abs(x - cx) < h and abs(y - cy) < h]
    grid = [(gx, gy) for gx in (-80, -40, 0, 40, 80) for gy in (-80, -40, 0, 40, 80)
            if all(math.hypot(gx - mx, gy - my) > 8 for mx, my in mine)]
    for pts, depth, r in ((mine, BOSS_DEPTH, 4.0), (grid, GRID_DEPTH, 3.2)):
        if pts:
            t = t.union(cq.Workplane("XY").pushPoints(pts).circle(r).extrude(depth))
            t = t.cut(cq.Workplane("XY").pushPoints(pts).circle(M2_TAP / 2).extrude(depth))
    seams = []                                                                      # interior edges only
    if i < 1:
        seams.append(("x", -h))        # world +x edge is local -x
    if i > -1:
        seams.append(("x", h))
    if j < 1:
        seams.append(("y", h))
    if j > -1:
        seams.append(("y", -h))
    for axis, e in seams:
        for s in SEAM_BOLTS:
            if axis == "x":
                hole = cq.Workplane("YZ").circle(M2 / 2).extrude(2 * DECK_WALL, both=True).translate((e, s, SEAM_Z))
            else:
                hole = cq.Workplane("XZ").circle(M2 / 2).extrude(2 * DECK_WALL, both=True).translate((s, e, SEAM_Z))
            t = t.cut(hole)
    return t


def _bar(length: float, side=(), top=()):
    """Printed 20 x 20 bar (replaces 2020 extrusion), lying along +x as printed. M2 self-tap pilots straight through at
    fixed stations: `side` along local y, `top` along local z. Clamps screw through their wall into these pilots."""
    b = cq.Workplane("XY").box(length, 20, 20, centered=(False, True, True)).edges("|X").chamfer(1.0)
    for x in side:
        b = b.cut(cq.Workplane("XZ").circle(M2_TAP / 2).extrude(12, both=True).translate((x, 0, 0)))
    for x in top:
        b = b.cut(cq.Workplane("XY").circle(M2_TAP / 2).extrude(12, both=True).translate((x, 0, 0)))
    return b


BAR_FIT = 20.4                                                    # clamp channel for a 20 x 20 bar
COUPLER_L, COUPLER_HOLE = 50.0, 12.5                              # joint sleeve; screws 12.5 mm either side of the joint


def bar_coupler():
    """Joins two bars end to end (outrigger, scan post): 28 x 28 x 50 sleeve, 4 M2 x 16 through one wall pair into the
    bars' pilots 12.5 mm from the joint. Print standing (bore vertical): no supports. Print 2."""
    c = cq.Workplane("XY").box(28, 28, COUPLER_L, centered=(True, True, False))
    c = c.cut(cq.Workplane("XY").rect(BAR_FIT, BAR_FIT).extrude(COUPLER_L))
    for z in (COUPLER_L / 2 - COUPLER_HOLE, COUPLER_L / 2 + COUPLER_HOLE):
        c = c.cut(cq.Workplane("YZ").circle(M2 / 2).extrude(20, both=True).translate((0, 0, z)))
    return c


def protractor_segment():
    """Ring scale + lazy-Susan clamp, 80 deg (print 4: 20-340 deg; the gap around 0 deg is the M4 motor's).
    Its inner wall (r 152.7) centres the lazy Susan's bottom plate (OD 305) and a 2.2 mm lip presses that plate onto
    the deck, so the lazy Susan needs no screws of its own. Two M2 x 10 + washers into the deck pilots
    (PLACE["ring scale"]). Ticks every 5 deg, long ticks every 10 deg, on the top face."""
    r_in, r_lip, r1, span, th, lip_z = 152.7, 150.5, 175.0, 80, 4.6, 3.0    # bottom plate z 0..3, top plate starts z 5
    seg = cq.Workplane("XY").circle(r1).circle(r_in).extrude(th)
    seg = seg.union(cq.Workplane("XY").circle(r_in + 0.5).circle(r_lip).extrude(th - lip_z).translate((0, 0, lip_z)))
    wedge = cq.Workplane("XY").polyline([(0, 0), (300, 0), (300 * math.cos(math.radians(span)), 300 * math.sin(math.radians(span)))]).close().extrude(th + 1)
    seg = seg.intersect(wedge)
    for a in range(0, span + 1, 5):
        ln = 9 if a % 10 == 0 else 5
        tick = cq.Workplane("XY").rect(ln, 0.8).extrude(1).translate((r1 - ln / 2, 0, th - 0.8)).rotate((0, 0, 0), (0, 0, 1), a)
        seg = seg.cut(tick)
    for a in RING_SCREW_A:
        x, y = _polar(RING_SCREW_R, a)
        seg = seg.cut(cq.Workplane("XY").circle(M2 / 2).extrude(th).translate((x, y, 0)))
    return seg


SADDLE_HOLES = [(sx * 14, sy * 13) for sx in (-1, 1) for sy in (-1, 1)]


def bar_saddle():
    """Holds the outrigger bar on the deck: 4 M2 x 12 down into the deck pilots (PLACE["bar saddles"]), 1 M2 x 16
    sideways through a cheek into the bar's pilot. Print 2."""
    s = cq.Workplane("XY").box(40, 40, 6, centered=(True, True, False))
    s = s.faces(">Z").workplane().pushPoints(SADDLE_HOLES).hole(M2)
    for sy in (-1, 1):
        s = s.union(cq.Workplane("XY").box(20, 5, 16, centered=(True, True, False)).translate((0, sy * (10.2 + CLEAR / 2 + 2.5), 6)))
    return s.cut(cq.Workplane("XZ").circle(M2 / 2).extrude(30, both=True).translate((0, 0, 16)))


def post_socket():
    """Stands the scan-camera post upright on the outrigger (x = 674.4): straddles the outrigger's top 14 mm (M2 x 16
    sideways into its pilot) and holds the post in a socket (M2 x 16 into the post's pilot)."""
    s = cq.Workplane("XY").box(40, 32, 20, centered=(True, True, False))
    s = s.cut(cq.Workplane("XY").rect(40, BAR_FIT).extrude(14))                                   # straddles the outrigger
    s = s.cut(cq.Workplane("XZ").circle(M2 / 2).extrude(20, both=True).translate((0, 0, 4)))
    sock = cq.Workplane("XY").box(30, 30, 30, centered=(True, True, False)).translate((0, 0, 20))
    sock = sock.cut(cq.Workplane("XY").rect(BAR_FIT, BAR_FIT).extrude(26).translate((0, 0, 24)))
    return s.union(sock).cut(cq.Workplane("YZ").circle(M2 / 2).extrude(40).translate((-20, 0, 38)))


OUTRIGGER_X = (215.0, 715.0)      # two 250 mm printed bars along +x, joined by a coupler at x = 465


def camera_pillar():
    """Measuring-camera pillar (x = 391.8): straddles the outrigger like the post socket (M2 x 16 into its pilot) and
    rises as a printed 20 x 20 column to z 196, so nothing stands in the scan camera's line of sight. The camera
    plate's clamp slides down the column; its M2 x 16 self-taps into the pilot at the camera axis (z = 150); the
    optional spectral tube (SPC-03a) clamps above it (pilot at z 181). Print standing up, brim on."""
    base_z = 12.0                                                    # straddle bottom (outrigger 6..26 above the deck)
    s = cq.Workplane("XY").box(40, 32, 20, centered=(True, True, False))
    s = s.cut(cq.Workplane("XY").rect(40, BAR_FIT).extrude(14))
    s = s.cut(cq.Workplane("XZ").circle(M2 / 2).extrude(20, both=True).translate((0, 0, 4)))
    top = 196.0 - base_z
    col = cq.Workplane("XY").box(20, 20, top - 20, centered=(True, True, False)).translate((0, 0, 20))
    col = col.union(cq.Workplane("XY").box(30, 30, 10, centered=(True, True, False)).translate((0, 0, 20)))   # foot fillet
    col = col.faces(">Z").edges().chamfer(1.5)
    for z in (150.0, 181.0):                                         # camera axis, spectral tube clamp
        col = col.cut(cq.Workplane("XZ").circle(M2_TAP / 2).extrude(20, both=True).translate((0, 0, z - base_z)))
    return s.union(col)


def end_foot():
    """Holds the far end of the outrigger level with the saddles: 30 mm = deck (24) + saddle floor (6). Stands on the
    table beyond the deck; M2 x 16 sideways into the outrigger's pilot."""
    f = cq.Workplane("XY").box(40, 40, 30, centered=(True, True, False))
    f = f.union(cq.Workplane("XY").box(20, 32, 12, centered=(True, True, False)).translate((0, 0, 30)))
    f = f.cut(cq.Workplane("XY").rect(20, BAR_FIT).extrude(12).translate((0, 0, 30)))
    return f.cut(cq.Workplane("XZ").circle(M2 / 2).extrude(20, both=True).translate((0, 0, 40)))


# ---------------- 04 light arm ----------------
RIM_TEETH = 480                               # 24:1 with a 20T pinion meshing the rim belt; set gear_ratio from the real rim
RIM_R = RIM_TEETH * GT2_PITCH / (2 * math.pi)


GT2_BACK = 0.38                               # GT2 belt back -> pitch line (1.38 thick - 0.75 tooth - 0.254 PLD)
RIM_SEAT_R = RIM_R - GT2_BACK                 # belt back glued here (teeth out): its pitch line lands on RIM_R
RIM_BODY_R = RIM_R - 2.5                      # the pinion's 16 mm flanges reach r = RIM_R - 1.6 at the mesh
RIM_H, BAND_Z = 9.0, (1.5, 7.5)               # 6 mm belt band; belt edges line up with the band edges


def rim_segment(inner: float = 22.0):
    """1/8 of the belt rim. The GT2 belt is CA-glued teeth-out on a 6 mm band whose edges match the belt's; no lips,
    so the 20T pinion's flanges pass above and below the band (lips would collide with them). Print 7 (+ the arm
    segment LAR-08c). Two radial M2 slots: bolt (M2 x 12 + printed washer + nut) through whichever top-plate hole falls
    under a slot; CA-glue the rest; the belt ties the ring together."""
    seg = cq.Workplane("XY").circle(RIM_BODY_R).circle(RIM_R - inner).extrude(RIM_H)
    seg = seg.union(cq.Workplane("XY").circle(RIM_SEAT_R).circle(RIM_BODY_R - 1).extrude(BAND_Z[1] - BAND_Z[0]).translate((0, 0, BAND_Z[0])))
    wedge = cq.Workplane("XY").polyline([(0, 0), (300, 0), (300 * math.cos(math.radians(45)), 300 * math.sin(math.radians(45)))]).close().extrude(10)
    seg = seg.intersect(wedge)
    for a in (11.25, 33.75):                                                          # radial slots, r = RIM_R-20 .. RIM_R-6
        sl = cq.Workplane("XY").slot2D(14 + M2, M2, 0).extrude(RIM_H).translate((RIM_R - 13, 0, 0))
        seg = seg.cut(sl.rotate((0, 0, 0), (0, 0, 1), a))
    return seg


RING_MOTOR_R = RIM_R + 20 * GT2_PITCH / (2 * math.pi)   # pitch circles touch: 20T pinion on the rim belt's pitch line
RING_BASE = (156.0 - RING_MOTOR_R, 211.0 - RING_MOTOR_R)  # base from r 156 (outside the lazy Susan) to r 211 (before saddle 1)


def ring_motor_mount():
    """M4 drive at angle 0 (+X). The base screws to the deck OUTSIDE the lazy Susan (r > 156) through slots that
    stay reachable from above; the 56 mm motor plate cantilevers inward at z 25 above the rim, narrow enough that the
    arm segment clears it at the travel ends (lamp 20 / 324 deg = upright 35 / 339 deg). Motor stands on the plate, shaft down; its 20T pulley meshes
    with the teeth-out rim belt at band height. Radial slots (M2 x 12 + washers into the deck pilots) set the mesh.
    Local x = radius - RING_MOTOR_R."""
    pz, WB, WP = 25.0, 96.0, 56.0
    x0, x1 = RING_BASE
    base = cq.Workplane("XY").box(x1 - x0, WB, 6, centered=(False, True, False)).translate((x0, 0, 0))
    for y in (-38, 38):                                         # outside the plate: a screwdriver reaches them
        base = base.cut(cq.Workplane("XY").slot2D(x1 - x0 - 14, M2, 0).extrude(6).translate(((x0 + x1) / 2, y, 0)))
    walls = cq.Workplane("XY").box(6, WP, pz - 6, centered=(False, True, False)).translate((x1 - 6, 0, 6))
    for s in (-1, 1):
        walls = walls.union(cq.Workplane("XY").box(x1 - x0, 6, pz - 6, centered=(False, False, False)).translate((x0, s * WP / 2 - (6 if s > 0 else 0), 6)))
    plate = cq.Workplane("XY").box(x1 + 26, WP, 5, centered=(False, True, False)).translate((-26, 0, pz))
    plate = plate.cut(cq.Workplane("XY").slot2D(NEMA17_BOSS + 8, NEMA17_BOSS, 0).extrude(5).translate((0, 0, pz)))
    for x in (-1, 1):
        for y in (-1, 1):
            plate = plate.cut(cq.Workplane("XY").slot2D(3.4 + 8, 3.4, 0).extrude(5).translate((x * NEMA17_HOLES / 2, y * NEMA17_HOLES / 2, pz)))
    return base.union(walls).union(plate)


ARM_R = RIM_R - 16.0                          # light-arm upright centre radius (on the rim, inside the belt band)
UPRIGHT_OFFSET = 36.0                         # upright stands this far BESIDE the lamp's beam line, not on it: a 20 mm
                                              # upright on the beam line would shade the sample (beam bundle +-21 mm there)
UPRIGHT_LEAD = math.degrees(math.asin(UPRIGHT_OFFSET / ARM_R))     # upright azimuth - lamp azimuth, 15.3 deg
LAMP_ARM_X = -UPRIGHT_OFFSET + 22.0           # horizontal arm, measured from the beam line (cross-clamp pitch 22 mm)


def arm_segment():
    """Arm segment: one rim segment (same belt band and slots, wider inward) carrying the upright bar's socket at its
    middle (22.5 deg), so the arm needs no plate holes of its own and cannot collide with the rim. The socket is
    turned by -UPRIGHT_LEAD so the cross clamp and the horizontal arm run parallel to the beam line (the upright
    stands 36 mm beside it). Turn the rim so one slot lands on a top-plate hole: M2 x 12 + nut there, CA-glue the
    whole underside. M2 x 16 through the socket wall into the upright's pilot."""
    seg = rim_segment(inner=31.0)
    sock = cq.Workplane("XY").box(30, 30, 30, centered=(True, True, False)).translate((0, 0, RIM_H))
    sock = sock.cut(cq.Workplane("XY").rect(BAR_FIT, BAR_FIT).extrude(26).translate((0, 0, RIM_H + 4)))
    sock = sock.cut(cq.Workplane("XZ").circle(M2 / 2).extrude(40).translate((0, 20, RIM_H + ARM_SOCKET_PIN)))   # into the upright
    sock = sock.rotate((0, 0, 0), (0, 0, 1), -UPRIGHT_LEAD).translate((ARM_R, 0, 0))
    return seg.union(sock.rotate((0, 0, 0), (0, 0, 1), 22.5))


def cross_clamp():
    """Joins the light-arm upright and the horizontal arm side by side (channels 22 mm apart, not crossing). Slide it
    down the upright until its screw lines up with the upright's lamp-height pilot: M2 x 16 into each bar."""
    c = cq.Workplane("XY").box(54, 32, 32, centered=(True, True, False))
    c = c.cut(cq.Workplane("XY").rect(BAR_FIT, BAR_FIT).extrude(32).translate((-11, 0, 0)))         # upright, through (along z)
    c = c.cut(cq.Workplane("XZ").rect(BAR_FIT, BAR_FIT).extrude(20, both=True).translate((11, 0, 16)))   # arm, through (along y)
    c = c.cut(cq.Workplane("YZ").circle(M2 / 2).extrude(10).translate((-27, 0, 16)))               # into the upright, from -x
    return c.cut(cq.Workplane("XY").circle(M2 / 2).extrude(6).translate((11, 0, 26)))              # into the arm, from above


# Light-arm bars: upright in the arm segment's socket (z 21 .. 221), horizontal arm along +y through the cross clamp.
ARM_SOCKET_PIN = 18.0                                         # socket screw height above the rim segment top
ARM_Z = 150.0 + 48 / 2 + 12                                   # horizontal-arm centre: the lamp clamp's channel (z 186)
UPRIGHT_Z0 = 8.0 + RIM_H + 4                                  # rim on the top plate (z 8), socket floor 4 mm
ARM_Y = math.sqrt(ARM_R ** 2 - UPRIGHT_OFFSET ** 2)           # upright centre, y (light arm at 90 deg)
ARM_Y0 = ARM_Y - 16                                           # arm bar starts flush with the cross clamp's back


def upright_bar():
    """Light-arm upright, 200 mm: pilots for the arm-segment socket and the cross clamp (both along world x)."""
    return _bar(200, top=(8 + RIM_H + ARM_SOCKET_PIN - UPRIGHT_Z0, ARM_Z - UPRIGHT_Z0))


def arm_bar():
    """Horizontal light arm, 200 mm: pilots (vertical) for the cross clamp and the lamp clamp, 11 mm in front of the
    lamp's back face (COB 300 mm from the zero point)."""
    return _bar(200, top=(ARM_Y - ARM_Y0, 300.0 + LAMP_COB_Z - 11.0 - ARM_Y0))


# ---------------- 05/08/09 axes: bolts as axles (no shafts to cut, no flats to file) ----------------
# Table: an M8 x 70 bolt turns in two 608s; head, inner races, spacers, the 100T pulley and the hub are clamped by
# one M8 nut in the hub's hex trap, so the stack turns as one. Tilt: two M8 x 35 stub bolts, nuts trapped in the
# cradle. Spin: direct drive, the platter clamps the pancake motor's D-shaft.
M8_NUT = 13.0 + 0.3                                       # across flats + clearance (hex trap)
STACK = {"head": 5.5, "bearing": 7.0, "pulley": 9.4, "shim_head": 2.0, "shim": 1.0}
MOTOR_BODY = 48.0                                         # clearance for bodies up to 48 mm (17HS4401 is 38 [P58])


def gt2_pulley(teeth: int, bore: float = 8.0 + CLEAR):
    """Printed GT2 pulley (simplified round-tooth profile), hubless: clamped on the tilt stub bolt. 100T = tilt (5:1)."""
    pd = teeth * GT2_PITCH / math.pi
    od = pd - 0.508
    body = cq.Workplane("XY").circle(od / 2).extrude(7)
    body = body.cut(cq.Workplane("XY").polarArray(od / 2 + 0.15, 0, 360, teeth).circle(0.6).extrude(7))
    fl = cq.Workplane("XY").circle(od / 2 + 2).extrude(1.2)
    p = fl.union(body.translate((0, 0, 1.2))).union(fl.translate((0, 0, 8.2)))
    return p.cut(cq.Workplane("XY").circle(bore / 2).extrude(10))


def home_flag():
    """1.5 mm blade for the TCST2103 3.1 mm slot, with a tab: two M2 x 8 self-tap into the moving part. Print 3."""
    tab = cq.Workplane("XY").box(16, 10, 4, centered=(True, True, False))
    tab = tab.faces(">Z").workplane().pushPoints([(-4.5, 0), (4.5, 0)]).hole(M2)
    blade = cq.Workplane("XY").box(1.5, 24, 10, centered=(True, False, False)).translate((0, 5, 0))
    return tab.union(blade)


# Table: FIXED axle. An M8 x 75 bolt stands in the post, its head locked in a hex pocket. The rotating drum (100T teeth
# + hub) carries two 608s on their OUTER races; the inner races sit on the bolt, clamped by a 1 mm shim on the post top,
# a 6 mm spacer and the top nut (13 mm spanner, the bolt can't turn). Like a skateboard wheel: nothing to cut or file.
# Heights in mm above the deck. The motor stands shaft-up inside the lazy Susan opening (ID ~160 mm); its 20T teeth
# (z ~54-61) set the drum's tooth band.
TABLE_Z = {"floor": 1.0}
TABLE_Z["head_top"] = TABLE_Z["floor"] + STACK["head"]                  # bolt head 1.0 .. 6.5, hex-locked
TABLE_Z["drum"] = MOTOR_BODY + 5.5                                      # drum bottom 53.5 (0.5 above the motor bracket); teeth 54.7 .. 61.7
TABLE_Z["post_top"] = TABLE_Z["drum"] - STACK["shim"]                   # 51.8: the shim carries the lower inner race
TABLE_Z["b1"] = TABLE_Z["drum"]                                         # lower 608 52.8 .. 59.8 (in the drum)
TABLE_Z["b2"] = TABLE_Z["b1"] + STACK["bearing"] + 6.0                  # upper 608 65.8 .. 72.8
TABLE_Z["nut"] = TABLE_Z["b2"] + STACK["bearing"]                       # M8 nut 72.8 .. 79.3 (bolt end 81.5)
TABLE_Z["hub_top"] = TABLE_Z["nut"] + 7.2                               # drum top 80.0: yoke base sits here
TABLE_BELT_C = 49.4                                                      # 232 mm GT2 loop, 20T-100T centre distance


def spacers():
    """All printed spacers (r 6: inner races only). Table: 1 mm shim (post top) + 6 mm spacer.
    Tilt: 2 x 6.8 (arm -> cradle), 2 x 1 mm (pulley / head side), 1 x 9.4 (the side without a pulley).
    Plus 2 wide M2 washers (12 mm) for the rim bolts: a steel M2 washer would slip through the lazy Susan's holes."""
    hs = [STACK["shim"], 6.0, 6.8, 6.8, 1.0, 1.0, STACK["pulley"]]
    s = cq.Workplane("XY")
    for i, h in enumerate(hs):
        s = s.union(cq.Workplane("XY").circle(6).circle(4.2 + CLEAR / 2).extrude(h).translate((16 * (i % 4), 16 * (i // 4), 0)))
    for i in range(2):
        s = s.union(cq.Workplane("XY").circle(6).circle(M2 / 2).extrude(1.6).translate((16 * (3 + i) - 16, 16, 0)))
    return s


def table_post():
    """Fixed post at (0, 0): round flange (4 x M2 x 12 into the deck pilots), tube up to z 51.8, hex pocket that locks
    the M8 x 75 bolt head (insert the bolt from below before screwing the post down)."""
    post = cq.Workplane("XY").circle(27).extrude(6)                    # r 27: clears the table motor (r > 28.4)
    post = post.faces(">Z").workplane().polarArray(22.2, 45, 360, 4).hole(M2)
    post = post.union(cq.Workplane("XY").circle(14).extrude(TABLE_Z["post_top"]))
    post = post.cut(cq.Workplane("XY").polygon(6, M8_NUT / math.cos(math.radians(30))).extrude(TABLE_Z["head_top"]))   # open below
    return post.cut(cq.Workplane("XY").circle(M8 / 2).extrude(TABLE_Z["post_top"]))


def table_drum():
    """The turning table: 100T GT2 teeth at the bottom, two 608 outer-race seats, nut recess at the top (open:
    tighten with a 13 mm spanner before the yoke goes on), OG-40 top (M2 x 12 self-tap) for the yoke, 2 flag holes."""
    pd = 100 * GT2_PITCH / math.pi
    od = pd - 0.508
    z0 = TABLE_Z["drum"]
    teeth = cq.Workplane("XY").circle(od / 2).extrude(7)
    teeth = teeth.cut(cq.Workplane("XY").polarArray(od / 2 + 0.15, 0, 360, 100).circle(0.6).extrude(7))
    fl = cq.Workplane("XY").circle(od / 2 + 2).extrude(1.2)
    d = fl.union(teeth.translate((0, 0, 1.2))).union(fl.translate((0, 0, 8.2)))
    d = d.union(cq.Workplane("XY").circle(34).extrude(TABLE_Z["hub_top"] - z0 - 9.4).translate((0, 0, 9.4)))
    h = TABLE_Z["hub_top"] - z0
    for zz in (TABLE_Z["b1"], TABLE_Z["b2"]):
        d = d.cut(cq.Workplane("XY").circle(BEARING_608[0] / 2).extrude(STACK["bearing"]).translate((0, 0, zz - z0)))
    d = d.cut(cq.Workplane("XY").circle(7.0).extrude(h))                                    # inner races / spacer clear
    d = d.cut(cq.Workplane("XY").circle(10).extrude(h - (TABLE_Z["nut"] - z0)).translate((0, 0, TABLE_Z["nut"] - z0)))   # nut + spanner
    d = d.faces(">Z").workplane().rect(OG40, OG40, forConstruction=True).vertices().hole(M2_TAP, 12)   # M2 x 12 self-tap from the yoke
    return d.cut(cq.Workplane("XY").pushPoints([(-TFLAG["tab_r"], -4.5), (-TFLAG["tab_r"], 4.5)]).circle(M2_TAP / 2).extrude(8).translate((0, 0, h - 8)))


def table_motor_bracket():
    """Holds the table motor shaft-up on the deck inside the lazy Susan opening (motor centre 49.4 mm from the
    axis for a 232 mm belt): two side rails with radial slots (M2 x 12 + washers into the deck pilots: slide to tension
    the belt), a top plate that screws to the motor face (4 x M3 x 8, the motor's own thread)."""
    gap = 42.6
    rails = cq.Workplane("XY")
    for s in (-1, 1):
        r = cq.Workplane("XY").box(46, 8, MOTOR_BODY, centered=(True, False, False)).translate((0, s * gap / 2 - (8 if s < 0 else 0), 0))
        foot = cq.Workplane("XY").box(36, 10, 6, centered=(True, False, False)).translate((0, s * (gap / 2 + 8) - (10 if s < 0 else 0), 0))
        foot = foot.cut(cq.Workplane("XY").slot2D(24, M2, 0).extrude(6).translate((0, s * (gap / 2 + 13), 0)))   # stays inside r 80
        rails = rails.union(r).union(foot)
    top = cq.Workplane("XY").box(46, gap + 16, 5, centered=(True, True, False)).translate((0, 0, MOTOR_BODY))
    top = top.cut(cq.Workplane("XY").circle(NEMA17_BOSS / 2 + 0.3).extrude(5).translate((0, 0, MOTOR_BODY)))
    top = top.cut(cq.Workplane("XY").rect(NEMA17_HOLES, NEMA17_HOLES, forConstruction=True).vertices().circle(M3 / 2).extrude(5).translate((0, 0, MOTOR_BODY)))
    return rails.union(top)


# Table home: the flag (TBL-07h) sits on the drum's top at local -x, so at home (M3 = -180) its fin is at world +X,
# in the slot of a TCST2103 endstop (TBL-04) on a riser (TBL-07g) screwed to three deck pilots inside the lazy Susan.
# Fin at r 60: clear of the table motor's pulley (r <= 57.4) and the motor bracket (z <= 53.5) when it swings past 180.
# Endstop PCB at z 56, so its plugged lead stays below the yoke base that sweeps r <= 72 from the drum top (z 80.7) up.
TFLAG = {"tab_r": 30.0, "fin_r": 60.0, "fin_len": 20.0, "fin_t": 1.5, "fin_bottom": 62.0, "tab_t": 4.0}
ENDSTOP_Z = 56.0                                                        # TBL-04 PCB underside above the deck
ENDSTOP_FEET = [(40.0, -40.0), (40.0, 0.0), (40.0, 40.0)]               # spare-grid pilots of the C tile


def table_flag():
    """Home flag for the table, in print pose (the face that sits on the drum is up at z 4; fin standing up from the
    bed): a tab on the drum's two flag holes, a bridge out past the drum, a fin at r 60 that hangs down when fitted and
    passes edge-first through the TCST2103's 3.1 mm slot (1.5 mm thick: 0.8 mm each side). x = radius from the axis."""
    t, r0, rf = TFLAG["tab_t"], TFLAG["tab_r"], TFLAG["fin_r"]
    tab = cq.Workplane("XY").box(10, 16, t, centered=(True, True, False)).translate((r0, 0, 0))
    tab = tab.cut(cq.Workplane("XY").pushPoints([(r0, -4.5), (r0, 4.5)]).circle(M2 / 2).extrude(t))
    bridge = cq.Workplane("XY").box(rf + 1.5 - (r0 + 5), 10, t, centered=(False, True, False)).translate((r0 + 5, 0, 0))
    fin_h = TABLE_Z["hub_top"] - TFLAG["fin_bottom"]
    fin = cq.Workplane("XY").box(TFLAG["fin_t"], TFLAG["fin_len"], fin_h + t, centered=(True, True, False)).translate((rf, 0, 0))
    return tab.union(bridge).union(fin)


def endstop_riser():
    """Stands the table endstop (TBL-04) at r 60 on +X, PCB long axis radial, slot at the fin's radius. A T foot on three
    deck pilots (3 x M2 x 10), a post outside the lazy Susan's drum clearance, a pad with two M2 self-tap pilots and
    2 mm bosses (the module's solder side clears the pad). World coordinates: deck top = z 0."""
    rf, z = TFLAG["fin_r"], ENDSTOP_Z
    foot = cq.Workplane("XY").box(12, 92, 5, centered=(True, True, False)).translate((40, 0, 0))
    foot = foot.union(cq.Workplane("XY").box(38, 20, 5, centered=(False, True, False)).translate((34, 0, 0)))
    foot = foot.cut(cq.Workplane("XY").pushPoints(ENDSTOP_FEET).circle(M2 / 2).extrude(5))
    post = cq.Workplane("XY").box(12, 20, z - 2 - 6 - 5, centered=(False, True, False)).translate((rf, 0, 5))
    pad = cq.Workplane("XY").box(33, 11, 6, centered=(True, True, False)).translate((rf, 0, z - 2 - 6))
    holes = [(rf - 12.5, 0), (rf + 12.5, 0)]
    pad = pad.union(cq.Workplane("XY").pushPoints(holes).circle(3).extrude(2).translate((0, 0, z - 2)))
    zp = z - 2 - 6                                                                    # 45 deg web under the inner pad: prints with no support
    web = cq.Workplane("XZ").polyline([(rf, zp - (rf - (rf - 16.5))), (rf, zp), (rf - 16.5, zp)]).close().extrude(5.5, both=True)
    r = foot.union(post).union(pad).union(web)
    return r.cut(cq.Workplane("XY").pushPoints(holes).circle(M2_TAP / 2).extrude(8).translate((0, 0, z - 8)))


YOKE_INNER = 116.0
YOKE_BASE = 6.0
YOKE_SEAT = 150.0 - TABLE_Z["hub_top"]                                  # tilt axis through the zero point
TILT_BELT_C = 75.6                                                       # 280 mm GT2 loop, 20T-100T
YOKE_TOP = YOKE_SEAT + TILT_BELT_C + 21 + 8                              # the tilt motor sits above the axis, inside the yoke


def tilt_yoke():
    """U yoke on the table hub (OG-40). 608 seats (outer face of each arm) put the tilt axis through the zero point.
    The tilt motor hangs on the inner face of the +X arm, above the axis, shaft out through the arm (slots = belt
    tension); its pulley drives the 100T on the stub axle outside the arm. Everything stays within r 70 of the table axis."""
    base = cq.Workplane("XY").box(YOKE_INNER + 24, 34, YOKE_BASE, centered=(True, True, False))
    base = og40_holes(base.faces(">Z").workplane())
    base = base.cut(cq.Workplane("XY").circle(5).extrude(YOKE_BASE))                     # bolt end of the table axle
    for s in (-1, 1):
        x0 = s * (YOKE_INNER / 2 + 6)
        arm = cq.Workplane("XY").box(12, 34, YOKE_TOP, centered=(True, True, False)).translate((x0, 0, 0))
        seat_x = s * (YOKE_INNER / 2 + 12) - (7.2 if s > 0 else 0)
        arm = arm.cut(cq.Workplane("YZ").circle(BEARING_608[0] / 2).extrude(7.2).translate((seat_x, 0, YOKE_SEAT)))
        arm = arm.cut(cq.Workplane("YZ").circle(6.5).extrude(14).translate((x0 - 7, 0, YOKE_SEAT)))
        if s > 0:
            mz = YOKE_SEAT + TILT_BELT_C
            arm = arm.cut(cq.Workplane("YZ").slot2D(NEMA17_BOSS + 8, NEMA17_BOSS, 90).extrude(14).translate((x0 - 7, 0, mz)))
            for dy in (-1, 1):
                for dz in (-1, 1):
                    arm = arm.cut(cq.Workplane("YZ").slot2D(3.4 + 8, 3.4, 90).extrude(14).translate((x0 - 7, dy * NEMA17_HOLES / 2, mz + dz * NEMA17_HOLES / 2)))
        base = base.union(arm)
    return base


SPIN = {"platter": 8.0, "hub": 10.0, "motor_face": -24.0, "motor_body": 21.5}   # 17HS08-1004S pancake, 20 mm shaft


def tilt_cradle():
    """Turns about the tilt axis (local z = 0 = sample face = zero point). End blocks trap the M8 nuts of the two
    M8 x 35 stub axles; the floor holds the pancake spin motor face-up (4 x M3 x 8). Printed upside down."""
    w = YOKE_INNER - 4
    depth = 34.0
    zb = SPIN["motor_face"]
    floor = cq.Workplane("XY").box(w, depth, 5, centered=(True, True, False)).translate((0, 0, zb))
    floor = floor.cut(cq.Workplane("XY").circle(NEMA17_BOSS / 2 + 0.3).extrude(5).translate((0, 0, zb)))
    floor = floor.cut(cq.Workplane("XY").rect(NEMA17_HOLES, NEMA17_HOLES, forConstruction=True).vertices().circle(M3 / 2).extrude(5).translate((0, 0, zb)))
    c = floor
    for s in (-1, 1):
        x0 = s * (w / 2 - 6)
        blk = cq.Workplane("XY").box(12, depth, 10 - zb, centered=(True, True, False)).translate((x0, 0, zb))
        blk = blk.cut(cq.Workplane("YZ").circle(M8 / 2).extrude(12).translate((x0 - 6, 0, 0)))
        inner = x0 - s * 6                                                         # nut trapped flush with the inner face
        blk = blk.cut(cq.Workplane("YZ").polygon(6, M8_NUT / math.cos(math.radians(30))).extrude(6.6).translate((inner if s > 0 else inner - 6.6, 0, 0)))
        c = c.union(blk)
    return c.translate((0, 0, -zb))


def spin_platter():
    """Sample face (top = tilt axis = zero point), r 42 between the cradle end blocks. Hub clamps the pancake motor's
    5 mm D-shaft: M2 x 6 into a captive M2 nut, tip on the flat. M2 holes for risers (stage 11); flag holes on the rim.
    Printed upside down (top face on the bed)."""
    p = cq.Workplane("XY").circle(42).extrude(SPIN["platter"])
    p = p.union(cq.Workplane("XY").circle(8).extrude(SPIN["hub"]).translate((0, 0, -SPIN["hub"])))
    p = p.cut(cq.Workplane("XY").circle(2.6 + CLEAR / 2).extrude(SPIN["hub"] + SPIN["platter"] - 4).translate((0, 0, -SPIN["hub"])))
    g = cq.Workplane("YZ").circle(M2 / 2).extrude(10).translate((0, 0, -SPIN["hub"] / 2))
    g = g.union(cq.Workplane("XY").box(1.8, M2_NUT / math.cos(math.radians(30)), 7).translate((4.2, 0, -SPIN["hub"] / 2 - 2.5)))   # nut slot from below
    p = p.cut(g)
    p = p.faces(">Z").workplane().polarArray(15, 45, 360, 4).hole(M2_TAP, 5)      # risers (stage 11): M2 self-tap
    return p.cut(cq.Workplane("XY").pushPoints([(36, -4.5), (36, 4.5)]).circle(M2_TAP / 2).extrude(5))


# ---------------- 06 camera + light ----------------
def aperture_stop():
    """f/8 for f = 16 mm: 2.0 mm hole. Disc sits in front of the M12 lens; adjust OD to your holder."""
    return cq.Workplane("XY").circle(7).circle(1.0).extrude(1.2)


CAM_PLATE, CAM_STANDOFF, CAM_BOARD, CAM_HOLDER, CAM_LENS_OUT = 4.0, 6.0, 1.6, 11.0, 7.0
CAM_LENS_Z = CAM_PLATE + CAM_STANDOFF + CAM_BOARD + CAM_HOLDER + CAM_LENS_OUT   # plate back -> lens front, 29.6
CAM_CLAMP = 24.4                                                                   # bar channel centre 12.2 behind the plate
CAM_POST_OFFSET = CAM_CLAMP / 2 + CAM_LENS_Z                                       # post centre -> lens front, 41.8
CAM_POST_X = 350.0 + CAM_POST_OFFSET                                               # measuring post: lens front at 350


def _camera_face():
    """Plate + 4 standoffs (6 mm: room for the board's back parts and a side-entry USB-C plug). Camera looks along +z."""
    p = cq.Workplane("XY").box(50, 50, CAM_PLATE, centered=(True, True, False))
    pts = [(sx * 17, sy * 17) for sx in (-1, 1) for sy in (-1, 1)]                                   # 34 mm square [K3]
    for x, y in pts:
        p = p.union(cq.Workplane("XY").circle(3).extrude(CAM_STANDOFF).translate((x, y, CAM_PLATE)))
    p = p.cut(cq.Workplane("XY").pushPoints(pts).circle(M2_TAP / 2).extrude(CAM_PLATE + CAM_STANDOFF))   # M2 x 8 self-tap (FRM-06)
    return p.cut(cq.Workplane("XY").circle(17 / 2).extrude(CAM_PLATE))                                # cable / back-part relief


def _post_clamp(tilt: float = 0.0, off: float = CAM_CLAMP / 2):
    """Clamp block behind the plate for a vertical 20 x 20 printed post, channel centre `off` mm behind the plate back.
    tilt > 0: the camera looks `tilt` deg down while the channel stays vertical (block rotated about the plate's
    x axis, then trimmed at the plate back)."""
    blk = cq.Workplane("XY").box(30, 40, off + 12.2 + 20, centered=(True, True, False)).translate((0, 0, -off - 12.2))
    ch = cq.Workplane("XZ").rect(BAR_FIT, BAR_FIT).extrude(40, both=True).translate((0, 0, -off))
    m2 = cq.Workplane("YZ").circle(M2 / 2).extrude(30, both=True).translate((0, 0, -off))
    rot = lambda w: w.rotate((0, 0, 0), (1, 0, 0), -tilt)
    blk = rot(blk).intersect(cq.Workplane("XY").box(30, 80, 80, centered=(True, True, False)).translate((0, 0, -80)))
    return blk.cut(rot(ch)).cut(rot(m2))


def camera_plate():
    """Arducam B0433 38 x 38 mm board on 4 x M2 x 8 self-tap into 6 mm standoffs. Clamp block behind grips the camera
    pillar (M2 x 16 into its pilot): the camera looks along +z, the post centre is CAM_POST_OFFSET = 41.8 mm behind
    the lens front (measuring post at x = 391.8 for a 350 mm working distance)."""
    return _camera_face().union(_post_clamp())


HS_H, PAD_T, COB_H = 11.6, 0.25, 1.4          # LSR-03 Wakefield 910-40-2-12-2-B-0 [L28], LSR-04 3M 8810, LSR-01 Citizen CLU701 [L25]
HOLDER_D, HOLDER_H, PRELOAD = 35.0, 3.6, 0.3  # LSR-06 TE Z35 2213678-5 [L23]; the stack stands 0.3 mm proud so the cap clamps it
LAMP_POCKET = HS_H + HOLDER_H - PRELOAD       # lamp back face -> pocket front wall (the holder face bears on it)
LAMP_COB_Z = HS_H - PRELOAD + PAD_T + COB_H   # lamp back face -> COB emitter: 300 mm from the zero point
LAMP_EXIT_Z = 74.0                            # lamp back face -> exit aperture


def lamp_tube():
    """Lamp: rear square pocket for the 40 x 40 heatsink, a round seat in front of it that centres the TE Z35 COB holder [L23],
    a 50 mm tube with a 10 mm exit aperture and a 1 mm polarizer slot, and a bar clamp on top (M2 x 16 into the arm's pilot),
    offset sideways by LAMP_ARM_X (the arm runs 14 mm beside the beam line) so the beam axis passes through the zero point.
    The cap (LSR-05b) presses heatsink + holder forward with 4 x M2 x 12 self-tap: the heatsink stops 0.5 mm short of the
    seat's ledge, so all the clamp force goes through the holder onto the COB. A groove in the -y wall takes the two leads."""
    S = 48.0
    body = cq.Workplane("XY").box(S, S, 22, centered=(True, True, False))
    body = body.cut(cq.Workplane("XY").rect(40.6, 40.6).extrude(HS_H - PRELOAD + 0.5))      # heatsink pocket
    body = body.cut(cq.Workplane("XY").circle(HOLDER_D / 2 + 0.2).extrude(LAMP_POCKET))     # holder seat (centres the COB)
    body = body.cut(cq.Workplane("XY").rect(6, 5.8).extrude(LAMP_POCKET).translate((0, -19.9, 0)))   # lead groove to the cap slot
    body = body.cut(cq.Workplane("XY").circle(12).extrude(22))                              # light through
    body = body.faces("<Z").workplane().pushPoints([(sx * 22, sy * 22) for sx in (-1, 1) for sy in (-1, 1)]).hole(M2_TAP, 10)
    tube = cq.Workplane("XY").circle(16).circle(13).extrude(50).translate((0, 0, 22))
    tube = tube.union(cq.Workplane("XY").circle(16).circle(5).extrude(2).translate((0, 0, 72)))
    tube = tube.cut(cq.Workplane("XY").box(40, 34, 1.2, centered=(False, True, False)).translate((-5, 0, 64)))
    clamp = cq.Workplane("XY").box(30, 24, 22, centered=(True, False, False)).translate((LAMP_ARM_X, S / 2, 0))
    clamp = clamp.cut(cq.Workplane("XY").rect(BAR_FIT, BAR_FIT).extrude(22).translate((LAMP_ARM_X, S / 2 + 12, 0)))
    clamp = clamp.cut(cq.Workplane("XZ").circle(M2 / 2).extrude(-30).translate((LAMP_ARM_X, S / 2 + 10, 11)))
    return body.union(tube).union(clamp)


def lamp_cap():
    """Back cap: 4 x M2 x 12 into the lamp body; slot over the body's lead groove; vents."""
    c = cq.Workplane("XY").box(48, 48, 3, centered=(True, True, False))
    c = c.faces(">Z").workplane().pushPoints([(sx * 22, sy * 22) for sx in (-1, 1) for sy in (-1, 1)]).hole(M2)
    c = c.cut(cq.Workplane("XY").rect(8, 2.8).extrude(3).translate((0, -21.5, 0)))
    for k in range(4):
        c = c.cut(cq.Workplane("XY").rect(24, 2.5).extrude(3).translate((0, -6 + 5 * k, 0)))
    return c


# ---------------- 07 calibrate ----------------
PTFE_SQ, PTFE_STACK = 50.0 + 1.0, 3 * 3.0       # 50 mm squares knife-cut from a 100 x 100 x 3 mm sheet (CAL-01), 3 stacked


def ptfe_holder():
    """White tile: 3 x 3 mm PTFE squares (9 mm: opaque like a 3/8 in plate), top face flush with the rim.
    Corner reliefs take knife-cut corners; finger notch to lift the stack out."""
    h = cq.Workplane("XY").box(60, 60, 2.4 + PTFE_STACK, centered=(True, True, False))
    h = h.cut(cq.Workplane("XY").rect(PTFE_SQ, PTFE_SQ).extrude(PTFE_STACK).translate((0, 0, 2.4)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            h = h.cut(cq.Workplane("XY").circle(1.5).extrude(PTFE_STACK).translate((sx * PTFE_SQ / 2, sy * PTFE_SQ / 2, 2.4)))
    return h.cut(cq.Workplane("XY").circle(8).extrude(PTFE_STACK).translate((0, 28.5, 2.4)))       # finger notch


def mirror_holder():
    h = cq.Workplane("XY").box(60, 60, 8, centered=(True, True, False))
    return h.cut(cq.Workplane("XY").rect(50.5, 50.5).extrude(5).translate((0, 0, 3)))


def ball_holder():
    """Two 1 in chrome balls 40 mm apart on conical seats [E6]."""
    b = cq.Workplane("XY").box(66, 28, 14, centered=(True, True, False))
    for x in (-20, 20):                                       # 90 deg cone, 22 mm at the top: the ball sits on a ring
        b = b.cut(cq.Workplane("XY").add(cq.Solid.makeCone(2.0, 11.0, 9.0, cq.Vector(x, 0, 5))))   # 2 mm below the top
    return b


def dowel_socket():
    s = cq.Workplane("XY").circle(10).extrude(40).union(cq.Workplane("XY").box(50, 24, 5, centered=(True, True, False)))   # 3.5 mm wall
    s = s.cut(cq.Workplane("XY").circle(6.45).extrude(36).translate((0, 0, 5)))                    # 1/2 in dowel [E3]
    return s.faces("<Z").workplane().pushPoints([(-19, 0), (19, 0)]).hole(M2)


# ---------------- 10 colour ----------------
def led_ring():
    """8 star LEDs on r = 24 mm; mounts at the top of the 40 deg mast."""
    r = cq.Workplane("XY").circle(40).circle(10).extrude(4)
    r = r.faces(">Z").workplane().polarArray(24, 0, 360, 8).hole(M2)
    return r.union(cq.Workplane("XY").box(16, 60, 4, centered=(True, False, False)).translate((0, -95, 0)))


def led_mast():
    """Bolts to the light arm; tilts the LED ring 40 deg up so photometric-stereo lights are non-coplanar."""
    plate = cq.Workplane("XY").box(30, 30, 5, centered=(True, True, False)).faces(">Z").workplane().rect(20, 20, forConstruction=True).vertices().hole(M2)
    arm = cq.Workplane("XY").box(16, 6, 160, centered=(True, True, False)).rotate((0, 0, 0), (1, 0, 0), -50).translate((0, 0, 5))
    return plate.union(arm)


def spectral_tube():
    """AS7341 breakout (25.4 x 17.8 mm, check holes) behind a 40 mm tube with a 3 mm aperture: ~4 deg field,
    ~25 mm spot at 350 mm. Clamps to the camera pillar (FRM-09h) above the camera plate (M2 x 16 into its z 181 pilot)."""
    base = cq.Workplane("XY").box(30, 24, 3, centered=(True, True, False))
    base = base.faces(">Z").workplane().pushPoints([(-10.15, 0), (10.15, 0)]).hole(M2)
    tube = cq.Workplane("XZ").circle(7).circle(5).extrude(-40).translate((0, 12, 10))
    cap = cq.Workplane("XZ").circle(7).circle(1.5).extrude(-1.5).translate((0, 52, 10))
    wall = cq.Workplane("XY").box(30, 3, 20, centered=(True, False, False)).translate((0, 9, 0))
    wall = wall.cut(cq.Workplane("XZ").circle(5).extrude(-5).translate((0, 8, 10)))
    clamp = cq.Workplane("XY").box(30, 26, 22, centered=(True, False, False)).translate((0, -38, 0))
    clamp = clamp.cut(cq.Workplane("XY").rect(BAR_FIT, BAR_FIT).extrude(22).translate((0, -25, 0)))
    clamp = clamp.cut(cq.Workplane("XZ").circle(M2 / 2).extrude(-40).translate((0, -45, 11)))
    return base.union(tube).union(cap).union(wall).union(clamp.translate((0, -0.0, 0)))


# ---------------- 11 scan ----------------
def riser(h: float):
    """Hollow riser: 3 mm tube, 6 mm top, 4 screw bosses (less ABS, same stiffness where it matters)."""
    r = cq.Workplane("XY").circle(25).extrude(h)
    if h > 10:
        r = r.cut(cq.Workplane("XY").circle(22).extrude(h - 6))
        r = r.union(cq.Workplane("XY").polarArray(15, 45, 360, 4).circle(5).extrude(h - 6))
    r = r.cut(cq.Workplane("XY").circle(20).extrude(2).translate((0, 0, h - 2)))                   # object nest
    return r.faces("<Z").workplane().polarArray(15, 45, 360, 4).cboreHole(M2, M2_HEAD, max(h - 6, 1))


SCAN_TILT = 15.0                  # scan camera looks 15 deg down (machine.yaml scan.camera_elevation_deg)


SCAN_CLAMP_OFF = 18.0             # the tilted plate's lower edge swings 6.5 mm back: post 18 mm behind the plate centre


def _scan_post():
    """Scan camera: lens front 650 mm from the zero point, looking SCAN_TILT down; the clamp channel is vertical and
    SCAN_CLAMP_OFF behind the plate-back centre, horizontally. Returns (post x, lens-front z)."""
    e = math.radians(SCAN_TILT)
    lx, lz = 650 * math.cos(e), 150 + 650 * math.sin(e)
    back_x = lx + CAM_LENS_Z * math.cos(e)                 # plate back centre, CAM_LENS_Z behind the lens front
    return back_x + SCAN_CLAMP_OFF, lz


SCAN_POST_X, SCAN_LENS_Z = _scan_post()
END_FOOT_X = round(SCAN_POST_X - 20 - 20 - 6)       # just inside the scan post socket (the post overhangs it by ~45 mm)


SCAN_CLAMP_Z = SCAN_LENS_Z + CAM_LENS_Z * math.sin(math.radians(SCAN_TILT))   # scan clamp screw height (z 325.9)
POST_Z0, POST_JOINT, POST_TOP = 36.0, 211.0, 386.0               # scan post: socket floor, coupler joint, top
OUT_JOINT = (OUTRIGGER_X[0] + OUTRIGGER_X[1]) / 2                # outrigger coupler joint, x = 465


def outrigger_bar(part: int):
    """Outrigger, two 250 mm bars along +x at y 0, z 6..26. Side pilots (world y) for the saddles, the camera pillar,
    the coupler, the end foot and the post socket."""
    x0 = OUTRIGGER_X[0] if part == 0 else OUT_JOINT
    x1 = OUT_JOINT if part == 0 else OUTRIGGER_X[1]
    st = list(SADDLES_X) + [CAM_POST_X, OUT_JOINT - COUPLER_HOLE, OUT_JOINT + COUPLER_HOLE, END_FOOT_X, SCAN_POST_X]
    return _bar(x1 - x0, side=[x - x0 for x in st if x0 < x < x1])


def scan_post_bar(part: int):
    """Scan-camera post, two 175 mm bars standing at x = 674.4 (z 36..211..386). Pilots along world x (socket,
    coupler) and world y (scan camera clamp)."""
    z0, z1 = (POST_Z0, POST_JOINT) if part == 0 else (POST_JOINT, POST_TOP)
    top = [z - z0 for z in (POST_Z0 + 14, POST_JOINT - COUPLER_HOLE, POST_JOINT + COUPLER_HOLE) if z0 < z < z1]
    side = [SCAN_CLAMP_Z - z0] if z0 < SCAN_CLAMP_Z < z1 else []
    return _bar(z1 - z0, side=side, top=top)


def scan_camera_plate():
    """Second camera plate: the plate looks 15 deg down while its clamp stays vertical on the scan post (replaces the
    old wedge; same M2 x 8 screws, 6 mm standoffs). M2 x 16 into the scan post's pilot. Lens front 650 mm from the zero point, centre 168 mm above it."""
    return _camera_face().union(_post_clamp(SCAN_TILT, SCAN_CLAMP_OFF))


# ---------------- 15 standalone ----------------
def pi_mount():
    """Pi Zero 2 W, 58 x 23 mm hole pattern [H51]: push-fit pegs through its 2.75 mm holes (no screws)."""
    p = cq.Workplane("XY").box(75, 40, 3, centered=(True, True, False))
    for x in (-29, 29):
        for y in (-11.5, 11.5):
            p = p.union(cq.Workplane("XY").circle(3).extrude(8).translate((x, y, 0)))
            p = p.union(cq.Workplane("XY").circle(1.25).extrude(2.6).translate((x, y, 8)))
    return p


# ---------------- hub add-on: status screen (STA-09) ----------------
# Waveshare 2inch LCD Module [L30]: 58.0 x 35.0 mm. Its hole positions and thickness are only in a drawing image, so
# nothing here depends on them: the module lies in a 1.2 mm pocket and the bezel clamps its two short ends (4 mm each).
TFT = (58.0, 35.0)
TFT_POCKET = 1.2                  # less than any PCB, so the bezel always presses the board
TFT_WIN = (50.0, 39.0)            # bezel window: full height, 50 of the 58 mm length (active area 40.8 x 30.6)
SCREEN_TILT = 30.0                # face leans back 30 deg from vertical
SCREEN_FACE = (74.0, 50.0, 4.0)   # face width (along the module), height up the slope, thickness
SCREEN_C = 27.0                   # module centre, up the slope from the face's bottom edge
SCREEN_HOLES = [(sx * 33.2, sy * 18.0) for sx in (-1, 1) for sy in (-1, 1)]   # bezel screws, outside the module
SCREEN_BASE = (-30.0, 22.5)       # base x range: user side (-x) to the back
SCREEN_XY = (-190.0, 117.0)       # NW tile, outside the ring scale (r 175), 2 mm short of the controller tray; ~8 cm from the hub
SCREEN_PILOTS = [(x, sy * 26.0) for x in (-25.0, 12.0) for sy in (-1, 1)]   # deck pilots, local


def _screen_face() -> cq.Workplane:
    """The face standing upright, front (pocket side) at x = 0 facing -x, bottom edge at z = 0."""
    fw, fh, ft = SCREEN_FACE
    f = cq.Workplane("XY").box(ft, fw, fh, centered=(False, True, False))
    f = f.cut(cq.Workplane("XY").box(TFT_POCKET, TFT[0] + CLEAR, TFT[1] + CLEAR, centered=(False, True, True)).translate((0, 0, SCREEN_C)))
    f = f.cut(cq.Workplane("XY").box(ft, TFT[0] - 8, TFT[1] - 6, centered=(False, True, True)).translate((0, 0, SCREEN_C)))   # back parts, cable
    for u, v in SCREEN_HOLES:
        f = f.union(cq.Workplane("YZ").circle(3).extrude(4).translate((ft, u, SCREEN_C + v)))                         # 8 mm of thread
        f = f.cut(cq.Workplane("YZ").circle(M2_TAP / 2).extrude(ft + 4).translate((0, u, SCREEN_C + v)))
    return f


def screen_stand():
    """Status screen stand: base on 4 deck pilots (M2 x 12), face at 30 deg from vertical toward -x (the laptop side),
    two side cheeks. The 8-pin cable leaves through the face window and out of the open back toward the hub."""
    fw = SCREEN_FACE[0]
    x0, x1 = SCREEN_BASE
    s = cq.Workplane("XY").box(x1 - x0, fw, 3, centered=(False, True, False)).translate((x0, 0, 0))
    s = s.faces(">Z").workplane().pushPoints([(x, y) for x, y in SCREEN_PILOTS]).cboreHole(M2, M2_HEAD, 1.5)
    a = math.radians(SCREEN_TILT)
    fx = -18.0
    s = s.union(_screen_face().rotate((0, 0, 0), (0, 1, 0), SCREEN_TILT).translate((fx, 0, 3)))
    top = (fx + SCREEN_FACE[1] * math.sin(a), 3 + SCREEN_FACE[1] * math.cos(a))
    for sy in (-1, 1):
        cheek = cq.Workplane("XZ").polyline([(fx, 3), top, (x1, 3)]).close().extrude(-3)
        s = s.union(cheek.translate((0, sy * (fw / 2 - 1.5) - 1.5, 0)))
    return s


def screen_bezel():
    """Bezel: presses the module's short ends into the face pocket, 4 x M2 x 8 into the face pilots."""
    fw, fh = SCREEN_FACE[0], 46.0
    b = cq.Workplane("XY").box(fw, fh, 2, centered=(True, True, False))
    b = b.cut(cq.Workplane("XY").rect(*TFT_WIN).extrude(2))
    return b.faces(">Z").workplane().pushPoints(SCREEN_HOLES).hole(M2)


PLACE = {   # part: deck pilot positions (x, y), mm from the zero point; deck_tile() puts a boss under each
    "table post": [_polar(22.2, a) for a in (45, 135, 225, 315)],
    "table motor bracket": [(-TABLE_BELT_C, s * 34.3) for s in (-1, 1)],
    "M4 motor mount": [(RING_MOTOR_R + (RING_BASE[0] + RING_BASE[1]) / 2, s * 38) for s in (-1, 1)],
    "bar saddles": [(x + dx, dy) for x in SADDLES_X for dx, dy in SADDLE_HOLES],
    "power plate": [(POWER_XY[0] + dx, POWER_XY[1] + dy) for dx in (-20, 20) for dy in (-20, 20)],
    "controller tray": [(TRAY_XY[0] + x, TRAY_XY[1] + y) for x, y in TRAY_HOLES],
    "ring scale": [_polar(RING_SCREW_R, 20 + 80 * k + a) for k in range(4) for a in RING_SCREW_A],
    "table endstop riser": ENDSTOP_FEET,
    "screen stand": [(SCREEN_XY[0] + x, SCREEN_XY[1] + y) for x, y in SCREEN_PILOTS],
}
_DECK_EDGES = [-DECK_HALF + DECK_TILE * k for k in range(DECK_N + 1)]


def _check_place():
    for name, pts in PLACE.items():
        for x, y in pts:
            d = min(abs(v - e) for v in (x, y) for e in _DECK_EDGES)
            assert d >= 5.5 and max(abs(x), abs(y)) <= DECK_HALF - 5.5, f"{name} pilot ({x:.1f}, {y:.1f}) is {d:.1f} mm from a seam"


_check_place()


# ---------------- registry ----------------
PARTS = {   # id: (stage folder, file stem, function, what)
    "PLAN-01": ("00-plan", "tolerance_coupon", tolerance_coupon, "Fit test: M2 self-tap holes + 608 pockets"),
    "PWR-18": ("01-power", "power_plate", power_plate, "Power plate (jack + e-stop box)"),
    "CTL-10a": ("02-controller", "button_panel", button_panel, "Keypad panel + OLED window"),
    "CTL-10b": ("02-controller", "controller_tray", controller_tray, "Controller tray (SKR Pico + ESP32-S3 + opto + LED driver)"),
    "FRM-01a": ("03-frame", "deck_tile_SW", lambda: deck_tile_k(0), "Deck tile SW (x -300..-100, y -300..-100)"),
    "FRM-01b": ("03-frame", "deck_tile_S", lambda: deck_tile_k(1), "Deck tile S (x -100..100, y -300..-100)"),
    "FRM-01c": ("03-frame", "deck_tile_SE", lambda: deck_tile_k(2), "Deck tile SE: power plate (x 100..300, y -300..-100)"),
    "FRM-01d": ("03-frame", "deck_tile_W", lambda: deck_tile_k(3), "Deck tile W (x -300..-100, y -100..100)"),
    "FRM-01e": ("03-frame", "deck_tile_C", lambda: deck_tile_k(4), "Deck tile C: table post + motor (x -100..100, y -100..100)"),
    "FRM-01f": ("03-frame", "deck_tile_E", lambda: deck_tile_k(5), "Deck tile E: M4 motor + saddles (x 100..300, y -100..100)"),
    "FRM-01g": ("03-frame", "deck_tile_NW", lambda: deck_tile_k(6), "Deck tile NW: controller tray (x -300..-100, y 100..300)"),
    "FRM-01h": ("03-frame", "deck_tile_N", lambda: deck_tile_k(7), "Deck tile N (x -100..100, y 100..300)"),
    "FRM-01i": ("03-frame", "deck_tile_NE", lambda: deck_tile_k(8), "Deck tile NE (x 100..300, y 100..300)"),
    "FRM-02a": ("03-frame", "outrigger_bar_1", lambda: outrigger_bar(0), "Outrigger bar 1, 250 mm (x 215..465)"),
    "FRM-02b": ("03-frame", "outrigger_bar_2", lambda: outrigger_bar(1), "Outrigger bar 2, 250 mm (x 465..715)"),
    "FRM-02c": ("03-frame", "scan_post_bar_1", lambda: scan_post_bar(0), "Scan post bar 1, 175 mm (z 36..211)"),
    "FRM-02d": ("03-frame", "scan_post_bar_2", lambda: scan_post_bar(1), "Scan post bar 2, 175 mm (z 211..386)"),
    "FRM-09c": ("03-frame", "protractor_segment", protractor_segment, "Ring scale + lazy-Susan clamp, 80 deg (print 4: 20-340 deg)"),
    "FRM-09d": ("03-frame", "bar_saddle", bar_saddle, "Outrigger saddle (print 2)"),
    "FRM-09e": ("03-frame", "post_socket", post_socket, "Scan-post socket on the outrigger"),
    "FRM-09h": ("03-frame", "camera_pillar", camera_pillar, "Measuring-camera pillar on the outrigger"),
    "FRM-09f": ("03-frame", "end_foot", end_foot, "Outrigger end foot"),
    "FRM-09i": ("03-frame", "bar_coupler", bar_coupler, "Bar coupler: outrigger, scan post (print 2)"),
    "LAR-08a": ("04-light-arm", "rim_segment", rim_segment, "Belt rim segment (print 7)"),
    "LAR-08b": ("04-light-arm", "ring_motor_mount", ring_motor_mount, "M4 motor mount at 0 deg, pinion meshes the rim"),
    "LAR-08c": ("04-light-arm", "arm_segment", arm_segment, "Arm segment: rim segment + upright socket"),
    "LAR-08e": ("04-light-arm", "cross_clamp", cross_clamp, "Cross clamp: upright to horizontal arm"),
    "LAR-08f": ("04-light-arm", "upright_bar", upright_bar, "Light-arm upright bar, 200 mm"),
    "LAR-08g": ("04-light-arm", "arm_bar", arm_bar, "Horizontal light-arm bar, 200 mm"),
    "TBL-07a": ("05-table", "table_drum", table_drum, "Table drum: 100T teeth, 608 seats, OG-40 top"),
    "TBL-07b": ("05-table", "home_flag", home_flag, "Home flag (print 2: tilt, spin)"),
    "TBL-07c": ("05-table", "table_motor_bracket", table_motor_bracket, "Table motor bracket (shaft up, slotted)"),
    "TBL-07d": ("05-table", "table_post", table_post, "Table post: fixed M8 x 75 axle (hex-locked head)"),
    "TBL-07f": ("05-table", "spacers", spacers, "Spacers + shims, table and tilt (one print)"),
    "TBL-07g": ("05-table", "endstop_riser", endstop_riser, "Table endstop riser (3 deck pilots, +X)"),
    "TBL-07h": ("05-table", "table_flag", table_flag, "Table home flag (fin at r 60)"),
    "CAM-03a": ("06-camera-light", "aperture_stop_f8", aperture_stop, "f/8 aperture stop"),
    "CAM-03b": ("06-camera-light", "camera_plate", camera_plate, "Camera plate + post clamp"),
    "LSR-05a": ("06-camera-light", "lamp_tube", lamp_tube, "Lamp body + tube, bar clamp, polarizer slot"),
    "LSR-05b": ("06-camera-light", "lamp_cap", lamp_cap, "Lamp back cap"),
    "CAL-06a": ("07-calibrate", "ptfe_holder", ptfe_holder, "PTFE holder"),
    "CAL-06b": ("07-calibrate", "mirror_holder", mirror_holder, "Mirror holder"),
    "CAL-06c": ("07-calibrate", "ball_holder", ball_holder, "Chrome-ball holder"),
    "ENC-04a": ("07-calibrate", "dowel_socket", dowel_socket, "Dowel socket (print 4)"),
    "TLT-07a": ("08-tilt", "tilt_yoke", tilt_yoke, "Tilt yoke: 608 seats, motor slots above the axis"),
    "TLT-07b": ("08-tilt", "pulley_100T", lambda: gt2_pulley(100), "GT2 100T pulley (5:1) on the stub axle"),
    "TLT-07c": ("08-tilt", "tilt_cradle", tilt_cradle, "Tilt cradle: stub-axle nut traps, spin motor floor"),
    "SPN-07a": ("09-spin", "spin_platter", spin_platter, "Spin platter: clamps the motor D-shaft (direct drive)"),
    "MSK-06a": ("10-color", "led_ring", led_ring, "LED ring (8 bands)"),
    "MSK-06b": ("10-color", "led_mast", led_mast, "40 deg LED mast"),
    "SPC-03a": ("10-color", "spectral_tube", spectral_tube, "Spectral sensor tube + post clamp"),
    "SCN-03a": ("11-scan-capture", "riser_20", lambda: riser(20), "Riser 20 mm"),
    "SCN-03b": ("11-scan-capture", "riser_40", lambda: riser(40), "Riser 40 mm"),
    "SCN-03c": ("11-scan-capture", "riser_60", lambda: riser(60), "Riser 60 mm"),
    "SCN-03d": ("11-scan-capture", "scan_camera_plate_15", scan_camera_plate, "Scan camera plate, looks 15 deg down"),
    "STA-07a": ("15-standalone", "pi_zero_mount", pi_mount, "Pi Zero 2 W mount"),
    "STA-10a": ("15-standalone", "screen_stand", screen_stand, "Status screen stand (4 deck pilots)"),
    "STA-10b": ("15-standalone", "screen_bezel", screen_bezel, "Status screen bezel"),
}


def build(only: str | None = None) -> list[Path]:
    out = []
    for pid, (stage, stem, fn, _) in PARTS.items():
        if only and pid != only:
            continue
        d = ROOT / "phases" / stage / "3d"
        d.mkdir(parents=True, exist_ok=True)
        shape = fn()
        for ext in ("step", "stl"):
            path = d / f"{pid}_{stem}.{ext}"
            if ext == "stl":
                cq.exporters.export(shape, str(path), tolerance=0.05, angularTolerance=0.2)
            else:
                cq.exporters.export(shape, str(path))
                stepio.stabilise(path)
            out.append(path)
        bb = shape.val().BoundingBox()
        print(f"{pid:8} {stage:16} {stem:22} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} mm")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    a = ap.parse_args()
    build(a.only)
    sys.exit(0)
