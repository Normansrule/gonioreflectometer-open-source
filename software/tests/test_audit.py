"""Regression tests for the 2026 technical audit (docs/audit/closure.md). Each test is named after the audit probe
or finding it closes; each failed on the pre-audit code (c19a847) and passes now."""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from opengonio.gantry.config import load_config
from opengonio.gantry.fluidnc import FluidNC, RecordingTransport
from opengonio.gantry.gantry import Gantry, GantryError
from opengonio.runrecord import AcquisitionError, RunExistsError, make_run_dir, unique_child
from opengonio.station import run_plan
from opengonio.verify import verify

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def cfg():
    return load_config()


def homed(cfg, transport=None):
    t = transport or RecordingTransport.for_machine(cfg)
    g = Gantry(cfg, FluidNC(t, timeout_s=1))
    g.home()
    return g, t


class Cam:
    """Fake camera: a flat grey RGB frame."""
    def __init__(self, v=120, fail_at=None):
        self.v, self.n, self.fail_at = v, 0, fail_at

    def grab(self):
        self.n += 1
        if self.fail_at is not None and self.n >= self.fail_at:
            raise RuntimeError("camera disconnected")
        return np.full((40, 50, 3), self.v, np.uint8)

    def configure(self, s):
        return {"exposure_ms": s.exposure_ms}

    def readback(self):
        return {"exposure_ms": 20.0}


def png_save(p, img):
    from opengonio.imageio import write_png
    write_png(p, img)


def manifest(d):
    return json.loads((Path(d) / "manifest.json").read_text())


def good_run(cfg, tmp_path, name="run"):
    g, _ = homed(cfg)
    plan = [{"M4": 60.0, "M3": 30.0}, {"M4": 70.0, "M3": 35.0}]
    return run_plan(g, Cam(), plan, tmp_path / name, png_save, "Swatch", sleep=lambda s: None)


# ---- F01 / F04: verification and run schema ------------------------------------------------------------------
def test_V01_zero_shot_run_fails(cfg, tmp_path):
    g, _ = homed(cfg)
    out = run_plan(g, Cam(), [], tmp_path / "empty", png_save, "Swatch", sleep=lambda s: None)
    rep = verify(out, cfg)
    assert rep["result"] == "FAIL" and not rep["acquisition_complete"] and "run has no shots" in rep["problems"]


def test_V02_text_file_named_png_fails(cfg, tmp_path):
    out = good_run(cfg, tmp_path)
    m = manifest(out)
    f = out / m["shots"][0]["file"]
    f.write_text("not an image")
    rep = verify(out, cfg)
    assert rep["result"] == "FAIL" and not rep["data_valid"]
    assert m["shots"][0]["file"] in rep["corrupt"]


def test_V02_tampered_image_fails_on_hash(cfg, tmp_path):
    out = good_run(cfg, tmp_path)
    m = manifest(out)
    png_save(out / m["shots"][1]["file"], np.full((40, 50, 3), 7, np.uint8))     # valid PNG, different content
    rep = verify(out, cfg)
    assert rep["result"] == "FAIL" and any("hash" in p for p in rep["invalid_shots"]["1"])


def test_V03_malformed_spectral_fails_and_valid_spectral_only_run_passes(cfg, tmp_path):
    g, _ = homed(cfg)
    plan = [{"M4": 60.0, "M3": 30.0}]
    ok = run_plan(g, None, plan, tmp_path / "spec", None, "Swatch", spectral=lambda: list(range(10)),
                  sleep=lambda s: None, reference=False)
    assert verify(ok, cfg)["result"] == "PASS"
    m = manifest(ok)
    for bad in ([1] * 9, [1] * 9 + [70000], [1] * 9 + ["x"], None):
        m["shots"][0]["spectral"] = bad
        (ok / "manifest.json").write_text(json.dumps(m))
        rep = verify(ok, cfg)
        assert rep["result"] == "FAIL" and not rep["data_valid"], bad


def test_V04_out_of_range_pose_fails(cfg, tmp_path):
    out = good_run(cfg, tmp_path)
    m = manifest(out)
    m["shots"][0]["pose"]["M3"] = 999.0
    (out / "manifest.json").write_text(json.dumps(m))
    rep = verify(out, cfg)
    assert rep["result"] == "FAIL" and "0" in rep["unsafe"]


def test_reported_pose_mismatch_fails(cfg, tmp_path):
    out = good_run(cfg, tmp_path)
    m = manifest(out)
    m["shots"][0]["reported_pose"]["M3"] += 0.5
    (out / "manifest.json").write_text(json.dumps(m))
    assert any("controller reported" in p for p in verify(out, cfg)["invalid_shots"]["0"])


