#!/usr/bin/env python3
"""Check a jd.json against the skeleton before it is rendered.

Checks the shape, the fixed labels, the space limits in
structure/skeleton.json, AI-writing patterns (em dashes, contrasts,
rhetorical questions), banned phrases, British/Indian spelling, and that
every must-include item from the user's input made it in.

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

# Patterns that make text read as machine-written. Any hit fails the JD.
AI_PATTERNS = [
    ("em dash", r"—"),
    ("dash used as punctuation", r"\s[–-]\s"),
    ("'not X, Y' contrast", r",\s+not\s+(?!only\b|just\b)\w+"),
    ("'not just/only' contrast", r"\bnot\s+(just|only|merely|simply)\b"),
    ("sentence opening with 'Not'", r"(^|[.!?]\s+)Not\b"),
    ("'isn't X, it's Y' contrast", r"\b(isn't|is not|aren't|are not|wasn't|don't|doesn't)\b[^.]{0,60},\s*(it's|it is|they're|we|you)\b"),
    ("'not X but Y' contrast", r"\bnot\b[^.]{0,40}\bbut\b"),
    ("'rather than' contrast", r"\brather than\b"),
    ("rhetorical question", r"\?"),
    ("exclamation", r"!"),
    ("staged colon reveal", r"\b(here's|the result|the answer|the catch|the point|the deal|the twist)\b[^.]{0,20}:"),
]

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
    span("header.title", h["title"], LIM["header.title"])
    span("header.lead", h["lead"], LIM["header.lead"])
    span("header.punchline", h["punchline"], LIM["header.punchline"])

    labels = [m["label"] for m in jd["meta"]]
    if labels[:4] != S["meta"]["fixed_labels"]:
        bad("meta", f"first four labels must be {S['meta']['fixed_labels']}, got {labels[:4]}")
    if len(labels) != 5 or labels[4] not in S["meta"]["fifth_label_options"]:
        bad("meta", f"fifth label must be one of {S['meta']['fifth_label_options']}")
    for m in jd["meta"]:
        span(f"meta.{m['label']}", m["value"], [1, 6])
    exp = next((m["value"] for m in jd["meta"] if m["label"] == "EXPERIENCE"), "")
    if not re.fullmatch(r"\d+(–\d+|\+) years?", exp):
        bad("meta.EXPERIENCE", f"'{exp}' should look like '3–5 years' or '6+ years'")

    r = jd["the_role"]
    span("the_role.lead", r["lead"], LIM["the_role.lead"])
    items("the_role.paragraphs", r["paragraphs"], LIM["the_role.paragraphs"])

    lv = jd["the_level"]
    span("the_level.lead", lv["lead"], LIM["the_level.lead"])
    items("the_level.rows", lv["rows"], LIM["the_level.rows"], key="text")
    for x in lv["rows"]:
        if not re.fullmatch(r"[A-Z]+", x["key"]):
            bad(f"the_level.{x['key']}", "key must be one upper-case word")

    w = jd["your_work"]
    items("your_work.groups", w["groups"], LIM["your_work.groups"])
    for g in w["groups"]:
        if g["label"] != g["label"].upper() or len(g["label"].split()) > 2:
            bad(f"your_work.{g['label']}", "group label must be 1–2 upper-case words")
        items(f"your_work.{g['label']}", g["bullets"], LIM["your_work.bullets"])

    b = jd["the_bar"]
    span("the_bar.intro", b["intro"], LIM["the_bar.intro"])
    items("the_bar.traits", b["traits"], LIM["the_bar.traits"], key="text")
    for t in b["traits"]:
        span(f"the_bar.{t['title']}.title", t["title"], LIM["the_bar.traits"]["title_words"])

    a = jd["ai"]
    span("ai.lead", a["lead"], LIM["ai.lead"])
    items("ai.bullets", a["bullets"], LIM["ai.bullets"])

    m = jd["minimum"]
    if m.get("note"):
        span("minimum.note", m["note"], LIM["minimum.note"])
    items("minimum.items", m["items"], LIM["minimum.items"])
    for i, it in enumerate(m["items"]):
        if not it.startswith("**") and "**" not in it[:40]:
            bad(f"minimum.items[{i}]", "needs a short **bold phrase** near the start (layout)")

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
    items("assessment.cards", asm["cards"], LIM["assessment.cards"], key="text")
    for c in asm["cards"]:
        span(f"assessment.{c['title']}.title", c["title"], LIM["assessment.cards"]["title_words"])

    items("not_for_you.items", jd["not_for_you"]["items"], LIM["not_for_you.items"])

    if jd["footer_tag"] != jd["footer_tag"].upper() or jd["footer_tag"].count(" · ") != 2:
        bad("footer_tag", "must be 'LEVEL · SPECIALISATION · CITY' in upper case")

    # Writing checks: plain, human, no AI patterns
    text = all_text(jd)
    for t in text:
        p = plain(t)
        for name, rx in AI_PATTERNS:
            mt = re.search(rx, p)
            if mt:
                bad("ai-pattern", f"{name}: '...{p[max(0, mt.start() - 25):mt.end() + 25]}...'")
        if "  " in t:
            bad("style", f"double space: '{p[:60]}'")
        if t.count("**") % 2 or t.count("__") % 2:
            bad("markup", f"unbalanced bold markers: '{t[:60]}'")
    body = " ".join(plain(t) for t in text)
    low = body.lower()
    for phrase in BANNED:
        if re.search(r"\b" + re.escape(phrase) + r"\b", low):
            bad("banned", f"'{phrase}'")
    us = re.findall(r"\b(center|centers|judgment|defense|organization|organizations|organize|optimize|optimizing|"
                    r"prioritize|analyze|analyzing|color|behavior|favorite|license|catalog|modeling)\b", low)
    for wd in sorted(set(us)):
        bad("spelling", f"US spelling '{wd}'; use British/Indian English")

    for item in must_include:
        if item.lower() not in low:
            bad("must_include", f"'{item}' from the user's input is missing")


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
