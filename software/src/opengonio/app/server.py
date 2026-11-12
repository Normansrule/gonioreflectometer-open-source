"""The control app's backend: one small JSON API over the same Gantry, camera and run code as the command line.

    opengonio app --sim mirror            simulated machine (every control works, nothing moves)
    opengonio app                         the real machine over USB (untested: no machine has been built yet)
    opengonio app --window                in a desktop window (pip install "opengonio[desktop]"), else the browser

Standard library only (http.server). One machine, one person: every motion goes through one lock, a capture runs
in a background thread and refuses other motion until it ends, and STOP is always accepted. The interface lives in
static/ and talks to these endpoints:

    GET  /api/state                     connection, pose, BRDF angles, lights, job progress, last error
    POST /api/connect {mode, material}  mode "sim" (material: mirror, ptfe, matte, paper, plastic) or "hardware"
    POST /api/disconnect | /api/home | /api/stop
    POST /api/check {pose}              angles and keep-out check without moving
    POST /api/move {pose} | /api/light {name, on}
    POST /api/run {plan, theta, step}   capture -> verify -> curve, in the background
    POST /api/spectral                  one AS7341 reading (simulator only for now: the app doesn't open the hub yet)
    GET  /api/frame.png                 one camera frame (the simulated camera is 64 x 48 px)
    GET  /api/runs | /api/curve?run=NAME
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import csv
import json
import threading
import time
import traceback
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .. import __version__
from ..calibration import load_calibration, DEFAULT_CAL
from ..gantry.collision import clearance_mm, pose_is_safe
from ..gantry.config import Machine, load_config
from ..gantry.fluidnc import FluidNC
from ..gantry.gantry import BLOCKED_LIGHTS, Gantry, GantryError
from ..gantry.hub import SafetyInterrupt
from ..gantry.kinematics import brdf_coords
from ..plans import hemisphere, inplane

STATIC = Path(__file__).parent / "static"
MATERIALS = ("mirror", "ptfe", "matte", "paper", "plastic")
PLANS = ("mirror", "inplane", "isotropic")
SPECTRAL_CHANNELS = ("F1 415", "F2 445", "F3 480", "F4 515", "F5 555", "F6 590", "F7 630", "F8 680", "Clear", "NIR")   # AS7341, nm


class Refused(Exception):
    """A request the machine state does not allow (409): not connected, busy, not homed, unsafe."""


@dataclass
class Job:
    name: str
    plan: str
    total: int
    done: int = 0
    status: str = "running"            # running | finished | aborted | error
    result: dict | None = None
    error: str | None = None
    started: float = field(default_factory=time.time)


class App:
    """Everything the endpoints touch. Methods raise Refused / GantryError; the handler turns them into JSON."""

    def __init__(self, cfg: Machine, data_dir: Path, cal_path: str = str(DEFAULT_CAL)):
        self.base_cfg = cfg
        self.cfg = cfg
        self.data = Path(data_dir)
        self.cal_path = cal_path
        self.lock = threading.RLock()
        self.g: Gantry | None = None
        self.cam = None
        self.mode = "disconnected"         # disconnected | sim | hardware
        self.material: str | None = None
        self.job: Job | None = None
        self.stop_flag = threading.Event()
        self.last_error: str | None = None
        self.spectral_last: dict | None = None

    # ---- connection -----------------------------------------------------------------------------------------
    def connect(self, mode: str, material: str | None = None) -> None:
        with self.lock:
            self._busy_refuse()
            self.disconnect()
            cal = load_calibration(self.cal_path)
            if mode == "sim":
                from ..sim import SimCamera, sim_transport
                if material not in MATERIALS:
                    raise Refused(f"unknown material {material!r}: choose one of {', '.join(MATERIALS)}")
                self.cfg = self.base_cfg.with_phase(max(self.base_cfg.installed_phase, 9))   # every axis to try
                t = sim_transport(self.cfg)
                self.g = Gantry(self.cfg, FluidNC(t, timeout_s=1), offsets=cal.offsets)
                self.cam = SimCamera(self.cfg, t, material, {"M3": 0.4})                   # the same hidden table error as the demo
                self.material = material
            elif mode == "hardware":  # pragma: no cover - needs the machine
                from ..cli import _transport
                self.cfg = self.base_cfg
                self.g = Gantry(self.cfg, FluidNC(_transport(self.cfg, False), timeout_s=120), offsets=cal.offsets)
                self.g.handshake()
                self.cam = None                     # the USB camera opens on the first frame or capture
            else:
                raise Refused(f"unknown mode {mode!r}")
            self.mode = mode
            self.last_error = None

    def disconnect(self) -> None:
        self._busy_refuse()
        with self.lock:
            if self.g is not None:
                try:
                    self.g.all_lights_off()
                except Exception:                   # leaving anyway; the next connect starts clean
                    pass
            if self.cam is not None and hasattr(self.cam, "close"):
                self.cam.close()
            self.g, self.cam, self.mode, self.material = None, None, "disconnected", None
            self.spectral_last = None
            self.cfg = self.base_cfg

    def _gantry(self) -> Gantry:
        if self.g is None:
            raise Refused("not connected")
        return self.g

    def _busy_refuse(self) -> None:
        if self.job and self.job.status == "running":
            raise Refused(f"a capture is running ({self.job.name}): wait for it or press STOP")

    def _camera(self):
        if self.cam is None and self.mode == "hardware":  # pragma: no cover - needs the camera
            from ..camera.uvc import CameraSettings, UvcCamera
            c = self.cfg.camera
            self.cam = UvcCamera(int(c.get("index", 0)), int(c["width"]), int(c["height"]))
            self.cam.configure(CameraSettings(float(c.get("exposure_ms", 20))))
        return self.cam

    # ---- motion and lights ----------------------------------------------------------------------------------
    def home(self) -> None:
        with self.lock:
            self._busy_refuse()
            self._gantry().home()

    def move(self, pose: dict) -> None:
        with self.lock:
            self._busy_refuse()
            g = self._gantry()
            g.move({k: float(v) for k, v in pose.items() if k in g.axes})

    def light(self, name: str, on: bool) -> None:
        with self.lock:
            self._busy_refuse()
            if not isinstance(on, bool):
                raise ValueError("'on' must be true or false")
            self._gantry().light(name, on)

    def stop(self) -> None:
        """Always accepted: flag the running job, then hold and reset the controller (re-home needed)."""
        self.stop_flag.set()
        g = self.g
        if g is None:
            return
        g.stop()                 # hold + reset first: realtime bytes, no lock and no reply to wait for
        if self.lock.acquire(timeout=5):      # then the lamp, once the capture thread has let go of the controller
            try:
                errs = g.all_lights_off()
            finally:
                self.lock.release()
            if errs:
                self.last_error = "LAMP MAY STILL BE ON: " + "; ".join(errs)
        else:                                  # the capture's own cleanup switches every light off as it ends
            self.last_error = "stopped; the capture is still releasing the controller and will switch the lamp off"

    def check(self, pose: dict) -> dict:
        cfg = self.cfg
        p = {**cfg.default_pose(), **(self.g.position if self.g else {}), **{k: float(v) for k, v in pose.items()}}
        b = brdf_coords(cfg, p)
        return {"pose": p, "theta_i": round(b.theta_i, 2), "theta_r": round(b.theta_r, 2), "delta_phi": round(b.delta_phi, 2),
                "measurable": b.measurable, "safe": pose_is_safe(cfg, p), "clearance_mm": round(clearance_mm(cfg, p["M4"]), 1)}

    # ---- capture --------------------------------------------------------------------------------------------
    LIMITS = {"mirror": ("theta", 10.0, 80.0), "inplane": ("step", 5.0, 40.0), "isotropic": ("step", 10.0, 45.0)}

    def plan(self, kind: str, theta: float, step: float) -> list[dict]:
        if kind in self.LIMITS:
            name, lo, hi = self.LIMITS[kind]
            v = theta if name == "theta" else step
            if not lo <= v <= hi:
                raise ValueError(f"{kind}: {name} must be between {lo:g} and {hi:g} degrees")
        if kind == "mirror":
            return inplane.mirror_sweep(theta, span=3.0, step=0.2)
        if kind == "inplane":
            return inplane.grid(self.cfg, step)
        if kind == "isotropic":
            if "M2" not in self.cfg.active_axes:
                raise Refused("isotropic needs the tilt axis (stage 08)")
            return hemisphere.isotropic(self.cfg, step)
        raise Refused(f"unknown plan {kind!r}: choose one of {', '.join(PLANS)}")

    def run(self, kind: str, theta: float = 30.0, step: float = 10.0) -> Job:
        with self.lock:
            self._busy_refuse()
            g = self._gantry()
            missing = [k for k in g.axes if k not in g.homed]
            if missing:
                raise Refused(f"home first: {', '.join(missing)} not homed")
            plan = self.plan(kind, float(theta), float(step))
            name = time.strftime("%Y%m%d-%H%M%S") + f"_{kind}" + (f"_{theta:g}" if kind == "mirror" else f"_{step:g}")
            self.job = Job(name, kind, total=len(plan) + 2)        # + reference shots before and after
            self.stop_flag.clear()
        threading.Thread(target=self._run, args=(self.job, plan), daemon=True).start()
        return self.job

    def _run(self, job: Job, plan: list[dict]) -> None:
        from ..imageio import save_image, write_png
        from ..station import run_plan
        from ..verify import curve, verify
        app = self

        class Counting:                                       # progress and STOP between shots
            def __init__(self, cam):
                self.cam = cam

            def grab(self):
                if app.stop_flag.is_set():
                    raise SafetyInterrupt("STOP pressed in the app")
                img = self.cam.grab()
                job.done += 1
                return img

            def __getattr__(self, k):
                return getattr(self.cam, k)
        try:
            with self.lock:
                cal = load_calibration(self.cal_path)
                cam = self._camera()
                sim = self.mode == "sim"
                out = run_plan(self.g, Counting(cam), plan, self.data / job.name, write_png if sim else save_image, job.name,
                               light="white", cal=cal, reference=True, warmup_s=0.0 if sim else None,
                               sleep=(lambda s: None) if sim else time.sleep, exposure_ms=float(self.cfg.camera.get("exposure_ms", 20)))
            rep = verify(out, self.cfg, cal=cal)
            curve(out, self.cfg, cal=cal)
            job.result = {k: rep.get(k) for k in ("result", "problems", "notes", "mirror_peak_error_deg", "lamp_drift_pct", "shots")}
            job.status = "finished"
        except SafetyInterrupt as exc:
            job.status, job.error = "aborted", str(exc)
        except Exception as exc:                           # recorded in the run's manifest too
            if self.stop_flag.is_set():                    # STOP reset the controller mid-move: that is an abort
                job.status, job.error = "aborted", "STOP pressed in the app"
            else:
                job.status, job.error = "error", str(exc)
                self.last_error = str(exc)

    # ---- reading ---------------------------------------------------------------------------------------------
    def frame_png(self) -> bytes:
        from ..imageio import encode_png
        with self.lock:
            self._busy_refuse()
            cam = self._camera()
            if cam is None:
                raise Refused("not connected")
            return encode_png(cam.grab())

    def spectral(self) -> dict:
        """One AS7341 reading (raw counts, 8 bands + clear + NIR) at the current pose. The simulator answers from its
        material model; on the machine the sensor sits on the button hub, which the app doesn't open yet."""
        with self.lock:
            self._busy_refuse()
            if self.mode == "disconnected":
                raise Refused("not connected")
            if self.mode != "sim":
                raise Refused("the spectral sensor (AS7341, stage 10) reads through the button hub, which this app "
                              "doesn't open yet: it arrives with the hub in the app")
            counts = self.cam.spectral()
            self.spectral_last = {"channels": list(SPECTRAL_CHANNELS), "counts": counts, "simulated": True,
                                  "pose": dict(self._gantry().position), "time": time.time()}
            return self.spectral_last

    def devices(self) -> list[dict]:
        """What the app talks to, and how: simulated, connected, offline, or not built yet (stage in `stage`).
        Status words are for people; nothing here claims a part works before it has been built and tested."""
        sim, hw = self.mode == "sim", self.mode == "hardware"
        cam = self.cfg.camera
        white = next((spec for n, spec in self.cfg.lights.items() if n == "white"), {})
        phase = self.cfg.installed_phase
        return [
            {"id": "motion", "name": "Motion board", "part": "BTT SKR Pico · grblHAL · USB-C", "stage": 2,
             "status": "simulated" if sim else "connected" if hw else "offline",
             "detail": "4 × TMC2209, firmware simulated" if sim else "untested: no machine built yet" if hw else "connect to start"},
            {"id": "camera", "name": "Measuring camera", "part": f"Arducam IMX477 · {cam['width']} × {cam['height']}", "stage": 6,
             "status": "simulated" if sim else ("connected" if self.cam is not None else "standby") if hw else "offline",
             "detail": "64 × 48 px stand-in" if sim else "opens on the first frame" if hw else ""},
            {"id": "lamp", "name": "White lamp", "part": "3000 K COB · CRI 97", "stage": int(white.get("phase", 6)),
             "status": "simulated" if sim else "connected" if hw else "offline",
             "detail": f"warm-up {white.get('warmup_s', 60)} s" if white else ""},
            {"id": "spectral", "name": "Spectral sensor", "part": "AS7341 · 10 channels", "stage": 10,
             "status": "simulated" if sim else "not_built" if phase < 10 else "not_in_app",
             "detail": "read on demand" if sim else f"built in stage 10 (installed: {phase:02d})" if phase < 10 else "on the button hub"},
            {"id": "hub", "name": "Button hub", "part": "ESP32-S3 · MicroPython", "stage": 2,
             "status": "not_in_app", "detail": "buttons, display and sensors: used by `opengonio station`"},
        ]

    def runs(self) -> list[dict]:
        out = []
        if self.data.is_dir():
            for d in sorted(self.data.iterdir(), reverse=True):
                m = d / "manifest.json"
                if m.is_file():
                    try:
                        man = json.loads(m.read_text(encoding="utf-8"))
                    except (OSError, ValueError):
                        continue
                    device = str((man.get("camera") or {}).get("device", ""))
                    out.append({"name": d.name, "status": man.get("status"), "shots": len(man.get("shots", [])),
                                "curve": (d / "curve.csv").is_file(), "simulated": device.startswith("sim:")})
        return out[:50]

    def curve(self, name: str) -> dict:
        d = (self.data / name).resolve()
        if self.data.resolve() not in d.parents or not (d / "curve.csv").is_file():
            raise Refused(f"no curve for {name!r}")
        with open(d / "curve.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        keys = ("M4", "M3", "M2", "M1", "theta_i", "theta_r", "delta_phi", "centre_mean", "linear_mean", "brdf_per_sr", "valid")
        man = json.loads((d / "manifest.json").read_text(encoding="utf-8")) if (d / "manifest.json").is_file() else {}
        simulated = str((man.get("camera") or {}).get("device", "")).startswith("sim:")
        return {"run": name, "simulated": simulated, "rows": [{k: r.get(k) for k in keys} for r in rows]}

    def state(self) -> dict:
        g, cfg = self.g, self.cfg
        lights = []
        for n, spec in cfg.lights.items():
            why = spec.get("blocked") or BLOCKED_LIGHTS.get(n)
            lights.append({"name": n, "installed": n in cfg.active_lights, "blocked": why, "on": bool(g and g.light_state.get(n))})
        axes = {k: {"min": a.min_deg, "max": a.max_deg, "home": a.home_deg, "stage": a.phase, "installed": k in cfg.active_axes,
                    "homed": bool(g and k in g.homed)} for k, a in cfg.axes.items()}
        s = {"version": __version__, "mode": self.mode, "material": self.material, "installed_phase": cfg.installed_phase,
             "materials": list(MATERIALS), "plans": list(PLANS), "axes": axes, "lights": lights,
             "position": dict(g.position) if g else {}, "last_error": self.last_error,
             "job": self.job.__dict__ if self.job else None, "data_dir": str(self.data),
             "devices": self.devices(), "spectral": self.spectral_last,
             "camera": {"exposure_ms": float(cfg.camera.get("exposure_ms", 20)), "width": cfg.camera["width"], "height": cfg.camera["height"]}}
        if g and all(k in g.position and k in g.homed for k in g.axes):     # angles only from a trusted (homed) pose
            s["angles"] = self.check({})
        return s


class Handler(SimpleHTTPRequestHandler):
    app: App

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STATIC), **kw)

    def log_message(self, fmt, *args):          # quiet: the terminal is for errors
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def _host_ok(self) -> bool:
        """Only this computer's own names: a DNS-rebinding page arrives under another Host and is refused."""
        port = self.server.server_address[1]
        return self.headers.get("Host", "") in (f"127.0.0.1:{port}", f"localhost:{port}", f"[::1]:{port}")

    def _json(self, obj, code: int = 200) -> None:
        body = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        data = json.loads(self.rfile.read(n) or b"{}")
        if not isinstance(data, dict):
            raise ValueError("JSON object expected")
        return data

    def do_GET(self):
        if not self._host_ok():
            return self._json({"error": "unknown host refused"}, HTTPStatus.FORBIDDEN)
        u = urlparse(self.path)
        if u.path == "/api/frame.png":
            try:
                png = self.app.frame_png()
            except (Refused, GantryError) as exc:
                return self._json({"error": str(exc)}, HTTPStatus.CONFLICT)
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(png)))
            self.end_headers()
            self.wfile.write(png)
            return
        if u.path.startswith("/api/"):
            return self._json(*reversed(respond(self.app, "GET", u.path, u.query, {})))
        return super().do_GET()

    def do_POST(self):
        u = urlparse(self.path)
        if not self._host_ok():
            return self._json({"error": "unknown host refused"}, HTTPStatus.FORBIDDEN)
        if self.headers.get("Origin") and urlparse(self.headers["Origin"]).netloc != self.headers.get("Host"):
            return self._json({"error": "cross-origin request refused"}, HTTPStatus.FORBIDDEN)   # another site can't drive the machine
        try:
            b = self._body()
        except ValueError as exc:
            return self._json({"error": f"bad request: {exc}"}, HTTPStatus.BAD_REQUEST)
        self._json(*reversed(respond(self.app, "POST", u.path, u.query, b)))


