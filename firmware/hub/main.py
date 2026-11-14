# OpenGonio panel + sensor hub - MicroPython (ESP32_GENERIC_S3) for the ESP32-S3-DevKitC-1 [C13][R86]
# SPDX-License-Identifier: GPL-3.0-or-later
#
# USB serial line protocol (laptop <-> hub)
#   out: BTN HOME|START|STOP|LIGHT|NEXT|PAUSE   POWER 0|1   ENC a b c d   PONG OpenGonio-hub 4 POWER n   ERR <msg>
#   in : BAND 0-7 | BAND OFF | ENC? | POWER? | PING | SHOW line1|line2|line3 | SPEC? <id> | BATT? | SOURCE WALL|PACK|USBC [Wh]
#        | SCREEN ON|OFF  (optional 2 in ST7789 status screen; kept in screen.txt, takes effect after the hub restarts)
#   BATT? -> 'BATT <source> <volts> <amps> <watts> <Wh used> <OK|LOW|CRIT|NONE>' from an INA219 (0x40, stage 17 battery kit)
#   on the first I2C pair; the hub also sends that line when the state changes, and 'BTN PAUSE' once on CRIT.
#   SPEC? <id> -> 'SPEC #<id> f1 f2 f3 f4 f5 f6 f7 f8 clear nir' from an AS7341 (0x39) on the first I2C pair (shared with the OLED).
# Same protocol on the board's USB connector (laptop) and on UART1 GPIO 47 TX / 48 RX (Pi Zero station, 3.3 V, 115200).
# Optional SSD1306 128x64 OLED at 0x3C on the first I2C pair (GPIO 2 SCL, GPIO 1 SDA); install: mpremote mip install ssd1306
# Pins (GPIO numbers, all clear of the strapping pins 0/3/45/46, USB 19/20, flash/PSRAM 26-37 and UART0 43/44 [R86]):
#   buttons HOME 4, START 5, STOP 6, LIGHT 7, NEXT 15, PAUSE 16 (each to GND), MOTION_SENSE 17 (PC817 module OUT,
#   low = motor power on), LED bank 8-14 + 21 -> MOSFET module inputs, I2C pairs (scl, sda) (2,1) (40,39) (42,41) (18,38).
# Status screen (optional, SCREEN ON): 2 in ST7789 240 x 320 SPI LCD on SCK 42, MOSI 41, DC 18, CS 38: the pins of I2C pairs
#   3 and 4, so with the screen on those two encoder buses are not started. Its RST and BL go to 3V3. It shows what the hub
#   knows by itself (motor power, keys, supply, laptop link, last spectral reading) plus the SHOW lines, so the machine's
#   state stays visible if the laptop app has a problem.
# The board's RGB LED sits on GPIO 48 (v1.0) or 38 (v1.1): it may flicker when that pin carries UART or I2C. Harmless.
import sys
import time
import uselect
from machine import SPI, UART, Pin, SoftI2C

BUTTONS = {"HOME": 4, "START": 5, "STOP": 6, "LIGHT": 7, "NEXT": 15, "PAUSE": 16}
SENSE_PIN = 17
SENSE_ACTIVE_LOW = True                 # PC817 module OUT pulls GPIO 17 low when motor power is on; False if yours drives OUT high
BAND_PINS = [8, 9, 10, 11, 12, 13, 14, 21]
I2C_PAIRS = [(2, 1), (40, 39), (42, 41), (18, 38)]   # (scl, sda)
UART_TX, UART_RX = 47, 48
SCREEN_PINS = {"SCK": 42, "MOSI": 41, "DC": 18, "CS": 38}   # status screen: I2C pairs 3 and 4 when it is fitted
MADCTL = 0x60                           # landscape 320 x 240; if the picture is mirrored, try 0xA0
AS5600 = 0x36
DEBOUNCE_MS = 30
INA = 0x40                              # INA219 power monitor, 0.1 ohm shunt (Adafruit 904): volts and amps on the 24 V line
SHUNT_OHM = 0.1

