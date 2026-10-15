#!/usr/bin/env python3
"""Gate for the rubric loop.

    python3 check_rubric.py rubric   <run>/02-rubric-rN.json
    python3 check_rubric.py challenge <run>/03-rubric-challenge-rN.json

Exit 0 = pass. One FAIL line per reason, then a JSON summary.
"""
import json
import sys
from pathlib import Path

SIGNALS = {"role_fit", "stability", "industry", "breadth_depth", "achievements", "progression",
           "background", "recency", "red_flags"}
REQUIRED_SIGNALS = SIGNALS - {"role_fit"}
GROUPS = {"role_fit", "career", "red_flags"}
CHALLENGE_MAX = {"job_relevance": 25, "coverage": 20, "anchors": 20, "weights": 20, "fairness": 15}
PASS = 85
fails = []


def fail(m):
    fails.append(m)


def rubric(d):
    crit = d.get("criteria", [])
    if not crit:
        return fail("no criteria")
    ids = [c.get("id") for c in crit]
    if len(set(ids)) != len(ids):
        fail("criterion ids must be unique")
    total = 0
    for c in crit:
        w = c.get("weight")
        if not isinstance(w, int) or isinstance(w, bool) or w < 0:
            fail(f"{c.get('id')}: weight must be a whole number ≥ 0")
            continue
        total += w
        if c.get("signal") not in SIGNALS:
            fail(f"{c.get('id')}: signal must be one of {sorted(SIGNALS)}")
        if c.get("group") not in GROUPS:
            fail(f"{c.get('id')}: group must be one of {sorted(GROUPS)}")
        anchors = c.get("anchors", {})
        for k in ("0", "5", "10"):
            if not str(anchors.get(k, "")).strip():
                fail(f"{c.get('id')}: anchor '{k}' is missing (what a {k}/10 looks like)")
        if w > 0 and not str(c.get("what_counts", "")).strip():
            fail(f"{c.get('id')}: 'what_counts' is empty")
    if total != 100:
        fail(f"weights add up to {total}; must be 100")
    present = {c.get("signal") for c in crit}
    for s in sorted(REQUIRED_SIGNALS - present):
        fail(f"career signal '{s}' is not considered (add it, with weight 0 and a reason if it shouldn't count)")
    for c in crit:
        if c.get("weight") == 0 and not str(c.get("zero_reason", "")).strip():
            fail(f"{c.get('id')}: weight 0 needs a zero_reason")
    bg = sum(c["weight"] for c in crit if c.get("signal") == "background" and isinstance(c.get("weight"), int))
    if bg > 10:
        fail(f"background weight is {bg}; cap is 10")
    fit = sum(c["weight"] for c in crit if c.get("group") == "role_fit" and isinstance(c.get("weight"), int))
    if fit < 50:
        fail(f"role-fit criteria carry {fit}; must carry at least 50")
    mh = d.get("must_haves", [])
    if not mh:
        fail("no must-haves")
    for m in mh:
        if not str(m.get("requirement", "")).strip() or not str(m.get("evidence_needed", "")).strip():
            fail(f"must-have {m.get('id')} needs 'requirement' and 'evidence_needed'")
    cut = d.get("cutoff")
    if not isinstance(cut, (int, float)) or not 0 < cut < 100:
        fail("cutoff must be a number between 0 and 100")


def challenge(d):
    dims = d.get("by_dimension", {})
    total = 0
    for k in dims:
        if k not in CHALLENGE_MAX:
            fail(f"unknown dimension '{k}'")
    for k, mx in CHALLENGE_MAX.items():
        v = dims.get(k)
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= mx:
            fail(f"by_dimension.{k} = {v!r}; must be 0–{mx}")
        else:
            total += v
    if total != d.get("score"):
        fail(f"score {d.get('score')} doesn't equal the sum ({total})")
    if total < PASS:
        fail(f"score {total} is below {PASS}")
    for o in d.get("objections", []):
        sev = o.get("severity")
        if sev not in ("blocking", "major", "minor"):
            fail(f"objection {o.get('id')}: severity {sev!r} must be blocking, major or minor")
        elif sev == "blocking":
            fail(f"open blocking objection {o.get('id')}")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("rubric", "challenge"):
        sys.exit(__doc__)
    d = json.loads(Path(sys.argv[2]).read_text())
    (rubric if sys.argv[1] == "rubric" else challenge)(d)
    for f in fails:
        print("FAIL", f)
    print(json.dumps({"gate": sys.argv[1], "file": sys.argv[2], "pass": not fails}))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