def test_planned_count_status_and_numbering(cfg, tmp_path):
    out = good_run(cfg, tmp_path)
    assert verify(out, cfg)["acquisition_complete"]
    m = manifest(out)
    for change in ({"planned": 3}, {"status": "error", "finished": False}, {"shots": [m["shots"][0], m["shots"][0]]}):
        (out / "manifest.json").write_text(json.dumps({**m, **change}))
        rep = verify(out, cfg)
        assert rep["result"] == "FAIL" and not rep["acquisition_complete"], change


def test_run_dir_is_exclusive(cfg, tmp_path):
    good_run(cfg, tmp_path, "r")
    with pytest.raises(RunExistsError):
        good_run(cfg, tmp_path, "r")
    g, _ = homed(cfg)
    run_plan(g, Cam(), [{"M4": 60.0, "M3": 30.0}], tmp_path / "r", png_save, "Swatch", sleep=lambda s: None, overwrite=True)
    assert len(list(tmp_path.glob("r.replaced-*"))) == 1                  # old run moved aside, not deleted
    a, b = unique_child(tmp_path, "job", 0.0), unique_child(tmp_path, "job", 0.0)
    assert a != b and a.exists() and b.exists()
    with pytest.raises(RunExistsError):
        make_run_dir(a.parent)


# ---- F03 / F17: transactional acquisition --------------------------------------------------------------------
def test_C01_dark_run_switches_lamp_off_first(cfg, tmp_path):
    g, t = homed(cfg)
    g.light("white", True)
    out = run_plan(g, Cam(3), [{"M4": 45.0, "M3": 0.0}], tmp_path / "dark", png_save, "dark", light=None,
                   sleep=lambda s: None, reference=False)
    first_shot_move = next(i for i, ln in enumerate(t.lines) if ln.startswith("G53 G1 X25"))   # M4 45 deg = 25 from its home
    assert "M63 P4" in t.lines[t.lines.index("M62 P4") + 1:first_shot_move]
    assert manifest(out)["lights"].startswith("all off")


def test_C01_dark_run_refused_when_a_light_will_not_go_off(cfg, tmp_path):
    g, _ = homed(cfg)
    g.light = lambda name, on: (_ for _ in ()).throw(GantryError("output stuck"))
    with pytest.raises(AcquisitionError):
        run_plan(g, Cam(3), [{"M4": 45.0, "M3": 0.0}], tmp_path / "dark", png_save, "dark", light=None,
                 sleep=lambda s: None, reference=False)
    m = manifest(tmp_path / "dark")
    assert m["status"] == "error" and not m["finished"] and not m["shots"]


def test_C02_failed_save_stops_the_run(cfg, tmp_path):
    g, t = homed(cfg)
    with pytest.raises(AcquisitionError):
        run_plan(g, Cam(), [{"M4": 60.0, "M3": 30.0}] * 3, tmp_path / "s", lambda p, img: False, "Swatch",
                 sleep=lambda s: None)
    m = manifest(tmp_path / "s")
    assert m["status"] == "error" and "writer returned False" in m["errors"][0]
    assert t.lines[-1] == "M63 P4"                                        # lamp off after the failure
    assert verify(tmp_path / "s", cfg)["result"] == "FAIL"


def test_C03_interrupt_during_warmup_turns_lamp_off(cfg, tmp_path):
    g, t = homed(cfg)

    def ctrl_c(s):
        raise KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt):
        run_plan(g, Cam(), [{"M4": 60.0, "M3": 30.0}], tmp_path / "w", png_save, "Swatch", sleep=ctrl_c, warmup_s=60)
    m = manifest(tmp_path / "w")
    assert m["status"] == "aborted" and t.lines[-1] == "M63 P4" and not g.light_state["white"]


def test_C04_cleanup_failure_still_writes_manifest(cfg, tmp_path):
    g, _ = homed(cfg)
    real = g.light

    def light(name, on):
        if not on:
            raise GantryError("controller link lost")
        real(name, on)
    g.light = light
    with pytest.raises(RuntimeError, match="camera disconnected"):            # the original error, not the cleanup one
        run_plan(g, Cam(fail_at=2), [{"M4": 60.0, "M3": 30.0}] * 3, tmp_path / "c", png_save, "Swatch",
                 sleep=lambda s: None)
    m = manifest(tmp_path / "c")
    assert m["status"] == "error" and "camera disconnected" in m["errors"][0]
    assert any("controller link lost" in e for e in m["cleanup_errors"])


