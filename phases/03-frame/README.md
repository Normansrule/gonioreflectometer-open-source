# 03 · Frame

<img src="../../docs/assets/steps/03.svg" width="100%" alt="Steps of stage 03">

<img src="../../docs/assets/axes.svg" width="100%" alt="Frame">

$22.45 · total so far $223.96 / $630

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/)

## M11 · Print and join the deck

Nine printed tiles bolted into one 600 mm deck; every mount already has its pilot hole. · 0/3 steps done · ~1.6 h hands-on · ~1 wk

### M11.1 Order frame parts

**Time** 20 min (+ shipping) · **Needs** `PARTS.md` → 03 · Frame

#### Do

1. Order every stage-03 part ticked `[x]`; set them `ordered` with `paid:`.

#### Verify

- [ ] Stage 03 has no `agreed` or `suggested` parts left.

#### Record

Commit `PARTS.md`.

### M11.2 Print the deck tiles

**Time** 30 min (+ print ≈ 55 h (9 × 6 h)) · **Needs** FIL-01 ABS (1.5 kg of it) · TLS-01 enclosed printer

#### Do

1. Print the 9 tiles `FRM-01a_deck_tile_SW.stl` … `FRM-01i_deck_tile_NE.stl` as exported: top face on the bed, no supports, 5 mm brim, door shut until cool.
2. Write each tile's name (SW … NE) on its underside as it comes off. Map: `phases/03-frame/design.md`.

#### Verify

- [ ] Each tile lies flat on the table: a sheet of paper won't slide under any corner.
- [ ] Calipers: every edge 200.0 ± 0.4 mm.

#### If a check fails

- Corner lifts: 8 mm brim, bed 105 °C, door shut until below 40 °C; reprint.
- Edges short: XY shrink compensation from M03.3 not set; reprint.

#### Record

Tick the boxes; `make done id=M11.2`.

### M11.3 Bolt the deck together

**Time** 45 min · **Needs** 9 deck tiles · 36 × M2 × 10 + nuts + washers (FRM-06) · TLS-03 hex key 1.5 mm · a flat table

#### Do

1. Tiles upside down (top face on the table, ribs up), in their places as seen from below: east and west swap, so E tiles lie on your left when N points away.
2. Butt neighbouring walls; M2 × 10 through each pair of seam holes (3 per edge), washer and nut on the other side. Finger-tight everywhere first, then tighten from the centre tile outward.
3. Turn the deck over, onto the table where it will live (+X, east, toward where the camera goes; leave 450 mm free beyond that edge for the outrigger).

#### Verify

- [ ] A straight edge across every seam: no step > 0.3 mm.
- [ ] Lift one corner 10 mm: the deck moves as one piece, no seam opens.

#### If a check fails

- Step at a seam: loosen its 3 bolts, press both skins flat on the table, tighten again.

#### Record

Photo `phases/03-frame/deck.jpg`; commit.

## M12 · Assemble the frame

Outrigger, camera pillar, scan post and boxes screwed into the deck's pilots. · 0/2 steps done · ~1.2 h hands-on · ~1 wk

### M12.1 Outrigger, camera pillar and scan post

**Time** 1 h (+ print 8 h) · **Needs** FRM-02a–d bars · 2 × FRM-09d saddles · 2 × FRM-09i couplers · FRM-09e post socket · FRM-09h camera pillar · FRM-09f end foot · 8 × M2 × 12 and 14 × M2 × 16 (FRM-06) · TLS-07 phone level app

#### Do

1. Print the bars `FRM-02a…d` (lying flat, as exported), 2 × `FRM-09d_bar_saddle.stl`, 2 × `FRM-09i_bar_coupler.stl` (standing), `FRM-09e_post_socket.stl`, `FRM-09f_end_foot.stl`, `FRM-09h_camera_pillar.stl`.
2. Saddles on their pilots in the east tile (x = 237 and 278, on the +X line): 4 × M2 × 12 each.
3. Outrigger: bars 1 and 2 butted inside a coupler, M2 × 16 through the coupler into each bar's pilots. Lay it in the saddles, inner end at x = 215, the far end on the end foot (standing on the table at x = 628). Every clamp's hole now lines up with a pilot in the bar: M2 × 16 through each saddle cheek and the end foot.
4. Camera pillar (FRM-09h) over the outrigger at its pilot (x = 391.8); post socket over the pilot at x = 674.4, M2 × 16 each. Scan post: bar 1 into the socket (M2 × 16), bar 2 on top through the second coupler. No tall post at the measuring camera: it would stand in the scan camera's view.

#### Verify

- [ ] Posts vertical: phone level app on two faces reads 90.0 ± 0.5°.
- [ ] Every screw found its pilot (none driven into plain plastic).
- [ ] Pillar and post centres 391.8 ± 1 and 674.4 ± 2 mm from the deck centre (tape); pillar's camera pilot at 150 ± 1 mm above the deck.
- [ ] Outrigger level end to end (phone level app ±0.5°).

#### If a check fails

- A screw misses its pilot by > 1 mm: that bar shrank; check the XY compensation (M03.3) and reprint it.
- Far end low: the end foot is 30 mm for the 24 mm deck + 6 mm saddle floor; shim it.

#### Record

Tick the boxes; `make done id=M12.1`.

### M12.2 Mount the plate and tray

**Time** 15 min · **Needs** power plate (with jack and e-stop box) · controller tray · 8 × M2 × 12 (FRM-06)

#### Do

1. Power plate: 4 × M2 × 12 through its counterbored holes into the SE tile's pilots (centre 220, −220), jack socket toward the +X edge. Lift the e-stop box off its tape to reach the two holes under it, then press it back.
2. Controller tray: 4 × M2 × 12 through its corner bosses into the NW tile's pilots (centre −200, 220).
3. Red and black runs along the deck edge to MOT+ / MOT− on the tray; take the red run up the +X side, past the ring at about 17° (the limit switch is spliced into it there in M14.1), and leave 10 cm of slack there.

#### Verify

- [ ] `opengonio status` still answers; e-stop still cuts (repeat T5).

#### Record

Photo `phases/03-frame/frame.jpg`; commit.

[Sources](../../REFERENCES.md): R1 · G10 · G38 · H30 · H38 · F7
