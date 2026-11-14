"""Rendering: the measured material reaches a picture and a .glb unchanged (render/ package)."""
import json
import math

import numpy as np
import pytest

from opengonio.fit import _vec, fit, ggx
from opengonio.render.demo import measure, mug_mask
from opengonio.render.gltf import glb_bytes, mesh_from_glb, read_glb
from opengonio.render.material import SIM_TRUTH, Material
from opengonio.render.mesh import from_voxels, read_ply_mesh, shader_ball, uv_sphere, write_ply_mesh
from opengonio.render.raster import ggx_world, render


def test_world_space_brdf_is_the_fitted_brdf():
    """raster.ggx_world (any normal) equals fit.ggx (normal +Z) after rotating the frame."""
    rng = np.random.default_rng(1)
    ti, pi_, tr, pr = rng.uniform(0, 80, 50), rng.uniform(0, 360, 50), rng.uniform(0, 80, 50), rng.uniform(0, 360, 50)
    wi, wo = _vec(ti, pi_), _vec(tr, pr)
    a, ax = 0.7, np.array([1.0, 2.0, -0.5]) / np.linalg.norm([1.0, 2.0, -0.5])
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    R = np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
    n = np.tile(R @ [0, 0, 1.0], (50, 1))
    for b, r, m in [(0.2, 0.3, 0.0), (0.8, 0.9, 0.0), (0.9, 0.1, 1.0), (0.5, 0.6, 0.4)]:
        ref = ggx(wi, wo, b, r, m)
        got = ggx_world(n, wi @ R.T, wo @ R.T, (b, b, b), r, m)
        assert np.allclose(got[:, 0], ref, rtol=1e-9, atol=1e-12)


@pytest.mark.parametrize("name", ["plastic", "paper", "mirror"])
def test_fit_recovers_simulated_material(name):
    res = fit(measure(name))
    t = SIM_TRUTH[name]
    assert abs(res["base_color"] - t["base_color"]) < 0.03
    assert abs(res["roughness"] - t["roughness"]) < 0.03
    assert abs(res["metallic"] - t["metallic"]) < 0.05


def test_material_from_fit_json(tmp_path):
    fj = {"base_color": 0.4, "roughness": 0.35, "metallic": 0.0, "rms_pct_of_peak": 1.2,
          "holdout": {"rms_pct_of_peak": 1.5}, "provenance": {"relative_only": True}}
    (tmp_path / "fit.json").write_text(json.dumps(fj))
    m = Material.from_fit(tmp_path, color=(1.0, 0.5, 0.25))
    assert m.base_color == (0.4, 0.2, 0.1) and m.roughness == 0.35
    assert any("relative" in n for n in m.notes) and any("holdout" in n for n in m.notes)
    g = m.to_gltf()["pbrMetallicRoughness"]
    assert g == {"baseColorFactor": [0.4, 0.2, 0.1, 1.0], "metallicFactor": 0.0, "roughnessFactor": 0.35}
    assert m.engines()["Unity (URP Lit, metallic)"]["Smoothness"] == 0.65


def test_glb_is_valid_gltf_and_round_trips():
    mesh = shader_ball()
    data = glb_bytes(mesh, Material.sim("plastic"))
    doc, binary = read_glb(data)
    assert doc["asset"]["version"] == "2.0" and len(data) % 4 == 0
    assert doc["buffers"][0]["byteLength"] == len(binary)
    pos = doc["accessors"][0]
    assert np.allclose(pos["min"], mesh.positions.min(0), atol=1e-4) and np.allclose(pos["max"], mesh.positions.max(0), atol=1e-4)
    for v in doc["bufferViews"]:
        assert v["byteOffset"] % 4 == 0 and v["byteOffset"] + v["byteLength"] <= len(binary)
    assert doc["nodes"][0]["scale"] == [0.001] * 3                       # mm -> m
    back, mat = mesh_from_glb(data)
    assert np.allclose(back.positions, mesh.positions, atol=1e-4) and (back.indices == mesh.indices).all()
    assert mat["pbrMetallicRoughness"]["roughnessFactor"] == 0.3


def test_voxel_hull_mesh_is_closed_and_outward(tmp_path):
    n = 24
    g = (np.arange(n) + 0.5) - n / 2
    X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
    occ = X ** 2 + Y ** 2 + Z ** 2 < 9.0 ** 2
    m = from_voxels(occ, origin=[-12, -12, -12], voxel_mm=1.0, smooth_iters=0)
    e = np.sort(np.vstack([m.indices[:, [0, 1]], m.indices[:, [1, 2]], m.indices[:, [2, 0]]]), axis=1)
    _, counts = np.unique(e, axis=0, return_counts=True)
    assert (counts % 2 == 0).all()                                         # every edge shared: watertight
    assert m.volume_mm3() == pytest.approx(occ.sum(), rel=1e-9)            # exact voxel volume, positive = outward
    smooth = from_voxels(occ, origin=[-12, -12, -12], voxel_mm=1.0)
    assert smooth.volume_mm3() == pytest.approx(4 / 3 * math.pi * 9 ** 3, rel=0.08)
    back = read_ply_mesh(write_ply_mesh(tmp_path / "m.ply", smooth))
    assert back.triangles == smooth.triangles


def test_lambert_sphere_brightness_matches_the_formula():
    """Head-on lamp, no sky: the sphere's centre pixel is base/pi x E (then tone curve)."""
    mat = Material("white", (0.8, 0.8, 0.8), 1.0, 0.0)
    out = render(uv_sphere(20), mat, (121, 121), cam_az=0, cam_el=0, light_az=0, light_el=0,
                 lamp_irradiance=1.0, sky_scale=0.0, background=False)
    c = out["linear"][60, 60, 0]
    f0 = 0.04
    expect = (1 - f0) * 0.8 / math.pi + (1 / (math.pi * 1.0)) * f0 / 4      # GGX at alpha 1, normal incidence, + diffuse
    assert c == pytest.approx(expect, rel=0.02)
    frac = out["mask"].mean()
    assert 0.45 < frac < 0.75                                               # bounding sphere fills the frame (pi/4 x 0.8)


def test_mug_silhouette_and_hull_volume():
    K = np.array([[300.0, 0, 100], [0, 300.0, 100], [0, 0, 1]])
    R = np.array([[0.0, 1, 0], [0, 0, -1], [-1, 0, 0]])                   # camera on -X looking +X, image y down
    t = np.array([0.0, 20.0, 200.0])
    m = mug_mask(K, R, t, 200, 200)
    assert 0.05 < m.mean() < 0.4 and not m[0].any() and not m[-1].any()