def test_M05_station_abort_records_and_lamp_off(cfg, tmp_path):
    import itertools
    from opengonio.gantry.hub import FakeHub
    from opengonio.station import Station
    g = Gantry(cfg, FluidNC(RecordingTransport.for_machine(cfg), timeout_s=1))
    tick = itertools.count(0.0, 5.0)
    st = Station(cfg, g, FakeHub(), Cam(fail_at=4), tmp_path, save=png_save, clock=lambda: next(tick))
    st.handle("BTN", "START")
    for _ in range(40):
        st.tick()
    m = manifest(st.run_dir)
    assert not st.running and m["status"] == "error" and "camera disconnected" in m["errors"][0]
    assert g.light_state.get("white") is False
    assert verify(st.run_dir, cfg)["result"] == "FAIL"


def test_F17_station_scan_job_writes_scanner_format(cfg, tmp_path):
    import itertools
    from opengonio.gantry.hub import FakeHub
    from opengonio.station import Station
    c10 = cfg.with_phase(max(cfg.installed_phase, 10))
    g = Gantry(c10, FluidNC(RecordingTransport.for_machine(c10), timeout_s=1))
    tick = itertools.count(0.0, 5.0)
    st = Station(c10, g, FakeHub(), Cam(), tmp_path, save=png_save, clock=lambda: next(tick))
    while st.job_name != "3D scan":
        st.handle("BTN", "NEXT")
    st.handle("BTN", "START")
    for _ in range(len(st.plan) + 30):
        st.tick()
    assert st.phase == "await_background"
    st.handle("BTN", "START")
    for _ in range(len(st.plan) + 30):
        st.tick()
    meta = json.loads((st.run_dir / "scan.json").read_text())
    assert meta["schema"] == 2 and meta["background"] and len(meta["plan"]) == len(st.plan)
    assert meta["image_ext"] == ".png" and (st.run_dir / "images" / "img_0000.png").exists()
    assert (st.run_dir / "background" / f"img_{len(st.plan) - 1:04d}.png").exists()     # what `scan hull` reads


def test_S02_scanner_camera_failure_turns_lights_off(cfg, tmp_path, monkeypatch):
    from opengonio.gantry.hub import FakeHub
    monkeypatch.setattr("opengonio.imageio.save_image", lambda p, img: (png_save(p, img), True)[1])   # no OpenCV needed
    from opengonio.scan.run import run_scan
    c10 = cfg.with_phase(max(cfg.installed_phase, 10))
    c10 = replace(c10, scan={**c10.scan, "calibration": None})
    g, t = homed(c10, RecordingTransport.for_machine(c10))
    hub = FakeHub()
    with pytest.raises(RuntimeError, match="camera disconnected"):
        run_scan(c10, g, Cam(fail_at=3), hub, tmp_path / "scan", 20.0, ps=False)
    meta = json.loads((tmp_path / "scan" / "scan.json").read_text())
    assert meta["status"] == "error" and len(meta["files"]) == 2 and t.lines[-1] == "M63 P4"
    assert "BAND OFF" in hub.sent


# ---- F05-F08: motion trust, events, power -------------------------------------------------------------------
class LostSteps(RecordingTransport):
    """Controller that ignores Y (M3) moves: the motor stalled."""
    def write(self, data: bytes) -> None:
        txt = data.decode()
        if txt.startswith("G53 G1") and "Y" in txt:
            txt = " ".join(w for w in txt.split() if not w.startswith("Y"))
        super().write(txt.encode())


def test_M01_endpoint_mismatch_refuses_and_clears_homing(cfg):
    t = LostSteps(); t.homes = RecordingTransport.for_machine(cfg).homes
    g, _ = homed(cfg, t)
    with pytest.raises(GantryError, match="end position mismatch"):
        g.move({"M3": 30.0})
    assert not g.homed
    with pytest.raises(GantryError, match="not homed"):
        g.move({"M4": 60.0})


def test_M02_alarm_invalidates_position(cfg):
    g, t = homed(cfg)
    t.state = "Alarm"
    with pytest.raises(GantryError, match="Alarm"):
        g.move({"M4": 60.0})
    assert not g.homed                                                      # re-home before any move
    with pytest.raises(GantryError, match="not homed"):
        g.move({"M4": 60.0})


def test_homing_reaches_configured_home(cfg):
    g, _ = homed(cfg)
    assert g.homed == set(cfg.active_axes) and abs(g.reported["M4"] - 180.0) < 1e-6


def test_firmware_homing_position_matches_machine_yaml(cfg):
    import yaml
    fw = yaml.safe_load((ROOT / "firmware/fluidnc/config.yaml").read_text())
    for k, ax in cfg.axes.items():
        assert float(fw["axes"][ax.fluidnc_axis.lower()]["homing"]["mpos_mm"]) == ax.home_deg, k
    assert fw["start"]["must_home"] is True


def test_M03_hub_keeps_stop_during_spectral_read():
    from opengonio.gantry.hub import FakeHub, SafetyInterrupt
    hub = FakeHub(["BTN NEXT", "BTN STOP", "SPEC #1 1 2 3 4 5 6 7 8 9 10"])
    with pytest.raises(SafetyInterrupt):
        hub.spectral(timeout_s=1)
    assert [hub.poll().value, hub.poll().value] == ["NEXT", "STOP"]         # nothing dropped, in order


