# 08 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| TLT-07a | Tilt yoke: 608 seats, motor slots above the axis | [TLT-07a_tilt_yoke.step](TLT-07a_tilt_yoke.step) | [TLT-07a_tilt_yoke.stl](TLT-07a_tilt_yoke.stl) |
| TLT-07b | GT2 60T pulley (3:1) on the stub axle | [TLT-07b_pulley_60T.step](TLT-07b_pulley_60T.step) | [TLT-07b_pulley_60T.stl](TLT-07b_pulley_60T.stl) |
| TLT-07c | Tilt cradle: stub-axle nut traps, spin motor floor | [TLT-07c_tilt_cradle.step](TLT-07c_tilt_cradle.step) | [TLT-07c_tilt_cradle.stl](TLT-07c_tilt_cradle.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| TLT-01 | NEMA 17 stepper 42 Ncm 1.5 A, 38 mm | [`LAR-02_nema17_17hs4401.step`](../../../cad/bought/LAR-02_nema17_17hs4401.step) | None published - repo model at 42.3 x 42.3 x 38 mm |
| TLT-02 | GT2 6 mm closed belt 232 mm (from the TBL-02 5-pack) | [`TLT-02_gt2_belt_232_loop.step`](../../../cad/bought/TLT-02_gt2_belt_232_loop.step) | None published - use the dummy (belt loop) |
| TLT-03 | GT2 20T pulley 5 mm bore | [`LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step`](../../../cad/open/LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step)<br>[`LAR-04_gt2_pulley_20t_5mm.step`](../../../cad/bought/LAR-04_gt2_pulley_20t_5mm.step) | cad/open/LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step (set bore to 5 mm) |
| TLT-04 | Optical endstop module, slot type (from the LAR-05 6-pack) | [`LAR-05_tcst2103_endstop_module.step`](../../../cad/bought/LAR-05_tcst2103_endstop_module.step) | [link](https://www.vishay.com/en/product/81147/) (TCST2103 sensor only) |
| TLT-05 | M8 x 35 hex bolts, half thread (10-pack; 2 used) | [`TLT-05_bolt_m8x35_nut.step`](../../../cad/bought/TLT-05_bolt_m8x35_nut.step) | Onshape Standard Content: ISO 4014 M8 x 35 hex bolt + ISO 4032 M8 nut |
| TLT-06 | Axis fasteners (M3 motor face + M2 set) | [`FRM-07_screw_m3x8.step`](../../../cad/bought/FRM-07_screw_m3x8.step) | Onshape Standard Content |

Design notes: [../design.md](../design.md).
