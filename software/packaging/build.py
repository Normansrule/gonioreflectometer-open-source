"""Build the OpenGonio desktop app for this computer's system with PyInstaller -> dist/OpenGonio-<os>.zip.

Run by .github/workflows/desktop.yml on Windows, macOS and Linux (each builds only its own system). By hand:
    pip install ./software pyserial opencv-python-headless segno pyinstaller [pywebview]
    python software/packaging/build.py
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIST = ROOT / "dist"
OS = {"Windows": "windows", "Darwin": "macos", "Linux": "linux"}[platform.system()]


def main() -> int:
    work = ROOT / "build" / "desktop"
    shutil.rmtree(work, ignore_errors=True)
    args = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--name", "OpenGonio",
            "--distpath", str(work / "dist"), "--workpath", str(work / "work"), "--specpath", str(work),
            "--collect-data", "opengonio", "--collect-submodules", "opengonio",
            "--hidden-import", "serial.tools.list_ports", "--hidden-import", "segno"]
    if OS == "windows":
        args += ["--onefile", "--windowed", "--icon", str(HERE / "icon.ico")]
    elif OS == "macos":
        args += ["--windowed", "--icon", str(HERE / "icon.icns"), "--osx-bundle-identifier", "org.opengonio.app"]
    else:
        args += ["--onefile", "--icon", str(HERE / "icon-512.png")]
    subprocess.run([*args, str(HERE / "opengonio_desktop.py")], check=True, cwd=ROOT)
    DIST.mkdir(exist_ok=True)
    out = DIST / f"OpenGonio-{OS}.zip"
    built = work / "dist"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(built.rglob("*")):
            if f.is_file():
                info = zipfile.ZipInfo.from_file(f, f.relative_to(built).as_posix())
                info.external_attr = (0o755 if f.stat().st_mode & 0o111 else 0o644) << 16   # keep the executable bit
                z.writestr(info, f.read_bytes(), zipfile.ZIP_DEFLATED)
        z.writestr("README.txt", (HERE / "README-desktop.txt").read_text(encoding="utf-8"))
    print(out, out.stat().st_size // (1 << 20), "MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
