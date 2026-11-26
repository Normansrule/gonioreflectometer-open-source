"""Slip model: how far an open-loop axis may have drifted from where the controller thinks it is, and what to do.

The motors are steppers without encoders; belts creep and a stalled motor loses steps, and the controller cannot see
either. The only absolute reference on each axis is its home switch. Per axis, with a = degrees travelled in a move:

    state        x = [d, s]      d = true angle - controller angle (deg), s = creep (deg lost or gained per deg travelled)
    move         d <- d + s a    P <- F P F' + Q,   F = [[1, a], [0, 1]],   Q = diag(q a, q_s a)      (random walk in travel)
    reference    y = d + v       v ~ N(0, r): the switch edge found again, compared with where it was after homing
    update       K = P H' / (H P H' + r), H = [1, 0]:   x <- x + K (y - d),   P <- (I - K H) P            (Kalman filter)

Three actions follow from it (gantry.py):
  feedforward  every commanded angle is corrected by the predicted d, so learned creep is cancelled as it happens;
  schedule     an axis is "due" when k_sigma * sqrt(P_dd) exceeds the budget; a run then re-references it;
  gate         a reference more than `gate` standard deviations from the prediction is a step-loss event (reported; it
               does not move s, but widens its variance so a creep larger than expected is learned from the next one);
               one beyond max_correct_deg is a mechanical fault (refused: tension the belt, lower the acceleration).
Re-homing puts d back to 0 +/- sqrt(r) whatever happened before (deadbeat correction); s and its variance are kept.

Every default below is a nominal starting value, not a measurement: set q, r and creep_sd from the repeatability
record of your machine (roadmap M19.2). Estimation follows the standard discrete Kalman filter [T59].
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

MODES = ("off", "rehome", "probe")
DEFAULTS = {
    "mode": "rehome",          # off | rehome (re-home when due; nothing measured) | probe (measure the switch edge first; grblHAL)
    "budget_deg": None,        # allowed 2-sigma angle error between references; None = machine.repeatability_target_deg
    "k_sigma": 2.0,
    "q_deg2_per_deg": 1.0e-6,  # random-walk variance per degree travelled (nominal)
    "creep_sd": 2.0e-4,        # prior standard deviation of the creep, deg per deg (nominal: 0.02 %)
    "creep_walk": 1.0e-12,     # lets the creep estimate follow slow changes (belt wear, temperature)
    "switch_sd_deg": 0.02,     # repeatability of the home switch edge (nominal; measured in M19.2)
    "gate": 4.0,               # innovation gate, standard deviations
    "max_correct_deg": 1.0,    # larger measured slip = mechanical fault, not something to correct in software
    "probe_step_deg": 0.02,
    "pulloff_deg": 2.0,        # controller homing pull-off ($27 / pulloff_mm)
    "approach_deg": 0.0,       # > 0: every final approach is made moving away from the switch, from this far back (backlash)
}


@dataclass(frozen=True)
class SlipConfig:
    mode: str
    budget_deg: float
    k_sigma: float
    q: float
    creep_sd: float
    creep_walk: float
    switch_sd: float
    gate: float
    max_correct_deg: float
    probe_step_deg: float
    pulloff_deg: float
    approach_deg: float

    @classmethod
    def from_machine(cls, cfg) -> "SlipConfig":
        raw = {**DEFAULTS, **(getattr(cfg, "slip", None) or {})}
        unknown = set(raw) - set(DEFAULTS)
        if unknown:
            raise ValueError(f"machine.yaml slip: unknown keys {sorted(unknown)}")
        if raw["mode"] not in MODES:
            raise ValueError(f"machine.yaml slip.mode must be one of {MODES}, not {raw['mode']!r}")
        budget = raw["budget_deg"] if raw["budget_deg"] is not None else cfg.repeatability_target_deg
        c = cls(str(raw["mode"]), float(budget), float(raw["k_sigma"]), float(raw["q_deg2_per_deg"]), float(raw["creep_sd"]),
                float(raw["creep_walk"]), float(raw["switch_sd_deg"]), float(raw["gate"]), float(raw["max_correct_deg"]),
                float(raw["probe_step_deg"]), float(raw["pulloff_deg"]), float(raw["approach_deg"]))
        if min(c.budget_deg, c.k_sigma, c.switch_sd, c.gate, c.max_correct_deg, c.probe_step_deg, c.pulloff_deg) <= 0 \
                or min(c.q, c.creep_sd, c.creep_walk, c.approach_deg) < 0:
            raise ValueError("machine.yaml slip: values must be positive (approach_deg, q, creep_sd, creep_walk may be 0)")
        if c.k_sigma * c.switch_sd >= c.budget_deg:
            raise ValueError(f"machine.yaml slip: the switch alone ({c.k_sigma:g} x {c.switch_sd:g} deg) already exceeds "
                             f"budget_deg {c.budget_deg:g}; no schedule could keep the axis inside it")
        return c


@dataclass
class AxisSlip:
    """Kalman filter for one axis. d, s: estimates; (pdd, pds, pss): their covariance; travel: degrees since the last reference."""
    c: SlipConfig
    d: float = 0.0
    s: float = 0.0
    pdd: float = 0.0
    pds: float = 0.0
    pss: float = 0.0
    travel: float = 0.0
    total: float = 0.0
    checks: int = 0
    events: list[dict] = field(default_factory=list)

    def __post_init__(self):
        self.pdd, self.pss = self.c.switch_sd ** 2, self.c.creep_sd ** 2

    @property
    def sigma(self) -> float:
        return math.sqrt(max(self.pdd, 0.0))

    @property
    def bound(self) -> float:
        """Angle error the axis may have right now (k sigma). Predicted drift is not in it: the commands cancel it."""
        return self.c.k_sigma * self.sigma

    @property
    def due(self) -> bool:
        return self.bound > self.c.budget_deg

    def predict(self, travel_deg: float) -> None:
        a = abs(float(travel_deg))
        if a == 0.0:
            return
        self.d += self.s * a
        self.pdd += 2 * a * self.pds + a * a * self.pss + self.c.q * a
        self.pds += a * self.pss
        self.pss += self.c.creep_walk * a
        self.travel += a
        self.total += a

    def update(self, measured_deg: float) -> dict:
        """One reference: measured d. Returns what happened; raises ValueError beyond max_correct_deg."""
        y = float(measured_deg)
        innov, s_var = y - self.d, self.pdd + self.c.switch_sd ** 2
        nsig = abs(innov) / math.sqrt(s_var)
        rep = {"measured_deg": round(y, 4), "predicted_deg": round(self.d, 4), "sigma_deg": round(self.sigma, 4),
               "travel_deg": round(self.travel, 1), "n_sigma": round(nsig, 2), "event": None}
        if abs(y) > self.c.max_correct_deg:
            rep["event"] = "fault"
            self.events.append(rep)
            raise ValueError(f"measured slip {y:+.3f} deg is beyond slip.max_correct_deg ({self.c.max_correct_deg:g}): "
                             f"a mechanical fault (belt tension, pulley screw, acceleration), not a drift to correct")
        if nsig > self.c.gate:              # step loss: a jump the creep model does not describe, so it must not teach s
            rep["event"] = "step loss"
            self.events.append(rep)
            if self.travel > 0:             # ...but if it was creep after all, the next one like it will be believed
                self.pss = max(self.pss, (innov / self.travel) ** 2)
            self.d, self.pdd, self.pds = y, self.c.switch_sd ** 2, 0.0
        else:
            kd, ks = self.pdd / s_var, self.pds / s_var
            self.d += kd * innov
            self.s += ks * innov
            self.pss -= ks * self.pds
            self.pds -= kd * self.pds
            self.pdd -= kd * self.pdd
        self.checks += 1
        rep["creep_pct"] = round(100 * self.s, 4)
        return rep

    def rehomed(self) -> None:
        """The axis stands on its switch again: d = 0 +/- switch_sd. The creep estimate stays."""
        self.d, self.pdd, self.pds, self.travel = 0.0, self.c.switch_sd ** 2, 0.0, 0.0

    def brief(self) -> dict:
        return {"offset_deg": round(self.d, 4), "bound_deg": round(self.bound, 4), "sigma_deg": round(self.sigma, 4),
                "creep_pct": round(100 * self.s, 4), "creep_sd_pct": round(100 * math.sqrt(max(self.pss, 0.0)), 4),
                "travel_deg": round(self.travel, 1), "total_deg": round(self.total, 1), "checks": self.checks,
                "budget_deg": self.c.budget_deg, "due": self.due, "events": len(self.events)}


def travel_until_due(c: SlipConfig, creep_sd: float | None = None) -> float:
    """Degrees an axis may travel after a reference before it is due (closed form of AxisSlip.bound = budget).
    Used by the documentation and the website; the filter itself decides during a run."""
    sd = c.creep_sd if creep_sd is None else creep_sd
    lo, hi = 0.0, 1.0e6
    for _ in range(60):
        a = 0.5 * (lo + hi)
        bound = c.k_sigma * math.sqrt(c.switch_sd ** 2 + c.q * a + (sd * a) ** 2)
        lo, hi = (a, hi) if bound <= c.budget_deg else (lo, a)
    return lo
