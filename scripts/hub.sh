#!/usr/bin/env bash
# ESP32-S3 button + sensor hub [C13][R86]. Plug the board's "USB" connector (not "UART") into the laptop, then:
#   bash scripts/hub.sh flash oct     erase + write MicroPython (pinned in firmware/hub/MICROPYTHON_VERSION) [C13]:
#                                      "oct" if the module's can says N8R8 / N16R8 (octal PSRAM), "plain" otherwise
#   bash scripts/hub.sh           copy firmware/hub/main.py, then PING it
#   bash scripts/hub.sh send "SCREEN ON"     send one line to the hub and print its reply (any command in main.py)
# If flash can't connect: hold BOOT, tap RST, release BOOT (download mode), run it again.
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q mpremote pyserial esptool
port() { python3 -c "from serial.tools import list_ports; p=[x.device for x in list_ports.comports() if x.vid == 0x303A]; print(p[0] if p else '')"; }
if [ "${1:-}" = "flash" ]; then
  case "${2:-}" in oct) V="-SPIRAM_OCT" ;; plain) V="" ;; *) echo "say which: bash scripts/hub.sh flash oct|plain"; exit 1 ;; esac
  VER="ESP32_GENERIC_S3$V-$(tr -d '[:space:]' < firmware/hub/MICROPYTHON_VERSION).bin"   # pinned release, never "latest"
  mkdir -p .micropython && curl -fL -o ".micropython/$VER" "https://micropython.org/resources/firmware/$VER"
  P=$(port); [ -n "$P" ] || { echo "no Espressif USB port (VID 0x303A) found: use the USB connector, or set download mode"; exit 1; }
  esptool.py --chip esp32s3 --port "$P" erase_flash
  esptool.py --chip esp32s3 --port "$P" write_flash -z 0 ".micropython/$VER"
  echo "Flashed. Press RST, then: bash scripts/hub.sh"; exit 0
fi
P=$(port); [ -n "$P" ] || { echo "hub not found (VID 0x303A): plug in its USB connector (not UART)"; exit 1; }
if [ "${1:-}" = "send" ]; then
  python3 - "$P" "${2:?say what: bash scripts/hub.sh send \"SCREEN ON\"}" <<'PY'
import serial, sys, time
with serial.Serial(sys.argv[1], 115200, timeout=1) as s:
    s.write(sys.argv[2].encode() + b"\n"); time.sleep(0.5); print(s.read(400).decode(errors="ignore").strip() or "no reply")
PY
  exit 0
fi
mpremote connect "$P" mip install ssd1306 || echo "no OLED driver (display optional)"   # this board only, never the SKR Pico
mpremote connect "$P" cp firmware/hub/main.py :main.py
mpremote connect "$P" reset
sleep 2
python3 - <<'PY'
import serial, time
from serial.tools import list_ports
p = [x.device for x in list_ports.comports() if x.vid == 0x303A]
if not p:
    raise SystemExit("hub not found (VID 0x303A): is it on the USB connector?")
with serial.Serial(p[0], 115200, timeout=1) as s:
    s.write(b"PING\n"); time.sleep(0.3); print(p[0], s.read(200).decode(errors="ignore").strip() or "no reply")
PY
echo "Press a button: run  opengonio panel"
