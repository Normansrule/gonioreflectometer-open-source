# 06 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| CAM-03a | f/8 aperture stop | [CAM-03a_aperture_stop_f8.step](CAM-03a_aperture_stop_f8.step) | [CAM-03a_aperture_stop_f8.stl](CAM-03a_aperture_stop_f8.stl) |
| CAM-03b | Camera plate + post clamp | [CAM-03b_camera_plate.step](CAM-03b_camera_plate.step) | [CAM-03b_camera_plate.stl](CAM-03b_camera_plate.stl) |
| LSR-05a | Lamp body + tube, bar clamp, polarizer slot | [LSR-05a_lamp_tube.step](LSR-05a_lamp_tube.step) | [LSR-05a_lamp_tube.stl](LSR-05a_lamp_tube.stl) |
| LSR-05b | Lamp back cap | [LSR-05b_lamp_cap.step](LSR-05b_lamp_cap.step) | [LSR-05b_lamp_cap.stl](LSR-05b_lamp_cap.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| CAM-01 | USB camera 12 MP IMX477, M12 mount (UVC) | [`CAM-01_arducam_b0433_imx477_usb.step`](../../../cad/bought/CAM-01_arducam_b0433_imx477_usb.step) | [link](https://www.uctronics.com/download/Amazon/B0433_Arducam_12MP_USB_Camera_Module_Datasheet.pdf) None published. Drawing:  (38 x 38 mm, holes 34/28 mm) - dummy built from it |
| CAM-02 | M12 lens 16 mm, ≥ 1/2 in format, low distortion | [`CAM-02_m12_lens_16mm.step`](../../../cad/bought/CAM-02_m12_lens_16mm.step) | None published - use the dummy (M12 x 0.5 barrel) |
| LSR-06 | Solderless COB holder 13.5 mm (TE LUMAWISE Z35) | [`LSR-06_te_lumawise_z35_2213678_5.step`](../../../cad/bought/LSR-06_te_lumawise_z35_2213678_5.step) | [link](https://www.te.com/) (search 2213678-5 → CAD 3D model) |
| LSR-01 | COB LED CRI 90, 9 V, 13.5 mm (Citizen CLU701) | [`LSR-01_citizen_clu701_cob.step`](../../../cad/bought/LSR-01_citizen_clu701_cob.step) | None published - use the dummy (datasheet: 13.5 x 13.5 x 1.4 mm) |
| LSR-02 | Constant-current driver 350 mA, wire leads (MEAN WELL NLDD-350HW) | [`LSR-02_meanwell_nldd_350hw.step`](../../../cad/bought/LSR-02_meanwell_nldd_350hw.step) | [link](https://www.meanwellusa.com/) (search NLDD-H → 3D STEP) |
| LSR-03 | Heatsink 40 x 40 x 11.6 mm, pin fin (Wakefield 910) | [`LSR-03_wakefield_910_40_2_12_2_b0.step`](../../../cad/bought/LSR-03_wakefield_910_40_2_12_2_b0.step) | None published - use the dummy (40 x 40 x 11.6 mm pin fin) |
| LSR-04 | Thermal adhesive tape 3M 8810, 19 mm | [`LSR-04_thermal_pad_40x40.step`](../../../cad/bought/LSR-04_thermal_pad_40x40.step) | None published - use the dummy (pad) |

Design notes: [../design.md](../design.md).
