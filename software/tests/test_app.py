"""Control app (opengonio app): the JSON API on the simulated machine, end to end over HTTP."""
import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from opengonio.app.server import STATIC, App, serve
from opengonio.gantry.config import load_config


@pytest.fixture()
def api(tmp_path):
    app = App(load_config(), tmp_path / "runs", str(tmp_path / "calibration.yaml"))
    srv = serve(app, port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"

    def call(path, body=None, headers=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(base + path, data=data, headers={"Content-Type": "application/json", **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if r.headers["Content-Type"] == "application/json" else raw)
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())
    call.app = app
    yield call
    srv.shutdown()
    app.disconnect()


def test_disconnected_state_and_refusals(api):
    code, s = api("/api/state")
    assert code == 200 and s["mode"] == "disconnected" and s["job"] is None
    assert api("/api/home", {})[0] == 409                        # not connected
    assert api("/api/connect", {"mode": "sim", "material": "unobtainium"})[0] == 409


def test_sim_session_home_move_light_frame(api):
    assert api("/api/connect", {"mode": "sim", "material": "ptfe"})[0] == 200
    code, err = api("/api/move", {"pose": {"M4": 60}})
    assert code == 409 and "not homed" in err["error"]           # moves refused until homed
    assert api("/api/home", {})[0] == 200
    assert api("/api/move", {"pose": {"M4": 60, "M3": 30, "M2": 0, "M1": 0}})[0] == 200   # tilt and spin home at their switches
    s = api("/api/state")[1]
    assert s["position"]["M4"] == 60 and s["angles"]["theta_r"] == pytest.approx(30, abs=0.01)
    code, err = api("/api/light", {"name": "multispectral", "on": True})
    assert code == 409                                            # the colour LED bank stays off
    assert any(lt["name"] == "multispectral" and lt["blocked"] for lt in s["lights"])
    assert api("/api/light", {"name": "white", "on": True})[0] == 200
    code, png = api("/api/frame.png")
    assert code == 200 and png[:8] == b"\x89PNG\r\n\x1a\n"


def test_check_reports_angles_without_moving(api):
    api("/api/connect", {"mode": "sim", "material": "mirror"})
    c = api("/api/check", {"pose": {"M4": 80, "M3": 40, "M2": 0, "M1": 0}})[1]
    assert c["theta_i"] == pytest.approx(40, abs=0.01) and c["theta_r"] == pytest.approx(40, abs=0.01)
    assert c["safe"] and c["measurable"] and c["delta_phi"] == pytest.approx(180, abs=0.01)
    assert api("/api/state")[1]["position"] == {}                # nothing moved


def test_mirror_capture_finds_the_hidden_table_error(api):
    api("/api/connect", {"mode": "sim", "material": "mirror"})
    assert api("/api/run", {"plan": "mirror", "theta": 40})[0] == 409    # home first
    api("/api/home", {})
    code, r = api("/api/run", {"plan": "mirror", "theta": 40})
    assert code == 200 and r["job"]["total"] == 33
    for _ in range(100):
        job = api("/api/state")[1]["job"]
        if job["status"] != "running":
            break
        time.sleep(0.05)
    assert job["status"] == "finished" and job["done"] == 33
    assert job["result"]["result"] == "PASS"
    assert job["result"]["mirror_peak_error_deg"] == pytest.approx(-0.4, abs=0.1)
    runs = api("/api/runs")[1]["runs"]
    assert runs[0]["name"] == job["name"] and runs[0]["curve"]
    rows = api(f"/api/curve?run={job['name']}")[1]["rows"]
    assert len(rows) == 31
    assert api("/api/curve?run=../../etc")[0] == 409             # no paths outside the data folder


def test_stop_invalidates_homing(api):
    api("/api/connect", {"mode": "sim", "material": "mirror"})
    api("/api/home", {})
    assert api("/api/stop", {})[0] == 200
    s = api("/api/state")[1]
    assert not any(a["homed"] for a in s["axes"].values())       # re-home after a stop


def test_cross_origin_post_refused_and_ui_served(api):
    code, _ = api("/api/home", {}, headers={"Origin": "https://example.com"})
    assert code == 403                                            # another web page can't drive the machine
    code, html = api("/")
    assert code == 200 and b"OpenGonio control" in html
    for f in ("app.css", "app.js", "og/og.css", "og/og.js"):
        assert (STATIC / f).is_file()


def test_dns_rebinding_host_refused(api):
    code, _ = api("/api/light", {"name": "white", "on": True}, headers={"Host": "evil.example:80", "Origin": "http://evil.example:80"})
    assert code == 403
    assert api("/api/state", headers={"Host": "evil.example:80"})[0] == 403


def test_inputs_validated(api):
    api("/api/connect", {"mode": "sim", "material": "mirror"})
    api("/api/home", {})
    assert api("/api/light", {"name": "white", "on": "false"})[0] == 400     # a string is not a switch state
    assert not api("/api/state")[1]["lights"][0]["on"]
    assert api("/api/run", {"plan": "inplane", "step": 0})[0] == 400
    assert api("/api/run", {"plan": "mirror", "theta": 85})[0] == 400


def test_stop_during_a_capture_aborts_it(api):
    api("/api/connect", {"mode": "sim", "material": "matte"})
    api("/api/home", {})
    assert api("/api/run", {"plan": "inplane", "step": 5})[0] == 200
    assert api("/api/disconnect", {})[0] == 409                    # busy: no disconnect mid-run
    assert api("/api/stop", {})[0] == 200
    for _ in range(100):
        job = api("/api/state")[1]["job"]
        if job["status"] != "running":
            break
        time.sleep(0.05)
    assert job["status"] in ("aborted", "finished")                # finished only if the run beat the button
    if job["status"] == "aborted":
        assert api("/api/state")[1]["last_error"] is None
    assert not any(lt["on"] for lt in api("/api/state")[1]["lights"])


def test_devices_and_spectral_reading(api):
    devs = {d["id"]: d for d in api("/api/state")[1]["devices"]}
    assert set(devs) >= {"motion", "camera", "lamp", "spectral", "hub"} and devs["motion"]["status"] == "offline"
    assert api("/api/spectral", {})[0] == 409                    # not connected
    api("/api/connect", {"mode": "sim", "material": "ptfe"})
    api("/api/home", {})
    api("/api/light", {"name": "white", "on": True})
    code, r = api("/api/spectral", {})
    assert code == 200 and r["simulated"] and len(r["counts"]) == len(r["channels"]) == 10
    s = api("/api/state")[1]
    assert s["spectral"]["counts"] == r["counts"] and {d["id"]: d["status"] for d in s["devices"]}["spectral"] == "simulated"


def test_respond_is_the_one_route_table(tmp_path):
    """The web demo (docs/app, Pyodide) calls respond() directly: same answers as over HTTP, no server needed."""
    from opengonio.app.server import respond
    app = App(load_config(), tmp_path / "runs", str(tmp_path / "calibration.yaml"))
    code, s = respond(app, "GET", "/api/state", "", {})
    assert code == 200 and s["mode"] == "disconnected"
    assert respond(app, "POST", "/api/home", "", {})[0] == 409            # refused: not connected
    assert respond(app, "POST", "/api/connect", "", {"mode": "sim", "material": "mirror"})[0] == 200
    assert respond(app, "POST", "/api/move", "", {})[0] == 400              # bad request: no pose
    assert respond(app, "GET", "/api/nope", "", {})[0] == 404


def test_web_demo_package_is_reproducible():
    """docs/app/opengonio.zip: same bytes for the same sources, with the server and both config files inside."""
    import io
    import zipfile
    import site_app
    a, b = site_app.package_zip(), site_app.package_zip()
    assert a == b
    names = zipfile.ZipFile(io.BytesIO(a)).namelist()
    assert "software/src/opengonio/app/server.py" in names and "software/config/machine.yaml" in names
    assert not any("static/" in n or "__pycache__" in n for n in names)
