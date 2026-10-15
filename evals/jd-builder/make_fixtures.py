#!/usr/bin/env python3
"""Write placeholder JD files: every block at its minimum size, and every block
filled as far as the total word ceiling allows. They carry no real content, only neutral filler, so they test the layout
without suggesting any wording."""
import json
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / "plugins/hr-hiring/skills/jd-builder"
LIM = json.loads((SKILL / "structure/skeleton.json").read_text())["limits"]
WORDS = "layout test words fill this block to check spacing and wrapping on the page".split()


def text(n, start=0):
    out = [WORDS[(start + i) % len(WORDS)] for i in range(n)]
    out[0] = out[0].capitalize()
    return " ".join(out) + "."


def make(pick):
    def w(key, sub="words"):
        v = LIM[key]
        rng = v if isinstance(v, list) else v[sub]
        return pick(rng)

    def c(key):
        return pick(LIM[key]["count"])

    def bullets(key, n=None):
        return [text(w(key), i) for i in range(n or c(key))]

    return {
        "schema_version": "1.0",
        "header": {"function": "Function", "city": "Bengaluru", "title": " ".join(["Layout"] * w("header.title")),
                   "lead": text(w("header.lead")), "punchline": text(w("header.punchline"))},
        "meta": [{"label": "LEVEL", "value": "Level"}, {"label": "TRACK", "value": "Individual contributor"},
                 {"label": "EXPERIENCE", "value": "3–5 years"}, {"label": "LOCATION", "value": "Bengaluru"},
                 {"label": "TOOLS", "value": "Tool · Tool · Tool"}],
        "the_role": {"lead": text(w("the_role.lead")), "paragraphs": bullets("the_role.paragraphs")},
        "the_level": {"level_name": "Level", "lead": text(w("the_level.lead")),
                      "rows": [{"key": f"KEY{chr(65 + i)}", "text": text(w("the_level.rows"), i)} for i in range(6)]},
        "your_work": {"heading": "What you'll own",
                      "groups": [{"label": f"GROUP {chr(65 + g)}", "bullets": bullets("your_work.bullets")}
                                 for g in range(c("your_work.groups"))]},
        "the_bar": {"intro": text(w("the_bar.intro")),
                    "traits": [{"title": " ".join(["Trait"] * w("the_bar.traits", "title_words")),
                                "text": text(w("the_bar.traits"), i)} for i in range(5)]},
        "ai": {"lead": text(w("ai.lead")), "bullets": bullets("ai.bullets")},
        "minimum": {"note": text(max(w("minimum.note"), 5)),
                    "items": ["**Bold phrase** " + text(w("minimum.items") - 2, i).lower() for i in range(c("minimum.items"))]},
        "preferred": {"items": bullets("preferred.items")},
        "toolkit": {"label": "OUR TOOLS", "note": text(max(w("toolkit.note"), 5)),
                    "rows": [{"key": f"category {i}", "value": "Tool one, Tool two, Tool three"} for i in range(c("toolkit.rows"))]},
        "assessment": {"lead": text(w("assessment.lead")),
                       "cards": [{"title": " ".join(["Card"] * w("assessment.cards", "title_words")),
                                  "text": text(w("assessment.cards"), i)} for i in range(6)]},
        "not_for_you": {"items": bullets("not_for_you.items")},
        "footer_tag": "LEVEL · LAYOUT · BENGALURU",
    }


def total(jd):
    out = []

    def walk(x):
        if isinstance(x, str):
            out.append(len(x.replace("*", "").split()))
        elif isinstance(x, list):
            [walk(y) for y in x]
        elif isinstance(x, dict):
            [walk(y) for k, y in x.items() if k != "schema_version"]
    walk(jd)
    return sum(out)


def ceiling():
    """The largest fill (between every block's min and max) that stays under total_words."""
    best = None
    for step in range(0, 101):
        f = step / 100
        jd = make(lambda r, f=f: round(r[0] + f * (r[1] - r[0])))
        if total(jd) > LIM["total_words"]:
            break
        best = jd
    return best


out = Path(__file__).resolve().parent / "fixtures"
for name, jd in (("layout-min", make(lambda r: r[0])), ("layout-max", ceiling())):
    (out / f"{name}.json").write_text(json.dumps(jd, indent=2, ensure_ascii=False) + "\n")
    print("wrote", name, total(jd), "words")
