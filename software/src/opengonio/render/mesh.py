"""Triangle meshes for rendering: test shapes and the scanner's visual hull.

Units: millimetres, object frame (Z up, the scanner's frame). gltf.py scales to metres and turns Z-up into glTF's
Y-up on export, so the numbers here stay the scanner's numbers.
from_voxels: the boundary faces of the carved voxel grid (every face between a kept and an empty voxel), welded,
then Taubin smoothing (lambda / mu steps: smooths without shrinking [T56]) so the voxel steps do not
read as the object's texture. It is still the visual hull: concavities stay filled.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Mesh:
    positions: np.ndarray        # (N, 3) float, mm
    normals: np.ndarray          # (N, 3) float, unit
    indices: np.ndarray          # (M, 3) int, counter-clockwise seen from outside
    name: str = "mesh"

    @property
    def triangles(self) -> int:
        return int(len(self.indices))

    def bounds(self) -> tuple[np.ndarray, np.ndarray]:
        return self.positions.min(0), self.positions.max(0)

    def volume_mm3(self) -> float:
        """Signed volume (divergence theorem); positive when the faces point outward."""
        a, b, c = (self.positions[self.indices[:, k]] for k in range(3))
        return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)


def vertex_normals(pos: np.ndarray, idx: np.ndarray) -> np.ndarray:
    a, b, c = (pos[idx[:, k]] for k in range(3))
    fn = np.cross(b - a, c - a)                     # length = 2 x area: area-weighted
    n = np.zeros_like(pos, dtype=float)
    for k in range(3):
        np.add.at(n, idx[:, k], fn)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    return n / np.where(ln > 0, ln, 1.0)


def merge(*meshes: Mesh, name: str = "mesh") -> Mesh:
    pos, nrm, idx, off = [], [], [], 0
    for m in meshes:
        pos.append(m.positions); nrm.append(m.normals); idx.append(m.indices + off); off += len(m.positions)
    return Mesh(np.vstack(pos), np.vstack(nrm), np.vstack(idx), name)


def uv_sphere(radius: float = 25.0, n_lat: int = 48, n_lon: int = 96, center=(0.0, 0.0, 0.0), name: str = "sphere") -> Mesh:
    th = np.linspace(0, math.pi, n_lat + 1)
    ph = np.linspace(0, 2 * math.pi, n_lon + 1)
    T, P = np.meshgrid(th, ph, indexing="ij")
    n = np.stack([np.sin(T) * np.cos(P), np.sin(T) * np.sin(P), np.cos(T)], -1).reshape(-1, 3)
    i = np.arange(n_lat)[:, None] * (n_lon + 1) + np.arange(n_lon)[None, :]
    a, b, c, d = i, i + 1, i + n_lon + 1, i + n_lon + 2
    idx = np.vstack([np.stack([a, c, b], -1).reshape(-1, 3), np.stack([b, c, d], -1).reshape(-1, 3)])
    pos = n * radius + np.asarray(center, float)
    return Mesh(pos, n.copy(), idx.astype(np.int64), name)


def cylinder(radius: float, z0: float, z1: float, n: int = 96, name: str = "cylinder") -> Mesh:
    """Closed cylinder: side (smooth normals) + two caps (flat normals)."""
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    ring = np.stack([np.cos(a), np.sin(a), np.zeros(n)], -1)
    side_p = np.vstack([ring * radius + [0, 0, z0], ring * radius + [0, 0, z1]])
    side_n = np.vstack([ring, ring])
    j = np.arange(n)
    k = (j + 1) % n
    side_i = np.vstack([np.stack([j, k, j + n], -1), np.stack([k, k + n, j + n], -1)])
    meshes = [Mesh(side_p, side_n, side_i)]
    for z, up in ((z1, 1.0), (z0, -1.0)):
        p = np.vstack([[0, 0, z], ring * radius + [0, 0, z]])
        nn = np.tile([0, 0, up], (n + 1, 1)).astype(float)
        tri = np.stack([np.zeros(n, int), j + 1, k + 1], -1) if up > 0 else np.stack([np.zeros(n, int), k + 1, j + 1], -1)
        meshes.append(Mesh(p, nn, tri))
    return merge(*meshes, name=name)


def shader_ball(radius: float = 25.0) -> Mesh:
    """Sphere resting on a short plinth: the usual material-preview object (shows highlights, grazing edges, contact)."""
    return merge(uv_sphere(radius, center=(0, 0, 0.9 * radius)),
                 cylinder(0.55 * radius, -0.25 * radius, 0.1 * radius), name="shader_ball")


def from_voxels(occ: np.ndarray, origin, voxel_mm: float, smooth_iters: int = 24, name: str = "visual_hull") -> Mesh:
    """Kept-voxel boundary -> welded, smoothed triangle mesh (outward faces)."""
    occ = np.asarray(occ, bool)
    nx, ny, nz = occ.shape
    pad = np.pad(occ, 1)
    quads = []
    # corner offsets of the face perpendicular to each axis, ordered so (+) faces wind outward
    for ax in range(3):
        for sgn in (1, -1):
            nb = np.roll(pad, -sgn, axis=ax)[1:-1, 1:-1, 1:-1]
            cells = np.argwhere(occ & ~nb)
            if not len(cells):
                continue
            base = cells.copy()
            if sgn > 0:
                base[:, ax] += 1
            u, v = (ax + 1) % 3, (ax + 2) % 3
            du, dv = np.zeros(3, int), np.zeros(3, int)
            du[u], dv[v] = 1, 1
            c = [base, base + du, base + du + dv, base + dv]
            if sgn < 0:
                c = c[::-1]
            quads.append(np.stack(c, 1))
    if not quads:
        raise ValueError("no kept voxels: nothing to mesh")
    q = np.vstack(quads)                                            # (F, 4, 3) lattice corners
    key = (q[..., 0] * (ny + 1) + q[..., 1]) * (nz + 1) + q[..., 2]
    uniq, inv = np.unique(key.ravel(), return_inverse=True)
    inv = inv.reshape(-1, 4)
    lat = np.stack([uniq // ((ny + 1) * (nz + 1)), (uniq // (nz + 1)) % (ny + 1), uniq % (nz + 1)], -1)
    pos = np.asarray(origin, float) + lat * voxel_mm
    idx = np.vstack([inv[:, [0, 1, 2]], inv[:, [0, 2, 3]]])
    pos = taubin(pos, idx, smooth_iters)
    return Mesh(pos, vertex_normals(pos, idx), idx.astype(np.int64), name)


def taubin(pos: np.ndarray, idx: np.ndarray, iters: int = 8, lam: float = 0.5, mu: float = -0.53) -> np.ndarray:
    if iters <= 0:
        return pos
    e = np.vstack([idx[:, [0, 1]], idx[:, [1, 2]], idx[:, [2, 0]]])
    e = np.unique(np.sort(np.vstack([e, e[:, ::-1]]), axis=1), axis=0)
    deg = np.bincount(e.ravel(), minlength=len(pos)).astype(float)
    p = pos.astype(float).copy()
    for _ in range(iters):
        for f in (lam, mu):
            s = np.zeros_like(p)
            np.add.at(s, e[:, 0], p[e[:, 1]])
            np.add.at(s, e[:, 1], p[e[:, 0]])
            p += f * (s / np.maximum(deg, 1)[:, None] - p)
    return p


def write_ply_mesh(path: str | Path, mesh: Mesh) -> Path:
    """ASCII PLY with faces (Blender, MeshLab [S16]); millimetres, Z up."""
    hdr = ["ply", "format ascii 1.0", f"comment opengonio {mesh.name} (mm, Z up)", f"element vertex {len(mesh.positions)}",
           "property float x", "property float y", "property float z", "property float nx", "property float ny",
           "property float nz", f"element face {len(mesh.indices)}", "property list uchar int vertex_indices", "end_header"]
    v = "\n".join(" ".join(f"{x:.4f}" for x in r) for r in np.hstack([mesh.positions, mesh.normals]))
    f = "\n".join("3 " + " ".join(str(int(i)) for i in t) for t in mesh.indices)
    Path(path).write_text("\n".join(hdr) + "\n" + v + "\n" + f + "\n", encoding="utf-8")
    return Path(path)


def read_ply_mesh(path: str | Path) -> Mesh:
    """ASCII PLY with x y z [nx ny nz] and triangle faces (what write_ply_mesh writes)."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "ply" or "ascii" not in lines[1]:
        raise ValueError("only ASCII PLY is read here")
    nv = nf = 0
    props = []
    i = 0
    for i, ln in enumerate(lines):
        w = ln.split()
        if w[:2] == ["element", "vertex"]:
            nv = int(w[2])
        elif w[:2] == ["element", "face"]:
            nf = int(w[2])
        elif w and w[0] == "property" and nf == 0 and w[1] != "list":
            props.append(w[-1])
        elif ln.strip() == "end_header":
            break
    if nf == 0:
        raise ValueError("PLY has no faces (a point cloud, like hull.ply): use hull_mesh.ply")
    v = np.array([[float(x) for x in lines[i + 1 + k].split()] for k in range(nv)])
    f = np.array([[int(x) for x in lines[i + 1 + nv + k].split()[1:4]] for k in range(nf)])
    pos = v[:, [props.index(a) for a in "xyz"]]
    nrm = v[:, [props.index(a) for a in ("nx", "ny", "nz")]] if "nx" in props else vertex_normals(pos, f)
    return Mesh(pos, nrm, f, Path(path).stem)
