#!/usr/bin/env python3
"""Placeholder ("dummy") 3D models for every BOUGHT part -> cad/bought/<ID>_<name>.step.

Each dummy is an envelope model from the datasheet / listing dimensions in the table below: right outside size,
mounting holes and shaft/connector positions where they matter for fit, no internal detail. Import into Onshape,
design around it, then swap in the vendor model from cad/README.md when you have it (same origin conventions are
NOT guaranteed: re-mate after swapping).

    python tools/cad/bought.py            all
    python tools/cad/bought.py --only LAR-02

Origins: boards and plates lie flat on z = 0; motors have their mounting face at z = 0, body below, shaft up (+z);
cylinders stand on z = 0 along +z. SPDX-License-Identifier: CERN-OHL-S-2.0
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
OUT = ROOT / "cad" / "bought"
W = cq.Workplane


def box(x, y, z, cx=True, cy=True):
    return W("XY").box(x, y, z, centered=(cx, cy, False))


def cyl(d, h):
    return W("XY").circle(d / 2).extrude(h)


def pcb(x, y, t=1.6, holes=(), hole_d=3.2):
    b = box(x, y, t)
    for hx, hy in holes:
        b = b.cut(W("XY").circle(hole_d / 2).extrude(t).translate((hx, hy, 0)))
    return b


def header(n, rows=1, pitch=2.54, h=8.5):
    """Male pin header, base 2.5 mm plastic + 0.64 mm square pins standing up."""
    b = box(n * pitch, rows * pitch, 2.5)
    for i in range(n):
        for j in range(rows):
            b = b.union(box(0.64, 0.64, h).translate(((i - (n - 1) / 2) * pitch, (j - (rows - 1) / 2) * pitch, 0)))
    return b


def nema17(body=48.0, shaft=24.0):
    """Mounting face at z = 0, body below, 22 mm boss + 5 mm D-shaft up, 4 x M3 on 31 mm."""
    b = box(42.3, 42.3, body).translate((0, 0, -body)).edges("|Z").chamfer(4)
    for x in (-15.5, 15.5):
        for y in (-15.5, 15.5):
            b = b.cut(W("XY").circle(1.5).extrude(4.5).translate((x, y, -4.5)))
    b = b.union(cyl(22, 2)).union(cyl(5, shaft))
    return b.cut(box(5, 5, shaft - 1.5, cx=True, cy=False).translate((0, 2.0, 2)))           # D flat, 4.5 mm across


def gt2_20t(bore=5.0):
    """Aluminium GT2 20T: flanges 16 mm, teeth 12.2 mm pitch dia x 7 mm, hub 16 x 7 mm with 2 set screws."""
    p = cyl(16, 1).union(cyl(12.2, 7).translate((0, 0, 1))).union(cyl(16, 1).translate((0, 0, 8))).union(cyl(16, 7).translate((0, 0, 9)))
    return p.cut(cyl(bore, 16)).cut(W("YZ").circle(1.5).extrude(10).translate((0, 0, 12.5)))


def belt_loop(r1, r2, c, w=6.0, t=1.4):
    """Closed GT2 belt around two pulleys (pitch radii r1, r2, centre distance c), flat ribbon w x t."""
    def hull(rr):
        return W("XY").circle(rr + r1 - r1).extrude(w)
    outer = W("XY").circle(r1 + t).extrude(w).union(W("XY").circle(r2 + t).extrude(w).translate((c, 0, 0)))
    outer = outer.union(W("XY").polyline([(0, r1 + t), (c, r2 + t), (c, -r2 - t), (0, -r1 - t)]).close().extrude(w))
    inner = W("XY").circle(r1).extrude(w).union(W("XY").circle(r2).extrude(w).translate((c, 0, 0)))
    inner = inner.union(W("XY").polyline([(0, r1), (c, r2), (c, -r2), (0, -r1)]).close().extrude(w))
    return outer.cut(inner)


def bolt(d, length, head_d, head_h, hex_head=False, nut=None):
    head = W("XY").polygon(6, head_d / math.cos(math.radians(30))).extrude(head_h) if hex_head else cyl(head_d, head_h)
    b = head.union(cyl(d, length).translate((0, 0, head_h)))
    if nut:
        b = b.union(W("XY").polygon(6, nut[0] / math.cos(math.radians(30))).circle(d / 2).extrude(nut[1]).translate((0, 0, head_h + length + 3)))
    return b


def cable(length=300.0, d=4.0, end_a=(10, 8, 20), end_b=(10, 8, 20)):
    c = box(*end_a).union(cyl(d, length).translate((0, 0, end_a[2]))).union(box(*end_b).translate((0, 0, end_a[2] + length)))
    return c


def sheet(x, y, t):
    return box(x, y, t)


def tcst2103_module():
    """Endstop module: 33 x 11 mm PCB, TCST2103 (24.5 x 6.3 x 10.8, 3.1 mm slot) on top, 3-pin header at one end."""
    b = pcb(33, 11, holes=[(-12.5, 0), (12.5, 0)], hole_d=3.2)
    s = box(24.5, 6.3, 10.8).translate((0, 0, 1.6)).cut(box(3.1, 7, 8).translate((0, 0, 1.6 + 2.8)))
    return b.union(s).union(header(3).rotate((0, 0, 0), (0, 0, 1), 90).translate((15, 0, 1.6)))


def heatsink(x=40, y=40, h=11.6, pins=7):
    """Wakefield 910-40-2-12-2-B-0 envelope: 40 x 40 x 11.6 mm pin fin [L28]; 2 mm base and the pin grid assumed."""
    b = box(x, y, 2)
    step = (x - 5) / (pins - 1)
    for i in range(pins):
        for j in range(pins):
            b = b.union(box(2.2, 2.2, h).translate((-x / 2 + 2.5 + i * step, -y / 2 + 2.5 + j * step, 0)))
    return b


def lazy_susan():
    """12 in round lazy Susan: two steel plates, OD 305, ID ~160, 8 mm total; 4 holes per plate (positions vary)."""
    b = W("XY").circle(152.5).circle(80).extrude(3).union(W("XY").circle(150).circle(82).extrude(3).translate((0, 0, 5)))
    b = b.union(W("XY").circle(140).circle(130).extrude(2).translate((0, 0, 3)))                         # ball race
    for a in (45, 135, 225, 315):
        b = b.cut(W("XY").circle(2.5).extrude(8).translate((130 * math.cos(math.radians(a)), 130 * math.sin(math.radians(a)), 0)))
    return b


def camera_b0433():
    """Arducam B0433: 38 x 38 mm board, 4 x M2 holes on 34 mm, M12 lens holder 14 x 14 x 11, USB-C at the back."""
    b = pcb(38, 38, holes=[(sx * 17, sy * 17) for sx in (-1, 1) for sy in (-1, 1)], hole_d=2.2)
    b = b.union(box(17, 17, 11).translate((0, 0, 1.6)).cut(cyl(12, 13).translate((0, 0, 1.6))))
    return b.union(box(9, 7.5, 3.3).translate((0, -15, -3.3)))


def lens_m12():
    return cyl(12, 13).union(cyl(14, 4).translate((0, 0, 13)))


def ldd_module():
    """MEAN WELL NLDD-H: 31.8 x 20.3 x 12.2 mm, pins down (2.54 mm grid)."""
    b = box(31.8, 20.3, 12.2)
    for x in (-11.43, -6.35, 6.35, 11.43):
        b = b.union(box(0.6, 0.6, 4).translate((x, -7.6, -4)))
    for x in (-11.43, 11.43):
        b = b.union(box(0.6, 0.6, 4).translate((x, 7.6, -4)))
    return b


def ldd_hw():
    """MEAN WELL NLDD-350HW: 32.1 x 20.5 x 12.5 mm, five 22 AWG leads 100 mm out of one short end [L27]."""
    b = box(32.1, 20.5, 12.5)
    for k in range(5):
        b = b.union(W("YZ").circle(0.8).extrude(100).translate((16.05, -6 + 3 * k, 6)))
    return b


def cob_clu701():
    """Citizen CLU701: 13.5 x 13.5 x 1.4 mm board [L25]; the emitting disc (no number in the datasheet) drawn 6 mm."""
    return box(13.5, 13.5, 1.4).union(cyl(6.0, 0.2).translate((0, 0, 1.4)))


def tft_2in():
    """Waveshare 2inch LCD Module envelope [L30]: 58 x 35 mm; 4 mm thick and the 1.6 mm board edge are estimates."""
    return box(58, 35, 1.6).union(box(46, 35, 2.4).translate((0, 0, 1.6)))


def cob_holder():
    """TE LUMAWISE Z35 2213678-5 (envelope): OD 35, 3.6 high, seat for a 13.5 mm board, window over the LES,
    2 x M3 holes (unused here: the lamp body clamps it) [L23]."""
    b = cyl(35, 3.6).cut(cyl(16, 3.6)).cut(box(13.8, 13.8, 1.7))
    for x in (-14, 14):
        b = b.cut(W("XY").circle(1.7).extrude(3.6).translate((x, 0, 0)))
    return b


def keypad_1x4():
    return box(69, 20, 0.8).union(box(10, 85, 0.3, cy=False).translate((0, -95, 0))).union(box(12.7, 5, 2.5).translate((0, -97, 0)))


WAGO_221 = {2: (13.1, 18.7, 8.3), 3: (18.7, 18.6, 8.3), 5: (30.0, 18.8, 8.6)}   # 221-412 / 413 / 415: W x D x H [P63]


def wago(n):
    """WAGO 221-41n lever connector, levers closed: x = depth (wires go in at -x), y = width, z = height (levers on top)."""
    w, d, h = WAGO_221[n]
    body = box(d, w, h - 2.0)
    for k in range(n):                                                         # one lever per wire, 1 mm apart
        body = body.union(box(d - 4.6, w / n - 1.0, 2.0).translate((2.3, -w / 2 + (k + 0.5) * w / n, h - 2.0)))
    return body


def wago_inline():
    """WAGO 221-2401 inline connector: 35.5 mm long [P63], one wire in each end; section ESTIMATE 10 x 9 mm."""
    return box(35.5, 10, 7).union(box(14, 8, 2).translate((-9, 0, 7))).union(box(14, 8, 2).translate((9, 0, 7)))


def wago_assortment():
    """PWR-20 as bought [P62]: 3 each of 221-412, 221-413, 221-415 and 221-2401, laid out in rows."""
    out = None
    for row, make in enumerate((lambda: wago(2), lambda: wago(3), lambda: wago(5), wago_inline)):
        for k in range(3):
            p = make().translate((k * 40.0, row * 36.0, 0))
            out = p if out is None else out.union(p)
    return out


def ptfe():
    """White tile as used: three 50 mm squares of 3 mm PTFE, stacked (cut from a 100 x 100 mm sheet)."""
    return box(50.0, 50.0, 3 * 3.0)


def oled_ssd1306():
    return pcb(27.3, 27.8, holes=[(sx * 11.5, sy * 11.5) for sx in (-1, 1) for sy in (-1, 1)], hole_d=2.2).union(
        box(26.7, 19.3, 1.5).translate((0, -1.5, 1.6))).union(header(4).translate((0, 12.5, -2.5)))


def buck_lm2596_display():
    b = pcb(66, 36, holes=[(sx * 30, sy * 15) for sx in (-1, 1) for sy in (-1, 1)])
    b = b.union(box(25, 13, 8).translate((-5, 5, 1.6)))                                  # display
    return b.union(box(8, 15, 10).translate((-27, 0, 1.6))).union(box(8, 15, 10).translate((27, 0, 1.6)))   # screw terminals


def pi_zero_2wh():
    b = pcb(65, 30, holes=[(sx * 29, sy * 11.5) for sx in (-1, 1) for sy in (-1, 1)], hole_d=2.75)
    return b.union(header(20, 2).translate((0, 11.5, 1.6))).union(box(10, 10, 1.4).translate((0, -2, 1.6)))


def pico_h():
    b = pcb(51, 21, t=1.0, holes=[(sx * 23.5, sy * 5.7) for sx in (-1, 1) for sy in (-1, 1)], hole_d=2.1)
    for y in (-8.89, 8.89):
        b = b.union(header(20).translate((0, y, -2.5)).mirror("XY", (0, 0, -1.25)))
    return b.union(box(8, 6, 3).translate((-23, 0, 1.0)))


def skr_pico():
    """BTT SKR Pico V1.0 envelope [C12]: 85 x 56 mm board, 4 x 2.7 mm holes on 58 x 49 mm (3.5 mm from the left/bottom
    edges), connectors up to 10 mm tall, USB-C on the +X edge. The maker STEP is linked in the BOM."""
    b = pcb(85, 56, holes=[(-39.0, sy * 24.5) for sy in (-1, 1)] + [(19.0, sy * 24.5) for sy in (-1, 1)], hole_d=2.7)
    b = b.union(box(78, 50, 8.4).translate((0, 0, 1.6)))
    return b.union(box(7, 9, 3.2).translate((42.5 - 3.5, 56 / 2 - 2.89 - 6, 1.6)))


def esp32s3_devkitc():
    """ESP32-S3-DevKitC-1, drawn as it sits in the tray: upside down (module can down, header pins up).
    Espressif board 62.74 x 25.4 mm [P65] (clones run to ~69 x 26): 2 x 22 pins 22.86 mm apart, can 18 x 25.5 x 3.2
    at the -X end, USB-C at +X."""
    L, Wd = 62.74, 25.4
    b = pcb(L, Wd).translate((0, 0, 3.2))
    b = b.union(box(25.5, 18, 3.2).translate((-L / 2 + 13, 0, 0)))                     # module can (rests on the pedestal)
    for y in (-11.43, 11.43):
        b = b.union(box(55.9, 2.5, 2.5).translate((2, y, 4.8))).union(box(55.9, 0.64, 8.5).translate((2, y, 7.3)))   # 22 pins x 2.54
    return b


def e4_board():
    """FYSETC E4 envelope: 96 x 68 mm, 4 x 3.2 holes on 83.6 x 60.6, 22 mm tall components (use the vendor STEP!)."""
    b = pcb(96, 68, holes=[(sx * 41.8, sy * 30.3) for sx in (-1, 1) for sy in (-1, 1)])
    return b.union(box(80, 50, 20).translate((0, 0, 1.6)))


def estop_station():
    """BAOMAIN e-stop station [P60]: 2.8 x 2.8 x 3.4 in overall (71 x 71 x 86 mm, listing copy [P64]); box height and
    head size ESTIMATE (62 mm box, 30 mm collar, 40 mm mushroom)."""
    head = W("XY").circle(20).extrude(14).faces(">Z").fillet(6).translate((0, 0, 72)).union(cyl(30, 10).translate((0, 0, 62)))
    return box(71, 71, 62).union(head)


def dc_jack_screw():
    """Female 5.5 x 2.1 mm DC jack to screw terminals (comes with PWR-30 [P59]): ESTIMATE 32 x 14 x 13 mm, socket toward +X."""
    j = box(32, 14, 13)
    return j.union(cyl(8, 4).rotate((0, 0, 0), (0, 1, 0), 90).translate((16, 0, 6.5)))


def limit_switch_sealed():
    """Joinfworld sealed roller-lever microswitch [P61]: ESTIMATE body 20 x 6.4 x 10 mm, lever + roller to 22 mm, 3 wires out."""
    b = box(20, 6.4, 10).union(box(18, 4, 0.8).translate((-1, 0, 10)).rotate((0, 0, 10), (0, 1, 10), -12))
    b = b.union(cyl(5, 4).rotate((0, 0, 0), (1, 0, 0), 90).translate((8, 2, 14)))
    return b.union(cyl(4, 40).rotate((0, 0, 0), (0, 1, 0), -90).translate((-10, 0, 5)))


def fan40():
    return box(40, 40, 10).cut(cyl(37, 10)).union(cyl(20, 10))


def jumper_wire():
    return box(2.54, 2.54, 14).union(cyl(1.4, 150).translate((0, 0, 14))).union(box(2.54, 2.54, 14).translate((0, 0, 164)))


def star_led():
    return W("XY").polygon(6, 20).extrude(1.6).union(W("XY").sphere(2.8).translate((0, 0, 1.6)).intersect(box(6, 6, 3).translate((0, 0, 1.6))))


B_PARTS = {   # id: (file stem, builder, source of the dimensions)
    "PWR-30": ("dc_jack_screw_terminal", dc_jack_screw, "Screw-terminal DC jack with the ALITOVE adapter [P59]: ESTIMATE 32 x 14 x 13 mm (none published)"),
    "PWR-28": ("estop_station_1no1nc", estop_station, "BAOMAIN e-stop station [P60]: 71 x 71 x 86 mm overall (listing copy [P64]); box/head split ESTIMATE"),
    "PWR-10": ("pc817_opto_module_24v", lambda: pcb(66, 16.5).union(box(10, 16.5, 10.4).translate((-28, 0, 1.6))).union(box(10, 16.5, 10.4).translate((28, 0, 1.6))),
               "NOYITO PC817 1-channel module: 66 x 16.5 x 12 mm (maker manual); screw terminals both ends"),
    "PWR-15": ("wire_18awg_pair", lambda: box(4, 2, 1000), "18 AWG silicone pair, 1 m"),
    "PWR-20": ("wago_221_assortment_12", wago_assortment, "WAGO 221 12-piece [P62]: 221-412 13.1 x 18.7 x 8.3, 221-413 18.7 x 18.6 x 8.3, 221-415 30 x 18.8 x 8.6 mm, 221-2401 35.5 mm long [P63]"),
    "CTL-01": ("btt_skr_pico_envelope", skr_pico, "BTT SKR Pico V1.0 maker STEP [C12]: 85 x 56 mm, holes 58 x 49"),
    "CTL-02": ("esp32s3_devkitc1", esp32s3_devkitc, "ESP32-S3-DevKitC-1: 62.74 x 25.4 mm (Espressif board [P65]; clones to ~69 x 26: measure)"),
    "CTL-03": ("usb_cable_e4", lambda: cable(1000, 3.5, (12, 7, 20), (9, 5, 15)), "USB cable envelope"),
    "CTL-05": ("membrane_keypad_1x4", keypad_1x4, "Adafruit 1332: 69 x 20 x 0.8 mm, 85 mm tail [C9]"),
    "CTL-06": ("jst_xh_lead_3pin", lambda: box(7.5, 5.75, 9.8).union(cyl(1.3, 500).translate((0, 0, 9.8))).union(box(7.5, 5.75, 9.8).translate((0, 0, 509.8))),
               "JST XH 3-pin housing 7.5 x 5.75 x 9.8 mm, 500 mm lead"),
    "CTL-07": ("jumper_wire_mf", jumper_wire, "Dupont jumper 2.54 mm, 150 mm"),
    "CTL-08": ("fan_40mm", fan40, "40 x 40 x 10 mm fan"),
    "CTL-11": ("stepper_cable_ph_xh", lambda: box(12.5, 4.5, 6).union(cyl(3, 1000).translate((0, 0, 6))).union(box(10, 5.75, 9.8).translate((0, 0, 1006))),
               "PH2.0 6-pin housing / XH 4-pin housing, 1 m"),
    "FRM-06": ("screws_m2_samples", lambda: bolt(2, 8, 3.8, 2).union(bolt(2, 12, 3.8, 2).translate((8, 0, 0))).union(bolt(2, 16, 3.8, 2).translate((16, 0, 0))),
               "ISO 4762 socket head M2 x 8 / 12 / 16 (Onshape Standard Content has exact ones)"),
    "FRM-07": ("screw_m3x8", lambda: bolt(3, 8, 5.5, 3), "ISO 4762 socket head M3 x 8 (NEMA 17 faces)"),
    "FRM-08": ("bearing_608_2rs", lambda: cyl(22, 7).cut(cyl(8, 7)), "608-2RS: 8 x 22 x 7 mm"),
    "LAR-01": ("lazy_susan_12in", lazy_susan, "12 in round, ID ~160 mm (Bearing King listing); measure holes on arrival"),
    "LAR-02": ("nema17_17hs4401", lambda: nema17(38, 24), "SIMAX3D 17HS4401 listing [P58]: 42 x 42 x 38 mm, 5 mm D-shaft (24 mm assumed: measure)"),
    "LAR-03": ("gt2_belt_open_1m", lambda: box(6, 1.4, 1000), "GT2 6 mm open belt, 1 m"),
    "LAR-04": ("gt2_pulley_20t_5mm", gt2_20t, "GT2 20T 5 mm bore, 16 mm flanges [P42]"),
    "LAR-05": ("tcst2103_endstop_module", tcst2103_module, "TCST2103 module: 33 x 11 mm PCB, 3.1 mm slot [P43]"),
    "LAR-06": ("limit_switch_sealed_prewired", limit_switch_sealed, "Joinfworld sealed roller-lever switch [P61]: ESTIMATE 20 x 6.4 x 10 mm body (none published)"),
    "TBL-02": ("gt2_belt_232_loop", lambda: belt_loop(6.37, 31.83, 49.4), "GT2 232 mm loop on 20T + 100T at 49.4 mm"),
    "TBL-05": ("bolt_m8x75_nut", lambda: bolt(8, 75, 13, 5.3, True, (13, 6.5)), "DIN 931 M8 x 75 + DIN 934 nut"),
    "CAM-01": ("arducam_b0433_imx477_usb", camera_b0433, "Arducam B0433 datasheet drawing: 38 x 38, holes 34 mm [K3]"),
    "CAM-02": ("m12_lens_16mm", lens_m12, "M12 x 0.5 lens, ~14 mm flange"),
    "LSR-01": ("citizen_clu701_cob", cob_clu701, "Citizen CLU701-0303C4: 13.5 x 13.5 x 1.4 mm [L25]"),
    "LSR-02": ("meanwell_nldd_350hw", ldd_hw, "MEAN WELL NLDD-350HW: 32.1 x 20.5 x 12.5 mm, 100 mm leads [L27]"),
    "LSR-03": ("wakefield_910_40_2_12_2_b0", heatsink, "Wakefield 910-40-2-12-2-B-0: 40 x 40 x 11.6 mm pin fin [L28]"),
    "LSR-04": ("thermal_pad_40x40", lambda: box(40, 40, 0.5), "Thermal adhesive pad"),
    "LSR-06": ("te_lumawise_z35_2213678_5", cob_holder, "TE Z35 envelope: OD 35 x 3.6 mm; vendor STEP recommended [L23]"),
    "ENC-01": ("blackout_fabric_2yd", lambda: box(1371, 1829, 0.5), "54 in x 2 yd"),
    "ENC-02": ("felt_9x12in", lambda: box(229, 305, 1), "9 x 12 in felt"),
    "ENC-03": ("dowel_half_in_36in", lambda: cyl(12.7, 914.4), "1/2 in x 36 in dowel"),
    "ENC-05": ("flock_sheet", lambda: box(445, 381, 1), "17.5 x 15 in flock sheet"),
    "CAL-01": ("ptfe_tile_50mm_3x3mm", ptfe, "3 x 50 mm squares of 3 mm PTFE, stacked"),
    "CAL-02": ("mirror_tile_50mm", lambda: box(50, 50, 3), "~50 mm mirror tile"),
    "CAL-03": ("chrome_ball_1in", lambda: W("XY").sphere(12.7).translate((0, 0, 12.7)), "1 in G25 ball"),
    "CAL-04": ("charuco_glass_4x6in", lambda: box(152.4, 101.6, 2.2), "4 x 6 in picture-frame glass + print"),
    "CAL-05": ("colorchecker_mini", lambda: box(63.5, 108, 3), "ColorChecker Mini envelope"),
    "CAL-07": ("grey_card_8x10in", lambda: box(203, 254, 1), "8 x 10 in card"),
    "TLT-05": ("bolt_m8x35_nut", lambda: bolt(8, 35, 13, 5.3, True, (13, 6.5)), "DIN 931 M8 x 35 + nut"),
    "TLT-02": ("gt2_belt_280_loop", lambda: belt_loop(6.37, 31.83, 75.6), "GT2 280 mm loop on 20T + 100T at 75.6 mm"),
    "SPN-01": ("nema17_17hs08_1004s_pancake", lambda: nema17(21.5, 20), "StepperOnline 17HS08-1004S: 42.3 x 42.3 x 21.5, shaft 20 [P48]"),
    "MSK-01": ("star_led_20mm", star_led, "20 mm hex star LED"),
    "MSK-03": ("mosfet_module_4ch", lambda: pcb(60, 45).union(box(8, 40, 10).translate((-26, 0, 1.6))).union(box(8, 40, 10).translate((26, 0, 1.6))),
               "4-channel MOSFET switch module (envelope ~60 x 45 x 12 mm); measure on arrival"),
    "MSK-05": ("polarizer_film_100mm", lambda: box(100, 100, 0.3), "10 x 10 cm film"),
    "SPC-02": ("jst_sh_cable", lambda: box(5, 4, 3).union(cyl(2, 150).translate((0, 0, 3))), "JST-SH 4-pin, 150 mm"),
    "SCN-01": ("mounting_putty_blob", lambda: W("XY").sphere(15).translate((0, 0, 10)).intersect(box(40, 40, 20)), "Putty blob"),
    "SCN-02": ("charuco_mat_print", lambda: box(279.4, 215.9, 0.2), "Letter print"),
    "STA-01": ("pi_zero_2wh", pi_zero_2wh, "Raspberry Pi Zero 2 W drawing [H51]: 65 x 30, holes 58 x 23"),
    "STA-02": ("microsd_card", lambda: box(15, 11, 1), "microSD"),
    "STA-03": ("buck_lm2596_display", buck_lm2596_display, "LM2596 adjustable buck (envelope ~66 x 36 x 20, the size with a display)"),
    "STA-04": ("otg_adapter", lambda: box(20, 14, 8).union(box(7, 2.5, 6).translate((0, 0, -6))), "Micro-USB OTG adapter"),
    "STA-05": ("ssd1306_oled_096in", oled_ssd1306, "0.96 in SSD1306 I2C module: 27.3 x 27.8 mm"),
    "STA-06": ("jumper_wire_ff", jumper_wire, "Dupont jumper 2.54 mm"),
    "STA-09": ("waveshare_2in_lcd", tft_2in, "Waveshare 2inch LCD Module: 58 x 35 mm [L30]; thickness estimated"),
    "MSK-02": ("meanwell_nldd_350h", ldd_module, "MEAN WELL NLDD-H spec: 31.8 x 20.3 x 12.2 mm [L6]"),
    "STA-08": ("usb_cable_micro_b", lambda: cable(1000, 3.5, (12, 7, 20), (8, 6, 15)), "USB-A to micro-B cable"),
}
ALIASES = {   # same physical part as another ID: same model
    "TBL-01": "LAR-02", "TLT-01": "LAR-02", "TBL-03": "LAR-04", "TLT-03": "LAR-04", "TBL-04": "LAR-05", "TLT-04": "LAR-05",
    "SPN-04": "LAR-05", "CTL-04": "STA-08", "MSK-04": "LSR-03", "CAM-04": "CAM-01", "CAM-05": "CAM-02",
    "TBL-06": "FRM-07", "TLT-06": "FRM-07", "SPN-06": "FRM-07",
}


def build(only: str | None = None) -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for pid, (stem, fn, _) in B_PARTS.items():
        if only and pid != only:
            continue
        path = OUT / f"{pid}_{stem}.step"
        shape = fn()
        cq.exporters.export(shape, str(path))
        stepio.stabilise(path)
        # STL beside the STEP: preview on GitHub, slicers, mesh tools (coarse: it is an envelope)
        cq.exporters.export(shape, str(path.with_suffix(".stl")), tolerance=0.1, angularTolerance=0.3)
        out.append(path)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    a = ap.parse_args(argv)
    for p in build(a.only):
        print(p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
