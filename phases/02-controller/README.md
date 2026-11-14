# 02 · Controller and buttons

<img src="../../docs/assets/steps/02.svg" width="100%" alt="Steps of stage 02">

$70.84 · total so far $201.51 / $630

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/) · [Tests](test.csv)

## M07 · Order controller parts

SKR Pico, keypads, cables, the motor 5-pack and the endstops on the bench; your ESP32-S3 as the hub. · 0/2 steps done · ~45 min hands-on · ~2 wk

### M07.1 Order

**Time** 30 min (+ shipping 3–10 days) · **Needs** `PARTS.md` → 02 · Controller and buttons

#### Do

1. Order every stage-02 part ticked `[x]` (all on Amazon). CTL-02 is your own ESP32-S3: already `have`.
2. Also order LAR-02 (the 17HS4401 5-pack) and LAR-05 (the endstop 6-pack) from stage 04 for the bench tests.
3. Set them `status: ordered` with `paid:` in `PARTS.md`.

#### Verify

- [ ] Stage 02 has no `agreed` or `suggested` parts left.

#### If a check fails

- SKR Pico sold out: its *Must meet* line names what a replacement needs (grblHAL board map, 4 × TMC2209 UART, USB-C); a FluidNC ESP32 board also works with `controller.firmware: fluidnc` and `firmware/fluidnc/config.yaml`.

#### Record

Commit the dated BOM.

### M07.2 Unpack and check

**Time** 15 min · **Needs** CTL parts · PWR-10 opto module · TLS-06 calipers

#### Do

1. SKR Pico: BOOT jumper cap in the box (or on the board). ESP32-S3: pins soldered, two USB-C connectors (USB, UART). Keypads: 5-wire tails intact. Jumpers: male–female.
2. Measure the ESP32-S3 board (L × W). If it differs from `ESP` in `tools/cad/parts.py` by > 1 mm, change it and `make parts` before printing the tray.
3. Find each keypad's common pin: meter on continuity, one probe on a tail pin, press keys; the common pin beeps with every key.

#### Verify

- [ ] Common pin found on both keypads (write it on the tail with a marker).
- [ ] ESP32-S3 size within 1 mm of the CAD (or the CAD updated).

#### If a check fails

- No pin beeps with all keys: tail not fully seated in the meter probe; use a jumper's male end as a probe tip.
- No BOOT jumper cap: any 2.54 mm jumper cap; or hold a female–female jumper across the two BOOT pins while pressing RESET.

#### Record

`status: have` per arrived part in `PARTS.md`; commit.

## M08 · One motor turns from the laptop

Laptop → USB-C → SKR Pico (grblHAL) → motor works on the bench. · 0/3 steps done · ~1 h hands-on · ~1 wk

### M08.1 USB-C into Ubuntu

**Time** 15 min · **Needs** CTL-01 SKR Pico · CTL-03 USB-C cable · Windows PowerShell (admin)

#### Do

1. Plug the SKR Pico into the laptop by USB-C (no motor power needed: its schematic feeds USB 5 V into the logic supply through a diode; if no LED lights, check the USB-C cable carries data; the board gets motor power only in M08.3).
2. PowerShell (admin): `usbipd list` (the board shows as 2e8a:…); `usbipd bind --busid <busid>`; `usbipd attach --wsl --busid <busid>`.
3. Ubuntu: `sudo usermod -aG dialout $USER && newgrp dialout`; `ls /dev/ttyACM*`.

#### Verify

- [ ] The board is listed (as RP2 Boot or a serial port).

#### If a check fails

- Not listed in `usbipd list`: charge-only cable; swap it.
- Vanishes after replug or flashing: run `usbipd attach` again (needed after every re-enumeration).

#### Record

Tick the boxes; `make done id=M08.1`.

### M08.2 Flash grblHAL

**Time** 25 min · **Needs** M08.1 · BOOT jumper cap

#### Do

