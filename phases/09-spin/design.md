# 09 · Design

- **Direct drive:** the platter (SPN-07a) sits on the 5 mm D-shaft of a pancake NEMA 17 (SPN-01, 21.5 mm body) held face-up under the tilt cradle floor; an M2 × 8 into a captive M2 nut clamps the flat. No belt, pulley, shaft or bearings.
- TMC2209 at 1/64 microstep: 0.028° per step (same steps per degree as a 4 : 1 belt at 1/16). Load is only the platter and the sample.
- Platter top = tilt axis = zero point (set with the grub height in M25.2); the cradle end blocks stand 10 mm higher (nut traps). r 42 clears them.
- Home flag (TBL-07b) on the platter rim at −180°, endstop on the cradle, lead to SKR Pico E0-STOP (signal, GND, 5 V; the A limit in grblHAL) (M27.1).
- Platter takes the stage-11 scan risers (M2 self-tap holes on r 15).

Cable: the pancake has bare leads (no plug). A spare 5-pack cable, its 6-pin plug cut off, joins them with 3 × WAGO 221-412 + 1 × 221-415: coil pair 1 → the wires of plug pins 1 + 4, pair 2 → pins 2 + 3 (the SKR Pico schematic); the XH plug goes into the SKR Pico E socket (M27.1, [README → Wiring → 3](../../README.md#3--skr-pico-motors)).

Fasteners: M3 × 8 × 4 (motor face, the only M3), M2 × 8 × 2 (flag, self-tap), M2 × 8 + M2 nut (shaft clamp).

## 3D parts

| Part | Source |
|---|---|
| Spin platter (SPN-07a) | `tools/cad/parts.py` (`SPIN`) |
| NEMA 17 pancake 17HS08-1004S | [product](https://www.omc-stepperonline.com/hybrid-stepper-motor/nema-17-bipolar-18deg-13ncm-184ozin-1a-35v-42x42x20mm-4-wires-17hs08-1004s.html) [P48] |

## Results

(fill in)
