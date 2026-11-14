"""Software renderer (numpy): z-buffer rasteriser + the fitted BRDF, for pictures without a GPU or a game engine.

Shading = one lamp, exact model:  L = f_r(l, v) * E * max(n.l, 0), with f_r the Lambert + GGX of fit.py (same
formula, written for world-space vectors; tests check the two agree), plus a studio that is approximate:
diffuse = studio irradiance x diffuse colour, specular = studio radiance in the mirror direction x a fitted
environment-BRDF curve (Karis 2014 [T57]). Only the lamp term is the measured
material exactly; the studio (sky gradient + two softboxes) is there so shadowed sides are not black and metals
have something to reflect.
Tone: exposure, ACES filmic fit [T58], sRGB. render-gl.js does the same steps on the GPU.
"""
from __future__ import annotations

import math

import numpy as np

from .material import Material
from .mesh import Mesh


def ggx_world(n, l, v, base, rough: float, metal: float, f0_d: float = 0.04) -> np.ndarray:
    """f_r(l, v) for unit vectors (..., 3) about normal n (..., 3); base (3,) -> (..., 3). Twin of fit.ggx."""
    base = np.asarray(base, float)
    ci = np.einsum("...k,...k", n, l)
    co = np.einsum("...k,...k", n, v)
    h = l + v
    h = h / np.maximum(np.linalg.norm(h, axis=-1, keepdims=True), 1e-12)
    a = max(rough * rough, 1e-4)
    a2 = a * a
    ch = np.einsum("...k,...k", n, h)
    d = a2 / (math.pi * (ch * ch * (a2 - 1) + 1) ** 2)
    cic, coc = np.clip(ci, 1e-6, 1), np.clip(co, 1e-6, 1)
    g = 2 * cic * coc / (coc * np.sqrt(cic * cic * (1 - a2) + a2) + cic * np.sqrt(coc * coc * (1 - a2) + a2))
    f0 = f0_d * (1 - metal) + base * metal                                    # (3,)
    fw = (1 - np.clip(np.einsum("...k,...k", l, h), 0, 1)) ** 5
    f = f0 + (1 - f0) * fw[..., None]
    spec = (d * g / (4 * cic * coc))[..., None] * f
    diff = (1 - metal) * (1 - f) * base / math.pi
    ok = ((ci > 0) & (co > 0))[..., None]
    return np.where(ok, spec + diff, 0.0)


def env_brdf(rough, nov) -> tuple[np.ndarray, np.ndarray]:
    """Karis 2014 [T57] analytic fit of the split-sum environment BRDF: specular = F0 * A + B."""
    r = np.asarray(rough)[..., None] * np.array([-1, -0.0275, -0.572, 0.022]) + np.array([1, 0.0425, 1.04, -0.04])
    a004 = np.minimum(r[..., 0] ** 2, np.exp2(-9.28 * nov)) * r[..., 0] + r[..., 1]
    return -1.04 * a004 + r[..., 2], 1.04 * a004 + r[..., 3]


SKY, GROUND = np.array([0.32, 0.34, 0.38]), np.array([0.10, 0.09, 0.08])
BOX, SIDE = np.array([1.0, 0.97, 0.92]), np.array([-0.5717, -0.7146, 0.4033])     # a studio: overhead + side softbox


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def grad(d: np.ndarray) -> np.ndarray:
    t = np.clip(0.5 + 0.5 * d[..., 2], 0, 1)[..., None]
    return GROUND * (1 - t) + SKY * t


def sky_radiance(d: np.ndarray) -> np.ndarray:
    """Seen in a mirror: gradient + the two softboxes."""
    return grad(d) + BOX * (2.4 * smoothstep(0.86, 0.9, d[..., 2]) + 1.4 * smoothstep(0.93, 0.96, d @ SIDE))[..., None]


