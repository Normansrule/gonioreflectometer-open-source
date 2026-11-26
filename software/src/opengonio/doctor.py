"""`opengonio doctor`: which of the software this project uses is installed, and in which version.

Required: Python, numpy, PyYAML. Hardware (`pip install opengonio[hw]`): pyserial, OpenCV (camera, HDR merge, ArUco
markers). Optional: the desktop window, phone pairing, COLMAP for dense scans, LaTeX and pandoc for the paper and
exports, cadquery for CAD. Nothing here touches the machine.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import importlib
import platform
import shutil
import subprocess
from dataclasses import dataclass

REQUIRED, HARDWARE, OPTIONAL = "required", "hardware", "optional"


@dataclass(frozen=True)
class Item:
    name: str
    level: str
    used_for: str
    found: bool
    version: str = ""
    note: str = ""


def _module(name: str, attr: str = "__version__") -> tuple[bool, str]:
    try:
        m = importlib.import_module(name)
    except Exception:                                    # ImportError, or a broken binary wheel
        return False, ""
    return True, str(getattr(m, attr, ""))


def _program(name: str, flag: str = "--version") -> tuple[bool, str]:
    path = shutil.which(name)
    if not path:
        return False, ""
    try:
        out = subprocess.run([path, flag], capture_output=True, text=True, timeout=10)
        return True, ((out.stdout or out.stderr).strip().splitlines() or [""])[0][:60]
    except Exception:
        return True, ""


def opencv_features() -> dict[str, bool]:
    """The OpenCV parts the project calls; False when OpenCV, or that part of the build, is missing."""
    try:
        import cv2
    except Exception:
        return {"import": False, "aruco": False, "charuco": False, "hdr_debevec": False, "video_capture": False}
    aruco = getattr(cv2, "aruco", None)
    return {"import": True, "aruco": aruco is not None and hasattr(aruco, "ArucoDetector"),
            "charuco": aruco is not None and hasattr(aruco, "CharucoBoard"),
            "hdr_debevec": hasattr(cv2, "createMergeDebevec") and hasattr(cv2, "createCalibrateDebevec"),
            "video_capture": hasattr(cv2, "VideoCapture")}


def survey() -> list[Item]:
    from . import __version__
    items = [Item("opengonio", REQUIRED, "this software", True, __version__),
             Item("Python", REQUIRED, "runs everything", True, platform.python_version())]
    for mod, level, why in (("numpy", REQUIRED, "arrays, fitting, the simulator"), ("yaml", REQUIRED, "machine.yaml, plans"),
                            ("serial", HARDWARE, "USB link to the motor board and the hub"),
                            ("cv2", HARDWARE, "camera, HDR merge, ArUco markers, image files"),
                            ("webview", OPTIONAL, "control app in a desktop window"), ("segno", OPTIONAL, "QR code to pair a phone"),
                            ("cadquery", OPTIONAL, "regenerate the printed parts"), ("openpyxl", OPTIONAL, "Excel parts list export")):
        ok, ver = _module(mod)
        note = ""
        if mod == "cv2" and ok:
            feats = opencv_features()
            missing = [k for k, v in feats.items() if not v]
            note = "missing: " + ", ".join(missing) if missing else "ArUco, ChArUco, Debevec HDR and video capture present"
        items.append(Item({"yaml": "PyYAML", "serial": "pyserial", "cv2": "OpenCV", "webview": "pywebview"}.get(mod, mod), level, why, ok, ver, note))
    for prog, why in (("colmap", "dense 3D reconstruction (scan)"), ("latexmk", "paper PDF"), ("pandoc", "Word and wiki exports"), ("git", "releases")):
        ok, ver = _program(prog, "-v" if prog == "latexmk" else ("help" if prog == "colmap" else "--version"))
        items.append(Item(prog, OPTIONAL, why, ok, ver))
    return items


def report(items: list[Item] | None = None) -> tuple[str, int]:
    """Text table and exit code: 1 if something required is missing, else 0."""
    items = survey() if items is None else items
    width = max(len(i.name) for i in items)
    lines = []
    for i in items:
        state = "ok     " if i.found else ("MISSING" if i.level == REQUIRED else "absent ")
        lines.append(f"{state} {i.name:<{width}}  {i.level:<8}  {i.version:<22}  {i.used_for}" + (f" ({i.note})" if i.note else ""))
    hw = [i.name for i in items if i.level == HARDWARE and not i.found]
    if hw:
        lines.append(f"To drive the machine and the camera: pip install \"opengonio[hw]\" (absent: {', '.join(hw)}). The simulator works without it.")
    return "\n".join(lines), int(any(i.level == REQUIRED and not i.found for i in items))
