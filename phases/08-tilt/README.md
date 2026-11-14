# 08 · Tilt (M2)

<img src="../../docs/assets/steps/08.svg" width="100%" alt="Steps of stage 08">

$16.68 · total so far $497.28 / $630

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/)

## M25 · Tilt yoke built and homed

Sample tilts without leaving the zero point. · 0/5 steps done · ~3.2 h hands-on · ~2 wk

### M25.1 Print

**Time** 10 min (+ print 9 h) · **Needs** stage-08 and stage-09 parts `have` in `PARTS.md`

#### Do

1. Print `TLT-07a_tilt_yoke.stl` (upright, 184 mm tall), `TLT-07b_pulley_100T.stl`, `TLT-07c_tilt_cradle.stl`, `SPN-07a_spin_platter.stl` (top face down).

#### Verify

- [ ] A 608 presses into each arm seat; an M8 nut drops into each cradle trap and can't turn.

#### Record

Tick the boxes; `make done id=M25.1`.

### M25.2 Cradle, platter and stub axles

**Time** 1 h · **Needs** 2 × 608 · TLT-05 2 × M8 × 35 + nuts · spacers (TBL-07f) · SPN-01 pancake motor · 4 × M3 × 8 (FRM-07), 4 × M2 × 12 · M2 × 6 + M2 nut · TLS-10 spanner

#### Do

1. Pancake motor under the cradle floor (shaft up through it, 4 × M3 × 8). Platter on the shaft: M2 nut in its slot, M2 × 6 through the hub onto the D flat; platter top level with the stub-bolt axis (the end blocks stand 10 mm higher).
2. Yoke on the drum (4 × M2 × 12 self-tap into the OG-40 pilots) with its arms along ±Y: at M3 = 0 the tilt axis is square to the camera direction (+X) and the flag holes on the drum stay clear. The pulley-side arm is +Y.
3. Pulley side: bolt through 100T pulley → 1 mm shim → 608 (outer face of the arm) → 6.8 mm spacer → cradle nut. Other side: the same with the 9.4 mm spacer instead of the pulley. Hold each bolt head with the spanner; snug, not tight.

#### Verify

- [ ] Cradle tilts ±90° by hand, no play you can feel at the platter edge.
- [ ] Platter top level with the bolt axis (ruler across both bolt centres).

#### If a check fails

- Binds: over-tightened; back off 1/6 turn.

#### Record

Tick the boxes; `make done id=M25.2`.

### M25.3 Tilt drive and flag

**Time** 45 min · **Needs** TLT-01 motor · TLT-02 280 mm belt · TLT-03 pulley · TLT-04 endstop · TBL-07b flag · 4 × M3 × 16 (FRM-07; through the 12 mm arm into the motor)

#### Do

1. E-stop pressed: motor cable into the SKR Pico Z1 socket first, along the yoke arm with slack for the table's ±180°.
2. Motor on the inner face of the pulley-side arm above the axis, shaft out through the arm slot (4 × M3 × 16 in the slots; the arm is 12 mm thick); 20T pulley outside, level with the 100T; belt on; slide the motor up to tension (~3 mm deflection); tighten.
3. Flag on a cradle end block at −90°; endstop on the arm; lead into the SKR Pico Z-STOP socket (CTL-06, as M10.2).

#### Verify

- [ ] `?` shows `Pn:Z` with the flag in the slot.
- [ ] Belt doesn't skip when you hold the platter and jog `M2` slowly.

#### Record

Tick the boxes; `make done id=M25.3`.

### M25.4 Home and repeat

**Time** 1 h · **Needs** laser + mirror · wall 2.0 m

#### Do

1. `installed_phase: 8`; `opengonio home` × 10.
2. `opengonio move M2=0`: platter vertical (phone level app on its face).
3. Mirror on the platter: `opengonio repeat M2 --at 0 --away 30 --n 20`.

#### Verify

- [ ] Home 10/10.
- [ ] Platter vertical within ±0.5° at M2 = 0.
- [ ] `"pass": true`.

#### Record

JSON in phases/08-tilt/design.md → Results.

### M25.5 Zero point stays

**Time** 20 min · **Needs** sample-centre mark

#### Do

1. `opengonio move M2=-45`, capture a frame; `M2=45`, capture a frame; compare the mark position.

#### Verify

- [ ] Mark moves < 15 px (0.5 mm).

#### If a check fails

- Larger: platter surface not on the bolt axis; move the platter on the shaft (grub) and redo.

#### Record

Shift (px) in design.md; commit.

## M26 · Full isotropic scan

All light directions, unattended. · 0/3 steps done · ~30 min hands-on · ~1 wk

### M26.1 Plan check

**Time** 5 min · **Needs** `installed_phase: 8`

#### Do

1. `opengonio plan isotropic --step 15`

#### Verify

- [ ] `poses` ≥ 100 and `axes` includes `M2`.

#### Record

Tick the boxes; `make done id=M26.1`.

### M26.2 Run

**Time** 10 min (+ ~15 min unattended) · **Needs** glossy plastic swatch on the yoke

#### Do

1. `opengonio capture isotropic --step 15 --out data/iso_plastic` (or station job *Isotropic 15deg*).
2. Don't touch the machine until it finishes.

#### Verify

- [ ] `opengonio verify data/iso_plastic`: PASS, or WARN with only `saturated` ≤ 5 % of shots.

#### Record

Tick the boxes; `make done id=M26.2`.

### M26.3 Fit and compare

**Time** 15 min · **Needs** M24 swatch fit

#### Do

1. `opengonio curve data/iso_plastic && opengonio fit data/iso_plastic`

#### Verify

- [ ] Roughness within 10 % of the in-plane fit (M24.2) for the same swatch.

#### If a check fails

- Very different: check M2 zero (M25.4) — a tilt offset biases out-of-plane rows.

#### Record

Both fits in phases/08-tilt/design.md → Results; commit.

> **Safety:** Before touching a motor plug or a screw terminal: press the e-stop and unplug the adapter.

[Sources](../../REFERENCES.md): G3 · G8 · G23 · G25 · G30 · T2 · T3 · T4 · T5 · T10 · T12 · T13 · T14 · T16 · T17 · T21 · T25 · T26 · V9 · N1 · N5 · N7 · N8 · H3 · H20 · H21 · H48 · P41 · P42 · P43 · P58 · F12