1. `bash scripts/controller.sh flash` and follow its four steps: build the .uf2 in the grblHAL Web Builder (board BTT SKR Pico 1.0, 4 axes), BOOT jumper on, RESET, copy the .uf2 onto `RPI-RP2`, jumper off, RESET.
2. `bash scripts/controller.sh settings` (sends `firmware/grblhal/settings.txt`, then prints `$$`).
3. `bash scripts/controller.sh pins`: note the port numbers of HE, HB and FAN1; set `lights.white.output` (HE) and `lights.multispectral.output` (HB) in `software/config/machine.yaml` if they differ from 4 and 3.

#### Verify

- [ ] `opengonio send '$I'` lists grblHAL and `BTT SKR Pico 1.0`.
- [ ] `opengonio send '?'` prints a line starting `<Alarm|MPos:` (homing required) or `<Idle|MPos:`.
- [ ] `$$` shows `$22=15` and `$10=17`.

#### If a check fails

- `error:` on a settings line: that number doesn't exist in your build (an option was left out in the Web Builder); rebuild with 4 axes and the Trinamic driver, or remove the line and note it in design.md.
- No `RPI-RP2` drive: BOOT jumper not on the right pins, or RESET not pressed after fitting it.

#### Record

C1 in `phases/02-controller/test.csv`.

### M08.3 Bench motor

**Time** 20 min · **Needs** LAR-02 motor · power wired (M05) · 2 × 10 cm PWR-15 offcuts (red, black) · tape flag on the shaft

#### Do

1. E-stop pressed, adapter unplugged. 10 cm red offcut from MOT+ slot 3 → SKR Pico POWER `+`, 10 cm black from MOT− slot 3 → POWER `−` (screw terminal). Motor → the X socket. Adapter in, release the e-stop.
2. `opengonio send 'M122 I'` (drivers configured now that motor power is on).
3. `opengonio send '$20=0' '$X' 'G91' 'G1 X10 F600' 'G1 X-10 F600' 'G90'` (soft limits off and `$X` unlock: unhomed bench test only).
4. `opengonio send '$X' 'G91' 'G1 X360 F300' 'G90'`; press the e-stop halfway.
5. `opengonio send '$20=1'` (soft limits back on).

#### Verify

- [ ] Shaft turns, then returns to the tape mark.
- [ ] E-stop stops it at once; after release `opengonio send '?'` shows `Alarm` or a lost position (must re-home).

#### If a check fails

- Motor buzzes, no turn: coil pairs crossed. The SKR Pico drives one coil on plug pins 1 + 4 (2B, 2A) and the other on pins 2 + 3 (1B, 1A) (maker schematic). Motor plugged in, meter on Ω at the 4-pin plug's back: 1–4 and 2–3 must each read a few ohms. If not, lift contact latches with a pin and move contacts until they do.
- Wrong direction: `opengonio send '$3=1'` (direction invert mask: X 1, Y 2, Z 4, A 8) and add `$3` to `tools/grblhal_settings.py`.
- `error:` on G1: the board is still locked or soft limits are on; `$20=0` and `$X` must come first in the same send line.

#### Record

Note the result under C7 in `test.csv`.

## M09 · Keypads work with the laptop

Membrane keys on the ESP32-S3 hub drive the machine. · 0/3 steps done · ~1.1 h hands-on · ~1 wk

### M09.1 Hub firmware

**Time** 15 min · **Needs** CTL-02 ESP32-S3 · CTL-03 USB-C cable

#### Do

1. Plug the ESP32-S3's **USB** connector (not UART) into the laptop; WSL: `usbipd attach` it too (303a:…).
2. Read the module can: N8R8 / N16R8 → `bash scripts/hub.sh flash oct`; otherwise `bash scripts/hub.sh flash plain`.
3. Press RST, then `bash scripts/hub.sh`.

#### Verify

- [ ] `hub.sh` prints `PONG OpenGonio-hub 4`.

#### If a check fails

