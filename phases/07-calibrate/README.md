# 07 · Calibrate → game material

<img src="../../docs/assets/steps/07.svg" width="100%" alt="Steps of stage 07">

$39.78 · total so far $480.60 / $630

[Design](design.md) · [Research](research.md) · [Parts list](bom.csv) · [3D files](3d/)

## M21 · Dark box

Only the lamp lights the sample. · 0/3 steps done · ~45 min hands-on · ~1 wk

### M21.1 Darken the room

**Time** 20 min · **Needs** ENC-02 felt · curtains / door · tape over bright LEDs

#### Do

1. Order the stage-07 parts ticked in `PARTS.md`. Felt behind the sample (opposite the camera).
2. Room lights off, curtains closed, tape over power LEDs that face the sample; laptop screen dimmed and turned away.
3. Only if M21.2 fails: build the optional drape (ENC-01 fabric on ENC-03 dowels in 4 printed `ENC-04a` sockets), vents of both boxes open.

#### Verify

- [ ] Standing at the machine, you can't read this page without the lamp.

#### Record

Tick the boxes; `make done id=M21.1`.

### M21.2 Stray light test

**Time** 15 min · **Needs** PTFE tile (CAL-01) · darkened room

#### Do

1. PTFE at 45:0 (`opengonio move M4=45 M3=0`). Room lights on.
2. `opengonio capture white --out data/stray_on`; then the same with the room light on: `--out data/stray_gap`.

#### Verify

- [ ] Dark vs lit room: centre brightness differs < 0.5 % (`opengonio curve` each, compare `centre_mean`): ambient light is negligible.

#### If a check fails

- Larger: find the source (window, monitor) and block it; if you can't, build the optional drape (M21.1) and repeat.

#### Record

Both values in phases/07-calibrate/design.md → Results.

### M21.3 Dark level

**Time** 10 min · **Needs** room dark (drape closed if built)

#### Do

1. `opengonio capture dark`
2. `opengonio calibrate dark data/dark`

#### Verify

- [ ] `opengonio calibrate show` lists `dark_counts` < 10 with today's date.

#### If a check fails

- High: light leak or camera gain not locked (M17.5).

#### Record

Commit `software/config/calibration.yaml`.

## M22 · Camera response and angle calibration

Linear brightness and true angles. · 0/2 steps done · ~1.1 h hands-on · ~1 wk

### M22.1 Camera response

**Time** 20 min · **Needs** PTFE at the zero point · M21.3 done

#### Do

1. `opengonio capture linearity`
2. `opengonio calibrate linearity data/linearity`

#### Verify

- [ ] `r2` ≥ 0.995 and `gamma` between 0.9 and 2.6; `points_used` ≥ 4.

#### If a check fails

- `points_used` < 3: change `--exposures` so the brightest is just below saturation (e.g. `--exposures 1 2 4 8 16 32`).

#### Record

`gamma`, `r2` in design.md; commit `calibration.yaml`.

### M22.2 Angle offset

**Time** 45 min · **Needs** mirror holder

#### Do

1. `opengonio capture mirror --theta 20` … repeat for 30, 40, 50, 60.
2. `opengonio calibrate mirror data/mirror_20 data/mirror_30 data/mirror_40 data/mirror_50 data/mirror_60`
3. `opengonio capture mirror --theta 40 --out data/mirror_40_after`; `opengonio verify data/mirror_40_after`

#### Verify

- [ ] `calibrate` prints five errors and `M3_offset_deg`.
- [ ] After: `mirror_peak_error_deg` within ±0.2.

#### If a check fails

- Errors grow with θ: M4 gear ratio wrong (M14.3), not an offset.

#### Record

Five errors + offset in design.md; commit `calibration.yaml`.

## M23 · Brightness calibration

Values in real reflectance units (1/sr). · 0/3 steps done · ~1.1 h hands-on · ~1 wk

### M23.1 White reference

**Time** 15 min · **Needs** CAL-01 PTFE in CAL-06a holder

#### Do

