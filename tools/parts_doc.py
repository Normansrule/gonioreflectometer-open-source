#!/usr/bin/env python3
"""PARTS.md: your working parts list. You decide there; the tool keeps everything else in step.

    python tools/parts_doc.py               read PARTS.md decisions -> bom.csv (Status, Own, Paid USD) -> rewrite PARTS.md
    python tools/parts_doc.py --seed DIR    first run only: take Own / Paid USD from an older copy of phases/

Run by `make build`, and on GitHub by .github/workflows/parts-sync.yml after you edit PARTS.md in the browser.
Specs (part, price, link) live in phases/NN/bom.csv; decisions (status, note, paid) live in PARTS.md.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "PARTS.md"
sys.path.insert(0, str(ROOT / "tools"))
import bom_check  # noqa: E402
import part_images  # noqa: E402

STATUSES = ["suggested", "agreed", "ordered", "have", "swap", "skip"]
CHECKED = {"agreed", "ordered", "have"}
LINE = re.compile(r"^- \[(?P<box>[ xX])\] \*\*(?P<id>[A-Z]{3}-\d+[a-z]?)\*\*.*?status:\s*(?P<status>[a-z-]+)")
SUB = re.compile(r"^\s+- (?P<key>note|paid):\s*(?P<val>.*)$")
TITLES = {}


def stage_titles() -> dict[str, str]:
    import yaml
    y = yaml.safe_load((ROOT / ".github" / "phases.yml").read_text(encoding="utf-8"))
    return {s["folder"]: s["title"] for s in y["stages"]}


def read_doc(text: str) -> dict[str, dict]:
    """ID -> {status, note, paid} from PARTS.md (unknown words fall back to `suggested`)."""
    out, cur = {}, None
    for line in text.splitlines():
        m = LINE.match(line)
        if m:
            st = m["status"] if m["status"] in STATUSES else "suggested"
            if m["box"] in "xX" and st == "suggested":
                st = "agreed"                         # ticking the box = agreeing
            elif m["box"] == " " and st == "agreed":
                st = "suggested"                      # unticking takes it back
            cur = out[m["id"]] = {"status": st, "note": "", "paid": ""}
            continue
        s = SUB.match(line)
        if s and cur is not None:
            cur[s["key"]] = s["val"].strip()
            if s["key"] == "paid" and money(cur["paid"]) and cur["status"] in ("suggested", "agreed"):
                cur["status"] = "ordered"             # paid for = ordered
        elif line.startswith(("#", "- [")):
            cur = None
    return out


def money(v: str) -> str:
    v = v.replace("$", "").replace(",", "").strip()
    try:
        return f"{float(v):.2f}" if v else ""
    except ValueError:
        return ""


def seed(old: Path) -> dict[str, dict]:
    """Decisions from an older phases/ copy (before PARTS.md existed): Own = Y -> have, Paid USD kept."""
    out = {}
    for f in old.glob("*/bom.csv"):
        for r in csv.DictReader(f.open(encoding="utf-8")):
            if r.get("Own") == "Y" and not r["Notes"].startswith("Consumable"):
                out[r["ID"]] = {"status": "have", "note": "", "paid": r.get("Paid USD", "")}
            elif r.get("Paid USD"):
                out[r["ID"]] = {"status": "ordered", "note": "", "paid": r["Paid USD"]}
    return out


def apply(decisions: dict[str, dict]) -> dict[str, list[dict]]:
    """Write Status / Own / Paid USD into every bom.csv; return the rows by stage."""
    boms = bom_check.load()
    for stage, rows in boms.items():
        for r in rows:
            d = decisions.get(r["ID"], {"status": r.get("Status") or "suggested", "note": "", "paid": r.get("Paid USD", "")})
            r["Status"] = d["status"]
            r["Own"] = "Y" if d["status"] == "have" else "N"
            r["Paid USD"] = money(d.get("paid", ""))
            r["_note"] = d.get("note", "")
        f = ROOT / "phases" / stage / "bom.csv"
        with f.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=bom_check.COLUMNS, lineterminator="\n", extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    return boms


def to_buy(r: dict) -> bool:
    """Machine parts still to buy (tools are counted separately: see to_buy_tool)."""
    return (r["Type"] == "Purchase" and r["Status"] in ("suggested", "agreed")) or \
        (r["Type"] == "Optional" and r["Status"] == "agreed")


def to_buy_tool(r: dict) -> bool:
    return r["Type"] == "Tool" and r["Status"] in ("suggested", "agreed")


def render(boms: dict[str, list[dict]]) -> str:
    titles = stage_titles()
    allrows = [r for rows in boms.values() for r in rows]
    buyable = [r for r in allrows if r["Type"] in ("Purchase", "Optional", "Tool")]
    tot = lambda rows: sum(float(r["Total USD"]) for r in rows)  # noqa: E731
    by = {s: [r for r in buyable if r["Status"] == s] for s in STATUSES}
    paid = sum(float(r["Paid USD"]) for r in allrows if r["Paid USD"])
    plan = tot([r for r in allrows if r["Type"] == "Purchase"])
    out = ["# Parts list (working copy)", "",
           "Your decisions on every part I suggested. **Edit this file** (on GitHub: open it → ✏️ → *Commit changes*); "
           "everything else follows: `bom.csv`, budget, checklists (`make`, or the *parts-sync* action on GitHub within a minute).", "",
           "**How to edit a line**", "",
           "- Tick `[x]` = you agree; untick = back to `suggested`.",
           "- Or change the word after `status:` to one of: `suggested` · `agreed` · `ordered` · `have` · `swap` (you want another part: "
           "say which in `note:`) · `skip` (not using it). For printed parts, `have` = printed.",
           "- `paid:` what you really paid, shipping included (e.g. `paid: 27.40`). `note:` anything.",
           "- Only the `- [ ]` line, `note:` and `paid:` are read; the picture, *Must meet* and *why* lines are rewritten each time. "
           "New parts: `python tools/new.py part …`.",
           "- **Must meet** = what any substitute has to match (rating, size, focal length, …), so you can buy elsewhere safely. "
           "Pictures are drawings of the kind of part; the buy link shows the real product.", "",
           "<!-- parts-summary -->",
           "| Status | Parts | Core USD | Optional USD | Tools USD |", "|---|---:|---:|---:|---:|"]
    core = lambda rows: [r for r in rows if r["Type"] == "Purchase"]  # noqa: E731
    opt = lambda rows: [r for r in rows if r["Type"] == "Optional"]  # noqa: E731
    tl = lambda rows: [r for r in rows if r["Type"] == "Tool"]  # noqa: E731
    for s in STATUSES:
        out.append(f"| {s} | {len(by[s])} | ${tot(core(by[s])):.2f} | ${tot(opt(by[s])):.2f} | ${tot(tl(by[s])):.2f} |")
    left = [r for r in buyable if to_buy(r) or to_buy_tool(r)]
    out += [f"| **Still to buy** | {len(left)} | **${tot(core(left)):.2f}** | **${tot(opt(left)):.2f}** | **${tot(tl(left)):.2f}** |",
            f"| Paid so far | | ${paid:.2f} | | |",
            f"| Plan: every core part bought (cap ${bom_check.HARD_CAP:.0f}) | | ${plan:.2f} | | |", "",
            "Still to buy = core parts not `ordered` / `have` / `swap` / `skip`, plus optional parts you `agreed` to. "
            "Tools are bought once and kept: they have their own total and are not in the machine cap.", ""]
    for stage, rows in boms.items():
        buy = [r for r in rows if r["Type"] in ("Purchase", "Optional", "Tool")]
        prn = [r for r in rows if r["Type"] in ("Print", "Owned")]
        n_dec = sum(r["Status"] != "suggested" for r in rows)
        out += [f"## {stage[:2]} · {titles.get(stage, stage)}", "",
                f"{n_dec}/{len(rows)} decided · still to buy ${tot([r for r in buy if to_buy(r)]):.2f} · "
                f"[bom.csv](phases/{stage}/bom.csv) · [checklist](phases/{stage}/README.md)", ""]
        for r in buy + prn:
            shop = r["Link"].split("/")[2].removeprefix("www.").removeprefix("us.") if r["Link"].startswith("http") else ""
            link = f" · [buy at {shop}]({r['Link']})" if shop else ""
            qty = r["Qty"]
            price = (f"{qty} × ${float(r['Unit USD']):.2f} = ${float(r['Total USD']):.2f}" if float(r["Unit USD"])
                     else "tool you supply" if r["ID"].startswith("TLS-") else "you supply" if r["Type"] == "Owned"
                     else "$0 (in another row)" if r["Type"] in ("Purchase", "Optional") else r["Type"].lower())
            kind = " · optional" if r["Type"] == "Optional" else " · print" if r["Type"] == "Print" else " · tool" if r["Type"] == "Tool" else ""
            out.append(f"- [{'x' if r['Status'] in CHECKED else ' '}] **{r['ID']}** {r['Part']} — {price}{kind}{link} · status: {r['Status']}")
            why = r["Use"] + (f" · {r['Notes']}" if r["Notes"] else "")
            files = f" · files: [{r['STEP'].split(';')[0].strip()}](phases/{stage}/{r['STEP'].split(';')[0].strip()})" \
                if r["Type"] == "Print" and r["STEP"].startswith("3d/") else ""
            out.append(f'  - <img src="{part_images.image_for(r)}" width="64" height="64" alt="{r["ID"]}"> '
                       f"**Qty {r['Qty']}** · **Must meet:** {r.get('Requirement', '')}{files}")
            out.append(f"  - *why:* {why}")
            out.append(f"  - note: {r.get('_note', '')}".rstrip())
            if r["Type"] in ("Purchase", "Optional", "Tool"):
                out.append(f"  - paid: {r['Paid USD']}".rstrip())
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=Path, help="older phases/ folder to take Own / Paid USD from (first run)")
    ap.add_argument("--set", nargs="+", metavar=("STATUS", "ID"),
                    help="set a status on part IDs without editing PARTS.md by hand, e.g. --set have PWR-30 CTL-01")
    a = ap.parse_args(argv)
    if DOC.exists():
        decisions = read_doc(DOC.read_text(encoding="utf-8"))
    else:
        decisions = seed(a.seed) if a.seed else {}
    if a.set:
        status, ids = a.set[0], a.set[1:]
        known = {r["ID"] for f in sorted(ROOT.glob("phases/*/bom.csv")) for r in csv.DictReader(f.open(encoding="utf-8"))}
        if status not in STATUSES or not ids or set(ids) - known:
            ap.error(f"--set needs one of {', '.join(STATUSES)} and known part IDs (unknown: {sorted(set(ids) - known)})")
        for i in ids:
            decisions[i] = {**decisions.get(i, {"note": "", "paid": ""}), "status": status}
    boms = apply(decisions)
    DOC.write_text(render(boms), encoding="utf-8")
    readme = ROOT / "README.md"
    t = readme.read_text(encoding="utf-8")
    if "<!-- budget:start -->" in t:
        rows = [r for v in boms.values() for r in v]
        core = [r for r in rows if r["Type"] == "Purchase"]
        f = lambda rr: sum(float(r["Total USD"]) for r in rr)  # noqa: E731
        kits = {"spectral sensor": [r for r in rows if r["ID"].startswith("SPC-") and r["Type"] == "Optional"],
                "standalone kit": [r for r in rows if r["ID"].startswith("STA-") and r["Type"] == "Optional"],
                "no-switching camera kit": [r for r in rows if r["ID"] in ("CAM-04", "CAM-05")],
                "colour kit (bands + polarizers)": [r for r in rows if r["ID"].startswith("MSK-") and r["Type"] == "Optional"]}
        tools = [r for r in rows if r["Type"] == "Tool"]
        body = (f"| Plan (every core part bought) | Still to buy | Have / ordered | Paid so far | Decided | Tools to buy (kept, separate) |\n|---:|---:|---:|---:|---:|---:|\n"
                f"| ${f(core):.2f} | ${f([r for r in rows if to_buy(r)]):.2f} | "
                f"${f([r for r in core if r['Status'] in ('have', 'ordered')]):.2f} | "
                f"${sum(float(r['Paid USD']) for r in rows if r['Paid USD']):.2f} | "
                f"{sum(r['Status'] != 'suggested' for r in rows)}/{len(rows)} parts | ${f([r for r in tools if to_buy_tool(r)]):.2f} |\n\n"
                + " · ".join(f"Optional {k} +\\${f(v):.2f}" for k, v in kits.items()))
        t = re.sub(r"\$\d+\.\d\d total \(cap \$\d+\)", f"${f(core):.2f} total (cap ${bom_check.HARD_CAP:.0f})", t)   # intro line
        head, rest = t.split("<!-- budget:start -->", 1)
        readme.write_text(f"{head}<!-- budget:start -->\n{body}\n<!-- budget:end -->{rest.split('<!-- budget:end -->', 1)[1]}",
                          encoding="utf-8")
    left = sum(float(r["Total USD"]) for rows in boms.values() for r in rows if to_buy(r))
    print(f"PARTS.md: {sum(len(v) for v in boms.values())} parts, still to buy ${left:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
