# 04 · Light arm (M4)

<img src="../../docs/assets/steps/04.svg" width="100%" alt="Steps of stage 04">

$77.43 · total so far $301.39 / $630

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/)

## M13 · Ring drive built

Light arm turns smoothly on the ring. · 0/5 steps done · ~3.2 h hands-on · ~1 wk

### M13.1 Measure and set the rim

**Time** 30 min · **Needs** LAR-01 lazy Susan · calipers

#### Do

1. Order the stage-04 parts ticked in `PARTS.md` (if not done); mark them `ordered`.
2. Measure the lazy Susan top-plate outer Ø and its 4 hole positions.
3. Set `RIM_TEETH` in `tools/cad/parts.py` so `RIM_R` ≈ plate radius − 5 mm; `python tools/cad/parts.py --only LAR-08a`.

#### Verify

- [ ] Printed `RIM_R` within 5 ± 1 mm of the plate edge.
- [ ] `gear_ratio` = `RIM_TEETH` / 20 noted.

#### Record

Plate Ø, `RIM_TEETH`, `gear_ratio` in phases/04-light-arm/design.md → Results.

### M13.2 Print ring parts

**Time** 15 min (+ print 9 h) · **Needs** FIL-01 ABS

#### Do

1. Print 7 × `LAR-08a_rim_segment.stl`, 1 × `LAR-08c_arm_segment.stl` (the 8th rim segment, with the upright socket), 1 × `LAR-08b_ring_motor_mount.stl`, 1 × `LAR-08e_cross_clamp.stl`, `LAR-08f_upright_bar.stl` and `LAR-08g_arm_bar.stl` (lying flat), 4 × `FRM-09c_protractor_segment.stl` (ring scale + lazy-Susan clamp, 80° each).

#### Verify

- [ ] Segments butt into a closed ring on the table (no gap > 0.5 mm).

#### Record

Tick the boxes; `make done id=M13.2`.

### M13.3 Lazy Susan, rim and belt

**Time** 1.25 h · **Needs** LAR-01 lazy Susan · LAR-03 belt · 4 × FRM-09c ring-scale clamps · 8 × M2 × 10 + washers · M2 × 12 + nuts + the 2 wide printed washers (TBL-07f) · TLS-09 CA glue · TLS-04 cutter

#### Do