1. `opengonio capture white`
2. `opengonio calibrate white data/white --rho 0.99` (ρ from the PTFE datasheet).

#### Verify

- [ ] `calibrate show` lists `white` with today's date and `exposure_ms` = your locked exposure.

#### Record

Commit `calibration.yaml`.

### M23.2 PTFE check

**Time** 20 min · **Needs** PTFE still mounted

#### Do

1. `opengonio capture inplane --step 10 --out data/ptfe`; `opengonio curve data/ptfe`.

#### Verify

- [ ] `brdf_per_sr` = 0.315 ± 5 % for θi ≤ 60°, θr ≤ 60° (0.99 / π).

#### If a check fails

- Falls with θi: lamp spot smaller than the sample at grazing angles — check the aperture in LSR-05.
- Uniformly off: exposure changed since `calibrate white`; redo M23.1.

#### Record

Min / max `brdf_per_sr` in design.md.

### M23.3 Reciprocity

**Time** 30 min · **Needs** matte swatch (card or paper)

#### Do

1. `opengonio capture inplane --step 10 --out data/matte`; `opengonio curve data/matte`.
2. Compare rows (θi, θr) = (30, 50) and (50, 30).

#### Verify

- [ ] The two `brdf_per_sr` values agree within 5 %.

#### If a check fails

- Larger: angle calibration (M22.2) or stray light (M21.2).

#### Record

Both values in design.md; commit.

## M24 · First game material

A measured swatch looks right in Blender, Unreal or Unity. · 0/3 steps done · ~1.8 h hands-on · ~1 wk

### M24.1 Measure

**Time** 40 min · **Needs** glossy plastic swatch

#### Do

1. `opengonio capture inplane --step 5 --out data/swatch`
2. `opengonio verify data/swatch`; `opengonio curve data/swatch`

#### Verify

- [ ] `result` PASS (or WARN with only `saturated` ≤ 5 % of shots).
- [ ] `curve.csv`: `brdf_per_sr` filled on every unsaturated row.

#### Record

Tick the boxes; `make done id=M24.1`.

### M24.2 Fit

**Time** 10 min · **Needs** M24.1

#### Do

1. `opengonio fit data/swatch`; open `data/swatch/fit.svg`.

#### Verify

- [ ] `rms_pct_of_peak` < 10.
- [ ] Fitted lines pass through the dots around each peak.

#### If a check fails

- Big error only near grazing angles: normal; refit with `--step 10` data, or ignore θ > 70°.

#### Record

Copy `fit.json` to `phases/07-calibrate/swatch_fit.json`.

### M24.3 In a game engine

**Time** 1 h · **Needs** Blender (free), Unreal or Unity · photo of the swatch at θi = 40°

#### Do

1. New material with the values under `engines` in `fit.json` (Blender: Principled BSDF Base Color, Roughness, Metallic).
2. Plane + point light at 40° from the normal, camera at the mirror angle; render.

#### Verify

- [ ] Side by side with the photo: highlight size and position match by eye.

#### Record

`phases/07-calibrate/render_vs_photo.png`; commit `make publish m="M24 first material"`.

[Sources](../../REFERENCES.md): R1 · R2 · R5 · R6 · R7 · R49 · S12 · S13 · G1 · G12 · G16 · G19 · G20 · G21 · G22 · G24 · G26 · G29 · G34 · T1 · T2 · T5 · T8 · T9 · T11 · T12 · T13 · T17 · T22 · T25 · T27 · T30 · T31 · T32 · T33 · T35 · T36 · T37 · T38 · T39 · T40 · T43 · T45 · T46 · T47 · T48 · T49 · T50 · V1 · V7 · V9 · V19 · V20 · V21 · V22 · V23 · V24 · N1 · N2 · N4 · N10 · N24 · N26 · N28 · N30 · N31 · N32 · N33 · N34 · N35 · N36 · H19 · H22 · H39 · H47 · H48 · E1 · E2 · E3 · E4 · E5 · E6 · E7 · E9 · E12 · E13
