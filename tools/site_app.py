"""The control app on the website: docs/app/ runs the real opengonio package (simulated machine) in the browser.

Copies software/src/opengonio/app/static/{index.html, app.js, app.css, manifest, icons} into docs/app/ (pointing at the website's og/
files and adding the in-browser loader), and zips the package source + config into docs/app/opengonio.zip, which
docs/app/worker.js unpacks into Pyodide (Python compiled to WebAssembly). Same zip bytes for the same sources.
Hand-written: docs/app/browser.js (routes the app's /api/ calls to the worker) and docs/app/worker.js.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "software" / "src" / "opengonio" / "app" / "static"
OUT = ROOT / "docs" / "app"
NOTE = ('<p class="demo-note" role="note"><b>Web demo:</b> this is the real OpenGonio software (Python, run in your browser '
        'with Pyodide) driving the <b>simulated machine</b>. Nothing here talks to hardware. First load fetches about 20 MB. '
        '<a href="../inside.html">How it works</a> · <a href="../">Website</a></p>\n')
STYLE = ('<style>.demo-note{margin:0;padding:.5rem 1rem;font-size:.9rem;background:var(--ground-3);border-bottom:1px solid var(--rule)}'
         '.demo-note a{color:inherit}</style>\n')


def page() -> str:
    h = (STATIC / "index.html").read_text(encoding="utf-8")
    h = h.replace('href="og/', 'href="../og/').replace('src="og/', 'src="../og/')
    h = h.replace("<title>OpenGonio control</title>", "<title>OpenGonio control app (web demo)</title>")
    h = h.replace("</head>", STYLE + "</head>", 1)
    h = h.replace("<body>\n", "<body>\n" + NOTE, 1)
    h = h.replace('<script src="app.js"></script>', '<script src="browser.js"></script>\n<script src="app.js"></script>', 1)
    assert h.count("browser.js") == 1 and h.count("demo-note") >= 2, "app/static/index.html changed shape: update tools/site_app.py"
    return h


def package_zip() -> bytes:
    files = sorted(p for p in (ROOT / "software" / "src" / "opengonio").rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts and "static" not in p.parts and p.suffix in (".py", ".yaml"))
    files += [ROOT / "software" / "config" / "machine.yaml", ROOT / "software" / "config" / "calibration.yaml"]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            info = zipfile.ZipInfo(f.relative_to(ROOT).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type, info.external_attr = zipfile.ZIP_DEFLATED, 0o644 << 16
            z.writestr(info, f.read_bytes())
    return buf.getvalue()


def write_if_changed(path: Path, data: bytes) -> None:
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    write_if_changed(OUT / "index.html", page().encode("utf-8"))
    for name in ("app.js", "app.css", "manifest.webmanifest"):
        write_if_changed(OUT / name, (STATIC / name).read_bytes())
    (OUT / "icons").mkdir(exist_ok=True)
    for f in sorted((STATIC / "icons").glob("*.png")):
        write_if_changed(OUT / "icons" / f.name, f.read_bytes())
    z = package_zip()
    write_if_changed(OUT / "opengonio.zip", z)
    print(f"docs/app: control app web demo, package zip {len(z) // 1024} kB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
