#!/usr/bin/env python3
"""Check one candidate's scorer and challenger files and, if they agree,
write the candidate's result. The score is computed here, never taken
from an agent.

    python3 reconcile.py <run>/candidates/<id> --rubric <run>/rubric-final.json [--max-rounds 1] [--tolerance 2]

First-round screening: by default the challenger reviews once. Criterion
scores within the tolerance count as agreed; wider gaps are averaged and
noted in the comments, so no extra rounds are spent.

Exit codes: 0 result written; 2 another round is needed (only when
--max-rounds is above 1); 1 a file is invalid (the step that wrote it must
redo it).
"""
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


def merge(a, b):
    """Scorer's points first, then the challenger's points that add something new."""
    out = list(a)
    for it in b:
        if not any(SequenceMatcher(None, it.lower(), o.lower()).ratio() > 0.7 for o in out):
            out.append(it)
    return out

fails = []


def fail(m):
    fails.append(m)


def norm(s):
    s = s.lower().replace("’", "'").replace("–", "-").replace("—", "-")
    return re.sub(r"[^a-z0-9%₹$.+#'/-]+", " ", s).strip()


def latest(d, prefix):
    files = sorted(d.glob(f"{prefix}-r*.json"), key=lambda p: int(re.search(r"-r(\d+)\.json$", p.name).group(1)))
    return files[-1] if files else None


def validate(doc, rubric, cv, who):
    crit = {c["id"]: c for c in rubric["criteria"]}
    got = {c.get("id"): c for c in doc.get("criteria", [])}
    for cid in crit:
        if cid not in got:
            fail(f"{who}: criterion {cid} not scored")
    for cid, c in got.items():
        if cid not in crit:
            fail(f"{who}: unknown criterion {cid}")
            continue
        s = c.get("score")
        if not isinstance(s, (int, float)) or isinstance(s, bool) or not 0 <= s <= 10:
            fail(f"{who}: {cid} score {s!r} must be 0–10")
        ev = c.get("evidence", [])
        if crit[cid]["weight"] > 0 and s and s > 0 and not ev:
            fail(f"{who}: {cid} scores {s} with no evidence quote")
        for q in ev:
            if len(norm(q)) < 8:
                fail(f"{who}: {cid} evidence too short to verify: {q!r}")
            elif norm(q) not in cv:
                fail(f"{who}: {cid} quote not found in the CV: {q[:80]!r}")
        if not str(c.get("reason", "")).strip():
            fail(f"{who}: {cid} has no reason")
    mh = {m["id"] for m in rubric["must_haves"]}
    gm = {m.get("id"): m for m in doc.get("must_haves", [])}
    for mid in mh:
        m = gm.get(mid)
        if not m or m.get("met") not in (True, False, "unclear"):
            fail(f"{who}: must-have {mid} needs met = true, false or \"unclear\"")
        elif m.get("met") is True:
            if not m.get("evidence") or norm(m["evidence"]) not in cv:
                fail(f"{who}: must-have {mid} marked met without a quote found in the CV")
    for k in ("why_proceed", "why_not"):
        if not isinstance(doc.get(k), list) or not doc.get(k):
            fail(f"{who}: '{k}' must be a non-empty list")


def weighted(scores, rubric):
    num = den = 0
    for c in rubric["criteria"]:
        num += c["weight"] * scores[c["id"]]
        den += c["weight"]
    return round(num / den * 10, 1) if den else 0.0