1. Lazy Susan on the deck centre, its bottom plate inside the ring of 8 pilot holes (r 163). Ring-scale segments end to end from 20° to 340° (0° = +X, toward the camera; the gap is the M4 motor): each inner wall against the bottom plate's edge, its lip over the plate; 2 × M2 × 10 + washer into the deck pilots. The lazy Susan needs no screws of its own.
2. Rim segments + the arm segment on the top plate, closed ring: turn the ring so an arm-segment slot lands on a plate hole; M2 × 12 + wide printed washer + nut through every slot that lands on a hole; CA-glue the rest (the arm segment's whole underside).
3. CA-glue the GT2 belt teeth-out on the 6 mm band, its edges flush with the band's edges, ends butted, no gap; it ties the segments together.

#### Verify

- [ ] Count the belt teeth: equals `RIM_TEETH` ± 1.
- [ ] No tooth step at the joint (run a fingernail over it).
- [ ] Bottom plate can't slide or lift (push hard sideways).
- [ ] The 20° and 340° scale ends sit symmetric about the line deck centre → camera pillar (string line).

#### If a check fails

- Gap at the joint: cut a 1-tooth filler from spare belt.

#### Record

Tooth count in design.md.

### M13.4 Motor

**Time** 30 min · **Needs** LAR-02 motor · LAR-04 20T pulley · LAR-08b mount · 4 × M3 × 8 (FRM-07) · 2 × M2 × 12 + washers

#### Do

1. E-stop pressed. This is the bench motor from M08.3: unplug it from the SKR Pico X socket only now, mount it, then plug it back into X with its cable along the deck edge.
2. Motor on the mount plate (shaft down through the slot, 4 × M3 × 8); 20T pulley on the shaft, grub on the D flat, teeth level with the rim belt (its flanges pass above and below the band).
3. Mount at 0° (+X), base outside the lazy Susan, its two slots over the two deck pilots; slide it in until the pulley meshes the rim belt fully, then M2 × 12 + washer through each slot.

#### Verify

- [ ] Pulley teeth engage the rim belt across its full width; turning the ring by hand turns the motor, no skipped tooth.

#### If a check fails

- Skips under a light push: slide the mount 0.5 mm inward and re-tighten.

#### Record

Tick the boxes; `make done id=M13.4`.

### M13.5 Arm

**Time** 45 min · **Needs** LAR-08c arm segment (in the ring) · LAR-08f upright + LAR-08g arm bars · LAR-08e cross clamp · 3 × M2 × 16 · LSR-05 lamp body (stage 06, or a dummy)

#### Do

1. The upright stands in the arm segment's socket, 36 mm beside the lamp's beam line (so it never shades the sample).
2. Upright bar in the socket, M2 × 16 through the socket wall into its lower pilot. Cross clamp down the upright until its screw meets the upper pilot (M2 × 16). Arm bar through the clamp's side channel, parallel to the beam line, pointing outward, its inner pilot under the clamp's top screw (M2 × 16). The lamp's clamp takes the outer pilot (M18.1), so the beam centre passes through the zero point, 300 mm out, at 150 mm.

#### Verify

- [ ] Turning by hand 20 → 324°: no tight spot, no skipped tooth; the arm segment and upright never touch the motor plate.
- [ ] Lamp position: 300 ± 2 mm from the zero point, height 150 ± 2 mm.

#### Record

Commit.

## M14 · Light arm homes and repeats

M4 returns to the same spot every time (≤ 0.1°). · 0/4 steps done · ~2.2 h hands-on · ~1 wk

### M14.1 Home switch

**Time** 45 min · **Needs** LAR-05 TCST2103 · LAR-06 limit switch (3 wires attached) · 3 × 221-2401 (PWR-20; two splices + the blue cap) · flag on the arm

#### Do

1. Mount the TCST2103 so the arm flag cuts it at 20°: M2 × 8 + washer through one module hole into the nearest spare deck pilot (40 mm grid), double-sided tape under it (lead as in M10.2).
2. Limit switch (LAR-06) on the deck at 17° (3° past home, outside the 20–324° travel), lever toward the arm (double-sided tape). Find its wires with the meter: COM–NC beeps with the lever untouched and opens when pressed (black = COM, grey = NC, blue = NO on the units bought).
3. Press the e-stop, unplug the adapter. Splice the switch into the red run (e-stop NC 2 → MOT+ slot 1), so the length of its own leads doesn't matter: lay the run past the switch and cut it where both the black and the grey lead reach it with slack. Strip 11 mm on both cut ends and on the black and grey leads.
4. One 221-2401: red from the e-stop + black (COM). A second: grey (NC) + red on to the tray. Blue (NO) alone in the third. Tug each; tape the connectors to the deck beside the switch.
5. Check before power (adapter unplugged, e-stop released): continuity e-stop NC 2 → MOT+ beeps; press the lever: it opens (proves the switch is in the + line). Ω MOT+ to MOT−: > 10 kΩ or OL (T1).
6. Adapter in, release the e-stop.

#### Verify

- [ ] `opengonio send '?'` shows `Pn:X` with the flag in the slot.
- [ ] Pressing the lever drops SKR Pico POWER to 0 V and the hub prints `POWER 0`; releasing it brings both back (T6).

#### Record

T6 in `phases/01-power/test.csv`; `make done id=M14.1`.

### M14.2 Config and homing

**Time** 20 min · **Needs** `software/config/machine.yaml`

#### Do

1. Set `installed_phase: 4` and `M4.gear_ratio` (from M13.1).
2. `make test`
3. Power-cycle the SKR Pico (e-stop, then USB): `opengonio send '?'`.
4. `opengonio home` ten times.

#### Verify

- [ ] Tests pass.
- [ ] After power-up `?` shows `<Alarm` (must_home: nothing moves until homed); after homing `<Idle`.
- [ ] Home finishes 10/10; arm stops on the flag, never on the limit switch.

#### If a check fails

- Homes the wrong way: clear the X bit of `$23` (homing direction mask) in `tools/grblhal_settings.py`, `make build`, `bash scripts/controller.sh settings`.
- Still `<Alarm` after homing the installed axes: your grblHAL build keeps the startup lock until every configured axis is homed. Note the version (`$I`) in design.md, set `$22=11` (no init lock) in `tools/grblhal_settings.py`, `make build`, `bash scripts/controller.sh settings`: the software still refuses every move until it has homed and checked the position.

#### Record

10/10 in design.md.

### M14.3 Angle check

**Time** 20 min · **Needs** protractor scale FRM-09c

#### Do

1. `opengonio move M4=90`, read the scale; `M4=180`; `M4=270`.

#### Verify

- [ ] Each reading within ±0.5° of the command.

#### If a check fails

- Error grows with angle: wrong `gear_ratio`; ratio_new = ratio × commanded / read.

#### Record

Three readings in design.md.

### M14.4 Repeatability

**Time** 45 min · **Needs** LAR-09 laser + mirror · wall 2.0 m away

#### Do

1. Laser on the deck, small mirror taped to the arm, spot on a wall 2.0 m away (0.1° = 7 mm).
2. `opengonio repeat M4 --at 60 --away 30 --n 20`; type each spot offset (mm).
3. `opengonio repeat M4 --at 60 --home --n 10`

#### Verify

- [ ] Both print `"pass": true` (every spot ≤ 7.0 mm from the mark).

#### If a check fails

- Spread > 7 mm: pinion mesh (slide the mount in 0.5 mm), pulley grub tight on the motor flat, wobble in the lazy Susan.

#### Record

Both JSON summaries in phases/04-light-arm/design.md → Results; commit.

> **Safety:** Before touching a motor plug or a screw terminal: press the e-stop and unplug the adapter.

[Sources](../../REFERENCES.md): R1 · G10 · N15 · N47 · H2 · H11 · H16 · H17 · H18 · H26 · P42 · P43 · P44 · P58 · P61 · M1 · M2
