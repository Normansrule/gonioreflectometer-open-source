# 3D scanning

The camera never moves; the sample axes turn the object, so every photo's pose is known.

1. **Pose from the axes:** camera calibrated once against the turntable (hand-eye, AX = YB) [@V15].
2. **Quick shape:** silhouettes → visual hull [@S5].
3. **Full mesh:** photogrammetry [@V40], then screened Poisson reconstruction [@V46].
4. **Surface detail (optional LED bank):** photometric stereo from known light directions [@V27].
5. **Material:** measured BRDF fitted onto the mesh; export to a game engine ([Rendering](Rendering.md)).

Stages [11]({{REPO}}/phases/11-scan-capture) · [12]({{REPO}}/phases/12-scan-mesh) · [13]({{REPO}}/phases/13-object-material). Background: [Appendix C](Appendix-C-Calibration-and-3D.md).
