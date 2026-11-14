# 01 · Power

<img src="../../docs/assets/steps/01.svg" width="100%" alt="Steps of stage 01">

<img src="../../docs/assets/power-flow.svg" width="100%" alt="Power">

$66.71 · total so far $130.67 / $630

[Design](design.md) · [Research](research.md) · [Parts list](bom.csv) · [3D files](3d/) · [Tests](test.csv)

## M04 · Order and check power parts

Wall adapter, e-stop box, wire and lever connectors on the bench, each checked; the power plate printed. · 0/3 steps done · ~50 min hands-on · ~2 wk

### M04.1 Order

**Time** 20 min (+ shipping 3–10 days) · **Needs** `PARTS.md` → 01 · Power · FRM-06 screws (03 · Frame) · `PARTS.md` → 00 · Tools

#### Do

1. Order every stage-01 part ticked `[x]` (status `agreed`), using its link.
2. Also order LAR-06 (the limit switch, stage 04) now; it goes in the same + line in M14.1.
3. Tools: order the TLS rows (00 · Plan; their own total, not in the machine total): multimeter (TLS-05) and wire stripper (TLS-04) are needed now; the printer and ABS were ordered in M03.1.
4. In `PARTS.md` set each ordered part to `status: ordered` and fill `paid:`.

#### Verify

- [ ] Stage 01 in `PARTS.md` has no `agreed` or `suggested` parts left; *Paid so far* went up.
- [ ] Tools TLS-02 to TLS-06 are `have` or `ordered`.

#### If a check fails

- Part out of stock: its *Must meet* line says what a substitute needs (adapter: regulated 24 V ≥ 3 A with short-circuit protection and a screw-terminal jack; e-stop: latching, NC rated for DC at ≥ 24 V / 3 A where the listing gives a DC rating); set `swap` + `note:`, or add one with `python tools/new.py part …`.

#### Record

Commit the dated BOM.

### M04.2 Check parts

**Time** 20 min · **Needs** PWR-30 adapter + jack · PWR-28 e-stop box · TLS-05 multimeter · calipers (TLS-06)

#### Do

1. E-stop: take the box lid off. Meter on continuity: find the NC pair (beeps with the button released, opens when it is pressed). On the BAOMAIN this is terminals 1 and 2; 3 and 4 are NO.
2. Adapter: round plug into the jack, nothing else on the jack. Plug the adapter into the wall. DC volts, red probe on the jack's `+` screw, black on `−`. Unplug it again.
3. Measure the jack (L × W × H) and the e-stop box (L × W). If either differs from `JACK` / `ESTOP_BOX` in `tools/cad/parts.py` by more than 1 mm, change it there and run `make parts` before printing.

#### Verify

- [ ] Adapter at the jack +23.0 to +25.0 V (a plus sign).
- [ ] E-stop NC pair found and written on its box lid.
- [ ] Jack and e-stop box within 1 mm of the CAD values (or the CAD updated).

#### If a check fails

- Reads about −24 V: the jack's + / − marks are the other way round from the plug; use the screws as measured and mark them on the jack with a pen.
- Reads 0 V: adapter not in the wall or the plug not fully in the jack.
- Wrong part: return it now; don't substitute ratings (adapter 24 V ≥ 3 A; e-stop and limit switch NC rated ≥ 3 A; neither listing gives a 24 V DC figure, so T5 and T6 are the check).

#### Record

`status: have` per part in `PARTS.md` as it arrives; measured sizes in design.md; commit.

### M04.3 Print the power plate

**Time** 10 min (+ print 1.5 h) · **Needs** FIL-01 ABS · TLS-01 enclosed printer

#### Do

1. Print `phases/01-power/3d/PWR-18_power_plate.stl` flat: ABS (settings from M03.3, brim on), 0.2 mm, 4 walls, 30 % infill.

#### Verify

- [ ] The jack drops between its two frame walls without forcing; the e-stop box sits inside its rim.

#### If a check fails

- Too tight: scale the plate XY by +1 % in the slicer and reprint (no filing).

#### Record

Tick the boxes; `make done id=M04.3`.

## M05 · Wire the power

Jack and e-stop wired with screw terminals and lever connectors only; nothing soldered; adapter unplugged throughout. · 0/3 steps done · ~50 min hands-on · ~1 wk

### M05.1 Plate hardware

**Time** 15 min · **Needs** PWR-18 power plate · PWR-30 jack · PWR-28 e-stop box · TLS-09 double-sided tape

#### Do

1. Jack into its frame on the plate, round socket toward the +X edge, screws toward the e-stop.
2. E-stop box into its rim on double-sided tape, button up. Lid off for wiring.

#### Verify

