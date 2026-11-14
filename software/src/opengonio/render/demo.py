"""The whole path offline, no hardware: measure -> fit -> scan -> combine -> render.

    opengonio render demo --out data/render_demo

1. Measure: BRDF samples of each simulated material (sim.py's ground truth) at the in-plane plan's angles
   (theta_i 15/30/45/60 deg, theta_r 0-80 deg every 5 deg) with 2 % noise: what `capture inplane` + `curve` give.
2. Fit: fit.py on those samples (the same code as `opengonio fit`), with its holdout check.
3. Scan: a mug (body, cavity, handle) seen by the real scan plan's cameras (rings_plan, object_to_camera);
   silhouettes by ray marching its shape; carve.py builds the visual hull; mesh.py turns it into a mesh.
4. Combine: hull mesh + fitted material -> .glb (opens in Blender, Unity, Unreal, three.js).
5. Render: raster.py draws truth and fit side by side.
Everything is simulated: numbers here show the software works, not what the machine measures.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from ..fit import fit, holdout
from ..gantry.config import Machine
from ..imageio import write_png
from .gltf import write_glb
from .material import SIM_TRUTH, Material
from .mesh import from_voxels, shader_ball, write_ply_mesh
from .raster import ggx_world, render

THETA_I = (15.0, 30.0, 45.0, 60.0)
THETA_R = tuple(float(t) for t in range(0, 81, 5))


def measure(material: str, noise: float = 0.02, seed: int = 7) -> dict[str, np.ndarray]:
    """Simulated in-plane BRDF samples of a sim.py material (theta_r on the far side of the normal)."""
    rng = np.random.default_rng(seed)
    m = Material.sim(material)
    ti, tr = np.meshgrid(THETA_I, THETA_R, indexing="ij")
    ti, tr = ti.ravel(), tr.ravel()
    wi = np.stack([np.sin(np.radians(ti)), np.zeros_like(ti), np.cos(np.radians(ti))], -1)
    wo = np.stack([-np.sin(np.radians(tr)), np.zeros_like(tr), np.cos(np.radians(tr))], -1)
    n = np.tile([0.0, 0.0, 1.0], (len(ti), 1))
    if SIM_TRUTH[material].get("lambert"):
        f = np.full(len(ti), m.base_color[0] / math.pi)
    else:
        f = ggx_world(n, wi, wo, m.base_color, m.roughness, m.metallic)[:, 0]
    f = f * (1 + noise * rng.standard_normal(len(f)))
    return {"theta_i": ti, "phi_i": np.zeros_like(ti), "theta_r": tr, "phi_r": np.full_like(tr, 180.0), "f": f}


# ---- the scanned object: a mug, as a signed distance (mm, Z up, standing on z = 0)
def mug_sdf(p: np.ndarray) -> np.ndarray:
    r = np.hypot(p[..., 0], p[..., 1])
    def cyl(rad, z0, z1):
        return np.maximum(r - rad, np.maximum(z0 - p[..., 2], p[..., 2] - z1))
    body = np.maximum(cyl(18.0, 0.0, 40.0), -cyl(14.5, 3.0, 45.0))
    q = np.hypot(np.hypot(p[..., 0] - 22.0, p[..., 2] - 21.0) - 9.0, p[..., 1])
    handle = np.maximum(q - 3.2, 18.5 - p[..., 0])
    return np.minimum(body, handle)


def mug_mask(K: np.ndarray, R: np.ndarray, t: np.ndarray, w: int, h: int, steps: int = 400) -> np.ndarray:
    """Exact silhouette by sphere tracing the signed distance; only rays still in flight are stepped."""
    u, v = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
    d = (np.stack([u, v, np.ones_like(u)], -1) @ np.linalg.inv(K).T @ R).reshape(-1, 3)
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    o = -R.T @ t
    c = np.array([4.0, 0.0, 20.0])                               # bounding sphere of the mug (radius 36 mm)
    b = d @ (o - c)
    disc = b * b - (np.sum((o - c) ** 2) - 36.0 ** 2)
    ray = np.flatnonzero(disc > 0)
    s = np.maximum(-b[ray] - np.sqrt(disc[ray]), 0)
    far = -b[ray] + np.sqrt(disc[ray])
    hit = np.zeros(h * w, bool)
    for _ in range(steps):
        if not len(ray):
            break
        dist = mug_sdf(o + s[:, None] * d[ray])
        done = dist < 0.05
        hit[ray[done]] = True
        s = s + dist
        go = ~done & (s < far)
        ray, s, far = ray[go], s[go], far[go]
    return hit.reshape(h, w)


def scan(cfg: Machine, scale: float = 0.1, every: int = 2, voxel_mm: float = 1.0) -> tuple:
    from ..scan.carve import carve
    from ..scan.geometry import intrinsics, object_to_camera
    from ..scan.plan import rings_plan
    scfg = cfg.for_scan()
    K = intrinsics(scfg, cfg.scan["camera_distance_mm"]).scaled(scale)
    plan = rings_plan(cfg)[::every]
    views = [object_to_camera(scfg, sp.pose) for sp in plan]
    masks = [mug_mask(K.K, R, t, K.width, K.height) for R, t in views]
    half = 34.0
    grid = carve(masks, views, K.K, half_size_mm=half, n=int(2 * half / voxel_mm), center=np.array([4.0, 0.0, 20.0]),
                 clip_below_z=0.0)
    return grid, len(views), K


def true_volume_mm3(voxel_mm: float = 0.5) -> float:
    g = np.arange(-30, 38, voxel_mm) + voxel_mm / 2
    z = np.arange(-2, 44, voxel_mm) + voxel_mm / 2
    X, Y, Z = np.meshgrid(g, np.arange(-22, 22, voxel_mm) + voxel_mm / 2, z, indexing="ij")
    return float((mug_sdf(np.stack([X, Y, Z], -1)) < 0).sum() * voxel_mm ** 3)


def run(cfg: Machine, out_dir: str | Path = "data/render_demo", size: int = 280,
        materials: tuple[str, ...] = ("plastic", "paper", "mirror", "matte")) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ball = shader_ball()
    report = {"simulated": True, "note": "simulated measurement and scan: shows the software path, not machine accuracy",
              "materials": {}}
    fitted = {}
    for name in materials:
        data = measure(name)
        res = fit(data)
        res["holdout"] = holdout(data)
        res["provenance"] = {"relative_only": False, "quantity": "simulated grey BRDF", "model": "Lambert + GGX"}
        mat = Material.from_fit(res, name=f"{name}_fit")
        mat.source = f"fit of simulated {name} samples"
        truth = Material.sim(name)
        fitted[name] = mat
        for tag, m in (("truth", truth), ("fit", mat)):
            write_png(out / f"ball_{name}_{tag}.png", render(ball, m, (size, size))["image"])
        report["materials"][name] = {
            "truth": {k: SIM_TRUTH[name][k] for k in ("base_color", "roughness", "metallic")},
            "fit": {"base_color": res["base_color"], "roughness": res["roughness"], "metallic": res["metallic"]},
            "rms_pct_of_peak": res["rms_pct_of_peak"],
            "holdout_rms_pct_of_peak": (res["holdout"] or {}).get("rms_pct_of_peak"),
            "samples": int(len(data["f"])),
            "curve": {"theta_i": data["theta_i"].tolist(), "theta_r": data["theta_r"].tolist(),
                      "f": [round(float(x), 5) for x in data["f"]]}}
        (out / f"material_{name}.json").write_text(json.dumps(mat.to_dict(), indent=1), encoding="utf-8")
    grid, nviews, K = scan(cfg)
    hull = from_voxels(grid.occ, grid.origin, grid.voxel_mm)
    write_ply_mesh(out / "hull_mesh.ply", hull)
    show = fitted.get("plastic") or next(iter(fitted.values()))
    write_glb(out / "mug_hull.glb", hull, show, extras={"opengonio": {"simulated": True, "views": nviews}})
    write_glb(out / "shader_ball.glb", ball, show)
    for name, m in fitted.items():
        write_png(out / f"mug_{name}_fit.png", render(hull, m, (size, size), cam_az=-70, cam_el=25)["image"])
    tv = true_volume_mm3()
    report["scan"] = {"views": nviews, "image_px": [K.width, K.height], "voxel_mm": round(grid.voxel_mm, 3),
                      "triangles": hull.triangles, "hull_volume_cm3": round(hull.volume_mm3() / 1000, 2),
                      "true_volume_cm3": round(tv / 1000, 2),
                      "why_larger": "the visual hull cannot see the mug's cavity: silhouettes never show a hole"}
    report["files"] = sorted(p.name for p in out.iterdir())
    (out / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    return report
