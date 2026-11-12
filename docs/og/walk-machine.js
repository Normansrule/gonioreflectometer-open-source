/* Machine walkthrough (docs/machine.html): motors, endstops, lamp, camera and add-ons of docs/wiring.yaml, drawn as the parts sit
   on the bench, read by og/walk.js. Wire and note text come from window.WIRING (docs/wiring-guide.js, generated); only titles,
   drawing and checks live here. tools/check.py fails if a from/to below is no longer a row in docs/wiring.yaml.
   SPDX-License-Identifier: GPL-3.0-or-later */
window.WALK = { next: "build.html", nextLabel: "Build book", steps: /*STEPS*/[
 {
  "type": "prepare",
  "title": "Before you start",
  "warn": "<b>E-stop pressed, adapter unplugged</b> for every wire on this page. Never plug or unplug a motor with motor power on.",
  "items": [
   "Done first: the <a href=\"power.html\">power walkthrough</a> and the <a href=\"controller.html\">controller walkthrough</a> (USB, both boards flashed, M4 on X, its endstop, keypads, power sense). Those wires are drawn dotted.",
   "This page wires and tests everything else on the bench, parts loose, before any printing: three motors, three endstops, the lamp, the camera, then the optional fan and spectral sensor.",
   "Per motor: a tape flag on the shaft to see it turn and come back. Per endstop: a piece of card to block its slot.",
   "Ends: plugs push into their sockets; bare ends 11 mm in lever connectors (thin wire folded double), 8 mm under screws. Tug-test every wire."
  ]
 },
 {
  "type": "wire",
  "title": "Table motor M3 → SKR Pico Y",
  "from": [
   "M3 motor, table (TBL-01)",
   "6-pin socket"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "Y pins 1–4 (2B 1B 1A 2A)"
  ],
  "d": "M205 80V125H230V170",
  "colour": "violet"
 },
 {
  "type": "wire",
  "title": "Tilt motor M2 → SKR Pico Z1",
  "from": [
   "M2 motor, tilt (TLT-01)",
   "6-pin socket"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "Z1 pins 1–4 (2B 1B 1A 2A)"
  ],
  "d": "M335 80V140H290V170",
  "colour": "violet"
 },
 {
  "type": "check",
  "title": "Check: Y and Z motors turn",
  "items": [
   "Power off: meter on Ω at the back of each plug in its socket: pins 1–4 and pins 2–3 each read a few ohms.",
   "Tape flag on each shaft. Adapter in, release the e-stop, then:"
  ],
  "cmd": [
   "opengonio send 'M122 I'",
   "opengonio send '$20=0' '$X' 'G91' 'G1 Y10 F600' 'G1 Y-10 F600' 'G90'",
   "opengonio send '$20=0' '$X' 'G91' 'G1 Z10 F600' 'G1 Z-10 F600' 'G90'",
   "opengonio send '$20=1'"
  ],
  "pass": "Each shaft turns, then returns to its tape mark.",
  "warn": "Buzzes without turning = coil pairs crossed (move plug contacts until 1–4 and 2–3 read a few ohms). Wrong direction = <code>$3</code> in software (Y 2, Z 4), not wiring. Press the e-stop and unplug the adapter again before the next wire."
 },
 {
  "type": "prepare",
  "title": "Spin motor: find its coil pairs (M27.1)",
  "warn": "<b>E-stop pressed, adapter unplugged</b> for every wire.",
  "items": [
   "The pancake (SPN-01) has 4 bare leads. Touch two together and turn the shaft by hand: noticeably stiffer = one pair (or meter: a pair reads a few ohms, leads from different pairs read open). Tape-label them pair 1 and pair 2.",
   "Spare motor cable: cut off the 6-pin (motor-end) plug, strip 11 mm of all 4 wires. Note which colours sit in pins 1 + 4 and pins 2 + 3 of its 4-pin plug.",
   "Lever connectors: 3 × WAGO 221-412 + 1 × 221-415, one motor lead and one cable wire in each."
  ]
 },
 {
  "type": "wire",
  "title": "Spin motor pair 1 → lever connectors",
  "from": [
   "M1 pancake, spin (SPN-01)",
   "coil pair 1 (2 bare leads)"
  ],
  "to": [
   "Lever connectors (WAGO 221-412 / 415)",
   "pair 1 (2 × 221-412)"
  ],
  "d": "M440 80V92H430V105",
  "colour": "violet"
 },
 {
  "type": "wire",
  "title": "Pair 1 connectors → SKR Pico E pins 1 + 4",
  "from": [
   "Lever connectors (WAGO 221-412 / 415)",
   "pair 1 (2 × 221-412)"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "E pin 1 (2B) + E pin 4 (2A)"
  ],
  "d": "M430 135V152H395V170",
  "colour": "violet"
 },
 {
  "type": "wire",
  "title": "Spin motor pair 2 → lever connectors",
  "from": [
   "M1 pancake, spin (SPN-01)",
   "coil pair 2 (2 bare leads)"
  ],
  "to": [
   "Lever connectors (WAGO 221-412 / 415)",
   "pair 2 (221-412 + 221-415)"
  ],
  "d": "M490 80V92H495V105",
  "colour": "violet"
 },
 {
  "type": "wire",
  "title": "Pair 2 connectors → SKR Pico E pins 2–3",
  "from": [
   "Lever connectors (WAGO 221-412 / 415)",
   "pair 2 (221-412 + 221-415)"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "E pins 2–3 (1B 1A)"
  ],
  "d": "M495 135V158H420V170",
  "colour": "violet"
 },
 {
  "type": "check",
  "title": "Check: spin motor turns",
  "items": [
   "Power off: meter on Ω at the back of the E plug: 1–4 and 2–3 read a few ohms, 1–2 open. Tape the four connectors together.",
   "Tape flag on the shaft. Adapter in, release the e-stop, then:"
  ],
  "cmd": [
   "opengonio send 'M122 I'",
   "opengonio send '$20=0' '$X' 'G91' 'G1 A10 F600' 'G1 A-10 F600' 'G90'",
   "opengonio send '$20=1'"
  ],
  "pass": "The pancake shaft turns, then returns to its tape mark.",
  "warn": "<code>error:</code> on the A move = grblHAL built with 3 axes: rebuild with 4 (M08.2). Buzzes = a lead from each coil in one pair: redo the pair test. Wrong way = <code>$3</code> bit 8."
 },
 {
  "type": "wire",
  "title": "Table endstop → SKR Pico Y-STOP",
  "from": [
   "M3 endstop (TBL-04)",
   "S / G / V (by label)"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "Y-STOP pins 1–3 (IO3 GND 5V)"
  ],
  "d": "M240 380V330",
  "colour": "green"
 },
 {
  "type": "wire",
  "title": "Tilt endstop → SKR Pico Z-STOP",
  "from": [
   "M2 endstop (TLT-04)",
   "S / G / V (by label)"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "Z-STOP pins 1–3 (IO25 GND 5V)"
  ],
  "d": "M300 380V330",
  "colour": "green"
 },
 {
  "type": "wire",
  "title": "Spin endstop → SKR Pico E0-STOP",
  "from": [
   "M1 endstop (SPN-04)",
   "S / G / V (by label)"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "E0-STOP pins 1–3 (IO16 GND 5V)"
  ],
  "d": "M410 380V330",
  "colour": "green"
 },
 {
  "type": "check",
  "title": "Check: endstops and homing (M10.2 per axis)",
  "items": [
   "Before plugging each lead into its STOP socket: the module's V pin to STOP pin 3 beeps.",
   "Adapter in, e-stop released. Each slot open, then blocked with card:"
  ],
  "cmd": [
   "opengonio send '?'",
   "# flag taped to the shaft, endstop held so the flag passes through its slot:",
   "opengonio send '$HY'",
   "opengonio send '$HZ'",
   "opengonio send '$HA'"
  ],
  "pass": "Pn:Y, Pn:Z and Pn:A show only while that slot is blocked · each $H turns until the flag cuts the slot, then stops.",
  "warn": "Pn while open or never stops = inverted input: <code>$5</code> bit (Y 2, Z 4, A 8). No Pn:A = S/G/V order at the module, or a 3-axis build. Module LED never lights = lead on the wrong module pins."
 },
 {
  "type": "wire",
  "title": "Lamp driver +Vin → SKR Pico HE +",
  "from": [
   "Lamp driver NLDD-350H (LSR-02)",
   "+Vin"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "HE 12/24V"
  ],
  "d": "M120 228H150",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "Lamp driver −Vin → SKR Pico HE IO23",
  "from": [
   "Lamp driver NLDD-350H (LSR-02)",
   "−Vin"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "HE IO23"
  ],
  "d": "M120 248H150",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Lamp driver +Vo → lamp red",
  "from": [
   "Lamp driver NLDD-350H (LSR-02)",
   "+Vo"
  ],
  "to": [
   "COB lamp in holder (LSR-01 + LSR-06)",
   "red (+) lead"
  ],
  "d": "M40 266V470",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "Lamp driver −Vo → lamp black",
  "from": [
   "Lamp driver NLDD-350H (LSR-02)",
   "−Vo"
  ],
  "to": [
   "COB lamp in holder (LSR-01 + LSR-06)",
   "black (−) lead"
  ],
  "d": "M64 266V470",
  "colour": "black"
 },
 {
  "type": "check",
  "title": "Check: lamp (M18.1, M18.2)",
  "items": [
   "COB in its holder, thermal tape and heatsink on (M18.1). Never light it bare.",
   "Power off: meter from the driver's +Vo pin to the lamp's red lead beeps. DIM stays unconnected (on/off only).",
   "Lamp facing the bench, not your eyes. <code>installed_phase</code> ≥ 6 in <code>software/config/machine.yaml</code>. Adapter in, e-stop released:"
  ],
  "cmd": [
   "opengonio light on",
   "opengonio light off"
  ],
  "pass": "Lamp follows every command, 5 on/off cycles · COB case ≤ 70 °C after 10 min on (probe).",
  "warn": "Always on = −Vin on GND instead of HE IO23. Never lights = −Vin on HE +, or +Vo / −Vo swapped."
 },
 {
  "type": "wire",
  "title": "Camera → laptop",
  "from": [
   "Camera (CAM-01)",
   "USB"
  ],
  "to": [
   "Laptop",
   "USB-A"
  ],
  "d": "M605 70V150",
  "colour": "usb",
  "dash": "3 6"
 },
 {
  "type": "check",
  "title": "Check: camera (M17.1)",
  "items": [
   "WSL has no USB-camera driver: test from Windows PowerShell, in the repo folder:"
  ],
  "cmd": [
   "cd \\\\wsl.localhost\\Ubuntu\\home\\<you>\\projects\\gonioreflectometer-open-source",
   "py -m venv $HOME\\og-win",
   "& $HOME\\og-win\\Scripts\\pip install \"./software[hw]\"",
   "& $HOME\\og-win\\Scripts\\python -c \"import cv2; print(cv2.VideoCapture(0).read()[0])\""
  ],
  "pass": "Prints True.",
  "warn": "False: the laptop's own webcam is index 0. Try <code>VideoCapture(1)</code>; if that prints True, set <code>camera.index: 1</code> in machine.yaml."
 },
 {
  "type": "wire",
  "title": "Optional: fan red → FAN1 12/24V",
  "from": [
   "40 mm fan (CTL-08, optional)",
   "red (+)"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "FAN1 12/24V"
  ],
  "d": "M130 280H150",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "Optional: fan black → FAN1 IO17",
  "from": [
   "40 mm fan (CTL-08, optional)",
   "black (−)"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "FAN1 IO17"
  ],
  "d": "M130 300H150",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Optional: AS7341 VIN → hub J1-2 (3V3)",
  "from": [
   "AS7341 sensor (SPC-01, optional)",
   "VIN (red)"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-2 (3V3)"
  ],
  "d": "M520 420V340",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "Optional: AS7341 GND → hub J3-22",
  "from": [
   "AS7341 sensor (SPC-01, optional)",
   "GND (black)"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J3-22 (GND)"
  ],
  "d": "M560 420V340",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Optional: AS7341 SCL → hub J3-5",
  "from": [
   "AS7341 sensor (SPC-01, optional)",
   "SCL (yellow)"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J3-5 (GPIO2)"
  ],
  "d": "M600 420V340",
  "colour": "amber"
 },
 {
  "type": "wire",
  "title": "Optional: AS7341 SDA → hub J3-4",
  "from": [
   "AS7341 sensor (SPC-01, optional)",
   "SDA (blue)"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J3-4 (GPIO1)"
  ],
  "d": "M640 420V340",
  "colour": "blue"
 },
 {
  "type": "check",
  "title": "Check: fan and spectral sensor (optional)",
  "items": [
   "Hub USB out while you wire the sensor; back in afterwards. Adapter in, e-stop released.",
   "Fan: <code>$PINS</code> lists FAN1's port (normally 2). Sensor: on the hub's port, type <code>SPEC? 1</code>."
  ],
  "cmd": [
   "opengonio send '$PINS'",
   "opengonio send 'M62 P2'",
   "opengonio send 'M63 P2'",
   "python -m serial.tools.miniterm /dev/ttyACM1 115200"
  ],
  "pass": "Fan runs on M62 P2, stops on M63 P2 · SPEC #1 and 10 numbers (F1–F8, clear, NIR) that drop when a finger covers the sensor.",
  "warn": "OLED instead of the sensor: the same four hub pins (wiring guide, section 8). Both fitted: OLED on the sensor's second STEMMA QT socket (cable [TBD])."
 },
 {
  "type": "check",
  "title": "Check: the whole machine on the bench",
  "items": [
   "Every motor plugged in, a flag on each shaft, each endstop held so its flag passes through the slot.",
   "<code>installed_phase: 9</code> in machine.yaml for this test (all four axes); set it back to the stage you have built afterwards.",
   "Adapter in, e-stop released. Press the e-stop once while a motor is moving."
  ],
  "cmd": [
   "opengonio home",
   "opengonio status",
   "opengonio light on",
   "opengonio light off",
   "opengonio panel"
  ],
  "pass": "Homes M4, M3, M2, M1 in turn, each stopping at its flag · status prints true angles for all four · lamp on and off · every key logged in the panel · the e-stop stops the move at once and the hub prints POWER 0.",
  "warn": "Not now: the colour LED bank (wiring guide section 10) is blocked: do not wire or power it. The standalone station (section 9) and the battery monitor (stage 17) come later."
 }
]/*END*/ };
