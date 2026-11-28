"""AR / VR trainer (docs/og/xr.js): its JavaScript physics must equal the Python the machine uses.

Runs the page's own functions in Node (no browser, no headset). Skipped when Node is not installed.
"""
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from opengonio.fit import ggx
from opengonio.gantry import kinematics as K
from opengonio.gantry.config import load_config

ROOT = Path(__file__).resolve().parents[2]
node = shutil.which("node")
pytestmark = pytest.mark.skipif(node is None, reason="Node.js not installed")


def js(expr: str):
    """Evaluate `expr` in Node with the rig's metadata (not its mesh) and the page's script loaded."""
    code = ("globalThis.window = globalThis;\n" + (ROOT / "docs/og/model/rig.js").read_text().split("window.RIG.data", 1)[0]
            + (ROOT / "docs/og/xr.js").read_text() + f"\nconsole.log(JSON.stringify({expr}));")
    out = subprocess.run([node, "-"], input=code, capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr[-400:]
    return json.loads(out.stdout)


def test_brdf_equals_fit_py():
    rng = np.random.default_rng(3)
    cases = []
    for _ in range(40):
        wi, wo = rng.normal(size=3), rng.normal(size=3)
        wi[2], wo[2] = abs(wi[2]) + 0.05, abs(wo[2]) + 0.05
        cases.append((wi / np.linalg.norm(wi), wo / np.linalg.norm(wo), rng.uniform(0.05, 1), rng.uniform(0.05, 1), rng.uniform(0, 1)))
    arg = json.dumps([[list(a), list(b), {"base": c, "rough": d, "metal": e}] for a, b, c, d, e in cases])
    got = js(f"{arg}.map(c => XRTrain.brdf([0,0,1], c[0], c[1], c[2]))")
    want = [float(ggx(a, b, c, d, e)) for a, b, c, d, e in cases]
    assert np.allclose(got, want, rtol=1e-9, atol=1e-12)


def test_pose_angles_equal_the_machine_kinematics():
    cfg = load_config()
    for pose in ({"M1": 0, "M2": 0, "M3": 45, "M4": 120}, {"M1": 30, "M2": 25, "M3": -60, "M4": 200}, {"M1": 0, "M2": 90, "M3": 0, "M4": 90}):
        o = js(f"XRTrain.optics(window.RIG, {json.dumps(pose)}, {{base:0.8, rough:0.35, metal:0}})")
        n = K.sample_normal(pose["M3"], pose["M2"], pose["M1"])
        assert np.allclose(o["n"], n, atol=1e-9)
        c = K.brdf_coords(cfg, pose)
        assert o["ti"] == pytest.approx(c.theta_i, abs=1e-6) and o["tr"] == pytest.approx(c.theta_r, abs=1e-6)


def test_arcs_use_the_travel_limits_of_machine_yaml():
    cfg = load_config()
    assert js("window.RIG.ranges") == {k: [a.min_deg, a.max_deg] for k, a in cfg.axes.items()}
    geo = js("(() => { const s = {pose:{M1:0,M2:0,M3:45,M4:120}, mat:{base:0.8,rough:0.35,metal:0}, lesson:4, clock:0, sweep:324};"
             " const g = XRTrain.scene(window.RIG, s).geo; return [g.n, Array.from(g.pos).every(Number.isFinite)]; })()")
    assert geo[0] > 1000 and geo[0] % 3 == 0 and geo[1]


def test_two_point_alignment_puts_the_zero_point_and_the_camera_where_they_were_touched():
    p0, p1 = [0.2, 0.9, -0.6], [float(0.2 + 0.35 * np.cos(0.4)), 0.9, float(-0.6 - 0.35 * np.sin(0.4))]
    out = js(f"(() => {{ const R = window.RIG, P = XRTrain.place(R, {p0}, {p1}), m = P.matrix;"
             " const ap = v => [0,1,2].map(r => m[r]*v[0] + m[4+r]*v[1] + m[8+r]*v[2] + m[12+r]);"
             " return [ap([0,0,R.zero_z]), ap(R.camera), ap([0,0,R.zero_z+100]), P.residual_mm]; })()")
    assert np.allclose(out[0], p0, atol=1e-9) and np.allclose(out[1], p1, atol=1e-9)
    assert np.allclose(out[2], [p0[0], p0[1] + 0.1, p0[2]], atol=1e-9)          # machine up is headset up
    assert out[3] == pytest.approx(0.0, abs=1e-6)


def test_frame_time_summary():
    s = js("XRTrain.summary([11,11,11,11,11,11,11,11,11,33])")
    assert s["frames"] == 10 and s["late_frames"] == 1 and s["median_ms"] == 11 and s["fps"] == pytest.approx(1000 / 13.2, abs=0.01)


def test_run_data_lands_on_the_fitted_lobe():
    """The simulated run shipped with the site, drawn for theta_i = 50 degrees, must sit on the lobe of its own fit."""
    pre = (ROOT / "docs/og/sim-examples.js").read_text()
    out = js("(() => { " + pre + " const ex = SIM_EXAMPLES.plastic, m = {base: ex.fit.base_color, rough: ex.fit.roughness, metal: ex.fit.metallic};"
             " const o = XRTrain.optics(window.RIG, {M1:0, M2:0, M3:45, M4:95}, m), d = XRTrain.dataPoints(o, ex.rows, 5);"
             " const dot = (a, b) => a[0]*b[0] + a[1]*b[1] + a[2]*b[2];"
             " return [o.ti, d.theta_i, d.pts.map(q => [q.value, XRTrain.brdf(o.n, o.l, q.dir, m) * dot(o.n, q.dir)]),"
             " XRTrain.dataPoints(XRTrain.optics(window.RIG, {M1:0, M2:0, M3:45, M4:102}, m), ex.rows, 2).pts.length]; })()")
    assert out[0] == pytest.approx(50.0, abs=1e-6) and out[1] == 50 and len(out[2]) >= 5
    got, want = np.array(out[2]).T
    assert np.allclose(got, want, rtol=0.03)
    assert out[3] == 0                                       # theta_i = 57 degrees: no rows within 2 degrees, nothing drawn


def test_curve_csv_parser_keeps_gaps_and_rejects_a_missing_column():
    rows = js(r"XRTrain.parseCurve('M3,theta_i,phi_i,theta_r,phi_r,brdf_per_sr\n0,20,0,10,180,0.5\n0,20,0,80,180,\n')")
    assert rows == [[20, 0, 10, 180, 0.5], [20, 0, 80, 180, None]]
    bad = js(r"(() => { try { XRTrain.parseCurve('theta_i,phi_i\n1,2\n'); return 'ok'; } catch (e) { return e.message; } })()")
    assert "theta_r" in bad
