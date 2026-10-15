#!/usr/bin/env python3
"""Work out career facts from a candidate's 10-profile.json, so scorers
don't have to: months per role, total months, short stints, promotions,
months since the last role, and gaps (gaps are never scored; they only
become interview questions).

    python3 facts.py <run>/candidates/<id> [--as-of YYYY-MM]

Writes 10-facts.json next to the profile and prints it.
"""
import json
import sys
from datetime import date
from pathlib import Path


def ym(s, today):
    s = str(s or "").strip().lower()
    if s in ("present", "current", "now", ""):
        return today
    try:
        y, m = s[:7].split("-")
        return int(y) * 12 + int(m) - 1
    except ValueError:
        return None


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    d = Path(a[0])
    asof = a[a.index("--as-of") + 1] if "--as-of" in a else date.today().strftime("%Y-%m")
    today = ym(asof, None)
    prof = json.loads((d / "10-profile.json").read_text())
    roles, problems = [], []
    for r in prof.get("roles", []):
        s, e = ym(r.get("start"), today), ym(r.get("end"), today)
        if s is None or e is None:
            problems.append(f"unreadable dates for {r.get('title')} at {r.get('company')}")
            continue
        if e < s:
            problems.append(f"end before start for {r.get('title')} at {r.get('company')}")
            continue
        roles.append({**r, "_s": s, "_e": e, "months": e - s + 1})
    roles.sort(key=lambda r: r["_s"])
    covered = set()
    for r in roles:
        covered.update(range(r["_s"], r["_e"] + 1))
    gaps = []
    for prev, nxt in zip(roles, roles[1:]):
        if nxt["_s"] - prev["_e"] - 1 >= 3:
            gaps.append({"after": prev.get("company"), "months": nxt["_s"] - prev["_e"] - 1})
    companies = {}
    for r in roles:
        companies.setdefault(r.get("company"), []).append(r)
    tenures = [{"company": c, "months": max(x["_e"] for x in rs) - min(x["_s"] for x in rs) + 1,
                "reason_given": " ".join(x.get("reason_for_short_stint", "") for x in rs).strip()}
               for c, rs in companies.items()]
    recent = [t for t in tenures if any(x["_e"] >= today - 60 for x in companies[t["company"]])]
    facts = {
        "as_of": asof,
        "total_months_worked": len(covered),
        "roles": [{"company": r.get("company"), "title": r.get("title"), "months": r["months"]} for r in roles],
        "companies": len(companies),
        "average_months_per_company": round(sum(t["months"] for t in tenures) / len(tenures), 1) if tenures else 0,
        "short_stints_last_5y": [t for t in recent if t["months"] < 12],
        "promotions": len(prof.get("promotions", [])),
        "months_since_last_role_ended": max(0, today - max((r["_e"] for r in roles), default=today)),
        "gaps_for_interview_only": gaps,
        "date_problems": problems,
    }
    (d / "10-facts.json").write_text(json.dumps(facts, indent=1, ensure_ascii=False))
    print(json.dumps(facts, ensure_ascii=False))


if __name__ == "__main__":
    main()
