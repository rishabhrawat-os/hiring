#!/usr/bin/env python3
"""Check a JD content file before it is rendered.

Checks, in order:
  1. shape: matches structure/jd.schema.json (types, required keys, allowed values)
  2. space: word and item limits from structure/skeleton.json, plus a total
     word ceiling that keeps the JD to about 7 pages
  3. user input: every must-include item appears (word-boundary match), and
     stated experience and city are the ones printed
  4. writing: no em dashes, contrast framing, rhetorical questions, staged
     reveals, banned phrases, salary talk or US spellings. Text the user
     named and tool names in the toolkit are exempt from the phrase and
     spelling checks, because user input beats voice rules.

    python3 validate_jd.py jd.json [--intake 01-intake.json]

Exit code 0 = pass. One FAIL line per problem, then a JSON summary.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKEL = json.loads((ROOT / "structure/skeleton.json").read_text())
SCHEMA = json.loads((ROOT / "structure/jd.schema.json").read_text())
LIM = SKEL["limits"]
S = SKEL["sections"]
BANNED = [l.strip().lower() for l in (ROOT / "voice/banned-phrases.txt").read_text().splitlines()
          if l.strip() and not l.startswith("#")]

# Patterns that make text read as machine-written. Any hit fails the JD.
AI_PATTERNS = [
    ("em dash", r"—"),
    ("dash used as punctuation", r"\s[–-]\s"),
    ("'X, not Y' contrast", r",\s+not\s+(?!only\b|just\b|required\b|needed\b|necessary\b|essential\b|mandatory\b)\w+"),
    ("'not just / not only' contrast", r"\bnot\s+(just|only|merely|simply)\b"),
    ("sentence opening with 'Not'", r"(^|[.!?]\s+)Not\b"),
    ("'isn't X, it's Y' contrast", r"\b(isn't|is not|it's not|it is not|aren't|are not)\b[^.]{0,60}[,.;]\s*(it's|it is|they're|they are)\b"),
    ("'not about' framing", r"\b(not|isn't|aren't)\s+about\b"),
    ("'instead of' contrast", r"\binstead of\b"),
    ("'rather than' contrast", r"\brather than\b"),
    ("'No X. Just Y' framing", r"(^|[.!?]\s+)No \w+( \w+)?\.\s+Just\b"),
    ("rhetorical question", r"\?"),
    ("exclamation", r"!"),
    ("staged colon reveal", r"\b(here's|here is|the result|the answer|the catch|the point|the deal|the twist|the secret)\b[^.]{0,20}:"),
    ("salary or pay", r"\b(CTC|LPA|salary|salaries|compensation|remuneration|stipend|per annum|pay band|pay range|pay scale|take-home)\b"),
]
US_OK = {"size", "sizes", "sized", "sizing", "prize", "prizes", "seize", "seized", "seizes", "resize", "resized",
         "downsize", "downsized", "oversize", "oversized", "capsize", "citizen", "citizens"}
US_EXTRA = re.compile(r"\b(center|centers|centered|color|colors|behavior|behaviors|favorite|catalog|catalogs|"
                      r"modeling|modeled|labeled|labeling|traveled|traveling|program(?:s)?(?= (?:manager|management|office))|"
                      r"judgment|defense|fulfill|enrollment|analog)\b")

problems = []


def bad(where, msg):
    problems.append(f"{where}: {msg}")


# ---------- schema (the subset jd.schema.json uses) ----------

def resolve(node):
    while "$ref" in node:
        node = SCHEMA["$defs"][node["$ref"].split("/")[-1]]
    return node


def check_schema(x, node, path="$"):
    node = resolve(node)
    t = node.get("type")
    if "const" in node and x != node["const"]:
        bad(path, f"must be {node['const']!r}")
    if "enum" in node and x not in node["enum"]:
        bad(path, f"must be one of {node['enum']}, got {x!r}")
    if t == "object":
        if not isinstance(x, dict):
            return bad(path, "must be an object")
        for k in node.get("required", []):
            if k not in x:
                bad(path, f"missing '{k}'")
        props = node.get("properties", {})
        if node.get("additionalProperties") is False:
            for k in x:
                if k not in props:
                    bad(path, f"unexpected key '{k}'")
        for k, v in x.items():
            if k in props:
                check_schema(v, props[k], f"{path}.{k}")
    elif t == "array":
        if not isinstance(x, list):
            return bad(path, "must be a list")
        if "minItems" in node and len(x) < node["minItems"]:
            bad(path, f"needs at least {node['minItems']} items")
        if "maxItems" in node and len(x) > node["maxItems"]:
            bad(path, f"allows at most {node['maxItems']} items")
        for i, v in enumerate(x):
            check_schema(v, node.get("items", {}), f"{path}[{i}]")
    elif t == "string":
        if not isinstance(x, str):
            return bad(path, "must be text")
        if len(x.strip()) < node.get("minLength", 0):
            bad(path, "is empty")


# ---------- helpers ----------

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
    lo, hi = spec.get("count", (0, 999))
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


def term_rx(term):
    """Word-boundary match; short terms (Go, R, C) must match case exactly."""
    flags = 0 if len(term) <= 3 else re.I
    return re.compile(r"(?<![\w.+#])" + re.escape(term) + r"(?![\w+#])", flags)


def must_terms(intake):
    out = []
    for it in intake.get("must_include", []):
        if isinstance(it, dict):
            out.append((it.get("item", ""), it.get("match") or [it.get("item", "")]))
        else:
            out.append((it, [it]))
    return out


# ---------- checks ----------

def check_space(jd):
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
        if not re.match(r"^(\S+\s){0,3}\*\*[^*]+\*\*", it):
            bad(f"minimum.items[{i}]", "needs a short **bold phrase** at or near the start (layout)")

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

    total = sum(words(t) for t in all_text(jd))
    if total > LIM["total_words"]:
        bad("length", f"{total} words in total; the ceiling is {LIM['total_words']} (about 7 pages). Tighten the content.")


def check_writing(jd, exempt_terms):
    texts = all_text(jd)
    exempt = [term_rx(t) for t in exempt_terms if t]

    def mask(s):
        for rx in exempt:
            s = rx.sub(" ", s)
        return s

    for t in texts:
        p = plain(t)
        for name, rx in AI_PATTERNS:
            mt = re.search(rx, mask(p), re.I)
            if mt:
                q = mask(p)
                bad("writing", f"{name}: '...{q[max(0, mt.start() - 30):mt.end() + 30].strip()}...'")
        if "  " in t:
            bad("style", f"double space: '{p[:60]}'")
        if t.count("**") % 2 or t.count("__") % 2:
            bad("markup", f"unbalanced bold markers: '{t[:60]}'")
    body = mask(" ".join(plain(t) for t in texts))
    low = body.lower()
    for phrase in BANNED:
        if re.search(r"(?<![\w-])" + re.escape(phrase) + r"(?![\w-])", low):
            bad("banned", f"'{phrase}'")
    found = set()
    for w in re.findall(r"\b[A-Za-z][a-z]+(?:iz|yz)(?:e|es|ed|ing|ation|ations|er|ers)\b", body):
        if w.lower() not in US_OK:
            found.add(w)
    for w in re.findall(r"\b\w+\b", body):
        if US_EXTRA.fullmatch(w.lower()) and (w.islower() or w.istitle()):
            found.add(w)
    for w in sorted(found):
        bad("spelling", f"US spelling '{w}'; use British/Indian English (-ise, -our, -re)")


def check_user_input(jd, intake):
    body = " ".join(plain(t) for t in all_text(jd))
    for item, terms in must_terms(intake):
        if not any(term_rx(t).search(body) for t in terms):
            bad("must_include", f"'{item}' from the user's input is missing")
    stated = intake.get("stated", {}) or {}
    meta = {m["label"]: m["value"] for m in jd["meta"]}
    exp = stated.get("experience")
    if exp:
        nums_s = re.findall(r"\d+", str(exp))
        nums_j = re.findall(r"\d+", meta.get("EXPERIENCE", ""))
        if nums_s and nums_s != nums_j[:len(nums_s)]:
            bad("meta.EXPERIENCE", f"user stated '{exp}', JD says '{meta.get('EXPERIENCE')}'")
    level = stated.get("seniority") or stated.get("level")
    if level:
        where = (meta.get("LEVEL", "") + " " + jd["header"]["title"]).lower()
        if level.lower() not in where:
            bad("meta.LEVEL", f"user stated '{level}', but neither LEVEL ('{meta.get('LEVEL')}') nor the title uses it")
    city = stated.get("city")
    if city and city.lower() not in meta.get("LOCATION", "").lower():
        bad("meta.LOCATION", f"user stated '{city}', JD says '{meta.get('LOCATION')}'")


def check(jd, intake=None):
    check_schema(jd, SCHEMA)
    if problems:
        return            # shape is wrong; later checks would only crash
    check_space(jd)
    exempt = []
    if intake:
        for _, terms in must_terms(intake):
            exempt += terms
        check_user_input(jd, intake)
    for row in jd["toolkit"]["rows"]:
        exempt += [v.strip() for v in row["value"].split(",")]
    check_writing(jd, exempt)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    jd = json.loads(Path(args[0]).read_text())
    intake = None
    for flag in ("--intake", "--must-include"):
        if flag in args:
            intake = json.loads(Path(args[args.index(flag) + 1]).read_text())
    check(jd, intake)
    for p in problems:
        print("FAIL", p)
    print(json.dumps({"file": args[0], "pass": not problems, "problems": len(problems)}))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
