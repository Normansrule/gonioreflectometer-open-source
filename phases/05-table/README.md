# 05 · Table (M3)

<img src="../../docs/assets/steps/05.svg" width="100%" alt="Steps of stage 05">

$23.56 · total so far $324.95 / $630

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/)

## M15 · Table axis built

Sample table turns on its fixed bolt axle without wobble. · 0/3 steps done · ~1.4 h hands-on · ~1 wk

### M15.1 Print table parts

**Time** 10 min (+ print 5 h) · **Needs** stage-05 parts `have` in `PARTS.md`

#### Do

1. {'Print `TBL-07a_table_drum`, 2 × `TBL-07b_home_flag` (tilt and spin), `TBL-07c_table_motor_bracket`, `TBL-07d_table_post`, `TBL-07f_spacers`, `TBL-07g_endstop_riser` (foot on the bed), `TBL-07h_table_flag` (as exported': 'bridge on the bed, fin up).'}

#### Verify

- [ ] A 608 presses into each drum seat by thumb and stays.
- [ ] The M8 bolt head drops into the post's hex pocket from below and can't turn.

#### Record

Tick the boxes; `make done id=M15.1`.

### M15.2 Fixed axle and drum

**Time** 45 min · **Needs** 2 × FRM-08 608 · TBL-05 M8 × 75 bolt + nut · 1 mm shim + 6 mm spacer (TBL-07f) · 4 × M2 × 12 (FRM-06) · TLS-10 13 mm spanner

#### Do

1. Bolt up through the post from below, head into the hex pocket. Post on its 4 pilots at the deck centre; 4 × M2 × 12 (the bolt is now trapped and can't turn).
2. Press both 608s into the drum. Onto the bolt: 1 mm shim (sits on the post top), the drum (lower 608 onto the bolt), 6 mm spacer down the drum's top hole, M8 nut.
3. Tighten the nut with the spanner until the drum has no up-down play but still turns freely (the nut presses only the inner races).

#### Verify

- [ ] Spin by hand ±180°: smooth, no click.
- [ ] Calipers on the drum top at 30 mm radius: height changes < 0.3 mm over a turn.

#### If a check fails

- Tight spot: nut too tight; back it off 1/6 turn.
- Wobble: a 608 not pressed square into its seat.

#### Record

Tick the boxes; `make done id=M15.2`.

### M15.3 Drive belt

**Time** 30 min · **Needs** TBL-01 motor · TBL-02 232 mm belt · TBL-03 pulley · TBL-07c bracket · 4 × M3 × 8 (FRM-07) · 2 × M2 × 12 + washers

#### Do

1. Motor face up, bracket top plate on its face (4 × M3 × 8); 20T pulley on the shaft, teeth level with the drum's teeth.
2. E-stop pressed: its cable into the SKR Pico Y socket, run along the deck edge (never plug or unplug a motor with motor power on).
3. Belt on the motor pulley and the drum's teeth; bracket rails' slots over their 2 deck pilots (inside the lazy Susan, at 180°); pull it outward until the belt deflects ~3 mm under a finger; M2 × 12 + washer through each slot.

#### Verify

- [ ] No belt skip when you hold the table and the motor turns slowly (`opengonio send 'G91' 'G1 Y5 F100' 'G90'` after M16.1).
- [ ] Motor and bracket stay inside the lazy Susan opening (no contact when M4 turns).

#### Record

Commit.

## M16 · Table homes and repeats

M3 returns to the same spot every time (≤ 0.1°). · 0/4 steps done · ~1.8 h hands-on · ~1 wk

### M16.1 Flag and homing

**Time** 30 min · **Needs** TBL-04 endstop · TBL-07g riser, TBL-07h flag · 3 × M2 × 10 + washers, 2 × M2 × 6, 2 × M2 × 8 · CTL-06 leads (as M10.2)

#### Do

1. Riser on the three deck pilots at x = 40 (y = −40, 0, +40; +X side, inside the lazy Susan opening), 3 × M2 × 10 + washer, post outward. Endstop on its pad: slot over the pad's middle, header end outward, 2 × M2 × 6 self-tap.
2. Flag on the drum top's two flag holes (the close pair outside the four yoke pilots), 2 × M2 × 8 self-tap, fin hanging down outside the drum. Turn the table by hand: at −180° (fin on +X) the fin passes through the slot without touching either side.
3. E-stop pressed. Lead into the SKR Pico Y-STOP socket, along the riser and the deck.
4. `installed_phase: 5`; `opengonio home` ten times.

#### Verify

- [ ] Home 10/10; after homing `opengonio status` shows MPos Y = 0 and true angle M3 = −180.

#### Record

10/10 in design.md.

### M16.2 Angle check

**Time** 15 min · **Needs** paper 360° protractor (any free printable, printed on TLS-08) taped on the drum top · a fixed pointer (tape on the post)

#### Do

1. `opengonio move M3=0`, `M3=90`, `M3=-90`; read the protractor against the pointer.

#### Verify

- [ ] Each within ±0.5°.

#### If a check fails

- Scaled error: `M3.gear_ratio` = 100 / 20 = 5 only with the printed 100T pulley.

#### Record

Readings in design.md.

### M16.3 Repeatability

**Time** 45 min · **Needs** laser + mirror · wall 2.0 m

#### Do

1. Mirror on the table; `opengonio repeat M3 --at 0 --away 45 --n 20`.

#### Verify

- [ ] `"pass": true`.

#### Record

JSON in phases/05-table/design.md → Results.

### M16.4 Both axes and collision guard

**Time** 15 min · **Needs** M4 and M3 built

#### Do

1. `opengonio move M4=60 M3=30`
2. `opengonio move M4=10`

#### Verify

- [ ] First move runs.
- [ ] Second prints `refused: M4=10.0 outside [20.0, 324.0]` and nothing moves.

#### Record

Commit `make publish m="M16 table done"`.

> **Safety:** Before touching a motor plug or a screw terminal: press the e-stop and unplug the adapter.

[Sources](../../REFERENCES.md): G33 · H11 · H16 · H17 · H26 · H37 · H41 · P41 · P42 · P43 · P58 · F12
