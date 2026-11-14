<!-- generated from wiki/src/Commands.md by tools/refs_bib.py - edit the source -->

# Commands

### Try without hardware

```bash
make setup && source .venv/bin/activate     # once; `source …` again in every new terminal
make all                                     # build + check + tests
make ci                                      # replay the GitHub checks on a clean clone (before pushing)
make sim                                     # simulated machine: mirror → calibrate → dark → gamma → white → matte → drift → fit; ends "ALL PASS"
opengonio check-pose M4=60 M3=30             # angles + collision check for one pose
opengonio --sim plastic capture inplane --step 10 --out data/sim/plastic && opengonio curve data/sim/plastic
opengonio scan demo --out demo               # 3D scan pipeline on a synthetic object
```

`--sim MATERIAL` (mirror, ptfe, matte, paper, plastic) runs any `capture` on a simulated machine; `--sim-error M3=0.8` hides an angle error in it, `--sim-drift 0.3` dims its lamp 0.3 % per shot and `--sim-gamma 2.2` makes its camera non-linear, so you can watch `verify` and `calibrate` find them. The [Calibration lab](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/docs/lab.html#calibrate) shows the same thing interactively.

### Measure and calibrate

![Measuring loop: capture, verify, calibrate, curve, fit](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/docs/assets/measure.svg?raw=true)

```bash
opengonio capture warmup --minutes 10        # stage 06: lamp settle time -> lights.white.warmup_s
opengonio capture mirror --theta 40          # mirror sweep -> data/mirror_40/ (images + manifest.json)
opengonio verify data/mirror_40              # PASS / WARN / FAIL: missing images, angles, lamp drift, saturation
opengonio curve data/mirror_40               # curve.csv + curve.svg (picture of the run)
opengonio calibrate mirror data/mirror_*     # angle offset -> software/config/calibration.yaml
opengonio capture dark      && opengonio calibrate dark data/dark            # lamp-off level
opengonio capture linearity && opengonio calibrate linearity data/linearity  # camera response (gamma)
opengonio capture white     && opengonio calibrate white data/white          # PTFE at 45:0 -> absolute units
opengonio capture inplane --step 10 --out data/paper && opengonio curve data/paper   # brdf_per_sr column
opengonio fit data/paper                     # base colour, roughness, metallic -> fit.json (+ Blender/Unreal/Unity values), fit.svg
opengonio render data/paper                  # that material on a shader ball -> material.glb + material.png (see Rendering)
opengonio render data/paper --mesh scan_out/hull_mesh.ply   # on your scanned object -> hull_mesh.glb
opengonio render demo                        # the whole path on simulated data -> data/render_demo/
opengonio capture isotropic --step 15        # stage 08: out-of-plane set from BRDF angles (inverse kinematics)
opengonio capture spin --theta 30            # stage 09: sample spun 0–180° (brushed metal)
opengonio scan hull --out scan_cube --voxel 0.5   # stage 12: silhouettes -> hull.ply + object size
opengonio scan ps --out scan_ball --sphere        # stage 12: photometric stereo -> normals, error on a sphere
opengonio calibrate show                     # every value, its date, and what is stale or not measured yet
```

| Mirror run before calibration (`curve.svg`) | Material fit (`fit.svg`) |
|---|---|
| ![Mirror sweep: peak 0.4 degrees left of M3 = M4/2](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/docs/assets/example-mirror.svg?raw=true) | ![Fitted GGX curves through measured points](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/docs/assets/example-fit.svg?raw=true) |

Both from the simulated machine (`make build` regenerates them): the mirror peak sits 0.4° left of the orange line until `calibrate mirror` runs; the fit recovers the simulated plastic (base 0.2, roughness 0.3).

Every run shoots its first pose again at the end (`ref_start.png`, `ref_end.png`); `verify` fails the run if the lamp changed by more than `drift_limit_pct` (2 %). Every `manifest.json` carries `schema`, units and the calibration used, so old data can be re-processed later.

### Flash and move the motors

Full steps (incl. WSL USB): [firmware.md](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/phases/02-controller/design.md).

```bash
bash scripts/controller.sh flash          # how to put grblHAL on the SKR Pico (Web Builder .uf2, drag and drop)
bash scripts/controller.sh settings       # send firmware/grblhal/settings.txt over USB-C
bash scripts/controller.sh pins           # output port numbers for machine.yaml lights
bash scripts/e4.sh test                   # home, move, motors off
bash scripts/hub.sh flash oct              # MicroPython onto the ESP32-S3 (oct = N8R8/N16R8 module)
bash scripts/hub.sh                       # button hub firmware
```

### Control app: laptop, desktop, phone, website

```bash
opengonio app --sim mirror                      # browser, simulated machine
opengonio app --window                          # desktop window (pip install "./software[desktop]")
opengonio app --lan                             # + phones and tablets on this Wi-Fi: scan the QR code under Phone (pip install "./software[lan]")
bash scripts/pages.sh                           # once: the website on GitHub Pages (asks before making the repo public)
python software/packaging/build.py              # desktop app for this computer -> dist/OpenGonio-<os>.zip (GitHub builds all three)
```

Each run in the app's list downloads as a zip (↓). The [web version](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/docs/app/index.html) runs the same Python in the browser (Pyodide) on the simulated machine. The optional status screen on the hub shows the machine's state without any app: `SCREEN ON` on the hub's serial port ([hub add-ons](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/docs/addons.html)).

### Standalone mode (no laptop)

[Wiring and setup](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/phases/15-standalone/design.md).

```bash
bash scripts/station.sh aleks@opengonio.local     # once: installs the station on the Pi Zero 2 W
# on the machine: NEXT = choose job, START = run, STOP = abort
opengonio pull aleks@opengonio.local              # later, on the laptop
opengonio verify data/*                           # PASS / WARN / FAIL per job
```

### Publish and update the private GitHub repo (Ubuntu)

```bash
# 1. Tools
sudo apt update && sudo apt install -y git python3-venv unzip curl
sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
sudo apt update && sudo apt install -y gh

# 2. Log in (workflow scope lets the CI file push)
gh auth login --hostname github.com --git-protocol https --web --scopes workflow
gh auth setup-git

# 3. Unzip (WSL: /mnt/c/Users/<you>/Downloads)
mkdir -p ~/projects && cd ~/projects
unzip -q ~/Downloads/Gonioreflectometer-Open-Source.zip
cd Gonioreflectometer-Open-Source

# 4. Private repo, push, milestones, issues
bash scripts/publish.sh

# 5. Check
gh repo view --web
```

Other account over SSH: `OWNER=<user> REMOTE=git@<host-alias>:<user>/Gonioreflectometer-Open-Source.git bash scripts/publish.sh`

**Every update after that** (pushes, then syncs milestones and issues with `.github/phases.yml`):

```bash
cd ~/projects/Gonioreflectometer-Open-Source

# your own edits (same as: make publish m="…")
bash scripts/update.sh "M05.1 done"

# a new zip (keeps your history; replaces repo files with the zip's)
bash scripts/update.sh "update from new zip" /mnt/c/Users/<you>/Downloads/Gonioreflectometer-Open-Source.zip
bash scripts/get_papers.sh
```