btn = {n: Pin(p, Pin.IN, Pin.PULL_UP) for n, p in BUTTONS.items()}
last = {n: 1 for n in BUTTONS}
since = {n: 0 for n in BUTTONS}
sense = Pin(SENSE_PIN, Pin.IN, Pin.PULL_UP)
bands = [Pin(p, Pin.OUT, value=0) for p in BAND_PINS]


def screen_wanted():
    try:
        return open("screen.txt").read().strip() == "ON"
    except Exception:                       # first boot: no file, no screen
        return False


screen_on = screen_wanted()
buses = [SoftI2C(scl=Pin(s), sda=Pin(d), freq=100_000) for s, d in (I2C_PAIRS[:2] if screen_on else I2C_PAIRS)]
poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)
uart = UART(1, baudrate=115200, tx=Pin(UART_TX), rx=Pin(UART_RX))
try:
    import ssd1306
    oled = ssd1306.SSD1306_I2C(128, 64, buses[0])
except Exception:                           # no display fitted: everything else still works
    oled = None


def battery_state(volts, source, used_wh, capacity_wh):
    """OK / LOW / CRIT for the power source in use. WALL never runs out; a sagging supply still reads LOW.
    PACK: six lithium-ion cells (25.2 V full): LOW at 3.6 V a cell, CRIT at 3.4 V, above the pack's own cut-off.
    USBC: the bank holds 20 V until it is empty, so the warning comes from energy used against its rated Wh."""
    if source == "PACK":
        return "CRIT" if volts < 20.4 else "LOW" if volts < 21.6 else "OK"
    if source == "USBC":
        if volts < 18.5:                    # the bank stopped holding 20 V: it is about to switch off
            return "CRIT"
        left = 1 - used_wh / capacity_wh if capacity_wh > 0 else 1
        return "CRIT" if left < 0.05 else "LOW" if left < 0.15 else "OK"
    return "LOW" if volts < 22.0 else "OK"   # WALL (24 V adapter)


def load_source():
    try:
        name, wh = (open("source.txt").read().split() + ["0"])[:2]
        return (name, float(wh)) if name in ("WALL", "PACK", "USBC") else ("WALL", 0.0)
    except Exception:                       # first boot: no file yet
        return "WALL", 0.0


def ina_read():
    raw = buses[0].readfrom_mem(INA, 0x01, 2)                       # shunt voltage, signed, 10 uV a count
    sh = (raw[0] << 8) | raw[1]
    sh = sh - 0x10000 if sh & 0x8000 else sh
    v = buses[0].readfrom_mem(INA, 0x02, 2)                         # bus voltage, bits 15-3, 4 mV a count
    return (((v[0] << 8) | v[1]) >> 3) * 0.004, sh * 10e-6 / SHUNT_OHM


saved = load_source()
source = saved[0]                           # WALL / PACK / USBC, kept in source.txt across restarts
capacity_wh = saved[1]                      # USBC: the bank's rated Wh; 0 = not set
used_wh = 0.0
batt = "NONE"
batt_t = time.ticks_ms()


def batt_line():
    try:
        volts, amps = ina_read()
    except OSError:                         # no INA219 fitted
        return None, "BATT %s 0 0 0 0 NONE" % source
    return (volts, amps), "BATT %s %.2f %.3f %.1f %.2f %s" % (source, volts, amps, volts * amps, used_wh,
                                                             battery_state(volts, source, used_wh, capacity_wh))


AS = 0x39                                   # AS7341 11-channel spectral sensor; register map per the ams datasheet


def as_w(reg, val):
    buses[0].writeto_mem(AS, reg, bytes([val]))


def as_r(reg, n=1):
    return buses[0].readfrom_mem(AS, reg, n)


SMUX_LOW = (0x30, 0x01, 0x00, 0x00, 0x00, 0x42, 0x00, 0x00, 0x50, 0x00,
            0x00, 0x00, 0x20, 0x04, 0x00, 0x30, 0x01, 0x50, 0x00, 0x06)   # F1-F4, clear, NIR -> ADC0-5
