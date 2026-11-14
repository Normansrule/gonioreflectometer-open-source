# 10 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| MSK-06a | LED ring (8 bands) | [MSK-06a_led_ring.step](MSK-06a_led_ring.step) | [MSK-06a_led_ring.stl](MSK-06a_led_ring.stl) |
| MSK-06b | 40 deg LED mast | [MSK-06b_led_mast.step](MSK-06b_led_mast.step) | [MSK-06b_led_mast.stl](MSK-06b_led_mast.stl) |
| SPC-03a | Spectral sensor tube + post clamp | [SPC-03a_spectral_tube.step](SPC-03a_spectral_tube.step) | [SPC-03a_spectral_tube.stl](SPC-03a_spectral_tube.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| MSK-01 | Narrow-band 3 W star LEDs, pre-soldered leads (7 bands, 450–660 nm) | [`MSK-01_star_led_20mm.step`](../../../cad/bought/MSK-01_star_led_20mm.step) | None published - use the dummy (20 mm star LED) |
| MSK-02 | Constant-current driver 350 mA | [`MSK-02_meanwell_nldd_350h.step`](../../../cad/bought/MSK-02_meanwell_nldd_350h.step) | [link](https://www.meanwellusa.com/) (search NLDD-H → 3D STEP) |
| MSK-03 | 4-channel MOSFET switch module, opto-isolated inputs, screw terminals (2 used: 8 channels) | [`MSK-03_mosfet_module_4ch.step`](../../../cad/bought/MSK-03_mosfet_module_4ch.step) | None published - use the dummy (4-channel module with terminal blocks) |
| MSK-04 | Heatsink 40 mm (second LSR-03) | [`LSR-03_wakefield_910_40_2_12_2_b0.step`](../../../cad/bought/LSR-03_wakefield_910_40_2_12_2_b0.step) | None published - use the dummy (40 x 40 x 11.6 mm pin fin) |
| MSK-05 | Linear polarizer film 10 x 10 cm (10) | [`MSK-05_polarizer_film_100mm.step`](../../../cad/bought/MSK-05_polarizer_film_100mm.step) | None published - use the dummy (film) |
| SPC-01 | AS7341 spectral sensor breakout, 8 visible bands + clear + NIR (STEMMA QT) | [`SPC-01_adafruit_4698_as7341.step`](../../../cad/open/SPC-01_adafruit_4698_as7341.step) | cad/open/SPC-01_adafruit_4698_as7341.step |
| SPC-02 | JST-SH 4-pin to female jumper cable 150 mm | [`SPC-02_jst_sh_cable.step`](../../../cad/bought/SPC-02_jst_sh_cable.step) | None published - use the dummy (cable) |

Design notes: [../design.md](../design.md).
