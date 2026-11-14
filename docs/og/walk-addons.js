/* Hub add-ons walkthrough (docs/addons.html): the spectral sensor and the status screen on the ESP32-S3 hub, drawn as
   the parts sit on the bench, read by og/walk.js. Wire and note text come from window.WIRING (docs/wiring-guide.js,
   generated); only titles, drawing and checks live here. tools/check.py fails if a from/to below is no longer a row in
   docs/wiring.yaml. SPDX-License-Identifier: GPL-3.0-or-later */
window.WALK = { next: "build.html", nextLabel: "Build book", steps: /*STEPS*/[
 {
  "type": "prepare",
  "title": "Before you start",
  "warn": "<b>Hub USB unplugged</b> while you wire it: the hub is powered from USB, not from the 24 V supply.",
  "items": [
   "Done first: the <a href=\"controller.html\">controller walkthrough</a> (hub flashed, keypads, power sense).",
   "Parts: AS7341 sensor (SPC-01) with its JST-SH cable (SPC-02); the status screen (STA-09, Waveshare 2inch LCD Module) with its 8-pin cable to female jumper ends, in its printed stand and bezel (STA-10); one WAGO 221-415 (5-way) and one 221-413 (3-way) from the lever-connector pack (PWR-20); male–female jumpers (CTL-07).",
   "The hub has two 3V3 pins and four GND pins, all but one already used, so the two lever connectors share 3V3 and GND with the sensor and the screen.",
   "A cut end: cut off the plug, strip 11 mm, fold the thin wire double, push it into the lever connector and close the lever. Tug-test every wire.",
   "Either part works alone: skip the sensor steps or the screen steps."
  ]
 },
 {
  "type": "wire",
  "title": "Hub J1-2 (3V3) → 3V3 lever connector",
  "from": [
   "ESP32-S3 hub (CTL-02)",
   "J1-2 (3V3)"
  ],
  "to": [
   "Lever connector hub 3V3 (WAGO 221-415, 5-way)",
   "1"
  ],
  "d": "M250 150H300",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "Hub J3-22 (GND) → GND lever connector",
  "from": [
   "ESP32-S3 hub (CTL-02)",
   "J3-22 (GND)"
  ],
  "to": [
   "Lever connector sensor GND (WAGO 221-413, 3-way)",
   "1"
  ],
  "d": "M250 100H300",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Sensor VIN → 3V3 lever connector",
  "from": [
   "AS7341 sensor (SPC-01, optional)",
   "VIN (red)"
  ],
  "to": [
   "Lever connector hub 3V3 (WAGO 221-415, 5-way)",
   "2"
  ],
  "d": "M470 145H350",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "Sensor GND → GND lever connector",
  "from": [
   "AS7341 sensor (SPC-01, optional)",
   "GND (black)"
  ],
  "to": [
   "Lever connector sensor GND (WAGO 221-413, 3-way)",
   "2"
  ],
  "d": "M470 88H350",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Sensor SCL → hub J3-5",
  "from": [
   "AS7341 sensor (SPC-01, optional)",
   "SCL (yellow)"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J3-5 (GPIO2)"
  ],
  "d": "M470 45H250",
  "colour": "amber"
 },
 {
  "type": "wire",
  "title": "Sensor SDA → hub J3-4",
  "from": [
   "AS7341 sensor (SPC-01, optional)",
   "SDA (blue)"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J3-4 (GPIO1)"
  ],
  "d": "M470 62H250",
  "colour": "blue"
 },
 {
  "type": "check",
  "title": "Check: spectral sensor",
  "items": [
   "Hub USB back in:"
  ],
  "cmd": [
   "bash scripts/hub.sh send \"SPEC? 1\""
  ],
  "pass": "SPEC #1 and 10 numbers (F1–F8, clear, NIR); they drop when a finger covers the sensor.",
  "warn": "ERR or no answer: SCL and SDA swapped, or VIN/GND not reaching the lever connectors. Unplug USB before fixing."
 },
 {
  "type": "wire",
  "title": "Screen VCC → 3V3 lever connector",
  "from": [
   "Status screen, Waveshare 2 in (STA-09, optional)",
   "VCC"
  ],
  "to": [
   "Lever connector hub 3V3 (WAGO 221-415, 5-way)",
   "3"
  ],
  "d": "M470 282H392V165H350",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "Screen GND → GND lever connector",
  "from": [
   "Status screen, Waveshare 2 in (STA-09, optional)",
   "GND"
  ],
  "to": [
   "Lever connector sensor GND (WAGO 221-413, 3-way)",
   "3"
  ],
  "d": "M470 260H400V110H350",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Screen RST → 3V3 lever connector",
  "from": [
   "Status screen, Waveshare 2 in (STA-09, optional)",
   "RST"
  ],
  "to": [
   "Lever connector hub 3V3 (WAGO 221-415, 5-way)",
   "4"
  ],
  "d": "M470 304H384V185H350",
  "colour": "violet"
 },
 {
  "type": "wire",
  "title": "Screen BL → 3V3 lever connector",
  "from": [
   "Status screen, Waveshare 2 in (STA-09, optional)",
   "BL"
  ],
  "to": [
   "Lever connector hub 3V3 (WAGO 221-415, 5-way)",
   "5"
  ],
  "d": "M470 326H376V205H350",
  "colour": "violet"
 },
 {
  "type": "wire",
  "title": "Screen CLK → hub J3-6",
  "from": [
   "Status screen, Waveshare 2 in (STA-09, optional)",
   "CLK"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J3-6 (GPIO42)"
  ],
  "d": "M470 360H250",
  "colour": "green"
 },
 {
  "type": "wire",
  "title": "Screen DIN → hub J3-7",
  "from": [
   "Status screen, Waveshare 2 in (STA-09, optional)",
   "DIN"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J3-7 (GPIO41)"
  ],
  "d": "M470 385H250",
  "colour": "green"
 },
 {
  "type": "wire",
  "title": "Screen DC → hub J1-11",
  "from": [
   "Status screen, Waveshare 2 in (STA-09, optional)",
   "DC"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-11 (GPIO18)"
  ],
  "d": "M470 410H250",
  "colour": "green"
 },
 {
  "type": "wire",
  "title": "Screen CS → hub J3-10",
  "from": [
   "Status screen, Waveshare 2 in (STA-09, optional)",
   "CS"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J3-10 (GPIO38)"
  ],
  "d": "M470 435H250",
  "colour": "green"
 },
 {
  "type": "check",
  "title": "Check: status screen",
  "items": [
   "Hub USB back in. Copy the current firmware to the hub: <code>bash scripts/hub.sh</code> (M09.1).",
   "Turn the screen on: the hub saves it and restarts. Then press a key, press and release the e-stop, and send a SHOW line:"
  ],
  "cmd": [
   "bash scripts/hub.sh",
   "bash scripts/hub.sh send \"SCREEN ON\"",
   "bash scripts/hub.sh send \"SHOW Bench test|line two\""
  ],
  "pass": "The screen shows OpenGonio hub, MOTOR POWER ON in green (OFF in red while the e-stop is pressed), the key you pressed, LAPTOP link, the SHOW lines and the uptime counting up.",
  "warn": "Blank white: CLK, DIN, DC or CS on the wrong pin, or RST not on 3V3. Mirrored or upside down: change MADCTL in firmware/hub/main.py (0x60 → 0xA0) and flash again. <code>SCREEN OFF</code> frees the pins for the encoders."
 }
]/*END*/ };
