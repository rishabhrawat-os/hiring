#!/usr/bin/env python3
"""Show where every candidate is, and which ones need work next.

    python3 status.py <run>            table of candidates and their step
    python3 status.py <run> --next     JSON: ids grouped by the step they need next
    python3 status.py <run> --check-blind <id>   fail if cv-blind.txt still has contact details
"""
import json
import re
import sys
from pathlib import Path

ORDER = ["ingested", "extracted", "screened_out", "scoring", "scored"]
PII = [("email", r"[\w.+-]+@[\w-]+\.[\w.]+"), ("phone", r"(?<![\d-])\+?(?:\d[\s().-]?){10,13}(?![\d-])"),
       ("profile link", r"(linkedin\.com|github\.com|facebook\.com|instagram\.com)/\S+"),
       ("date of birth", r"\b(DOB|date of birth|born on)\b"),
       ("personal detail", r"\b(marital status|married|unmarried|religion|caste|gender|male|female|nationality|father'?s name)\b")]


def candidates(run):
    for d in sorted((run / "candidates").glob("C*")):
        st = json.loads((d / "status.json").read_text())
        yield d, st


def next_step(d, st):
    if st.get("status") == "needs_manual_read" and not (d / "cv.txt").read_text().strip():
        return "manual_read"
    if not (d / "10-profile.json").exists() or not (d / "cv-blind.txt").exists():
        return "extract"
    if (d / "11-screen.json").exists() and json.loads((d / "11-screen.json").read_text()).get("screened_out"):
        return "done"
    if (d / "result.json").exists():
        return "done"
    scores = list(d.glob("12-score-r*.json"))
    chals = list(d.glob("13-challenge-r*.json"))
    if len(scores) > len(chals):
        return "challenge"
    return "score"


def check_blind(run, cid):
    text = (run / "candidates" / cid / "cv-blind.txt").read_text()
    bad = [(n, m.group(0)[:40]) for n, rx in PII for m in [re.search(rx, text, re.I)] if m]
    for n, s in bad:
        print(f"FAIL {cid}: cv-blind.txt still contains {n}: {s!r}")
    print(json.dumps({"candidate": cid, "blind": not bad}))
    sys.exit(1 if bad else 0)


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    run = Path(a[0])
    if "--check-blind" in a:
        return check_blind(run, a[a.index("--check-blind") + 1])
    groups = {}
    rows = []
    for d, st in candidates(run):
        n = next_step(d, st)
        groups.setdefault(n, []).append(d.name)
        res = json.loads((d / "result.json").read_text()) if (d / "result.json").exists() else {}
        rows.append((d.name, n, res.get("score", ""), len(list(d.glob("12-score-r*.json")))))
    if "--next" in a:
        print(json.dumps(groups))
        return
    print(f"{'ID':<5} {'next':<12} {'score':<6} rounds")
    for r in rows:
        print(f"{r[0]:<5} {r[1]:<12} {str(r[2]):<6} {r[3]}")
    print(json.dumps({k: len(v) for k, v in groups.items()}))


if __name__ == "__main__":
    main()
