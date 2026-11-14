"""OpenGonio desktop app (PyInstaller entry point): the control app in its own window, runs kept in ~/OpenGonio/runs.

Double-click starts it not connected; choose the simulator or the machine over USB inside the app. Arguments pass
through to `opengonio app`, e.g. `OpenGonio --sim mirror` or `OpenGonio --lan` (phones on the same Wi-Fi pair with a
QR code). SPDX-License-Identifier: GPL-3.0-or-later
"""
import sys
from pathlib import Path

from opengonio.cli import main


def run() -> int:
    args = sys.argv[1:]
    if not any(a == "--data" or a.startswith("--data=") for a in args):
        runs = Path.home() / "OpenGonio" / "runs"
        runs.mkdir(parents=True, exist_ok=True)
        args += ["--data", str(runs)]
    if "--window" not in args and "--no-browser" not in args:
        args.append("--window")          # a native window where pywebview is bundled (Windows, macOS); else the browser
    return main(["app", *args])


if __name__ == "__main__":
    raise SystemExit(run())
