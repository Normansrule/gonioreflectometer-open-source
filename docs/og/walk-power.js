/* Power walkthrough (docs/power.html): wires of docs/wiring.yaml drawn as the parts sit on the bench, read by og/walk.js.
   Wire and note text come from window.WIRING (docs/wiring-guide.js, generated); only titles, drawing and checks live here.
   tools/check.py fails if a from/to below is no longer a row in docs/wiring.yaml.
   SPDX-License-Identifier: GPL-3.0-or-later */
window.WALK = { next: "controller.html", nextLabel: "Controller wiring", steps: /*STEPS*/[
 {
  "type": "prepare",
  "title": "Before you start",
  "warn": "<b>Press the e-stop. The adapter stays out of the wall</b> until the step that says otherwise.",
  "items": [
   "Strip: 8 mm for screw terminals, 11 mm for lever connectors; twist the strands; tug-test every wire.",
   "Meter: black probe in COM, red in V/Ω. Continuity (beep) for wiring, DC volts only when a step says live.",
   "Parts: adapter and jack, e-stop box, over-travel switch, three WAGO 221-2401 (splice A, splice B, cap), two 3-way lever connectors (MOT+, MOT−), SKR Pico, PC817 opto, 18 AWG red and black."
  ]
 },
 {
  "type": "wire",
  "title": "Adapter plug → jack socket",
  "from": [
   "24 V wall adapter (PWR-30)",
   "round 24 V plug"
  ],
  "to": [
   "Screw-terminal jack (with PWR-30)",
   "socket"
  ],
  "d": "M206 72C226 72 210 174 230 174",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Jack + → e-stop NC 1",
  "from": [
   "Screw-terminal jack (with PWR-30)",
   "+"
  ],
  "to": [
   "E-stop box (PWR-28)",
   "NC 1"
  ],
  "d": "M282 174C330 174 345 170 345 130",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "Jack − → MOT− slot 1",
  "from": [
   "Screw-terminal jack (with PWR-30)",
   "−"
  ],
  "to": [
   "Lever connector MOT− (3-way, on the tray)",
   "1"
  ],
  "d": "M282 190C291 190 292 196 292 206L292 404Q292 410 298 410L374 410Q380 410 380 404L380 390",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "MOT− slot 3 → SKR Pico GND",
  "from": [
   "Lever connector MOT− (3-way, on the tray)",
   "3"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "POWER GND"
  ],
  "d": "M450 390L450 400L505 400L505 340L520 340",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "E-stop NC 2 → splice A",
  "from": [
   "E-stop box (PWR-28)",
   "NC 2"
  ],
  "to": [
   "Splice A, e-stop side (WAGO 221-2401)",
   "red in"
  ],
  "d": "M390 130C390 190 400 217 430 217",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "Switch black (COM) → splice A",
  "from": [
   "Limit switch, over-travel (LAR-06)",
   "black (COM)"
  ],
  "to": [
   "Splice A, e-stop side (WAGO 221-2401)",
   "black"
  ],
  "d": "M545 150C545 178 480 172 480 200",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Switch grey (NC) → splice B",
  "from": [
   "Limit switch, over-travel (LAR-06)",
   "grey (NC)"
  ],
  "to": [
   "Splice B, tray side (WAGO 221-2401)",
   "grey"
  ],
  "d": "M580 150C580 176 570 176 570 200",
  "colour": "grey"
 },
 {
  "type": "wire",
  "title": "Splice B → MOT+ slot 1",
  "from": [
   "Splice B, tray side (WAGO 221-2401)",
   "red out"
  ],
  "to": [
   "Lever connector MOT+ (3-way, on the tray)",
   "1"
  ],
  "d": "M570 234C570 262 380 252 380 280",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "Switch blue (NO) → cap",
  "from": [
   "Limit switch, over-travel (LAR-06)",
   "blue (NO)"
  ],
  "to": [
   "Blue-wire cap (WAGO 221-2401)",
   "blue"
  ],
  "d": "M615 150C615 178 647 172 647 200",
  "colour": "blue"
 },
 {
  "type": "wire",
  "title": "MOT+ slot 3 → SKR Pico + 12/24V",
  "from": [
   "Lever connector MOT+ (3-way, on the tray)",
   "3"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "POWER 12/24V"
  ],
  "d": "M450 280L450 268Q450 262 456 262L500 262Q506 262 506 268L506 312L520 312",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "MOT+ slot 2 → opto IN+",
  "from": [
   "Lever connector MOT+ (3-way, on the tray)",
   "2"
  ],
  "to": [
   "Opto module (PWR-10)",
   "IN+"
  ],
  "d": "M415 320L415 334L484 334Q490 334 490 340L490 420L520 420",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "MOT− slot 2 → opto IN−",
  "from": [
   "Lever connector MOT− (3-way, on the tray)",
   "2"
  ],
  "to": [
   "Opto module (PWR-10)",
   "IN−"
  ],
  "d": "M415 390L415 432Q415 438 421 438L520 438",
  "colour": "black"
 },
 {
  "type": "check",
  "title": "Check before going on",
  "groups": [
   "1 ·",
   "2 ·"
  ]
 }
]/*END*/ };
