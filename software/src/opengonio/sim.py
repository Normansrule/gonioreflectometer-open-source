"""Simulated machine: the whole capture → verify → calibrate → curve chain with no hardware.

    opengonio --sim mirror capture mirror --theta 30          fake controller + camera, real files in data/
    opengonio --sim mirror --sim-error M3=0.4 capture mirror   machine with a 0.4 deg table zero error
    opengonio --sim matte --sim-drift 0.3 capture inplane      lamp that dims 0.3 % per shot
    opengonio --sim ptfe --sim-gamma 2.2 capture linearity     camera with sRGB-like (non-linear) output
    opengonio sim-demo --out data/sim                          full walkthrough; must end with "ALL PASS"

The camera renders the material's BRDF at the TRUE pose (commanded + hidden error) [R2][R6]:
    counts = dark + gain * f_r(w_i, w_r) * cos(theta_i) * (1 - drift * shot) + noise
so the angle offsets, dark level, white scale and drift found by `calibrate` and `verify` must match what was put in.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .brdf.models import ggx_brdf, lambert
from .gantry.config import Machine
from .gantry.fluidnc import AXIS_ORDER, RecordingTransport, home_mpos, switch_edges
from .gantry.kinematics import camera_dir, light_dir, sample_rotation

MATERIALS = {   # name: (BRDF of unit vectors in the sample frame, camera gain)
    "mirror": (lambda wi, wo: ggx_brdf(wi, wo, 0.9, 0.1, metallic=1.0), None),      # gain set so the peak is ~220
    "ptfe": (lambda wi, wo: lambert(0.99), 300.0),
    "matte": (lambda wi, wo: lambert(0.50), 300.0),
    "paper": (lambda wi, wo: ggx_brdf(wi, wo, 0.80, 0.9), 300.0),
    "plastic": (lambda wi, wo: ggx_brdf(wi, wo, 0.20, 0.3), 300.0),
}
LETTER = {"X": "M4", "Y": "M3", "Z": "M2", "A": "M1"}


@dataclass
class SimTransport(RecordingTransport):
    """Controller stand-in: machine position (RecordingTransport) plus the lamp outputs."""
    outputs: dict[int, bool] = field(default_factory=dict)

    def write(self, data: bytes) -> None:
        txt = data.decode().strip()
        if m := re.match(r"M6([23]) P(\d+)", txt):
            self.outputs[int(m.group(2))] = m.group(1) == "2"
        super().write(data)


def sim_transport(cfg: Machine) -> SimTransport:
    t = SimTransport()
    t.homes = home_mpos(cfg)
    t.mpos = dict.fromkeys(AXIS_ORDER[:4], 0.0)
    t.edges = switch_edges(cfg)
    return t


def _local(w: np.ndarray, R: np.ndarray) -> np.ndarray:
    loc = R.T @ w                       # machine sample frame: normal = local x
    return np.array([loc[1], loc[2], loc[0]])   # models: normal = +Z


@dataclass
class SimCamera:
    cfg: Machine
    t: SimTransport
    material: str = "mirror"
    error_deg: dict[str, float] = field(default_factory=dict)   # hidden: true = machine + error
    drift_pct_per_shot: float = 0.0
    dark: float = 4.0
    noise: float = 0.8
    size: tuple[int, int] = (48, 64)
    seed: int = 0
    shots: int = 0
    gamma: float = 1.0          # 2.2 = camera output encoded like sRGB (undo with `calibrate linearity`)
    exposure_ms: float = 20.0   # signal scales with exposure / 20 ms

    def __post_init__(self):
        self.f, gain = MATERIALS[self.material]
        self.rng = np.random.default_rng(self.seed)
        if gain is None:                 # mirror: exposure short enough that the 60 deg peak (the brightest) is not saturated
            w = np.array([math.sin(math.radians(60)), 0.0, math.cos(math.radians(60))])
            gain = 220.0 / (self.f(w, w * [-1, -1, 1]) * w[2])
        self.gain = gain

    def true_pose(self) -> dict[str, float]:
        zero = {k: v for k, v in home_mpos(self.cfg).items()}                  # machine position at home
        home = {a.fluidnc_axis: a.home_deg for a in self.cfg.axes.values()}
        p = {**self.cfg.default_pose(), **{LETTER[k]: v - zero.get(k, 0.0) + home.get(k, 0.0)
                                           for k in self.t.mpos for v in [self.t.where(k)] if LETTER.get(k) in self.cfg.active_axes}}
        return {k: v + self.error_deg.get(k, 0.0) for k, v in p.items()}

    def signal(self) -> float:
        lamp = self.cfg.active_lights.get("white", 0)
        if not self.t.outputs.get(lamp):
            return 0.0
        p = self.true_pose()
        R = sample_rotation(p["M3"], p["M2"], p["M1"])
        wi = _local(light_dir(p["M4"], self.cfg.light_elevation("white")), R)
        wo = _local(camera_dir(self.cfg.camera_elevation_deg), R)
        if wi[2] <= 0 or wo[2] <= 0:
            return 0.0
        return self.gain * self.f(wi, wo) * wi[2] * (1.0 - self.drift_pct_per_shot / 100.0 * self.shots)

    def configure(self, s) -> dict:
        """Same interface as UvcCamera.configure: the simulated camera applies exactly what is asked."""
        self.exposure_ms = float(s.exposure_ms)
        return self.readback()

    def readback(self) -> dict:
        return {"exposure_ms": self.exposure_ms, "gain": 0, "method": "simulated camera", "width": self.size[1],
                "height": self.size[0], "discard_frames": 0, "device": f"sim:{self.material}"}

    def set_exposure_ms(self, ms: float) -> dict:
        self.exposure_ms = ms
        return self.readback()

    def grab(self) -> np.ndarray:
        lin = self.signal() * self.exposure_ms / 20.0
        v = self.dark + 255.0 * (max(lin, 0.0) / 255.0) ** (1.0 / self.gamma)
        self.shots += 1
        img = v + self.rng.normal(0.0, self.noise, self.size)
        return np.clip(np.round(img), 0, 255).astype(np.uint8)

    def spectral(self) -> list[int]:
        """AS7341 stand-in: a flat-white lamp, 10 readings (F1-F8, clear, NIR)."""
        s = self.signal() + 2.0
        return [int(round(s * k)) for k in (0.3, 0.6, 0.8, 0.9, 1.0, 1.0, 0.95, 0.8, 3.0, 0.4)]


def parse_error(items: list[str] | None) -> dict[str, float]:
    return {k.upper(): float(v) for k, v in (i.split("=") for i in (items or []))}


# ---- one-command walkthrough --------------------------------------------------
def demo(cfg: Machine, out: str | Path, m3_error: float = 0.37, gamma: float = 2.2, today=None) -> dict:
    """Simulated stages 06–07 on a machine with a hidden table error and a non-linear camera:
    mirror -> calibrate angle -> dark -> linearity -> white -> matte (absolute BRDF) -> drifting lamp -> plastic fit."""
    from .calibration import Calibration, from_dark, from_linearity, from_mirror, from_white
    from .fit import fit_run
    from .gantry.fluidnc import FluidNC
    from .gantry.gantry import Gantry
    from .imageio import write_png
    from .plans import inplane
    from .station import run_plan
    from .verify import curve, verify

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    cal = Calibration(path=out / "calibration.yaml")
    err = {"M3": m3_error}
    steps = {}

    def run(name, material, plan, light="white", reference=True, drift=0.0, exposures=None):
        t = sim_transport(cfg)
        g = Gantry(cfg, FluidNC(t, timeout_s=1), offsets=cal.offsets)
        cam = SimCamera(cfg, t, material, err, drift, gamma=gamma)
        g.home()
        return run_plan(g, cam, plan, out / name, write_png, name, light=light, cal=cal, reference=reference,
                        warmup_s=0.0, sleep=lambda s: None, exposure_ms=20.0, exposures=exposures)

    mirror = lambda th: inplane.mirror_sweep(th, span=3.0, step=0.2)          # noqa: E731
    before = [verify(run(f"mirror_{th}", "mirror", mirror(th)), cfg, cal=cal) for th in (20, 40, 60)]
    steps["1 mirror before"] = [r["mirror_peak_error_deg"] for r in before]
    steps["2 offset M3"] = from_mirror(cal, steps["1 mirror before"], today)
    after = verify(run("mirror_40_after", "mirror", mirror(40)), cfg, cal=cal)
    steps["3 mirror after"] = after["mirror_peak_error_deg"]
    at45 = [{"M4": 45.0, "M3": 0.0}] * 5
    steps["4 dark"] = from_dark(cal, run("dark", "ptfe", at45, light=None, reference=False), today=today)
    ladder = [2.0, 4.0, 8.0, 16.0, 32.0, 64.0]
    steps["5 linearity (expect gamma 2.2)"] = from_linearity(
        cal, run("linearity", "ptfe", at45[:1] * len(ladder), reference=False, exposures=ladder), today=today)
    steps["5 white"] = from_white(cal, run("white", "ptfe", at45, reference=False), cfg, today=today)
    matte = run("matte", "matte", inplane.grid(cfg, 20.0))
    rep = verify(matte, cfg, cal=cal)
    import csv
    rows = list(csv.DictReader(curve(matte, cfg, cal=cal).open(encoding="utf-8")))
    f = [float(r["brdf_per_sr"]) for r in rows if r["brdf_per_sr"] and float(r["theta_i"]) <= 60]
    steps["6 matte brdf (expect 0.159)"] = round(sum(f) / len(f), 4)
    drift = verify(run("drift", "matte", inplane.grid(cfg, 20.0), drift=0.3), cfg, cal=cal)
    steps["7 drifting lamp"] = [drift["lamp_drift_pct"], drift["result"]]
    plastic = run("plastic", "plastic", inplane.grid(cfg, 10.0))
    curve(plastic, cfg, cal=cal)
    steps["8 plastic fit (made with base 0.2, roughness 0.3, metallic 0)"] = fit_run(plastic)
    cal.save()
    checks = {
        "mirror error found": abs(sum(steps["1 mirror before"]) / 3 + m3_error) <= 0.15,
        "mirror error fixed": abs(steps["3 mirror after"]) <= 0.1,
        "dark level": abs(steps["4 dark"]["dark_counts"] - 4.0) < 0.5,
        "absolute BRDF": abs(steps["6 matte brdf (expect 0.159)"] - 0.5 / math.pi) / (0.5 / math.pi) < 0.05,
        "matte run passes": rep["result"] == "PASS",
        "drift caught": drift["result"] == "FAIL",
        "camera response found": abs(steps["5 linearity (expect gamma 2.2)"]["gamma"] - gamma) / gamma < 0.05,
        "material fitted": abs(steps["8 plastic fit (made with base 0.2, roughness 0.3, metallic 0)"]["roughness"] - 0.3) <= 0.05,
    }
    summary = {"steps": steps, "checks": checks, "result": "ALL PASS" if all(checks.values()) else "FAIL"}
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    return summary
