"""Material: what a fit gives a renderer.

Metallic-roughness (glTF 2.0 core [T40], Unreal [T35], Blender Principled, Unity URP Lit): base colour, roughness,
metallic. fit.py fits exactly this model (Lambert + GGX [R6], Schlick Fresnel [R7], F0 dielectric 0.04), so a
renderer that implements glTF's BRDF draws the fitted curve, not an approximation of it.
The fit is grey (one camera channel): the base colour is the same in R, G and B unless a colour is given.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Ground truth of the simulated materials in sim.py (same numbers): what a perfect measurement + fit would return.
SIM_TRUTH = {
    "mirror": {"base_color": 0.9, "roughness": 0.1, "metallic": 1.0},
    "ptfe": {"base_color": 0.99, "roughness": 1.0, "metallic": 0.0, "lambert": True},
    "matte": {"base_color": 0.5, "roughness": 1.0, "metallic": 0.0, "lambert": True},
    "paper": {"base_color": 0.8, "roughness": 0.9, "metallic": 0.0},
    "plastic": {"base_color": 0.2, "roughness": 0.3, "metallic": 0.0},
}


@dataclass
class Material:
    name: str
    base_color: tuple[float, float, float]
    roughness: float
    metallic: float
    source: str = "manual"                 # "fit: <run>", "simulated truth", "manual"
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_fit(cls, fit: dict | str | Path, name: str | None = None, color: tuple[float, float, float] | None = None):
        """fit.json (dict or path) -> Material. color: optional RGB tint (the fit itself is grey)."""
        src = "fit"
        if not isinstance(fit, dict):
            p = Path(fit)
            p = p / "fit.json" if p.is_dir() else p
            src = f"fit: {p.parent.name}"
            fit = json.loads(p.read_text(encoding="utf-8"))
        b = float(fit["base_color"])
        notes = []
        prov = fit.get("provenance") or {}
        if prov.get("relative_only"):
            notes.append("fitted to relative values (no white reference): base colour is not absolute")
        ho = fit.get("holdout")
        if ho:
            notes.append(f"holdout RMS {ho['rms_pct_of_peak']} % of peak (fit {fit.get('rms_pct_of_peak')} %)")
        if color is not None:
            notes.append("colour tint added by hand: the fit is grey")
        rgb = tuple(round(b * c, 4) for c in color) if color is not None else (b, b, b)
        return cls(name or "opengonio_fit", rgb, float(fit["roughness"]), float(fit["metallic"]), src, notes)

    @classmethod
    def sim(cls, material: str) -> "Material":
        t = SIM_TRUTH[material]
        b = t["base_color"]
        return cls(material, (b, b, b), t["roughness"], t["metallic"], "simulated truth (sim.py)",
                   ["Lambert in sim.py: drawn here as roughness 1, which adds a weak 4 % gloss"] if t.get("lambert") else [])

    def to_gltf(self) -> dict:
        """glTF 2.0 material object [T40]; provenance in extras so it survives the round trip."""
        return {"name": self.name, "doubleSided": False,
                "pbrMetallicRoughness": {"baseColorFactor": [*map(float, self.base_color), 1.0],
                                         "metallicFactor": float(self.metallic), "roughnessFactor": float(self.roughness)},
                "extras": {"opengonio": {"source": self.source, "notes": self.notes,
                                         "model": "Lambert + GGX, metallic-roughness, F0 dielectric 0.04"}}}

    def engines(self) -> dict:
        """The same material typed into each tool (Unity takes smoothness = 1 - roughness)."""
        c, r, m = list(self.base_color), self.roughness, self.metallic
        return {"glTF / Blender Principled BSDF": {"Base Color": c, "Roughness": r, "Metallic": m},
                "Unreal": {"BaseColor": c, "Roughness": r, "Metallic": m, "Specular": 0.5},
                "Unity (URP Lit, metallic)": {"Base Map": c, "Smoothness": round(1 - r, 3), "Metallic": m}}

    def to_dict(self) -> dict:
        return {**asdict(self), "base_color": list(self.base_color), "engines": self.engines()}