def main():
    a = sys.argv[1:]
    if len(a) < 3 or "--rubric" not in a:
        sys.exit(__doc__)
    d = Path(a[0])
    rubric = json.loads(Path(a[a.index("--rubric") + 1]).read_text())
    max_rounds = int(a[a.index("--max-rounds") + 1]) if "--max-rounds" in a else 1
    tolerance = float(a[a.index("--tolerance") + 1]) if "--tolerance" in a else 2
    cv = norm((d / "cv-blind.txt").read_text())
    sf, cf = latest(d, "12-score"), latest(d, "13-challenge")
    if not sf or not cf:
        sys.exit("need at least one 12-score-rN.json and 13-challenge-rN.json")
    s, c = json.loads(sf.read_text()), json.loads(cf.read_text())
    rnd = int(re.search(r"-r(\d+)\.json$", sf.name).group(1))
    if int(re.search(r"-r(\d+)\.json$", cf.name).group(1)) != rnd:
        sys.exit(f"scorer is on round {rnd} but challenger file is {cf.name}")
    validate(s, rubric, cv, "scorer")
    validate(c, rubric, cv, "challenger")
    if fails:
        for f in fails:
            print("FAIL", f)
        print(json.dumps({"candidate": d.name, "status": "invalid"}))
        sys.exit(1)

    ss = {x["id"]: x["score"] for x in s["criteria"]}
    cs = {x["id"]: x["score"] for x in c["criteria"]}
    gaps = {k: (ss[k], cs[k]) for k in ss if abs(ss[k] - cs[k]) > tolerance}
    smh = {m["id"]: m["met"] for m in s["must_haves"]}
    cmh = {m["id"]: m["met"] for m in c["must_haves"]}
    mh_gaps = {k: (smh[k], cmh[k]) for k in smh if smh[k] != cmh.get(k)}
    if (gaps or mh_gaps) and rnd < max_rounds:
        for k, (x, y) in gaps.items():
            print(f"DISAGREE {k}: scorer {x}, challenger {y}")
        for k, (x, y) in mh_gaps.items():
            print(f"DISAGREE must-have {k}: scorer {x}, challenger {y}")
        print(json.dumps({"candidate": d.name, "status": "another_round", "next_round": rnd + 1}))
        sys.exit(2)

    final = {k: round((ss[k] + cs[k]) / 2 * 2) / 2 for k in ss}       # mean, to the nearest 0.5
    names = {c["id"]: c["name"] for c in rubric["criteria"]}
    mh_final = {}
    for k in smh:
        a_, b_ = smh[k], cmh.get(k)
        mh_final[k] = a_ if a_ == b_ else "unclear"
    must_fail = [k for k, v in mh_final.items() if v is False]
    result = {
        "candidate": d.name,
        "rounds": rnd,
        "agreed": not gaps and not mh_gaps,
        "unresolved": [{"id": k, "scorer": x, "challenger": y} for k, (x, y) in gaps.items()]
                      + [{"id": k, "scorer": x, "challenger": y} for k, (x, y) in mh_gaps.items()],
        "criteria": {k: {"score": v, "scorer_reason": next(x["reason"] for x in s["criteria"] if x["id"] == k),
                         "challenger_reason": next(x["reason"] for x in c["criteria"] if x["id"] == k),
                         "evidence": sorted(set(next(x.get("evidence", []) for x in s["criteria"] if x["id"] == k)
                                               + next(x.get("evidence", []) for x in c["criteria"] if x["id"] == k)))}
                     for k, v in final.items()},
        "must_haves": mh_final,
        "must_have_fail": must_fail,
        "score": weighted(final, rubric),
        "why_proceed": merge(s["why_proceed"], c["why_proceed"]),
        "why_not": merge(s["why_not"], c["why_not"]),
        "flags": merge(s.get("flags", []), c.get("flags", []))
                 + [f"{names[k]}: scorer {x}, challenger {y}, averaged" for k, (x, y) in gaps.items()]
                 + [f"must-have {k} unclear (scorer {x}, challenger {y})" for k, (x, y) in mh_gaps.items()],
    }
    (d / "result.json").write_text(json.dumps(result, indent=1, ensure_ascii=False))
    st = json.loads((d / "status.json").read_text())
    st.update(step="scored", status="done")
    (d / "status.json").write_text(json.dumps(st, indent=1))
    print(json.dumps({"candidate": d.name, "status": "done", "score": result["score"], "agreed": result["agreed"]}))


if __name__ == "__main__":
    main()