def test_M03_hub_rejects_bad_lines_and_stale_replies():
    from opengonio.gantry.hub import FakeHub, parse
    for bad in ("BTN EXPLODE", "POWER 2", "BTN STOP\x00junk", "X" * 300, "SPEC"):
        ev = parse(bad)
        assert ev is None or ev.kind == "SPEC", bad
    hub = FakeHub(["SPEC #9 9 9 9 9 9 9 9 9 9 9", "SPEC #1 1 2 3 4 5 6 7 8 9 10"])
    assert hub.spectral(timeout_s=1) == list(range(1, 11))                 # stale #9 skipped
    with pytest.raises(ValueError):
        FakeHub(["SPEC #1 1 2 3"]).spectral(timeout_s=1)
    with pytest.raises(ValueError):
        FakeHub(["SPEC #1 1 2 3 4 5 6 7 8 9 99999"]).spectral(timeout_s=1)


def test_M04_station_power_events(cfg, tmp_path):
    import itertools
    from opengonio.gantry.hub import FakeHub
    from opengonio.station import Station
    t = RecordingTransport.for_machine(cfg)
    g = Gantry(cfg, FluidNC(t, timeout_s=1))
    tick = itertools.count(0.0, 5.0)
    st = Station(cfg, g, FakeHub(), Cam(), tmp_path, save=png_save, clock=lambda: next(tick))
    st.handle("BTN", "START")
    for _ in range(15):
        st.tick()
    st.handle("POWER", "0")
    m = manifest(st.run_dir)
    assert not st.running and m["status"] == "aborted" and not g.homed
    st.handle("POWER", "1")
    assert t.lines[-1] == "M122 I" and not g.homed and not st.running        # drivers re-initialised, nothing resumes


def test_panel_light_locked_while_running(cfg):
    from opengonio.gantry.panel import Panel
    g, t = homed(cfg)
    p = Panel(g, [{"M4": 60.0, "M3": 30.0}] * 3)
    p.handle("BTN", "START")
    n = len(t.lines)
    p.handle("BTN", "LIGHT")
    assert not any(ln.startswith("M6") for ln in t.lines[n:])


# ---- F02, F11-F16: camera, calibration, radiometry ----------------------------------------------------------
def test_R01_one_pixel_convention_rgb(tmp_path):
    from opengonio.imageio import default_reader, read_png, save_image, signal_plane
    img = np.zeros((4, 6, 3), np.uint8); img[..., 0] = 200; img[..., 2] = 20     # red-ish, RGB order
    assert save_image(tmp_path / "a.png", img)
    for read in (default_reader(), read_png):
        back = read(tmp_path / "a.png")
        assert back.shape == (4, 6, 3) and back[0, 0, 0] == 200 and back[0, 0, 2] == 20, read
    assert signal_plane(img)[0, 0] == pytest.approx(220 / 3)


def test_R01_linearise_per_pixel_before_averaging():
    from opengonio.imageio import region_mean
    a = np.tile(np.array([[0, 255]], np.uint8), (9, 9))                       # half black, half white
    lin = lambda x: (np.asarray(x, float) / 255.0) ** 2.2 * 255.0           # noqa: E731
    assert region_mean(a, linear=lin) == pytest.approx(127.5)              # mean of linear values
    assert lin(region_mean(a)) < 60                                         # linearising the mean is wrong


def test_R02_curve_uses_capture_snapshot_and_recalibration_is_separate(cfg, tmp_path):
    from opengonio.calibration import Calibration, merged
    from opengonio.verify import curve
    cap = Calibration(merged({"gamma": 1.0, "dark_counts": 0.0}), tmp_path / "cal.yaml")
    g, _ = homed(cfg)
    out = run_plan(g, Cam(), [{"M4": 45.0, "M3": 0.0}], tmp_path / "r", png_save, "Swatch", sleep=lambda s: None,
                   cal=cap)
    snap_id = manifest(out)["calibration"]["id"]
    later = Calibration(merged({"gamma": 2.2, "dark_counts": 10.0}), tmp_path / "cal2.yaml")
    c1 = curve(out, cfg, cal=later)
    assert json.loads(c1.with_suffix(".json").read_text())["calibration"]["id"] == snap_id
    row = c1.read_text().splitlines()[1].split(",")
    assert float(row[11]) == pytest.approx(120.0, abs=0.5)                  # linear = counts (gamma 1, dark 0)
    c2 = curve(out, cfg, cal=later, recalibrate=True)
    assert c2.name.startswith("curve_recal-") and c1.exists() and c2 != c1
    assert json.loads(c2.with_suffix(".json").read_text())["calibration"]["capture_id"] == snap_id


