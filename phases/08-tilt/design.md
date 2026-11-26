# 08 · Design

- Yoke (TLT-07a) on the table drum (OG-40, 4 × M2 × 12 self-tap), arms along ±Y so the tilt axis is square to the camera at M3 = 0. Arms carry a 608 each at the tilt axis, 150 mm above the deck = the zero point.
- Cradle (TLT-07c) turns on two **M8 × 35 stub bolts** (TLT-05): head outside → (60T pulley on the +Y arm, 9.4 mm spacer on the other) → 1 mm shim → 608 inner race → 6.8 mm spacer → M8 nut trapped in the cradle. One nut per side clamps the whole stack: nothing to cut, no flats.
- Drive 3 : 1 (20T → printed 60T) at 1/32 microstepping, on the same 232 mm belt as the table (one closed-belt size in the machine). The motor hangs on the inner face of the pulley-side arm, 74.9 mm above the axis, shaft out through the arm (slots = belt tension); everything that turns with the table stays within r ≈ 90 of its axis (pulley and bolt head outside the arm), so the table can turn ±180°.
- The cradle floor holds the pancake spin motor (stage 09); home flag (TBL-07b) on a cradle end block at −90°, endstop on the arm, lead to SKR Pico Z-STOP.
- Checked in CAD: no part of the cradle, platter or spin motor touches the yoke over M2 = −90…90°, and nothing turning with the table touches the table motor, the lazy Susan or the M4 motor over M3 = 0…360°.

Fasteners: M8 × 35 × 2 + nuts, M2 × 12 × 4 (OG-40, self-tap), M2 × 8 × 2 (flag), M2 × 8 + nut (platter hub), M3 × 8 × 4 (tilt motor, counterbored slots in the arm's motor pad) and M3 × 8 × 4 (spin motor face, cradle floor), FRM-07.

## 3D parts

| Part | Source |
|---|---|
| Yoke, 100T pulley, cradle (TLT-07a–c) | `tools/cad/parts.py` (`YOKE_SEAT`, `TILT_BELT_C`) |
| Spacers and shims (TBL-07f) | printed with the table set |
| NEMA 17 (17HS4401, 38 mm) | repo model `cad/bought/LAR-02_nema17_17hs4401.step` (no maker STEP for the SIMAX pack) [P58] |

## Results

(fill in)
