"""glTF 2.0 binary (.glb) writer and reader, no dependencies [T40].

One node, one mesh, one metallic-roughness material. Geometry stays in the scanner's millimetres and Z-up frame;
the node's scale (0.001) and rotation (-90 deg about X) make it metres and Y-up, as glTF requires, so Blender,
Unity, Unreal and three.js place it right side up at its real size.
"""
from __future__ import annotations

import json
import math
import struct
from pathlib import Path

import numpy as np

from .material import Material
from .mesh import Mesh

Z_UP_TO_Y_UP = [-math.sin(math.pi / 4), 0.0, 0.0, math.cos(math.pi / 4)]     # quaternion x y z w


def _pad(b: bytes, fill: bytes) -> bytes:
    return b + fill * ((4 - len(b) % 4) % 4)


def glb_bytes(mesh: Mesh, material: Material, extras: dict | None = None) -> bytes:
    pos = np.ascontiguousarray(mesh.positions, np.float32)
    nrm = np.ascontiguousarray(mesh.normals, np.float32)
    idx = np.ascontiguousarray(mesh.indices, np.uint32)
    blobs = [pos.tobytes(), nrm.tobytes(), idx.tobytes()]
    views, offset = [], 0
    for b, target in zip(blobs, (34962, 34962, 34963)):              # ARRAY_BUFFER, ARRAY_BUFFER, ELEMENT_ARRAY_BUFFER
        views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(b), "target": target})
        offset += len(_pad(b, b"\x00"))
    binary = b"".join(_pad(b, b"\x00") for b in blobs)
    doc = {
        "asset": {"version": "2.0", "generator": "opengonio.render"},
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [{"name": mesh.name, "mesh": 0, "rotation": Z_UP_TO_Y_UP, "scale": [0.001] * 3}],
        "meshes": [{"name": mesh.name, "primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 2,
                                                       "material": 0, "mode": 4}]}],
        "materials": [material.to_gltf()],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(pos), "type": "VEC3",
             "min": pos.min(0).tolist(), "max": pos.max(0).tolist()},
            {"bufferView": 1, "componentType": 5126, "count": len(nrm), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5125, "count": int(idx.size), "type": "SCALAR"}],
        "bufferViews": views,
        "buffers": [{"byteLength": len(binary)}],
    }
    if extras:
        doc["asset"]["extras"] = extras
    js = _pad(json.dumps(doc, separators=(",", ":")).encode("utf-8"), b" ")
    total = 12 + 8 + len(js) + 8 + len(binary)
    return (struct.pack("<4sII", b"glTF", 2, total) + struct.pack("<I4s", len(js), b"JSON") + js
            + struct.pack("<I4s", len(binary), b"BIN\x00") + binary)


def write_glb(path: str | Path, mesh: Mesh, material: Material, extras: dict | None = None) -> Path:
    p = Path(path)
    p.write_bytes(glb_bytes(mesh, material, extras))
    return p


def read_glb(data: bytes | str | Path) -> tuple[dict, bytes]:
    """-> (glTF JSON, BIN chunk). Checks the header and chunk layout."""
    if not isinstance(data, (bytes, bytearray)):
        data = Path(data).read_bytes()
    magic, version, total = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or total != len(data):
        raise ValueError("not a glTF 2.0 binary")
    jl, jt = struct.unpack_from("<I4s", data, 12)
    if jt != b"JSON" or jl % 4:
        raise ValueError("first chunk must be 4-byte aligned JSON")
    doc = json.loads(data[20:20 + jl])
    bl, bt = struct.unpack_from("<I4s", data, 20 + jl)
    if bt != b"BIN\x00":
        raise ValueError("second chunk must be BIN")
    return doc, bytes(data[28 + jl:28 + jl + bl])


def mesh_from_glb(data: bytes | str | Path) -> tuple[Mesh, dict]:
    """First primitive of the first mesh -> Mesh (in the file's own units and axes) + its material JSON."""
    doc, binary = read_glb(data)
    prim = doc["meshes"][0]["primitives"][0]

    def acc(i):
        a = doc["accessors"][i]
        v = doc["bufferViews"][a["bufferView"]]
        dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}[a["componentType"]]
        n = {"VEC3": 3, "SCALAR": 1}[a["type"]]
        start = v.get("byteOffset", 0) + a.get("byteOffset", 0)
        return np.frombuffer(binary, dt, a["count"] * n, start).reshape(-1, n) if n > 1 else \
            np.frombuffer(binary, dt, a["count"], start)
    pos = acc(prim["attributes"]["POSITION"]).astype(float)
    nrm = acc(prim["attributes"]["NORMAL"]).astype(float)
    idx = acc(prim["indices"]).astype(np.int64).reshape(-1, 3)
    mat = doc["materials"][prim["material"]] if "material" in prim else {}
    return Mesh(pos, nrm, idx, doc["meshes"][0].get("name", "mesh")), mat
