/* Controller walkthrough (docs/controller.html): wires of docs/wiring.yaml drawn as the parts sit on the bench, read by og/walk.js.
   Wire and note text come from window.WIRING (docs/wiring-guide.js, generated); only titles, drawing and checks live here.
   tools/check.py fails if a from/to below is no longer a row in docs/wiring.yaml.
   SPDX-License-Identifier: GPL-3.0-or-later */
window.WALK = { next: "machine.html", nextLabel: "Machine wiring", steps: /*STEPS*/[
 {
  "type": "prepare",
  "title": "Before you start",
  "warn": "<b>E-stop pressed, adapter unplugged</b> for every wire on this page.",
  "items": [
   "Male–female jumpers (CTL-07). A cut jumper: one end cut off, 11 mm stripped, folded double in a lever connector.",
   "Hub pins: count from the antenna end (pin 1). Wire the hub before mounting it pins-up: mounted, the drawing is mirrored.",
   "Keypad tails: find the common pin with the meter first (M07.2): it beeps to every key while that key is pressed.",
   "Power wiring done and checked first: <a href=\"power.html\">power walkthrough</a>."
  ]
 },
 {
  "type": "wire",
  "title": "SKR Pico USB-C → laptop",
  "from": [
   "SKR Pico (CTL-01)",
   "USB-C"
  ],
  "to": [
   "Laptop",
   "USB-A"
  ],
  "d": "M200 104L215 104L215 29L500 29",
  "colour": "usb",
  "dash": "3 6"
 },
 {
  "type": "wire",
  "title": "Hub USB → laptop",
  "from": [
   "ESP32-S3 hub (CTL-02)",
   "USB (not UART)"
  ],
  "to": [
   "Laptop",
   "USB-A"
  ],
  "d": "M580 70L580 50",
  "colour": "usb",
  "dash": "3 6"
 },
 {
  "type": "check",
  "title": "Check: the laptop sees both boards",
  "items": [
   "Windows PowerShell (admin), for 2e8a (SKR Pico) and 303a (hub):"
  ],
  "cmd": [
   "usbipd list",
   "usbipd bind --busid <busid>",
   "usbipd attach --wsl --busid <busid>",
   "ls /dev/ttyACM*"
  ],
  "pass": "Two ports listed. Use data cables, not charge-only."
 },
 {
  "type": "check",
  "title": "Flash the SKR Pico (M08.2)",
  "items": [
   "Follow the script's four steps: build the .uf2 in the grblHAL Web Builder (board BTT SKR Pico 1.0, 4 axes), BOOT jumper on, RESET, copy the .uf2 onto RPI-RP2, jumper off, RESET."
  ],
  "cmd": [
   "bash scripts/controller.sh flash",
   "bash scripts/controller.sh settings",
   "bash scripts/controller.sh pins",
   "opengonio send '$I'",
   "opengonio send '?'"
  ],
  "pass": "$I lists grblHAL and BTT SKR Pico 1.0 · ? prints <Alarm|MPos: or <Idle|MPos: · $$ shows $22=15 and $10=17.",
  "warn": "pins: if HE / HB are not ports 4 / 3, set lights.white.output and lights.multispectral.output in software/config/machine.yaml."
 },
 {
  "type": "check",
  "title": "Flash the hub (M09.1)",
  "items": [
   "Read the module can: N8R8 or N16R8 → <code>flash oct</code>; anything else → <code>flash plain</code>. Then press RST."
  ],
  "cmd": [
   "bash scripts/hub.sh flash oct",
   "bash scripts/hub.sh"
  ],
  "pass": "PONG OpenGonio-hub 4.",
  "warn": "Won't connect: hold BOOT, tap RST, release BOOT, run it again."
 },
 {
  "type": "wire",
  "title": "Bench motor → SKR Pico X",
  "from": [
   "M4 motor, light arm (LAR-02)",
   "6-pin socket"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "X pins 1–4 (2B 1B 1A 2A)"
  ],
  "d": "M200 156L210 156L210 295L180 295",
  "colour": "violet"
 },
 {
  "type": "check",
  "title": "Check: bench motor (M08.3)",
  "items": [
   "Power off: meter on Ω at the back of the plug in the X socket: pins 1–4 and pins 2–3 each read a few ohms.",
   "E-stop pressed, adapter in, release the e-stop, then:"
  ],
  "cmd": [
   "opengonio send 'M122 I'",
   "opengonio send '$20=0' '$X' 'G91' 'G1 X10 F600' 'G1 X-10 F600' 'G90'",
   "opengonio send '$X' 'G91' 'G1 X360 F300' 'G90'",
   "opengonio send '$20=1'"
  ],
  "pass": "The shaft turns and returns to its tape mark · pressing the e-stop during the last move stops it at once.",
  "warn": "Never plug or unplug a motor with motor power on. Buzzes without turning = coil pairs crossed; wrong direction = $3 in software."
 },
 {
  "type": "wire",
  "title": "X endstop → SKR Pico X-STOP",
  "from": [
   "M4 endstop (LAR-05)",
   "S / G / V (by label)"
  ],
  "to": [
   "SKR Pico (CTL-01)",
   "X-STOP pins 1–3 (IO4 GND 5V)"
  ],
  "d": "M200 182L220 182L220 378L180 378",
  "colour": "green"
 },
 {
  "type": "check",
  "title": "Check: endstop (M10.2)",
  "items": [
   "Before plugging in: the module's V pin to X-STOP pin 3 beeps.",
   "Live:"
  ],
  "cmd": [
   "opengonio send '?'"
  ],
  "pass": "Pn:X with the slot blocked, no Pn with it open · $HX turns until the flag cuts the slot and stops."
 },
 {
  "type": "wire",
  "title": "Keypad A common → GND WAGO 1",
  "from": [
   "Keypad A (CTL-05)",
   "common"
  ],
  "to": [
   "Lever connector keypad GND (3-way)",
   "1"
  ],
  "d": "M400 286L414 286L414 442L420 442",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Keypad B common → GND WAGO 2",
  "from": [
   "Keypad B (CTL-05)",
   "common"
  ],
  "to": [
   "Lever connector keypad GND (3-way)",
   "2"
  ],
  "d": "M400 436L405 436L405 464L420 464",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "GND WAGO 3 → hub J1-22",
  "from": [
   "Lever connector keypad GND (3-way)",
   "3"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-22 (GND)"
  ],
  "d": "M470 486L497 486L497 322L500 322",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Keypad A key 1 → J1-4 (HOME)",
  "from": [
   "Keypad A (CTL-05)",
   "key 1"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-4 (GPIO4)"
  ],
  "d": "M400 308L476 308L476 140L500 140",
  "colour": "blue"
 },
 {
  "type": "wire",
  "title": "Keypad A key 2 → J1-5 (START)",
  "from": [
   "Keypad A (CTL-05)",
   "key 2"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-5 (GPIO5)"
  ],
  "d": "M400 330L482 330L482 166L500 166",
  "colour": "blue"
 },
 {
  "type": "wire",
  "title": "Keypad A key 3 → J1-6 (STOP)",
  "from": [
   "Keypad A (CTL-05)",
   "key 3"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-6 (GPIO6)"
  ],
  "d": "M400 352L488 352L488 192L500 192",
  "colour": "blue"
 },
 {
  "type": "wire",
  "title": "Keypad A key 4 → J1-7 (LIGHT)",
  "from": [
   "Keypad A (CTL-05)",
   "key 4"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-7 (GPIO7)"
  ],
  "d": "M400 374L493 374L493 218L500 218",
  "colour": "blue"
 },
 {
  "type": "wire",
  "title": "Keypad B key 1 → J1-8 (NEXT)",
  "from": [
   "Keypad B (CTL-05)",
   "key 1"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-8 (GPIO15)"
  ],
  "d": "M400 458L466 458L466 244L500 244",
  "colour": "blue"
 },
 {
  "type": "wire",
  "title": "Keypad B key 2 → J1-9 (PAUSE)",
  "from": [
   "Keypad B (CTL-05)",
   "key 2"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-9 (GPIO16)"
  ],
  "d": "M400 480L471 480L471 270L500 270",
  "colour": "blue"
 },
 {
  "type": "check",
  "title": "Check: keypads (M09.2, M09.3)",
  "items": [
   "On the hub's port (ls /dev/ttyACM* before and after plugging it in shows which), press each key:"
  ],
  "cmd": [
   "python -m serial.tools.miniterm /dev/ttyACM1 115200",
   "opengonio panel"
  ],
  "pass": "Each key prints its own BTN <NAME> exactly once · in the panel: HOME, LIGHT, NEXT, START, PAUSE, START, STOP each logged; PAUSE stops after the pose in progress.",
  "warn": "Nothing printed: check the commons reach J1-22 through the GND WAGO. Keypad B keys 3 and 4 stay unconnected."
 },
 {
  "type": "wire",
  "title": "MOT+ 2 → opto IN+",
  "from": [
   "Lever connector MOT+ (3-way, on the tray)",
   "2"
  ],
  "to": [
   "Opto module (PWR-10)",
   "IN+"
  ],
  "d": "M265 86L265 100",
  "colour": "red"
 },
 {
  "type": "wire",
  "title": "MOT− 2 → opto IN−",
  "from": [
   "Lever connector MOT− (3-way, on the tray)",
   "2"
  ],
  "to": [
   "Opto module (PWR-10)",
   "IN−"
  ],
  "d": "M335 86L335 100",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Opto VCC → J1-1 (3V3)",
  "from": [
   "Opto module (PWR-10)",
   "VCC"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-1 (3V3)"
  ],
  "d": "M380 140L420 140L420 114L500 114",
  "colour": "amber"
 },
 {
  "type": "wire",
  "title": "Opto GND → J3-21 (GND)",
  "from": [
   "Opto module (PWR-10)",
   "GND"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J3-21 (GND)"
  ],
  "d": "M380 166L428 166L428 348L500 348",
  "colour": "black"
 },
 {
  "type": "wire",
  "title": "Opto OUT → J1-10 (GPIO17)",
  "from": [
   "Opto module (PWR-10)",
   "OUT"
  ],
  "to": [
   "ESP32-S3 hub (CTL-02)",
   "J1-10 (GPIO17)"
  ],
  "d": "M380 186L436 186L436 296L500 296",
  "colour": "blue"
 },
 {
  "type": "check",
  "title": "Check: power sense (M10.3)",
  "items": [
   "Adapter in, e-stop released: the opto module's input LED is on.",
   "Home, wait while the motor holds; DC volts on SKR Pico POWER (T4) and from jack + to SKR POWER + (T12). Then press and release the e-stop 20 times."
  ],
  "cmd": [
   "opengonio home"
  ],
  "pass": "T4 ≥ 22.5 V · T12 ≤ 0.3 V · hub prints POWER 0 on e-stop and POWER 1 after release, 20 of 20 · moves refused until HOME."
 }
]/*END*/ };