SMUX_HIGH = (0x00, 0x00, 0x00, 0x40, 0x02, 0x00, 0x10, 0x03, 0x50, 0x10,
             0x03, 0x00, 0x00, 0x00, 0x24, 0x00, 0x00, 0x50, 0x00, 0x06)  # F5-F8, clear, NIR -> ADC0-5


def as_read6(smux):
    as_w(0x80, 0x01)                         # power on, measurement off
    as_w(0xAF, 0x10)                         # SMUX command: write config from RAM
    for i, v in enumerate(smux):
        as_w(i, v)
    as_w(0x80, 0x11)                         # SMUXEN
    t = time.ticks_ms()
    while as_r(0x80)[0] & 0x10:
        if time.ticks_diff(time.ticks_ms(), t) > 500:
            raise OSError("AS7341 SMUX timeout")
    as_w(0x80, 0x03)                         # spectral measurement on
    t = time.ticks_ms()
    while not as_r(0xA3)[0] & 0x40:          # AVALID
        if time.ticks_diff(time.ticks_ms(), t) > 2000:
            raise OSError("AS7341 timeout")
    d = as_r(0x95, 12)
    as_w(0x80, 0x01)
    return [d[2 * i] | (d[2 * i + 1] << 8) for i in range(6)]


def spectral():
    as_w(0x81, 29)                           # ATIME
    as_w(0xCA, 0xE7); as_w(0xCB, 0x03)       # ASTEP 999 -> (29+1)(999+1)2.78 us = 83 ms
    as_w(0xAA, 6)                            # gain 32x; lower it if a channel reads 65535
    lo, hi = as_read6(SMUX_LOW), as_read6(SMUX_HIGH)
    return lo[:4] + hi[:4] + [lo[4], lo[5]]  # F1..F8, clear, NIR


def rgb(r, g, b):
    """RGB565, high byte first as the ST7789 wants it."""
    c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return bytes([c >> 8, c & 0xFF])


