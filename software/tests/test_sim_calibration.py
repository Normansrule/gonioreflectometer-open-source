"""Calibration, lamp drift and the simulated machine: capture -> verify -> calibrate -> curve with no hardware."""
import datetime as dt
import json
import math
import struct
import zlib

import numpy as np
import pytest

from opengonio.calibration import Calibration, load_calibration
from opengonio.gantry.config import load_config
from opengonio.gantry.fluidnc import FluidNC, RecordingTransport
from opengonio.gantry.gantry import Gantry
from opengonio.imageio import read_png, write_png


@pytest.fixture
def cfg():
    return load_config()


def test_png_round_trip(tmp_path):
    g = np.arange(12 * 7, dtype=np.uint8).reshape(12, 7)
    rgb = np.dstack([g, 255 - g, g // 2])
    write_png(tmp_path / "g.png", g)
    write_png(tmp_path / "c.png", rgb)
    assert (read_png(tmp_path / "g.png") == g).all()
    assert (read_png(tmp_path / "c.png") == rgb).all()


def _png_with_filter(a, f):
    """Encode grey rows with PNG filter f (1 Sub, 2 Up, 3 Average, 4 Paeth) to test the decoder."""
    a = a.astype(int)
    rows = []
    for y in range(a.shape[0]):
        prev = a[y - 1] if y else np.zeros(a.shape[1], int)
        out = []
        for x in range(a.shape[1]):
            l = a[y, x - 1] if x else 0
            c = prev[x - 1] if x else 0
            p = {1: l, 2: prev[x], 3: (l + prev[x]) // 2}.get(f)
            if f == 4:
                pa, pb, pc = abs(prev[x] - c), abs(l - c), abs(l + prev[x] - 2 * c)
                p = l if pa <= pb and pa <= pc else prev[x] if pb <= pc else c
            out.append((a[y, x] - p) & 255)
        rows.append(bytes([f]) + bytes(out))
    ch = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))  # noqa: E731
    h, w = a.shape
    return b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)) + \
        ch(b"IDAT", zlib.compress(b"".join(rows))) + ch(b"IEND", b"")


@pytest.mark.parametrize("f", [1, 2, 3, 4])
def test_png_filters(tmp_path, f):
    a = np.random.default_rng(f).integers(0, 256, (9, 11)).astype(np.uint8)
    (tmp_path / "f.png").write_bytes(_png_with_filter(a, f))
    assert (read_png(tmp_path / "f.png") == a).all()


def test_offsets_only_change_gcode(cfg):
    t = RecordingTransport.for_machine(cfg)
    g = Gantry(cfg, FluidNC(t, timeout_s=1), offsets={"M3": 0.4})
    g.home()
    g.move({"M4": 60.0, "M3": 30.0})
    assert t.lines[-2:] == ["G53 G1 X40.0000 Y209.6000 F600", "G4 P0"]     # command = true - offset - home (grblHAL zero)
    assert g.position["M3"] == 30.0                              # software keeps true angles


def test_brdf_from_white_is_lambert(cfg):
    cal = Calibration()
    cal.set("dark_counts", 4.0)
    cal.set("white", {"counts": 4.0 + 100 * math.cos(math.radians(45)), "theta_i_deg": 45.0, "rho": 1.0})
    # a Lambertian sample with the same reflectance gives counts proportional to cos(theta_i)
    for ti in (0, 30, 60):
        c = 4.0 + 100 * math.cos(math.radians(ti))
        assert abs(cal.brdf(c, ti) - 1 / math.pi) < 1e-9


def test_calibration_file_loads_and_stale():
    cal = load_calibration()
    assert set(cal.offsets) == {"M4", "M3", "M2", "M1"}
    cal.set("white", {"counts": 1, "theta_i_deg": 45, "rho": 0.99}, dt.date(2026, 1, 1))
    assert cal.stale(dt.date(2026, 3, 1)) == ["white (2026-01-01)"]
    assert cal.stale(dt.date(2026, 1, 20)) == []


def test_sim_demo_all_pass(tmp_path, cfg):
    from opengonio.sim import demo
    rep = demo(cfg, tmp_path)        # calibration dated today: the runs are stamped with today's date, so a fixed date goes stale
    assert rep["result"] == "ALL PASS", rep
    saved = load_calibration(tmp_path / "calibration.yaml")
    assert abs(saved.offsets["M3"] - 0.37) <= 0.15


def test_cli_sim_capture_verify_calibrate(tmp_path, capsys):
    from opengonio.cli import main
    c = ["--cal", str(tmp_path / "cal.yaml")]
    sim = c + ["--sim", "mirror", "--sim-error", "M3=-0.6"]
    assert main(sim + ["capture", "mirror", "--theta", "40", "--out", str(tmp_path / "a")]) == 0
    assert main(c + ["verify", str(tmp_path / "a")]) == 1                    # WARN: 0.6 deg off
    assert main(c + ["calibrate", "mirror", str(tmp_path / "a")]) == 0
    assert main(sim + ["capture", "mirror", "--theta", "40", "--out", str(tmp_path / "b")]) == 0
    capsys.readouterr()
    assert main(c + ["verify", str(tmp_path / "b")]) == 0
    assert abs(json.loads(capsys.readouterr().out)["mirror_peak_error_deg"]) <= 0.1


def test_drifting_lamp_fails(tmp_path, cfg):
    from opengonio.cli import main
    c = ["--cal", str(tmp_path / "cal.yaml")]
    assert main(c + ["--sim", "matte", "--sim-drift", "0.5", "capture", "inplane", "--step", "20", "--out", str(tmp_path / "d")]) == 0
    assert main(c + ["verify", str(tmp_path / "d")]) == 2
    assert main(c + ["--sim", "matte", "capture", "inplane", "--step", "20", "--out", str(tmp_path / "s")]) == 0
    assert main(c + ["verify", str(tmp_path / "s")]) == 0


def test_warmup_settle_time(tmp_path, cfg):
    from opengonio.station import run_warmup
    g = Gantry(cfg, FluidNC(RecordingTransport.for_machine(cfg), timeout_s=1))
    g.home()

    class Lamp:                       # brightness rises 10 % with a 60 s time constant
        k = 0
        def grab(self):
            v = 100 * (1 - 0.1 * math.exp(-self.k * 10 / 60)); self.k += 1
            return np.full((9, 9), v)
    rep = run_warmup(g, Lamp(), tmp_path, minutes=10, sleep=lambda s: None)
    assert 180 <= rep["settle_s"] <= 260 and rep["change_pct"] > 9            # 0.5 % of the end: ~3 time constants
    assert (tmp_path / "warmup.csv").read_text().count("\n") == 62
