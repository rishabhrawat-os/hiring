#!/usr/bin/env python3
"""Verify a step's output before the orchestrator moves on. Never trust a
self-reported "pass": this recomputes it.

    python3 check_gate.py research  <run>/02-research-rN.json  --run-date YYYY-MM-DD
    python3 check_gate.py challenge <run>/03-challenge-rN.json --research <run>/02-research-rN.json
    python3 check_gate.py format    <run>/05-format-review-rN.json
    python3 check_gate.py facts     <run>/05-facts-check.json --approved <draft> --final <run>/06-final.json --intake <run>/01-intake.json

Research rounds 2+ also take --previous-challenge <run>/03-challenge-r(N-1).json.

Exit 0 = gate passed. Prints one FAIL line per reason, then a JSON summary.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

PASS_SCORE = 95
MAX = {"role_accuracy": 20, "seniority": 15, "currency": 15, "coverage": 15,
       "realism": 10, "context": 10, "evidence": 10, "fairness": 5}
FORMAT_MAX = {"blueprint": 30, "faithful": 25, "human": 30, "proofreading": 15}

fails = []


def fail(msg):
    fails.append(msg)


def months_between(d1, d2):
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def source_ids_used(x, out):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "sources" and isinstance(v, list) and all(isinstance(s, str) for s in v):
                out.update(v)
            else:
                source_ids_used(v, out)
    elif isinstance(x, list):
        for v in x:
            source_ids_used(v, out)
    return out


SEVERITIES = ("blocking", "major", "minor")


def scored(dims, maxes):
    """Sum only the known dimensions; any other key is a failure."""
    for k in dims:
        if k not in maxes:
            fail(f"unknown dimension '{k}' in by_dimension")
    total = 0
    for k, mx in maxes.items():
        v = dims.get(k)
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= mx:
            fail(f"by_dimension.{k} = {v!r}; must be 0–{mx}")
        else:
            total += v
    return total


def heavy_open(entries, label):
    out = []
    for o in entries:
        sev = o.get("severity")
        if sev not in SEVERITIES:
            fail(f"{label} {o.get('id')} has severity {sev!r}; must be one of {SEVERITIES} (lower case)")
        if sev in ("blocking", "major") or sev not in SEVERITIES:
            out.append(o.get("id"))
    return out


def claims_without_sources(x, path="$", out=None):
    out = [] if out is None else out
    if isinstance(x, dict):
        if "sources" in x and isinstance(x["sources"], list) and not x["sources"] and path != "$":
            out.append(path)
        for k, v in x.items():
            if k not in ("sources", "objection_responses", "must_include_status"):
                claims_without_sources(v, f"{path}.{k}", out)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            claims_without_sources(v, f"{path}[{i}]", out)
    return out


def research(d, run_date, previous_challenge=None):
    srcs = d.get("sources", [])
    ids = {s.get("id") for s in srcs}
    urls = {s.get("url") for s in srcs if s.get("url")}
    if len(urls) < 15:
        fail(f"{len(urls)} distinct sources; need 15+")
    recent = 0
    for s in srcs:
        m = re.match(r"(\d{4})-(\d{2})", str(s.get("date", "")))
        if m and months_between(date(int(m[1]), int(m[2]), 1), run_date) <= 18:
            recent += 1
    if srcs and recent / len(srcs) < 0.6:
        fail(f"{recent}/{len(srcs)} sources dated within 18 months of {run_date}; need 60%+")
    used = source_ids_used({k: v for k, v in d.items() if k != "sources"}, set())
    missing = used - ids
    if missing:
        fail(f"claims cite unknown source ids: {sorted(missing)[:10]}")
    for key in ("level", "level_dimensions", "responsibilities", "must_haves", "behaviours", "assessment"):
        if not d.get(key):
            fail(f"'{key}' is empty")
    if len(d.get("level_dimensions", [])) != 6:
        fail("need exactly 6 level_dimensions")
    if len(d.get("behaviours", [])) != 5:
        fail("need exactly 5 behaviours")
    if len(d.get("assessment", [])) != 6:
        fail("need exactly 6 assessment items")
    empty = claims_without_sources({k: v for k, v in d.items() if k != "sources"})
    if empty:
        fail(f"claims with no source: {empty[:8]}")
    if previous_challenge:
        prev = json.loads(Path(previous_challenge).read_text())
        need = {o["id"] for o in prev.get("objections", [])}
        got = {r.get("id") for r in d.get("objection_responses", []) if r.get("status") in ("fixed", "disputed")}
        if need - got:
            fail(f"objections not answered: {sorted(need - got)}")
    for item in d.get("must_include_status", []):
        if item.get("status") not in ("current", "being replaced", "pair with"):
            fail(f"must_include_status for '{item.get('item')}' has no valid status")


def challenge(d, research_file):
    total = scored(d.get("by_dimension", {}), MAX)
    if total != d.get("score"):
        fail(f"score {d.get('score')} doesn't equal the sum of dimensions ({total})")
    if total < PASS_SCORE:
        fail(f"score {total} is below {PASS_SCORE}")
    heavy = heavy_open(d.get("objections", []), "objection")
    if heavy:
        fail(f"open blocking/major objections: {heavy}")
    searches = {q.strip().lower() for q in d.get("own_searches", []) if isinstance(q, str) and q.strip()}
    if len(searches) < 6:
        fail(f"{len(searches)} distinct own searches; need 6+")
    checks = d.get("spot_checks", [])
    if len({c.get("source") for c in checks}) < 5:
        fail(f"{len({c.get('source') for c in checks})} distinct sources spot-checked; need 5+")
    if research_file:
        ids = {s["id"] for s in json.loads(Path(research_file).read_text()).get("sources", [])}
        for c in checks:
            if c.get("source") not in ids:
                fail(f"spot check on unknown source {c.get('source')}")
    for c in checks:
        if c.get("supports_claim") is not True:
            src = c.get("source", "")
            named = [o for o in d.get("objections", []) if src and re.search(r"\b" + re.escape(src) + r"\b", json.dumps(o))]
            if not any(str(o.get("severity", "")).lower() in ("blocking", "major") for o in named):
                fail(f"spot check {src} did not support its claim but has no blocking/major objection naming it")


def format_review(d):
    total = scored(d.get("by_dimension", {}), FORMAT_MAX)
    if total != d.get("score"):
        fail(f"score {d.get('score')} doesn't equal the sum of dimensions ({total})")
    if total < PASS_SCORE:
        fail(f"score {total} is below {PASS_SCORE}")
    heavy = heavy_open(d.get("issues", []), "issue")
    if heavy:
        fail(f"open blocking/major issues: {heavy}")


def facts(d, approved, final, intake):
    if d.get("changed_facts"):
        fail(f"{len(d['changed_facts'])} facts changed in the copy pass")
    a = json.loads(Path(approved).read_text())
    f = json.loads(Path(final).read_text())
    if json.dumps(sorted(a)) != json.dumps(sorted(f)):
        fail("top-level blocks differ between the approved draft and the final file")
    if intake:
        ftxt = json.dumps(f, ensure_ascii=False)
        for it in json.loads(Path(intake).read_text()).get("must_include", []):
            terms = it.get("match", [it.get("item")]) if isinstance(it, dict) else [it]
            if not any(t and t in ftxt for t in terms):
                fail(f"must-include '{terms[0]}' is missing from the final file")
    for key in ("meta", "footer_tag"):
        if a.get(key) != f.get(key):
            fail(f"'{key}' changed in the copy pass")


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    kind, path = a[0], a[1]
    d = json.loads(Path(path).read_text())
    opt = lambda k: a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else None
    if kind == "research":
        try:
            rd = date.fromisoformat(opt("--run-date") or date.today().isoformat())
        except ValueError:
            fail(f"--run-date {opt('--run-date')!r} is not YYYY-MM-DD")
            rd = None
        if rd:
            research(d, rd, opt("--previous-challenge"))
    elif kind == "challenge":
        challenge(d, opt("--research"))
    elif kind == "format":
        format_review(d)
    elif kind == "facts":
        if not (opt("--approved") and opt("--final")):
            sys.exit("facts needs --approved and --final")
        facts(d, opt("--approved"), opt("--final"), opt("--intake"))
    else:
        sys.exit(__doc__)
    for f in fails:
        print("FAIL", f)
    print(json.dumps({"gate": kind, "file": path, "pass": not fails}))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