class ST7789:
    """Minimal ST7789 driver for the status screen: init, clear, and text lines drawn at twice the 8 x 8 font size."""
    W, H, ROW = 320, 240, 16                # 20 characters x 15 lines

    def __init__(self, spi, dc, cs, madctl=0x60):
        self.spi, self.dc, self.cs, self.madctl = spi, dc, cs, madctl
        self.cs.value(1)

    def cmd(self, c, data=None):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes([c]))
        if data:
            self.dc.value(1)
            self.spi.write(data)
        self.cs.value(1)

    def init(self):
        for c, d, wait in ((0x01, None, 150), (0x11, None, 120), (0x3A, b"\x55", 0), (0x36, bytes([self.madctl]), 0),
                           (0x21, None, 0), (0x13, None, 0), (0x29, None, 20)):   # reset, wake, 16-bit colour, rotate, IPS invert, on
            self.cmd(c, d)
            if wait:
                time.sleep_ms(wait)

    def window(self, x0, y0, x1, y1):
        self.cmd(0x2A, bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        self.cmd(0x2B, bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(b"\x2c")
        self.dc.value(1)

    def clear(self, bg):
        self.window(0, 0, self.W - 1, self.H - 1)
        row = bg * self.W
        for _ in range(self.H):
            self.spi.write(row)
        self.cs.value(1)

    def line(self, n, text, fg, bg):
        """Line n (0-14): up to 20 characters, each 8 x 8 font pixel drawn as 2 x 2."""
        import framebuf
        text = text[:self.W // 16]
        mono = framebuf.FrameBuffer(bytearray(self.W // 2), self.W // 2, 8, framebuf.MONO_HLSB)   # 160 x 8 px, 1 bit
        mono.fill(0)
        mono.text(text, 0, 0, 1)
        out = bytearray(self.W * 2 * self.ROW)
        for sy in range(8):
            row = bytearray(bg * self.W)
            for sx in range(len(text) * 8):
                if mono.pixel(sx, sy):
                    row[sx * 4:sx * 4 + 4] = fg + fg
            a = sy * 2 * self.W * 2
            out[a:a + self.W * 2] = row
            out[a + self.W * 2:a + self.W * 4] = row
        self.window(0, n * self.ROW, self.W - 1, n * self.ROW + self.ROW - 1)
        self.spi.write(out)
        self.cs.value(1)


def out(msg):
    print(msg)
    uart.write(msg + "\n")


laptop_lines = []                           # the last SHOW lines (the laptop or the Pi station writes these)


def show(lines):
    global laptop_lines
    laptop_lines = [str(t) for t in lines[:6]]
    if oled is None:
        return
    oled.fill(0)
    for i, t in enumerate(lines[:6]):
        oled.text(t[:16], 0, i * 11)
    oled.show()


def band(n):
    for i, p in enumerate(bands):
        p.value(1 if i == n else 0)        # only one band on at a time


def read_angle(bus):
    try:
        hi, lo = bus.readfrom_mem(AS5600, 0x0C, 2)
        return (((hi & 0x0F) << 8) | lo) * 360.0 / 4096.0
    except OSError:
        return float("nan")


BLACK = rgb(12, 11, 10)
WHITE = rgb(239, 233, 223)
GREEN = rgb(80, 200, 120)
RED = rgb(230, 70, 60)
AMBER = rgb(255, 201, 120)
GREY = rgb(150, 145, 138)
boot_t = time.ticks_ms()
last_key, key_t, host_t, spec_last = "-", 0, None, None


def ago(t, now):
    s = time.ticks_diff(now, t) // 1000
    return "%ds" % s if s < 60 else "%dm" % (s // 60) if s < 3600 else "%dh" % (s // 3600)


def screen_lines(now, power, source, batt, last_key, key_t, host_t, laptop, spec, boot):
    """The status screen's 15 lines as (text, colour name). Pure: tests/test_hub_screen.py runs it on a laptop."""
    up = time.ticks_diff(now, boot) // 1000
    lines = [("OpenGonio hub", "white"),
             ("MOTOR POWER ON" if power else "MOTOR POWER OFF", "green" if power else "red"),
             ("SUPPLY %s %s" % (source, batt), "amber" if batt in ("LOW", "CRIT") else "white"),
             ("KEY %s %s" % (last_key, ago(key_t, now) if key_t else ""), "white"),
             ("LAPTOP %s" % ("link " + ago(host_t, now) if host_t is not None else "not heard yet"), "grey"),
             ("", "white")]
    lines += [(t, "white") for t in laptop[:6]] + [("", "white")] * (6 - len(laptop[:6]))
    lines.append(("SPEC %s" % (" ".join(str(v) for v in spec[:4]) if spec else "-"), "grey"))
    lines.append(("UP %02d:%02d:%02d" % (up // 3600, up // 60 % 60, up % 60), "grey"))
    lines.append(("", "white"))
    return lines[:15]


def motion_power():
    on = not sense.value() if SENSE_ACTIVE_LOW else bool(sense.value())   # opto module: MOTION power present
    return 1 if on else 0


def handle(line):
    global source, capacity_wh, used_wh, host_t, spec_last
    host_t = time.ticks_ms()
    if line.strip().upper().startswith("SHOW"):
        show(line.strip()[4:].strip().split("|"))
        return
    parts = line.strip().upper().split()
    if not parts:
        return
    try:
        if parts[0] == "PING":
            out("PONG OpenGonio-hub 4 POWER %d" % motion_power())
        elif parts[0] == "POWER?":
            out("POWER %d" % motion_power())
        elif parts[0] == "BAND":
            n = None if parts[1] == "OFF" else int(parts[1])
            if n is not None and not 0 <= n < len(bands):
                raise ValueError("band out of range")
            band(n)
        elif parts[0] == "SPEC?":                # "SPEC? <id>": the reply echoes the id so the host can match it
            rid = ("#%d " % int(parts[1])) if len(parts) > 1 else ""
            spec_last = spectral()
            out("SPEC " + rid + " ".join(str(v) for v in spec_last))
        elif parts[0] == "BATT?":
            out(batt_line()[1])
        elif parts[0] == "SOURCE":               # after a full charge: SOURCE PACK, or SOURCE USBC 74 (the bank's Wh)
            if parts[1] not in ("WALL", "PACK", "USBC"):
                raise ValueError("source is WALL, PACK or USBC")
            source, capacity_wh, used_wh = parts[1], float(parts[2]) if len(parts) > 2 else 0.0, 0.0
            with open("source.txt", "w") as f:
                f.write("%s %s" % (source, capacity_wh))
            out(batt_line()[1])
        elif parts[0] == "SCREEN":               # SCREEN ON / OFF: saved; the hub restarts to free or take the pins
            if parts[1] not in ("ON", "OFF"):
                raise ValueError("SCREEN ON or SCREEN OFF")
            with open("screen.txt", "w") as f:
                f.write(parts[1])
            out("SCREEN %s (restarting)" % parts[1])
            time.sleep_ms(200)
            import machine
            machine.reset()
        elif parts[0] == "ENC?":
            out("ENC " + " ".join("%.3f" % read_angle(b) for b in buses))
        else:
            out("ERR unknown " + parts[0])
    except Exception as e:                  # bad input must never stop the hub
        out("ERR %s" % e)


power = motion_power()
out("POWER %d" % power)
show(["OpenGonio", "ready", "", "HOME START STOP", "LIGHT NEXT PAUSE"])
tft = None
drawn = []
screen_t = time.ticks_ms()
if screen_on:
    try:
        tft = ST7789(SPI(1, baudrate=40_000_000, sck=Pin(SCREEN_PINS["SCK"]), mosi=Pin(SCREEN_PINS["MOSI"])),
                     Pin(SCREEN_PINS["DC"], Pin.OUT), Pin(SCREEN_PINS["CS"], Pin.OUT), MADCTL)
        tft.init()
        tft.clear(BLACK)
        drawn = [None] * 15
    except Exception as e:                  # a missing or miswired screen must never stop the hub
        out("ERR screen %s" % e)
        tft = None
COLOURS = {"white": WHITE, "green": GREEN, "red": RED, "amber": AMBER, "grey": GREY}
buf = ""
ubuf = ""
while True:
    now = time.ticks_ms()
    for name, pin in btn.items():          # debounced falling edge = press
        v = pin.value()
        if v != last[name] and time.ticks_diff(now, since[name]) > DEBOUNCE_MS:
            since[name] = now
            last[name] = v
            if v == 0:
                out("BTN " + name)
                last_key, key_t = name, now
    if motion_power() != power:
        power = motion_power()
        out("POWER %d" % power)
        if not power:
            band(None)
    if time.ticks_diff(now, batt_t) >= 1000:   # once a second: energy used and the battery state
        dt, batt_t = time.ticks_diff(now, batt_t) / 3_600_000, now
        reading, line = batt_line()
        if reading:
            used_wh += reading[0] * reading[1] * dt
        state = line.split()[-1]
        if state != batt:
            batt = state
            out(line)
            if state == "CRIT":
                out("BTN PAUSE")            # the run stops at its next safe point, as if PAUSE were pressed
                show(["BATTERY", "CRITICAL", "", "charge or plug", "in the adapter"])
    while poll.poll(0):
        ch = sys.stdin.read(1)
        if ch in "\r\n":
            handle(buf)
            buf = ""
        elif len(buf) < 256:
            buf += ch
    while uart.any():
        try:
            ch = uart.read(1).decode()
        except Exception:                  # noise on the Pi link must never stop STOP / POWER handling
            continue
        if ch in "\r\n":
            handle(ubuf)
            ubuf = ""
        elif len(ubuf) < 256:
            ubuf += ch
    if tft and time.ticks_diff(now, screen_t) >= 500:   # twice a second: redraw only the lines that changed
        screen_t = now
        for i, (text, colour) in enumerate(screen_lines(now, power, source, batt, last_key, key_t, host_t, laptop_lines,
                                                        spec_last, boot_t)):
            if drawn[i] != (text, colour):
                try:
                    tft.line(i, text, COLOURS[colour], BLACK)
                    drawn[i] = (text, colour)
                except Exception:           # keep STOP / POWER handling alive whatever the screen does
                    pass
    time.sleep_ms(2)
