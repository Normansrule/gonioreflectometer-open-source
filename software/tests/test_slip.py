"""Slip model (gantry/slip.py): the filter, the feedforward correction, the schedule and the switch probe, all on the
simulated controller with slip injected. Nothing here is a measurement of a real machine."""
from dataclasses import replace

import pytest

from opengonio.gantry.config import load_config
from opengonio.gantry.fluidnc import FluidNC
from opengonio.gantry.gantry import Gantry, GantryError
from opengonio.gantry.slip import AxisSlip, SlipConfig, travel_until_due
from opengonio.sim import sim_transport


def rig(creep=0.0, **slip):
    cfg = load_config()
    cfg = replace(cfg.with_phase(9), slip={**cfg.slip, "mode": "probe", **slip})
    t = sim_transport(cfg)
    if creep:
        t.creep["Y"] = creep
    g = Gantry(cfg, FluidNC(t, timeout_s=1))
    g.home()
    return cfg, t, g


def true_m3(cfg, t):
    return t.where("Y") + cfg.axes["M3"].home_deg          # grblHAL: machine position 0 at home


def strokes(g, n, lo=-170.0, hi=-110.0):
    for _ in range(n):
        g.move({"M3": hi}); g.move({"M3": lo})


def test_filter_learns_the_creep_and_the_commands_cancel_it():
    creep = 0.001                                          # 0.1 %: 0.36 deg lost per turn
    cfg, t, g = rig(creep)
    g.check("M3")                                          # first check: learns where the switch edge is
    errs = []
    for _ in range(7):
        strokes(g, 3)
        g.move({"M3": -90.0})
        errs.append(abs(true_m3(cfg, t) - (-90.0)))
        rep = g.check("M3")
        assert rep["measured_deg"] is not None
    assert len(g.slip["M3"].events) == 1                   # 5x the expected creep: the first reference is not believed...
    assert g.slip["M3"].s == pytest.approx(creep, rel=0.15)   # ...the following ones are
    assert errs[0] > 0.3 and errs[-1] < 0.05               # uncorrected first round, corrected once the creep is known
    assert g.slip["M3"].pss < SlipConfig.from_machine(cfg).creep_sd ** 2 / 20


def test_no_slip_no_drift_and_soft_limits_always_restored():
    cfg, t, g = rig()
    g.check("M3"); strokes(g, 2)
    rep = g.check("M3")
    assert abs(rep["measured_deg"]) <= 0.021               # one probe step
    assert abs(g.slip["M3"].s) < 2e-4
    assert t.lines.count("$20=0") == t.lines.count("$20=1") == 3      # reference probe + one per check


def test_lost_steps_are_an_event_and_do_not_teach_the_creep():
    cfg, t, g = rig()
    g.check("M3"); strokes(g, 1)
    s_before = g.slip["M3"].s
    t.jump["Y"] = -0.5                                     # the belt jumps a tooth on the next move
    g.move({"M3": -150.0})
    rep = g.check("M3")
    assert rep["event"] == "step loss" and rep["measured_deg"] == pytest.approx(-0.5, abs=0.03)
    assert g.slip["M3"].s == s_before and len(g.slip["M3"].events) == 1
    g.move({"M3": -90.0})
    assert true_m3(cfg, t) == pytest.approx(-90.0, abs=0.01)           # re-homed: the jump is gone


def test_slip_beyond_the_limit_is_a_fault_not_a_correction():
    cfg, t, g = rig(max_correct_deg=0.4)
    g.check("M3")
    t.jump["Y"] = 0.3                                      # away from the switch: found late, measured, refused? no: inside
    g.move({"M3": -150.0})
    assert g.check("M3")["event"] == "step loss"
    t.jump["Y"] = -0.6                                     # toward the switch: beyond the limit
    g.move({"M3": -150.0})
    with pytest.raises(GantryError, match="mechanical fault"):
        g.check("M3")
    assert "M3" not in g.homed and t.lines[-1] != "$20=0" and t.lines.count("$20=0") == t.lines.count("$20=1")


def test_schedule_rehomes_when_the_bound_passes_the_budget():
    cfg = load_config()
    cfg = replace(cfg.with_phase(9), slip={**cfg.slip, "mode": "rehome"})
    t = sim_transport(cfg)
    g = Gantry(cfg, FluidNC(t, timeout_s=1)); g.home()
    c = g.slip_cfg
    limit = travel_until_due(c)
    assert 100 < limit < 1000
    assert g.maintain() == []
    g.move({"M3": -180.0 + limit * 0.9})
    assert g.due() == []
    g.move({"M3": -180.0}); g.move({"M3": -100.0})
    assert g.due() == ["M3"]
    homes = t.lines.count("$HY")
    rep = g.maintain()
    assert [r["axis"] for r in rep] == ["M3"] and rep[0]["measured_deg"] is None
    assert t.lines.count("$HY") == homes + 1 and "$20=0" not in t.lines        # rehome mode never lifts the soft limits
    assert g.position["M3"] == -100.0 and g.due() == [] and g.slip["M3"].travel == pytest.approx(80.0)


