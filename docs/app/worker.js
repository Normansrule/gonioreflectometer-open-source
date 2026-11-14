/* Runs the opengonio Python package in the browser with Pyodide (Python compiled to WebAssembly), for the control app
   web demo (docs/app/). Requests arrive from browser.js; the same respond() as `opengonio app` answers them
   (software/src/opengonio/app/server.py). Simulated machine only. SPDX-License-Identifier: GPL-3.0-or-later */
"use strict";
const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";
importScripts(PYODIDE + "pyodide.js");

const GLUE = `
import json, sys, threading
from urllib.parse import parse_qs
sys.path.insert(0, "/home/pyodide/og/software/src")


class _Inline(threading.Thread):        # a browser worker has no threads: a capture runs to the end inside its request
    def start(self):
        self.run()


threading.Thread = _Inline

from pathlib import Path
from opengonio.app.server import App, Refused, respond
from opengonio.gantry.config import load_config
from opengonio.gantry.gantry import GantryError

app = App(load_config(), Path("/home/pyodide/data"))
WEB_ONLY = ("This web demo runs the simulated machine only. On a laptop, \`opengonio app\` "
            "connects to the machine over USB.")


def handle(method, path, query, body):
    b = json.loads(body) if body else {}
    if method == "POST" and path == "/api/connect" and b.get("mode") == "hardware":
        return 409, json.dumps({"error": WEB_ONLY, "kind": "refused"}), None
    try:
        if path == "/api/frame.png":
            return 200, "image/png", app.frame_png()
        if path == "/api/download":
            return 200, "application/zip", app.download(parse_qs(query).get("run", [""])[0])
        if path == "/api/glb":
            return 200, "model/gltf-binary", app.glb(parse_qs(query).get("run", [""])[0])
    except (Refused, GantryError) as exc:
        return 409, json.dumps({"error": str(exc)}), None
    code, out = respond(app, method, path, query, b)
    return int(code), json.dumps(out, default=str), None
`;

const ready = (async () => {
  postMessage({ type: "status", text: "Loading Python in your browser (Pyodide)…" });
  const py = await loadPyodide({ indexURL: PYODIDE });
  postMessage({ type: "status", text: "Loading numpy and PyYAML…" });
  await py.loadPackage(["numpy", "pyyaml"]);
  postMessage({ type: "status", text: "Loading the OpenGonio software…" });
  const zip = await (await fetch("opengonio.zip")).arrayBuffer();
  py.unpackArchive(zip, "zip", { extractDir: "/home/pyodide/og" });
  await py.runPythonAsync(GLUE);
  return py.globals.get("handle");
})();
ready.catch(e => postMessage({ type: "status", text: "Couldn't start Python here: " + e.message }));

onmessage = async e => {
  const m = e.data;
  try {
    const handle = await ready;
    const r = handle(m.method, m.path, m.query, m.body);
    const [status, body, bin] = r.toJs();
    r.destroy();
    if (bin) postMessage({ id: m.id, status, ctype: body, bin }, [bin.buffer]);
    else postMessage({ id: m.id, status, body });
  } catch (err) {
    postMessage({ id: m.id, status: 500, body: JSON.stringify({ error: String(err.message || err), kind: "internal" }) });
  }
};
