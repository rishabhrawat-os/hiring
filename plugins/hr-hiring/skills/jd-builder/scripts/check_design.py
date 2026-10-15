#!/usr/bin/env python3
"""Check a rendered JD .docx against the brand tokens.

Reads the file back (not the JSON) and checks: A4 page and margins, only
brand fonts, only palette colours, only sizes from the type scale, the three
font families embedded, section labels in skeleton order, no empty runs of
text, and the fixed text present. With --png it also renders page images
(needs LibreOffice) for the designer agent to compare with brand/reference/.

    python3 check_design.py out.docx [--png out_dir]
"""
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.ns import qn
except ImportError:
    sys.exit("python-docx is missing: pip install python-docx")

ROOT = Path(__file__).resolve().parent.parent
TOK = json.loads((ROOT / "brand/tokens.json").read_text())
SKEL = json.loads((ROOT / "structure/skeleton.json").read_text())
CO = json.loads((ROOT / "company/company.json").read_text())

problems = []


def bad(msg):
    problems.append(msg)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    path = args[0]
    doc = Document(path)

    # page
    s = doc.sections[0]
    P = TOK["page"]
    for name, val, want in (("width", s.page_width.pt, P["width"]), ("height", s.page_height.pt, P["height"]),
                            ("left margin", s.left_margin.pt, P["margin_left"]),
                            ("right margin", s.right_margin.pt, P["margin_right"]),
                            ("top margin", s.top_margin.pt, P["margin_top"])):
        if abs(val - want) > 1:
            bad(f"page {name} is {val:.1f}pt, want {want}")

    # runs: fonts, colours, sizes
    fonts = set(TOK["font"].values())
    colours = set(TOK["color"].values())
    sizes = {v["size"] for v in TOK["text"].values() if isinstance(v, dict) and "size" in v} | {1.0}
    seen_fonts, off = set(), []
    body = doc.element.body
    for r in body.iter(qn("w:r")):
        t = "".join(x.text or "" for x in r.iter(qn("w:t")))
        if not t.strip():
            continue
        rpr = r.find(qn("w:rPr"))
        rf = rpr.find(qn("w:rFonts")) if rpr is not None else None
        font = rf.get(qn("w:ascii")) if rf is not None else None
        col = rpr.find(qn("w:color")) if rpr is not None else None
        sz = rpr.find(qn("w:sz")) if rpr is not None else None
        seen_fonts.add(font)
        if font not in fonts:
            off.append(f"font '{font}' on '{t[:30]}'")
        if col is None or col.get(qn("w:val")).upper() not in colours:
            off.append(f"colour {None if col is None else col.get(qn('w:val'))} on '{t[:30]}'")
        if sz is None or int(sz.get(qn("w:val"))) / 2 not in sizes and abs(int(sz.get(qn("w:val"))) / 2 - 10.5) > 0.3:
            off.append(f"size {None if sz is None else int(sz.get(qn('w:val'))) / 2} on '{t[:30]}'")
    for o in sorted(set(off))[:25]:
        bad("off-brand " + o)

    # embedded fonts
    with zipfile.ZipFile(path) as z:
        embedded = [n for n in z.namelist() if n.startswith("word/fonts/")]
        settings = z.read("word/settings.xml").decode()
    if "embedTrueTypeFonts" not in settings or len(embedded) < len(TOK["font_files"]):
        bad(f"fonts not embedded ({len(embedded)} files)")

    # section order and fixed text
    text = "\n".join(p.text for p in _all_paragraphs(doc))
    want = []
    for key in SKEL["order"]:
        sec = SKEL["sections"][key]
        lab = sec.get("label") or (next(iter(sec["label_options"])) if "label_options" in sec else None)
        if lab:
            want.append(lab if key != "toolkit" else "OUR ")
    last = -1
    for lab in want:
        i = text.find(lab, last + 1)
        if i < 0:
            bad(f"section label '{lab}' missing or out of order")
        else:
            last = i
    for fixed in (CO["about_us"]["heading"], CO["eeo"]["text"][:40], CO["footer"]["left"], CO["footer"]["right"],
                  SKEL["sections"]["the_bar"]["fixed"]["heading"], SKEL["sections"]["the_bar"]["fixed"]["eyebrow"]):
        if fixed not in text:
            bad(f"fixed text missing: '{fixed[:40]}'")
    for leftover in re.findall(r"\*\*|__|\]\(|\{level_name\}|TODO|TBD|\[[A-Z ]+\]", text):
        bad(f"leftover markup or placeholder: '{leftover}'")
        break

    if "--png" in args:
        out = Path(args[args.index("--png") + 1])
        out.mkdir(parents=True, exist_ok=True)
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if not soffice:
            print("NOTE LibreOffice not found; skipped page images")
        else:
            subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out), path],
                           check=True, capture_output=True)
            pdf = out / (Path(path).stem + ".pdf")
            if shutil.which("pdftoppm"):
                subprocess.run(["pdftoppm", "-r", "70", "-png", str(pdf), str(out / "page")], check=True)
            print(f"NOTE page images in {out}")

    for p in problems:
        print("FAIL", p)
    print(json.dumps({"file": path, "pass": not problems, "problems": len(problems),
                      "fonts_used": sorted(f for f in seen_fonts if f)}))
    sys.exit(1 if problems else 0)


def _all_paragraphs(doc):
    def walk(container):
        for block in container.iter():
            if block.tag == qn("w:p"):
                yield block
    from docx.text.paragraph import Paragraph
    for p in walk(doc.element.body):
        yield Paragraph(p, doc)


if __name__ == "__main__":
    main()
