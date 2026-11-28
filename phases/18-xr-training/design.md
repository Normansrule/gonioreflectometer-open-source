# 18 · Design

Details: wiki → XR training. Paper draft: `paper/xr/opengonio-xr.tex`.

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Delivery | one WebXR page for both headsets | same content on both, so the comparison is of the platforms |
| Engine | none (plain WebGL) | matches the website; nothing to install on the headsets |
| Alignment | two pinched points | no markers and no camera access needed |
| Fallback | native OpenXR build (M54.3) | HoloLens 2's browser may not start AR sessions [X6] |

## Open questions

- Which Meta Quest model the lab has: [TBD].
- Whether the study with participants is in scope, and its ethics approval number: [TBD].
- Author list and order for the paper: [TBD].

## Results

| Step | Result |
|---|---|
| M51.1 | Desktop browser: five lessons render; `test_xr.py` passes (2026-11-25, headless Chrome). No headset. |
| M54.1 | Page part built (2026-11-28): simulated run drawn on the lobe, `curve.csv` loader. Real run: [TBD] |
| M54.2 | Occlusion built, untested on a headset. Lit sample: not built |
| M52.1 – M53.2, M54.3, M55 | [TBD]: needs the headsets and the built machine |
