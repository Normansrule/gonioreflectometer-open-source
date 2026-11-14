# 15 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| STA-07a | Pi Zero 2 W mount | [STA-07a_pi_zero_mount.step](STA-07a_pi_zero_mount.step) | [STA-07a_pi_zero_mount.stl](STA-07a_pi_zero_mount.stl) |
| STA-10a | Status screen stand (4 deck pilots) | [STA-10a_screen_stand.step](STA-10a_screen_stand.step) | [STA-10a_screen_stand.stl](STA-10a_screen_stand.stl) |
| STA-10b | Status screen bezel | [STA-10b_screen_bezel.step](STA-10b_screen_bezel.step) | [STA-10b_screen_bezel.stl](STA-10b_screen_bezel.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| STA-01 | Raspberry Pi Zero 2 WH (header soldered) | [`STA-01_pi_zero_2wh.step`](../../../cad/bought/STA-01_pi_zero_2wh.step) | [link](https://www.snapeda.com/parts/RASPBERRY%20PI%20ZERO%202%20W/Raspberry%20Pi/view-part/) (free login); outline = Pi Zero W |
| STA-02 | microSD card 32 GB | [`STA-02_microsd_card.step`](../../../cad/bought/STA-02_microsd_card.step) | None published - use the dummy (microSD) |
| STA-03 | Buck converter 24 V to 5 V 3 A | [`STA-03_buck_lm2596_display.step`](../../../cad/bought/STA-03_buck_lm2596_display.step) | None published - use the dummy (generic LM2596 board) |
| STA-04 | Micro-USB OTG adapter | [`STA-04_otg_adapter.step`](../../../cad/bought/STA-04_otg_adapter.step) | None published - use the dummy (adapter) |
| STA-05 | SSD1306 OLED 0.96 in I2C 128x64 | [`STA-05_ssd1306_oled_096in.step`](../../../cad/bought/STA-05_ssd1306_oled_096in.step) | None published - use the dummy (generic SSD1306 board) |
| STA-06 | Jumper wires female-female (10) | [`STA-06_jumper_wire_ff.step`](../../../cad/bought/STA-06_jumper_wire_ff.step) | None published - use the dummy (wire) |
| STA-08 | USB-A to micro-B data cable 1 m | [`STA-08_adafruit_592_microusb_cable.step`](../../../cad/open/STA-08_adafruit_592_microusb_cable.step)<br>[`STA-08_usb_cable_micro_b.step`](../../../cad/bought/STA-08_usb_cable_micro_b.step) | cad/open/STA-08_adafruit_592_microusb_cable.step |
| STA-09 | Status screen 2 in IPS 240 x 320, SPI (Waveshare 2inch LCD Module) | [`STA-09_waveshare_2in_lcd.step`](../../../cad/bought/STA-09_waveshare_2in_lcd.step) | None published - use the dummy (58 x 35 mm envelope; thickness [TBD]) |

Design notes: [../design.md](../design.md).
