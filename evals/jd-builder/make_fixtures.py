#!/usr/bin/env python3
"""Write placeholder JD files that fill every block at its minimum and maximum
size. They carry no real content, only neutral filler, so they test the layout
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


out = Path(__file__).resolve().parent / "fixtures"
for name, pick in (("layout-min", lambda r: r[0]), ("layout-max", lambda r: r[1])):
    (out / f"{name}.json").write_text(json.dumps(make(pick), indent=2, ensure_ascii=False) + "\n")
    print("wrote", name)
