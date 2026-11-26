---
title: 'opengonio: control, calibration, fitting and rendering software for a printable gonioreflectometer and 3D scanner'
tags:
  - Python
  - BRDF
  - gonioreflectometer
  - material appearance
  - photometric calibration
  - 3D scanning
  - glTF
  - open hardware
authors:
  - name: Aleksander Norman
    affiliation: 1
affiliations:
  - name: California State University, Dominguez Hills, United States
    index: 1
date: 14 November 2026
bibliography: paper.bib
---

<!-- JOSS software paper for the opengonio Python package (software/). Generated bibliography: tools/joss_bib.py.
     Checked by tools/paper_check.py (sections, 750-1750 words). Results belong in the HardwareX article, not here. -->

# Summary

How a surface reflects light depends on where the light comes from and where it is seen from. That dependence, the
bidirectional reflectance distribution function (BRDF), is what makes paper look matte, plastic glossy and brushed
metal streaked. Instruments that measure it, gonioreflectometers, move a light, a sample and a camera through many
angles and record brightness at each pose. `opengonio` is the Python software for an open, 3D-printed
gonioreflectometer that also works as a turntable 3D scanner. It drives the four motor axes, plans the measurement
poses, captures and checks images, calibrates the camera and lamp, fits a reflectance model that rendering engines
understand, builds a 3D shape from silhouettes, and writes both as one glTF file [@T40] that opens in Blender, Unity,
Unreal or a web browser. Every command also runs against a built-in simulator, so the whole pipeline can be learned,
tested and taught before any hardware exists.

# Statement of need

Measured appearance data underpins realistic rendering, material science and quality control, but the instruments are
either laboratory systems [@G25; @G27] or image-based setups that still need machining, industrial robots or
specialised optics [@G12; @G15; @G39]. Consumer-hardware capture trades angular coverage for speed [@G38]. The
hardware this package controls follows the geometry of a published multispectral goniometric device [@R1] but is built
from printed parts, stepper motors and a USB camera. Such a machine is only useful if the software around it is as
open and checkable as the hardware: which pose reaches which pair of angles, how raw pixels become an absolute BRDF,
how well a model fits, and how the result reaches a renderer.

`opengonio` is for three groups: builders of the instrument, who need guided capture with pass/fail checks;
researchers and students in graphics and optics, who need calibrated BRDF samples and fits with their provenance; and
teachers, who need the full measure-calibrate-fit-render chain to run on a laptop with no hardware at all.

# State of the field

Open BRDF datasets such as MERL [@G15] and RGL-EPFL [@R16] provide measurements but not the software that produced
them for a reusable instrument. Commercial appearance scanners ship closed software [@R40]. Open goniometer code exists
for other measurements, for example angle-resolved emission of light sources [@R38], which does not cover
reflectance, calibration to absolute units, or model fitting. Photogrammetry packages [@S3] reconstruct shape but not
reflectance. General renderers [@T2] consume materials but do not measure them. Building a new package rather than
extending one of these was needed because the instrument's kinematics, its calibration (mirror angle offset, camera
response [@R5], pressed-PTFE white reference) and its export to engine materials have to share one data model and one
record of provenance per run.

# Software design

The package is organised around the run folder, the unit of provenance. Every capture writes a manifest (machine
configuration, calibration in force, software version) next to its images, and every later step (verify, curve, fit,
render) reads that folder and writes its outputs beside it, so a published number can be traced to its photos.

- **Kinematics and plans** (`gantry`, `plans`): pose solving for the light arm and the three sample axes, collision
  checks, and measurement plans (mirror sweep, in-plane, isotropic, anisotropic, scan rings).
- **Machine control** (`gantry`, `station`): G-code over USB to the grblHAL motion board and a line protocol to a
  microcontroller hub for keypads and sensors; the same interface is implemented by the simulator.
- **Capture and calibration** (`camera`, `hdr`, `calibration`, `verify`): locked exposure, exposure-series response
  fit [@R5], dark level, lamp drift, angle offset from the mirror peak, and absolute scale from a white reference.
- **Fitting** (`fit`, `brdf`): Lambert + GGX microfacet [@R6; @T11] with Schlick Fresnel [@R7] in the
  metallic-roughness parameterisation that game engines use, with a holdout check on rows the fit never saw.
- **Scanning** (`scan`): silhouettes from calibrated views carve a visual hull [@S5], which becomes a smoothed,
  watertight mesh; dense meshes come from COLMAP [@S3].
- **Rendering** (`render`): a dependency-free glTF 2.0 writer and a NumPy software renderer that uses exactly the
  fitted BRDF; a WebGL viewer in the browser and the control app draws the same formula.
- **Control app** (`app`): a local web interface for connect, home, jog, capture and results, which also runs
  entirely in the browser through Pyodide, and on phones paired over the local network.

The main trade-off was to keep the core free of heavy dependencies (NumPy, PyYAML) so that it installs anywhere,
runs in the browser, and can be audited; optional extras add camera drivers and network pairing. The test suite
covers kinematics, plans, calibration, fitting, scanning, rendering (including that the renderer's BRDF equals the
fitted one) and the app, against the simulator, and runs in continuous integration on every change.

# Research impact statement

[TBD: after the first measurements: validated BRDF data of real samples (PTFE check, reciprocity, fit holdout) and any
use outside the author's build. JOSS requires evidence that is "compelling and specific, not aspirational", so this
paper is submitted only after that evidence exists (roadmap milestone M50.5).]

# AI usage disclosure

[TBD: author to confirm tools, versions and scope.] Generative AI (Claude, Anthropic) was used to draft and revise
software, tests, documentation and this paper. The author reviewed the output; correctness is checked by the automated
test suite, by continuous integration on every change, and by simulator runs of every command before hardware use.

# Acknowledgements

[TBD: acknowledgements and any financial support.]

# References
