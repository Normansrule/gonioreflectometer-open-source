# Tools and joins

Nothing is assumed owned except a laptop: the tools are rows `TLS-01`–`TLS-10` with prices, a separate total from the machine's (printer $279 of it; a print service or makerspace replaces it). Prints are black ABS, which needs an enclosed printer and a ventilated room. The parts were picked so nothing needs a soldering iron, drill, saw, crimper or heat-set inserts. Mark them `have` / `ordered` in [PARTS.md]({{REPO}}/PARTS.md).

| Join | How, without solder or drilling | Parts |
|---|---|---|
| Wire to wire | strip 11 mm, lever connector (thin jumper wire: fold the stripped end double) | PWR-20 [P47]({{REPO}}/REFERENCES.md) |
| Wire to terminal | stripped, twisted wire under the screw (2 wires may share one) | PWR-30 jack, PWR-28 e-stop, SKR Pico POWER |
| Wire to a pin | jumper wire (cut one in half for pin → bare wire); XH leads crimped on both ends for endstops; PH→XH cables for motors | CTL-07 [C10]({{REPO}}/REFERENCES.md), CTL-06, CTL-11 [C11]({{REPO}}/REFERENCES.md) |
| Small electronics | modules with screw terminals (opto PWR-10, MOSFET MSK-03) or wire leads (LED driver LSR-02, into screw terminals and lever connectors), held in printed frames with double-sided tape; no breadboard, no loose chips | PWR-10, MSK-03, LSR-02 |
| Boards | SKR Pico (connectors fitted), ESP32-S3 dev board and Pi Zero 2 WH with headers soldered | CTL-01 [C12]({{REPO}}/REFERENCES.md), CTL-02 [C13]({{REPO}}/REFERENCES.md), STA-01 |
| COB LED | sits in a solderless holder with poke-in wire terminals; the lamp cap clamps it | LSR-06 [L23]({{REPO}}/REFERENCES.md) |
| Printed part to the deck | M2 × 12 into the pilot boss already printed at that spot ([deck map]({{REPO}}/phases/03-frame/deck-map.svg)); spare pilots every 40 mm | FRM-06 |
| Deck tile to tile | M2 × 10 + nut through the shared walls, 3 per edge | FRM-06 |
| Screw into a printed part | M2 self-taps into 1.7 mm pilots (`M2_TAP`, set from the coupon); one screw size everywhere. Only the motor faces take M3 (FRM-07) | FRM-06 |
| Bar to clamp | printed 20 × 20 bars with M2 pilots at every clamp station; couplers join the halves | FRM-02, FRM-09i |
| Axles | M8 bolts instead of shafts: the table drum turns on two 608s around a fixed bolt (one nut clamps the inner races); the tilt cradle turns on two stub bolts; spin is direct drive. No shaft to cut, no flat to file | TBL-05, TLT-05, SPN-01 |

Trade-off: the solderless power path has no reverse-polarity MOSFET or surge diode. The jack's screws are marked + / −, and step M04.2 checks the adapter's polarity at the jack with the meter (M06.1 again at MOT+ / MOT−) before the motor board is connected; the SKR Pico has its own input fuse and capacitors. Short-circuit protection comes from the adapter itself (listing), not from anything built here.
