#!/usr/bin/env python3
"""Deck map -> phases/03-frame/deck-map.svg: the 9 printed tiles with their names, seen from above and from below
(for bolting them together upside down), and every pilot hole from PLACE in tools/cad/parts.py.
Nothing to print 1:1: the pilots are in the tiles. Needs cadquery (imports parts.py): run by `make parts`.
SPDX-License-Identifier: CERN-OHL-S-2.0
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parts as P  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "phases/03-frame/deck-map.svg"
H, T = P.DECK_HALF, P.DECK_TILE
COL = {"table post": "#c00", "table motor bracket": "#c60", "M4 motor mount": "#a0a", "bar saddles": "#06c",
       "power plate": "#080", "controller tray": "#088", "ring scale": "#555",
       "table endstop riser": "#b80", "screen stand": "#46c"}


def panel(ox: float, title: str, mirror: bool) -> list[str]:
    """One 600 mm deck drawn at 1 SVG unit = 1 mm, left edge at ox. mirror: seen from below (x flipped)."""
    X = (lambda x: ox + H - x) if mirror else (lambda x: ox + H + x)
    Y = lambda y: 40 + H - y
    g = [f'<text x="{ox + H}" y="25" text-anchor="middle" font-size="16">{title}</text>']
    for k, name in enumerate(P.TILE_NAMES):
        i, j = k % 3 - 1, k // 3 - 1
        x0, x1 = sorted((X(T * i - T / 2), X(T * i + T / 2)))
        g.append(f'<rect x="{x0}" y="{Y(T * j + T / 2)}" width="{x1 - x0}" height="{T}" fill="#f4f4f4" stroke="#000" stroke-width="1.5"/>')
        g.append(f'<text x="{x0 + 8}" y="{Y(T * j - T / 2) - 8}" font-size="14" fill="#888">FRM-01{chr(97 + k)} {name}</text>')
    if not mirror:
        g.append(f'<circle cx="{X(0)}" cy="{Y(0)}" r="152.5" fill="none" stroke="#999" stroke-dasharray="4 3"/>')
        for name, pts in P.PLACE.items():
            for x, y in pts:
                g.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="4" fill="{COL[name]}"/>')
        g.append(f'<path d="M{X(H)} {Y(0)}h40" stroke="#06c" stroke-width="3" marker-end="url(#a)"/>'
                 f'<text x="{X(H) + 4}" y="{Y(0) - 8}" font-size="12" fill="#06c">+X camera</text>')
    else:
        g.append(f'<text x="{ox + H}" y="{40 + 2 * H + 22}" text-anchor="middle" font-size="12">upside down on the table: '
                 f'east and west swap; 3 x M2 x 10 + nut per shared edge</text>')
    return g


svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1330 720" font-family="Arial">',
       '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0L8 4L0 8z" fill="#06c"/></marker></defs>',
       '<rect width="1330" height="720" fill="#fff"/>']
svg += panel(10, "Deck from above: pilot holes for every mount (M2 self-tap)", False)
svg += panel(10 + 2 * H + 110, "From below: how the tiles lie while you bolt them", True)
ly = 40 + 2 * H + 45
for n, (name, c) in enumerate(COL.items()):
    svg.append(f'<circle cx="{20 + 175 * n}" cy="{ly}" r="5" fill="{c}"/><text x="{30 + 175 * n}" y="{ly + 4}" font-size="12">{name}</text>')
svg.append(f'<text x="10" y="{ly + 30}" font-size="12">Origin = deck centre under the zero point; 200 mm tiles; spare pilots on a 40 mm grid in every tile '
           f'(not drawn) take endstops, switches and cable clips.</text>')
svg.append("</svg>")
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"{sum(len(v) for v in P.PLACE.values())} pilots -> {OUT.relative_to(ROOT)}")