def test_R03_white_reference_checks(cfg, tmp_path):
    from opengonio.calibration import Calibration, CalibrationError, from_white, merged
    cal = Calibration(merged({"gamma": 1.0, "dark_counts": 2.0}), tmp_path / "c.yaml")
    g, _ = homed(cfg)
    out = run_plan(g, Cam(150), [{"M4": 45.0, "M3": 0.0}] * 3, tmp_path / "w", png_save, "white",
                   sleep=lambda s: None, reference=False, exposure_ms=20.0)
    with pytest.raises(CalibrationError):
        from_white(cal, out, cfg, rho=1.5)
    w = from_white(cal, out, cfg, rho=0.98, rho_source="cert 123")
    assert w["rho_source"] == "cert 123" and w["linear"] == pytest.approx(148.0)
    assert cal.brdf_problems(20.0) == [] and cal.brdf_problems(40.0)        # exposure mismatch is reported
    sat = run_plan(g, Cam(255), [{"M4": 45.0, "M3": 0.0}] * 3, tmp_path / "sat", png_save, "white",
                   sleep=lambda s: None, reference=False, exposure_ms=20.0)
    with pytest.raises(CalibrationError):
        from_white(cal, sat, cfg)
    d = manifest(out); d["status"] = "aborted"; (out / "manifest.json").write_text(json.dumps(d))
    with pytest.raises(CalibrationError):
        from_white(cal, out, cfg)


def test_R03_linearity_fit_rejects_weak_series():
    from opengonio.calibration import CalibrationError, linearity
    with pytest.raises(CalibrationError):
        linearity([2, 4], [20, 40], 0)                                     # too few points
    with pytest.raises(CalibrationError):
        linearity([2, 2.5, 3], [20, 25, 30], 0)                            # under 4x range
    with pytest.raises(CalibrationError):
        linearity([2, 4, 8, 16], [60, 20, 90, 30], 0)                      # noisy / non-monotonic
    assert linearity([2, 4, 8, 16], [20, 40, 80, 160], 0)["gamma"] == pytest.approx(1.0, abs=1e-3)


def test_F14_roi_valid_region_and_rejection(cfg):
    from opengonio.roi import field_mm, sample_roi
    shape = (int(cfg.camera["height"]), int(cfg.camera["width"]))
    fw, fh = field_mm(cfg)
    assert 100 < fw < 150 and 80 < fh < 120
    r = sample_roi(cfg, {"M4": 45.0, "M3": 0.0}, shape)
    assert r.valid and 25 < r.area_mm2 < 2 * 3.1416 * 16.2 ** 2 and 0 < r.view_spread_deg < 15
    assert r.mask.shape == shape and 0 < r.mask.mean() < 0.2
    back = sample_roi(cfg, {"M4": 45.0, "M3": 89.0}, shape)
    assert not back.valid


def test_F02_v4l2_readback_must_confirm(monkeypatch):
    from types import SimpleNamespace as NS
    from opengonio.camera.uvc import CameraSettings, CameraSettingsError, v4l2_configure

    def run_factory(exposure_units):
        def run(args, **kw):
            if "-C" in args:
                return NS(returncode=0, stdout=f"auto_exposure: 1\nexposure_time_absolute: {exposure_units}\ngain: 0\n")
            return NS(returncode=0, stdout="")
        return run
    assert v4l2_configure("/dev/video0", CameraSettings(20.0), run=run_factory(200))["exposure_ms"] == 20.0
    with pytest.raises(CameraSettingsError):
        v4l2_configure("/dev/video0", CameraSettings(20.0), run=run_factory(156))   # camera ignored the request


# ---- F18-F21: scanner -------------------------------------------------------------------------------------------
def test_S03_empty_or_missing_calibration_refused(tmp_path, cfg):
    from opengonio.scan.calibrate import solve_ax_yb
    from opengonio.scan.process import _calib
    with pytest.raises(ValueError):
        solve_ax_yb([], [], np.eye(4))
    with pytest.raises(ValueError):
        solve_ax_yb([np.eye(4)] * 3, [np.eye(4)] * 2, np.eye(4))
    with pytest.raises(FileNotFoundError):
        _calib(cfg, {"schema": 2, "calibrated": True, "calibration_file": "scan_calibration.yaml"}, tmp_path)


