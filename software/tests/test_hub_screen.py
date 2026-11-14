"""Optional hub status screen (firmware/hub/main.py): the ST7789 driver's bytes and the status lines, run on a laptop
with stand-ins for MicroPython's machine pins, SPI and framebuf (the screen itself needs the board)."""
import ast
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def firmware(*names):
    """Exec the named top-level functions / classes of the hub firmware into one namespace."""
    tree = ast.parse((ROOT / "firmware/hub/main.py").read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    clock = types.SimpleNamespace(sleep_ms=lambda ms: None, ticks_ms=lambda: 0,
                                  ticks_diff=lambda a, b: a - b)
    ns = {"time": clock}
    exec(compile(ast.Module(nodes, []), "main.py", "exec"), ns)
    return ns


class Pin:
    def __init__(self):
        self.v = None

    def value(self, v=None):
        self.v = v


class SPI:
    def __init__(self):
        self.log, self.pins = [], None

    def write(self, b):
        self.log.append((self.pins["dc"].v, bytes(b)))


class FrameBuffer:                       # 1-bit stand-in: text() lights the first pixel of each character cell
    def __init__(self, buf, w, h, fmt):
        self.w, self.on = w, set()

    def fill(self, c):
        self.on.clear()

    def text(self, s, x, y, c):
        for i, ch in enumerate(s):
            if ch != " ":
                self.on.add((x + i * 8, y))

    def pixel(self, x, y):
        return (x, y) in self.on


def test_rgb565_is_high_byte_first():
    rgb = firmware("rgb")["rgb"]
    assert rgb(255, 0, 0) == b"\xf8\x00" and rgb(0, 0, 255) == b"\x00\x1f" and rgb(255, 255, 255) == b"\xff\xff"


def test_driver_init_window_and_one_text_line():
    import sys
    ns = firmware("rgb", "ST7789")
    sys.modules["framebuf"] = types.SimpleNamespace(FrameBuffer=FrameBuffer, MONO_HLSB=0)
    try:
        spi, dc, cs = SPI(), Pin(), Pin()
        spi.pins = {"dc": dc}
        t = ns["ST7789"](spi, dc, cs, 0x60)
        t.init()
        cmds = [b[0] for d, b in spi.log if d == 0]
        assert cmds == [0x01, 0x11, 0x3A, 0x36, 0x21, 0x13, 0x29]            # reset, wake, RGB565, rotate, invert, on
        assert (1, b"\x55") in spi.log and (1, b"\x60") in spi.log
        spi.log.clear()
        fg, bg = ns["rgb"](255, 255, 255), ns["rgb"](0, 0, 0)
        t.line(2, "AB", fg, bg)
        assert spi.log[0] == (0, b"\x2a") and spi.log[1] == (1, bytes([0, 0, 1, 63]))     # columns 0-319
        assert spi.log[2] == (0, b"\x2b") and spi.log[3] == (1, bytes([0, 32, 0, 47]))    # rows 32-47 (line 2)
        assert spi.log[4] == (0, b"\x2c")
        dc_, data = spi.log[5]
        assert dc_ == 1 and len(data) == 320 * 16 * 2                                     # one 320 x 16 line, 2 bytes a pixel
        assert data[0:4] == fg + fg and data[640:644] == fg + fg                          # font pixel (0,0) -> 2 x 2
        assert data[4:8] == bg + bg and data[32:36] == fg + fg                            # 'B' starts at x 8 -> byte 32
    finally:
        sys.modules.pop("framebuf", None)


def test_status_lines():
    ns = firmware("ago", "screen_lines")
    lines = ns["screen_lines"](125_000, 1, "WALL", "OK", "START", 120_000, 124_000, ["Run 3 of 31"], [1, 2, 3, 4, 5], 0)
    text = [t for t, _ in lines]
    assert len(lines) == 15 and all(len(t) <= 20 for t in text)
    assert lines[1] == ("MOTOR POWER ON", "green") and "KEY START 5s" in text and "LAPTOP link 1s" in text
    assert "Run 3 of 31" in text and "SPEC 1 2 3 4" in text and "UP 00:02:05" in text
    off = ns["screen_lines"](1000, 0, "PACK", "CRIT", "-", 0, None, [], None, 0)
    assert off[1] == ("MOTOR POWER OFF", "red") and off[2][1] == "amber" and off[4][0] == "LAPTOP not heard yet"
