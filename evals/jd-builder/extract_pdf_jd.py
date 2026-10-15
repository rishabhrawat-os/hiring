#!/usr/bin/env python3
"""Turn an Onsurity-format JD PDF back into jd.json.

Reads the type styles (font, size, colour, x position) that the house layout
uses, so it only works on PDFs made from this layout. Used to build the
examples/ and to import an existing JD for a revision.

    python3 extract_pdf_jd.py in.pdf out.json
"""
import json
import re
import sys
from collections import defaultdict

try:
    import pdfplumber
except ImportError:
    sys.exit("pdfplumber is missing: pip install pdfplumber")

LABEL_X = 150          # anything left of this is the section-label gutter
CONTENT_X = 155.0      # content column starts here


def hexcol(c):
    if not c:
        return None
    if len(c) == 1:
        c = (c[0],) * 3
    return "#" + "".join(f"{round(v * 255):02X}" for v in c[:3])


def style_of(ch):
    name = ch["fontname"].split("+")[-1]
    if "Mono" in name:
        fam = "mono"
    elif "Archivo" in name:
        fam = "sans-bold" if "Bold" in name and "Semi" not in name else "sans"
    elif "Italic" in name:
        fam = "serif-italic"
    elif "wght258" in name:          # Newsreader at weight 600
        fam = "serif-strong"
    else:
        fam = "serif"
    return fam, round(ch["size"], 1), hexcol(ch["non_stroking_color"])


class Line:
    def __init__(self, page, top, x0):
        self.page, self.top, self.x0 = page, top, x0
        self.runs = []      # (x0, x1, style, text)

    @property
    def style(self):
        return self.runs[0][2]

    def text(self, marks=True):
        out, prev_x1 = "", None
        for x0, x1, st, t in self.runs:
            if prev_x1 is not None and x0 - prev_x1 > 0.18 * st[1] and not out.endswith(" ") and not t.startswith(" "):
                out += " "
            if marks:
                fam = st[0]
                body = "serif"
                if fam == "sans" and body.startswith("serif"):
                    t = f"**{t.strip()}**" + (" " if t.endswith(" ") else "")
                    if t.startswith("**") and out and not out.endswith((" ", "(", "—")):
                        out += " "
                elif fam == "serif-strong":
                    t = f"__{t.strip()}__" + (" " if t.endswith(" ") else "")
                elif fam == "serif-italic" and body != "serif-italic":
                    t = f"*{t.strip()}*" + (" " if t.endswith(" ") else "")
            out += t
            prev_x1 = x1
        return tidy(out)


