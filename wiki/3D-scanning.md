<!-- generated from wiki/src/3D-scanning.md by tools/refs_bib.py - edit the source -->

# 3D scanning

The camera never moves; the sample axes turn the object, so every photo’s pose is known.

1.  **Pose from the axes:** camera calibrated once against the turntable (hand-eye, AX = YB) (Shah, 2013).
2.  **Quick shape:** silhouettes → visual hull (Laurentini, 1994).
3.  **Full mesh:** photogrammetry (Griwodz et al., 2021), then screened Poisson reconstruction (Kazhdan & Hoppe, 2013).
4.  **Surface detail (optional LED bank):** photometric stereo from known light directions (Ackermann & Goesele, 2015).
5.  **Material:** measured BRDF fitted onto the mesh; export to a game engine ([Rendering](Rendering.md)).

Stages [11](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/phases/11-scan-capture) · [12](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/phases/12-scan-mesh) · [13](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/phases/13-object-material). Background: [Appendix C](Appendix-C-Calibration-and-3D.md).

## References

Ackermann, J., & Goesele, M. (2015). A survey of photometric stereo techniques. *Foundations and Trends in Computer Graphics and Vision*, *9*. <https://doi.org/10.1561/0600000065>

Griwodz, C. et al. (2021). AliceVision meshroom: An open-source 3D reconstruction pipeline. *Proc. ACM MMSys*. <https://doi.org/10.1145/3458305.3478443>

Kazhdan, M., & Hoppe, H. (2013). Screened Poisson surface reconstruction. *ACM Transactions on Graphics*, *32*(3), 29. <https://doi.org/10.1145/2487228.2487237>

Laurentini, A. (1994). The visual hull concept for silhouette-based image understanding. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, *16*(2). <https://doi.org/10.1109/34.273735>

Shah, M. (2013). Solving the robot-world/hand-eye calibration problem using the Kronecker product. *Journal of Mechanisms and Robotics*, *5*(3), 031007. <https://doi.org/10.1115/1.4024473>
