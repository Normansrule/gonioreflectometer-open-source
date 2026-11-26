# XR training

Augmented Reality (AR) and Virtual Reality (VR) training for the gonioreflectometer: the axis arcs and their limits, the light path, and the Bidirectional Reflectance Distribution Function (BRDF) lobe, over the real machine or around its CAD model. Extended Reality (XR) covers both.

Status: runs in a desktop browser. **Not yet run on a headset.** Every headset number below is `[TBD]` until measured (roadmap milestones M51–M55, stage 18).

| | |
|---|---|
| Page | [AR and VR](https://normansrule.github.io/gonioreflectometer-open-source/xr.html) (`docs/xr.html`, `docs/og/xr.js`) |
| Test | `software/tests/test_xr.py`: the page's JavaScript against `fit.py` and `kinematics.py` |
| Paper draft | [paper/xr/opengonio-xr.tex]({{REPO}}/paper/xr/opengonio-xr.tex), for Springer's *Virtual Reality* |
| Headsets | Microsoft HoloLens 2, Meta Quest (lab equipment; not in the parts list) |

## Lessons

| # | Lesson | Shows |
|---|---|---|
| 1 | Arcs and limits | Travel of M4 (20°–324°), M3, M2, M1 from `machine.yaml`; red where an axis must not go |
| 2 | Incident light | Ray from the lamp to the sample; θi |
| 3 | Reflection | Mirror direction, camera ray, θr, angle between camera and mirror direction |
| 4 | BRDF lobe | Lambert + GGX lobe [@R6] for the current lamp angle, radius √(f·cos θr) |
| 5 | Measure | The lamp sweeps; one bar per lamp angle is the camera reading |

## How it is built

| Part | Choice | Why |
|---|---|---|
| Delivery | One web page, WebXR Device API [@X1] with the AR module [@X2] | Same code and content on both headsets: differences measured are differences of the platforms |
| Rendering | Plain WebGL, one draw per eye, no engine | Nothing to install; the page's other 3D views work the same way |
| Geometry | `docs/og/model/rig.js`, written by `make cad` | Axes, travel, lamp and camera points come from the CAD and `machine.yaml`; `make check` fails if they drift |
| BRDF | Same formula as `fit.py` | One model in the fit, the three renderers and the trainer |
| Lines | Two crossed ribbons, width in millimetres | One-pixel lines are hard to see in a headset |
| Alignment (AR) | Two points: pinch at the sample centre, then at the camera lens | No markers, no camera access; gives position and heading, height from gravity |
| Log | Frame times, views, framebuffer size, alignment residual, as JSON | The raw data of the comparison |

Terms follow Milgram and Kishino [@X7]; registration and the two display types follow Azuma [@X8].

## Platforms

| | HoloLens 2 | Meta Quest |
|---|---|---|
| Display | optical see-through | video passthrough |
| AR through WebXR | listed as supported in Edge [@X3]; users report periods where sessions did not start [@X6] | `immersive-ar` passthrough in Browser [@X4] |
| Vendor status | out of production; updates until 31 December 2027 [@X5] | in production |
| Fallback | native build (M54.3) | native build (M54.3) |

Risk: if Edge on the lab's HoloLens 2 does not start an AR session, the web build cannot be compared on that device. M52.1 records what happens; M54.3 is the fallback.

## Comparison protocol

| Measure | Method | Unit | HoloLens 2 | Meta Quest |
|---|---|---|---|---|
| AR session starts | Enter AR on the page | yes / no | [TBD] | [TBD] |
| Frame rate | session log, mean | frames per second | [TBD] | [TBD] |
| Frame time, 95th percentile | session log | ms | [TBD] | [TBD] |
| Alignment residual | session log: distance between the two pinches minus 350 mm | mm | [TBD] | [TBD] |
| Drift | ruler at the 20° stop after one walk round the bench, 5 repeats | mm | [TBD] | [TBD] |
| Arc in view | fraction of the M4 arc visible at 0.75 m without moving the head | % | [TBD] | [TBD] |
| Legibility | rating 1–5, lab lights on with lamp on, and lights off | score | [TBD] | [TBD] |
| Learning gain | post-quiz minus pre-quiz | points | [TBD] | [TBD] |
| Usability | System Usability Scale [@X9] | 0–100 | [TBD] | [TBD] |
| Workload | NASA Task Load Index [@X10] | 0–100 | [TBD] | [TBD] |
| Discomfort | Simulator Sickness Questionnaire [@X11] | score | [TBD] | [TBD] |

The last four rows need participants and ethics approval (M53.2). Without approval they stay out of the paper. Related work on AR for learning: [@X12; @X13].

## Graphics development

| Item | State |
|---|---|
| BRDF lobe from the fitted model, in stereo | built |
| Ribbon lines with premultiplied alpha (correct on additive and on video displays) | built |
| CAD model as a ghost in VR, hidden in AR | built |
| Measured points on the lobe (M54.1) | planned |
| Sample lit with the fitted material in the headset; occlusion by the real machine (M54.2) | planned |
| Native OpenXR build with the same lessons (M54.3) | planned |

## Journal rules (Springer *Virtual Reality*)

Read from the journal's submission guidelines on 2026-11-25; re-read before submitting.

| Item | Rule |
|---|---|
| Review | single-blind |
| Abstract | 150–250 words, no undefined abbreviations, no references |
| Keywords | 4–6 |
| Format | Word, or LaTeX with the Springer Nature template; editable source files required |
| Headings | decimal numbering, at most three levels |
| Citations | author and year in parentheses; reference list alphabetical |
| Figures | vector preferred; line art ≥ 1200 dpi, halftones ≥ 300 dpi; Helvetica or Arial 8–12 pt; captions in the text |
| Declarations | funding, competing interests, ethics approval, consent, data availability; author contributions recommended |
| AI tools | a language model cannot be an author; its use is described in Methods |
| Length | no limit stated |

## Limits

- No headset has run the page. Nothing here is a result.
- Overlays are not hidden by the real machine yet.
- Two-point alignment assumes a level bench and gives no tilt correction.
- The lobe is the fitted model on a square-root scale, not measured data.
