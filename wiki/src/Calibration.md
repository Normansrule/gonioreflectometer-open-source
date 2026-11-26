# Calibration

| Quantity | Method | Pass |
|---|---|---|
| Angle offset | mirror peak must sit at M3 = M4 / 2 [@R1] | residual ≤ 0.1° |
| Dark level $C_d$ | lamp-off frame | — |
| Camera response $\gamma$ | exposure series [@R5] | linear fit |
| Absolute BRDF | PTFE (polytetrafluoroethylene) tile, ≈ 99 % diffuse, at 45° [@N30] | — |
| Lamp drift | repeat the first pose at the end | ≤ 2 % |

```math
f_r=\frac{C_{\mathrm{lin}}}{C_{w,\mathrm{lin}}}\cdot\frac{\rho_w}{\pi}\cdot\frac{\cos 45^\circ}{\cos\theta_i},\qquad C_{\mathrm{lin}}=(C-C_d)^{\gamma}
```

$C$ camera counts, $C_w$ white tile, $\rho_w$ its reflectance. Steps: stage [07]({{REPO}}/phases/07-calibrate).

## Slip (axis drift)

The motors run open loop, so the software keeps an error bound per axis and acts on it (`gantry/slip.py`, model in [Theory](Theory.md)). All values below are nominal until measured in M19.2; nothing here has been measured on a built machine yet.

| What | How | Where |
|---|---|---|
| Predict | error bound grows with degrees travelled (random walk + creep) | `slip:` in `machine.yaml` |
| Correct | every commanded angle minus the predicted drift | automatic |
| Schedule | bound > budget (default 0.1°): the axis re-homes before the next shot, then returns | every run; listed in `manifest.json` → `slip_checks` |
| Measure | `slip.mode: probe` or `opengonio slip M3`: steps to the home switch, reads the drift, updates the creep | grblHAL only (lifts soft limits `$20` for the search, restores them) |
| Detect | drift > 4σ from the prediction = lost steps (reported); > 1° = mechanical fault (run stops) | `opengonio slip` exits 1 on any event |
| Backlash | `approach_deg` > 0: every pose is reached moving away from the switch | off by default |
| Record | each shot stores `angle_bound_deg` per axis | `manifest.json` |

| `slip.mode` | Does | Use |
|---|---|---|
| `rehome` (default) | re-homes when due; measures nothing | any firmware |
| `probe` | measures the drift first, so the creep is learned and references get rarer | grblHAL, after M19.2 passes |
| `off` | no model | comparison only |

If lost steps are reported: tension the belt, tighten the pulley set screw, then lower that axis's acceleration (`tools/grblhal_settings.py`) before raising motor current.

