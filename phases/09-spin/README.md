# 09 · Spin (M1)

<img src="../../docs/assets/steps/09.svg" width="100%" alt="Steps of stage 09">

$11.99 · total so far $509.27 / $630

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/)

## M27 · Spin wired and homed

Sample spins on its own axis (direct drive). · 0/2 steps done · ~1.4 h hands-on · ~1 wk

### M27.1 Wire the spin motor

**Time** 40 min · **Needs** spare LAR-02 motor cable · 3 × WAGO 221-412 + 1 × 221-415 (PWR-20) · TLS-04 stripper · multimeter · SPN-04 endstop · TBL-07b flag · CTL-06 leads · jumpers

#### Do

1. The pancake (SPN-01) has bare leads. Find its coil pairs: touch two leads together and turn the shaft by hand; noticeably stiffer = one pair (or the meter: a pair reads a few ohms, two leads from different pairs read open). Tape-label them pair 1 and pair 2.
2. Spare 5-pack cable: cut off the 6-pin (motor-end) plug, strip 11 mm of each of its 4 wires, twist the strands. At the 4-pin XH plug, note which wire colour sits in pins 1 + 4 (board labels 2B, 2A: one driver coil) and 2 + 3 (1B, 1A: the other), from the SKR Pico schematic.
3. 3 × WAGO 221-412 + 1 × 221-415 (one motor lead and one cable wire in each): pair 1's two leads to the wires of plug pins 1 and 4; pair 2's two leads to the wires of pins 2 and 3. Tug-test each; tape the four connectors together. Check: meter at the plug, 1–4 and 2–3 read a few ohms, 1–2 open. Table: README → Wiring → 3.
4. E-stop pressed. XH plug into the SKR Pico E socket (route the cable along the yoke arm with slack for ±90° tilt and ±180° table).
5. Flag on the platter rim (2 × M2 × 8), endstop on the cradle.
6. Endstop lead into E0-STOP (3-pin: signal, GND, 5 V, as M10.2): grblHAL uses it as the A limit.

#### Verify

- [ ] Platter turns 360° by hand with the motor unpowered; face runout < 0.3 mm at 40 mm radius.
- [ ] `?` shows `Pn:A` with the flag in the slot.

#### If a check fails

- No `Pn:A`: lead order wrong at the module end (S, G, V), or the firmware was built with 3 axes (rebuild with 4).
- Spin motor buzzes, no turn: a lead from each coil on one driver coil; redo the pair test (plug 1–4 and 2–3 must each read a few ohms).
- Turns the wrong way: `$3` A bit (8), as in M08.3.

#### Record

Tick the boxes; `make done id=M27.1`.

### M27.2 Home and repeat

**Time** 45 min · **Needs** laser + mirror

#### Do

1. `installed_phase: 9`; `opengonio home`.
2. Mirror on the platter: `opengonio repeat M1 --at 0 --away 90 --n 20`.

#### Verify

- [ ] `"pass": true`.

#### Record

JSON in phases/09-spin/design.md → Results; commit.

## M28 · Anisotropic material measured

Brushed metal: highlight depends on direction. · 0/3 steps done · ~55 min hands-on · ~1 wk

### M28.1 Spin sweep

**Time** 30 min · **Needs** brushed aluminium swatch · tape arrow on the brushing direction

#### Do

1. Clamp the swatch, arrow at M1 = 0.
2. `opengonio capture spin --theta 30 --step 15 --out data/spin_brushed`
3. `opengonio curve data/spin_brushed`

#### Verify

- [ ] `centre_mean` max ÷ min ≥ 2 across M1 (curve.csv).
- [ ] Brightest when the arrow is vertical, i.e. grooves perpendicular to the light–camera plane (note that M1).

#### If a check fails

- < 2×: swatch not brushed enough, or polished; try a different piece.

#### Record

Max/min ratio and brightest M1 in phases/09-spin/design.md → Results.

### M28.2 Anisotropic set

**Time** 10 min (+ ~1.5 h unattended) · **Needs** same swatch

#### Do

1. `opengonio capture anisotropic --step 15 --phi-step 30 --out data/aniso_brushed`
2. `opengonio verify data/aniso_brushed`

#### Verify

- [ ] PASS, or WARN with only `saturated` ≤ 5 % of shots.

#### Record

Tick the boxes; `make done id=M28.2`.

### M28.3 Why it needs 4 angles

**Time** 15 min · **Needs** M28.2 · M26.3 plastic fit

#### Do

1. `opengonio curve data/aniso_brushed && opengonio fit data/aniso_brushed`

#### Verify

- [ ] `rms_pct_of_peak` for brushed ≥ 2 × the plastic's (an isotropic model can't fit it).

#### Record

Both RMS values in design.md; commit.

> **Safety:** Before touching a motor plug or a screw terminal: press the e-stop and unplug the adapter.

[Sources](../../REFERENCES.md): G5 · G9 · G11 · G14 · G16 · G18 · G27 · G40 · G43 · G44 · G49 · G50 · T4 · T15 · T26 · T34 · T37 · T41 · T42 · T44 · V9 · V48 · N8 · H3 · H37 · P43 · P48
