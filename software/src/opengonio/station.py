"""Standalone station: buttons + OLED pick and run a job; every image is saved with a manifest.

Runs on a Raspberry Pi Zero 2 W (no laptop) or on the laptop. The laptop later pulls the folders
(`opengonio pull`) and checks them (`opengonio verify`).

    NEXT  choose job (when idle)      START run job      STOP abort
    HOME  home axes                    LIGHT white light on/off
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .gantry.config import Machine
from .gantry.gantry import Gantry
from .gantry.safety import on_power
from .plans import inplane
from .plans.hemisphere import complete
from .runrecord import (AcquisitionError, finish, make_run_dir, new_manifest, save_frame, stamp, unique_child,
                        write_json_atomic)


def jobs(cfg: Machine) -> list[tuple[str, Callable[[], list[dict]]]]:
    out = [("Mirror check 30", lambda: inplane.mirror_sweep(30.0, span=3.0, step=0.2)),
           ("Swatch 10deg", lambda: inplane.grid(cfg, 10.0))]
    if "M2" in cfg.active_axes:
        from .plans.hemisphere import isotropic
        out.append(("Isotropic 15deg", lambda: isotropic(cfg, 15.0)))
    if "M1" in cfg.active_axes:
        from .plans.hemisphere import spin
        out.append(("Spin 30", lambda: spin(cfg, 30.0, 15.0)))
    if {"M1", "M2"} <= set(cfg.active_axes):
        from .scan.plan import rings_plan
        out.append(("3D scan", lambda: [sp.pose for sp in rings_plan(cfg)]))
    return out


@dataclass
class Station:
    """Tick-driven job runner for the standalone station. Every failure path ends in a defined state: lights off,
    run marked aborted/error with the reason, position trust cleared after power events; nothing resumes by itself."""
    cfg: Machine
    g: Gantry
    hub: object
    cam: object
    data_dir: Path
    save: Callable[[Path, object], object]
    clock: Callable[[], float] = time.time
    job: int = 0
    running: bool = False
    plan: list[dict] = field(default_factory=list)
    i: int = 0
    run_dir: Path | None = None
    manifest: dict = field(default_factory=dict)
    cal: object = None                    # Calibration: snapshot goes into every manifest
    scan_cam: object = None               # second camera for the 3D scan job (None: same camera)
    warm_until: float = 0.0
    phase: str = "idle"                   # idle | object | await_background | background
    folder: str = ""                      # "" (run root) | "images" | "background"

    def __post_init__(self):
        self.jobs = jobs(self.cfg)
        self.idle_screen()

    @property
    def job_name(self) -> str:
        return self.jobs[self.job][0]

    @property
    def is_scan(self) -> bool:
        return self.job_name == "3D scan"

    def idle_screen(self, msg: str = "ready") -> None:
        self.hub.show("OpenGonio", f"> {self.job_name}", msg, "NEXT=job START=go")

    def handle(self, kind: str, value: str) -> None:
        if kind == "POWER":
            if value == "0":
                self.abort("motion power lost (e-stop)")
            msg = on_power(self.g, value)
            self.hub.show("OpenGonio", msg[:21], "press HOME" if value == "1" else "")
            return
        if kind != "BTN":
            return
        if self.phase == "await_background":
            if value == "START":
                self._begin_pass("background")
            elif value == "STOP":
                self._finish_scan(background=False)
            return
        if value == "NEXT" and not self.running:
            self.job = (self.job + 1) % len(self.jobs)
            self.idle_screen()
        elif value == "START" and not self.running:
            self.start()
        elif value == "STOP":
            self.abort("stopped")
            try:
                self.g.stop()
            except Exception as exc:
                self.hub.show("OpenGonio", "stop failed", str(exc)[:21])
        elif value == "PAUSE":                      # unattended jobs run to the end; STOP is the way out here
            self.hub.show("OpenGonio", "PAUSE: laptop panel", "only; STOP aborts")
        elif value == "HOME" and not self.running:
            self.hub.show("OpenGonio", "homing...")
            try:
                self.g.home()
                self.idle_screen("homed")
            except Exception as exc:
                self.idle_screen(f"home failed: {exc}"[:21])
        elif value == "LIGHT":
            if self.running:
                self.hub.show("OpenGonio", self.job_name, "LIGHT locked in a run", "STOP=abort")
            else:
                self.g.toggle_light("white")

    def start(self) -> None:
        name, make = self.jobs[self.job]
        try:
            if not self.g.homed:
                self.g.home()
            self.plan, self.i = make(), 0
            self.run_dir = unique_child(self.data_dir, name, self.clock())
            self.manifest = new_manifest(self.cfg, name, "white", self.cal, self.cfg.station.get("exposure_ms"),
                                         stamp(self.clock()), planned=len(self.plan),
                                         kind="scan" if self.is_scan else "measurement")
            self.manifest["controller"] = self.g.controller_id
            cam = self._cam()
            self.manifest["camera"] = cam.readback() if hasattr(cam, "readback") else None
            self.running = True
            self.write()
            self._begin_pass("images" if self.is_scan else "")
        except Exception as exc:
            self.fail(exc)

    def _begin_pass(self, folder: str) -> None:
        self.folder, self.i = folder, 0
        self.phase = "background" if folder == "background" else "object"
        if folder:
            (self.run_dir / folder).mkdir(exist_ok=True)
        self.running = True
        try:
            self.g.light("white", True)
        except Exception as exc:
            self.fail(exc)
            return
        self.warm_until = self.clock() + float(self.cfg.lights.get("white", {}).get("warmup_s", 0.0))

    def _cam(self):
        return self.scan_cam if self.scan_cam is not None and self.is_scan else self.cam

    def tick(self) -> None:
        """One pose per call; a failure in any step aborts the run safely."""
        if not self.running:
            return
        try:
            self._tick()
        except Exception as exc:
            self.fail(exc)

    def _tick(self) -> None:
        left = self.warm_until - self.clock()
        if left > 0:                                    # lamp warm-up: brightness settles first
            self.hub.show("OpenGonio", self.job_name, f"lamp warm-up {left:.0f} s", "STOP=abort")
            return
        refs = not self.is_scan
        if refs and self.manifest["reference"] is None and self.plan:
            self.manifest["reference"] = {"start": self.shoot(self.plan[0], "ref_start.png")}
            return
        if self.i >= len(self.plan):
            if refs and self.plan:
                self.manifest["reference"]["end"] = self.shoot(self.plan[0], "ref_end.png")
            self.manifest["cleanup_errors"] += self.g.all_lights_off()
            if self.phase == "object" and self.is_scan:
                self.running, self.phase = False, "await_background"
                self.write()
                self.hub.show("OpenGonio", "object pass done", "remove object:", "START=empty STOP=skip")
                return
            if self.phase == "background":
                self._finish_scan(background=True)
                return
            finish(self.manifest, "finished")
            self.running, self.phase = False, "idle"
            self.write()
            self.idle_screen(f"done {self.i} shots")
            return
        key = "background_shots" if self.phase == "background" else "shots"
        self.manifest.setdefault(key, []).append({"i": self.i, **self.shoot(self.plan[self.i], f"img_{self.i:04d}.png")})
        self.i += 1
        self.write()
        self.hub.show("OpenGonio", self.job_name, f"{self.i}/{len(self.plan)}", "STOP=abort")

    def _finish_scan(self, background: bool) -> None:
        from .scan.run import scan_meta
        meta = scan_meta(self.cfg, self.plan, background=background, camera=self.manifest.get("camera"),
                         run_id=self.manifest.get("run_id"), image_ext=".png")
        write_json_atomic(self.run_dir / "scan.json", meta)
        finish(self.manifest, "finished")
        self.running, self.phase = False, "idle"
        self.write()
        self.idle_screen("scan saved" + ("" if background else " (no background)"))

    def shoot(self, pose: dict, name: str) -> dict:
        pose = complete(self.cfg, pose)
        checks = self.g.maintain()
        if checks:
            self.manifest.setdefault("slip_checks", []).extend({"before": name, **c} for c in checks)
        reported = self.g.move(pose)
        img = self._cam().grab()
        rel = f"{self.folder}/{name}" if self.folder else name
        rec = save_frame(self.save, self.run_dir, rel, img)
        return {"pose": pose, "reported_pose": reported or None, **rec, "t": round(self.clock(), 3)}

    def fail(self, exc: BaseException) -> None:
        self.abort(f"{type(exc).__name__}: {exc}", status="error")

    def abort(self, why: str, status: str = "aborted") -> None:
        errs = self.g.all_lights_off()                    # always: a stopped job must not leave the lamp on
        if self.running or self.phase in ("object", "background", "await_background") or \
                self.manifest.get("status") == "running":                # also a start that failed half-way
            self.running, self.phase = False, "idle"
            if self.manifest:
                self.manifest["aborted"] = why
                self.manifest["cleanup_errors"] += errs
                finish(self.manifest, status, why)
                self.write()
        self.idle_screen(why[:21])

    def write(self) -> None:
        if self.run_dir is not None:
            write_json_atomic(self.run_dir / "manifest.json", self.manifest)


def run_plan(g: Gantry, cam, plan: list[dict], out_dir: Path, save: Callable[[Path, object], object], name: str,
             spectral: Callable[[], list[int]] | None = None, light: str | None = "white", cal=None,
             reference: bool = True, warmup_s: float | None = None, sleep: Callable[[float], None] = time.sleep,
             exposure_ms: float | None = None, exposures: list[float] | None = None, overwrite: bool = False) -> Path:
    """Laptop capture: move through `plan`, one image (and optional spectral reading) per pose.
    Same folder format as the station: img_NNNN.png + manifest.json (+ spectral.csv).

    The whole run - lamp on, warm-up, moves, captures, saves - is one transaction:
      * the folder is new (an existing run is refused unless overwrite=True, which moves it aside);
      * manifest.json is written at the start (status "running") and after every shot;
      * light=None (dark frames) switches EVERY light off first and fails if any light won't go off;
      * a frame that can't be saved stops the run (no "finished" with missing images);
      * on any error or interrupt (Ctrl+C, STOP) every light is switched off independently, the original error and
        any cleanup errors are recorded separately, and the manifest is written even if cleanup fails.
    reference: the first pose is shot again before and after the run (ref_start / ref_end) so `verify` can measure
    lamp drift. exposures: one exposure (ms) per pose, for the camera-response test (`capture linearity`)."""
    from .camera.uvc import CameraSettings
    from .gantry.hub import SafetyInterrupt
    out = make_run_dir(out_dir, overwrite)
    man = new_manifest(g.cfg, name, light, cal, exposure_ms, planned=len(plan))
    man["controller"] = g.controller_id
    man["camera"] = cam.readback() if cam is not None and hasattr(cam, "readback") else None
    write_json_atomic(out / "manifest.json", man)
    spec_rows = []

    def shoot(pose: dict, f: str, exp: float | None = None) -> dict:
        pose = complete(g.cfg, pose)
        checks = g.maintain()                # axes whose drift bound passed the budget go back to their switch first
        if checks:
            man.setdefault("slip_checks", []).extend({"before": f, **c} for c in checks)
        reported = g.move(pose)
        shot = {"pose": pose, "reported_pose": reported or None, "file": None}
        if g.slip:                           # 2-sigma angle error bound of each axis at this shot (slip model)
            shot["angle_bound_deg"] = {k: v["bound_deg"] for k, v in g.trust().items()}
        if exp is not None:
            applied = cam.configure(CameraSettings(exp))
            shot["exposure_ms"] = exp
            shot["applied_exposure_ms"] = (applied or {}).get("exposure_ms", exp)
        if cam is not None:
            img = cam.grab()
            shot.update(save_frame(save, out, f, img))
        if spectral is not None:
            shot["spectral"] = spectral()
        return shot

    try:
        if light is None:
            errs = g.all_lights_off()
            if errs:
                raise AcquisitionError("dark run: could not switch every light off: " + "; ".join(errs))
            man["lights"] = "all off (commanded and acknowledged)"
        else:
            g.light(light, True)
            man["lights"] = f"{light} on"
            sleep(g.cfg.lights.get(light, {}).get("warmup_s", 0.0) if warmup_s is None else warmup_s)
        if reference and plan:
            man["reference"] = {"start": shoot(plan[0], "ref_start.png")}
        for i, pose in enumerate(plan):
            shot = {"i": i, **shoot(pose, f"img_{i:04d}.png", exposures[i] if exposures else None)}
            if "spectral" in shot:
                spec_rows.append([i, *[shot["pose"].get(k, 0.0) for k in ("M4", "M3", "M2", "M1")], *shot["spectral"]])
            man["shots"].append(shot)
            write_json_atomic(out / "manifest.json", man)
        if reference and plan:
            man["reference"]["end"] = shoot(plan[0], "ref_end.png")
        finish(man, "finished")
    except BaseException as exc:
        finish(man, "aborted" if isinstance(exc, (KeyboardInterrupt, SafetyInterrupt)) else "error", exc)
        raise
    finally:
        man["cleanup_errors"] += g.all_lights_off()
        if exposures and exposure_ms and cam is not None:
            try:
                cam.configure(CameraSettings(exposure_ms))
            except Exception as exc:
                man["cleanup_errors"].append(f"exposure restore failed: {exc}")
        if spec_rows:
            try:
                head = "i,M4,M3,M2,M1," + ",".join(SPECTRAL_CHANNELS)
                (out / "spectral.csv").write_text(head + "\n" + "\n".join(",".join(str(x) for x in r) for r in spec_rows) + "\n")
            except OSError as exc:
                man["cleanup_errors"].append(f"spectral.csv not written: {exc}")
        write_json_atomic(out / "manifest.json", man)
    return out


def run_warmup(g: Gantry, cam, out_dir: Path, minutes: float = 10.0, every_s: float = 10.0, tol_pct: float = 0.5,
               sleep: Callable[[float], None] = time.sleep, light: str = "white", overwrite: bool = False) -> dict:
    """Lamp warm-up (M18.2): PTFE or grey card at 45:0, one frame every `every_s` s with the lamp on.
    settle_s = first time after which every frame stays within tol_pct of the last one -> lights.<light>.warmup_s."""
    from .imageio import centre_mean
    out = make_run_dir(out_dir, overwrite)
    g.move({"M4": 45.0, "M3": 0.0})
    rows = []
    try:
        g.light(light, True)
        for k in range(int(minutes * 60 / every_s) + 1):
            if k:
                sleep(every_s)
            rows.append((k * every_s, centre_mean(cam.grab())))
    except BaseException as exc:
        errs = g.all_lights_off()
        if errs and hasattr(exc, "add_note"):                     # Python 3.11+
            exc.add_note("cleanup: lamp may still be on: " + "; ".join(errs))
        raise
    errs = g.all_lights_off()
    if errs:
        raise AcquisitionError("lamp may still be on: " + "; ".join(errs))
    final = rows[-1][1]
    ok = [abs(v - final) <= tol_pct / 100 * final for _, v in rows]
    k = next(i for i in range(len(ok)) if all(ok[i:]))
    (out / "warmup.csv").write_text("t_s,centre_mean\n" + "".join(f"{t:g},{v:.3f}\n" for t, v in rows), encoding="utf-8")
    return {"settle_s": rows[k][0], "change_pct": round(100 * (final - rows[0][1]) / final, 2), "csv": str(out / "warmup.csv"),
            "set": f"software/config/machine.yaml -> lights.{light}.warmup_s: {max(rows[k][0], every_s):g}"}


SPECTRAL_CHANNELS = ["F1_415", "F2_445", "F3_480", "F4_515", "F5_555", "F6_590", "F7_630", "F8_680", "CLEAR", "NIR"]