def test_F18_projection_matches_opencv_with_distortion():
    cv2 = pytest.importorskip("cv2")
    from opengonio.scan.geometry import project
    rng = np.random.default_rng(1)
    pts = rng.uniform(-40, 40, (50, 3)) + [0, 0, 600]
    K = np.array([[3000.0, 0, 1920], [0, 3000.0, 1516], [0, 0, 1]])
    R, t = np.eye(3), np.zeros(3)
    dist = [-0.12, 0.05, 0.001, -0.002]
    uv, _ = project(pts, K, R, t, dist)
    ref, _ = cv2.projectPoints(pts, cv2.Rodrigues(R)[0], t, K, np.array(dist + [0.0]))
    assert np.allclose(uv, ref.reshape(-1, 2), atol=1e-6)
    assert not np.allclose(project(pts, K, R, t)[0], uv)                    # distortion actually applied


def test_F19_hull_refuses_low_coverage_and_huge_grids(cfg, tmp_path):
    from opengonio.scan.carve import carve
    from opengonio.scan.plan import rings_plan
    from opengonio.scan.process import hull
    from opengonio.scan.run import scan_meta
    c10 = cfg.with_phase(max(cfg.installed_phase, 10))
    plan = rings_plan(c10)
    (tmp_path / "images").mkdir(); (tmp_path / "background").mkdir()
    (tmp_path / "scan.json").write_text(json.dumps(scan_meta(c10, plan, background=True, image_ext=".png")))
    for i in range(3):                                                       # 3 of many views captured
        for f in ("images", "background"):
            png_save(tmp_path / f / f"img_{i:04d}.png", np.full((60, 80), 100, np.uint8))
    with pytest.raises(ValueError, match="only 3 of"):
        hull(c10, tmp_path)
    with pytest.raises(MemoryError):
        carve([], [], np.eye(3), half_size_mm=100.0, n=400)


def test_F21_fit_reports_holdout_and_provenance(cfg, tmp_path):
    from opengonio.fit import fit_run
    from opengonio.sim import demo
    rep = demo(cfg.with_phase(max(cfg.installed_phase, 6)), tmp_path)
    run = next(p.parent for p in tmp_path.rglob("fit.json"))
    res = json.loads((run / "fit.json").read_text())
    assert res["holdout"]["rows_held_out"] >= 2 and res["provenance"]["calibration"]["id"]
    assert "one channel" in res["provenance"]["quantity"] and rep["result"] == "ALL PASS"


# ---- F27: scripts ---------------------------------------------------------------------------------------------
def test_F27_scripts_do_not_mask_failures_or_lose_station_config():
    e4 = (ROOT / "scripts/e4.sh").read_text()
    assert "|| echo" not in e4 and "releases/latest" not in e4 and "FLUIDNC_VERSION" in e4
    assert (ROOT / "firmware/fluidnc/FLUIDNC_VERSION").read_text().strip().startswith("v")
    st = (ROOT / "scripts/station.sh").read_text()
    assert "rm -rf ~/opengonio &&" not in st and "calibration.yaml" in st and "opengonio.prev" in st


# ---- F25: packaging -------------------------------------------------------------------------------------------
def test_packaged_config_is_current_and_version_single_sourced():
    from opengonio import __version__
    from opengonio.gantry.config import PACKAGED_CONFIG, REPO_CONFIG
    assert PACKAGED_CONFIG.read_bytes() == REPO_CONFIG.read_bytes(), "run `make build` (packaged machine.yaml is stale)"
    py = (ROOT / "software/pyproject.toml").read_text()
    assert 'dynamic = ["version"]' in py and 'attr = "opengonio.__version__"' in py and '\nversion = "' not in py
    assert __version__.count(".") == 2


def test_config_resolution_order(tmp_path, monkeypatch):
    from opengonio.gantry import config as C
    monkeypatch.delenv("OPENGONIO_CONFIG", raising=False)
    assert C.default_config_path() == C.REPO_CONFIG                         # source checkout
    monkeypatch.setattr(C, "REPO_CONFIG", tmp_path / "none.yaml")
    monkeypatch.setattr(C, "USER_CONFIG", tmp_path / "user.yaml")
    assert C.default_config_path() == C.PACKAGED_CONFIG                     # installed, no init yet
    (tmp_path / "user.yaml").write_text(C.PACKAGED_CONFIG.read_text())
    assert C.default_config_path() == tmp_path / "user.yaml"                # after `opengonio init`
    monkeypatch.setenv("OPENGONIO_CONFIG", str(tmp_path / "x.yaml"))
    assert C.default_config_path() == tmp_path / "x.yaml"
    from opengonio.gantry.config import ConfigError
    with pytest.raises(ConfigError, match="opengonio init"):
        C.load_config()


def test_scan_depth_of_field_check_runs_without_repo_tools(cfg):
    import optics
    from opengonio.scan.plan import scan_dof_mm
    args = (float(cfg.camera["focal_length_mm"]), 650.0, 8.0, float(cfg.camera["pixel_um"]))
    assert scan_dof_mm(*args) == pytest.approx(optics.scan_dof_mm(*args), rel=1e-9)
    import inspect
    from opengonio.scan import plan
    assert "import optics" not in inspect.getsource(plan) and "ImportError" not in inspect.getsource(plan)