def sky_irradiance(n: np.ndarray) -> np.ndarray:
    """Felt by a rough surface: gradient + a broad share of the softboxes."""
    return grad(n) + BOX * (0.3 * np.clip(n[..., 2], 0, None) ** 2 + 0.1 * np.clip(n @ SIDE, 0, None) ** 2)[..., None]


def aces(x: np.ndarray) -> np.ndarray:
    return np.clip(x * (2.51 * x + 0.03) / (x * (2.43 * x + 0.59) + 0.14), 0, 1)


def to_srgb8(lin: np.ndarray) -> np.ndarray:
    c = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.power(np.clip(lin, 0, None), 1 / 2.4) - 0.055)
    return np.clip(np.round(c * 255), 0, 255).astype(np.uint8)


def sph(az_deg: float, el_deg: float) -> np.ndarray:
    a, e = math.radians(az_deg), math.radians(el_deg)
    return np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])


def camera(eye, target, fov_deg: float, w: int, h: int):
    f = target - eye
    f = f / np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1.0])
    r = r / np.linalg.norm(r)
    u = np.cross(r, f)
    fy = 0.5 * h / math.tan(math.radians(fov_deg) / 2)
    return np.stack([r, -u, f]), fy                                           # rows: camera x (right), y (down), z (forward)


def render(mesh: Mesh, mat: Material, size: tuple[int, int] = (320, 320), cam_az: float = -55.0, cam_el: float = 22.0,
           light_az: float = 35.0, light_el: float = 40.0, lamp_irradiance: float = 2.6, sky_scale: float = 1.0,
           exposure: float = 1.0, fov_deg: float = 28.0, background: bool = True) -> dict:
    """-> {"image": uint8 (H, W, 3), "linear": float radiance, "mask": bool coverage}. Angles in degrees, Z up."""
    w, h = size
    lo, hi = mesh.bounds()
    target = (lo + hi) / 2
    radius = float(np.linalg.norm(mesh.positions - target, axis=1).max())     # bounding sphere: frames any view
    dist = 1.12 * radius / math.sin(math.radians(fov_deg) / 2)
    eye = target + dist * sph(cam_az, cam_el)
    Rc, fpx = camera(eye, target, fov_deg, w, h)
    pc = (mesh.positions - eye) @ Rc.T                                       # camera frame
    z = pc[:, 2]
    sx = fpx * pc[:, 0] / z + w / 2
    sy = fpx * pc[:, 1] / z + h / 2
    tid, bary = rasterize(sx, sy, z, mesh.indices, w, h)
    mask = tid >= 0
    ys, xs = np.nonzero(mask)
    tri = mesh.indices[tid[mask]]
    bw = bary[mask]
    p = np.einsum("ij,ijk->ik", bw, mesh.positions[tri])
    n = np.einsum("ij,ijk->ik", bw, mesh.normals[tri])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    v = eye - p
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    flip = np.einsum("ij,ij->i", n, v) < 0                                    # interpolated normal past the silhouette
    n[flip] = n[flip] - 2 * np.einsum("ij,ij->i", n[flip], v[flip])[:, None] * v[flip]
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    l = sph(light_az, light_el)[None, :].repeat(len(p), 0)
    base = np.asarray(mat.base_color, float)
    nl = np.clip(np.einsum("ij,ij->i", n, l), 0, None)
    lamp = ggx_world(n, l, v, base, mat.roughness, mat.metallic) * (lamp_irradiance * nl)[:, None]
    nov = np.clip(np.einsum("ij,ij->i", n, v), 1e-4, 1)
    r = 2 * nov[:, None] * n - v
    f0 = 0.04 * (1 - mat.metallic) + base * mat.metallic
    A, B = env_brdf(mat.roughness, nov)
    spec_env = sky_radiance(r) * (1 - mat.roughness) + sky_irradiance(n) * mat.roughness    # rougher: a blurrier studio
    sp = f0 * A[:, None] + B[:, None]
    ambient = (1 - mat.metallic) * base * sky_irradiance(n) * (1 - sp) + spec_env * sp
    lin = np.zeros((h, w, 3))
    if background:
        g = np.linspace(1, 0, h)[:, None, None]
        lin[:] = 0.05 + 0.07 * g
    lin[ys, xs] = lamp + sky_scale * ambient
    img = to_srgb8(aces(lin * exposure))
    return {"image": img, "linear": lin, "mask": mask}


