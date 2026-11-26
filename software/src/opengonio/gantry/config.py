"""Load and validate config/machine.yaml (axes are data; phases gate them)."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
import os
from pathlib import Path
from typing import Any

import yaml

REPO_CONFIG = Path(__file__).resolve().parents[3] / "config" / "machine.yaml"      # source checkout
PACKAGED_CONFIG = Path(__file__).resolve().parents[1] / "data" / "machine.yaml"    # copy shipped in the wheel
USER_CONFIG = Path(os.environ.get("OPENGONIO_HOME", "~/.config/opengonio")).expanduser() / "machine.yaml"


def default_config_path() -> Path:
    """Which machine.yaml to use when --config is not given, first match wins:
    $OPENGONIO_CONFIG -> the repository's software/config/machine.yaml (source checkout) ->
    ~/.config/opengonio/machine.yaml (or $OPENGONIO_HOME; made by `opengonio init`) -> the copy inside the package."""
    env = os.environ.get("OPENGONIO_CONFIG")
    if env:
        return Path(env).expanduser()
    for p in (REPO_CONFIG, USER_CONFIG):
        if p.exists():
            return p
    return PACKAGED_CONFIG


DEFAULT_CONFIG = REPO_CONFIG if REPO_CONFIG.exists() else PACKAGED_CONFIG             # kept for callers and tests
MICROSTEPS_PER_REV = 200 * 16          # default: 1.8 deg motor at 1/16 (an axis may set its own microsteps)


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Axis:
    key: str
    name: str
    fluidnc_axis: str
    phase: int
    min_deg: float
    max_deg: float
    home_deg: float
    gear_ratio: float
    microsteps: int = 16

    @property
    def steps_per_deg(self) -> float:
        """Controller steps_per_mm ($10x in grblHAL), used as steps per output degree."""
        return 200 * self.microsteps * self.gear_ratio / 360.0

    @property
    def resolution_deg(self) -> float:
        return 1.0 / self.steps_per_deg

    def in_range(self, deg: float) -> bool:
        return self.min_deg - 1e-9 <= deg <= self.max_deg + 1e-9


@dataclass(frozen=True)
class Machine:
    name: str
    installed_phase: int
    camera_distance_mm: float
    camera_elevation_deg: float
    light_distance_mm: float
    ring_radius_mm: float
    camera_head_radius_mm: float
    lamp_head_radius_mm: float
    arm_radius_mm: float
    keep_out_mm: float
    min_phase_angle_deg: float
    repeatability_target_deg: float
    axes: dict[str, Axis]
    controller: dict[str, Any] = field(default_factory=dict)
    hub: dict[str, Any] = field(default_factory=dict)
    camera: dict[str, Any] = field(default_factory=dict)
    lights: dict[str, dict] = field(default_factory=dict)
    scan: dict[str, Any] = field(default_factory=dict)
    station: dict[str, Any] = field(default_factory=dict)
    spectral: dict[str, Any] = field(default_factory=dict)
    sample: dict[str, Any] = field(default_factory=dict)      # planar sample size + valid-region rules (roi.py)
    slip: dict[str, Any] = field(default_factory=dict)        # slip model parameters (gantry/slip.py)

    @property
    def active_axes(self) -> dict[str, Axis]:
        order = ["M4", "M3", "M2", "M1"]
        return {k: self.axes[k] for k in order if k in self.axes and self.axes[k].phase <= self.installed_phase}

    @property
    def active_lights(self) -> dict[str, int]:
        """Lights of finished stages; `built: false` marks an optional one you skipped (stage 10 colour kit)."""
        return {k: v["output"] for k, v in self.lights.items() if v["phase"] <= self.installed_phase and v.get("built", True)}

    def light_elevation(self, name: str) -> float:
        return float(self.lights.get(name, {}).get("elevation_deg", 0.0))

    def for_scan(self) -> "Machine":
        """The scan camera (stage 11): a second camera fixed at 650 mm, raised to look over the measuring
        camera (scan.camera_index / camera_elevation_deg), or the same camera moved there (index unchanged)."""
        s = self.scan
        return replace(self, camera_distance_mm=float(s["camera_distance_mm"]),
                       camera_elevation_deg=float(s.get("camera_elevation_deg", self.camera_elevation_deg)),
                       camera={**self.camera, "index": int(s.get("camera_index", self.camera.get("index", 0)))})

    def with_phase(self, phase: int) -> "Machine":
        return replace(self, installed_phase=phase)

    def default_pose(self) -> dict[str, float]:
        """Pose assumed for axes that are not installed yet."""
        return {"M4": 90.0, "M3": 0.0, "M2": 0.0, "M1": 0.0}


def load_config(path: str | Path | None = None) -> Machine:
    path = Path(path) if path is not None else default_config_path()
    if not path.exists():
        raise ConfigError(f"{path} not found: run `opengonio init` or pass --config")
    raw = yaml.safe_load(path.read_text())
    m = raw["machine"]
    axes = {}
    for k, d in raw["axes"].items():
        a = Axis(k, d["name"], d["fluidnc_axis"].upper(), int(d["phase"]), float(d["min_deg"]),
                 float(d["max_deg"]), float(d["home_deg"]), float(d["gear_ratio"]),
                 int(d.get("microsteps", 16)))
        if a.min_deg >= a.max_deg or not a.in_range(a.home_deg):
            raise ConfigError(f"{k}: bad range or home")
        if a.home_deg not in (a.min_deg, a.max_deg):
            raise ConfigError(f"{k}: home switch must sit at a range end (controller soft limits)")
        axes[k] = a
    letters = [a.fluidnc_axis for a in axes.values()]
    if len(set(letters)) != len(letters):
        raise ConfigError("fluidnc_axis letters must be unique")
    return Machine(
        name=m["name"], installed_phase=int(m["installed_phase"]),
        camera_distance_mm=float(m["camera_distance_mm"]), camera_elevation_deg=float(m["camera_elevation_deg"]),
        light_distance_mm=float(m["light_distance_mm"]), ring_radius_mm=float(m["ring_radius_mm"]),
        camera_head_radius_mm=float(m["camera_head_radius_mm"]), lamp_head_radius_mm=float(m["lamp_head_radius_mm"]),
        arm_radius_mm=float(m["arm_radius_mm"]), keep_out_mm=float(m["keep_out_mm"]),
        min_phase_angle_deg=float(m["min_phase_angle_deg"]), repeatability_target_deg=float(m["repeatability_target_deg"]),
        axes=axes, controller=raw.get("controller", {}), hub=raw.get("hub", {}),
        camera=raw.get("camera", {}), lights=raw.get("lights", {}), scan=raw.get("scan", {}),
        station=raw.get("station", {}), spectral=raw.get("spectral", {}), sample=raw.get("sample", {}),
        slip=raw.get("slip") or {},
    )
