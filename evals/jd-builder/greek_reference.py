#!/usr/bin/env python3
"""Make the designer's reference images: render a blueprint PDF page and
replace every word with a bar in the word's own colour, so the layout,
colours and spacing are visible but no wording is.

    python3 greek_reference.py blueprint.pdf out_dir
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import pdfplumber
from PIL import Image, ImageDraw

DPI = 60


def main(pdf, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    scale = DPI / 72
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", str(DPI), "-png", pdf, f"{tmp}/p"], check=True)
        doc = pdfplumber.open(pdf)
        for i, page in enumerate(doc.pages, start=1):
            img = Image.open(sorted(Path(tmp).glob("p-*.png"))[i - 1]).convert("RGB")
            draw = ImageDraw.Draw(img)
            for ch in page.chars:
                if not ch["text"].strip():
                    continue
                size = ch["size"] * scale
                x0, x1 = ch["x0"] * scale, ch["x1"] * scale
                top = ch["top"] * scale
                bg = img.getpixel((min(max(int(x0) - 1, 0), img.width - 1), min(int(top + size * 0.55), img.height - 1)))
                draw.rectangle([x0 - 0.6, top - 0.5, x1 + 0.6, top + size * 1.05], fill=bg)
            for ch in page.chars:
                if not ch["text"].strip():
                    continue
                size = ch["size"] * scale
                x0, x1 = ch["x0"] * scale, ch["x1"] * scale
                top = ch["top"] * scale
                c = ch["non_stroking_color"] or (0,)
                if len(c) == 1:
                    c = (c[0],) * 3
                rgb = tuple(int(round(v * 255)) for v in c[:3])
                mid = top + size * 0.55
                h = max(size * 0.3, 1.2)
                draw.rectangle([x0, mid - h / 2, x1 + 0.4, mid + h / 2], fill=rgb)
            img.convert("P", palette=Image.ADAPTIVE, colors=48).save(out / f"layout-page-{i}.png", optimize=True)
            print("wrote", out / f"layout-page-{i}.png")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
