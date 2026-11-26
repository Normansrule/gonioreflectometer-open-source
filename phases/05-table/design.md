# 05 · Design

- **Fixed bolt axle (skateboard-wheel style):** an M8 × 75 bolt (TBL-05, DIN 931 smooth shank) stands in the post at (0, 0), its head locked in a hex pocket. The **drum** (TBL-07a: 100T teeth, two 608 seats, OG-40 top) turns on the two bearings around it. The inner races are clamped to the bolt by a 1 mm shim on the post top, a 6 mm spacer and one nut tightened with a 13 mm spanner; the outer races turn with the drum. Nothing to cut or file.
- Drive 5 : 1 (20T → 100T teeth on the drum) on a 232 mm belt: the motor stands shaft-up on the deck **inside the lazy Susan opening** (centre 49.4 mm from the axis), in a bracket whose rails slide in slots for belt tension.
- **Home switch:** the table flag (TBL-07h) screws to the drum top (2 × M2 × 8 into the flag holes, on the side away from the motor); its 1.5 mm fin hangs down at r 60, 62–80.7 mm above the deck. At home (M3 = −180°) the fin sits in the 3.1 mm slot of the endstop (TBL-04), which stands on a printed riser (TBL-07g) on three spare deck pilots at x = 40 (y = −40, 0, 40) on +X, inside the lazy Susan opening. The PCB is 56 mm up, so its plugged lead stays below the yoke base that sweeps r ≤ 72 from the drum top; r 60 keeps the fin clear of the table motor's pulley (r ≤ 57.4) when it swings past 180°.
- The drum's OG-40 top (M2 × 12 self-tap) takes the stage-08 yoke (a swatch clamp until then).
- Checked in CAD: nothing that turns with the table (drum, flag, yoke, cradle, motors) touches the table motor, its bracket, the endstop and its riser, the lazy Susan or the M4 motor over a full turn; at home the fin fills the endstop's slot.

| z above the deck (mm) | Part |
|---|---|
| 1.0–6.5 | bolt head (hex-locked in the post) |
| 52.5–53.5 | 1 mm shim on the post top (inner race only) |
| 53.5–60.5 / 66.5–73.5 | lower / upper 608 in the drum; drum teeth 54.7–61.7 (= the motor's 20T: motor body 48 + bracket plate 5) |
| 73.5–80.0 | M8 nut (bolt end 81.5) |
| 80.7 | drum top: yoke base; tilt axis at 150 |

Fasteners: M2 × 12 × 4 (post) + 2 + washers (bracket slots), M2 × 8 × 2 (flag), M2 × 10 × 3 + washers (riser foot), M2 × 8 × 2 (endstop on the riser), M3 × 8 × 4 (motor face, FRM-07).

## 3D parts

| Part | Source |
|---|---|
| Drum, flags, motor bracket, post, spacers, endstop riser, table flag (TBL-07a–h) | `tools/cad/parts.py` (`TABLE_Z`, `TABLE_BELT_C`) |
| NEMA 17 (17HS4401, 38 mm) | repo model `cad/bought/LAR-02_nema17_17hs4401.step` (no maker STEP for the SIMAX pack) [P58] |

## Results

(fill in)
