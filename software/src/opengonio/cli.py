"""opengonio command line.

    opengonio init                           installed package: copy machine.yaml to ~/.config/opengonio/ to edit
    opengonio check-pose M4=40 M3=20         offline: BRDF angles + collision check
    opengonio plan inplane --step 10         offline: list in-plane poses
    opengonio --dry-run move M4=60 M3=30     print the G-code instead of sending it
    opengonio home | move ... | light on|off | sleep | wake | status
    opengonio panel                          run the button panel (ESP32-S3 hub) loop
    opengonio app [--sim mirror] [--lan]     control app; --lan: phones on this Wi-Fi pair with a QR code
    opengonio send '$I' '?'                  raw controller lines (grblHAL / FluidNC); prints the replies
    opengonio station                        standalone: buttons + OLED run jobs, images to station.data_dir
    opengonio pull pi@opengonio.local        copy job folders from the station to ./data
    opengonio verify data/<job>              check a job folder (PASS / WARN / FAIL)
    opengonio repeat M4 --at 60 --away 30    laser-and-mirror repeatability test (20 returns, you read the wall)
    opengonio capture mirror --theta 30      camera (+ --spectral) at every pose -> data/<name>/ (manifest, images)
    opengonio capture dark | white           5 shots at 45:0, lamp off | on (PTFE tile) for `calibrate`
    opengonio capture warmup --minutes 10    lamp brightness every 10 s -> warmup.csv + the warm-up time to set
    opengonio capture linearity              PTFE at 2-64 ms exposures -> `calibrate linearity` (camera response)
    opengonio capture isotropic --step 15    out-of-plane set from BRDF angles (needs M2, stage 08)
    opengonio capture spin --theta 30        theta_i 30, theta_r 40, sample spun 0-180 deg (needs M1, stage 09)
    opengonio fit data/<name>                game-engine material (base colour, roughness, metallic) -> fit.json + fit.svg
    opengonio curve data/<name>              curve.csv: angles, brightness, BRDF in 1/sr (+ spectral) per pose
    opengonio calibrate show | mirror DIRS | dark DIR | white DIR    measured values -> config/calibration.yaml
    opengonio --sim mirror capture mirror    same commands on the simulated machine (no hardware)
    opengonio sim-demo --out data/sim        simulated stage 06-07 walkthrough; ends with "ALL PASS"
    opengonio app --sim mirror               control app in the browser on a simulated machine (--window: desktop window)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .calibration import DEFAULT_CAL, from_dark, from_mirror, from_white, load_calibration
from .gantry.collision import clearance_mm, min_safe_m4, pose_is_safe
from .gantry.config import load_config
from .gantry.fluidnc import FluidNC, RecordingTransport
from .gantry.gantry import Gantry
from .gantry.kinematics import brdf_coords
from .plans import inplane


def _pose(items: list[str]) -> dict[str, float]:
    return {k.upper(): float(v) for k, v in (i.split("=") for i in items)}


def _transport(cfg, dry: bool, sim: bool = False):
    if sim:
        from .sim import sim_transport
        return sim_transport(cfg)
    if dry:
        return RecordingTransport.for_machine(cfg)
    c = cfg.controller
    if c.get("transport", "serial") == "tcp":
        from .gantry.fluidnc import TcpTransport
        return TcpTransport(c.get("host", "fluidnc.local"), int(c.get("tcp_port", 23)))
    from .gantry.fluidnc import SerialTransport, dialect
    return SerialTransport(c.get("port", "auto"), int(c.get("baud", 115200)), dialect(cfg)["usb_vid"])


def _scan_offline(cfg, a, cal=None) -> int:
    from .scan import demo
    from .scan.colmap import write_model
    from .scan.geometry import intrinsics
    from .scan.plan import check_object, rings_plan
    cfg4 = cfg.with_phase(max(cfg.installed_phase, 10))
    if a.action == "plan":
        check_object(cfg4)
        plan = rings_plan(cfg4)
        print(json.dumps({"views": len(plan), "rings": cfg4.scan["rings"],
                          "first": plan[0].pose, "last": plan[-1].pose}, indent=2))
    elif a.action == "sync-ids":
        from .scan.colmap import sync_image_ids
        print(f"updated {sync_image_ids(a.db, a.model)} image IDs")
    elif a.action == "export-colmap":
        plan = rings_plan(cfg4)
        K = intrinsics(cfg4.for_scan(), cfg4.scan["camera_distance_mm"])
        calib = None
        if cfg4.scan.get("calibration"):
            from .scan.calibrate import CameraCalibration
            calib = CameraCalibration.load(cfg4.scan["calibration"])
        out = write_model(f"{a.out}/sparse_known", cfg4.for_scan(), plan, K,
                          float(cfg4.scan["platter_offset_mm"]), calib)
        print(f"wrote {out} ({len(plan)} images) and {a.out}/run_colmap.sh")
    elif a.action == "demo":
        print(json.dumps(demo.run(cfg4, a.out), indent=2))
    elif a.action == "hull":
        from .scan.process import hull
        print(json.dumps(hull(cfg4, a.out, a.voxel, clip_below_mm=a.clip_below), indent=1))
    elif a.action == "ps":
        from .scan.process import ps
        print(json.dumps(ps(cfg4, a.out, a.station, cal.gamma if cal else 1.0, a.sphere), indent=1))
    return 0


def _init(force: bool) -> int:
    """Installed package: put an editable machine.yaml where load_config() finds it (never overwrites silently)."""
    import shutil
    from .gantry.config import PACKAGED_CONFIG, USER_CONFIG, default_config_path
    if USER_CONFIG.exists() and not force:
        print(f"{USER_CONFIG} exists (use --force to replace it; the old file is kept as .bak)")
        return 1
    USER_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    if USER_CONFIG.exists():
        shutil.copyfile(USER_CONFIG, USER_CONFIG.with_suffix(".yaml.bak"))
    shutil.copyfile(PACKAGED_CONFIG, USER_CONFIG)
    print(f"wrote {USER_CONFIG}\nin use now: {default_config_path()}\ncalibration: {DEFAULT_CAL}")
    return 0


def main(argv: list[str] | None = None) -> int:
    from .calibration import CalibrationError
    from .gantry.gantry import GantryError
    from .runrecord import AcquisitionError, RunExistsError
    try:
        return _main(argv)
    except (GantryError, RunExistsError, CalibrationError) as exc:   # unsafe / not homed / run exists: refuse
        print(f"refused: {exc}")
        return 3
    except AcquisitionError as exc:            # run stopped part-way; its manifest records why
        print(f"acquisition failed: {exc}")
        return 4


def _main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="opengonio")
    ap.add_argument("--config")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cal", default=str(DEFAULT_CAL), help="calibration file (default config/calibration.yaml)")
    ap.add_argument("--sim", metavar="MATERIAL", help="simulated machine: mirror, ptfe, matte, paper, plastic")
    ap.add_argument("--sim-error", action="append", metavar="AXIS=DEG", help="hidden zero error of the simulated machine (repeatable)")
    ap.add_argument("--sim-drift", type=float, default=0.0, metavar="PCT", help="simulated lamp dimming per shot")
    ap.add_argument("--sim-gamma", type=float, default=1.0, metavar="G", help="simulated camera response (2.2 = sRGB-like)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    it = sub.add_parser("init", help="copy the default machine.yaml to ~/.config/opengonio/ (installed package)")
    it.add_argument("--force", action="store_true", help="replace an existing user machine.yaml (old one kept as .bak)")
    cp = sub.add_parser("check-pose"); cp.add_argument("pose", nargs="+")
    pl = sub.add_parser("plan"); pl.add_argument("kind", choices=["inplane", "mirror", "isotropic", "spin"])
    pl.add_argument("--step", type=float, default=10.0); pl.add_argument("--theta", type=float, default=30.0)
    sub.add_parser("home"); sub.add_parser("status"); sub.add_parser("sleep"); sub.add_parser("wake")
    mv = sub.add_parser("move"); mv.add_argument("pose", nargs="+")
    li = sub.add_parser("light"); li.add_argument("state", choices=["on", "off"]); li.add_argument("--name", default="white")
    sub.add_parser("panel")
    se = sub.add_parser("send", help="raw controller lines"); se.add_argument("lines", nargs="+")
    sub.add_parser("station", help="standalone mode (no laptop)")
    pu = sub.add_parser("pull", help="copy job folders from the station"); pu.add_argument("host"); pu.add_argument("--dest", default="data")
    ve = sub.add_parser("verify", help="check a job folder"); ve.add_argument("dirs", nargs="+")
    ca = sub.add_parser("capture", help="move through a plan, image (+ spectral) at every pose")
    ca.add_argument("plan", choices=["mirror", "inplane", "dark", "white", "warmup", "linearity", "isotropic",
                                     "anisotropic", "spin"])
    ca.add_argument("--exposures", type=float, nargs="+", default=[2, 4, 8, 16, 32, 64], help="linearity: ms")
    ca.add_argument("--phi-step", type=float, default=30.0, help="anisotropic: phi_i step (deg)")
    ca.add_argument("--off", type=float, default=10.0, help="spin: theta_r - theta_i (deg)")
    ca.add_argument("--minutes", type=float, default=10.0, help="warmup: how long to watch the lamp"); ca.add_argument("--theta", type=float, default=30.0)
    ca.add_argument("--step", type=float, default=10.0); ca.add_argument("--out")
    ca.add_argument("--spectral", action="store_true", help="also read the AS7341 at every pose")
    ca.add_argument("--no-camera", action="store_true", help="spectral sensor only")
    ca.add_argument("--overwrite", action="store_true", help="--out already holds a run: move it aside and start fresh")
    cu = sub.add_parser("curve", help="angles + brightness per pose -> curve.csv"); cu.add_argument("dirs", nargs="+")
    cu.add_argument("--recalibrate", action="store_true",
                    help="use the current calibration file instead of the run's own snapshot (writes curve_recal-<id>.csv)")
    rp = sub.add_parser("repeat", help="repeatability test with a laser, a mirror and a wall")
    rp.add_argument("axis", choices=["M4", "M3", "M2", "M1"]); rp.add_argument("--at", type=float, required=True)
    rp.add_argument("--away", type=float, default=30.0); rp.add_argument("--n", type=int, default=20)
    rp.add_argument("--wall-mm", type=float, default=2000.0); rp.add_argument("--home", action="store_true", help="re-home instead of moving away")
    cb = sub.add_parser("calibrate", help="measured values -> calibration.yaml")
    cb.add_argument("action", choices=["show", "mirror", "dark", "white", "linearity"]); cb.add_argument("dirs", nargs="*")
    cb.add_argument("--rho", type=float, default=0.99, help="PTFE reflectance (datasheet)")
    cb.add_argument("--rho-source", default="assumed (datasheet nominal, not a certificate)",
                    help="where --rho comes from (certificate number, datasheet); recorded with the white reference")
    fi = sub.add_parser("fit", help="fit a game-engine material to curve.csv"); fi.add_argument("dirs", nargs="+")
    sd = sub.add_parser("sim-demo", help="simulated calibration walkthrough"); sd.add_argument("--out", default="data/sim")
    apx = sub.add_parser("app", help="control app: browser or desktop window (stage 14)")
    apx.add_argument("--sim", dest="app_sim", metavar="MATERIAL", help="start on a simulated machine: " + ", ".join(
        ("mirror", "ptfe", "matte", "paper", "plastic")))
    apx.add_argument("--port", type=int, default=8747)
    apx.add_argument("--data", default="data/app", help="folder for the app's runs")
    apx.add_argument("--window", action="store_true", help='desktop window (pip install "opengonio[desktop]"), else the browser')
    apx.add_argument("--no-browser", action="store_true", help="only serve; open the printed address yourself")
    apx.add_argument("--lan", action="store_true", help="also serve phones and tablets on this Wi-Fi (they pair with a QR code)")
    rn = sub.add_parser("render", help="fitted material on a sphere or a scanned mesh -> .glb + picture")
    rn.add_argument("what", help="a run folder with fit.json (opengonio fit), or 'demo' for the offline pipeline")
    rn.add_argument("--mesh", help="hull_mesh.ply or a .glb (default: the shader ball)")
    rn.add_argument("--color", type=float, nargs=3, metavar=("R", "G", "B"), help="tint 0-1 (the fit is grey)")
    rn.add_argument("--size", type=int, default=480, help="picture size (px)")
    rn.add_argument("--out", help="output folder (default: the run folder; demo: data/render_demo)")
    sc = sub.add_parser("scan", help="3D photo scanner (phases 11-12)")
    sc.add_argument("action", choices=["plan", "export-colmap", "demo", "run", "calibrate", "sync-ids", "hull", "ps"])
    sc.add_argument("--voxel", type=float, default=1.0, help="hull: voxel size (mm)")
    sc.add_argument("--clip-below", type=float, help="hull: drop voxels below this height (mm, object frame)")
    sc.add_argument("--station", type=int, default=0, help="ps: photometric station")
    sc.add_argument("--sphere", action="store_true", help="ps: report the normal error against an ideal sphere (S6)")
    sc.add_argument("--db", default="database.db")
    sc.add_argument("--model", default="sparse_known")
    sc.add_argument("--background", action="store_true", help="capture the empty-platter pass")
    sc.add_argument("--out", default="scan_out")
    sc.add_argument("--exposure-ms", type=float, default=20.0)
    sc.add_argument("--overwrite", action="store_true", help="--out already holds a scan: move it aside")
    a = ap.parse_args(argv)
    if a.cmd == "init":
        return _init(a.force)
    cfg = load_config(a.config) if a.config else load_config()
    cal = load_calibration(a.cal)

    if a.cmd == "app":
        from .app.server import main as app_main
        return app_main(cfg, a.app_sim or a.sim, a.port, a.data, a.window, not a.no_browser, a.cal, a.lan)
    if a.cmd == "render":
        from .render.cli import main as render_main
        return render_main(a, cfg)
    if a.cmd == "sim-demo":
        from .sim import demo
        rep = demo(cfg.with_phase(max(cfg.installed_phase, 6)), a.out)
        print(json.dumps(rep, indent=1))
        return 0 if rep["result"] == "ALL PASS" else 1
    if a.cmd == "calibrate":
        if a.action == "show":
            print(json.dumps({**cal.data, "stale": cal.stale(), "not measured yet": cal.missing()}, indent=1, default=str))
            return 0
        if not a.dirs:
            ap.error("calibrate mirror|dark|white needs run folder(s)")
        if a.action == "mirror":
            from .verify import verify
            errs = [verify(d, cfg, cal=cal).get("mirror_peak_error_deg") for d in a.dirs]
            if None in errs:
                ap.error("every folder must be a mirror run (opengonio capture mirror)")
            print(json.dumps({"peak_errors_deg": errs, "M3_offset_deg": from_mirror(cal, errs)}))
        elif a.action == "dark":
            print(json.dumps(from_dark(cal, a.dirs[0])))
        elif a.action == "linearity":
            from .calibration import from_linearity
            print(json.dumps(from_linearity(cal, a.dirs[0])))
        else:
            print(json.dumps(from_white(cal, a.dirs[0], cfg, a.rho, rho_source=a.rho_source)))
        print(f"saved {cal.save()}")
        return 0

    if a.cmd == "check-pose":
        pose = {**cfg.default_pose(), **_pose(a.pose)}
        b = brdf_coords(cfg, pose)
        print(json.dumps({"pose": pose, "theta_i": round(b.theta_i, 3), "theta_r": round(b.theta_r, 3),
                          "delta_phi": round(b.delta_phi, 3), "measurable": b.measurable,
                          "clearance_mm": round(clearance_mm(cfg, pose["M4"]), 1),
                          "min_safe_M4": min_safe_m4(cfg), "safe": pose_is_safe(cfg, pose)}, indent=2))
        return 0 if pose_is_safe(cfg, pose) else 2
    if a.cmd == "plan":
        from .plans import hemisphere
        poses = {"inplane": lambda: inplane.grid(cfg, a.step), "mirror": lambda: inplane.mirror_sweep(a.theta),
                 "isotropic": lambda: hemisphere.isotropic(cfg, a.step), "spin": lambda: hemisphere.spin(cfg, a.theta, a.step)}[a.kind]()
        print(json.dumps({"poses": len(poses), "minutes_at_5s_each": round(len(poses) * 5 / 60, 1),
                          "first": poses[:3], "axes": sorted({k for p in poses for k in p})}))
        return 0

    if a.cmd == "scan" and a.action == "plan":
        from .scan.geometry import scan_view_clearance_mm
        s = cfg.for_scan()
        print(json.dumps({"scan_camera": {"index": s.camera["index"], "distance_mm": s.camera_distance_mm,
                                          "elevation_deg": s.camera_elevation_deg,
                                          "two_cameras": s.camera["index"] != cfg.camera.get("index", 0),
                                          "clearance_over_measuring_camera_mm": scan_view_clearance_mm(cfg)}}, indent=2))
    if a.cmd == "scan" and a.action not in ("run", "calibrate"):
        return _scan_offline(cfg, a, cal)
    if a.cmd == "verify":
        from .verify import verify
        worst = 0
        for d in a.dirs:
            rep = verify(d, cfg, cal=cal)
            print(json.dumps(rep, indent=1))
            worst = max(worst, {"PASS": 0, "WARN": 1, "FAIL": 2}[rep["result"]])
        return worst
    if a.cmd == "fit":
        from .fit import fit_run
        for d in a.dirs:
            r = fit_run(d)
            print(json.dumps({k: v for k, v in r.items() if k != "engines"}), f"-> {d}/fit.json, {d}/fit.svg")
        return 0
    if a.cmd == "curve":
        from .verify import curve
        for d in a.dirs:
            print(curve(d, cfg, cal=cal, recalibrate=a.recalibrate))
        return 0
    if a.cmd == "pull":  # pragma: no cover - needs the station
        import shutil
        import subprocess
        src = f"{a.host}:{cfg.station.get('data_dir', '~/opengonio-data').replace('~/', '')}/"
        cmd = ["rsync", "-av", src, a.dest + "/"] if shutil.which("rsync") else ["scp", "-r", src + ".", a.dest]
        Path(a.dest).mkdir(exist_ok=True)
        return subprocess.call(cmd)
    if a.cmd == "station":  # pragma: no cover - hardware loop
        from dataclasses import replace
        from .camera.uvc import CameraSettings, UvcCamera
        from .gantry.hub import Hub
        from .imageio import save_image
        from .station import Station
        st_cfg = cfg.station
        cfg = replace(cfg, controller={**cfg.controller, **st_cfg.get("controller", {})})
        g = Gantry(cfg, FluidNC(_transport(cfg, False)))
        g.handshake()
        hub = Hub(st_cfg.get("hub_port", "/dev/serial0"), int(cfg.hub.get("baud", 115200)))
        cam = UvcCamera(int(cfg.camera.get("index", 0)), int(cfg.camera["width"]), int(cfg.camera["height"]))
        cam.configure(CameraSettings(float(st_cfg.get("exposure_ms", 20))))
        g.offsets = cal.offsets
        sc_i = int(cfg.for_scan().camera["index"])
        scan_cam = None if sc_i == int(cfg.camera.get("index", 0)) else \
            UvcCamera(sc_i, int(cfg.camera["width"]), int(cfg.camera["height"]))
        st = Station(cfg, g, hub, cam, Path(st_cfg.get("data_dir", "~/opengonio-data")),
                     save=save_image, cal=cal, scan_cam=scan_cam)
        print("station ready: NEXT chooses a job, START runs it")
        while True:
            ev = hub.poll()
            if ev:
                st.handle(ev.kind, ev.value)
            st.tick()

    t = _transport(cfg, a.dry_run, bool(a.sim))
    g = Gantry(cfg, FluidNC(t, timeout_s=1 if a.sim else 120), offsets=cal.offsets)
    if a.dry_run:                      # pretend everything is homed at its home position
        g.position = {k: ax.home_deg + g.offsets.get(k, 0.0) for k, ax in cfg.active_axes.items()}
        g.homed = set(cfg.active_axes)
    if a.cmd == "home":
        g.home()
    elif a.cmd == "move":
        if not a.dry_run:
            g.home()                   # positions are not persisted between CLI calls
        g.move(_pose(a.pose))
    elif a.cmd == "light":
        g.light(a.name, a.state == "on")
    elif a.cmd == "sleep":
        g.sleep()
    elif a.cmd == "wake":
        g.wake()
    elif a.cmd == "capture":
        from .station import run_plan
        at45 = [{"M4": 45.0, "M3": 0.0}] * 5              # 45:0 geometry: lamp 45 deg off the camera, sample facing it
        from .plans import hemisphere
        plan = {"mirror": lambda: inplane.mirror_sweep(a.theta, span=3.0, step=0.2), "inplane": lambda: inplane.grid(cfg, a.step),
                "dark": lambda: at45, "white": lambda: at45, "warmup": lambda: at45,
                "linearity": lambda: at45[:1] * len(a.exposures),
                "isotropic": lambda: hemisphere.isotropic(cfg, a.step), "spin": lambda: hemisphere.spin(cfg, a.theta, a.step, off=a.off),
                "anisotropic": lambda: hemisphere.anisotropic(cfg, a.step, a.phi_step)}[a.plan]()
        if a.plan in ("spin", "anisotropic") and "M1" not in cfg.active_axes:
            ap.error(f"{a.plan} needs the spin axis: set installed_phase: 9 in machine.yaml once M1 is built")
        name = {"mirror": f"mirror_{a.theta:g}", "inplane": f"inplane_{a.step:g}", "spin": f"spin_{a.theta:g}"}.get(a.plan, a.plan)
        cam = save = spec = None
        exposure = float(cfg.camera.get("exposure_ms", 20))
        if a.sim:
            from .imageio import write_png
            from .sim import SimCamera, parse_error
            sim_cam = SimCamera(cfg, t, a.sim, parse_error(a.sim_error), a.sim_drift, gamma=a.sim_gamma)
            cam, save = (None if a.no_camera else sim_cam), write_png
            spec = sim_cam.spectral if a.spectral else None
        else:  # pragma: no cover - needs hardware
            if not a.no_camera:
                from .camera.uvc import CameraSettings, UvcCamera
                from .imageio import save_image
                cam = UvcCamera(int(cfg.camera.get("index", 0)), int(cfg.camera["width"]), int(cfg.camera["height"]))
                cam.configure(CameraSettings(exposure))           # read back: refuses if the camera ignores it
                save = save_image
            if a.spectral:
                from .gantry.hub import Hub
                spec = Hub(cfg.hub.get("port", "auto"), int(cfg.hub.get("baud", 115200))).spectral
        if not a.sim and not a.dry_run:  # pragma: no cover - needs hardware
            g.handshake()
        g.home()
        if a.plan == "warmup":
            from .station import run_warmup
            print(json.dumps(run_warmup(g, cam, Path(a.out or "data/warmup"), a.minutes,
                                        sleep=(lambda s: None) if a.sim else __import__("time").sleep,
                                        overwrite=a.overwrite), indent=1))
            return 0
        print(run_plan(g, cam, plan, Path(a.out or f"data/{name}"), save, name, spectral=spec,
                       light=None if a.plan == "dark" else "white", cal=cal,
                       reference=a.plan in ("mirror", "inplane", "isotropic", "spin", "anisotropic"),
                       warmup_s=0.0 if a.sim else None, exposure_ms=exposure,
                       exposures=a.exposures if a.plan == "linearity" else None, overwrite=a.overwrite))
    elif a.cmd == "repeat":  # pragma: no cover - needs hardware and a person
        from .plans.repeatability import laser_angle_deg, laser_limit_mm, summarize
        limit = laser_limit_mm(cfg.repeatability_target_deg, a.wall_mm)
        g.home() if not a.dry_run else None
        g.move({a.axis: a.at})
        input(f"Mark the laser spot on the wall ({a.wall_mm:.0f} mm away), then press Enter ")
        shifts = []
        for i in range(a.n):
            if a.home:
                g.home((a.axis,))
            else:
                g.move({a.axis: a.at + a.away})
            g.move({a.axis: a.at})
            v = input(f"{i + 1}/{a.n}: spot distance from the mark in mm (pass if <= {limit:.1f}): ")
            shifts.append(float(v or 0))
        rep = summarize([laser_angle_deg(x, a.wall_mm) for x in shifts], cfg.repeatability_target_deg)
        rep["max_shift_mm"] = max(shifts)
        print(json.dumps(rep, indent=1))
        return 0 if rep["pass"] else 1
    elif a.cmd == "send":
        from .gantry.gantry import GantryError, switches_blocked_output
        bad = [ln for ln in a.lines if switches_blocked_output(cfg, ln)]
        if bad:
            raise GantryError(f"{bad[0]} switches a blocked light on (see phases/10-color/design.md)")
        for line in a.lines:
            if line == "?":
                print(g.nc.status())
            else:
                print("\n".join(g.nc.command(line)) or "ok")
    elif a.cmd == "status":
        st = g.nc.status()
        print(st)                                    # raw controller machine position (grblHAL: 0 at each switch)
        print("true angles:", {k: round(v, 4) for k, v in g._true(st.mpos).items()})
    elif a.cmd == "panel":  # pragma: no cover - hardware loop
        from .gantry.hub import Hub
        from .gantry.panel import Panel
        hub = Hub(cfg.hub.get("port", "auto"), int(cfg.hub.get("baud", 115200)))
        panel = Panel(g, inplane.grid(cfg, 10.0))
        print("panel ready: HOME START STOP LIGHT NEXT PAUSE")
        hub.send("POWER?")
        try:
            while True:
                ev = hub.poll()
                if ev:
                    panel.handle(ev.kind, ev.value)
                    print(panel.log[-1] if panel.log else ev)
                panel.tick()
        finally:                                          # any error or Ctrl+C: lamp off before leaving
            errs = g.all_lights_off()
            if errs:
                print("LAMP MAY STILL BE ON: " + "; ".join(errs))
    elif a.cmd == "scan":  # pragma: no cover - hardware
        from .camera.uvc import UvcCamera
        from .gantry.hub import Hub
        from .scan.run import run_scan
        c = cfg.for_scan().camera                 # the scan camera (second camera, or the moved one)
        g.handshake()
        g.home()
        if a.action == "calibrate":
            from .scan.run import calibrate_scan
            calibrate_scan(cfg, g, UvcCamera(int(c["index"]), int(c["width"]), int(c["height"])),
                           f"{a.out}/scan_calibration.yaml")
            return 0
        run_scan(cfg, g, UvcCamera(int(c["index"]), int(c["width"]), int(c["height"])),
                 Hub(cfg.hub.get("port", "auto")), a.out, a.exposure_ms, background=a.background,
                 ps="multispectral" in cfg.active_lights and not cfg.lights["multispectral"].get("blocked"), overwrite=a.overwrite)   # photometric set only with the optional LED bank
    if isinstance(t, RecordingTransport) and not a.sim:
        print("\n".join(t.lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