- Flash can't connect: hold BOOT, tap RST, release BOOT (download mode), run it again.
- `mpremote` can't find it: `ls /dev/ttyACM*` empty → attach with usbipd again.

#### Record

C4 (PING part) in `test.csv`.

### M09.2 Wire the keypads

**Time** 30 min · **Needs** 2 × CTL-05 keypads · CTL-07 jumpers · 1 × WAGO 221-413 (PWR-20) · README → Wiring → 6

#### Do

1. Keypad A: male jumper ends into its tail; keys 1–4 → header J1-4 (GPIO 4) HOME, J1-5 (5) START, J1-6 (6) STOP, J1-7 (7) LIGHT.
2. Keypad B: key 1 → J1-8 (GPIO 15) NEXT; key 2 → J1-9 (GPIO 16) PAUSE.
3. Both commons: cut the female end off each common jumper, strip 11 mm, fold double, into a 3-way lever connector; a third jumper (male end cut, stripped, folded) from it to J1-22 (GND).
4. `python -m serial.tools.miniterm /dev/ttyACM1 115200` (the hub's port), press each key.

#### Verify

- [ ] Each press prints its own `BTN <NAME>` exactly once.

#### If a check fails

- Nothing on any key: common on a key pin; redo M07.2.
- Two lines per press: the firmware debounces 30 ms — reseat the jumper on that pin.

#### Record

C4 in `test.csv`.

### M09.3 Panel drives the motor

**Time** 20 min · **Needs** bench motor on X

#### Do

1. `opengonio panel`
2. Press HOME, LIGHT, NEXT, START, PAUSE, START, then STOP.

#### Verify

- [ ] Each press prints its action in the panel log.
- [ ] PAUSE stops the plan after the pose in progress; START carries on from the next pose.

#### If a check fails

- A key does nothing: wrong GPIO; check the pin table.

#### Record

C5, C6 in `test.csv`.

## M10 · Controller box closed

Boards on the tray; homing, e-stop sense and heat tested. · 0/4 steps done · ~1.7 h hands-on · ~1 wk

### M10.1 Print and mount

**Time** 30 min (+ print 4 h) · **Needs** CTL-10 prints · 4 × M2 × 8 + washers · PWR-10 opto module · TLS-09 double-sided foam tape

#### Do

1. Measure the ESP32-S3 board first: the tray's frame fits Espressif's 62.7 × 25.4 mm board. A clone that is longer (up to ~69 × 26): set `ESP` in `tools/cad/parts.py`, `make parts`. Then print `CTL-10a_button_panel.stl`, `CTL-10b_controller_tray.stl`.
2. Drive M2 × 8 into the 4 SKR Pico standoffs once; mount the board (holes 58 × 49 mm), USB-C toward the tray edge, a washer under each head.
3. ESP32-S3 (flashed in M09.1): a square of foam tape on the pedestal, then the board upside down (module can on the tape, header pins up), USB end at the opening.
4. Opto module (PWR-10) into the long frame, double-sided tape under it, terminals up. The short frame is for the LED driver (M18.1). Keypads: peel and stick into the panel recesses, tails through the slots.
5. Lever connectors: MOT+ and MOT− (from M05.2) and a third 221-413 for the keypad GND (M09) slide into the pockets along the tray's south edge, wire openings out, levers up. The fourth pocket is spare.

#### Verify

- [ ] SKR Pico sits flat on all four standoffs; its USB-C is reachable.
- [ ] The ESP32-S3 doesn't lift when you unplug a jumper; its USB connector takes a plug.

#### If a check fails

- Holes off: measure your board's hole spacing, set `SKR_HOLES` in `tools/cad/parts.py` (CTL-10b), `make parts`, reprint.
- Module doesn't fit its frame: measure it, set `OPTO_MOD` / `LED_DRV` / `ESP` in `tools/cad/parts.py`, `make parts`, reprint the tray.

#### Record

Tick the boxes; `make done id=M10.1`.

### M10.2 Flags and homing

**Time** 30 min · **Needs** LAR-05 endstop · CTL-06: 3 double-ended XH leads + two 3-pin housings · a card to block it

#### Do

1. Endstop lead: 3 CTL-06 leads. Board end: one 3-pin XH housing, pin 1 signal, 2 GND, 3 5 V (SKR Pico pin diagram) into X-STOP. Module end: each wire onto the module pin with the matching printed label (S/OUT, G/GND, V/VCC; its pin order may differ: use single housings or a 3-pin housing in that order). Meter the module's V pin to STOP pin 3 before plugging in.
2. `opengonio send '?'` with the slot open, then blocked.
3. Motor on X, endstop flag taped to the shaft: `opengonio send '$HX'`.

#### Verify

- [ ] Blocked shows `Pn:X`; open shows no `Pn`.
- [ ] `$HX` turns until the flag cuts the slot and stops; `?` shows MPos X = 0 (`opengonio status` reports M4 = 20).

#### If a check fails

- Never stops / `Pn:X` while open: inverted input; `opengonio send '$5=1'` (X bit) and add `$5` to `tools/grblhal_settings.py`.
- Module LED never lights: lead on the wrong module pins. Match each wire to the module's printed label (S/OUT, G/GND, V/VCC); meter the module's V pin to STOP pin 3 (5 V) before plugging in.

#### Record

C2, C3 in `test.csv`.

### M10.3 E-stop sense with the opto module

**Time** 30 min · **Needs** PWR-10 opto module (24 V version) · 2 × short PWR-15 offcuts (red, black) · M-F jumpers

#### Do

1. E-stop pressed, adapter unplugged. Short red offcut from MOT+ slot 2 → the opto module's IN+ screw; short black from MOT− slot 2 → IN−. 8 mm under the module screws, 11 mm in the lever connectors.
2. Output side: module VCC ← ESP32-S3 J1-1 (3V3), GND ← J3-21 (GND), OUT → J1-10 (GPIO 17) (female jumper ends on the hub pins; bare ends under the module screws, or female ends on its pins).
3. Motor holding (`opengonio home`, then wait): measure SKR Pico POWER (T4), and DC volts from jack `+` to SKR Pico POWER `+` (T12, the drop along the wires and switches). Press the e-stop: watch the hub output and the panel; release; `opengonio home`.

#### Verify

- [ ] T4 ≥ 22.5 V; T12 ≤ 0.3 V.
- [ ] Module input LED on with motor power on; hub prints `POWER 0` on e-stop, `POWER 1` after release, 20 times out of 20 (T7); moves refused until HOME (C7).

#### If a check fails

- Reads the wrong way round (`POWER 1` with the e-stop pressed): your module drives OUT high when powered; set `SENSE_ACTIVE_LOW = False` in `firmware/hub/main.py`, `bash scripts/hub.sh`.
- Never changes: input `+` / `−` swapped, or OUT not on GPIO 17; the module's input LED must light with motor power on.

#### Record

T4, T7, T12 in `phases/01-power/test.csv`; C7 in `phases/02-controller/test.csv`.

### M10.4 Heat

**Time** 10 min (+ 30 min hold) · **Needs** TLS-05 temperature probe

#### Do

1. `opengonio home`, motor holding at 0.8 A run current for 30 min, lid on; probe on the SKR Pico driver heatsink.

#### Verify

- [ ] Driver area ≤ 80 °C (C8).

#### If a check fails

- Hotter: fit the optional CTL-08 fan on FAN1 (`M62 P2`; BTT advise a fan above 0.8 A), or lower `$140` to 700 mA.

#### Record

C8 in `test.csv`; commit `make publish m="M10 controller done"`.

> **Safety:** Never plug or unplug motors with 24 V on.

[Sources](../../REFERENCES.md): R83 · R84 · R85 · R86 · N48 · H1 · H2 · H4 · H5 · H6 · H7 · H8 · H23 · H24 · H25 · H43 · H54 · P22 · C11 · C12 · C13