def test_closed_form_matches_the_filter():
    c = SlipConfig.from_machine(load_config())
    a, f = travel_until_due(c), AxisSlip(c)
    f.predict(a * 0.999); assert not f.due
    f.predict(a * 0.002); assert f.due
    g = AxisSlip(c)                                        # many short moves = one long one (variance is in travel)
    for _ in range(100):
        g.predict(a / 100)
    assert g.pdd == pytest.approx(AxisSlip(c).pdd + c.q * a + (c.creep_sd * a) ** 2, rel=5e-3)


def test_backlash_approach_always_arrives_moving_away_from_the_switch():
    cfg, t, g = rig(approach_deg=1.5)
    g.move({"M3": -100.0})
    n = len(t.lines)
    g.move({"M3": -120.0})                                 # toward the switch: go past, come back
    moves = [l for l in t.lines[n:] if l.startswith("G53")]
    assert len(moves) == 2 and "Y58.5" in moves[0] and "Y60.0" in moves[1]
    n = len(t.lines)
    g.move({"M3": -110.0})                                 # away from the switch already: one move
    assert len([l for l in t.lines[n:] if l.startswith("G53")]) == 1


def test_off_changes_nothing_and_bad_config_is_refused():
    cfg = load_config()
    off = replace(cfg.with_phase(9), slip={"mode": "off"})
    t = sim_transport(off)
    g = Gantry(off, FluidNC(t, timeout_s=1)); g.home(); g.move({"M3": 10.0})
    assert g.slip == {} and g.trust() == {} and g.maintain() == [] and "Y190.0000" in t.lines[-2]
    with pytest.raises(GantryError):
        g.check("M3")
    for bad in ({"mode": "sometimes"}, {"budget_deg": 0.03}, {"typo": 1}, {"switch_sd_deg": 0}):
        with pytest.raises(ValueError):
            SlipConfig.from_machine(replace(cfg, slip=bad))


def test_runs_record_the_bound_and_every_reference(tmp_path):
    import json
    from opengonio.imageio import write_png
    from opengonio.sim import SimCamera
    from opengonio.station import run_plan
    cfg, t, g = rig(0.002, mode="rehome")
    cam = SimCamera(cfg, t, "ptfe")
    plan = [{"M4": 60.0, "M3": m3} for m3 in (-150.0, 150.0, -150.0, 150.0)]
    out = run_plan(g, cam, plan, tmp_path / "r", write_png, "slip", warmup_s=0.0, sleep=lambda s: None)
    man = json.loads((out / "manifest.json").read_text())
    assert man["status"] == "finished" and man["slip_checks"]
    assert "M3" in {c["axis"] for c in man["slip_checks"]}
    assert all(max(s["angle_bound_deg"].values()) <= g.slip_cfg.budget_deg + 0.25 for s in man["shots"])


def test_website_twin_uses_the_same_nominal_values():
    """docs/og/slip-lab.js repeats the filter in JavaScript: its constants must be slip.py DEFAULTS."""
    import json, re
    from pathlib import Path
    from opengonio.gantry.slip import DEFAULTS
    js = (Path(__file__).resolve().parents[2] / "docs" / "og" / "slip-lab.js").read_text()
    obj = re.search(r"const NOMINAL = (\{[^}]*\})", js).group(1)
    nominal = json.loads(re.sub(r"(\w+):", r'"\1":', obj))
    assert nominal == {k: DEFAULTS[k] for k in nominal} and len(nominal) == 7


def test_app_shows_trust_and_checks_on_the_switches(tmp_path):
    from opengonio.app.server import App, Refused
    app = App(load_config(), tmp_path)
    app.connect("sim", "plastic")
    assert app.state()["slip"] == {"mode": "probe", "sim": {}, "measures": True}
    with pytest.raises(Refused):
        app.reference()                                    # nothing homed yet
    app.home()
    app.reference()                                        # learns the edges
    app.set_sim_slip(0.02)
    for m3 in (-60, 60, -60, 60):
        app.move({"M3": m3})
    rep = app.reference("M3")["checks"][0]
    assert rep["axis"] == "M3" and rep["measured_deg"] == pytest.approx(0.02 / 100 * 720, abs=0.03)   # 480 deg of moves + 240 back to the switch
    t = app.state()["trust"]["M3"]
    assert t["checks"] == 1 and t["creep_pct"] > 0 and not t["due"] and t["travel_deg"] == pytest.approx(240.0)
    with pytest.raises(ValueError):
        app.set_sim_slip(5)
