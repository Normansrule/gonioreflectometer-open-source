#!/usr/bin/env python3
"""Whole machine as ONE STEP assembly -> cad/assembly/opengonio_assembly.step (Onshape: Insert -> Import, or drag in;
it arrives as an Assembly with every part separate and named by BOM ID).

Printed parts come from tools/cad/parts.py, bought parts from the dummies in tools/cad/bought.py (envelopes: swap in
vendor models from cad/README.md). Pose shown: M4 = 90 deg (light arm on +Y), M3 = 0, M2 = 90 deg (platter face up).
Frame: origin under the zero point on the deck top, +X toward the camera, z up; zero point at (0, 0, 150).
Positions are v0 (from the docs and the CAD constants); expect to nudge some by a few mm.
SPDX-License-Identifier: CERN-OHL-S-2.0
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq
from OCP.gp import gp_Trsf
from OCP.TopLoc import TopLoc_Location

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bought as B  # noqa: E402
import stepio  # noqa: E402
import parts as P  # noqa: E402

OUT = ROOT / "cad" / "assembly" / "opengonio_assembly.step"
PRINT, BUY, OPT = cq.Color(0.12, 0.12, 0.13), cq.Color(0.75, 0.55, 0.25), cq.Color(0.5, 0.5, 0.55)


def orient(shape, z_to=(0, 0, 1), y_to=(0, 1, 0), t=(0, 0, 0)):
    """Rigid transform: local +z -> z_to, local +y -> y_to (both unit, perpendicular), then translate by t."""
    z = cq.Vector(*z_to).normalized()
    y = cq.Vector(*y_to).normalized()
    x = y.cross(z)
    tr = gp_Trsf()
    tr.SetValues(x.x, y.x, z.x, float(t[0]), x.y, y.y, z.y, float(t[1]), x.z, y.z, z.z, float(t[2]))
    s = shape.val() if hasattr(shape, "val") else shape
    if isinstance(s, cq.Workplane):
        s = s.val()
    if not isinstance(s, cq.Shape):
        s = cq.Compound.makeCompound(list(shape.vals()))
    return s.moved(cq.Location(TopLoc_Location(tr)))


def rot_z(shape, deg, t=(0, 0, 0)):
    s = shape.val() if hasattr(shape, "val") else shape
    return s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), deg).translate(cq.Vector(*t))


GROUPS: dict[str, str] = {}   # part name -> what moves it: fixed, arm (M4), table (M3), tilt (M2), spin (M1); transforms in poses.py


def build() -> cq.Assembly:
    a = cq.Assembly(name="OpenGonio")
    n = {}
    GROUPS.clear()

    def add(name, shape, color, g="fixed"):
        n[name] = n.get(name, 0) + 1
        full = f"{name}_{n[name]}" if n[name] > 1 or name in ("LAR-08a", "FRM-09c", "FRM-09d", "FRM-09i") else name
        a.add(shape, name=full, color=color)
        GROUPS[full] = g

    Z = P.TABLE_Z
    # ---- frame
    for k, tile in enumerate(P.TILE_NAMES):                                          # printed deck, flipped from print pose
        i, j = k % 3 - 1, k // 3 - 1
        add(f"FRM-01{chr(97 + k)}_deck_{tile}", orient(P.deck_tile(i, j), z_to=(0, 0, -1), y_to=(0, 1, 0), t=(P.DECK_TILE * i, P.DECK_TILE * j, 0)), PRINT)
    for x in P.SADDLES_X:
        add("FRM-09d", orient(P.bar_saddle(), t=(x, 0, 0)), PRINT)
    vert = dict(z_to=(-1, 0, 0), y_to=(0, 1, 0))                                     # bar along world z, `top` pilots along x
    add("FRM-02a_outrigger_1", orient(P.outrigger_bar(0), t=(P.OUTRIGGER_X[0], 0, 16)), PRINT)
    add("FRM-02b_outrigger_2", orient(P.outrigger_bar(1), t=(P.OUT_JOINT, 0, 16)), PRINT)
    add("FRM-09i", orient(P.bar_coupler(), z_to=(1, 0, 0), y_to=(0, 0, 1), t=(P.OUT_JOINT - P.COUPLER_L / 2, 0, 16)), PRINT)
    add("FRM-09f_end_foot", orient(P.end_foot(), t=(P.END_FOOT_X, 0, -P.DECK_H)), PRINT)
    add("FRM-09h_camera_pillar", orient(P.camera_pillar(), t=(P.CAM_POST_X, 0, 12)), PRINT)            # measuring camera
    add("FRM-09e_post_socket", orient(P.post_socket(), t=(P.SCAN_POST_X, 0, 12)), PRINT)
    add("FRM-02c_scan_post_1", orient(P.scan_post_bar(0), t=(P.SCAN_POST_X, 0, P.POST_Z0), **vert), PRINT)
    add("FRM-02d_scan_post_2", orient(P.scan_post_bar(1), t=(P.SCAN_POST_X, 0, P.POST_JOINT), **vert), PRINT)
    add("FRM-09i", orient(P.bar_coupler(), t=(P.SCAN_POST_X, 0, P.POST_JOINT - P.COUPLER_L / 2)), PRINT)
    for k in range(4):
        add("FRM-09c", rot_z(P.protractor_segment(), 20 + 80 * k), PRINT)
    # ---- power and controller
    px, py = P.POWER_XY
    add("PWR-18_power_plate", orient(P.power_plate(), t=(px, py, 0)), PRINT)
    add("PWR-28_estop", orient(B.estop_station(), t=(px + P.ESTOP_BOX_AT[0], py + P.ESTOP_BOX_AT[1], P.PLATE[2])), BUY)
    add("PWR-30_dc_jack", orient(B.dc_jack_screw(), t=(px + P.JACK_AT[0], py + P.JACK_AT[1], P.PLATE[2])), BUY)
    tx, ty = P.TRAY_XY
    add("CTL-10b_controller_tray", orient(P.controller_tray(), t=(tx, ty, 0)), PRINT)
    add("CTL-01_btt_skr_pico", orient(B.skr_pico(), y_to=(0, -1, 0), t=(tx + P.SKR_AT[0], ty + P.SKR_AT[1], 3 + P.SKR_STANDOFF)), BUY)   # turned 180 deg
    add("CTL-02_esp32s3_hub", orient(B.esp32s3_devkitc(), t=(tx + P.ESP_AT[0], ty + P.ESP_AT[1], 3 + P.ESP_PED + 1.0)), BUY)   # pins up, 1 mm foam tape
    add("PWR-10_opto_module", orient(B.B_PARTS["PWR-10"][1](), t=(tx + 47, ty + 40, 3)), BUY)
    for (x, y), name in zip(P.WAGO_POCKETS, ("MOT_plus", "MOT_minus", "keypad_GND")):          # 221-413s, entries facing -Y
        add(f"PWR-20_{name}", orient(B.wago(3), z_to=(0, 0, 1), y_to=(-1, 0, 0), t=(tx + x, ty + y, 3)), BUY)
    add("LSR-02_led_driver", orient(B.ldd_hw(), t=(tx + 40, ty + 5, 3)), BUY)                     # leads toward +X
    # ---- hub add-on: status screen (STA-09) on its stand, face toward -X
    sx, sy = P.SCREEN_XY
    ta = math.radians(P.SCREEN_TILT)
    add("STA-10a_screen_stand", orient(P.screen_stand(), t=(sx, sy, 0)), PRINT)
    n_ = (-math.cos(ta), 0, math.sin(ta))                                           # face normal, toward the user
    d_ = (math.sin(ta), 0, math.cos(ta))                                            # up the slope
    cz = P.SCREEN_C
    mod = (sx - 18 + P.TFT_POCKET * math.cos(ta) + cz * math.sin(ta), sy,           # module back on the pocket floor
           3 - P.TFT_POCKET * math.sin(ta) + cz * math.cos(ta))
    add("STA-09_status_screen", orient(B.tft_2in(), z_to=n_, y_to=d_, t=mod), OPT)
    top = (mod[0] + 4.0 * n_[0], sy, mod[2] + 4.0 * n_[2])
    add("STA-10b_screen_bezel", orient(P.screen_bezel(), z_to=n_, y_to=d_, t=top), PRINT)
    # ---- light arm (M4 = 90 deg: arm on +Y)
    add("LAR-01_lazy_susan", orient(B.lazy_susan()), BUY)
    lead = P.UPRIGHT_LEAD                                                       # lamp on +Y; upright 15.3 deg further on
    rim0 = 90 + lead - 22.5                                                     # arm segment centred on the upright
    for k in range(1, 8):
        add("LAR-08a", rot_z(P.rim_segment(), rim0 + 45 * k, (0, 0, 8)), PRINT, g="arm")
    add("LAR-08c_arm_segment", rot_z(P.arm_segment(), rim0, (0, 0, 8)), PRINT, g="arm")
    R = P.RING_MOTOR_R
    add("LAR-08b_ring_motor_mount", orient(P.ring_motor_mount(), t=(R, 0, 0)), PRINT)
    add("LAR-02_motor_M4", orient(B.nema17(38, 24), z_to=(0, 0, -1), y_to=(0, 1, 0), t=(R, 0, 30)), BUY)
    add("LAR-04_pulley_M4", orient(B.gt2_20t(), t=(R, 0, 8)), BUY)
    ux, uy = -P.UPRIGHT_OFFSET, math.sqrt(P.ARM_R ** 2 - P.UPRIGHT_OFFSET ** 2)  # upright beside the beam line (x = 0)
    add("LAR-08f_upright_bar", orient(P.upright_bar(), t=(ux, uy, P.UPRIGHT_Z0), **vert), PRINT, g="arm")
    arm_z = P.ARM_Z                                                                                     # lamp clamp channel centre
    add("LAR-08e_cross_clamp", orient(P.cross_clamp(), t=(ux + 11, uy, arm_z - 16)), PRINT, g="arm")
    add("LAR-08g_arm_bar", orient(P.arm_bar(), z_to=(0, 0, 1), y_to=(-1, 0, 0), t=(P.LAMP_ARM_X, P.ARM_Y0, arm_z)), PRINT, g="arm")
    ly = 300.0 + P.LAMP_COB_Z                                                    # back face: COB 300 mm from the zero point
    lamp = dict(z_to=(0, -1, 0), y_to=(0, 0, 1), t=(0, ly, 150))                     # beam axis through the zero point
    add("LSR-05a_lamp", orient(P.lamp_tube(), **lamp), PRINT, g="arm")
    add("LSR-05b_lamp_cap", orient(P.lamp_cap(), z_to=(0, -1, 0), y_to=(0, 0, 1), t=(0, ly + 3, 150)), PRINT, g="arm")
    hs = ly - (P.HS_H - P.PRELOAD)                                                   # heatsink front face (stack clamped)
    add("LSR-03_heatsink", orient(B.heatsink(), z_to=(0, 1, 0), y_to=(0, 0, 1), t=(0, hs, 150)), BUY, g="arm")
    add("LSR-06_holder", orient(B.cob_holder(), z_to=(0, -1, 0), y_to=(0, 0, 1), t=(0, hs, 150)), BUY, g="arm")
    add("LSR-01_cob", orient(B.cob_clu701(), z_to=(0, -1, 0), y_to=(0, 0, 1), t=(0, hs - P.PAD_T, 150)), BUY, g="arm")
    # ---- table (M3 = 0)
    add("TBL-07d_table_post", orient(P.table_post()), PRINT)
    add("TBL-05_axle_bolt", orient(B.bolt(8, 75, 13, 5.3, True)), BUY)
    add("TBL-07a_table_drum", orient(P.table_drum(), t=(0, 0, Z["drum"])), PRINT, g="table")
    for zz in (Z["b1"], Z["b2"]):
        add("FRM-08_608", orient(B.cyl(22, 7).cut(B.cyl(8, 7)), t=(0, 0, zz)), BUY, g="table")
    add("TBL-07c_table_motor_bracket", orient(P.table_motor_bracket(), t=(-P.TABLE_BELT_C, 0, 0)), PRINT)
    add("TBL-01_motor_M3", orient(B.nema17(38, 24), t=(-P.TABLE_BELT_C, 0, 48)), BUY)
    add("TBL-03_pulley_M3", orient(B.gt2_20t(), t=(-P.TABLE_BELT_C, 0, 53.7)), BUY)
    add("TBL-02_belt_232", orient(B.belt_loop(6.37, 31.83, P.TABLE_BELT_C), t=(-P.TABLE_BELT_C, 0, Z["drum"] + 1.2)), BUY)
    add("TBL-07g_endstop_riser", orient(P.endstop_riser()), PRINT)                       # table home (M3 = -180): +X
    add("TBL-04_endstop", orient(B.tcst2103_module(), t=(P.TFLAG["fin_r"], 0, P.ENDSTOP_Z)), BUY)
    add("TBL-07h_table_flag", orient(P.table_flag(), z_to=(0, 0, -1), y_to=(0, 1, 0), t=(0, 0, Z["hub_top"] + P.TFLAG["tab_t"])), PRINT, g="table")
    # ---- tilt (yoke arms along Y) + spin, M2 = 90 deg: platter face up
    yz = Z["hub_top"]
    add("TLT-07a_tilt_yoke", rot_z(P.tilt_yoke(), 90, (0, 0, yz)), PRINT, g="table")
    add("TLT-07c_tilt_cradle", rot_z(P.tilt_cradle(), 90, (0, 0, 150 + P.SPIN["motor_face"])), PRINT, g="tilt")
    add("SPN-07a_spin_platter", orient(P.spin_platter(), t=(0, 0, 150 - P.SPIN["platter"])), PRINT, g="spin")
    add("SPN-01_motor_M1", orient(B.nema17(21.5, 20), t=(0, 0, 150 + P.SPIN["motor_face"])), BUY, g="tilt")
    ya = P.YOKE_INNER / 2
    add("TLT-01_motor_M2", orient(B.nema17(38, 24), z_to=(0, 1, 0), y_to=(0, 0, 1), t=(0, ya, yz + P.YOKE_SEAT + P.TILT_BELT_C)), BUY, g="table")
    add("TLT-07b_pulley_100T", orient(P.gt2_pulley(100), z_to=(0, 1, 0), y_to=(0, 0, 1), t=(0, ya + 13, 150)), PRINT, g="tilt")
    for s in (-1, 1):
        add("TLT-05_stub_bolt", orient(B.bolt(8, 35, 13, 5.3, True), z_to=(0, -s, 0), y_to=(0, 0, 1), t=(0, s * (ya + 12 + 1 + 9.4 + 5.3), 150)), BUY, g="tilt")
        add("FRM-08_608", orient(B.cyl(22, 7).cut(B.cyl(8, 7)), z_to=(0, s, 0), y_to=(0, 0, 1), t=(0, s * (ya + 12 - 7.2), 150)), BUY, g="table")
    # ---- cameras (look along -X at the zero point); lens front 350 (measuring) / 650 mm at 15 deg down (scan)
    def camera(plate, tag, view, up, back):
        """plate back centre at `back`, camera looking along `view`."""
        f = dict(z_to=view, y_to=up)
        at = lambda d: tuple(back[i] + d * view[i] for i in range(3))
        add(f"CAM-03b_camera_plate{tag}" if not tag else "SCN-03d_scan_camera_plate", orient(plate, t=back, **f), PRINT)
        z_board = P.CAM_PLATE + P.CAM_STANDOFF
        add(f"CAM-0{1 if not tag else 4}_camera{tag}", orient(B.camera_b0433(), t=at(z_board), **f), BUY)
        add(f"CAM-0{2 if not tag else 5}_lens{tag}", orient(B.lens_m12(), t=at(P.CAM_LENS_Z - 17.0), **f), BUY)
    camera(P.camera_plate(), "", (-1, 0, 0), (0, 0, 1), (P.CAM_POST_X - P.CAM_CLAMP / 2, 0, 150))
    e = math.radians(P.SCAN_TILT)
    camera(P.scan_camera_plate(), "_scan", (-math.cos(e), 0, -math.sin(e)), (-math.sin(e), 0, math.cos(e)),
           (P.SCAN_POST_X - P.SCAN_CLAMP_OFF, 0, P.SCAN_LENS_Z + P.CAM_LENS_Z * math.sin(e)))
    return a


STAMP = OUT.with_name("inputs.sha256")      # the STEP writer orders colour records differently each run, so the
                                           # file is only rewritten when the CAD sources change (or with --force)


def inputs_hash() -> str:
    import hashlib
    h = hashlib.sha256()
    for f in ("parts.py", "bought.py", "assembly.py"):
        h.update((Path(__file__).resolve().parent / f).read_bytes())
    return h.hexdigest()


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    digest = inputs_hash()
    if "--force" not in sys.argv and OUT.exists() and STAMP.exists() and STAMP.read_text().strip() == digest:
        print(f"{OUT.relative_to(ROOT)} up to date (CAD sources unchanged; --force to rebuild)")
        return 0
    a = build()
    a.export(str(OUT), exportType="STEP")
    stepio.stabilise(OUT)
    STAMP.write_text(digest + "\n")
    print(f"{len(a.children)} parts -> {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
