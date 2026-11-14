# Carrier board (future option)

Status: **reference specification, not designed yet.** Nets follow the module build: BTT SKR Pico V1.0 + ESP32-S3-DevKitC-1, pin by pin in [README → Wiring](../README.md#wiring) (source `docs/wiring.yaml`). The machine is built today from modules, jumper wires and screw terminals (no soldering). This page fixes what a printed circuit board (PCB) version must do, so it can be designed later without changing the machine, the firmware or the wiring at the motors.

## Purpose

One board on the controller tray that replaces the loose modules and most jumpers:

| Today (modules, stage) | On the board |
|---|---|
| PC817 opto module PWR-10 + 5 jumpers (02) | PC817 + 10 kΩ, motion-power sense to ESP32-S3 GPIO 17 |
| LED driver LSR-02 (NLDD-350HW, wire leads) taped in a printed frame + lever connectors (06) | footprint for the pin version MEAN WELL NLDD-350H (2.54 mm pins, same circuit) |
| Two 4-channel MOSFET modules MSK-03 (10, optional, BLOCKED) | footprints only until a reviewed colour-LED driver exists |
| Keypad, OLED, sensor and status-screen jumpers to the ESP32-S3, 3V3 / GND lever connectors for the add-ons (02, 10, 15) | keyed headers; keypad commons and add-on 3V3 / GND joined on the board (no lever connectors); 8-pin header for the status screen (SCK 42, MOSI 41, DC 18, CS 38) |
| Nothing (trade-off in stage 01) | reverse-polarity MOSFET, transient-voltage-suppression (TVS) diode, bulk capacitor |
| INA219 power monitor BAT-05 + hub GND jumper (17, battery upgrade) | INA219 + 0.1 Ω shunt between TB1 `+` and the e-stop line, on I2C0 at 0x40; ground shared on the board |

## Rules

- The builder still solders nothing: order the board **assembled** (surface-mount and through-hole parts fitted by the maker). The ESP32-S3-DevKitC-1 plugs into two 22-pin sockets; every cable lands on a screw terminal or a keyed header.
- Same pins and nets as the module build, so the firmware (`firmware/hub/main.py`, `firmware/grblhal/settings.txt`) needs no change except `SENSE_ACTIVE_LOW` if the sense polarity differs.
- Fits the controller tray's module area (about 90 × 70 mm, tray local x 5–95, y −25–60); 4 × M2 holes (Ø 2.4 mm) for M2 × 8 into tray pilots added in `tools/cad/parts.py` with the board.
- 2 layers, 1.6 mm, 1 oz copper; 24 V traces ≥ 0.8 mm; parts from Digi-Key.
- KiCad (open source) project in this folder: `opengonio-carrier.kicad_pro`, schematic, layout, Gerbers, bill of materials and a STEP model for `cad/`.

## Netlist

Board terminals are TB1–TB4; J1-n / J3-n are ESP32-S3-DevKitC-1 header pins.

Nets as in [01 power](../phases/01-power/design.md) and [02 controller](../phases/02-controller/design.md).

| Net | From | To | Part on the board |
|---|---|---|---|
| MOTION | TB1 (2-way 5.08 mm terminal: red wire after the e-stop and over-travel switch) | reverse-polarity P-MOSFET → V24 | P-MOSFET ≥ 40 V, ≥ 5 A; SMBJ28A TVS; 100 µF 50 V |
| GND | TB1 black wire | board ground, SKR Pico POWER GND via TB2 | — |
| V24 → SKR Pico | TB2 (2-way 5.08 mm terminal) | SKR Pico POWER 12/24V / GND | 5 A traces |
| SENSE | V24 → 10 kΩ → PC817 LED → GND | PC817 transistor → ESP32-S3 GPIO 17 (J1-10; pull-up in the ESP32-S3), emitter → GND | PC817 (DIP-4 or SMD) |
| LAMP_IN | SKR Pico HE 12/24V → NLDD +Vin; NLDD −Vin → TB3 | TB3 (2-way terminal) → SKR Pico HE IO23 (switched −, `M62 P4`) | NLDD-350H footprint |
| LAMP_OUT | NLDD +Vo / −Vo | TB4 (2-way terminal) → lamp leads | — |
| BAND0–7 | ESP32-S3 GPIO 8–14, 21 | reserved: no parts until the colour-LED driver is reviewed (stage 10 BLOCKED) | — |
| KEY_A, KEY_B | ESP32-S3 GPIO 4–7 (J1-4…7), 15, 16 (J1-8, 9), GND | 2 × 5-pin 2.54 mm headers (keypad tails plug in), commons to ground on the board | — |
| I2C0 | ESP32-S3 GPIO 1 SDA (J3-4), GPIO 2 SCL (J3-5), 3V3, GND | 4-pin header (OLED) + 4-pin JST-SH (AS7341 sensor) on the same bus | — |
| UART1 + HUB_5V | ESP32-S3 GPIO 47 TX (J3-17), GPIO 48 RX (J3-16), GND (J3-1), 5V (J1-21) | 4-pin header (Pi Zero station, stage 15: Pi TX, RX, GND, 5V) | — |
| USB | ESP32-S3 USB connector | edge of the board, reachable from the tray side | — |

The SKR Pico stays a separate board: its motor, endstop and USB-C connectors are used as they are.

## Done when

- `make cad` places the board on the tray with no clash; the PC817 module, LED-driver frame and jumper rows are gone from stages 02, 06 and 10.
- Stage 02 tests C1–C8 and power tests T4, T7 pass on the board; the stage-01 polarity test still passes, and reversed input (bench test, 24 V through a 1 kΩ resistor) draws < 1 mA.
- The board's cost (assembled, 5 pieces) is listed in a BOM row with a Digi-Key or fab link.
