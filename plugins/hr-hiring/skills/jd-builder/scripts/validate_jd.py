#!/usr/bin/env python3
"""Check a jd.json against the skeleton before it is rendered.

Checks the shape, the fixed parts (labels, trait titles, level keys), the
word and item limits in structure/skeleton.json, house punctuation, banned
phrases, and that every must-include item from the intake made it in.

    python3 validate_jd.py jd.json [--must-include intake.json]

Exit code 0 = pass. Prints one line per problem, then a JSON summary.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKEL = json.loads((ROOT / "structure/skeleton.json").read_text())
LIM = SKEL["limits"]
S = SKEL["sections"]
BANNED = [l.strip().lower() for l in (ROOT / "voice/banned-phrases.txt").read_text().splitlines()
          if l.strip() and not l.startswith("#")]
REQUIRED = json.loads((ROOT / "structure/jd.schema.json").read_text())["required"]

problems = []


def bad(where, msg):
    problems.append(f"{where}: {msg}")


def plain(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return re.sub(r"[*_]{1,2}", "", s)


def words(s):
    return len(plain(s or "").split())


def span(where, text, rng):
    n = words(text)
    if not rng[0] <= n <= rng[1]:
        bad(where, f"{n} words, want {rng[0]}–{rng[1]}")


def items(where, lst, spec, key=None):
    lo, hi = spec["count"] if "count" in spec else (0, 999)
    if not lo <= len(lst) <= hi:
        bad(where, f"{len(lst)} items, want {lo}–{hi}")
    if "words" in spec:
        for i, it in enumerate(lst):
            span(f"{where}[{i}]", it[key] if key else it, spec["words"])


def all_text(jd):
    out = []

    def walk(x):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, list):
            for y in x:
                walk(y)
        elif isinstance(x, dict):
            for k, y in x.items():
                if k != "schema_version":
                    walk(y)
    walk(jd)
    return out


def check(jd, must_include=()):
    for k in REQUIRED:
        if k not in jd:
            bad(k, "missing")
    if problems:
        return

    h = jd["header"]
    span("header.lead", h["lead"], LIM["header.lead"])
    span("header.punchline", h["punchline"], LIM["header.punchline"])

    labels = [m["label"] for m in jd["meta"]]
    if labels[:4] != S["meta"]["fixed_labels"]:
        bad("meta", f"first four labels must be {S['meta']['fixed_labels']}, got {labels[:4]}")
    if len(labels) != 5 or labels[4] not in S["meta"]["fifth_label_options"]:
        bad("meta", f"fifth label must be one of {S['meta']['fifth_label_options']}")
    exp = next((m["value"] for m in jd["meta"] if m["label"] == "EXPERIENCE"), "")
    if not re.fullmatch(r"\d+(–\d+|\+) years", exp):
        bad("meta.EXPERIENCE", f"'{exp}' should look like '0–2 years' or '6+ years' (en dash)")

    r = jd["the_role"]
    span("the_role.lead", r["lead"], LIM["the_role.lead"])
    items("the_role.paragraphs", r["paragraphs"], LIM["the_role.paragraphs"])

    lv = jd["the_level"]
    span("the_level.lead", lv["lead"], LIM["the_level.lead"])
    items("the_level.rows", lv["rows"], LIM["the_level.rows"], key="text")
    keys = [x["key"] for x in lv["rows"]]
    if keys[:5] != S["the_level"]["fixed_keys"]:
        bad("the_level.rows", f"first five keys must be {S['the_level']['fixed_keys']}")
    if len(keys) == 6 and keys[5] not in S["the_level"]["sixth_key_options"]:
        bad("the_level.rows", f"sixth key must be one of {list(S['the_level']['sixth_key_options'])}")

    w = jd["your_work"]
    items("your_work.groups", w["groups"], LIM["your_work.groups"])
    for g in w["groups"]:
        if g["label"] != g["label"].upper():
            bad(f"your_work.{g['label']}", "group label must be upper case")
        items(f"your_work.{g['label']}", g["bullets"], LIM["your_work.bullets"])
    last = w["groups"][-1]["label"] if w["groups"] else ""
    if last not in ("GROW", "MULTIPLY", "LEAD"):
        bad("your_work", f"last group must be GROW, MULTIPLY or LEAD, got {last}")

    b = jd["the_bar"]
    span("the_bar.intro", b["intro"], LIM["the_bar.intro"])
    items("the_bar.traits", b["traits"], LIM["the_bar.traits"], key="text")
    titles = [t["title"] for t in b["traits"]]
    if titles != S["the_bar"]["fixed_trait_titles"]:
        bad("the_bar.traits", f"titles must be exactly {S['the_bar']['fixed_trait_titles']}")

    a = jd["ai"]
    span("ai.lead", a["lead"], LIM["ai.lead"])
    if not any(a["lead"].startswith(o) for o in S["ai"]["fixed_opener"].values()):
        bad("ai.lead", f"must start with one of {list(S['ai']['fixed_opener'].values())}")
    items("ai.bullets", a["bullets"], LIM["ai.bullets"])

    m = jd["minimum"]
    if m.get("note"):
        span("minimum.note", m["note"], LIM["minimum.note"])
    items("minimum.items", m["items"], LIM["minimum.items"])
    for i, it in enumerate(m["items"]):
        if "**" not in it:
            bad(f"minimum.items[{i}]", "needs a **bold lead phrase**")
    if m["items"] and not re.match(r"\*\*\d", m["items"][0]):
        bad("minimum.items[0]", "must open with the experience range in bold, e.g. **6+ years**")

    items("preferred.items", jd["preferred"]["items"], LIM["preferred.items"])

    tk = jd["toolkit"]
    if tk.get("note"):
        span("toolkit.note", tk["note"], LIM["toolkit.note"])
    items("toolkit.rows", tk["rows"], LIM["toolkit.rows"])
    for row in tk["rows"]:
        if row["key"] != row["key"].lower():
            bad(f"toolkit.{row['key']}", "row key must be lower case")

    asm = jd["assessment"]
    span("assessment.lead", asm["lead"], LIM["assessment.lead"])
    if not asm["lead"].startswith("Six dimensions."):
        bad("assessment.lead", "must start with 'Six dimensions.'")
    items("assessment.cards", asm["cards"], LIM["assessment.cards"], key="text")
    for c in asm["cards"]:
        span(f"assessment.{c['title']}.title", c["title"], LIM["assessment.cards"]["title_words"])

    nfy = jd["not_for_you"]["items"]
    items("not_for_you.items", nfy, LIM["not_for_you.items"])
    for i, it in enumerate(nfy):
        if not it.startswith("You"):
            bad(f"not_for_you.items[{i}]", "must start with 'You'")
    if nfy and "hospital admission. That's the seriousness this team runs at." not in nfy[-1]:
        bad("not_for_you.items[-1]", "last item must be the fixed hospital-admission line")

    if jd["footer_tag"] != jd["footer_tag"].upper() or jd["footer_tag"].count(" · ") != 2:
        bad("footer_tag", "must be 'LEVEL · SPECIALISATION · CITY' in upper case")

    # House punctuation and phrasing across all text
    text = all_text(jd)
    body = " ".join(plain(t) for t in text)
    n_words = len(body.split())
    dashes = body.count("—")
    if dashes / max(n_words, 1) * 100 > LIM["em_dash_per_100_words"]:
        bad("style", f"{dashes} em dashes in {n_words} words; cap is {LIM['em_dash_per_100_words']} per 100")
    for t in text:
        p = plain(t)
        if re.search(r"\w—|—\w", p):
            bad("style", f"em dash needs a space either side: '{p[:60]}'")
        if " - " in p:
            bad("style", f"use ' — ' not ' - ': '{p[:60]}'")
        if re.search(r"\d-\d", p) and "years" in p:
            bad("style", f"ranges take an en dash (0–2): '{p[:60]}'")
        if "  " in t:
            bad("style", f"double space: '{p[:60]}'")
        if t.count("**") % 2 or (t.count("__") % 2):
            bad("markup", f"unbalanced bold markers: '{t[:60]}'")
    low = body.lower()
    for phrase in BANNED:
        if re.search(r"\b" + re.escape(phrase) + r"\b", low):
            bad("banned", f"'{phrase}'")
    us = re.findall(r"\b(center|judgment|defense|organization|organize|optimize|prioritize|analyze|color|behavior|favorite|program(?!m))\b", low)
    for wd in sorted(set(us)):
        bad("spelling", f"US spelling '{wd}', house style is British English")

    for item in must_include:
        if item.lower() not in low:
            bad("must_include", f"'{item}' from the intake is missing")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    jd = json.loads(Path(args[0]).read_text())
    must = []
    if "--must-include" in args:
        intake = json.loads(Path(args[args.index("--must-include") + 1]).read_text())
        must = intake.get("must_include", [])
    check(jd, must)
    for p in problems:
        print("FAIL", p)
    print(json.dumps({"file": args[0], "pass": not problems, "problems": len(problems)}))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
