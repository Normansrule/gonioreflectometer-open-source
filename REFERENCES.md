# References

510 sources. IDs are cited in docs, code and the BOM `Refs` column; each phase README lists its IDs. Accessed 2026-10-03/07. All figures are original.

| Prefix | Topic |
|---|---|
| R | [Design, theory, firmware, alternatives](#primary-design-references) |
| S | [3D photo scanner](#3d-photo-scanner) |
| G | [Measurement devices and datasets](#measurement-devices-and-datasets) |
| T | [Reflectance models and material formats](#reflectance-models-and-material-formats) |
| V | [Calibration, HDR, photometric stereo, 3D scanning](#calibration-hdr-photometric-stereo-and-3d-scanning) |
| N | [Standards, colour, optics, safety](#standards-colour-optics-and-safety) |
| H | [Motion control, electronics, open hardware](#motion-control-electronics-and-open-hardware) |
| P C K L M F E | [Parts](#parts-power-and-electrical) |

## Primary design references

| ID | Source | Used for |
|---|---|---|
| **R1** | M. Ansari-Asl, M. Barbieri, G. Obein, J. Y. Hardeberg, "Optical and Electromechanical Design and Implementation of an Advanced Multispectral Device to Capture Material Appearance," *J. Imaging* 10(3):55, 2024. doi:[10.3390/jimaging10030055](https://doi.org/10.3390/jimaging10030055) · [article](https://www.mdpi.com/2313-433X/10/3/55) | Main design reference: layout, homing, safety, kinematics, optics, tests |
| **R2** | P. Hanrahan, *Reflection Models I: Ideal Materials*, CS348b Lecture 10, Stanford University, Spring 2016 (slides provided by the user) | BRDF equations (phase 00 theory) |
| **R3** | Stanford Spherical Gantry — [graphics.stanford.edu/projects/gantry](https://graphics.stanford.edu/projects/gantry/) | First-draft architecture |
| **R4** | Stanford Spherical Gantry specifications — [link](https://graphics.stanford.edu/projects/gantry/design/specifications.html) | First-draft sizing |

## Theory and algorithms

| ID | Source | Used for |
|---|---|---|
| **R5** | P. Debevec, J. Malik, "Recovering High Dynamic Range Radiance Maps from Photographs," *Proc. SIGGRAPH ’97*, 1997 — [PDF](https://pauldebevec.com/Research/HDR/debevec-siggraph97.pdf), [ACM](https://dl.acm.org/doi/10.1145/258734.258884) | Camera response + HDR for 8-bit UVC frames |
| **R6** | B. Walter, S. Marschner, H. Li, K. Torrance, "Microfacet Models for Refraction through Rough Surfaces," *EGSR*, 2007 (bibliographic; not fetched) | GGX distribution |
| **R7** | C. Schlick, "An Inexpensive BRDF Model for Physically-based Rendering," *Computer Graphics Forum* 13(3), 1994 (bibliographic; cited via [R2]) | Schlick Fresnel |
| **R8** | R. Cook, K. Torrance, "A Reflectance Model for Computer Graphics," *ACM TOG* 1(1), 1982 (bibliographic; cited via [R2]) | Cook-Torrance colour shift |
| **R9** | C. Ericson, *Real-Time Collision Detection*, Morgan Kaufmann, 2005, §5.1.9 (bibliographic) | Segment-segment distance in the collision model |

## Other rigs and data

| ID | Source | Used for |
|---|---|---|
| **R10** | Cornell gonioreflectometer — [link](http://w1.graphics.cornell.edu/research/measure/gonio.html) | Comparison |
| **R11** | S. Westin et al., Cornell three-axis gonioreflectometer, SPIE 5878-29 — [PDF](https://www.graphics.cornell.edu/~westin/SPIE_5878-29_Gonio.pdf) | Comparison |
| **R12** | Cornell measurement data — [link](https://www.graphics.cornell.edu/online/measurements/) | Validation data |
| **R13** | MERL BRDF database — [merl.com/brdf](https://www.merl.com/brdf/) | Validation data |
| **R14** | W. Matusik et al., MERL TR2003-83 — [PDF](https://www.merl.com/publications/docs/TR2003-83.pdf) | Comparison |
| **R15** | J. Dupuy, W. Jakob, "An Adaptive Parameterization for Efficient Material Acquisition and Rendering," 2018 — [link](https://rgl.epfl.ch/publications/Dupuy2018Adaptive) | Adaptive sampling (phase 17) |
| **R16** | RGL-EPFL material database — [link](https://rgl.epfl.ch/pages/lab/material-database) | Validation data |
| **R17** | J. Filip et al., specular BRDF with a goniometer, 2017 — [PDF](https://staff.utia.cas.cz/filip/papers/filip17brdf.pdf) | Comparison |
| **R18** | UTIA BTF database — [link](https://btf.utia.cas.cz/?faq=) | BTF context |
| **R19** | X-Rite TAC7 — [product](https://www.xrite.com/categories/appearance/tac7) | Commercial multi-light capture |
| **R37** | F. Schröder, master's thesis, 2019 — [link](https://f-schroeder.github.io/publication/masterthesis/) | DIY prior art |
| **R38** | GatherLab/Goniometer — [GitHub](https://github.com/GatherLab/Goniometer) | Consulted; emission goniometer, not used |
| **R39** | X-Rite TAC7 user guide — [PDF](https://www.xrite.com/-/media/xrite/files/manuals_and_userguides/t/tac7_user_guide_en.pdf) | Context |
| **R40** | X-Rite PANTORA — [link](https://www.xrite.com/pantora-software) | Context |

## 3D photo scanner

| ID | Source | Used for |
|---|---|---|
| **S1** | COLMAP output format — [format.html](https://colmap.github.io/format.html) ([source](https://colmap.github.io/_sources/format.rst.txt)); camera models — [cameras](https://colmap.github.io/_sources/cameras.rst.txt); PINHOLE params comment in [models.h](https://github.com/colmap/colmap/blob/ff8842e7d9e985bd0dd87169f61d5aaeb309ab32/src/colmap/sensor/models.h#L197) | COLMAP text model, quaternions |
| **S2** | COLMAP FAQ, "Reconstruct sparse/dense model from known camera poses" — [faq.html](https://colmap.github.io/faq.html); CLI — [cli.html](https://colmap.github.io/cli.html) | `run_colmap.sh` command sequence, meshing |
| **S3** | J. L. Schönberger, J.-M. Frahm, "Structure-from-Motion Revisited," CVPR 2016 — [CVF](https://openaccess.thecvf.com/content_cvpr_2016/html/Schonberger_Structure-From-Motion_Revisited_CVPR_2016_paper.html), [PDF](https://openaccess.thecvf.com/content_cvpr_2016/papers/Schonberger_Structure-From-Motion_Revisited_CVPR_2016_paper.pdf); J. L. Schönberger, E. Zheng, M. Pollefeys, J.-M. Frahm, "Pixelwise View Selection for Unstructured Multi-View Stereo," ECCV 2016 — [doi:10.1007/978-3-319-46487-9_31](https://link.springer.com/chapter/10.1007/978-3-319-46487-9_31), [mlanthology](https://mlanthology.org/eccv/2016/schonberger2016eccv-pixelwise/); COLMAP licence (BSD) — [license](https://colmap.github.io/license.html) | Photogrammetry engine |
| **S4** | R. J. Woodham, "Photometric method for determining surface orientation from multiple images," *Optical Engineering* 19(1), 1980 — [doi:10.1117/12.7972479](https://www.spiedigitallibrary.org/journals/optical-engineering/volume-19/issue-1/191139/Photometric-Method-For-Determining-Surface-Orientation-From-Multiple-Images/10.1117/12.7972479.short) | Photometric stereo |
| **S5** | A. Laurentini, "The Visual Hull Concept for Silhouette-Based Image Understanding," *IEEE TPAMI* 16(2), 1994 — [doi:10.1109/34.273735](https://dl.acm.org/doi/10.1109/34.273735) | Visual hull |
| **S6** | R. Szeliski, "Rapid Octree Construction from Image Sequences," *CVGIP: Image Understanding* 58(1), 1993 — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1049966083710296) | Voxel carving |
| **S7** | K. N. Kutulakos, S. M. Seitz, "A Theory of Shape by Space Carving," *IJCV*, 2000 — [doi:10.1023/A:1008191222954](https://link.springer.com/article/10.1023/A:1008191222954), [PDF (Toronto)](https://www.cs.toronto.edu/~kyros/pubs/00.ijcv.carve.pdf), [PDF (CMU)](https://www.cs.cmu.edu/~seitz/papers/kutu-ijcv00.pdf) | Space carving |
| **S8** | MVTec HALCON `photometric_stereo` reference — [link](https://www.mvtec.com/doc/halcon/13/en/photometric_stereo.html) | ≥ 3 images, non-coplanar light directions |
| **S9** | A. W. Fitzgibbon, G. Cross, A. Zisserman, "Automatic 3D Model Construction for Turn-Table Sequences," SMILE 1998 — [doi:10.1007/3-540-49437-5_11](https://link.springer.com/chapter/10.1007/3-540-49437-5_11), [open copy](https://ora.ox.ac.uk/objects/uuid:f4e19b7a-4606-4f63-b532-6a0d0bf19845) | Turntable (rotating-object) reconstruction |
| **S10** | Meshroom / AliceVision — [alicevision.org](https://alicevision.org/), [Meshroom](https://alicevision.org/view/meshroom.html), [GitHub](https://github.com/alicevision/meshroom), [licence MPL2](https://github.com/alicevision/meshroom/blob/develop/COPYING.md) | Alternative reconstruction |
| **S11** | OpenCV `solvePnP` — [docs](https://docs.opencv.org/4.13.0/d5/d1f/calib3d_solvePnP.html) | Camera axis convention, pose checks |
| **S12** | OpenCV ChArUco calibration — [tutorial](https://docs.opencv.org/4.13.0/da/d13/tutorial_aruco_calibration.html), [detection](https://docs.opencv.org/4.13.0/df/d4a/tutorial_charuco_detection.html) | Scan-mode intrinsics, scanning mat |
| **S13** | D. Schnieders, K.-Y. K. Wong, "Camera and light calibration from reflections on a sphere," *CVIU*, 2013 — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1077314213001082), [PDF](https://i.cs.hku.hk/~kykwong/publications/dschnieders_cviu2013.pdf) | Chrome-ball light calibration |
| **S14** | Yu, Chen, Da, "Geometric calibration for photometric stereo under near-field point light sources using spheres," *Optics & Laser Technology* 180, 2025 — [link](https://www.sciencedirect.com/science/article/pii/S0030399224010156) | Near-light correction (phase 11) |
| **S15** | D. B. Goldman, B. Curless, A. Hertzmann, S. M. Seitz, "Shape and Spatially-Varying BRDFs from Photometric Stereo," ICCV 2005 — [doi:10.1109/ICCV.2005.219](https://mlanthology.org/iccv/2005/goldman2005iccv-shape/) | Material on the mesh (phase 13) |
| **S16** | Blender manual: [PLY](https://docs.blender.org/manual/en/latest/files/import_export/ply.html), [OBJ](https://docs.blender.org/manual/en/latest/files/import_export/obj.html), [glTF 2.0](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html), [formats](https://docs.blender.org/manual/en/latest/files/import_export/index.html) | Mesh import check |
| **S17** | OpenMVS — [GitHub](https://github.com/cdcseacave/openMVS), [licence AGPL](https://github.com/cdcseacave/openMVS/blob/develop/COPYRIGHT.md) | Optional dense/mesh stage |
| **S18** | RealityScan (formerly RealityCapture) — [licence](https://www.realityscan.com/license), [2.0 rename](https://www.realityscan.com/news/realityscan-20-new-release-brings-powerful-new-features-to-a-rebranded-realitycapture), [CG Channel 2.0](https://www.cgchannel.com/2025/06/epic-games-to-rebrand-realitycapture-as-realityscan-2-0/), [CG Channel 2.2](https://www.cgchannel.com/2026/06/epic-games-releases-realityscan-2-2-with-amd-gpu-support/) | Optional reconstruction |
| **S19** | QuakeHold! museum putty — [SOS Products](https://www.sosproducts.com/quakehold-museum-putty-p/64810.htm), [Fire Supply Depot](https://www.firesupplydepot.com/quakehold-museum-putty-white-22111.html) | Heavier-object option |
| **S20** | Loctite Fun-Tak 2 oz — [Staples](https://www.staples.com/Loctite-Fun-Tak-2-oz-Mounting-Adhesive-Putty-1270884/product_1480018), [Amazon](https://www.amazon.com/Loctite-Fun-Tak-Mounting-2-Ounce-1270884-12/dp/B074R72PSH) | $3.49 object mount |

## Measurement devices and datasets

### Foundations, surveys and books

| ID | Source | Used for |
|---|---|---|
| **G1** | F. E. Nicodemus, J. C. Richmond, J. J. Hsia, I. W. Ginsberg, T. Limperis, "Geometrical Considerations and Nomenclature for Reflectance," *NBS Monograph* 160, 1977 — [doi:10.6028/NBS.MONO.160](https://doi.org/10.6028/NBS.MONO.160) · [archive.org](https://archive.org/details/geometricalconsi160nico) | BRDF definition, units, nomenclature (phases 00, 07) |
| **G2** | J. Dorsey, H. Rushmeier, F. Sillion, *Digital Modeling of Material Appearance*, Morgan Kaufmann, 2008, ISBN 978-0-12-221181-2 — [front matter PDF](https://booksite.elsevier.com/samplechapters/9780122211812/Sample_Chapters/01~Front_Matter.pdf) · [O'Reilly](https://www.oreilly.com/library/view/digital-modeling-of/9780122211812/) | Measurement chapter, device taxonomy (phase 00) |
| **G3** | D. Guarnera, G. C. Guarnera, A. Ghosh, C. Denk, M. Glencross, "BRDF Representation and Acquisition," *Computer Graphics Forum* 35(2):625–650, 2016 — [doi:10.1111/cgf.12867](https://doi.org/10.1111/cgf.12867) · [York](https://pure.york.ac.uk/portal/en/publications/brdf-representation-and-acquisition/) | Survey of acquisition devices, models (phase 08) |
| **G4** | M. Weinmann, R. Klein, "Advances in Geometry and Reflectance Acquisition (course notes)," *SIGGRAPH Asia 2015 Courses*, 2015 — [doi:10.1145/2818143.2818165](https://doi.org/10.1145/2818143.2818165) | Joint shape + reflectance capture (phases 11, 13) |
| **G5** | J. Filip, M. Haindl, "Bidirectional Texture Function Modeling: A State of the Art Survey," *IEEE TPAMI* 31(11), 2009 — [doi:10.1109/TPAMI.2008.246](https://doi.org/10.1109/TPAMI.2008.246) | BTF capture and representation (phase 09) |
| **G6** | Y. Zou, L. Zhang, J. Zhang, B. Li, X. Lv, "Developmental Trends in the Application and Measurement of the Bidirectional Reflection Distribution Function," *Sensors* 22(5):1739, 2022 — [doi:10.3390/s22051739](https://doi.org/10.3390/s22051739) · [HTML](https://mdpi.com/1424-8220/22/5/1739/htm) | Recent review of BRDF instruments (phase 00) |
| **G7** | G. Obein, "The measurement of appearance," *Proc. Int. School of Physics "Enrico Fermi"* 206:175–186, 2021 — [doi:10.3254/ENFI210025](https://doi.org/10.3254/ENFI210025) | Metrology view of appearance (phase 00) |

### Classic gonioreflectometers and image-based BRDF measurement

| ID | Source | Used for |
|---|---|---|
| **G8** | J. F. Murray-Coleman, A. M. Smith, "The Automated Measurement of BRDFs and their Application to Luminaire Modeling," *J. Illuminating Engineering Society* 19:87–99, 1990 — [doi:10.1080/00994480.1990.10747944](https://doi.org/10.1080/00994480.1990.10747944) | Early automated gonioreflectometer (phase 08) |
| **G9** | G. J. Ward, "Measuring and Modeling Anisotropic Reflection," *ACM SIGGRAPH Computer Graphics* 26(2):265–272, 1992 — [doi:10.1145/142920.134078](https://doi.org/10.1145/142920.134078) · [PDF](https://cseweb.ucsd.edu/~ravir/6998/papers/p265-ward.pdf) | Imaging gonioreflectometer, anisotropic fit (phase 09) |
| **G10** | D. R. White, P. Saunders, S. J. Bonsey, J. van de Ven, H. Edgar, "Reflectometer for measuring the bidirectional reflectance of rough surfaces," *Applied Optics* 37(16):3450–3454, 1998 — [doi:10.1364/AO.37.003450](https://doi.org/10.1364/AO.37.003450) | Four-axis rotating-arm gonio design (phases 03, 04) |
| **G11** | K. J. Dana, B. van Ginneken, S. K. Nayar, J. J. Koenderink, "Reflectance and Texture of Real-World Surfaces," *ACM TOG* 18(1):1–34, 1999 — [doi:10.1145/300776.300778](https://doi.org/10.1145/300776.300778) · [PDF](https://cave.cs.columbia.edu/old/publications/pdfs/Dana_TOG99.pdf) | CUReT robot-arm BTF capture/dataset (phases 09, 17) |
| **G12** | S. R. Marschner, S. H. Westin, E. P. F. Lafortune, K. E. Torrance, "Image-based bidirectional reflectance distribution function measurement," *Applied Optics* 39(16):2592–2600, 2000 — [doi:10.1364/AO.39.002592](https://doi.org/10.1364/AO.39.002592) | Camera-based BRDF from curved samples (phases 06, 07) |
| **G13** | J. Y. Han, K. Perlin, "Measuring Bidirectional Texture Reflectance with a Kaleidoscope," *ACM TOG* 22(3) (SIGGRAPH), 2003 — [doi:10.1145/882262.882341](https://doi.org/10.1145/882262.882341) | Mirror-based multi-view BTF alternative (phase 17) |
| **G14** | K. J. Dana, J. Wang, "Device for convenient measurement of spatially varying bidirectional reflectance," *JOSA A* 21(1):1–12, 2004 — [doi:10.1364/JOSAA.21.000001](https://doi.org/10.1364/JOSAA.21.000001) | Curved-mirror SVBRDF camera (phase 09) |
| **G15** | W. Matusik, H. Pfister, M. Brand, L. McMillan, "Efficient Isotropic BRDF Measurement," *Proc. 14th Eurographics Workshop on Rendering*, 241–247, 2003 — [cited in PBR 4ed](https://www.pbr-book.org/4ed/Reflection_Models/Further_Reading) | Sphere-sample MERL acquisition method (phase 17) |
| **G16** | A. Ngan, F. Durand, W. Matusik, "Experimental Analysis of BRDF Models," *Eurographics Symposium on Rendering*, 2005 — [EG DL](https://diglib.eg.org/items/b3a3223e-ad94-4366-8ae7-fce371c08d04) · [PDF](https://people.csail.mit.edu/wojciech/BRDFAnalysis/BRDFAnalysis.pdf) · [MERL TR2005-151](https://www.merl.com/publications/docs/TR2005-151.pdf) | Model-fit comparison, anisotropic cylinder rig (phases 07, 09) |
| **G17** | M. Ben-Ezra, J. Wang, B. Wilburn, X. Li, L. Ma, "An LED-Only BRDF Measurement Device," *CVPR*, 2008 — [doi:10.1109/CVPR.2008.4587766](https://doi.org/10.1109/CVPR.2008.4587766) · [mlanthology](https://mlanthology.org/cvpr/2008/benezra2008cvpr-led/) | LEDs as emitters/sensors, multispectral (phase 10) |
| **G18** | M. Kurt, L. Szirmay-Kalos, J. Křivánek, "An Anisotropic BRDF Model for Fitting and Monte Carlo Rendering," *ACM SIGGRAPH Computer Graphics* 44(1):1–15, 2010 — [doi:10.1145/1722991.1722996](https://doi.org/10.1145/1722991.1722996) | Anisotropic fit to measured data (phase 09) |
| **G19** | A. Sole, I. Farup, P. Nussbaum, S. Tominaga, "Evaluating an image-based bidirectional reflectance distribution function measurement setup," *Applied Optics* 57(8):1918–1928, 2018 — [doi:10.1364/AO.57.001918](https://doi.org/10.1364/AO.57.001918) | Validating camera BRDF vs commercial (phase 07) |
| **G20** | A. Sole, *Image-Based Bidirectional Reflectance Measurement of Non-Diffuse and Gonio-Chromatic Materials*, PhD thesis, NTNU, 2019 — [NTNU Colourlab theses](https://www.ntnu.edu/colourlab/phd-theses) | Image-based BRDF method details (phase 07) |

### National metrology institute instruments and references

| ID | Source | Used for |
|---|---|---|
| **G21** | P. Y. Barnes, E. A. Early, A. C. Parr, *NIST Measurement Services: Spectral Reflectance*, NIST Special Publication 250-48, 1998 — [PDF](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication250-48.pdf) · [GovInfo](https://www.govinfo.gov/app/details/GOVPUB-C13-7ab8bd6b271101964fdf6c44e8b0bf14) | STARR reference reflectometer, uncertainty (phase 07) |
| **G22** | J. E. Proctor, P. Y. Barnes, "NIST High Accuracy Reference Reflectometer-Spectrophotometer," *J. Res. NIST* 101(5):619, 1996 — [PDF](https://nvlpubs.nist.gov/nistpubs/jres/101/5/j5proc.pdf) · [archive.org](https://archive.org/details/jresv101n5p619) | STARR design, absolute BRDF (phase 07) |
| **G23** | H. Patrick, C. Cooksey, T. A. Germer, M. E. Nadal, C. Zarobila, "Bidirectional reflectance capabilities of the NIST Robotic Optical Scattering Instrument," *Applied Optics* 60(28):8774, 2021 — [doi:10.1364/AO.435117](https://doi.org/10.1364/AO.435117) · [NIST](https://www.nist.gov/publications/bidirectional-reflectance-capabilities-nist-robotic-optical-scattering-instrument-rosi) | Robot-arm reference gonio, STARR comparison (phase 08) |
| **G24** | C. Durell, D. Scharpf, G. McKee, M. L'Heureux, G. Georgiev, G. Obein, C. Cooksey, "Creation and Validation of Sintered PTFE BRDF Targets & Standards," *Proc. SPIE* 9639, paper 49, 2015 — [PDF](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=919590) | PTFE white reference BRDF (phase 07) |
| **G25** | A. Höpe, D. Hünerhoff, K.-O. Hauer, "Robot-based Gonioreflectometer," in *Industrial Robotics: Programming, Simulation and Applications* (ed. L. K. Huat), pp. 624–632, 2006 — [PDF](https://cdn.intechopen.com/pdfs/284/InTech-Robot_based_gonioreflectometer.pdf) | PTB robot sample holder concept (phase 08) |
| **G26** | A. Höpe, K.-O. Hauer, "Three-dimensional appearance characterization of diffuse standard reflection materials," *Metrologia* 47(3):295, 2010 — [doi:10.1088/0026-1394/47/3/021](https://doi.org/10.1088/0026-1394/47/3/021) | Non-Lambertian behaviour of white standards (phase 07) |
| **G27** | A. Höpe et al., "ARGon3: '3D appearance robot-based gonioreflectometer' at PTB," *Rev. Sci. Instrum.* 83(4):045102, 2012 — [AIP](https://pubs.aip.org/aip/rsi/article/83/4/045102/355039/ARGon3-3D-appearance-robot-based) | Camera-based spatially resolved gonio (phase 09) |
| **G28** | A. Höpe et al., "Multidimensional reflectometry for industry (xD-Reflect) an European research project," *Proc. SPIE* 9018:901804, 2014 — [doi:10.1117/12.2035981](https://doi.org/10.1117/12.2035981) · [project](https://www.xdreflect.eu/project-publications/) | Gonio colour, sparkle, gloss metrology (phase 10) |
| **G29** | E. Molloy, H. Patrick, K.-O. Hauer, D. Hünerhoff, T. Quast, "Comparison of bidirectional reflectance distribution function scales over the hemisphere," *Applied Optics* 65(18):6358–6365, 2026 — [doi:10.1364/AO.603369](https://doi.org/10.1364/AO.603369) | Inter-lab BRDF agreement limits (phase 07) |
| **G30** | R. Le Breton, G. Ged, G. Obein, "Out of plane BRDF measurement at LNE-Cnam using 'ConDOR' our primary goniospectrophotometer," *Proc. 28th CIE Session*, 1401–1407, 2015 — [Obein publications](https://inm.cnam.fr/gael-obein-71373.kjsp) | High-resolution out-of-plane gonio (phase 08) |
| **G31** | D. Saha, L. Gevaux, J. R. Frisvad, G. Obein, "Bidirectional reflectance measurements over a micrometric surface area using a goniospectrophotometer," *Rev. Sci. Instrum.* 95(5):055114, 2024 — [doi:10.1063/5.0193490](https://doi.org/10.1063/5.0193490) · [DTU](https://orbit.dtu.dk/en/publications/bidirectional-reflectance-measurements-over-a-micrometric-surface) | Small-spot BRDF, spatial resolution (phase 17) |
| **G32** | RGL-EPFL, customized PAB pgII gonio-photometer (instrument page) — [rgl.epfl.ch/pages/lab/pgII](https://rgl.epfl.ch/pages/lab/pgII) | Reference instrument behind RGL data (phase 17) |

### Lineage of the main design reference (NTNU / LNE-CNAM)

| ID | Source | Used for |
|---|---|---|
| **G33** | M. Ansari-Asl, M. Barbieri, G. Obein, J. Y. Hardeberg, "Advancing Material Appearance Measurement: A Cost-effective Multispectral Imaging System for Capturing SVBRDF and BTF," *London Imaging Meeting* 4:104–108, 2023 — [doi:10.2352/lim.2023.4.1.25](https://doi.org/10.2352/lim.2023.4.1.25) · [Zenodo](https://zenodo.org/records/10404932) | Precursor of R1 rig layout (phases 00, 05) |
| **G34** | M. Ansari-Asl, J.-B. Thomas, J. Y. Hardeberg, "Camera Response Function Assessment in Multispectral HDR Imaging," *IS&T Electronic Imaging (Color Imaging XXVII)*, COLOR-141, 2022 — [doi:10.2352/EI.2022.34.15.COLOR-141](https://doi.org/10.2352/EI.2022.34.15.COLOR-141) | Measured vs Debevec CRF for HDR (phase 07) |
| **G35** | M. Ansari-Asl, *Development of a Multispectral Camera-Based Device for Goniometric Acquisition of Spatially Varying Reflectance Properties*, PhD thesis, NTNU, 2026 — [NTNU Colourlab theses](https://www.ntnu.edu/colourlab/phd-theses) | Full design record of R1 (phase 00) |
| **G36** | A. Sole, D. Gigilashvili, H. Midtfjord, D. Guarnera, G. C. Guarnera, J.-B. Thomas, J. Y. Hardeberg, "On the Acquisition and Reproduction of Material Appearance," *CCIW 2019*, LNCS 11418:26–38, 2019 — [doi:10.1007/978-3-030-13940-7_3](https://doi.org/10.1007/978-3-030-13940-7_3) | NTNU appearance-capture context (phase 00) |
| **G37** | S. Chitnis, A. Sole, S. Chandran, "Spectral Bidirectional Reflectance Distribution Function Simplification," *J. Imaging* 11(1):18, 2025 — [doi:10.3390/jimaging11010018](https://doi.org/10.3390/jimaging11010018) | Fewer spectral bands per BRDF (phase 10) |

### Low-cost, robotic and portable devices

| ID | Source | Used for |
|---|---|---|
| **G38** | J. Filip, R. Vávra, M. Krupička, "Rapid Material Appearance Acquisition Using Consumer Hardware," *Sensors* 14(10):19785–19805, 2014 — [doi:10.3390/s141019785](https://doi.org/10.3390/s141019785) | Toy-gantry low-cost BTF prior art (phases 00, 03) |
| **G39** | R. A. Lyngby, J. B. Matthiassen, J. R. Frisvad, A. B. Dahl, H. Aanæs, "Using a Robotic Arm for Measuring BRDFs," *SCIA 2019*, LNCS 11482:184–196, 2019 — [doi:10.1007/978-3-030-20205-7_16](https://doi.org/10.1007/978-3-030-20205-7_16) | Hand-eye calibration for BRDF rigs (phase 11) |
| **G40** | J. Riviere, P. Peers, A. Ghosh, "Mobile Surface Reflectometry," *Computer Graphics Forum* 35:191–202, 2016 — [doi:10.1111/cgf.12719](https://doi.org/10.1111/cgf.12719) | Phone-flash SVBRDF capture baseline (phase 09) |

### Spherical, polarized and linear-light illumination; SVBRDF capture

| ID | Source | Used for |
|---|---|---|
| **G41** | A. Ghosh, T. Chen, P. Peers, C. A. Wilson, P. Debevec, "Estimating Specular Roughness and Anisotropy from Second Order Spherical Gradient Illumination," *Eurographics Symposium on Rendering*, 2009 — [PDF](https://www.cs.wm.edu/~ppeers/publications/Ghosh2009ESR/Ghosh_EGSR2009.pdf) | Polarized diffuse/specular separation (phase 10) |
| **G42** | A. Ghosh, T. Chen, P. Peers, C. A. Wilson, P. Debevec, "Circularly Polarized Spherical Illumination Reflectometry," *ACM SIGGRAPH Asia*, 2010 — [project](https://vgl.ict.usc.edu/Research/CPSIR/) · [PDF](https://vgl.ict.usc.edu/Research/CPSIR/CPSIR_SIGGRAPH_Asia2010.pdf) | Polarization-based index/specular estimation (phase 10) |
| **G43** | G. Chen, Y. Dong, P. Peers, J. Zhang, X. Tong, "Reflectance Scanning: Estimating Shading Frame and BRDF with Generalized Linear Light Sources," *ACM TOG* 33(4), 2014 — [doi:10.1145/2601097.2601180](https://doi.org/10.1145/2601097.2601180) | Linear-light SVBRDF scanning (phase 09) |
| **G44** | M. Aittala, T. Weyrich, J. Lehtinen, "Practical SVBRDF Capture in the Frequency Domain," *ACM TOG* 32(4) (SIGGRAPH), 2013 — [doi:10.1145/2461912.2461978](https://doi.org/10.1145/2461912.2461978) | Screen-pattern SVBRDF capture (phase 09) |
| **G45** | S.-H. Baek, T. Zeltner, H. Ku, I. Hwang, X. Tong, W. Jakob, M. H. Kim, "Image-based Acquisition and Modeling of Polarimetric Reflectance," *ACM TOG* 39(4):139, 2020 — [doi:10.1145/3386569.3392387](https://doi.org/10.1145/3386569.3392387) | Polarimetric BRDF capture (phase 10) |

### Sampling strategies

| ID | Source | Used for |
|---|---|---|
| **G46** | J. B. Nielsen, H. W. Jensen, R. Ramamoorthi, "On Optimal, Minimal BRDF Sampling for Reflectance Acquisition," *ACM TOG* 34(6):186, 2015 — [cited in PBR 4ed](https://www.pbr-book.org/4ed/Reflection_Models/Further_Reading) | Few-sample BRDF from MERL basis (phase 17) |
| **G47** | R. Vávra, J. Filip, "Minimal Sampling for Effective Acquisition of Anisotropic BRDFs," *Computer Graphics Forum* 35(7):299–309, 2016 — [cited in PBR 4ed](https://www.pbr-book.org/4ed/Reflection_Models/Further_Reading) | Anisotropic sparse sampling (phase 17) |
| **G48** | R. Vávra, J. Filip, "Adaptive slices for acquisition of anisotropic BRDF," *Computational Visual Media* 4(1):55–69, 2018 — [doi:10.1007/s41095-017-0099-z](https://doi.org/10.1007/s41095-017-0099-z) | Adaptive 1D-slice sampling (phase 17) |

### BTF capture setups (Bonn)

| ID | Source | Used for |
|---|---|---|
| **G49** | C. Schwartz, R. Sarlette, M. Weinmann, M. Rump, R. Klein, "Design and Implementation of Practical Bidirectional Texture Function Measurement Devices Focusing on the Developments at the University of Bonn," *Sensors* 14(5):7753–7819, 2014 — [doi:10.3390/s140507753](https://doi.org/10.3390/s140507753) | BTF device requirements, HDR, calibration (phase 09) |
| **G50** | C. Schwartz, R. Sarlette, M. Weinmann, R. Klein, "DOME II: A Parallelized BTF Acquisition System," *Eurographics Workshop on Material Appearance Modeling*, 25–31, 2013 — [doi:10.2312/MAM.MAM2013.025-031](https://doi.org/10.2312/MAM.MAM2013.025-031) | Camera-array dome comparison (phase 09) |

### Datasets and data formats

| ID | Source | Used for |
|---|---|---|
| **G51** | W. Matusik, H. Pfister, M. Brand, L. McMillan, "BRDF Database – Bidirectional Reflectance Distribution Function" (MERL 100 materials, CC-BY-SA-4.0), Zenodo, 2023 — [doi:10.5281/zenodo.8101681](https://doi.org/10.5281/zenodo.8101681) | Licensed MERL copy for comparison (phase 17) |
| **G52** | D. Lanevski et al., "Machine-readable universal data format for bidirectional reflectance distribution function and BiRDview—An open-source web-based application for viewing and comparing bidirectional reflectance data," *Color Research & Application*, 2022 — [doi:10.1002/col.22790](https://doi.org/10.1002/col.22790) | BRDF export format, viewer (phase 14) |

## Reflectance models and material formats

### Rendering theory and textbooks

| ID | Source | Used for |
|---|---|---|
| **T1** | J. T. Kajiya, "The Rendering Equation," *Proc. SIGGRAPH '86, Computer Graphics* 20(4):143–150, 1986 — [doi:10.1145/15922.15902](https://doi.org/10.1145/15922.15902) · [PDF](https://www.cs.cmu.edu/afs/cs/academic/class/15462-s13/www/lec_slides/86kajiyaRenderingEquation.pdf) | Reflection/rendering equation background (phases 00, 07) |
| **T2** | M. Pharr, W. Jakob, G. Humphreys, *Physically Based Rendering: From Theory to Implementation*, 4th ed., MIT Press, 2023 — [pbr-book.org/4ed](https://www.pbr-book.org/4ed/Reflection_Models/Further_Reading) · [MIT Press](https://mitpress.mit.edu/9780262048026/physically-based-rendering/) | BRDF, microfacet, sampling reference (phases 07, 08) |
| **T3** | E. Veach, "Robust Monte Carlo Methods for Light Transport Simulation," PhD thesis, Stanford University, 1997 — [PDF](https://graphics.stanford.edu/papers/veach_thesis/thesis-bw.pdf) · [dblp](https://dblp.dagstuhl.de/rec/phd/us/Veach97.html) | Reciprocity, importance sampling theory (phases 08, 17) |
| **T4** | T. Weyrich, J. Lawrence, H. P. A. Lensch, S. Rusinkiewicz, T. Zickler, "Principles of Appearance Acquisition and Representation," *Foundations and Trends in Computer Graphics and Vision* 4(2):75–191, 2009 — [doi:10.1561/0600000022](https://doi.org/10.1561/0600000022) · [PDF](https://gfx.cs.princeton.edu/pubs/Weyrich_2009_POA/0600000022.pdf) | Measurement-to-representation overview (phases 00, 08, 09) |
| **T5** | R. Montes, C. Ureña, "An Overview of BRDF Models," Tech. Rep. LSI-2012-001, Univ. of Granada, 2012 — [PDF](https://digibug.ugr.es/bitstream/handle/10481/19751/rmontes_LSI-2012-001TR.pdf) | Model catalogue for choosing fits (phases 07, 08) |
| **T6** | M. Nimier-David, D. Vicini, T. Zeltner, W. Jakob, "Mitsuba 2: A Retargetable Forward and Inverse Renderer," *ACM TOG* 38(6):203, 2019 — [doi:10.1145/3355089.3356498](https://doi.org/10.1145/3355089.3356498) · [project](https://tizianzeltner.com/projects/NimierDavidVicini2019Mitsuba2/) | Differentiable reference renderer for fit checks (phase 17) |
| **T7** | Mitsuba 3 documentation, "BSDFs" (roughconductor, measured, …) — [mitsuba.readthedocs.io](https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_bsdfs.html) | Render fitted vs RGL measured BSDF (phase 17) |

### Classic analytic reflectance models

| ID | Source | Used for |
|---|---|---|
| **T8** | B. T. Phong, "Illumination for Computer Generated Pictures," *Communications of the ACM* 18(6):311–317, 1975 — [doi:10.1145/360825.360839](https://doi.org/10.1145/360825.360839) | Baseline lobe model for comparisons (phase 07) |
| **T9** | J. F. Blinn, "Models of Light Reflection for Computer Synthesized Pictures," *Proc. SIGGRAPH '77*, 192–198, 1977 — [doi:10.1145/563858.563893](https://doi.org/10.1145/563858.563893) | Half-vector lobe, legacy export mapping (phase 07) |
| **T10** | K. E. Torrance, E. M. Sparrow, "Theory for Off-Specular Reflection from Roughened Surfaces," *JOSA* 57(9):1105–1114, 1967 — [doi:10.1364/JOSA.57.001105](https://doi.org/10.1364/JOSA.57.001105) · [ADS](https://ui.adsabs.harvard.edu/abs/1967JOSA...57.1105T/abstract) | Microfacet theory, off-specular peak (phase 08) |
| **T11** | T. S. Trowbridge, K. P. Reitz, "Average Irregularity Representation of a Rough Surface for Ray Reflection," *JOSA* 65(5):531–536, 1975 — [doi:10.1364/JOSA.65.000531](https://doi.org/10.1364/JOSA.65.000531) · [ADS](https://ui.adsabs.harvard.edu/abs/1975JOSA...65..531T/abstract) | Origin of GGX/TR distribution (phase 07) |
| **T12** | B. G. Smith, "Geometrical Shadowing of a Random Rough Surface," *IEEE Trans. Antennas and Propagation* 15(5):668–671, 1967 — [ADS](https://ui.adsabs.harvard.edu/abs/1967ITAP...15..668S/abstract) · [NTRS](https://ntrs.nasa.gov/citations/19670062103) | Smith masking-shadowing term (phases 07, 08) |
| **T13** | M. Oren, S. K. Nayar, "Generalization of Lambert's Reflectance Model," *Proc. SIGGRAPH '94*, 239–246, 1994 — [doi:10.1145/192161.192213](https://doi.org/10.1145/192161.192213) | Rough-diffuse alternative to Lambert (phases 07, 08) |
| **T14** | E. P. F. Lafortune, S.-C. Foo, K. E. Torrance, D. P. Greenberg, "Non-Linear Approximation of Reflectance Functions," *Proc. SIGGRAPH '97*, 117–126, 1997 — [doi:10.1145/258734.258801](https://doi.org/10.1145/258734.258801) | Multi-lobe fit, retroreflection (phase 08) |
| **T15** | M. Ashikhmin, P. Shirley, "An Anisotropic Phong BRDF Model," *Journal of Graphics Tools* 5(2):25–32, 2000 — [doi:10.1080/10867651.2000.10487522](https://doi.org/10.1080/10867651.2000.10487522) | Anisotropic fit alternative (phase 09) |
| **T16** | S. Rusinkiewicz, "A New Change of Variables for Efficient BRDF Representation," *Rendering Techniques '98* (EGWR), 11–22, 1998 — [doi:10.1007/978-3-7091-6453-2_2](https://doi.org/10.1007/978-3-7091-6453-2_2) · [project](https://gfx.cs.princeton.edu/gfx/pubs/Rusinkiewicz_1998_ANC/index.php) | Half/difference angle data layout (phases 08, 17) |

### Microfacet theory and sampling (modern)

| ID | Source | Used for |
|---|---|---|
| **T17** | E. Heitz, "Understanding the Masking-Shadowing Function in Microfacet-Based BRDFs," *JCGT* 3(2):48–107, 2014 — [PDF](https://jcgt.org/published/0003/02/03/paper.pdf) · [HAL](https://hal.science/hal-01024289/) | Correct Smith G for GGX fit (phases 07, 08) |
| **T18** | E. Heitz, E. d'Eon, "Importance Sampling Microfacet-Based BSDFs using the Distribution of Visible Normals," *Computer Graphics Forum* 33(4):103–112, 2014 — [doi:10.1111/cgf.12417](https://doi.org/10.1111/cgf.12417) | Sampling fitted GGX in renders (phases 14, 17) |
| **T19** | E. Heitz, "Sampling the GGX Distribution of Visible Normals," *JCGT* 7(4):1–13, 2018 — [PDF](https://jcgt.org/published/0007/04/01/paper.pdf) | Simple VNDF sampler code (phase 14) |
| **T20** | J. Dupuy, A. Benyoub, "Sampling Visible GGX Normals with Spherical Caps," *Computer Graphics Forum* 42(8), 2023 — [doi:10.1111/cgf.14867](https://doi.org/10.1111/cgf.14867) | Faster VNDF sampling (phase 14) |
| **T21** | E. Heitz, J. Hanika, E. d'Eon, C. Dachsbacher, "Multiple-Scattering Microfacet BSDFs with the Smith Model," *ACM TOG* 35(4):58, 2016 — [doi:10.1145/2897824.2925943](https://doi.org/10.1145/2897824.2925943) | Energy loss at high roughness (phase 08) |
| **T22** | E. Turquin, "Practical Multiple Scattering Compensation for Microfacet Models," Weta Digital tech. report, 2019 — [PDF](https://blog.selfshadow.com/publications/turquin/ms_comp_final.pdf) | Energy compensation when fitting rough metals (phase 07) |
| **T23** | M. M. Bagher, C. Soler, N. Holzschuch, "Accurate Fitting of Measured Reflectances Using a Shifted Gamma Micro-facet Distribution," *Computer Graphics Forum* 31(4), 2012 — [HAL](https://inria.hal.science/hal-00702304) | Long-tail NDF fitting option (phase 17) |
| **T24** | M. Ribardière, B. Bringier, D. Meneveaux, L. Simonot, "STD: Student's t-Distribution of Slopes for Microfacet Based BSDFs," *Computer Graphics Forum* 36(2), 2017 — [doi:10.1111/cgf.13137](https://doi.org/10.1111/cgf.13137) | Generalised GGX tail fitting (phase 17) |

### Fitting measured data and evaluating fits

| ID | Source | Used for |
|---|---|---|
| **T25** | J. Löw, J. Kronander, A. Ynnerman, J. Unger, "BRDF Models for Accurate and Efficient Rendering of Glossy Surfaces," *ACM TOG* 31(1):9, 2012 — [doi:10.1145/2077341.2077350](https://doi.org/10.1145/2077341.2077350) · [PDF](https://liu.diva-portal.org/smash/get/diva2:683489/FULLTEXT01.pdf) | Fit error metric, glossy model choice (phases 07, 08) |
| **T26** | J. Dupuy, E. Heitz, J.-C. Iehl, P. Poulin, V. Ostromoukhov, "Extracting Microfacet-based BRDF Parameters from Arbitrary Materials with Power Iterations," *Computer Graphics Forum* 34(4):21–30, 2015 — [doi:10.1111/cgf.12675](https://doi.org/10.1111/cgf.12675) · [HAL](https://inria.hal.science/hal-01168516) | Robust NDF extraction for GGX fit (phases 08, 09) |
| **T27** | G. Lavoué, N. Bonneel, J.-P. Farrugia, C. Soler, "Perceptual Quality of BRDF Approximations: Dataset and Metrics," *Computer Graphics Forum* 40(2), 2021 — [doi:10.1111/cgf.142636](https://doi.org/10.1111/cgf.142636) · [PDF](https://perso.liris.cnrs.fr/nbonneel/BVQM_CGF.pdf) | Perceptual fit-quality metric (phases 07, 17) |
| **T28** | B. Kavoosighafi et al., "Perceived Quality of BRDF Models," *Computer Graphics Forum*, 2025 — [doi:10.1111/cgf.70162](https://doi.org/10.1111/cgf.70162) | Which model looks best when fitted (phase 17) |
| **T29** | A. Sztrajman, G. Rainer, T. Ritschel, T. Weyrich, "Neural BRDF Representation and Importance Sampling," *Computer Graphics Forum* 40, 2021 — [doi:10.1111/cgf.14335](https://doi.org/10.1111/cgf.14335) · [project](https://reality.cs.ucl.ac.uk/projects/reflectance-remapping/sztrajman2021neural.html) | Neural fit stretch; remap to analytic (phase 17) |

### Fresnel and optical constants

| ID | Source | Used for |
|---|---|---|
| **T30** | M. Born, E. Wolf, *Principles of Optics*, 7th ed., Cambridge University Press, 1999 (60th anniv. ed. 2019) — [Cambridge](https://www.cambridge.org/9781108477437) | Exact Fresnel equations, polarisation (phases 07, 10) |
| **T31** | O. Gulbrandsen, "Artist Friendly Metallic Fresnel," *JCGT* 3(4):64–72, 2014 — [PDF](https://jcgt.org/published/0003/04/03/paper.pdf) | Map n,k to reflectivity/edge tint (phase 07) |
| **T32** | M. N. Polyanskiy, "Refractiveindex.info Database of Optical Constants," *Scientific Data* 11:94, 2024 — [doi:10.1038/s41597-023-02898-2](https://doi.org/10.1038/s41597-023-02898-2) · [GitHub](https://github.com/polyanskiy/refractiveindex.info-database) | Metal F0 sanity check vs mirror, chrome (phases 06, 07) |

### Production shading models (course notes)

| ID | Source | Used for |
|---|---|---|
| **T33** | B. Burley, "Physically-Based Shading at Disney," SIGGRAPH 2012 course *Practical Physically Based Shading in Film and Game Production* — [PDF](https://static1.squarespace.com/static/58586fa5ebbd1a60e7d76d3e/t/593a3afa46c3c4a376d779f6/1496988449807/s2012_pbs_disney_brdf_notes_v2.pdf) · [course](https://blog.selfshadow.com/publications/s2012-shading-course/) | Principled parameters, MERL-based design (phases 07, 17) |
| **T34** | B. Burley, "Extending the Disney BRDF to a BSDF with Integrated Subsurface Scattering," SIGGRAPH 2015 course notes — [PDF](https://blog.selfshadow.com/publications/s2015-shading-course/burley/s2015_pbs_disney_bsdf_notes.pdf) | Anisotropic alpha mapping, sheen (phase 09) |
| **T35** | B. Karis, "Real Shading in Unreal Engine 4," SIGGRAPH 2013 course *Physically Based Shading in Theory and Practice* — [PDF](https://cdn2.unrealengine.com/Resources/files/2013SiggraphPresentationsNotes-26915738.pdf) · [slides](https://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_slides.pdf) | UE GGX/Smith/Schlick, α = roughness² (phase 07) |
| **T36** | S. Lagarde, C. de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0," SIGGRAPH 2014 course notes — [PDF](https://seblagarde.wordpress.com/wp-content/uploads/2015/07/course_notes_moving_frostbite_to_pbr_v3.pdf) · [post](https://seblagarde.wordpress.com/2015/07/14/siggraph-2014-moving-frostbite-to-physically-based-rendering/) | Validation against references, photometric units (phase 07) |
| **T37** | C. Kulla, A. Conty, "Revisiting Physically Based Shading at Imageworks," SIGGRAPH 2017 course — [slides](https://blog.selfshadow.com/publications/s2017-shading-course/imageworks/s2017_pbs_imageworks_slides_v2.pdf) · [sheen supplement](https://blog.selfshadow.com/publications/s2017-shading-course/imageworks/s2017_pbs_imageworks_sheen.pdf) | Energy compensation, Charlie sheen (phases 07, 09) |
| **T38** | N. Hoffman, "Physics and Math of Shading," SIGGRAPH 2015 course *Physically Based Shading in Theory and Practice* — [slides](https://blog.selfshadow.com/publications/s2015-shading-course/hoffman/s2015_pbs_physics_math_slides.pdf) · [course](https://blog.selfshadow.com/publications/s2015-shading-course/) | Plain-language theory for docs (phases 00, 07) |
| **T39** | R. Guy, M. Agopian, "Physically Based Rendering in Filament," Google — [docs](https://google.github.io/filament/Filament.md.html) | Readable real-time BRDF derivations (phases 07, 14) |

### Material exchange formats and engine docs

| ID | Source | Used for |
|---|---|---|
| **T40** | Khronos Group, *glTF 2.0 Specification* v2.0.1, §3.9.2 Metallic-Roughness Material and Appendix B BRDF Implementation — [spec](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#metallic-roughness-material) | Core export target and BRDF (phases 07, 13) |
| **T41** | Khronos, KHR_materials_anisotropy — [README](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_materials_anisotropy/README.md) | Export fitted anisotropy (phase 09) |
| **T42** | Khronos, KHR_materials_sheen, KHR_materials_clearcoat — [sheen](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_materials_sheen/README.md) · [clearcoat](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_materials_clearcoat/README.md) | Fabric and coated-sample export (phase 09) |
| **T43** | Khronos, KHR_materials_specular, KHR_materials_ior — [specular](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_materials_specular/README.md) · [ior](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_materials_ior/README.md) | Export measured dielectric F0 (phase 07) |
| **T44** | Khronos, KHR_texture_transform — [README](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_texture_transform/README.md) | SVBRDF texture tiling on models (phases 09, 13) |
| **T45** | Khronos, glTF Sample Viewer — [GitHub](https://github.com/KhronosGroup/glTF-Sample-Viewer) | Reference check of exported .glb (phases 07, 13) |
| **T46** | Epic Games, "Physically Based Materials in Unreal Engine" — [docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/physically-based-materials-in-unreal-engine); "Importing glTF Files Into Unreal Engine" — [docs](https://dev.epicgames.com/documentation/unreal-engine/importing-gltf-files-into-unreal-engine) | Unreal export mapping (phases 07, 13) |
| **T47** | Unity, HDRP "Lit Shader" — [docs](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@14.0/manual/Lit-Shader.html); Unity glTFast — [docs](https://docs.unity3d.com/Packages/com.unity.cloud.gltfast@6.9/manual/index.html) | Unity export mapping (phases 07, 13) |
| **T48** | Blender Manual, "Principled BSDF" — [docs](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html) | Check exports in Blender (phases 07, 13) |
| **T49** | I. Georgiev, J. Portsmouth, Z. Andersson, A. Herubel, A. King, S. Ogaki, F. Servant, *Autodesk Standard Surface* v1.0.1 — [spec](https://autodesk.github.io/standard-surface/) · [GitHub](https://github.com/Autodesk/standard-surface) | DCC/film material mapping (phase 07) |
| **T50** | Z. Andersson, P. Edmondson, J. Guertault, A. Herubel, P. Kutz, A. Machizaud, J. Portsmouth, F. Servant, J. Stone, "OpenPBR Surface: An Open Shading Model for Physically Based Materials," *DigiPro 2025* — [doi:10.1145/3744199.3744632](https://doi.org/10.1145/3744199.3744632) · [spec v1.1.1](https://academysoftwarefoundation.github.io/OpenPBR/) | Future-proof export, F82-tint metals (phases 07, 16) |
| **T51** | ASWF, MaterialX Specification and Physically Based Shading Nodes — [GitHub](https://github.com/AcademySoftwareFoundation/MaterialX/blob/main/documents/Specification/MaterialX.PBRSpec.md) · [v1.38 PDF](https://materialx.org/assets/MaterialX.v1.38.PBRSpec.pdf) | Renderer-neutral material file (phases 13, 16) |

### Spectral rendering

| ID | Source | Used for |
|---|---|---|
| **T52** | B. Smits, "An RGB-to-Spectrum Conversion for Reflectances," *Journal of Graphics Tools* 4(4):11–22, 1999 — [doi:10.1080/10867651.1999.10487511](https://doi.org/10.1080/10867651.1999.10487511) | Baseline RGB↔spectrum for 8 bands (phase 10) |
| **T53** | W. Jakob, J. Hanika, "A Low-Dimensional Function Space for Efficient Spectral Upsampling," *Computer Graphics Forum* 38(2):147–155, 2019 — [doi:10.1111/cgf.13626](https://doi.org/10.1111/cgf.13626) · [RGL](https://rgl.epfl.ch/publications/Jakob2019Spectral) | Smooth spectra from fitted RGB albedo (phase 10) |
| **T54** | C. Peters, S. Merzbach, J. Hanika, C. Dachsbacher, "Using Moments to Represent Bounded Signals for Spectral Rendering," *ACM TOG* 38(4):136, 2019 — [doi:10.1145/3306346.3322964](https://doi.org/10.1145/3306346.3322964) | Compact storage of 8-band reflectance (phase 10) |
| **T55** | A. Wilkie, S. Nawaz, M. Droske, A. Weidlich, J. Hanika, "Hero Wavelength Spectral Sampling," *Computer Graphics Forum* 33(4):123–131, 2014 — [doi:10.1111/cgf.12419](https://doi.org/10.1111/cgf.12419) | Spectral preview render of measured bands (phases 10, 14) |
| **T56** | G. Taubin, "A Signal Processing Approach to Fair Surface Design," *SIGGRAPH* 1995 (bibliographic; not fetched) | λ/μ mesh smoothing without shrinkage: scanned visual hull → mesh (`render/mesh.py`) |
| **T57** | B. Karis, "Physically Based Shading on Mobile," Unreal Engine blog, 2014 (bibliographic; not fetched) | Analytic environment-BRDF fit for the viewer's approximate studio light (`render/raster.py`, `render-gl.js`) |
| **T58** | K. Narkowicz, "ACES Filmic Tone Mapping Curve," blog, 2016 (bibliographic; not fetched) | Tone curve shared by the software and WebGL renderers |

## Calibration, HDR, photometric stereo and 3D scanning

### Geometric camera calibration

| ID | Source | Used for |
|---|---|---|
| **V1** | Z. Zhang, "A Flexible New Technique for Camera Calibration," *IEEE TPAMI* 22(11):1330–1334, 2000 — [doi:10.1109/34.888718](https://doi.org/10.1109/34.888718) | Planar-target intrinsics (phase 06) |
| **V2** | R. Y. Tsai, "A Versatile Camera Calibration Technique for High-Accuracy 3D Machine Vision Metrology Using Off-the-Shelf TV Cameras and Lenses," *IEEE J. Robotics and Automation* 3(4):323–344, 1987 — [doi:10.1109/JRA.1987.1087109](https://doi.org/10.1109/JRA.1987.1087109) | Classic calibration background (phase 06) |
| **V3** | J. Heikkilä, O. Silvén, "A Four-step Camera Calibration Procedure with Implicit Image Correction," *Proc. CVPR* 1997, pp. 1106–1112 — [doi:10.1109/CVPR.1997.609468](https://doi.org/10.1109/CVPR.1997.609468) | Distortion model and correction (phase 06) |
| **V4** | D. C. Brown, "Close-Range Camera Calibration," *Photogrammetric Engineering* 37(8):855–866, 1971 — [Semantic Scholar](https://www.semanticscholar.org/paper/Close-Range-Camera-Calibration-Brown/1150007b62a3c7dac99c2c8f85c63bfab74891af) | Radial/tangential lens distortion (phase 06) |
| **V5** | J.-Y. Bouguet, "Camera Calibration Toolbox for Matlab," Caltech DATA, 2022 release — [doi:10.22002/D1.20164](https://doi.org/10.22002/D1.20164) · [record](https://data.caltech.edu/records/jx9cx-fdh55) | Reference calibration workflow (phase 06) |
| **V6** | T. Schöps, V. Larsson, M. Pollefeys, T. Sattler, "Why Having 10,000 Parameters in Your Camera Model Is Better Than Twelve," *Proc. CVPR* 2020 — [CVF](https://openaccess.thecvf.com/content_CVPR_2020/html/Schops_Why_Having_10000_Parameters_in_Your_Camera_Model_Is_Better_CVPR_2020_paper.html) · [PDF](https://arxiv.org/pdf/1912.02908) | Calibration accuracy limits (phase 17) |
| **V7** | S. Garrido-Jurado, R. Muñoz-Salinas, F. J. Madrid-Cuevas, M. J. Marín-Jiménez, "Automatic Generation and Detection of Highly Reliable Fiducial Markers under Occlusion," *Pattern Recognition* 47(6):2280–2292, 2014 — [doi:10.1016/j.patcog.2014.01.005](https://doi.org/10.1016/j.patcog.2014.01.005) | ArUco markers on ChArUco board (phases 06, 11) |
| **V8** | R. Hartley, A. Zisserman, *Multiple View Geometry in Computer Vision*, 2nd ed., Cambridge University Press, 2004 — [doi:10.1017/CBO9780511811685](https://doi.org/10.1017/CBO9780511811685) | Projection, triangulation, bundle adjustment (phases 06, 11) |
| **V9** | R. Szeliski, *Computer Vision: Algorithms and Applications*, 2nd ed., Springer (Texts in Computer Science), 2022 — [doi:10.1007/978-3-030-34372-9](https://doi.org/10.1007/978-3-030-34372-9) · [free PDF](https://szeliski.org/Book/download.php) | General CV reference (phases 06, 07, 08, 09, 10, 11, 12, 13) |

### Hand-eye and robot-world calibration (AX=XB, AX=YB)

| ID | Source | Used for |
|---|---|---|
| **V10** | R. Y. Tsai, R. K. Lenz, "A New Technique for Fully Autonomous and Efficient 3D Robotics Hand/Eye Calibration," *IEEE Trans. Robotics and Automation* 5(3):345–358, 1989 — [doi:10.1109/70.34770](https://doi.org/10.1109/70.34770) | Hand-eye AX=XB baseline (phase 11) |
| **V11** | F. C. Park, B. J. Martin, "Robot Sensor Calibration: Solving AX=XB on the Euclidean Group," *IEEE Trans. Robotics and Automation* 10(5):717–721, 1994 — [doi:10.1109/70.326576](https://doi.org/10.1109/70.326576) | Lie-group hand-eye solver (phase 11) |
| **V12** | K. Daniilidis, "Hand-Eye Calibration Using Dual Quaternions," *Int. J. Robotics Research* 18(3):286–298, 1999 — [doi:10.1177/02783649922066213](https://doi.org/10.1177/02783649922066213) | Simultaneous rotation/translation hand-eye (phase 11) |
| **V13** | H. Zhuang, Z. S. Roth, R. Sudhakar, "Simultaneous Robot/World and Tool/Flange Calibration by Solving Homogeneous Transformation Equations of the Form AX=YB," *IEEE Trans. Robotics and Automation* 10(4):549–554, 1994 — [doi:10.1109/70.313105](https://doi.org/10.1109/70.313105) | AX=YB formulation (phase 11) |
| **V14** | F. Dornaika, R. Horaud, "Simultaneous Robot-World and Hand-Eye Calibration," *IEEE Trans. Robotics and Automation* 14(4):617–622, 1998 — [doi:10.1109/70.704233](https://doi.org/10.1109/70.704233) | AX=YB nonlinear solution (phase 11) |
| **V15** | M. Shah, "Solving the Robot-World/Hand-Eye Calibration Problem Using the Kronecker Product," *J. Mechanisms and Robotics* 5(3):031007, 2013 — [doi:10.1115/1.4024473](https://doi.org/10.1115/1.4024473) · [NIST](https://www.nist.gov/publications/solving-robot-worldhand-eye-calibration-problem-using-kronecker-product) | Closed-form AX=YB (OpenCV SHAH) (phase 11) |
| **V16** | A. Tabb, K. M. Ahmad Yousef, "Solving the Robot-World Hand-Eye(s) Calibration Problem with Iterative Methods," *Machine Vision and Applications*, 2017 — [doi:10.1007/s00138-017-0841-7](https://doi.org/10.1007/s00138-017-0841-7) · [code](https://github.com/amy-tabb/RWHEC-Tabb-AhmadYousef) | Reprojection-error AX=YB refinement (phase 11) |
| **V17** | I. Ali, O. Suominen, A. Gotchev, E. Ruiz Morales, "Methods for Simultaneous Robot-World-Hand–Eye Calibration: A Comparative Study," *Sensors* 19(12):2837, 2019 — [doi:10.3390/s19122837](https://doi.org/10.3390/s19122837) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6631330/) | Choosing an AX=YB method (phase 11) |
| **V18** | OpenCV, Camera Calibration and 3D Reconstruction (`calibrateHandEye`, `calibrateRobotWorldHandEye`) — [docs 4.13.0](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html) | Hand-eye implementation (phase 11) |

### Radiometric calibration and HDR capture

| ID | Source | Used for |
|---|---|---|
| **V19** | T. Mitsunaga, S. K. Nayar, "Radiometric Self Calibration," *Proc. CVPR* 1999, pp. 374–380 — [doi:10.1109/CVPR.1999.786966](https://doi.org/10.1109/CVPR.1999.786966) | Polynomial response curve (phase 07) |
| **V20** | M. A. Robertson, S. Borman, R. L. Stevenson, "Estimation-Theoretic Approach to Dynamic Range Enhancement Using Multiple Exposures," *J. Electronic Imaging* 12(2):219–228, 2003 — [doi:10.1117/1.1557695](https://doi.org/10.1117/1.1557695); earlier "Dynamic Range Improvement Through Multiple Exposures," ICIP 1999 — [academia.edu](https://www.academia.edu/11184116/Dynamic_Range_Improvement_Through_Multiple_Exposures) | Weighted HDR merge (OpenCV Robertson) (phase 07) |
| **V21** | M. D. Grossberg, S. K. Nayar, "What Is the Space of Camera Response Functions?," *Proc. CVPR* 2003 — [PDF](https://cave.cs.columbia.edu/old/publications/pdfs/Grossberg_CVPR03.pdf); "Modeling the Space of Camera Response Functions," *IEEE TPAMI* 26(10):1272–1282, 2004 — [doi:10.1109/TPAMI.2004.88](https://doi.org/10.1109/TPAMI.2004.88) | Response-curve prior (EMoR) (phase 07) |
| **V22** | S. W. Hasinoff, F. Durand, W. T. Freeman, "Noise-Optimal Capture for High Dynamic Range Photography," *Proc. CVPR* 2010, pp. 553–560 — [doi:10.1109/CVPR.2010.5540167](https://doi.org/10.1109/CVPR.2010.5540167) · [project](https://people.csail.mit.edu/hasinoff/hdrnoise) | Choosing exposure brackets (phase 07) |
| **V23** | M. Granados, B. Ajdin, M. Wand, C. Theobalt, H.-P. Seidel, H. P. A. Lensch, "Optimal HDR Reconstruction with Linear Digital Cameras," *Proc. CVPR* 2010 — [project](https://vcai.mpi-inf.mpg.de/projects/opthdr/) · [mlanthology](https://mlanthology.org/cvpr/2010/granados2010cvpr-optimal/) | Noise-weighted HDR merge (phase 07) |
| **V24** | E. Reinhard, G. Ward, S. Pattanaik, P. Debevec, W. Heidrich, K. Myszkowski, *High Dynamic Range Imaging: Acquisition, Display, and Image-Based Lighting*, 2nd ed., Morgan Kaufmann, 2010 — [O'Reilly](https://www.oreilly.com/library/view/high-dynamic-range/9780123749147/) | HDR formats and theory (phase 07) |

### Photometric stereo

| ID | Source | Used for |
|---|---|---|
| **V25** | A. Hertzmann, S. M. Seitz, "Example-Based Photometric Stereo: Shape Reconstruction with General, Varying BRDFs," *IEEE TPAMI* 27(8):1254–1264, 2005 — [doi:10.1109/TPAMI.2005.158](https://doi.org/10.1109/TPAMI.2005.158) · [PDF](https://grail.cs.washington.edu/projects/sam/HertzmannSeitzPAMI2005.pdf) | Reference-sphere PS for glossy objects (phase 11) |
| **V26** | R. Basri, D. Jacobs, I. Kemelmacher, "Photometric Stereo with General, Unknown Lighting," *IJCV* 72(3):239–257, 2007 — [doi:10.1007/s11263-006-8815-7](https://doi.org/10.1007/s11263-006-8815-7) · [project](https://www.wisdom.weizmann.ac.il/~vision/photostereo/) | Spherical-harmonic lighting PS (phase 12) |
| **V27** | J. Ackermann, M. Goesele, "A Survey of Photometric Stereo Techniques," *Foundations and Trends in Computer Graphics and Vision* 9(3–4):149–254, 2015 — [doi:10.1561/0600000065](https://doi.org/10.1561/0600000065) · [PDF](http://mesh.brown.edu/3DP-2018/refs/Ackermann-now2015.pdf) | PS method overview (phases 11, 12) |
| **V28** | B. Shi et al., "A Benchmark Dataset and Evaluation for Non-Lambertian and Uncalibrated Photometric Stereo," *Proc. CVPR* 2016 — [CVF](https://openaccess.thecvf.com/content_cvpr_2016/html/Shi_A_Benchmark_Dataset_CVPR_2016_paper.html); extended in *IEEE TPAMI* 41(2), 2019 — [IEEE](https://ieeexplore.ieee.org/document/8281537/); DiLiGenT data — [site](https://sites.google.com/site/photometricstereodata/single) | PS validation dataset (phase 12) |
| **V29** | R. Mecca, A. Wetzler, A. M. Bruckstein, R. Kimmel, "Near Field Photometric Stereo with Point Light Sources," *SIAM J. Imaging Sciences* 7(4):2732–2770, 2014 — [doi:10.1137/140968100](https://doi.org/10.1137/140968100) | Near-light PS model (phase 12) |
| **V30** | Y. Quéau, B. Durix, T. Wu, D. Cremers, F. Lauze, J.-D. Durou, "LED-Based Photometric Stereo: Modeling, Calibration and Numerical Solution," *J. Mathematical Imaging and Vision* 60(3):313–340, 2018 — [doi:10.1007/s10851-017-0761-1](https://doi.org/10.1007/s10851-017-0761-1) | LED anisotropy and falloff model (phases 11, 12) |
| **V31** | F. Logothetis, Y. Quéau, R. Mecca, R. Cipolla, "Semi-calibrated Near-Light Photometric Stereo," *SSVM* 2017, LNCS — [doi:10.1007/978-3-319-58771-4_52](https://doi.org/10.1007/978-3-319-58771-4_52) | Unknown LED intensities (phase 12) |
| **V32** | H. Santo, M. Waechter, Y. Matsushita, "Deep Near-Light Photometric Stereo for Spatially Varying Reflectances," *ECCV* 2020 — [doi:10.1007/978-3-030-58598-3_9](https://doi.org/10.1007/978-3-030-58598-3_9) | Learned near-light PS option (phase 17) |
| **V33** | T. Papadhimitri, P. Favaro, "A New Perspective on Uncalibrated Photometric Stereo," *Proc. CVPR* 2013 — [PDF](https://openaccess.thecvf.com/content_cvpr_2013/papers/Papadhimitri_A_New_Perspective_2013_CVPR_paper.pdf) · [mlanthology](https://mlanthology.org/cvpr/2013/papadhimitri2013cvpr-new/) | Perspective uncalibrated PS fallback (phase 12) |
| **V34** | S. Ikehata, "CNN-PS: CNN-Based Photometric Stereo for General Non-convex Surfaces," *ECCV* 2018 — [doi:10.1007/978-3-030-01267-0_1](https://doi.org/10.1007/978-3-030-01267-0_1) · [PDF](https://www.ecva.net/papers/eccv_2018/papers_ECCV/papers/Ikehata_CNN-PS_CNN-based_Photometric_ECCV_2018_paper.pdf) | Learned PS for glossy objects (phase 17) |
| **V35** | Y. Quéau, J.-D. Durou, J.-F. Aujol, "Normal Integration: A Survey," *J. Mathematical Imaging and Vision* 60(4):576–593, 2018 — [doi:10.1007/s10851-017-0773-x](https://doi.org/10.1007/s10851-017-0773-x) · [code](https://github.com/yqueau/normal_integration) | Normals to depth map (phase 12) |
| **V36** | D. Nehab, S. Rusinkiewicz, J. Davis, R. Ramamoorthi, "Efficiently Combining Positions and Normals for Precise 3D Geometry," *ACM TOG (SIGGRAPH)* 24(3), 2005 — [project](https://gfx.cs.princeton.edu/pubs/Nehab_2005_ECP/index.php) | Fuse PS normals with mesh (phase 12) |

### Multi-view reconstruction, visual hulls, meshing

| ID | Source | Used for |
|---|---|---|
| **V37** | N. Snavely, S. M. Seitz, R. Szeliski, "Photo Tourism: Exploring Photo Collections in 3D," *ACM TOG* 25(3):835–846, 2006 — [doi:10.1145/1141911.1141964](https://doi.org/10.1145/1141911.1141964) | Incremental SfM background (phase 12) |
| **V38** | Y. Furukawa, J. Ponce, "Accurate, Dense, and Robust Multiview Stereopsis," *IEEE TPAMI* 32(8):1362–1376, 2010 — [doi:10.1109/TPAMI.2009.161](https://doi.org/10.1109/TPAMI.2009.161) | Patch-based MVS (PMVS) (phase 12) |
| **V39** | Y. Furukawa, C. Hernández, "Multi-View Stereo: A Tutorial," *Foundations and Trends in Computer Graphics and Vision* 9(1–2):1–148, 2015 — [doi:10.1561/0600000052](https://doi.org/10.1561/0600000052) | MVS overview (phase 12) |
| **V40** | C. Griwodz et al., "AliceVision Meshroom: An Open-Source 3D Reconstruction Pipeline," *Proc. ACM MMSys* 2021 — [doi:10.1145/3458305.3478443](https://doi.org/10.1145/3458305.3478443) · [HAL](https://hal.science/hal-03351139v1) | Alternative pipeline citation (phase 12) |
| **V41** | W. Matusik, C. Buehler, R. Raskar, S. J. Gortler, L. McMillan, "Image-Based Visual Hulls," *Proc. SIGGRAPH* 2000 — [doi:10.1145/344779.344951](https://doi.org/10.1145/344779.344951) · [project](https://people.csail.mit.edu/wojciech/IBVH/index.html) | Silhouette visual hull (phase 12) |
| **V42** | C. Hernández Esteban, F. Schmitt, "Silhouette and Stereo Fusion for 3D Object Modeling," *Computer Vision and Image Understanding* 96(3):367–392, 2004 — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1077314204000542) · [PDF (3DIM'03)](https://carlos-hernandez.org/papers/hernandez_3dim03.pdf) | Hull + stereo fusion on turntable (phase 12) |
| **V43** | W. E. Lorensen, H. E. Cline, "Marching Cubes: A High Resolution 3D Surface Construction Algorithm," *Proc. SIGGRAPH* 1987 — [doi:10.1145/37401.37422](https://doi.org/10.1145/37401.37422) | Voxel grid to mesh (phase 12) |
| **V44** | B. Curless, M. Levoy, "A Volumetric Method for Building Complex Models from Range Images," *Proc. SIGGRAPH* 1996 — [doi:10.1145/237170.237269](https://doi.org/10.1145/237170.237269) | TSDF fusion of depth maps (phase 12) |
| **V45** | M. Kazhdan, M. Bolitho, H. Hoppe, "Poisson Surface Reconstruction," *Eurographics Symp. Geometry Processing* 2006 — [EG DL](https://diglib.eg.org/items/245d6ba1-0209-4365-a4a4-16ce46421620) · [PDF](https://hhoppe.com/poissonrecon.pdf) | Oriented points to mesh (phase 12) |
| **V46** | M. Kazhdan, H. Hoppe, "Screened Poisson Surface Reconstruction," *ACM TOG* 32(3):29, 2013 — [doi:10.1145/2487228.2487237](https://doi.org/10.1145/2487228.2487237) · [PDF](https://www.cs.jhu.edu/~misha/Fall13b/Papers/Kazhdan13.pdf) | Default meshing step (phase 12) |
| **V47** | Q.-Y. Zhou, J. Park, V. Koltun, "Open3D: A Modern Library for 3D Data Processing," arXiv:1801.09847, 2018 — [arXiv](https://arxiv.org/abs/1801.09847) | Point cloud/mesh library (phases 12, 13, 14) |

### Reflectance capture rigs and polarization

| ID | Source | Used for |
|---|---|---|
| **V48** | P. Debevec, T. Hawkins, C. Tchou, H.-P. Duiker, W. Sarokin, M. Sagar, "Acquiring the Reflectance Field of a Human Face," *Proc. SIGGRAPH* 2000 — [doi:10.1145/344779.344855](https://doi.org/10.1145/344779.344855) · [PDF](https://cseweb.ucsd.edu/~ravir/6160/papers/p145-debevec.pdf) | Light-stage relighting concept (phases 09, 11) |
| **V49** | W.-C. Ma, T. Hawkins, P. Peers, C.-F. Chabert, M. Weiss, P. Debevec, "Rapid Acquisition of Specular and Diffuse Normal Maps from Polarized Spherical Gradient Illumination," *EGSR* 2007 — [EG DL](https://diglib.eg.org/items/da04b92c-39fe-41d1-a658-a8535521521c) · [PDF](https://vgl.ict.usc.edu/Research/FaceScanning/EGSR2007_SGI_low.pdf) | Polarized diffuse/specular normals (phase 10) |
| **V50** | A. Ghosh, G. Fyffe, B. Tunwattanapong, J. Busch, X. Yu, P. Debevec, "Multiview Face Capture Using Polarized Spherical Gradient Illumination," *ACM TOG* 30(6), 2011 — [doi:10.1145/2070781.2024163](https://doi.org/10.1145/2070781.2024163) | Multi-view polarized capture (phases 10, 11) |
| **V51** | S. K. Nayar, X.-S. Fang, T. Boult, "Separation of Reflection Components Using Color and Polarization," *IJCV* 21(3):163–186, 1997 — [doi:10.1023/A:1007937815113](https://doi.org/10.1023/A:1007937815113) | Diffuse/specular split with polarizer (phase 10) |
| **V52** | L. B. Wolff, "Polarization-Based Material Classification from Specular Reflection," *IEEE TPAMI* 12(11):1059–1071, 1990 — [doi:10.1109/34.61705](https://doi.org/10.1109/34.61705) | Polarization physics background (phase 10) |

### Open-source turntable scanners

| ID | Source | Used for |
|---|---|---|
| **V53** | OpenScan (Raspberry Pi photogrammetry scanner) — [openscan.eu](https://openscan.eu/pages/openscan-mini) · [GitHub OpenScan3](https://github.com/OpenScan-org/OpenScan3) · [docs](https://openscan-org.github.io/OpenScan-Doc/) | DIY scanner prior art (phase 11) |
| **V54** | FabScan, Media Computing Group, RWTH Aachen University — [project](https://hci.rwth-aachen.de/fabscan) · [FabScan Pi (Hackaday.io)](https://hackaday.io/project/5857-fabscan-pi-3d-laser-scanner) | Turntable laser scanner prior art (phase 11) |
| **V55** | BQ Ciclop scanner + Horus software — [Ciclop GitHub](https://github.com/bqlabs/ciclop) · [Horus GitHub](https://github.com/bqlabs/horus) · [Horus docs](https://horus.readthedocs.io/en/release-0.2/source/getting-started/) | Turntable calibration UX reference (phases 11, 14) |

### Texturing and UV unwrapping

| ID | Source | Used for |
|---|---|---|
| **V56** | B. Lévy, S. Petitjean, N. Ray, J. Maillot, "Least Squares Conformal Maps for Automatic Texture Atlas Generation," *ACM TOG (SIGGRAPH)* 21(3):362–371, 2002 — [doi:10.1145/566654.566590](https://doi.org/10.1145/566654.566590) · [HAL](https://inria.hal.science/inria-00100754/) | LSCM UV unwrapping (phase 13) |
| **V57** | xatlas, mesh parameterization / UV unwrapping library — [GitHub](https://github.com/jpcy/xatlas) | Automatic UV atlas (phase 13) |
| **V58** | M. Waechter, N. Moehrle, M. Goesele, "Let There Be Color! Large-Scale Texturing of 3D Reconstructions," *ECCV* 2014 — [doi:10.1007/978-3-319-10602-1_54](https://doi.org/10.1007/978-3-319-10602-1_54) | View selection for mesh textures (phase 13) |

## Standards, colour, optics and safety

### Appearance and scatter measurement standards (ASTM)

| ID | Source | Used for |
|---|---|---|
| **N1** | ASTM International, "Standard Practice for Goniometric Optical Scatter Measurements," ASTM E2387-19, 2019 — [ASTM store](https://store.astm.org/e2387-19.html) | BRDF/BTDF measurement practice (phases 07, 08) |
| **N2** | ASTM International, "Standard Practice for Angle Resolved Optical Scatter Measurements on Specular or Diffuse Surfaces," ASTM E1392 (withdrawn 2003) — [ASTM](https://www.astm.org/DATABASE.CART/WITHDRAWN/E1392.htm) | Historical BRDF practice cited by Labsphere (phase 07) |
| **N3** | ASTM International, "Standard Practice for Goniophotometry of Objects and Materials," ASTM E167-96 (withdrawn 2005) — [ASTM store](https://store.astm.org/e0167-96.html) | Goniophotometer geometry conventions (phase 06) |
| **N4** | ASTM International, "Standard Test Method for Specular Gloss," ASTM D523 — [ASTM store](https://store.astm.org/standards/d523) | 20/60/85° gloss cross-check (phase 07) |
| **N5** | ASTM International, "Standard Test Methods for Measurement of Gloss of High-Gloss Surfaces by Abridged Goniophotometry," ASTM E430-23, 2023 — [ASTM store](https://store.astm.org/standards/e430) | Haze/distinctness-of-image near specular (phases 08, 17) |
| **N6** | ASTM International, "Standard Terminology of Appearance," ASTM E284-25, 2025 — [doi:10.1520/E0284-25](https://doi.org/10.1520/E0284-25) · [ASTM store](https://store.astm.org/standards/e284) | Docs glossary terms (phase 00) |
| **N7** | ASTM International, "Standard Practice for Specifying the Geometry of Multiangle Spectrophotometers," ASTM E2175-01(2026) — [ASTM store](https://store.astm.org/standards/e2175) | Reporting light/camera angle geometry (phase 08) |
| **N8** | ASTM International, "Standard Test Method for Multiangle Color Measurement of Metal Flake Pigmented Materials," ASTM E2194-14(2025) — [doi:10.1520/E2194-14R25](https://doi.org/10.1520/E2194-14R25) · [ASTM store](https://store.astm.org/standards/e2194) | Aspecular angles for metallic samples (phases 08, 09) |
| **N9** | ASTM International, "Standard Practice for Obtaining Spectrometric Data for Object-Color Evaluation," ASTM E1164-23, 2023 — [ASTM store](https://store.astm.org/standards/e1164) | Spectral data and calibration practice (phase 10) |
| **N10** | ISO, "Paints and varnishes — Determination of gloss value at 20°, 60° and 85°," ISO 2813:2014 — [ISO catalogue](https://www.iso.org/standard/56807.html) | Gloss reference geometry (phase 07) |
| **N11** | M. E. Nadal, E. A. Thompson, "NIST Reference Goniophotometer for Specular Gloss Measurements," *J. Coatings Technology* 73(917):73–80, 2001 — [PDF](https://www.paint.org/wp-content/uploads/2021/09/jctJUNE01-Nadal.pdf) | Reference-instrument design and uncertainty (phases 06, 17) |

### CIE colorimetry, appearance and colour rendering

| ID | Source | Used for |
|---|---|---|
| **N12** | CIE, *A Framework for the Measurement of Visual Appearance*, CIE 175:2006 (ISBN 978-3-901906-52-7) — [CIE](https://cie.co.at/publications/framework-measurement-visual-appearance) | Colour/gloss/translucency/texture scope (phase 00) |
| **N13** | CIE, *Colorimetry, 4th Edition*, CIE 015:2018 — [doi:10.25039/TR.015.2018](https://doi.org/10.25039/TR.015.2018) · [CIE](https://cie.co.at/publications/colorimetry-4th-edition) | XYZ, CIELAB, illuminants from spectra (phase 10) |
| **N14** | CIE, *ILV: International Lighting Vocabulary, 2nd Edition*, CIE S 017/E:2020 — [doi:10.25039/S017.2020](https://doi.org/10.25039/S017.2020) · [CIE](https://cie.co.at/publications/ilv-international-lighting-vocabulary-2nd-edition-0) | Radiometric/photometric terminology (phase 00) |
| **N15** | CIE, *Method of Measuring and Specifying Colour Rendering Properties of Light Sources*, CIE 13.3-1995 (ISBN 978-3-900734-57-2) — [CIE](https://cie.co.at/publications/method-measuring-and-specifying-colour-rendering-properties-light-sources) | COB CRI (Ra) meaning (phases 04, 10) |
| **N16** | CIE, *CIE 2017 Colour Fidelity Index for Accurate Scientific Use*, CIE 224:2017 — [doi:10.25039/TR.224.2017](https://doi.org/10.25039/TR.224.2017) · [CIE](https://cie.co.at/publications/cie-2017-colour-fidelity-index-accurate-scientific-use) | Rf for white and LED-bank spectra (phase 10) |
| **N17** | K. A. G. Smet, CRI_CIE_Rf_2017 calculator (MATLAB/Excel) — [GitHub](https://github.com/ksmet1977/CRI_CIE_Rf_2017) | Checking our Rf implementation (phase 10) |
| **N18** | IES, *Technical Memorandum: IES Method for Evaluating Light Source Color Rendition*, ANSI/IES TM-30-24 — [IES store](https://store.ies.org/product/technical-memorandum-ies-method-for-evaluating-light-source-color-rendition/?v=eb65bcceaa5f) · [ANSI](https://webstore.ansi.org/standards/iesna/ansiiestm3024) | Rf/Rg report for light sources (phase 10) |
| **N19** | M. P. Royer, "Analysis of Color Rendition Specification Criteria," *Proc. SPIE* 10940 (Light-Emitting Devices, Materials, and Applications), 2019 — [DOE](https://www.energy.gov/cmei/ssl/articles/analysis-color-rendition-specification-criteria) | Choosing Rf/Rg acceptance thresholds (phase 10) |
| **N20** | Y. Ohno, "Spectral design considerations for white LED color rendering," *Optical Engineering* 44(11), 2005 — [doi:10.1117/1.2130694](https://doi.org/10.1117/1.2130694) | Designing the 8-band LED spectrum (phase 10) |

### Colour science books

| ID | Source | Used for |
|---|---|---|
| **N21** | G. Wyszecki, W. S. Stiles, *Color Science: Concepts and Methods, Quantitative Data and Formulae*, 2nd ed., Wiley, 1982 — review [doi:10.1002/col.5080080421](https://doi.org/10.1002/col.5080080421) | Colorimetric data and formulae (phase 10) |
| **N22** | M. D. Fairchild, *Color Appearance Models*, 3rd ed., Wiley, 2013 — [doi:10.1002/9781118653128](https://doi.org/10.1002/9781118653128) | Appearance/white point for renders (phases 10, 13) |
| **N23** | R. W. G. Hunt, M. R. Pointer, *Measuring Colour*, 4th ed., Wiley, 2011 — [doi:10.1002/9781119975595](https://doi.org/10.1002/9781119975595) | Practical colour measurement geometry (phase 10) |

### Camera characterization and colour encoding

| ID | Source | Used for |
|---|---|---|
| **N24** | EMVA, *Standard 1288: Standard for Characterization of Image Sensors and Cameras*, Release 4.0 (Linear), 2021 — [EMVA](https://www.emva.org/standards-technology/emva-1288/) · [PDF](https://corp.dxomark.com/wp-content/uploads/2026/06/EMVA1288Linear_4.0Release.pdf) | IMX477 linearity, noise, dark current tests (phases 06, 07) |
| **N25** | ISO, "Photography — Electronic still picture imaging — Resolution and spatial frequency responses," ISO 12233:2023 (revised by ISO 12233:2024, "Digital cameras — Resolution and spatial frequency responses") — [ISO catalogue](https://www.iso.org/standard/79169.html) | Slanted-edge SFR of 16 mm lens (phase 06) |
| **N26** | ISO, "Photography — Electronic still-picture imaging — Noise measurements," ISO 15739:2023 — [ISO catalogue](https://www.iso.org/standard/82233.html) | Noise and dynamic range for HDR (phase 07) |
| **N27** | ISO, "Graphic technology and photography — Colour characterisation of digital still cameras (DSCs) — Part 1: Stimuli, metrology and test procedures," ISO 17321-1:2012 — [ISO (2006 ed., revised by 2012)](https://www.iso.org/standard/35835.html) · [2012 ed. catalogue](https://standards.iteh.ai/catalog/standards/iso/4256cfe1-8683-4b48-a68b-45aff0db2c4e/iso-17321-1-2012) | Camera spectral sensitivity/colour matrix (phase 10) |
| **N28** | IEC, "Multimedia systems and equipment — Colour measurement and management — Part 2-1: Colour management — Default RGB colour space — sRGB," IEC 61966-2-1:1999 (+AMD1:2003) — [ANSI webstore](https://webstore.ansi.org/standards/iec/iec61966ed1999) · [IEC AMD1](https://webstore.iec.ch/en/publication/6168) | sRGB transfer function for texture export (phases 07, 13) |
| **N29** | M. Stokes, M. Anderson, S. Chandrasekar, R. Motta, "A Standard Default Color Space for the Internet — sRGB," v1.10, 1996 — [W3C](https://www.w3.org/Graphics/Color/sRGB.html) | Linear vs gamma-encoded texture handling (phase 13) |

### Reflectance standards (PTFE / Spectralon)

| ID | Source | Used for |
|---|---|---|
| **N30** | V. R. Weidner, J. J. Hsia, "Reflection properties of pressed polytetrafluoroethylene powder," *J. Opt. Soc. Am.* 71(7):856–861, 1981 — [doi:10.1364/JOSA.71.000856](https://doi.org/10.1364/JOSA.71.000856) | PTFE white reference reflectance (phase 07) |
| **N31** | V. R. Weidner, J. J. Hsia, B. Adams, "Laboratory intercomparison study of pressed polytetrafluoroethylene powder reflectance standards," *Appl. Opt.* 24(14):2225, 1985 — [doi:10.1364/AO.24.002225](https://doi.org/10.1364/AO.24.002225) | PTFE reference repeatability (phase 07) |
| **N32** | J. J. Hsia, P. Y. Barnes, "45°/0° reflectance factors of pressed polytetrafluoroethylene (PTFE) powder," NIST Technical Note 1413, 1995 — [doi:10.6028/NIST.TN.1413](https://doi.org/10.6028/NIST.TN.1413) | 45/0 PTFE factor for our geometry (phase 07) |
| **N33** | P. Y. Barnes, E. A. Early, A. C. Parr, "Spectral Reflectance," NIST Special Publication 250-48, 1998 — [doi:10.6028/NIST.SP.250-48](https://doi.org/10.6028/NIST.SP.250-48) | Traceable reflectance calibration method (phase 07) |
| **N34** | Labsphere, *Technical Guide: Reflectance Materials and Coatings* (Spectralon >99 % 400–1500 nm) — [PDF](https://www.systems-eng.co.jp/dcms_media/other/Guide_Reflectance_Materials_Coatings.pdf) | Spectralon vs DIY PTFE choice (phase 07) |
| **N35** | A. Springsteen, "Reflectance Spectroscopy: An Overview of Classification and Techniques," in *Applied Spectroscopy: A Compact Reference for Practitioners*, Academic Press, 1998, pp. 193–224 — [doi:10.1016/B978-012764070-9/50008-1](https://doi.org/10.1016/B978-012764070-9/50008-1) | Reflectance geometry nomenclature (phase 07) |
| **N36** | A. Springsteen, "Standards for Reflectance Measurements," in *Applied Spectroscopy: A Compact Reference for Practitioners*, Academic Press, 1998, pp. 247–267 — [doi:10.1016/B978-012764070-9/50010-X](https://doi.org/10.1016/B978-012764070-9/50010-X) | Choosing white/grey/black references (phase 07) |

### Multispectral imaging with LED illumination

| ID | Source | Used for |
|---|---|---|
| **N37** | J.-I. Park, M.-H. Lee, M. D. Grossberg, S. K. Nayar, "Multispectral Imaging Using Multiplexed Illumination," *ICCV* 2007, pp. 1–8 — [doi:10.1109/ICCV.2007.4409090](https://doi.org/10.1109/ICCV.2007.4409090) | Multiplexed LED band capture (phase 10) |
| **N38** | R. Shrestha, J. Y. Hardeberg, "Multispectral imaging using LED illumination and an RGB camera," *Color and Imaging Conf.* 21(1):8–13, 2013 — [doi:10.2352/CIC.2013.21.1.art00003](https://doi.org/10.2352/cic.2013.21.1.art00003) | LED bank + RGB camera reflectance (phase 10) |
| **N39** | R. Shrestha, J. Y. Hardeberg, "Evaluation and comparison of multispectral imaging systems," *Color and Imaging Conf.* 22(1), 2014 — [doi:10.2352/CIC.2014.22.1.art00018](https://doi.org/10.2352/cic.2014.22.1.art00018) | Spectral accuracy metrics (phases 10, 17) |
| **N40** | R. Shrestha, J. Y. Hardeberg, "How Are LED Illumination Based Multispectral Imaging Systems Influenced by Different Factors?," *ICISP 2014*, LNCS, pp. 61–71 — [doi:10.1007/978-3-319-07998-1_8](https://doi.org/10.1007/978-3-319-07998-1_8) | Noise/band-count sensitivity of LED bank (phase 10) |
| **N41** | F. H. Imai, R. S. Berns, D.-Y. Tzeng, "A Comparative Analysis of Spectral Reflectance Estimated in Various Spaces Using a Trichromatic Camera System," *J. Imaging Sci. Technol.* 44(4):280–287, 2000 — [doi:10.2352/J.ImagingSci.Technol.2000.44.4.art00003](https://doi.org/10.2352/j.imagingsci.technol.2000.44.4.art00003) | Spectral reconstruction from camera signals (phase 10) |
| **N42** | F. H. Imai, M. R. Rosen, R. S. Berns, "Comparison of Spectrally Narrow-Band Capture Versus Wide-Band with a Priori Sample Analysis for Spectral Reflectance Estimation," *Color and Imaging Conf.* 8(1):234–241, 2000 — [doi:10.2352/CIC.2000.8.1.art00043](https://doi.org/10.2352/cic.2000.8.1.art00043) | Narrow-band LEDs vs filters trade-off (phase 10) |
| **N43** | J. Y. Hardeberg, *Acquisition and Reproduction of Color Images: Colorimetric and Multispectral Approaches*, 2001 (book of PhD thesis) — review by M. H. Brill [doi:10.1002/col.10073](https://doi.org/10.1002/col.10073) | Camera colorimetric/spectral calibration (phase 10) |
| **N44** | J. Y. Hardeberg, "Filter Selection for Multispectral Color Image Acquisition," *J. Imaging Sci. Technol.* 48(2), 2004 — [doi:10.2352/J.ImagingSci.Technol.2004.48.2.art00005](https://doi.org/10.2352/j.imagingsci.technol.2004.48.2.art00005) | Choosing the 8 LED bands (phase 10) |

### Optics textbooks

| ID | Source | Used for |
|---|---|---|
| **N45** | R. Kingslake, R. B. Johnson, *Lens Design Fundamentals*, 2nd ed., Academic Press/Elsevier, 2010 (ISBN 978-0-12-374301-5) — e.g. ch. "Aberration Theory" [doi:10.1016/B978-0-12-374301-5.00008-5](https://doi.org/10.1016/b978-0-12-374301-5.00008-5) | M12 lens f-number/aberration reasoning (phase 06) |
| **N46** | J. W. Goodman, *Introduction to Fourier Optics* (1st ed. 1968; 4th ed. 2017) — review [doi:10.1063/1.3035549](https://doi.org/10.1063/1.3035549) | Diffraction limit and MTF at f/8 (phase 06) |

### Photobiological and machine/electrical safety

| ID | Source | Used for |
|---|---|---|
| **N47** | IEC, "Photobiological safety of lamps and lamp systems," IEC 62471 (BS EN 62471) — [BSI record doi:10.3403/30149289](https://doi.org/10.3403/30149289) | COB and LED-bank eye-safety risk groups (phases 04, 10) |
| **N48** | ISO, "Safety of machinery — Emergency stop function — Principles for design," ISO 13850:2015 (BS EN ISO 13850:2015) — [BSI record doi:10.3403/30265059](https://doi.org/10.3403/30265059) | E-stop category and reset behaviour (phases 01, 02) |
| **N49** | IEC, "Safety of machinery — Electrical equipment of machines — Part 1: General requirements," IEC 60204-1 (BS EN 60204-1) — [BSI record doi:10.3403/30238348](https://doi.org/10.3403/30238348) | Power wiring, colours, stop circuit (phase 01) |
| **N50** | ISO, "Safety of machinery — General principles for design — Risk assessment and risk reduction," ISO 12100:2010 (BS EN ISO 12100:2010) — [BSI record doi:10.3403/30201665](https://doi.org/10.3403/30201665) | Pinch-point/hazard risk assessment (phases 00, 16) |
| **N51** | IEC, "Audio/video, information and communication technology equipment — Part 1: Safety requirements," IEC 62368-1 (BS EN IEC 62368-1) — [BSI record doi:10.3403/30347376U](https://doi.org/10.3403/30347376u) | Bought-in PSU safety listing (phase 01) |

## Motion control, electronics and open hardware

### Stepper drivers and microcontrollers

| ID | Source | Used for |
|---|---|---|
| **H1** | Analog Devices (Trinamic), "TMC2209 Datasheet," rev. 1.09 — [PDF](https://www.analog.com/media/en/technical-documentation/data-sheets/tmc2209_datasheet_rev1.09.pdf) · [product](https://www.analog.com/en/products/tmc2209.html) | Driver registers, UART, current (phase 02) |
| **H2** | Analog Devices (Trinamic), "AN-002: Parameterization of StallGuard2 & CoolStep," application note — [page](https://www.analog.com/en/resources/app-notes/an-002.html) · [PDF](https://www.analog.com/media/en/technical-documentation/app-notes/an-002.pdf) | Stall-detection thresholds, crash detection (phases 02, 04) |
| **H3** | B. Dwersteg (Analog Devices/Trinamic), "AN-026: Programmable Adaptive Microstep Table," application note — [page](https://www.analog.com/en/resources/app-notes/an-026.html) · [PDF](https://www.analog.com/media/en/technical-documentation/app-notes/an-026.pdf) | Microstep linearity, even step spacing (phases 08, 09) |
| **H4** | Marlin Firmware, "Trinamic drivers" (StealthChop, SpreadCycle, hybrid threshold, sensorless homing) — [docs](https://marlinfw.org/docs/hardware/tmc_drivers.html) | StealthChop vs SpreadCycle choice (phase 02) |
| **H5** | Espressif Systems, "ESP32 Technical Reference Manual," v5.8 (GPIO matrix, UART, RMT, LEDC, MCPWM, timers) — [PDF](https://documentation.espressif.com/esp32_technical_reference_manual_en.pdf) | E4 MCU peripherals, step timing (phase 02) |
| **H6** | Espressif Systems, "ESP32 Series Datasheet," v5.3 — [PDF](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf) · [HTML](https://documentation.espressif.com/esp32_datasheet_en.html) | Strapping pins, electrical limits (phase 02) |
| **H7** | Raspberry Pi Ltd, "RP2040 Datasheet" — [PDF](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) · [product brief](https://datasheets.raspberrypi.com/rp2040/rp2040-product-brief.pdf) | Pico GPIO, pull-ups, PIO (phase 02) |
| **H8** | Raspberry Pi Ltd, "Raspberry Pi Pico-series Python SDK: A MicroPython environment for Raspberry Pi microcontrollers" — [PDF](https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf) | MicroPython button-hub firmware (phase 02) |

### Interface electronics and position sensors

| ID | Source | Used for |
|---|---|---|
| **H9** | Sharp Corporation, "PC817XxNSZ1B Series" photocoupler data sheet, OP18002EN, 2018 — [PDF](https://global.sharp/products/device/lineup/data/pdf/datasheet/PC817XxNSZ1B_e.pdf) | 24 V sense optocoupler, CTR (phase 01) |
| **H10** | Texas Instruments, "ULN200x, ULQ200x High-Voltage, High-Current Darlington Transistor Arrays," SLRS027T, 2025 — [PDF](https://www.ti.com/lit/gpn/ULN2003A) · [product](https://www.ti.com/product/ULN2003A); "ULN2803A Darlington Transistor Array," SLRS049 — [PDF](https://datasheet.octopart.com/ULN2803AN-Texas-Instruments-datasheet-14122296.pdf) | 8-band LED low-side switching (phase 10) |
| **H11** | Vishay Semiconductors, "TCST2103, TCST2202, TCST2300: Transmissive Optical Sensor with Phototransistor Output," doc. 81147 — [PDF](https://www.vishay.com/docs/81147/tcst2103.pdf) · [product](https://www.vishay.com/en/product/81147/) | Optical homing flag, 1 mm aperture (phases 04, 05) |
| **H12** | ams AG (ams OSRAM), "AS5600 – 12-bit Programmable Contactless Potentiometer," datasheet v1-00, 2014 — [PDF](https://www.mouser.com/pdfdocs/AMS_AS5600_Datasheet_EN.PDF) · [v1-06](https://files.seeedstudio.com/wiki/Grove-12-bit-Magnetic-Rotary-Position-Sensor-AS5600/res/Magnetic%20Rotary%20Position%20Sensor%20AS5600%20Datasheet.pdf) | Absolute-angle check of axes (phase 17) |

### Camera interface

| ID | Source | Used for |
|---|---|---|
| **H13** | Sony Semiconductor Solutions, "IMX477-AACK: Diagonal 7.857 mm (Type 1/2.3) 12.3 Mega-Pixel CMOS Image Sensor," flyer, 2018 — [PDF](https://www.sony-semicon.com/files/62/pdf/p-13_IMX477-AACK_Flyer.pdf) | Pixel pitch 1.55 µm, sensor size (phase 06) |
| **H14** | USB Implementers Forum, "Video Class v1.5 document set" (USB Device Class Definition for Video Devices, rev. 1.5), 2012 — [usb.org](https://www.usb.org/document-library/video-class-v15-document-set) | UVC exposure/white-balance controls (phase 06) |
| **H15** | Linux kernel documentation, "The Linux USB Video Class (UVC) driver" — [docs](https://www.kernel.org/doc/html/latest/userspace-api/media/drivers/uvcvideo.html) | uvcvideo controls, extension units (phases 06, 14) |

### Belt drives and positioning accuracy

| ID | Source | Used for |
|---|---|---|
| **H16** | Gates Corporation, "PowerGrip GT2 Belt Drives – Drive Design Manual" — [PDF](https://docs.rs-online.com/5016/0900766b8002d3b7.pdf) | GT tooth profile, registration, backlash (phases 04, 05) |
| **H17** | Gates Corporation, "Light Power & Precision Drive Design Manual" (2 mm GT profile, belt tensioning) — [PDF](https://www.gates.com/content/dam/documents-library/catalogs/light-power-and-precision-manual.pdf) | Small-pitch pulley sizing, tension (phases 04, 05) |
| **H18** | Prusa Research, "Adjusting belt tension (CORE One/+, CORE One INDX, CORE One L/+)," Prusa Knowledge Base — [article](https://help.prusa3d.com/article/adjusting-belt-tension-core-one_845048) · [MK4 article](https://help.prusa3d.com/article/adjusting-belt-tension-mk4-s-mk3-9-s-mk3-5-s-mk3-s_112380) | Frequency-based belt tension check (phase 04) |
| **H19** | Oriental Motor USA, "Stepper Motor Basics" (step-angle accuracy ±3 arcmin, non-cumulative) — [page](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html) · ["Everything You Need to Know About Stepper Motors" PDF](https://www.orientalmotor.com/stepper-motors/technology/pdf/everything-you-need-to-know-about-stepper-motors.pdf) | Angular error budget per axis (phase 07) |
| **H20** | M. Walter, "How Accurate Is Microstepping Really?," *Hackaday*, 29 Aug 2016 — [article](https://hackaday.com/2016/08/29/how-accurate-is-microstepping-really/) | Microsteps ≠ accuracy under load (phase 08) |
| **H21** | Dr. Fritz Faulhaber GmbH, "Stepper Motor Technical Note: Microstepping Myths and Realities" — [PDF](https://www.faulhaber.com/fileadmin/user_upload/Support/dff_200276_whitepaper_microstepping_8cb.pdf) | Incremental torque per microstep (phase 08) |
| **H22** | Zaber Technologies, "Microstepping Tutorial" — [article](https://www.zaber.com/technical-articles/microstepping-tutorial) | Stiction vs microstep resolution (phase 07) |
| **H23** | C. Chang, T. Tran, "Mastering Precision: Understanding Microstepping in Motion Control," *Analog Dialogue* 59(2), 2025 — [article](https://www.analog.com/en/resources/analog-dialogue/articles/mastering-precision-understanding-microstepping.html) | Microstep current waveforms, holding torque (phase 02) |

### Motion firmware, homing and G-code

| ID | Source | Used for |
|---|---|---|
| **H24** | Grbl project (gnea), "An open source, embedded, high performance g-code-parser and CNC milling controller" — [GitHub gnea/grbl](https://github.com/gnea/grbl) · [wiki](https://github.com/gnea/grbl/wiki) | FluidNC lineage, protocol, homing cycle (phase 02) |
| **H25** | grblHAL, "grblHAL core code and master Wiki" — [GitHub grblHAL/core](https://github.com/grblHAL/core) | Alternative Grbl-derived firmware (phase 02) |
| **H26** | LinuxCNC, "Homing Configuration" (HOME_SEARCH_VEL, HOME_LATCH_VEL, HOME_OFFSET) — [docs](https://linuxcnc.org/docs/html/config/ini-homing.html) | Two-speed search/latch homing (phases 04, 05) |
| **H27** | T. R. Kramer, F. M. Proctor, E. R. Messina, "The NIST RS274NGC Interpreter – Version 3," NISTIR 6556, NIST, 2000 — [NIST](https://www.nist.gov/publications/nist-rs274ngc-interpreter-version-3) · [PDF](https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir6556.pdf) | G-code semantics for capture scripts (phase 14) |

### Open-source hardware practice and licensing

| ID | Source | Used for |
|---|---|---|
| **H28** | J. M. Pearce, "Building Research Equipment with Free, Open-Source Hardware," *Science* 337(6100):1303–1304, 2012 — [doi:10.1126/science.1228183](https://doi.org/10.1126/science.1228183) · [MTU repository](https://digitalcommons.mtu.edu/michigantech-p/12237/) | Rationale for open lab equipment (phase 00) |
| **H29** | J. M. Pearce, *Open-Source Lab: How to Build Your Own Hardware and Reduce Research Costs*, Elsevier, 2014 — [doi:10.1016/C2012-0-07249-3](https://doi.org/10.1016/C2012-0-07249-3) · [MTU repository](https://digitalcommons.mtu.edu/michigantech-p/5871/) | Low-cost scientific tool design (phase 00) |
| **H30** | R. Jones, P. Haufe, E. Sells, P. Iravani, V. Olliver, C. Palmer, A. Bowyer, "RepRap – the replicating rapid prototyper," *Robotica* 29(1):177–191, 2011 — [doi:10.1017/S026357471000069X](https://doi.org/10.1017/S026357471000069X) · [PDF](https://fab.cba.mit.edu/classes/865.18/replication/Jones.pdf) | Printed-part machine heritage (phase 03) |
| **H31** | Open Source Hardware Association, "Open Source Hardware (OSHW) Definition 1.0" — [oshwa.org](https://oshwa.org/definition/) · [best practices](https://oshwa.org/resources/sharing-best-practices/) | Release documentation criteria (phase 16) |
| **H32** | CERN, "CERN Open Hardware Licence Version 2" (P, W, S variants) — [ohwr.org](https://www.ohwr.org/cernohl) · [CERN-OHL-S-2.0 text](https://ohwr.org/project/cernohl/-/wikis/uploads/819d71bea3458f71fba6cf4fb0f2de6b/cern_ohl_s_v2.txt) · [FAQ](https://gitlab.com/ohwr/project/cernohl/-/wikis/faq) · [OSI page](https://opensource.org/license/cern-ohl-s-2.0) | Hardware licence choice (phase 16) |
| **H33** | Gathering for Open Science Hardware, "GOSH Manifesto" — [openhardware.science](https://openhardware.science/gosh-manifesto/) | Project values, accessibility (phase 16) |
| **H34** | J. Bonvoisin, R. Mies, J.-F. Boujut, R. Stark, "What is the 'Source' of Open Source Hardware?," *Journal of Open Hardware* 1(1), 2017 — [doi:10.5334/joh.7](https://doi.org/10.5334/joh.7) · [HAL/RePEc](https://ideas.repec.org/p/hal/journl/hal-01582660.html) | What files to publish (phase 16) |
| **H35** | J. T. Collins, J. Knapper, J. Stirling, …, R. Bowman, "Robotic microscopy for everyone: the OpenFlexure microscope," *Biomedical Optics Express* 11(5):2447–2460, 2020 — [doi:10.1364/BOE.385729](https://doi.org/10.1364/BOE.385729) · [open access](https://opg.optica.org/boe/fulltext.cfm?uri=boe-11-5-2447&id=429869) | Model for documented printed instrument (phases 00, 16) |
| **H36** | Elsevier, "Guide for authors – HardwareX" — [ScienceDirect](https://www.sciencedirect.com/journal/hardwarex/publish/guide-for-authors); T. Duncombe, "HardwareX manuscript templates," Zenodo, 2021 — [doi:10.5281/zenodo.5078227](https://doi.org/10.5281/zenodo.5078227) | Paper structure, BOM, validation (phase 16) |

### Low-cost open instruments (HardwareX and related)

| ID | Source | Used for |
|---|---|---|
| **H37** | Y. Toschke, J. Klenen, M. Imlau, "Open Photonics: An integrated approach for building a 3D-printed motorized rotation stage system," *HardwareX* 20:e00577, 2024 — [doi:10.1016/j.ohx.2024.e00577](https://doi.org/10.1016/j.ohx.2024.e00577) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11639585) | ESP32 rotation stage, home switch (phases 05, 09) |
| **H38** | D. Schneidereit, L. Kraus, J. C. Meier, O. Friedrich, D. F. Gilbert, "Step-by-step guide to building an inexpensive 3D printed motorized positioning stage for automated high-content screening microscopy," *Biosensors and Bioelectronics* 92:472–481, 2017 — [doi:10.1016/j.bios.2016.10.078](https://doi.org/10.1016/j.bios.2016.10.078) | Printed stepper stage accuracy (phase 03) |
| **H39** | I. Hietanen, I. T. S. Heikkinen, H. Savin, J. M. Pearce, "Approaches to open source 3-D printable probe positioners and micromanipulators for probe stations," *HardwareX* e00042, 2018 — [doi:10.1016/j.ohx.2018.e00042](https://doi.org/10.1016/j.ohx.2018.e00042) | Validating printed positioners (phase 07) |
| **H40** | J. Salazar-Vazquez, A. Mendez-Vazquez, "A plug-and-play Hyperspectral Imaging Sensor using low-cost equipment," *HardwareX* e00087, 2020 — [doi:10.1016/j.ohx.2019.e00087](https://doi.org/10.1016/j.ohx.2019.e00087) | Low-cost spectral imaging prior art (phase 10) |
| **H41** | K. C. Dhankania, J. M. Pearce, "Open Source Laboratory Sample Rotator Mixer and Shaker," *HardwareX*, 2016 — [ScienceDirect](http://www.sciencedirect.com/science/article/pii/S2468067216300049) | Printed rotary stage prior art (phase 05) |
| **H42** | Public Lab, "Desktop Spectrometry Kit 3.0" and Spectral Workbench — [wiki](https://publiclab.org/wiki/desktop-spectrometry-kit-3-0) · [spectrometer wiki](http://publiclab.org/wiki/spectrometer) · [GitHub](https://github.com/publiclab/spectral-workbench) | DIY spectral calibration (phase 10) |

### Design tools and project publishing

| ID | Source | Used for |
|---|---|---|
| **H43** | KiCad EDA — [kicad.org](https://kicad.org/) · [source mirror](https://github.com/KiCad/kicad-source-mirror) · [developer docs](https://dev-docs.kicad.org) | Power-box and hub schematics (phases 01, 02) |
| **H44** | GitHub Docs, "REST API endpoints for milestones," "…for issues," "…for labels" — [milestones](https://docs.github.com/en/rest/issues/milestones) · [issues](https://docs.github.com/en/rest/issues/issues) · [labels](https://docs.github.com/en/rest/issues/labels) | Phase milestones and issue scripts (phase 00) |
| **H45** | GitHub Docs, "Configuring a publishing source for your GitHub Pages site" and "Using custom workflows with GitHub Pages" — [publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) · [custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) | Documentation site deployment (phase 16) |

### Software dependencies

| ID | Source | Used for |
|---|---|---|
| **H46** | Python Software Foundation, Python language and standard library — [python.org](https://www.python.org) · [docs](https://docs.python.org) · [CPython](https://github.com/python/cpython) | Laptop app runtime (phase 14) |
| **H47** | C. R. Harris, K. J. Millman, S. J. van der Walt, et al., "Array programming with NumPy," *Nature* 585:357–362, 2020 — [doi:10.1038/s41586-020-2649-2](https://doi.org/10.1038/s41586-020-2649-2) · [numpy.org](https://numpy.org) | Image arrays, HDR, geometry (phase 07) |
| **H48** | P. Virtanen, R. Gommers, T. E. Oliphant, et al., "SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python," *Nature Methods* 17:261–272, 2020 — [doi:10.1038/s41592-019-0686-2](https://doi.org/10.1038/s41592-019-0686-2) · [scipy.org](https://scipy.org/) | BRDF least-squares fitting, rotations (phases 07, 08) |
| **H49** | G. Bradski, "The OpenCV Library," *Dr. Dobb's Journal of Software Tools*, 2000 — [citation (OpenCV wiki)](https://github.com/opencv/opencv/wiki/CiteOpenCV) · [opencv.org](https://opencv.org) | Capture, calibration, ChArUco (phases 06, 11) |
| **H50** | PyYAML (YAML parser and emitter for Python) — [pyyaml.org](https://pyyaml.org/) · [docs](https://pyyaml.org/wiki/PyYAMLDocumentation) · [GitHub](https://github.com/yaml/pyyaml); H. Krekel, B. Oliveira, R. Pfannschmidt, F. Bruynooghe, B. Laugher, F. Bruhin, "pytest," 2004– — [docs](https://docs.pytest.org/en/latest/) · [GitHub](https://github.com/pytest-dev/pytest) | Config files and test suite (phase 14) |

### Standalone station

| ID | Source | Used for |
|---|---|---|
| **H51** | Raspberry Pi Zero 2 W — [product](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) | Standalone station (phase 15) |
| **H52** | micropython-lib SSD1306 driver — [GitHub](https://github.com/micropython/micropython-lib/tree/master/micropython/drivers/display/ssd1306) | Panel OLED (phase 15) |
| **H53** | Raspberry Pi configuration, `raspi-config` and UART — [docs](https://www.raspberrypi.com/documentation/computers/configuration.html) | Pi UART to Pico (phase 15) |
| **H54** | usbipd-win — [GitHub](https://github.com/dorssel/usbipd-win) | USB boards into WSL (phase 02) |
| **H55** | MicroPython `machine.UART` — [docs](https://docs.micropython.org/en/latest/library/machine.UART.html) | Pico ↔ Pi link (phase 15) |
| **H56** | CadQuery 2.x, parametric CAD in Python — [PyPI](https://pypi.org/project/cadquery/), [GitHub](https://github.com/CadQuery/cadquery) | Generated STEP/STL parts (phase 00) |
| **H57** | numpy-stl — [PyPI](https://pypi.org/project/numpy-stl/) | Parts gallery rendering (phase 00) |
| **H58** | Matplotlib — [matplotlib.org](https://matplotlib.org/) | Parts gallery rendering (phase 00) |
| **H59** | ams AS7341 11-channel spectral sensor; Adafruit breakout #4698 — [product](https://www.adafruit.com/product/4698) (not fetched; price to confirm) | Spectral sensor (phase 10) |
| **H60** | W3C, Portable Network Graphics (PNG) Specification — [w3.org/TR/png](https://www.w3.org/TR/png/) | Built-in PNG reader/writer in `opengonio.imageio` (phase 00) |


## Firmware, protocols, software

| ID | Source | Used for |
|---|---|---|
| **R20** | FluidNC wiki, Axes — [link](http://wiki.fluidnc.com/en/config/axes) | Axis/homing keys, degrees as units, shared limits |
| **R21** | FluidNC wiki, Trinamic drivers — [link](http://wiki.fluidnc.com/en/config/trinamic_drivers) | tmc_2209 keys |
| **R22** | FluidNC UART sections — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/config/uart_sections.md) | uart1 block |
| **R23** | FluidNC example TMC2209 config — [yaml](https://github.com/bdring/fluidnc-config-files/blob/main/official/TMC2209_corexy.yaml) | Config template |
| **R24** | FluidNC WiFi/Bluetooth — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/features/wifi_bt.md) | WiFi modes, telnet :23, BT build |
| **R25** | FluidNC Web API — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/features/WebAPI.md) | Websocket port |
| **R26** | FluidNC user outputs — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/config/user_outputs.md) | M62/M63 light control |
| **R27** | FluidNC control pins — [link](http://wiki.fluidnc.com/en/config/control) | Feed-hold (PAUSE) pin |
| **R28** | FluidNC commands and settings — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/features/commands_and_settings.md) | $H, $HX, $MD, $ME |
| **R29** | FluidNC serial protocol — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/support/serial_protocol.md) | Status report format |
| **R30** | FluidNC serial port usage (old wiki) — [link](https://github.com/bdring/FluidNC/wiki/Serial-Port-Usage/29e7ed734b79534bf9c8e59aa6ca9fba6ba8c96f) | 115200 8N1 |
| **R31** | FluidNC hardware list — [link](https://github.com/bdring/FluidNC/wiki/Hardware-that-Runs-FluidNC/a1d2287bd26a527c9c327af35360ff75a36d6f93) | E4 supported |
| **R32** | fluidnc-config-files — [GitHub](https://github.com/bdring/fluidnc-config-files) | Searched for an E4 config |
| **R33** | V1E forum, FluidNC config for FYSETC E4 — [thread](https://forum.v1e.com/t/fluidnc-primo-config-for-fysetc-e4-board/34096) | E4 TMC addresses |
| **R34** | FluidNC issue #1311 (E4 config) — [link](https://github.com/bdring/FluidNC/issues/1311) | E4 notes |
| **R35** | OnStepX E4 pin map — [link](https://github.com/hjd1964/OnStepX/blob/main/src/pinmaps/Pins.FYSETC_E4.h) | E0 UART address |
| **R36** | Arduino-ESP32 Bluetooth docs — [link](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/bluetooth.html) | BT serial is classic-ESP32 only |
| **R42** | MicroPython rp2 quick reference — [link](https://docs.micropython.org/en/latest/rp2/quickref.html) | SoftI2C, pins (download page micropython.org/download, not fetched) |
| **R43** | MicroPython machine.PWM — [link](https://docs.micropython.org/en/latest/library/machine.PWM.html) | Servo PWM (phase 10 option) |
| **R44** | pyserial — [API](https://pyserial.readthedocs.io/en/latest/pyserial_api.html), [intro](https://pyserial.readthedocs.io/en/latest/shortintro.html) | Serial transport |
| **R45** | Bluetooth COM ports on Windows — [Microsoft Q&A](https://learn.microsoft.com/en-gb/answers/questions/1166304/standard-serial-over-bluetooth-link-select-com-por), [In The Hand](https://inthehand.com/2020/11/22/bluetooth-virtual-com-ports/) | BT link |
| **R46** | rfcomm(1) — [man page](https://manpages.debian.org/testing/bluez/rfcomm.1.en.html) | BT link on Linux |
| **R47** | OpenCV video I/O flags — [link](https://docs.opencv.org/4.x/d4/d15/group__videoio__flags__base.html) | Camera properties |
| **R48** | OpenCV issue #17019 — [link](https://github.com/opencv/opencv/issues/17019) | Backend-dependent properties |
| **R49** | OpenCV HDR tutorial — [link](https://docs.opencv.org/4.13.0/d2/df0/tutorial_py_hdr.html), [photo.hpp](https://docs.opencv.org/4.13.0/dc/d81/photo_8hpp.html) | CalibrateDebevec / MergeDebevec |
| **R50** | v4l2-ctl(1) — [man page](https://www.mankier.com/1/v4l2-ctl) | Manual camera controls |
| **R51** | Linux V4L2 camera controls — [link](https://dri.freedesktop.org/docs/drm/media/uapi/v4l/ext-ctrls-camera.html) | Exposure units |
| **R52** | Arducam, minimum exposure time — [link](https://docs.arducam.com/UVC-Camera/Adjust-the-minimum-exposure-time/) | Exposure units |
| **R53** | DirectShow exposure table — [link](https://www.principiaprogramatica.com/2017/06/11/setting-manual-exposure-in-opencv/) | Windows exposure values |
| **R54** | SpellSight PR (V4L2 control names) — [link](https://github.com/mtaylor45/-SpellSight/pull/14) | Control names by kernel |
| **R70** | GitHub CLI Linux install — [link](https://github.com/cli/cli/blob/trunk/docs/install_linux.md) | README publish commands |
| **R73** | KaTeX — [katex.org](https://katex.org/) (loaded from cdn.jsdelivr.net) | Equations on the Pages site |
| **R81** | FluidNC web installer — [installer.fluidnc.com](https://installer.fluidnc.com/); install walkthrough — [Hackaday.io log](https://hackaday.io/project/194302-convert-a-mach3-cnc-controller-to-grbl-or-fluidnc/log/226954-installing-fluidnc) | Flashing steps |

## Considered and not used

| ID | Source | Used for |
|---|---|---|
| **R55** | grblHAL RP2040 — [SKR Pico map](https://github.com/grblHAL/RP2040/blob/master/boards/btt_skr_pico_10_map.h), [README](https://github.com/grblHAL/RP2040/blob/master/README.md) | Alternative firmware |
| **R56** | BTT SKR Pico — [BIQU](https://biqu.equipment/products/btt-skr-pico-v1-0) ($39.85) | Alternative board |
| **R57** | Klipper Config Reference — [link](https://www.klipper3d.org/Config_Reference.html) | First draft: firmware |
| **R58** | Moonraker printer API — [link](https://moonraker.readthedocs.io/en/latest/external_api/printer/) | First draft: host API |
| **R59** | KIAUH — [GitHub](https://github.com/dw-0/kiauh) | First draft: install |
| **R60** | Raspberry Pi overlays README — [link](https://github.com/raspberrypi/linux/blob/rpi-6.12.y/arch/arm/boot/dts/overlays/README) | First draft: I2C buses |
| **R61** | Raspberry Pi camera software — [link](https://www.raspberrypi.com/documentation/computers/camera_software.html) | First draft: camera |
| **R62** | Hackster, Raspberry Pi price rises — [link](https://www.hackster.io/news/raspberry-pi-hikes-prices-by-up-to-150-as-the-ai-bubble-hits-hard-confirms-raspberry-pi-6-plans-711d4384a4dd) | Decision to avoid buying compute |
| **R63** | PiShop Raspberry Pi 5 prices — [link](https://www.pishop.us/product-category/raspberry-pi/raspberry-pi-5/raspberry-pi-5-boards/) | Decision to avoid buying compute |
| **R64** | BTT SKR Mini E3 V3 — [BIQU](https://biqu.equipment/products/bigtreetech-skr-mini-e3-v2-0-32-bit-control-board-for-ender-3), [GitHub](https://github.com/bigtreetech/BIGTREETECH-SKR-mini-E3/tree/master/hardware/BTT%20SKR%20MINI%20E3%20V3.0) | First draft: controller |
| **R65** | MKS DLC32 — [eBay](https://www.ebay.com/itm/237008535637), [FluidNC #751](https://github.com/bdring/FluidNC/issues/751), [store](https://www.cnccontroller.store/mks-dlc32-v2-1-cnc-controller-with-ts24-touchscreen-32-bit-wifi-grbl-board/) | Alternative board |
| **R66** | BTT Rodent — [BIQU](https://biqu.equipment/products/bigtreetech-rodent), [Rat Rig](https://ratrig.com/products/bigtreetech-rat-rig-rodent-cnc-controller-tmc2160) | Alternative board |
| **R67** | MKS TinyBee — [store](https://makerparts3d.com/products/mks-tinybee-3d-printer-control-board-with-esp32-wifi), [GitHub](https://github.com/makerbase-mks/MKS-TinyBee), [FluidNC config](https://github.com/bdring/fluidnc-config-files/blob/main/official/MKS_TinyBee_1_XYZAB.yaml) | Alternative board |
| **R68** | ESP32-DevKitC-32E — [Grid Connect](https://www.gridconnect.com/products/esp32-devkitc-32e-wroom-module-development-kit) | DIY alternative |
| **R69** | BTT TMC2209 module — [BIQU](https://biqu.equipment/products/bigtreetech-tmc2209-stepper-motor-driver-for-3d-printer-board-vs-tmc2208) | DIY alternative |
| **R79** | Seeed XIAO ESP32S3 Sense — [link](https://www.seeedstudio.com/XIAO-ESP32S3-Sense-p-5639.html), [OV5640 add-on](https://www.seeedstudio.com/OV5640-Camera-for-XIAO-ESP32S3-Sense-With-Heat-Sink-p-5739.html) | Wireless camera alternative (rejected: autofocus) |
| **R80** | Freenove FNK0085 — [store](https://store.freenove.com/products/fnk0085); [espressif issue #10792](https://github.com/espressif/arduino-esp32/issues/10792) | Wireless camera alternative |
| **R82** | Mean Well STEP files FAQ — [link](https://meanwellpowersupplies.com/technical-articles/faq/where-to-find-mean-well-step-files-3d-files/) | Where Mean Well CAD lives |
| **R83** | grblHAL core settings and commands — [settings.h](https://github.com/grblHAL/core/blob/master/settings.h), [system.c](https://github.com/grblHAL/core/blob/master/system.c) | $10 report mask (bit 0 MPos, bit 4 Pn), $22 homing flags (enable, single-axis $HX, init lock, force origin), $23, $62 sleep, $100–$133; `$HX`/`$HA`, `$SLP` |
| **R84** | grblHAL Trinamic plugin — [Plugins_motor README](https://github.com/grblHAL/Plugins_motor/blob/master/README.md) | `M122 I` re-initialises the drivers after motor power returns; $14x current (mA), $15x microsteps, $21x hold current (%) |
| **R85** | grblHAL RP2040 driver: BTT SKR Pico 1.0 board map — [btt_skr_pico_10_map.h](https://github.com/grblHAL/RP2040/blob/master/boards/btt_skr_pico_10_map.h); [Web Builder](https://svn.io-engineering.com:8443/?driver=RP2040) | 4th axis (A) on the E driver with its own limit input (E0-stop) when N_AXIS > 3; aux outputs FAN1-3, HB, HE; TMC2209 on UART; no WiFi; USB VID 0x2E8A (pico-sdk stdio_usb) |
| **R86** | ESP32-S3-DevKitC-1 user guide (Espressif) — [docs.espressif.com](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide.html); safe-GPIO summary — [esp32.co.uk](https://esp32.co.uk/esp32-s3-devkitc-1-pinout/) | hub pin map: avoids strapping pins 0/3/45/46, USB 19/20, flash/PSRAM 26–37, UART0 43/44; RGB LED on 48 (v1.0) or 38 (v1.1) |

## Licences and publishing

| ID | Source | Used for |
|---|---|---|
| **R71** | SPDX license-list-data — [GitHub](https://github.com/spdx/license-list-data) | Licence texts in `LICENSES/` |
| **R72** | OSHWA certification — [certification.oshwa.org](https://certification.oshwa.org/) | Certification checklist |

## Parts: power and electrical

| ID | Source | Used for |
|---|---|---|
| **P1** | MEAN WELL GST60A24-P1J — [Mouser](https://www.mouser.com/ProductDetail/MEAN-WELL/GST60A24-P1J?qs=odmYgEirbwyH6XaEPxnETQ%3D%3D) | $19.40, STEP listing |
| **P2** | GST60A spec — [PDF](https://www.meanwell.com/Upload/PDF/GST60A/GST60A-SPEC.PDF); [MEAN WELL UK](https://www.meanwell.co.uk/power-supplies/external-power-supplies/gst60a-series) | Plug, efficiency, Level VI, UL |
| **P3** | GST60A24-P1J — [TRC](https://trcelectronics.com/products/mean-well-gst60a24-p1j), [Jameco](https://www.jameco.com/z/GST60A24-P1J-MEAN-WELL-24-Volt-2500mA-60-Watt-3-Wire-Regulated-Switching-Desktop-Power-Adapter-2-1mm-Plug-Level-VI_2224411.html), [Bravo](https://www.bravoelectro.com/gst60a24-p1j.html), [Digi-Key](https://www.digikey.com/en/products/detail/mean-well-usa-inc/GST60A24-P1J/7703715) | No-load power, price cross-check, cord sold separately |
| **P4** | Switchcraft 721A — [product](https://www.switchcraft.com/dc-power-jack-0-084-2-1mm-pin-solder-lugs-termination/721a/) | 2.1 mm, 5 A / 24 V · not used since the no-solder, no-drill build |
| **P5** | Switchcraft 721A — [Octopart](https://octopart.com/721a-switchcraft-89444436), [Digi-Key](https://www.digikey.com/en/products/detail/switchcraft-inc/721A/8571716) | $4.03 · not used since the no-solder, no-drill build |
| **P6** | Littelfuse 01500274ZXU — [Mouser](https://www.mouser.com/ProductDetail/Littelfuse/01500274ZXU?qs=HS3fcsxbgMwxzHo3fy8LGg%3D%3D) | $3.27; body 47.5 ± 1 mm × Ø11.0 mm, 16 AWG leads 330 mm ([Littelfuse drawing](https://www.farnell.com/datasheets/2259214.pdf), checked 2026-10-14) |
| **P7** | Infineon IRF4905PBF — [Mouser](https://www.mouser.com/ProductDetail/Infineon-Technologies/IRF4905PBF?qs=9%2BKlkBgLFf39l0HsWdxvdw%3D%3D) | $2.73 · not used since the no-solder, no-drill build |
| **P8** | IRF4905 — [datasheet](https://www.infineon.com/dgdl/irf4905pbf.pdf?fileId=5546d462533600a4015355e329b1197e), [Digi-Key](https://www.digikey.com/en/products/detail/infineon-technologies/IRF4905PBF/812139), [SnapEDA](https://www.snapeda.com/parts/IRF4905PBF/Infineon/view-part/) | Rds(on), Vgs · not used since the no-solder, no-drill build |
| **P9** | onsemi 1N4742A — [Mouser](https://www.mouser.com/ProductDetail/onsemi/1N4742A?qs=SSucg2PyLi71ahupZUxJzg%3D%3D) | $0.28 · not used since the no-solder, no-drill build |
| **P10** | P6KE30A (Littelfuse via Verical, chosen; ST at Mouser compared) — [Mouser](https://www.mouser.com/ProductDetail/STMicroelectronics/P6KE30A?qs=5Uvc6lfWVJxhgPKxz%252Bj4DQ%3D%3D), [Octopart](https://octopart.com/p6ke30a-littelfuse-348661) | $0.94 · not used since the no-solder, no-drill build |
| **P11** | Nichicon UFW1H101MPD1TD — [Mouser](https://www.mouser.com/ProductDetail/Nichicon/UFW1H101MPD1TD?qs=WJSLByB5Mu30jPPJ2KiG3A%3D%3D) | $0.59 · not used since the no-solder, no-drill build |
| **P12** | Vishay BAT85S-TAP — [Mouser](https://www.mouser.com/ProductDetail/Vishay-Semiconductors/BAT85S-TAP?qs=yIvl1B2wDi5bZOHuqaPTHw%3D%3D) | Considered for the sense clamp (replaced by an optocoupler) |
| **P13** | Bulgin C1353ABNAB — [Digi-Key](https://www.digikey.com/en/products/detail/bulgin/C1353ABNAB/9598373) | 10 A DC rating · not used since the no-solder, no-drill build |
| **P14** | Arcolectric C1300ALAAA — [Newark](https://www.newark.com/arcolectric-bulgin-limited/c1300alaaa/rocker-switch-spst-on-off-black/dp/48W5536), [Octopart](https://octopart.com/part/arcolectric/C1300ALAAA) | Rocker alternative |
| **P15** | IDEC YW1B-V4E01R — [TME](https://www.tme.com/us/en-us/details/yw1b-v4e01r/panel-mount-switches-standard-22mm/idec/) | $9.96 |
| **P16** | IDEC YW series — [datasheet](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6163/D004450YWapem.pdf) | DC ratings |
| **P17** | Eaton M22-PV / M22-K01 — [IMC](https://www.imc-direct.com/product_p/m22-pv.htm), [TME](https://www.tme.com/us/en-us/details/m22-k01/panel-mount-accessories/eaton-electric/), [IMC kit](https://www.imc-direct.com/product_p/m22-pv-k01.htm), [Mouser](https://www.mouser.com/en/ProductDetail/Eaton-Electrical/M22-PV-K01?qs=HFfMDpzxxd0QRHbJBijxWA%3D%3D) | E-stop price comparison |
| **P18** | AMASS XT30U — [rcbattery](https://rcbattery.com/genuine-amass-xt30u-male-female-pair-plugs-5-pairs.html) | $2.19 / 5 pairs · not used since the no-solder, no-drill build |
| **P19** | realthunder/Connectors_Amass.3dshapes — [GitHub](https://github.com/realthunder/Connectors_Amass.3dshapes) | XT30 STEP · not used since the no-solder, no-drill build |
| **P20** | 18 AWG silicone pair — [Walmart](https://www.walmart.com/ip/2-Conductor-Parallel-Silicone-Wire-18AWG-18-Gauge-Red-Black-Electrical-Wire-Tinned-Copper-1m-3-3ft/2401235173), [BNTECHGO](https://www.amazon.com/BNTECHGO-Silicone-Flexible-Strands-Stranded/dp/B01AQOI36M) | $8.09 |
| **P21** | Adafruit perfboard 4783 — [link](https://www.adafruit.com/product/4783) | $2.25 · not used since the no-solder, no-drill build |
| **P22** | Keszoox JST-XH kit — [Amazon](https://www.amazon.com/Keszoox-Connector-Pre-Crimped-Housing-Socket%EF%BC%8810/dp/B09SX4LC13) | Listing (price not confirmed) |
| **P23** | Schneider XB5AS8442 — [TME](https://www.tme.com/us/en-us/details/xb5as8442/panel-mount-switches-standard-22mm/schneider-electric/), [RSP Supply](https://rspsupply.com/p-83740-schneider-electric-xb5as8442-red-40-emergency-stop-switching-off-pushbutton-22-latching-turn-release.aspx); XB2BS542C — [LCSC](https://www.lcsc.com/product-detail/Pushbutton-Switches_Schneider-XB2BS542C_C5122145.html) | Rejected (0.5 A DC-13) |
| **P24** | Omron A22E-M-01 — [Octopart](https://octopart.com/a22e-m-01-omron-35187) | Rejected (price) |
| **P25** | Pololu rocker #1406 — [link](https://www.pololu.com/product/1406) | Rejected (AC only) |
| **P26** | CW Industries GRB112B802BR1 — [Octopart](https://octopart.com/grb112b802br1-cw+industries-19058098) | Rejected (14 V DC) |
| **P27** | Switchcraft 722A — [Mouser](https://www.mouser.com/ProductDetail/Switchcraft/722A?qs=MI16PYk8XEPiQCOy7frM9Q%3D%3D) | Rejected (2.0 mm pin) |
| **P28** | Same Sky PJ-002BH — [link](https://www.sameskydevices.com/product/interconnect/connectors/dc-power-connectors/jacks/pj-002bh) | Rejected (2.5 mm pin) |
| **P29** | Same Sky PJ-009A — [Octopart](https://octopart.com/part/same-sky/PJ-009A) | Rejected (2.5 A) |
| **P30** | GST90A24-P1M — [Jameco](https://www.jameco.com/z/GST90A24-P1M-MEAN-WELL-24-Volt-3750mA-90-Watt-3-Wire-Regulated-Switching-Desktop-Power-Adapter-2-5mm-Plug-Level-VI_2223494.html), [Digi-Key](https://www.digikey.com/en/products/detail/mean-well-usa-inc/GST90A24-P1M/7703720) | Comparison |
| **P31** | GST120A24-P1M (first draft) — [Mouser](https://www.mouser.com/en/ProductDetail/MEAN-WELL/GST120A24-P1M?qs=V113mesSgrhUmhAWUz3R2A%3D%3D), [TRC](https://www.trcelectronics.com/products/mean-well-gst120a24-p1m), [spec](https://www.meanwell.com/Upload/PDF/GST120A/GST120A-SPEC.PDF) | First draft: supply |
| **P32** | Pololu regulators (first draft) — [D42V55F5](https://www.pololu.com/product/5571), [D42V55F5.3](https://www.pololu.com/product/5572), [D36V50F5](https://www.pololu.com/product/4091), [resources/STEP](https://www.pololu.com/product/4091/resources), [D24V50F5](https://www.pololu.com/product/2851) | First draft: 5 V rail (removed: no Pi) |
| **P33** | Same Sky PJ-005B (first draft) — [Digi-Key](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/PJ-005B/172263), [datasheet](https://www.sameskydevices.com/product/resource/pj-005b.pdf), [Octopart](https://octopart.com/part/same-sky/PJ-005B); Switchcraft 712A — [Newark](https://www.newark.com/switchcraft/712a/connector-dc-power-jack-5a/dp/37F2993) | First draft: jack |
| **P34** | Littelfuse (first draft) — [03455LS1H](https://www.newark.com/littelfuse/03455ls1h/fuse-holder-5-x-20mm-panel-mount/dp/67K0280), [021806.3MXP](https://www.newark.com/littelfuse/021806-3mxp/fuse-cartridge-6-3a-5x20mm-slow/dp/42K9390), [03453LS1H](https://www.digikey.com/en/products/detail/littelfuse-inc/03453LS1H/553765) | First draft: fuse |
| **P35** | Jameco SRC1-1B-DC-1-B (first draft) | Rejected (momentary) |
| **P40** | StepperOnline 17HS19-2004S1 — [product](https://www.omc-stepperonline.com/nema-17-bipolar-59ncm-84oz-in-2a-42x48mm-4-wires-w-1m-cable-connector-17hs19-2004s1), [datasheet](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1_Full_Datasheet.pdf), [STEP](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) | $9.62, coil data |
| **P41** | Kingroon GT2 closed belts — [link](https://kingroon.com/products/gt2-closed-loop-timing-belt-rubber-2gt-6mm-3d-printers-parts-110-112-122-158-200-280-300-400-610-852-mm-synchronous-belts) | $1.88 |
| **P42** | ZYLtech GT2 20T pulley — [link](https://www.zyltech.com/2gt-gt2-6mm-wide-20t-pulley-5mm-6-35mm-or-8mm-bore/) | $2.95 |
| **P43** | TCST2103 optical endstop — [eBay](https://www.ebay.com/itm/182778778905) | $2.93 |
| **P44** | ZYLtech GT2 belt per metre — [link](https://www.zyltech.com/fiber-glass-reinforced-2gt-gt2-timing-belt-custom-length-price-per-meter/) | $2.50/m |
| **P45** | Adafruit 368 DC jack to screw terminal — [product](https://www.adafruit.com/product/368) | $2.00, + / − marked, centre-positive |
| **P46** | Adafruit 64 half-size breadboard — [product](https://www.adafruit.com/products/64) | 400 points, solderless |
| **P47** | WAGO 221 lever connectors, 28-piece assortment — [Amazon](https://www.amazon.com/dp/B01N0LRTXZ), [price seen $15.71](https://slickdeals.net/f/18335398-28-piece-wago-221-lever-nuts-splicing-wire-connector-assortment-w-case-15-71-free-shipping-w-prime) | Solderless joins |
| **P48** | StepperOnline 17HS08-1004S pancake NEMA 17 — [product](https://www.omc-stepperonline.com/hybrid-stepper-motor/nema-17-bipolar-18deg-13ncm-184ozin-1a-35v-42x42x20mm-4-wires-17hs08-1004s.html) | $7.99, 21.5 mm body, 16 N·cm, 1 A, 5 mm D-shaft |
| **P49** | Xeanerol 24 V 5 Ah Li-ion pack with 2 A charger (YX-DIY-24-50) — [Amazon](https://www.amazon.com/dp/B0FHPST5TP) | $41.99 (checked 2026-10-12); label input 25.2 V 2 A, output 22–25 V 10 A max; 78 × 50 × 72 mm |
| **P50** | DROK buck-boost converter 6–36 V to 0.6–36 V, 5 A 80 W, LCD — [Amazon](https://www.amazon.com/dp/B0BQBXMH67) | $22.99 (checked 2026-10-12); 78.6 × 42.7 × 38.6 mm; LVP, OCP, power-on state, lock; 88 % efficiency (listing) |
| **P51** | MEAN WELL RSD-60G-24 DC-DC converter — [Digi-Key](https://www.digikey.com/en/products/detail/mean-well-usa-inc/RSD-60G-24/7706259), [3D model](https://www.meanwell.com/upload/pdf/RSD-60/RSD-60-3D.zip) | $43.70 (checked 2026-10-12); 9–36 V in, 24 V 2.5 A, 90 %, 128 × 60 × 25 mm |
| **P52** | Phoenix Contact UT 4-HESI (5X20) fuse terminal block 3046032 — [Digi-Key](https://www.digikey.com/en/products/detail/phoenix-contact/3046032/2051197), [Phoenix Contact](https://www.phoenixcontact.com/en-us/products/fuse-terminal-block-ut-4-hesi-5x20-3046032) | $5.56; 6.2 × 57.8 × 75.6 mm on NS 35/7.5; CAD download on both pages |
| **P53** | Phoenix Contact PLC-RSC- 24DC/21AU relay module 2966265 — [Digi-Key](https://www.digikey.com/en/products/detail/phoenix-contact/2966265/349708), [Phoenix Contact](https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21au-2966265) | $19.64; 6.2 × 80 × 94 mm; hard-gold contact, min. 1 mA at 24 V; CAD download on both pages |
| **P54** | INIU 20000 mAh 65 W laptop power bank — [Amazon](https://www.amazon.com/dp/B0DB86W481) | $46.99 (checked 2026-10-13); 73 Wh, 109 × 71 × 28 mm, 12 cm USB-C cable |
| **P55** | USB-C PD trigger board, DIP 5–20 V, LED display, screw terminals — [Amazon](https://www.amazon.com/dp/B0HHNFY7HT) | $9.99 (checked 2026-10-13); falls back to 5 V if 20 V is not offered |
| **P56** | MEETOOT 22 mm emergency stop, 1 NO + 1 NC, 2-pack — [Amazon](https://www.amazon.com/dp/B09JP4JKY6) | $8.99 (checked 2026-10-13); 40 mm head, 60 × 70 mm max |
| **P57** | DROK buck-boost 5.5–30 V, 4 A 35 W, CC/CV, LCD — [Amazon](https://www.amazon.com/dp/B07VNDGFT6) | $16.99 (checked 2026-10-12); 72 × 59 × 32 mm with case ([DROK product page](https://www.droking.com/Adjustable-Buck-Boost-Converter-Board-DC-5.5-30V-to-0.5-30V-4A-High-Power-Supply-Regulator-with-Case-LCD-Display), checked 2026-10-14); CV + CC pots, display in/out V, A, W; reverse-input and output anti-backflow protection |
| **P58** | SIMAX3D 17HS4401 NEMA 17, 5-pack — [Amazon](https://www.amazon.com/dp/B088B756MY) | $32.99 (checked 2026-10-14); 1.5 A, 42 N·cm, 42 × 42 × 38 mm, 4-wire, five 1 m cables |
| **P59** | ALITOVE 24 V 3 A 72 W AC/DC adapter with 5.5 × 2.1 mm screw-terminal jack — [Amazon](https://www.amazon.com/dp/B078RY7BPL) | $17.85 (checked 2026-10-23, in stock); FCC / CE / RoHS; short-circuit, overload and over-temperature protection; AC cable ~120 cm, DC cable ~110 cm |
| **P60** | BAOMAIN Red Sign E-Stop station, 1 NO + 1 NC, IP65 box — [Amazon](https://www.amazon.com/dp/B00NTT91Y0) | $8.99 (checked 2026-10-22, in stock); latching, press to stop, rotate to reset; contacts 660 V / 10 A (AC) |
| **P61** | Joinfworld IP67 sealed roller-lever microswitch, SPDT, pre-wired, 2-pack — [Amazon](https://www.amazon.com/dp/B09VGL29HS) | $9.88 (checked 2026-10-30, in stock); 6 A at 12 V DC or 5 A at 250 V AC; lever removable |
| **P62** | WAGO 221 Lever-Nuts 12-piece assortment with case — [Amazon](https://www.amazon.com/dp/B0CJ5QF4Z2) | $12.45 (checked 2026-11-01, in stock); 3 × 221-2401, 3 × 221-412, 3 × 221-413, 3 × 221-415 |
| **P63** | WAGO 221 sizes from distributor pages — 221-412: [Core Electronics](https://core-electronics.com.au/wago-2-conductor-lever-inline-connector-221-2401.html) (13.1 × 8.3 × 18.7 mm); 221-413: [Altex](https://altex.com/collections/connectors-adapters/products/wago-221-413-24-12awg-3-conductor-compact-splicing-connector) (8.3 × 18.7 × 18.6 mm); 221-415: [Powermatic](https://www.powermatic.net/part/wago/221-415/1422237) (30 × 8.6 × 18.8 mm); 221-2401: [RS](https://uk.rs-online.com/web/p/splice-connectors/0303327) (35.5 mm long) | Read 2026-11-03; strip 11 mm; 0.2–4 mm² (221-41x also 0.14 mm² fine-stranded). The Core Electronics page is titled 221-2401 but lists 221-412 data |
| **P64** | BAOMAIN e-stop listing copy — [desertcart](https://www.desertcart.nz/products/30687541) | Read 2026-11-03: 2.8 × 2.8 × 3.4 in, 150 g, 1 NO + 1 NC 660 V / 10 A, IP65. A reseller copy of an Amazon listing; that it is B00NTT91Y0 is not shown: measure yours (M04.2) |
| **P65** | Espressif ESP32-S3-DevKitC-1 board size — [Electrokit](https://www.electrokit.com/en/esp32-s3-devkitc-utvecklingskort-8mb-pram-8mb) | Read 2026-11-03: 62.74 × 25.4 mm. Espressif's own drawing: [user guide v1.1](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html) (DXF linked there) |

## Parts: controller

| ID | Source | Used for |
|---|---|---|
| **C1** | FYSETC E4 — [GitHub README](https://github.com/FYSETC/FYSETC-E4), [schematic](https://github.com/FYSETC/FYSETC-E4/blob/main/hardware/FYSETC%20E4_V1.0%20SCH.pdf), [hardware](https://github.com/FYSETC/FYSETC-E4/tree/main/hardware) | Pin map, specs |
| **C2** | FYSETC E4 wiki — [link](https://wiki.fysetc.com/docs/E4) | Drivers, CH340, size |
| **C3** | FYSETC E4 store — [link](https://www.fysetc.com/products/fysetc-e4-board-with-built-in-wi-fi-and-bluetooth-4-pcs-tmc2209-240mhz-16m-flash-3d-printer-control-board-based-for-3d-printer) | $32.00 |
| **C4** | E4 listings — [AliExpress 1](https://www.aliexpress.com/item/1005001703930983.html), [AliExpress 2](https://www.aliexpress.com/item/1005001704413148.html), [Amazon.ca](https://www.amazon.ca/Compatible-Bluetooth-TMC2209-Printer-Control/dp/B0FDWPRKS5) | Availability |
| **C5** | Raspberry Pi Pico — [product](https://www.raspberrypi.com/products/raspberry-pi-pico/), [SparkFun](https://www.sparkfun.com/raspberry-pi-pico.html) | $4.00 |
| **C6** | Pico files — [STEP](https://datasheets.raspberrypi.com/pico/Pico-R3-step.zip), [pinout](https://datasheets.raspberrypi.com/pico/Pico-2-Pinout.pdf), [datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf), [docs](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) | CAD, pins |
| **C7** | Adafruit USB cables — [4474](https://www.adafruit.com/product/4474), [898](https://www.adafruit.com/product/898) | Cable prices |
| **C8** | Raspberry Pi Pico H (headers soldered) — [Adafruit 5525](https://www.adafruit.com/product/5525), [Jameco](https://www.jameco.com/z/5525-Adafruit-Industries-Raspberry-Pi-Pico-H-Pico-with-Headers-Soldered_2882023.html) | No soldering |
| **C9** | Adafruit 1332 membrane 1x4 keypad — [product](https://www.adafruit.com/product/1332) | Panel keys |
| **C10** | Adafruit 1954 male/female jumper wires 20 x 6 in — [product](https://www.adafruit.com/product/1954), [Jameco](https://www.jameco.com/z/1954-Adafruit-Industries-Premium-Female-Male-Extension-Jumper-Wires-20-X-6_2507535.html) | Solderless leads |
| **C11** | Stepper cable PH2.0 6-pin to XH2.54 4-pin, 1 m — [Jameco 2333607](https://www.jameco.com/z/JST-PH20-XH4P-Jameco-ValuePro-4-Wire-Stepper-Motor-Cable-4-Pin-Series-PH-2mm-to-6-Pin-XH2-2-54mm-1-Meter_2333607.html) | $1.95, closeout |
| **C12** | BIGTREETECH SKR Pico V1.0 — [Amazon](https://www.amazon.com/dp/B09MYKL9MP), [GitHub: manual, STEP, pins](https://github.com/bigtreetech/SKR-Pico) | $35.99 (checked 2026-10-14); RP2040, 4 × TMC2209 UART, USB-C, DC 12/24 V, 85 × 56 mm, 4 × Ø2.7 holes on 58 × 49 mm (measured from the maker STEP); fan advised above 0.8 A per motor; flashing: BOOT jumper + reset, copy the .uf2 |
| **C13** | ESP32-S3-DevKitC-1 (owned) — MicroPython firmware [ESP32_GENERIC_S3](https://micropython.org/download/ESP32_GENERIC_S3/) | button + sensor hub (replaces the Pico H); USB-C; see R86 for pins |

## Parts: camera

| ID | Source | Used for |
|---|---|---|
| **K1** | Arducam B0433 (IMX477 USB, M12) — [product](https://www.arducam.com/12mp-usb-camera-module-with-m12-lens-1-2-3-3840hx3032v-4k30fps-for-windows-linux-macos-and-android.html) | $59.99, controls |
| **K2** | Arducam UVC selection guide — [link](https://docs.arducam.com/UVC-Camera/USB2-UVC-Camera-Kit/Specs-and-Selection-Guide/) | Sensor = IMX477 |
| **K3** | B0433 datasheet — [PDF](https://www.uctronics.com/download/Amazon/B0433_Arducam_12MP_USB_Camera_Module_Datasheet.pdf) | Mechanical drawing |
| **K4** | Arducam B0446 (IMX179) — [product](https://www.arducam.com/8mp-imx179-usb-camera-module-with-wide-angle-115h-m12-lens-for-windows-linux-android-and-mac-os.html) | Fallback ($54.99, manual WB) |
| **K5** | VA Imaging 16 mm M12 lens — [link](https://va-imaging.com/en-us/products/lens-m12-5mp-16mm-f2-0-1-2-va-lm12-5mp-16mm-f2-0-020) | $21.00 |
| **K6** | Arducam forum, B0433 exposure via v4l2 — [link](https://forum.arducam.com/t/b0433-camera-unable-to-change-exposure-time-from-v4l2/7522) | Discard frames after a change |
| **K23** | SparkFun M2.5 x 8 mm Phillips machine screw — [product](https://www.sparkfun.com/m2-5-0-45x8mm-machine-screw-phillips-head.html) | $0.15 each |
| **K7** | Arducam forum, IMX477 UVC max exposure — [link](https://forum.arducam.com/t/arducam-imx477-uvc-camera-adapter-board-max-exposure-time/1387) | ~0.5 s limit |
| **K8** | Arducam forum, IMX477 USB 12-bit — [link](https://forum.arducam.com/t/imx477-usb-12bit-capabilities/2466) | No RAW over UVC |
| **K9** | Arducam USB3.0 Camera Shield Plus — [link](https://docs.arducam.com/USB-Industrial-Camera/USB3.0-Camera-Shield-Plus/USB3.0-Camera-Shield-Plus-Datasheet/) | RAW option (SDK) |
| **K10** | Arducam B0459 — [link](https://www.arducam.com/arducam-12mp-usb-3-0-camera-with-m12-manual-focus-lens.html) | Step-up option |
| **K11** | Arducam B0280 — [link](https://www.arducam.com/arducam-high-quality-complete-usb-camera-bundle-12mp-1-2-3-inch-imx477-camera-module-with-6mm-cs-mount-lens-metal-enclosure-tripod-and-usb-cable-b0280.html) | Compared |
| **K12** | ELP IMX179 — [link](http://www.webcamerausb.com/elpusb30w04mtl36-p-149.html) | Compared |
| **K13** | Arducam B0304 IMX708 — [link](https://www.uctronics.com/12mp-imx708-usb-uvc-fixed-focus-camera-module-3.html) | Compared |
| **K14** | Arducam B0362 IMX291 — [link](https://www.arducam.com/arducam-imx291-usb-camera-with-2-8-12mm-lens-b0362.html) | Compared |
| **K15** | TraceParts Arducam models — [link](https://www.traceparts.com/en/search/arducam-usb-uvc-camera?CatalogPath=ARDUCAM_1206236589:ARDUCAM.020) | CAD search |
| **K16** | Arducam forum, 3D model request — [link](https://forum.arducam.com/t/searching-for-3d-model-of-b0202/809) | CAD search |
| **K17** | InnoMaker IMX298 USB — [Amazon](https://www.amazon.com/InnoMaker-4656x3496-Detection-Auto-Focus-Raspberry/dp/B0G2VZP6SL) | Rejected (autofocus) |
| **K18** | Commonlands CIL160 16 mm — [link](https://commonlands.com/products/16mm-m12-lens) | Lens upgrade |
| **K19** | Raspberry Pi HQ Camera (first draft) — [CS](https://www.pishop.us/product/raspberry-pi-hq-camera-cs/), [M12](https://www.pishop.us/product/raspberry-pi-hq-camera-m12/), [brief](https://pip-assets.raspberrypi.com/categories/659-raspberry-pi-high-quality-camera/documents/RP-008202-DS-1-hq-camera-product-brief.pdf), [M12 drawing](https://pip-assets.raspberrypi.com/categories/659-raspberry-pi-high-quality-camera/documents/RP-008201-DS-1-hq-camera-m12-mechanical-drawing.pdf) | First draft: camera |
| **K20** | Raspberry Pi Camera Module 3 (first draft) — [PiShop](https://www.pishop.us/product/raspberry-pi-camera-module-3/), [STEP](https://pip-assets.raspberrypi.com/categories/1207-design-files/documents/RP-008154-DS-1-camera-module-3-step.zip) | First draft: fallback |
| **K21** | Pi 5 camera cable (first draft) — [PiShop](https://www.pishop.us/product/camera-cable-for-raspberry-pi-5/) | First draft: |
| **K22** | Arducam LN036 (first draft) — [link](https://www.arducam.com/arducam-telephoto-20-degree-1-2-3-m12-mount-with-lens-adapter-for-raspberry-pi-high-quality-camera.html) | First draft: lens note |

## Parts: light

| ID | Source | Used for |
|---|---|---|
| **L1** | Cree CXA1304-0000-000C0Y9430H — [Mouser](https://www.mouser.com/ProductDetail/Cree-LED/CXA1304-0000-000C0Y9430H?qs=G0uBbFPHMulh2b3olRHR4A%3D%3D) | $2.66, CRI 93, 9 V |
| **L2** | Luminus CXM-4 Gen 4 — [datasheet](https://download.luminus.com/datasheets/Luminus_CXM-4_GEN4_Datasheet.pdf) | 18 V class, CRI 95 options |
| **L3** | CXM-4 availability — [Octopart CXM-4-30-95-18](https://octopart.com/part/luminus-devices/CXM-4-30-95-18-AC40-F5-3), [Mouser -50-95-18](https://www.mouser.com/ProductDetail/Luminus-Devices/CXM-4-50-95-18-AC40-F5-3?qs=DPoM0jnrROW%252BbPFMtDMVfQ%3D%3D), [Mouser -30-90-18](https://www.mouser.com/en/ProductDetail/Luminus-Devices/CXM-4-30-90-18-AC40-F5-3?qs=DPoM0jnrROVkRRFTMvUU3g%3D%3D), [Digi-Key -27-80-18](https://www.digikey.com/en/products/detail/luminus-devices-inc/CXM-4-27-80-18-TE60-F7-2/21348065) | Preferred-if-stocked option |
| **L4** | MEAN WELL NLDD-350H — [Power Supply Mall](https://powersupplymall.com/products/mean-well-nldd-350h-dc-dc-led-driver-cc-350ma-step-down) | $4.81 |
| **L5** | NLDD-350H — [TRC](https://trcelectronics.com/products/mean-well-nldd-350h) | $5.55, ranges |
| **L6** | NLDD-H spec — [PDF](https://www.meanwell.com/Upload/PDF/NLDD-H/NLDD-H-SPEC.PDF) | Efficiency, DIM |
| **L7** | Easycargo 40 mm heatsinks — [Amazon](https://www.amazon.com/Easycargo-40x40x11mm-TEC1-12706-Thermoelectric-40mmx40mmx11mm/dp/B07WR7MPB1) | Listing |
| **L8** | Yuji LEDs — [HD5 CRI 95](https://store.yujiintl.com/products/yujileds-cri-95-5mm-9w-cob-led-2700k-3200k-4000k-hd5), [CRI 98 9 W](https://store.yujiintl.com/products/yujileds-cri-98-9w-cob-led-135l) | High-CRI upgrade |
| **L9** | Luminus CXM-9 (first draft) — [datasheet](https://download.luminus.com/datasheets/Luminus_CXM-9_GEN6_Datasheet.pdf), [Mouser](https://www.mouser.com/ProductDetail/Luminus-Devices/CXM-9-30-95-36-AA00-F2-3?qs=Qlzq7FOrON4Xiqce7VRkYw%3D%3D) | Rejected (36 V) |
| **L10** | Bridgelux Vero SE 13 Thrive — [datasheet](https://www.bridgelux.com/sites/default/files/resource_media/Bridgelux%20DS346%20Gen%207%20Vero%20SE%2013%20Thrive%20Array%20Datasheet%20RevA%2020220331.pdf) | Compared |
| **L11** | LEDiL C13658 clamp — [Digi-Key](https://azcus.digikey.com/en/products/detail/ledil/C13658-CLAMP-VERO13-18/4490851) | Compared |
| **L12** | LEDSupply heatsinks — [link](https://www.ledsupply.com/led-housing-heatsinks) | Compared |
| **L13** | MEAN WELL LDD-H — [LEDSupply](https://www.ledsupply.com/led-drivers/mean-well-ldd-h-series-cc-step-down-mode); [LDD-700H Octopart](https://octopart.com/ldd-700h-mean+well-20023764) | First draft: driver |
| **L14** | NLDD-350H — [RapidLED](https://rapidled.com/products/mean-well-ldd-350h-dimmable-driver) | First draft: price |
| **L15** | LEDiL ANGELA-S — [Digi-Key](https://www.digikey.com/en/products/detail/ledil/F13379-ANGELA-S/4946614) | Optic option |
| **L16** | LEDiL Angelina — [cobkits](https://cobkits.com/product/ledil-angelina-reflector-f13838-for-ideal/) | Rejected (90 deg) |
| **L17** | Generic COB reflector — [Amazon](https://www.amazon.com/10W-100W-Adapter-Reflector-Collimator-Bracket/dp/B00VSNYNCY) | Compared |
| **L18** | Cree CXA1507 — [Newark](https://www.newark.com/cree-led/cxa1507-0000-000n0ye230g/led-array-cob-warm-wht-3000k-590lm/dp/49AC0147) | Rejected (35 V) |
| **L19** | 24 V COB strip CRI 90 — [ledupdates](https://ledupdates.com/products/24v-cob-series-cri-90-4000k-natural-white-color-led-strip-light) | Rejected (roll price) |
| **L20** | Edmund XP42 polarizer film — [link](https://www.edmundoptics.com/p/100-x-100mm-linear-polarizing-film-xp42-40/52988/) | Compared |
| **L21** | Molex SlimRay CXA13 holders 180555-0001 (110 mm leads) / -0002 (254 mm leads), pre-wired, no solder — [Mouser](https://www.mouser.com/new/molex/molex-slimray-cxa13-led-holders), [Euroimpex](https://euroimpex.krakow.pl/product/details/180555-0001) | First-draft COB holder: obsolete at Digi-Key (checked 2026-10-10) |
| **L22** | Citizen CLU7A3-0403E1-303H7X5 — [Digi-Key](https://www.digikey.com/en/products/detail/citizen/CLU7A3-0403E1-303H7X5/17053751), [datasheet](https://ce.citizen.co.jp/cms/ce/lighting_led/dl_data/COB_High_Intensity_Type_Version4/datasheet/CLU7A3-0403E1_0824P-202110.pdf) | White COB: $5.91, CRI 97, 12.2 V, 4.2 mm LES, Tc ≤ 120 °C |
| **L23** | TE LUMAWISE Z35 2213678-5 — [Digi-Key](https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/2213678-5/6174915), [Z35 overview](https://www.digikey.com/en/product-highlight/t/te-connectivity-amp/lumawise-led-holders-type-z35) | Solderless COB holder: $3.50, 13.5 mm boards (Citizen CLU700), Ø35 × 3.6 mm, poke-in 18–20 AWG |
| **L24** | MEAN WELL LDH-45B-350 — [Digi-Key](https://www.digikey.com/en/products/detail/mean-well-usa-inc/LDH-45B-350/7704773), [spec](https://files.trcelectronics.com/datasheets/ldh45.pdf) | Compared: 24 V boost driver for a 37 V COB; not needed with the 12 V CLU7A3 |
| **L25** | Citizen CLU701-0303C4-273H5K2 — [Digi-Key](https://www.digikey.com/en/products/detail/citizen/CLU701-0303C4-273H5K2/5820601), [datasheet](https://www.endrich.com/sixcms/media.php/2/CLU701-0303C4_0035P_201710.pdf) | White COB (bought): 13.5 × 13.5 × 1.4 mm, Vf 8.6 / 9.4 / 10.2 V at 525 mA, max 690 mA, Tc ≤ 105 °C, Rj-c 3.5 °C/W, H5 = Ra ≥ 90 |
| **L26** | TE 114-32208 Rev F, LUMAWISE holder cross-reference — [PDF](https://www.mouser.lt/pdfDocs/ENG_SS_114-32208_F.pdf) | Lists Citizen CLU701 for the Z35 2213678-5 |
| **L27** | MEAN WELL NLDD-350HW — [Digi-Key](https://www.digikey.com/en/products/detail/mean-well-usa-inc/NLDD-350HW/13913611), [NLDD-H spec](https://www.meanwell.com/Upload/PDF/NLDD-H/NLDD-H-SPEC.PDF) | Wire-lead driver (bought): 32.1 × 20.5 × 12.5 mm, 22 AWG leads 100 mm, input 10–56 V, DIM open = on |
| **L28** | Wakefield 910-40-2-12-2-B-0 — [Digi-Key](https://www.digikey.com/en/products/detail/wakefield-thermal-solutions/910-40-2-12-2-B-0/4815166), [maker page](https://wakefieldthermal.com/wakefield-thermal-heatsink-40x40x12mm-pin-910-40-2-12-2-b-0/), [Octopart](https://octopart.com/part/wakefield-vette/910-40-2-12-2-B-0) | Pin-fin heatsink (bought): 40 × 40 × 11.6 mm, 9.2 °C/W natural convection, clip mount (no tape) |
| **L29** | 3M 8810 tape 19 mm × 4.57 m — [Digi-Key](https://www.digikey.com/en/products/detail/3m-tc/8810-0-75-5/2649863) | Thermal adhesive transfer tape, COB to heatsink |
| **L30** | Waveshare 2inch LCD Module (SKU 17344) — [maker page](https://www.waveshare.com/2inch-LCD-Module.htm), [wiki](https://www.waveshare.com/wiki/2inch_LCD_Module), [Amazon](https://www.amazon.com/dp/B081Q79X2F) | Status screen: ST7789VW, 240 × 320, 58 × 35 mm, PH2.0 8-pin, 20 cm cable in the box |

## Parts: mechanics and frame

| ID | Source | Used for |
|---|---|---|
| **M1** | Bear Woods LZ-12 — [link](https://www.bearwood.com/en-us/products/12-round-lazy-susan-turntable-bearings) | $13.90 |
| **M2** | VXB 12 in aluminium turntable — [link](https://vxb.com/products/12-inch-aluminum-lazy-susan-turntable-bearing) | Upgrade |
| **M3** | KW12-3 roller micro switches — [Walmart](https://www.walmart.com/ip/10Pcs-Roller-Lever-Arm-Open-Close-Limit-Switch-Kw12-3-Pcb-Microswitch/1344341711) | $7.00 / 10 |
| **M4** | Woodpeckers bearings — [12C](https://woodpeckerscrafts.com/products/12c-ls-bearing), [4 in](https://woodpeckerscrafts.com/products/4c-ls-bearing) | Compared |
| **M5** | VXB 12 in steel, VXB 4 in — [12 in](https://vxb.com/products/12-inch-lazy-susan-bearing-1000lb-usa), [4 in](https://vxb.com/products/300-lbs-capacity-4-lazy-susan-bearing-5-16-thick-t) | Compared |
| **M6** | 3 x 3 in turntable (McMaster 6031K16) — [RobotShop](https://www.robotshop.com/en/3x3-ball-bearing-turntable.html) | Corrected first-draft assumption |
| **M7** | VXB bearings — [608 10-pack](https://vxb.com/products/10-pack-skateboard-bearing-608-2rs-sealed-8x22x7mm), [6806](https://vxb.com/products/6806-2rs-bearing-30x42x7-sealed) | Compared |
| **M8** | TNutz LF-015-A foot — [link](https://www.tnutz.com/product/lf-015-a/) | First draft: feet |
| **M9** | ZYLtech extrusion and T-nuts — [2020](https://www.zyltech.com/store/aluminum-extrusion-hardware/2020-t-slot/), [T-nuts](https://www.zyltech.com/100x-zyltech-spring-loaded-t-nuts-for-2020-aluminum-extrusion-m4-or-m5/) | First draft: |
| **M10** | ME-8108 roller-lever limit switch, screw terminals, 2-pack — [eBay](https://www.ebay.com/itm/156727632134), [spec page](https://st.robu.in/product/me-8108-rotary-adjustable-roller-lever-arm-mini-limit-switch) | Over-travel, no solder |
| **F1** | Birch plywood 2 x 2 ft — [Lowe's](https://www.lowes.com/pd/1-2-in-Birch-Plywood-Application-as-2-x-2/1000066183) | Base (price not confirmed) |
| **F2** | OpenBuilds V-Slot 20x20 — [link](https://us.openbuilds.com/v-slot-20x20-linear-rail/) | $3.29 / 500 mm |
| **F3** | KB-3D M5 T-nut — [link](https://kb-3d.com/store/extrusion-framing/252-t-nut-drop-inroll-in-20-series-6mm-slot-width-m5-threads-1657989339400.html) | $0.17 |
| **F4** | M8 tee nut — [Albany County Fasteners](https://www.albanycountyfasteners.com/metric-t-nuts-zinc-plated-steel-m8-x-125-4-prong-5602-010-042/) | $0.45 · not used since the no-solder, no-drill build |
| **F5** | Glarks screw kit — [Amazon](https://www.amazon.com/Glarks-510Pcs-Socket-Screws-Assortment/dp/B08HHZHXTP) | Listing |
| **F6** | M3 heat-set inserts — [Adafruit 4255](https://www.adafruit.com/product/4255), [CNC Kitchen](https://cnckitchenus.store/products/heat-set-insert-m3-x-5-7-100-pieces) | $5.95 · not used since the no-solder, no-drill build |
| **F7** | 608-2RS 10-pack — [Walmart](https://www.walmart.com/ip/10Pcs-set-608-2RS-Bearing-Deep-Groove-Steel-Sealed-Ball-Bearings-608RS-608-2RS/3999331773) | $9.90 |
| **F8** | #8 x 5/8 in Type 17 pan-head wood screws — [Fastener Superstore](https://www.fastenersuperstore.com/products/578040/wood-screws) | Self-drilling: no pilot holes (price to confirm) |
| **F9** | AstroAI DM6000AR multimeter with temperature probe — [AstroAI](https://www.astroai.com/digital-multimeter-6000-counts-dm6000ar/ap/100019) | Tool |
| **F10** | IRWIN VISE-GRIP 2078300 self-adjusting wire stripper 10–24 AWG — [Gexpro](https://www.gexpro.com/p/544823/irwin/self-adjusting-wire-stripper-10-24-awg/038548088457/2078300) | Tool |
| **F11** | SparkFun 6 in digital calipers — [product](https://www.sparkfun.com/6-digital-calipers.html) | Tool |
| **F12** | DIN 931 M8 hex bolts, partial thread — [M8 x 75](https://www.fastenersuperstore.com/products/276566/hex-cap-screws), [M8 x 35](https://www.fastenersuperstore.com/products/276362/hex-cap-screws) | Bolt axles (price to confirm) |
| **F13** | M2.5 x 20 mm Phillips pan machine screws — [Fastener Superstore](https://www.fastenersuperstore.com/products/529783/machine-screws) | Not used since the scan wedge became the tilted scan plate (kept so IDs stay stable) |
| **F14** | Elegoo Centauri Carbon enclosed CoreXY printer — [All3DP, $300 launch](https://all3dp.com/4/elegoo-opens-preorders-for-300-centauri-carbon-3d-printer/), [Slickdeals $265.99](https://slickdeals.net/f/18984553-elegoo-centauri-carbon-corexy-fdm-3d-printer-265-99-30-shipping-fee); Bambu Lab P1S [$399](https://www.3dtested.com/3d-printing/grab-this-usd399-bambu-lab-p1s-3d-printer-back-down-to-a-record-low-price-for-the-new-year-save-usd300-on-high-speed-enclosed-printer-for-beginners-and-enthusiasts-alike) | Tool: ABS-capable printer |
| **F15** | Screwdriver sets — [Home Depot](https://www.homedepot.com/b/Tools-Hand-Tools-Screwdrivers-Nut-Drivers-Screwdrivers-Screwdriver-Sets/philips-screwdriver/N-5yc1vZc998Z1z1lpee), [Husky 16-pc ~$15](https://slickdeals.net/f/18741004-husky-ratcheting-pivot-head-screwdriver-16-piece-14-88-fs-home-depot) | Tool |
| **F16** | SUNLU ABS 1.75 mm 1 kg black — [listing](https://woodartsupply.com/products/sunlu-abs-filament-1-75mm-3d-printer-filament-highly-resistant-durable-heat-resistance-excellent-toughness-compatible-with-99-fdm-3d-printers-1kg-spool-2-2lbs-black) | Filament (price to confirm) |
| **F17** | SUNLU ABS 1.75 mm black, 1 kg rolls, 3 kg minimum — [SUNLU store, $11.99/kg](https://store.sunlu.com/products/over-3kg-bundle-sale-abs-filament-1kg-roll) | Filament (checked 2026-10-09) |

## Parts: enclosure, calibration, multispectral

| ID | Source | Used for |
|---|---|---|
| **E1** | Roc-lon blackout fabric — [Walmart](https://www.walmart.com/ip/Roc-lon-54-Blackout-White-Fabric-per-Yard/164714653) | $6.62 / yd |
| **E2** | Protostar FlockBoard — [link](https://www.fpi-protostar.com/flockboard.htm); flocking — [First Light Optics](https://www.firstlightoptics.com/telescope-flocking-material/protostar-self-adhesive-hi-tack-flocking-material-1m-roll.html) | Backdrop upgrade |
| **E3** | Oak dowel 1/2 x 36 in — [Home Depot](https://www.homedepot.com/p/Builder-s-Choice-1-2-in-x-36-in-Oak-Round-Dowel-HDDO1236/206184685) | $4.04 |
| **E4** | PTFE (virgin) — [OnlineMetals sheet/plate list](https://www.onlinemetals.com/en/buy/plastic-sheet-plate-ptfe): 1/8 in 6 × 6 in $12.53, 3/8 in 6 × 6 in $22.97; [Online Metal Supply 2 × 2.5 × 2.5 in block](https://onlinemetalsupply.com/2-x-2-5-x-2-5-ptfe-teflon-plastic-sheet-white/) $23.48 | White tile (CAL-01) |
| **E5** | Edmund #43-876 first-surface mirror — [link](https://www.edmundoptics.com/p/50-x-50mm-enhanced-aluminum-4-6lambda-mirror/5362); also [BMI Surplus](https://bmisurplus.com/product/first-surface-mirror-4-inch-square/), [firstsurfacemirror.com](https://www.firstsurfacemirror.com/product/4-x-4-1-4-wave-glass-first-surface-mirror-13-64-5mm-thickness/) | Mirror upgrade / price check |
| **E6** | BC Precision 1 in G25 balls — [link](https://www.bcprecision.com/products/1-inch-chrome-steel-ball-bearings-g25) | $9.95 |
| **E7** | Colour targets — [Calibrite CC Mini (B&H)](https://www.bhphotovideo.com/c/product/1649333-REG/calibrite_ccc_mini_colorchecker_classic_mini.html), [SpyderCHECKR 24 (B&H)](https://www.bhphotovideo.com/c/product/1070560-REG/datacolor_sck24_sypdercheckr_24.html) | Optional, borrow |
| **E8** | Linear polarizer film 10-pack — [Walmart](https://www.walmart.com/ip/5466199163) | $8.95 |
| **E9** | Neewer 18 % gray card — [link](https://neewer.com/products/neewer-18-gray-white-card-set-for-white-balance-exposure-value-66600656) | Optional |
| **E10** | Opal acrylic 12 x 12 — [Walmart](https://www.walmart.com/ip/1-8-3mm-Milky-White-Acrylic-12-x12-Sheet-Translucent-Plexiglass-Cast-AZM/1515407359) | Diffuser option |
| **E11** | Micro servos — [Adafruit SG92R](https://www.adafruit.com/product/169), [Pololu FS90](https://www.pololu.com/product/2818) | Phase 10 option |
| **E12** | Protostar Hi-Tack flocked light-trap material, absorbs > 99 % — [fpi-protostar.com](https://www.fpi-protostar.com/hitack.htm), [First Light Optics](https://www.firstlightoptics.com/telescope-flocking-material.html) | Stray-light lining behind the sample and inside the lamp tube (phase 07) |
| **E13** | Madison Mill 1/2 x 36 in poplar dowel — [True Value](https://www.truevalue.com/product/163701/madison-mill-1-2-in-x-36-in-poplar-dowel-rod-163701/) | $2.79, drape posts |
