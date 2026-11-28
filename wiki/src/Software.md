# Software

Python package `opengonio` ([software/]({{REPO}}/software)). Motion: grblHAL on the BTT SKR Pico over USB-C (FluidNC ESP32 boards also supported); the ESP32-S3 hub reads keypads and sensors.

```bash
make setup && source .venv/bin/activate
make sim                                   # simulated machine, ends "ALL PASS"
opengonio check-pose M4=60 M3=30           # angles + collision check
opengonio --sim plastic capture inplane --step 10 --out data/sim/plastic
opengonio curve data/sim/plastic           # reflectance curve
```

- Laptop mode: the laptop runs jobs. Standalone mode: a Pi Zero 2 W runs them; `opengonio pull` + `opengonio verify` bring data back.
- `make all`: rebuild docs, checks, tests.

## Other software this project uses

`opengonio doctor` lists what is installed, with versions, and what is missing.

| Software | Needed for | Install | Without it |
|---|---|---|---|
| NumPy, PyYAML | everything | with `pip install opengonio` | does not run |
| OpenCV (Open Source Computer Vision Library) | USB camera control, High Dynamic Range (HDR) merge, ChArUco marker calibration, image files other than PNG | `pip install "opengonio[hw]"` | simulator and PNG still work; no real camera |
| pyserial | USB link to the motor board and the hub | `pip install "opengonio[hw]"` | simulator only |
| pywebview | control app in its own window | `pip install "opengonio[desktop]"` | the app opens in the browser |
| segno | QR code to pair a phone | `pip install "opengonio[lan]"` | type the address by hand |
| COLMAP | dense 3D reconstruction from the scan photos | from colmap.github.io | visual hull only |
| CadQuery | regenerating the printed parts | `pip install cadquery` | use the STEP and STL files in the repository |
| LaTeX (latexmk, biber), pandoc | paper PDF, Word and wiki exports | system packages | `make paper` and `make export` are skipped |
| Node.js | one test: the AR / VR page's JavaScript against the Python | nodejs.org | that test is skipped |
| GitHub Actions | the automated checks, the website, the wiki and the desktop app builds on every push | runs on GitHub; nothing to install | run `make all` and `make ci` by hand |
| A WebXR browser (Edge on HoloLens 2, Browser on Meta Quest) | AR and VR training in a headset | on the headset | the trainer runs in the page |

OpenCV is checked by `software/tests/test_opencv.py` on synthetic images: the HDR merge returns linear radiance from gamma-encoded frames, a rendered ChArUco board calibrates a camera, and image files keep RGB order. The camera itself needs the hardware.
