"""`opengonio render`: run folder (fit.json) or 'demo' -> .glb + PNG."""
from __future__ import annotations

import json
from pathlib import Path

from ..imageio import write_png


def main(a, cfg) -> int:
    from .gltf import mesh_from_glb, write_glb
    from .material import Material
    from .mesh import read_ply_mesh, shader_ball
    from .raster import render
    if a.what == "demo":
        from .demo import run
        rep = run(cfg.with_phase(max(cfg.installed_phase, 12)), a.out or "data/render_demo")
        for m in rep["materials"].values():
            m.pop("curve", None)
        print(json.dumps(rep, indent=1))
        return 0
    run_dir = Path(a.what)
    fit_file = run_dir / "fit.json" if run_dir.is_dir() else run_dir
    if not fit_file.is_file():
        print(f"no fit.json in {a.what}: run `opengonio fit {a.what}` first")
        return 2
    mat = Material.from_fit(fit_file, color=tuple(a.color) if a.color else None)
    if a.mesh:
        mp = Path(a.mesh)
        mesh = mesh_from_glb(mp)[0] if mp.suffix.lower() == ".glb" else read_ply_mesh(mp)
    else:
        mesh = shader_ball()
    out = Path(a.out) if a.out else fit_file.parent
    out.mkdir(parents=True, exist_ok=True)
    stem = mesh.name if a.mesh else "material"
    glb = write_glb(out / f"{stem}.glb", mesh, mat)
    png = out / f"{stem}.png"
    write_png(png, render(mesh, mat, (a.size, a.size))["image"])
    print(json.dumps({"material": mat.to_dict(), "glb": str(glb), "picture": str(png), "triangles": mesh.triangles,
                      "lighting": "one lamp (exact fitted model) + studio sky (approximate)"}, indent=1))
    return 0