def rasterize(sx, sy, z, idx, w: int, h: int, chunk: int = 4096):
    """Front-facing triangles -> per-pixel triangle id (-1 = empty) and perspective-correct barycentrics.
    Vectorised: every triangle tests the pixels of its bounding box at once (triangles grouped by box size),
    fragments are depth-sorted and the nearest per pixel wins."""
    X, Y, Z = sx[idx], sy[idx], z[idx]                                          # (T, 3)
    area = (X[:, 1] - X[:, 0]) * (Y[:, 2] - Y[:, 0]) - (X[:, 2] - X[:, 0]) * (Y[:, 1] - Y[:, 0])
    keep = (area < 0) & (Z.min(1) > 0)                                          # front-facing (y down) and in front
    x0 = np.clip(np.floor(X.min(1)), 0, w).astype(int)
    x1 = np.clip(np.floor(X.max(1)) + 1, 0, w).astype(int)
    y0 = np.clip(np.floor(Y.min(1)), 0, h).astype(int)
    y1 = np.clip(np.floor(Y.max(1)) + 1, 0, h).astype(int)
    keep &= (x1 > x0) & (y1 > y0)
    bw, bh = x1 - x0, y1 - y0
    frag_t, frag_p, frag_d, frag_b = [], [], [], []
    for size in (2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096):
        sel = np.flatnonzero(keep & (np.maximum(bw, bh) <= size) & (np.maximum(bw, bh) > size // 2 if size > 2 else True))
        for s in range(0, len(sel), max(1, chunk * 16 // (size * size))):
            tt = sel[s:s + max(1, chunk * 16 // (size * size))]
            oy, ox = np.meshgrid(np.arange(size), np.arange(size), indexing="ij")
            px = x0[tt, None, None] + ox + 0.5
            py = y0[tt, None, None] + oy + 0.5
            Xt, Yt, A = X[tt][:, :, None, None], Y[tt][:, :, None, None], area[tt][:, None, None]
            b0 = ((Xt[:, 1] - px) * (Yt[:, 2] - py) - (Xt[:, 2] - px) * (Yt[:, 1] - py)) / A
            b1 = ((Xt[:, 2] - px) * (Yt[:, 0] - py) - (Xt[:, 0] - px) * (Yt[:, 2] - py)) / A
            b2 = 1 - b0 - b1
            ins = (b0 >= 0) & (b1 >= 0) & (b2 >= 0) & (px < x1[tt, None, None]) & (py < y1[tt, None, None])
            k, iy, ix = np.nonzero(ins)
            if not len(k):
                continue
            zt = Z[tt][k]
            bb = np.stack([b0[k, iy, ix], b1[k, iy, ix], b2[k, iy, ix]], -1) / zt
            iz = bb.sum(1)
            frag_t.append(tt[k]); frag_d.append(1 / iz); frag_b.append(bb / iz[:, None])
            frag_p.append((y0[tt][k] + iy) * w + x0[tt][k] + ix)
    tid = np.full(h * w, -1, np.int64)
    bary = np.zeros((h * w, 3))
    if frag_t:
        ft, fp, fd, fb = (np.concatenate(a) for a in (frag_t, frag_p, frag_d, frag_b))
        order = np.lexsort((fd, fp))                                           # by pixel, then nearest first
        fp, ft, fb = fp[order], ft[order], fb[order]
        first = np.r_[True, fp[1:] != fp[:-1]]
        tid[fp[first]] = ft[first]
        bary[fp[first]] = fb[first]
    return tid.reshape(h, w), bary.reshape(h, w, 3)
