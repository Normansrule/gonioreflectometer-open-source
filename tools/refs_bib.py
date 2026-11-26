#!/usr/bin/env python3
"""Scholarly references (REFERENCES.md sections with IDs R1-R9, Sx, Gx, Tx, Vx, Nx, Hx) -> paper/references.bib,
then APA 7 text (pandoc citeproc + paper/apa.csl) -> wiki/Bibliography.md and wiki/Appendix-*.md, and
wiki/src/*.md (hand-written, cites as [@G12]) -> wiki/*.md with APA in-text citations and a reference list.
BibTeX keys are the reference IDs, so the paper cites \\parencite{G12} and the wiki shows the same ID.

    python tools/refs_bib.py

Parts, firmware and vendor sources stay in REFERENCES.md only. Needs pandoc >= 2.11.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main"   # wiki pages live outside the tree
REFS, BIB, CSL, WIKI = ROOT / "REFERENCES.md", ROOT / "paper" / "references.bib", ROOT / "paper" / "apa.csl", ROOT / "wiki"
SCHOLARLY = re.compile(r"^(R[1-9]|[SGTVNHX]\d+)$")
R_SECTIONS = {"Primary design references", "Theory and algorithms", "Other rigs and data"}   # R IDs that are literature
APPENDICES = [   # (page, title, ID prefixes)
    ("Appendix-A-Measurement", "Appendix A · Reflectance measurement and gonioreflectometers", ("R", "G")),
    ("Appendix-B-Reflectance-models", "Appendix B · Reflectance theory and models", ("T",)),
    ("Appendix-C-Calibration-and-3D", "Appendix C · Calibration, HDR, photometric stereo, 3D scanning", ("V", "S")),
    ("Appendix-D-Standards-and-colour", "Appendix D · Standards, colour, optics, safety", ("N",)),
    ("Appendix-E-Hardware", "Appendix E · Motion control, electronics, open hardware", ("H",)),
    ("Appendix-F-Mixed-reality", "Appendix F · Mixed reality, training and evaluation", ("X",)),
]
VENUE = {   # APA wants full journal / proceedings names
    "ACM TOG": "ACM Transactions on Graphics", "ACM TOG (SIGGRAPH)": "ACM Transactions on Graphics",
    "IEEE TPAMI": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
    "IEEE Trans. Robotics and Automation": "IEEE Transactions on Robotics and Automation",
    "IEEE J. Robotics and Automation": "IEEE Journal of Robotics and Automation",
    "IEEE Trans. Antennas and Propagation": "IEEE Transactions on Antennas and Propagation",
    "JCGT": "Journal of Computer Graphics Techniques", "IJCV": "International Journal of Computer Vision",
    "Rev. Sci. Instrum.": "Review of Scientific Instruments", "JOSA": "Journal of the Optical Society of America",
    "J. Opt. Soc. Am.": "Journal of the Optical Society of America", "JOSA A": "Journal of the Optical Society of America A",
    "J. Mathematical Imaging and Vision": "Journal of Mathematical Imaging and Vision",
    "J. Imaging Sci. Technol.": "Journal of Imaging Science and Technology", "J. Imaging": "Journal of Imaging",
    "Appl. Opt.": "Applied Optics", "SIAM J. Imaging Sciences": "SIAM Journal on Imaging Sciences",
    "J. Res. NIST": "Journal of Research of the National Institute of Standards and Technology",
    "J. Mechanisms and Robotics": "Journal of Mechanisms and Robotics",
    "J. Illuminating Engineering Society": "Journal of the Illuminating Engineering Society",
    "J. Electronic Imaging": "Journal of Electronic Imaging", "J. Coatings Technology": "Journal of Coatings Technology",
    "Int. J. Robotics Research": "International Journal of Robotics Research", "CVIU": "Computer Vision and Image Understanding",
    "Proc. CVPR": "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition",
    "CVPR": "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition",
    "ICCV": "Proceedings of the IEEE International Conference on Computer Vision", "ECCV": "European Conference on Computer Vision",
    "EGSR": "Eurographics Symposium on Rendering", "Proc. SPIE": "Proceedings of SPIE",
    "Color and Imaging Conf.": "Color and Imaging Conference", "Eurographics Symp. Geometry Processing": "Eurographics Symposium on Geometry Processing",
}
PROC = re.compile(r"Proc|SIGGRAPH|Symposium|Conference|EGSR|CVPR|ICCV|ECCV|SCIA|SSVM|Workshop|LNCS|Eurographics|"
                  r"Rendering Techniques|Course|Congress|Meeting", re.I)


def read_refs() -> list[dict]:
    out, sec = [], ""
    for line in REFS.read_text(encoding="utf-8").splitlines():
        h = re.match(r"^##+ (.+)$", line)
        if h:
            sec = h.group(1).strip()
            continue
        m = re.match(r"^\| \*\*([A-Z]+\d+)\*\* \| (.+?) \| (.*) \|$", line)
        if m and (SCHOLARLY.match(m.group(1)) or (m.group(1)[0] == "R" and sec in R_SECTIONS)):
            out.append({"id": m.group(1), "src": m.group(2), "use": m.group(3).strip(), "sec": sec})
    return out


def unmd(s: str) -> str:
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return re.sub(r"\s*\((?:bibliographic|slides provided|first draft)[^)]*\)", "", s).strip(" ,;—-")


def person(a: str) -> str:
    a = a.strip()
    if re.fullmatch(r"et al\.?", a):
        return "others"
    m = re.match(r"^((?:[A-Z][a-z]?\.(?:-[A-Z]\.)?\s*)+)(.+)$", a)
    return f"{m.group(2).strip()}, {m.group(1).strip()}" if m else "{" + a + "}"


def authors(s: str) -> str:
    s = s.replace(" et al.", ", et al.").replace(" and ", ", ")
    return " and ".join(person(a) for a in s.split(",") if a.strip())


PROPER = {"Pi", "Python", "Raspberry", "Monte", "Carlo", "Disney", "Unreal", "Lambert's", "Lambertian", "Phong", "Smith",
          "Fresnel", "Frostbite", "Imageworks", "Filament", "Matlab", "Euclidean", "Kronecker", "Bonn", "Gaussian",
          "Student's", "Torrance", "Sparrow", "Stanford", "European", "I", "Beckmann", "Trowbridge", "Reitz", "Lafortune",
          "Ward", "Oren", "Pico", "Zero", "Nayar", "Blinn", "Cook", "Schlick", "Poisson", "Zhang", "Tsai", "Fourier", "Bayesian", "Spectralon"}


def protect(t: str) -> str:
    """Keep acronyms, mixed-case names and proper nouns capitalised when APA sentence-cases a title."""
    def one(w: str) -> str:
        return "{" + w + "}" if (sum(c.isupper() for c in w) >= 2 or any(c.isdigit() for c in w) or w in PROPER
                                 or (len(w) == 1 and w.isupper() and w != "A")) else w
    return re.sub(r"[A-Za-z0-9’'][\w’']*", lambda m: one(m.group(0)), t)


def esc(s: str) -> str:
    return re.sub(r"([&%#_$])", r"\\\1", s.replace("*", ""))


def entry(r: dict) -> str:
    src = r["src"]
    bibpart, _, links = src.partition(" — ")
    doi = re.search(r"doi(?:\.org/|:)\s*\[?(10\.\d{4,}/[^\]\s)]+)", src, re.I)
    url = re.search(r"\((https?://[^)\s]+)\)", links or src)
    f: dict[str, str] = {}
    typ = "misc"
    b = bibpart.strip()
    m = re.match(r'^(?P<a>[^"“]+?),\s*["“](?P<t>.+?),?["”]\s*,?\s*(?P<r>.*)$', b)
    mb = re.match(r"^(?P<a>[^*\"]+?),\s*\*(?P<t>[^*]+)\*,?\s*(?P<r>.*)$", b)
    if m:
        f["author"], f["title"] = authors(m.group("a")), m.group("t").rstrip(",")
        rest = m.group("r")
        inb = re.match(r"^in \*(?P<bk>[^*]+)\*,?\s*(?P<x>.*)$", rest)
        ven = re.search(r"\*([^*]+)\*", rest)
        if inb:
            typ, f["booktitle"] = "incollection", inb.group("bk")
            x = inb.group("x")
            pub = re.match(r"^([^,]+),", x)
            if pub and not re.search(r"\d{4}", pub.group(1)):
                f["publisher"] = pub.group(1)
        elif ven:
            v = VENUE.get(ven.group(1).strip(), ven.group(1).strip())
            vol_follows = re.match(r"^\s*\d+\(\d+\)", rest[ven.end():])
            typ = "inproceedings" if PROC.search(v) and not vol_follows else "article"
            f["booktitle" if typ == "inproceedings" else "journal"] = v
            after = rest[ven.end():]
            vi = re.search(r"\b(\d+)(?:\((\d+)\))?(?::\s*([\w–-]+))?", after)
            if vi and typ == "article" and not re.fullmatch(r"(19|20)\d\d", vi.group(1)):
                f["volume"] = vi.group(1)
                if vi.group(2):
                    f["number"] = vi.group(2)
                if vi.group(3):
                    f["pages"] = vi.group(3).replace("–", "--")
        else:
            note = unmd(rest)
            if note:
                f["note"] = note
        pp = re.search(r"pp\. ([\d–-]+)", rest)
        if pp:
            f["pages"] = pp.group(1).replace("–", "--")
    elif mb:
        typ, f["author"], f["title"] = "book", authors(mb.group("a")), mb.group("t")
        rest = unmd(mb.group("r"))
        pub = re.match(r"^([^,\d]+?)(?:,|\s+\d{4}|$)", rest)
        if pub and pub.group(1).strip():
            f["publisher"] = pub.group(1).strip()
        ed = re.search(r"(\d+)(?:st|nd|rd|th) ed", rest)
        if ed:
            f["edition"] = ed.group(1)
    else:
        f["title"] = unmd(b)
        typ = "online" if url else "misc"
    yr = re.findall(r"\b((?:19|20)\d\d)\b", bibpart)
    if yr:
        f["year"] = yr[-1]
    if doi:
        f["doi"] = doi.group(1).rstrip(".,;")
    elif url:
        f["url"] = url.group(1)
    val = lambda k, v: v if k in ("url", "doi") else protect(esc(v)) if k == "title" else esc(v)
    body = ",\n".join(f"  {k} = {{{val(k, v)}}}" for k, v in f.items())
    return f"@{typ}{{{r['id']},\n{body}\n}}\n"


def apa(refs: list[dict]) -> dict[str, str]:
    """ID -> APA 7 reference in Markdown (one pandoc citeproc run)."""
    with tempfile.TemporaryDirectory() as td:
        md = Path(td) / "n.md"
        md.write_text("---\nnocite: |\n  " + ", ".join("@" + r["id"] for r in refs) + "\n---\n", encoding="utf-8")
        out = subprocess.run(["pandoc", str(md), "--citeproc", f"--csl={CSL}", f"--bibliography={BIB}", "-t", "html"],
                             capture_output=True, text=True, check=True).stdout
    res = {}
    for key, body in re.findall(r'<div id="ref-([^"]+)" class="csl-entry"[^>]*>\s*(.*?)\s*</div>', out, re.S):
        body = re.sub(r"<em>(.*?)</em>", r"*\1*", body, flags=re.S)
        body = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r"<\1>", body, flags=re.S)
        txt = html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"\s+", " ", body))).strip()
        res[key] = re.sub(r"Retrieved (<?https?://)", r"\1", txt)    # undated page: the URL alone
    return res


def build_pages() -> int:
    """wiki/src/*.md -> wiki/*.md: {{REPO}} -> repo URL, [@ID] -> APA in-text citation + reference list."""
    n = 0
    for src in sorted((WIKI / "src").glob("*.md")):
        text = src.read_text(encoding="utf-8").replace("{{REPO}}", REPO)
        head = f"<!-- generated from wiki/src/{src.name} by tools/refs_bib.py - edit the source -->\n\n"
        if src.name.startswith("_") or "[@" not in text and "@" not in re.sub(r"`[^`]*`", "", text):
            (WIKI / src.name).write_text(head + text, encoding="utf-8")
        else:
            out = subprocess.run(["pandoc", "-f", "markdown-implicit_figures", "-t", "gfm-raw_html", "--wrap=none", "--citeproc",
                                  f"--csl={CSL}", f"--bibliography={BIB}", "-M", "reference-section-title=References"],
                                 input=text, capture_output=True, text=True, check=True).stdout
            (WIKI / src.name).write_text(head + out.replace("\n# References\n", "\n## References\n"), encoding="utf-8")
        n += 1
    return n


def main() -> int:
    refs = read_refs()
    BIB.parent.mkdir(exist_ok=True)
    BIB.write_text("% Generated by tools/refs_bib.py from REFERENCES.md - edit REFERENCES.md, not this file.\n"
                   "% Keys = reference IDs.\n\n" + "\n".join(entry(r) for r in refs), encoding="utf-8")
    import shutil
    if not shutil.which("pandoc"):                             # bib written; APA wiki pages need pandoc
        print(f"paper/references.bib: {len(refs)} entries; wiki pages skipped (needs pandoc >= 2.11)")
        return 0
    text = apa(refs)
    order = list(text)                                         # pandoc order = APA alphabetical
    WIKI.mkdir(exist_ok=True)
    gen = "<!-- generated by tools/refs_bib.py from REFERENCES.md - edit that file, then `make build` -->"
    L = ["# Bibliography", "", gen, "", f"{len(order)} scholarly sources, APA 7th edition. `[G12]` = ID in "
         f"[REFERENCES.md]({REPO}/REFERENCES.md) and BibTeX key in [paper/references.bib]({REPO}/paper/references.bib). "
         "Topic lists with what each source is used for: " + " · ".join(f"[{t.split(' · ')[0]}]({p}.md)" for p, t, _ in APPENDICES) + ".", ""]
    L += [f"- {text[k]} `[{k}]`" for k in order]
    (WIKI / "Bibliography.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    for page, title, prefixes in APPENDICES:
        rows = [r for r in refs if r["id"].rstrip("0123456789") in prefixes and r["id"] in text]
        A = [f"# {title}", "", gen, "", f"Background papers and sources, by topic. Format: APA reference — *what this project uses it for*. "
             "Full list: [Bibliography](Bibliography.md).", ""]
        sec = None
        for r in rows:
            if r["sec"] != sec:
                sec = r["sec"]
                A += ["", f"## {sec}", ""]
            A.append(f"- {text[r['id']]} — *{unmd(r['use']) or 'background'}* `[{r['id']}]`")
        (WIKI / f"{page}.md").write_text("\n".join(A) + "\n", encoding="utf-8")
    pages = build_pages()
    missing = [r["id"] for r in refs if r["id"] not in text]
    print(f"paper/references.bib: {len(refs)} entries; wiki: {pages} pages + Bibliography + {len(APPENDICES)} appendices"
          + (f"; no APA text for {missing}" if missing else ""))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