def call(app: App, fn, post: bool) -> tuple[int, dict]:
    """Run one endpoint function; Refused, machine and request errors become (status, {error, kind})."""
    try:
        out = fn() or {"ok": True}
        if post:
            app.last_error = None                  # a successful action clears the old error
        return HTTPStatus.OK, out
    except Refused as exc:
        return HTTPStatus.CONFLICT, {"error": str(exc), "kind": "refused"}
    except GantryError as exc:                    # unsafe, not homed, controller refused: the message says what to do
        app.last_error = str(exc)
        return HTTPStatus.CONFLICT, {"error": str(exc), "kind": "machine"}
    except (ValueError, KeyError, TypeError) as exc:
        return HTTPStatus.BAD_REQUEST, {"error": f"bad request: {exc}", "kind": "request"}
    except Exception as exc:                      # pragma: no cover - unexpected: show it, keep serving
        traceback.print_exc()
        app.last_error = str(exc)
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc), "kind": "internal"}


def respond(app: App, method: str, path: str, query: str, b: dict) -> tuple[int, dict]:
    """The JSON endpoints, shared by the local server and the in-browser demo (docs/app runs this file in Pyodide)."""
    a = app
    if method == "GET":
        routes = {
            "/api/state": a.state,
            "/api/runs": lambda: {"runs": a.runs()},
            "/api/curve": lambda: a.curve(parse_qs(query).get("run", [""])[0]),
        }
    else:
        routes = {
            "/api/connect": lambda: a.connect(b.get("mode", "sim"), b.get("material")),
            "/api/disconnect": a.disconnect,
            "/api/home": a.home,
            "/api/stop": a.stop,
            "/api/move": lambda: a.move(b["pose"]),
            "/api/check": lambda: a.check(b.get("pose", {})),
            "/api/light": lambda: a.light(b["name"], b["on"]),
            "/api/spectral": a.spectral,
            "/api/run": lambda: {"job": a.run(b.get("plan", "mirror"), b.get("theta", 30), b.get("step", 10)).__dict__},
        }
    fn = routes.get(path)
    if fn is None:
        return HTTPStatus.NOT_FOUND, {"error": "not found"}
    return call(a, fn, method == "POST")


def serve(app: App, host: str = "127.0.0.1", port: int = 8747) -> ThreadingHTTPServer:
    handler = type("BoundHandler", (Handler,), {"app": app})
    return ThreadingHTTPServer((host, port), handler)


def main(cfg: Machine, sim: str | None, port: int, data: str, window: bool, open_browser: bool, cal: str) -> int:
    app = App(cfg, Path(data), cal)
    if sim:
        app.connect("sim", sim)
    srv = serve(app, port=port)
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"OpenGonio app on {url}  ({'simulated ' + sim if sim else 'not connected'}; Ctrl+C to quit)")
    try:
        if window:
            try:
                import webview  # pywebview: pip install "opengonio[desktop]"
            except ImportError:
                print("no desktop window (pip install \"opengonio[desktop]\"): opening the browser instead")
            else:  # pragma: no cover - opens a native window
                webview.create_window("OpenGonio", url, width=1360, height=860, min_size=(380, 600), background_color="#0c0b0a")
                webview.start()
                return 0
        if open_browser:
            import webbrowser
            webbrowser.open(url)
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        app.disconnect()
        srv.shutdown()
    return 0