- [ ] Twisting each part by hand: nothing rotates or lifts.
- [ ] The adapter's round plug goes into the jack from the +X edge.

#### Record

Tick the boxes; `make done id=M05.1`.

### M05.2 Main wiring

**Time** 30 min · **Needs** PWR-20 lever connectors (2 × 221-413) · PWR-15 18 AWG (1.5 m of each colour) · TLS-04 stripper · TLS-02 flat screwdriver · README → Wiring → 1, 2 (or `docs/wiring.html`)

#### Do

1. Adapter **unplugged** from the wall, round plug in the jack. E-stop pressed.
2. Cut list (measure your own route along the deck edge first): red 10 cm (jack → NC 1) and one run NC 2 → tray (≈ 1 m); black one run jack → tray (≈ 1 m). Keep the rest: 10 cm offcuts for M08.3 and M10.3, 15 cm leads for the lamp (M18.1).
3. Jack `+` → red wire → e-stop NC terminal 1. Strip 8 mm, twist, under either gap of the terminal screw, tighten, tug.
4. E-stop NC terminal 2 → red wire (the whole run to the tray) → a 3-way lever connector: MOT+, slot 1. Mark it with tape. (M14.1 puts the limit switch in place of this wire.)
5. Jack `−` → black wire (the whole run to the tray) → a second 3-way lever connector: MOT−, slot 1. Mark it.
6. Tug every wire: none slips out. Lid back on the e-stop box.

#### Verify

- [ ] Continuity: jack `+` to MOT+ beeps with the e-stop released; pressing the e-stop opens it.
- [ ] Continuity: jack `−` to MOT− beeps.

#### If a check fails

- No beep through the e-stop: you used the NO contact; move the wires to the NC pair found in M04.2.
- Wire pulls out: strip longer (11 mm in lever connectors), twist, re-close the lever.

#### Record

Tick each row of README → Wiring → 1. Tick the boxes; `make done id=M05.2`.

### M05.3 Checks with power off

**Time** 5 min · **Needs** TLS-05 multimeter · adapter unplugged · e-stop released

#### Do

1. Ω range: MOT+ to MOT− (T1), both probe directions.

#### Verify

- [ ] T1 > 10 kΩ (or OL) both ways.

#### If a check fails

- T1 low: a stray strand bridges + and − at the jack or the e-stop terminals; re-strip and re-tighten.

#### Record

T1 in `phases/01-power/test.csv` (date, value, PASS/FAIL).

## M06 · First power-on

24 V at MOT+ / MOT− with the right polarity, cut by the e-stop. · 0/2 steps done · ~50 min hands-on · ~1 wk

### M06.1 Voltage and polarity

**Time** 10 min · **Needs** PWR-30 adapter · TLS-05 multimeter · MOT+ / MOT− connectors free (no motor board)

#### Do

1. E-stop pressed. Adapter into the wall.
2. Release the e-stop. DC V: black probe in a free slot of MOT−, red probe in a free slot of MOT+ (T3).

#### Verify

- [ ] T3 = +23.0 to +25.0 V (a plus sign: polarity right).
- [ ] Nothing warm after 1 min.

#### If a check fails

- Reads negative: + and − swapped at the jack; unplug the adapter, then swap the two wires there.
- Reads 0 V: e-stop still pressed, wired to NO, or the plug not in the jack.

#### Record

T3 in `test.csv`.

### M06.2 E-stop and heat

**Time** 40 min (+ 30 min on, watched) · **Needs** TLS-05 multimeter + temperature probe · optional: the SKR Pico with one motor holding, from M08

#### Do

1. Press the e-stop; read MOT+ to MOT− after 1 s (T5). Release.
2. 30 min on (with the SKR Pico + one motor holding if you have them); then the temperature of the adapter case and each terminal (T9).
3. Press the e-stop; pull the adapter out of the wall.

#### Verify

- [ ] T5 < 1 V within 1 s.
- [ ] T9 every point ≤ 45 °C.

#### If a check fails

- Stays at 24 V on e-stop: NC / NO swapped, or a wire bypasses the e-stop.
- A terminal hot: loose screw or a few strands only; unplug, re-strip, re-tighten.

#### Record

T5, T9 in `test.csv`; label the plate *24 V · press the e-stop and unplug before touching a terminal*; commit.

> **Safety:** Only 24 V inside the machine: the wall adapter stays outside it. Before touching any screw terminal: press the e-stop and pull the adapter out of the wall. Wire everything with the adapter unplugged; it goes into the wall last.

[Sources](../../REFERENCES.md): N48 · N49 · N51 · H9 · H43 · P20 · P47 · P59 · P60 · P61 · P62
