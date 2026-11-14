"""Rendering: the measured material on real geometry (stage 07 fit + stages 11-12 scan -> graphics).

    material.py  fit.json -> Material (glTF metallic-roughness, the convention Blender, Unity and Unreal share)
    mesh.py      sphere / shader ball / scanned visual hull -> triangle mesh
    gltf.py      Material + Mesh -> .glb (glTF 2.0 binary) that opens in Blender, Unity, Unreal, three.js
    raster.py    numpy software renderer: same GGX formula as fit.py, so the picture is the fitted model
    demo.py      the whole path offline: simulated measurement -> fit -> scanned object -> .glb + pictures
"""
