# Rendering

What the machine measures, on a real shape: the fitted material and the scanned object as computer graphics.

| Step | Command | File |
|---|---|---|
| 1. Measure the Bidirectional Reflectance Distribution Function (BRDF) | `opengonio capture inplane` (after `calibrate white`) | `curve.csv` |
| 2. Fit base colour, roughness, metallic | `opengonio fit data/<run>` | `fit.json`, `fit.svg` |
| 3. Scan the object | `opengonio scan run`, `opengonio scan hull` | `hull_mesh.ply`, `hull.glb` |
| 4. Combine shape + material | `opengonio render data/<run> --mesh scan_out/hull_mesh.ply` | `hull_mesh.glb`, `hull_mesh.png` |
| 5. Render | [Render page](https://normansrule.github.io/gonioreflectometer-open-source/render.html), Blender, Unity, Unreal, three.js | pixels |

Without hardware: `opengonio render demo` runs all five on simulated data (`data/render_demo/`).

## One model everywhere

The fit is Lambert + GGX with metallic-roughness parameters [@R6] [@T40], the model glTF, Blender, Unreal [@T35] and Unity use. Three renderers draw it with the same formula:

| Renderer | Where | Use |
|---|---|---|
| `opengonio.render.raster` | numpy, CPU | pictures in scripts and tests; no GPU |
| `docs/og/render-gl.js` | WebGL 2, browser | Render page and the control app's material preview |
| Blender, Unity, Unreal, three.js | the `.glb` | production |

`tests/test_render.py` checks that the renderer's BRDF equals `fit.py`'s, and that a lit white sphere has the brightness the formula predicts.

## The `.glb`

- glTF 2.0 binary [@T40]: one mesh, one metallic-roughness material, provenance (run, holdout, notes) in `extras`.
- Geometry stays in the scanner's millimetres, Z up; the node's scale (0.001) and rotation make it metres, Y up.
- Unity: smoothness = 1 − roughness (URP Lit).

## Lighting

- Lamp: the fitted model, exactly.
- Studio (sky gradient + two softboxes): approximate. A fitted curve lights the shadowed sides [@T57]; it is not measured.
- Tone: ACES filmic [@T58], then sRGB.

## Scan → mesh

The visual hull's boundary voxels become triangles, then λ/μ smoothing removes the voxel steps without shrinking [@T56]. It is still the visual hull: cavities come out filled (the demo mug: hull 43 cm³ against 17 cm³ real).

## Limits

- Grey: one camera channel. A colour tint is typed by hand (`--color R G B`).
- One material per object; no texture.
- Isotropic only.
- Between and beyond the measured angles the picture is the model's guess: check the holdout in `fit.json`.

## In the control app

Under a run's curve: **Material**. With a fit it shows it; with absolute values it offers **Fit material**; a relative-only run says why it can't be fitted, and a simulated run previews the simulator's true material. **Download .glb** saves it on a shader ball.