# ---- F09: selectable-colour circuit blocked ---------------------------------------------------------------------
def test_F09_colour_led_bank_cannot_be_switched_on(cfg):
    built = replace(cfg, lights={**cfg.lights, "multispectral": {**cfg.lights["multispectral"], "built": True}})
    g, t = homed(built.with_phase(10), RecordingTransport.for_machine(built))
    assert "multispectral" in g.cfg.active_lights and cfg.lights["multispectral"]["blocked"]
    with pytest.raises(GantryError, match="blocked"):
        g.light("multispectral", True)
    assert "M62 P3" not in t.lines
    g.light("multispectral", False)                                          # switching it OFF is always allowed
    loads = (ROOT / "phases/01-power/power_loads.yaml").read_text()
    assert "peak_w: 2.1" in loads


# ---- independent-review follow-ups -------------------------------------------------------------------------------
def test_review_one_clipped_channel_invalidates_region():
    from opengonio.imageio import region_mean
    img = np.zeros((9, 9, 3), np.uint8); img[..., 0] = 255; img[..., 1:] = 150     # red clipped, mean 185
    assert region_mean(img, reject_saturated=True) is None


def test_review_schema2_requires_hash_reported_pose_and_plan(cfg, tmp_path):
    out = good_run(cfg, tmp_path)
    m = manifest(out)
    for change in (lambda m: m["shots"][0].pop("sha256"), lambda m: m["shots"][0].update(reported_pose=None),
                   lambda m: m.update(planned=None)):
        mm = json.loads(json.dumps(m)); change(mm)
        (out / "manifest.json").write_text(json.dumps(mm))
        assert verify(out, cfg)["result"] == "FAIL"


def test_review_white_reference_must_match_current_response_and_exposure():
    from opengonio.calibration import Calibration, merged
    w = {"counts": 150, "linear": 148.0, "theta_i_deg": 45.0, "rho": 0.98, "exposure_ms": 20.0, "dark_counts": 2.0, "gamma": 1.0}
    ok = Calibration(merged({"gamma": 1.0, "dark_counts": 2.0, "white": w}))
    assert ok.brdf_problems(20.0) == []
    assert ok.brdf_problems(None)                                            # run exposure unknown
    stale = Calibration(merged({"gamma": 2.2, "dark_counts": 2.0, "white": w}))   # linearity redone after white
    assert any("gamma" in p for p in stale.brdf_problems(20.0)) and stale.brdf_linear(148.0, 45.0) is None


def test_review_power_loss_and_panel_stop_switch_lamp_off(cfg):
    from opengonio.gantry.panel import Panel
    from opengonio.gantry.safety import on_power
    g, t = homed(cfg)
    g.light("white", True)
    assert "lamp off" in on_power(g, "0") and t.lines[-1] == "M63 P4" and not g.homed
    g, t = homed(cfg)
    p = Panel(g, [{"M4": 60.0, "M3": 30.0}])
    g.light("white", True)
    p.handle("BTN", "STOP")
    assert "M63 P4" in t.lines[-4:] and not g.light_state["white"]


def test_review_blocked_light_enforced_in_code_and_raw_send(cfg, capsys):
    from opengonio.cli import main
    old = replace(cfg, lights={**cfg.lights, "multispectral": {k: v for k, v in cfg.lights["multispectral"].items()
                                                               if k != "blocked"} | {"built": True}})
    g, _ = homed(old.with_phase(10), RecordingTransport.for_machine(old))
    with pytest.raises(GantryError, match="blocked"):                       # an old machine.yaml can't lift the block
        g.light("multispectral", True)
    assert main(["--dry-run", "send", "M62 P3"]) == 3


def test_review_station_start_failure_still_writes_manifest(cfg, tmp_path):
    import itertools
    from opengonio.gantry.hub import FakeHub
    from opengonio.station import Station

    class BadCam(Cam):
        def readback(self):
            raise RuntimeError("camera gone")
    g = Gantry(cfg, FluidNC(RecordingTransport.for_machine(cfg), timeout_s=1))
    tick = itertools.count(0.0, 5.0)
    st = Station(cfg, g, FakeHub(), BadCam(), tmp_path, save=png_save, clock=lambda: next(tick))
    st.handle("BTN", "START")
    m = manifest(st.run_dir)
    assert m["status"] == "error" and "camera gone" in m["errors"][0]


def test_review_run_dir_claim_is_exclusive(tmp_path):
    p = make_run_dir(tmp_path / "r")
    with pytest.raises(RunExistsError):
        make_run_dir(tmp_path / "r")
    assert (p / ".run").exists()