def tidy(s):
    s = re.sub(r"\*\*\s*\*\*", " ", s)
    s = re.sub(r"__\s*__", " ", s)
    s = re.sub(r"(?<!\*)\*\s+\*(?!\*)", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def lines_of(pdf):
    """Group characters into visual lines, split by column gaps."""
    out = []
    for pi, page in enumerate(pdf.pages):
        chars = sorted(page.chars, key=lambda c: (round(c["bottom"]), c["x0"]))
        rows = defaultdict(list)
        for c in chars:
            key = round(c["bottom"] / 2.5)
            rows[key].append(c)
        merged = {}
        for key in sorted(rows):
            hit = next((k for k in merged if abs(k - key) <= 1), None)
            merged.setdefault(hit if hit is not None else key, []).extend(rows[key])
        for key, cs in merged.items():
            cs.sort(key=lambda c: c["x0"])
            cur = None
            for c in cs:
                st = style_of(c)
                gap = c["x0"] - cur.runs[-1][1] if cur else 0
                if cur is None or gap > 14 or (cur.x0 < LABEL_X <= c["x0"] and gap > 5):
                    cur = Line(pi, min(x["top"] for x in cs), c["x0"])
                    out.append(cur)
                if cur.runs and cur.runs[-1][2] == st and c["x0"] - cur.runs[-1][1] < 0.18 * st[1]:
                    x0, _, s, t = cur.runs[-1]
                    cur.runs[-1] = (x0, c["x1"], s, t + c["text"])
                else:
                    cur.runs.append((c["x0"], c["x1"], st, c["text"]))
        dashes = [(pi, r["x0"], r["top"]) for r in page.rects
                  if 4.5 < r["width"] < 6 and r["height"] < 2]
        for d in dashes:
            out.append(("dash",) + d)
    return out


def bullets_from(lines, dashes, col_x):
    """Join wrapped lines into bullets; a dash rect marks each bullet start."""
    items = []
    for ln in lines:
        starts = any(p == ln.page and abs(x - col_x) < 20 and -2 < top - ln.top < 12
                     for p, x, top in dashes)
        if starts or not items:
            items.append(ln.text())
        else:
            items[-1] = join(items[-1], ln.text())
    return items


def join(a, b):
    if a.endswith("-") and not a.endswith(" -") and b[:1].islower():
        return tidy(a + b)      # month-\nend is a real hyphen in these JDs, keep it
    return tidy(a + " " + b)


def paragraphs(lines, gap=17.5):
    paras, prev = [], None
    for ln in lines:
        new = prev is None or ln.page != prev.page or ln.top - prev.top > gap
        if new:
            paras.append(ln.text())
        else:
            paras[-1] = join(paras[-1], ln.text())
        prev = ln
    return paras


def extract(path):
    pdf = pdfplumber.open(path)
    items = lines_of(pdf)
    dashes = [(p, x, t) for kind, p, x, t in (i for i in items if isinstance(i, tuple))]
    lines = [i for i in items if isinstance(i, Line)]
    lines.sort(key=lambda l: (l.page, l.top, l.x0))

    # Split into the header block and labelled sections.
    sections, header = [], []
    for ln in lines:
        fam, size, col = ln.style
        if ln.x0 < 45 and fam == "mono" and size == 7.5 and col == "#8B93A5":
            if ln.text().startswith("ONSURITY TECHNOLOGIES"):
                sections.append({"label": "FOOTER", "lines": [ln]})
                continue
            sections.append({"label": ln.text(False), "lines": []})
        elif sections:
            sections[-1]["lines"].append(ln)
        else:
            header.append(ln)

    jd = {}

    # Header: eyebrow, title, lead + punchline, meta panel.
    eyebrow = sorted([l for l in header if l.style[0] == "mono" and l.style[1] == 7.5], key=lambda l: l.x0)
    jd["eyebrow"] = {"function": eyebrow[1].text(False).title() if len(eyebrow) > 1 else "",
                     "city": eyebrow[2].text(False).title() if len(eyebrow) > 2 else ""}
    jd["title"] = " ".join(l.text(False) for l in header if l.style[0] == "sans-bold")
    lead = [l for l in header if l.style[1] in (11.0, 10.6)]
    lead_txt, punch = "", ""
    for l in lead:
        if punch and not punch.endswith(" "):
            punch += " "
        for x0, x1, st, t in l.runs:
            if st[0] == "sans":
                punch += t
            else:
                lead_txt += (" " if lead_txt and not lead_txt.endswith(" ") else "") + t
    jd["lead"] = re.sub(r"\s+", " ", lead_txt).strip()
    jd["punchline"] = re.sub(r"\s+", " ", punch).strip()
    labels = [l for l in header if l.style[0] == "mono" and l.style[1] == 6.5]
    values = [l for l in header if l.style[0] == "sans" and l.style[1] == 9.0]
    meta = []
    for lab in sorted(labels, key=lambda l: l.x0):
        vals = [v for v in values if abs(v.x0 - lab.x0) < 5]
        meta.append({"label": lab.text(False), "value": " ".join(v.text(False) for v in vals)})
    jd["meta"] = meta

    def body(sec):
        return [l for l in sec["lines"] if l.style[0].startswith("serif") or (l.style[0] == "sans" and l.style[1] == 9.0)]

    for sec in sections:
        lab, ls = sec["label"], sec["lines"]
        head = next((l.text(False) for l in ls if l.style[1] == 14.0), None)
        sec_lead = [l for l in ls if l.style[1] == 10.5 and l.style[2] == "#59637A"]
        lead_p = paragraphs(sec_lead)[0] if sec_lead else None
        rest = [l for l in ls if l not in sec_lead]
        if lab == "ABOUT US":
            jd["about_us"] = "static"
        elif lab == "THE ROLE":
            jd["role"] = {"heading": head, "lead": lead_p,
                          "paragraphs": paragraphs([l for l in rest if l.style[1] in (9.0, 9.5)])}
        elif lab == "THE LEVEL":
            keys = [l for l in rest if l.style[0] == "mono"]
            descs = [l for l in rest if l.style[0] == "serif"]
            rows = []
            for k in keys:
                nxt = [k2.top for k2 in keys if (k2.page, k2.top) > (k.page, k.top)]
                end = min(nxt) if nxt else 1e9
                d = [x for x in descs if x.page == k.page and k.top - 4 <= x.top < end - 4]
                rows.append({"key": k.text(False), "text": paragraphs(d, 20)[0] if d else ""})
            jd["level"] = {"heading": head, "lead": lead_p, "rows": rows}
        elif lab == "YOUR WORK":
            groups, cur = [], None
            for l in rest:
                if l.style[0] == "mono" and l.style[2] == "#4076E2":
                    cur = {"label": l.text(False), "lines": []}
                    groups.append(cur)
                elif cur and l.style[1] != 14.0:
                    cur["lines"].append(l)
            jd["work"] = {"heading": head, "groups": [
                {"label": g["label"], "bullets": bullets_from(g["lines"], dashes, 157)} for g in groups]}
        elif lab == "THE BAR":
            intro = [l for l in rest if l.style[0] == "serif" and l.style[2] == "#BCCAEB"]
            titles = [l for l in rest if l.style[0] == "sans" and l.style[1] == 10.0]
            traits = []
            for t in titles:
                nxt = [x.top for x in titles if (x.page, x.top) > (t.page, t.top)]
                end = min(nxt) if nxt else 1e9
                d = [x for x in intro if x.page == t.page and t.top < x.top < end]
                traits.append({"title": t.text(False), "text": paragraphs(d)[0] if d else ""})
            first_title = min((t.page, t.top) for t in titles)
            jd["bar"] = {"intro": paragraphs([x for x in intro if (x.page, x.top) < first_title])[0],
                         "traits": traits}
        elif lab == "AI":
            jd["ai"] = {"lead": lead_p, "bullets": bullets_from([l for l in rest if l.style[1] in (9.0, 9.5)], dashes, 157)}
        elif lab == "MINIMUM":
            b = [l for l in rest if l.style[1] in (9.5, 9.0)]
            left = [l for l in b if l.x0 < 360]
            right = [l for l in b if l.x0 >= 360]
            jd["minimum"] = {"note": lead_p,
                             "items": bullets_from(left, dashes, 157) + bullets_from(right, dashes, 372)}
        elif lab == "PREFERRED":
            jd["preferred"] = {"items": bullets_from([l for l in rest if l.style[1] in (9.0, 9.5)], dashes, 157)}
        elif lab in ("OUR STACK", "OUR TOOLS"):
            keys = [l for l in rest if l.style[0] == "mono" and l.style[2] == "#8B93A5"]
            vals = [l for l in rest if l.style[0] == "mono" and l.style[2] == "#1A1F2E"]
            rows = [{"key": k.text(False), "value": " ".join(v.text(False) for v in vals if v.page == k.page and abs(v.top - k.top) < 3)} for k in keys]
            jd["stack"] = {"label": lab, "note": lead_p, "rows": rows}
        elif lab == "THE BAR, TESTED":
            cards_l = [l for l in rest if l.style[1] in (9.5, 9.0)]
            cards = []
            title_lines = [l for l in cards_l if l.style[0] == "sans"]
            # rows of cards: cluster title lines by (page, top)
            row_tops = sorted({(l.page, round(l.top)) for l in title_lines})
            row_starts = []
            for rt in row_tops:
                if not row_starts or rt[0] != row_starts[-1][0] or rt[1] - row_starts[-1][1] > 40:
                    row_starts.append(rt)
            for ri, rs in enumerate(row_starts):
                end = row_starts[ri + 1] if ri + 1 < len(row_starts) else (99, 0)
                in_row = [l for l in cards_l if rs <= (l.page, round(l.top)) < end]
                for cx in sorted({round(l.x0) for l in in_row if l.style[0] == "sans" and (l.page, round(l.top)) == rs}):
                    col = [l for l in in_row if abs(l.x0 - cx) < 10]
                    t = " ".join(l.text(False) for l in col if l.style[0] == "sans")
                    d = " ".join(l.text(False) for l in col if l.style[0] != "sans")
                    cards.append({"title": t, "text": re.sub(r"\s+", " ", d).strip()})
            jd["assessment"] = {"lead": lead_p, "cards": cards}
        elif lab == "READ TWICE":
            jd["not_for_you"] = {"items": bullets_from([l for l in rest if l.style[1] in (9.0, 9.5)], dashes, 174)}
        elif lab == "EQUAL OPPORTUNITY":
            jd["eeo"] = "static"
        elif lab == "FOOTER":
            jd["footer_tag"] = sec["lines"][0].text(False)
    # Footer middle part, e.g. "SDE III · JAVA · BENGALURU"
    foot = [l for l in lines if l.style[0] == "mono" and l.x0 > LABEL_X and l.style[1] == 7.5 and "·" in l.text(False)]
    if foot:
        jd["footer_tag"] = foot[-1].text(False)
    return jd


def to_schema(raw):
    """Map the raw extraction onto structure/jd.schema.json."""
    level = raw["level"]["heading"].removeprefix("What ").removesuffix(" means here")
    return {
        "schema_version": "1.0",
        "header": {
            "function": raw["eyebrow"]["function"],
            "city": raw["eyebrow"]["city"],
            "title": raw["title"],
            "lead": raw["lead"],
            "punchline": raw["punchline"],
        },
        "meta": raw["meta"],
        "the_role": {"lead": raw["role"]["lead"], "paragraphs": raw["role"]["paragraphs"]},
        "the_level": {"level_name": level, "lead": raw["level"]["lead"], "rows": raw["level"]["rows"]},
        "your_work": {"heading": raw["work"]["heading"],
                      "groups": [{"label": g["label"], "bullets": g["bullets"]} for g in raw["work"]["groups"]]},
        "the_bar": raw["bar"],
        "ai": raw["ai"],
        "minimum": {k: v for k, v in raw["minimum"].items() if v},
        "preferred": raw["preferred"],
        "toolkit": {k: v for k, v in raw["stack"].items() if v},
        "assessment": raw["assessment"],
        "not_for_you": raw["not_for_you"],
        "footer_tag": raw["footer_tag"],
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    jd = to_schema(extract(sys.argv[1]))
    with open(sys.argv[2], "w") as f:
        json.dump(jd, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {sys.argv[2]}")
