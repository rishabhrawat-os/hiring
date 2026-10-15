#!/usr/bin/env python3
"""Verify a step's output before the orchestrator moves on. Never trust a
self-reported "pass": this recomputes it.

    python3 check_gate.py research  <run>/02-research-rN.json  --run-date YYYY-MM-DD
    python3 check_gate.py challenge <run>/03-challenge-rN.json --research <run>/02-research-rN.json
    python3 check_gate.py format    <run>/05-format-review-rN.json

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


def research(d, run_date):
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
    for item in d.get("must_include_status", []):
        if item.get("status") not in ("current", "being replaced", "pair with"):
            fail(f"must_include_status for '{item.get('item')}' has no valid status")


def challenge(d, research_file):
    dims = d.get("by_dimension", {})
    for k, mx in MAX.items():
        v = dims.get(k)
        if not isinstance(v, (int, float)) or not 0 <= v <= mx:
            fail(f"by_dimension.{k} = {v!r}; must be 0–{mx}")
    total = sum(v for v in dims.values() if isinstance(v, (int, float)))
    if total != d.get("score"):
        fail(f"score {d.get('score')} doesn't equal the sum of dimensions ({total})")
    if total < PASS_SCORE:
        fail(f"score {total} is below {PASS_SCORE}")
    heavy = [o["id"] for o in d.get("objections", []) if o.get("severity") in ("blocking", "major")]
    if heavy:
        fail(f"open blocking/major objections: {heavy}")
    if len(d.get("own_searches", [])) < 6:
        fail(f"{len(d.get('own_searches', []))} own searches; need 6+")
    checks = d.get("spot_checks", [])
    if len(checks) < 5:
        fail(f"{len(checks)} spot checks; need 5+")
    if research_file:
        ids = {s["id"] for s in json.loads(Path(research_file).read_text()).get("sources", [])}
        for c in checks:
            if c.get("source") not in ids:
                fail(f"spot check on unknown source {c.get('source')}")
    for c in checks:
        if c.get("supports_claim") is False and not any(c.get("source", "") in json.dumps(o) for o in d.get("objections", [])):
            fail(f"spot check {c.get('source')} failed but has no objection")


def format_review(d):
    dims = d.get("by_dimension", {})
    for k, mx in FORMAT_MAX.items():
        v = dims.get(k)
        if not isinstance(v, (int, float)) or not 0 <= v <= mx:
            fail(f"by_dimension.{k} = {v!r}; must be 0–{mx}")
    total = sum(v for v in dims.values() if isinstance(v, (int, float)))
    if total != d.get("score"):
        fail(f"score {d.get('score')} doesn't equal the sum of dimensions ({total})")
    if total < PASS_SCORE:
        fail(f"score {total} is below {PASS_SCORE}")
    heavy = [i["id"] for i in d.get("issues", []) if i.get("severity") in ("blocking", "major")]
    if heavy:
        fail(f"open blocking/major issues: {heavy}")


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    kind, path = a[0], a[1]
    d = json.loads(Path(path).read_text())
    if kind == "research":
        rd = a[a.index("--run-date") + 1] if "--run-date" in a else date.today().isoformat()
        research(d, date.fromisoformat(rd))
    elif kind == "challenge":
        challenge(d, a[a.index("--research") + 1] if "--research" in a else None)
    elif kind == "format":
        format_review(d)
    else:
        sys.exit(__doc__)
    for f in fails:
        print("FAIL", f)
    print(json.dumps({"gate": kind, "file": path, "pass": not fails}))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