def test_grblhal_settings_current_and_match_machine_yaml(cfg):
    """SKR Pico settings are generated from machine.yaml: steps, travel, homing direction and the report mask."""
    import subprocess
    import sys
    r = subprocess.run([sys.executable, str(ROOT / "tools/grblhal_settings.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
    s = {}
    for ln in (ROOT / "firmware/grblhal/settings.txt").read_text().splitlines():
        ln = ln.split(";")[0].strip()
        if ln:
            k, v = ln.split("=")
            s[k] = float(v)
    assert s["$10"] == 17 and s["$22"] == 15 and s["$62"] == 1           # MPos + Pn; homing, $HX, lock, origin 0; $SLP
    for ax in cfg.axes.values():
        i = "XYZA".index(ax.fluidnc_axis)
        assert abs(s[f"${100 + i}"] - ax.steps_per_deg) < 1e-3
        assert s[f"${130 + i}"] == ax.max_deg - ax.min_deg and ax.home_deg == ax.min_deg
        assert int(s["$23"]) >> i & 1                                         # homes toward the minimum
        assert s[f"${150 + i}"] == ax.microsteps and s[f"${140 + i}"] <= 800  # SKR Pico: fan needed above 0.8 A


def test_hub_firmware_avoids_esp32s3_reserved_pins():
    import ast
    src = (ROOT / "firmware/hub/main.py").read_text()
    vals = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            try:
                vals[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Tuple):
            for t, v in zip(node.targets[0].elts, node.value.elts):
                vals[t.id] = ast.literal_eval(v)
    pins = list(vals["BUTTONS"].values()) + [vals["SENSE_PIN"], vals["UART_TX"], vals["UART_RX"]] + vals["BAND_PINS"]
    pins += [p for pair in vals["I2C_PAIRS"] for p in pair]
    reserved = {0, 3, 45, 46, 19, 20, 43, 44, *range(26, 38)}                 # strapping, USB, flash/PSRAM, UART0 [R86]
    assert len(pins) == len(set(pins)) and not set(pins) & reserved and all(0 < p <= 48 for p in pins)
    assert "PAUSE" in vals["BUTTONS"]
    screen = set(vals["SCREEN_PINS"].values())                                # status screen: I2C pairs 3-4 only
    assert screen == {p for pair in vals["I2C_PAIRS"][2:] for p in pair} and not screen & reserved


def test_controller_script_pins_firmware_and_settings():
    sh = (ROOT / "scripts/controller.sh").read_text()
    assert "firmware/grblhal/settings.txt" in sh and "BTT SKR Pico 1.0" in sh and "|| echo" not in sh
    hub = (ROOT / "scripts/hub.sh").read_text()
    assert "MICROPYTHON_VERSION" in hub and "latest" not in hub.replace("never \"latest\"", "")


def test_review_pause_is_parsed_by_the_hub_client():
    from opengonio.gantry.hub import FakeHub
    hub = FakeHub(["BTN PAUSE"])
    ev = hub.poll()
    assert ev is not None and (ev.kind, ev.value) == ("BTN", "PAUSE")


def test_review_firmware_mismatch_refused(cfg):
    class Fluid(RecordingTransport):
        def write(self, data):
            if data.decode().strip() == "$I":
                self.lines.append("$I"); self.pending += ["[VER:3.9.9 FluidNC v3.9.9]", "ok"]
                return
            super().write(data)
    g = Gantry(cfg, FluidNC(Fluid.for_machine(cfg), timeout_s=1))
    with pytest.raises(GantryError, match="controller.firmware"):
        g.handshake()                                     # grblhal config, FluidNC board: no move allowed


def test_review_lamp_off_and_reinit_go_through_alarm(cfg):
    g, t = homed(cfg)
    t.state = "Alarm"                                     # grblHAL refuses G/M-code in Alarm (error:9)
    g.light("white", False); g.reinit_drivers()
    out = cfg.lights["white"]["output"]
    i = t.lines.index(f"M63 P{out}")
    assert t.lines[i - 1] == "$X" and t.lines[-2:] == ["$X", "M122 I"] and not g.homed


def test_review_blocked_output_any_spelling(cfg):
    from opengonio.gantry.gantry import switches_blocked_output
    built = replace(cfg, lights={**cfg.lights, "multispectral": {**cfg.lights["multispectral"], "built": True}})
    p = built.lights["multispectral"]["output"]
    for line in (f"M62 P{p}", f"m62p{p}", f"M64 P{p}", f"M62 P{p}.0", f"M062 P{p}", f"G4 P0 M62 P{p}"):
        assert switches_blocked_output(built, line), line
    for line in (f"M63 P{p}", f"M65 P{p}", "M62 P99", "M620 P1", f"G4 P{p}"):
        assert not switches_blocked_output(built, line), line
