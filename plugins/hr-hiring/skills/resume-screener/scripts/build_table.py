#!/usr/bin/env python3
"""Apply the panel's approved adjustments and the recruiter's overrides,
then print the final table. Scores and verdicts are computed here.

    python3 build_table.py <run> [--draft]

--draft: before the panel has run (no panel files needed). Prints the
table and, last, a JSON line listing the borderline candidates (within 5
points of the cut-off) that the panel must review. No borderline
candidates means no panel is needed.
Writes <run>/final.json and <run>/report.md.
"""
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path


def dedupe(items):
    """Drop points that say nearly the same thing as an earlier one (scorer and challenger often overlap)."""
    out = []
    for it in items or []:
        if not any(SequenceMatcher(None, it.lower(), o.lower()).ratio() > 0.7 for o in out):
            out.append(it)
    return out


def weighted(scores, rubric):
    num = den = 0
    for c in rubric["criteria"]:
        num += c["weight"] * scores[c["id"]]
        den += c["weight"]
    return round(num / den * 10, 1) if den else 0.0


def cell(items, n=2):
    items = [i.replace("|", "/").replace("\n", " ") for i in dedupe(items)][:n]
    return "; ".join(items) if items else "—"


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    run = Path(a[0])
    draft = "--draft" in a
    rubric = json.loads((run / "rubric-final.json").read_text())
    cutoff = rubric["cutoff"]
    manifest = {c["id"]: c for c in json.loads((run / "manifest.json").read_text())["candidates"]}

    adjustments, borderline = {}, {}
    if not draft and (run / "panel" / "20-panel.json").exists():
        panel = json.loads((run / "panel" / "20-panel.json").read_text())
        pch = json.loads((run / "panel" / "21-panel-challenge.json").read_text())
        approved = set(pch.get("approve_adjustments", []))
        for adj in panel.get("adjustments", []):
            if adj.get("id") in approved:
                adjustments.setdefault(adj["candidate"], []).append(adj)
        for b in pch.get("borderline_reviews", []):
            borderline[b["candidate"]] = b
    overrides = {}
    ov_file = run / "overrides.json"
    if ov_file.exists():
        for o in json.loads(ov_file.read_text()):
            overrides[o["candidate"]] = o

    rows = []
    for cid in manifest:
        d = run / "candidates" / cid
        screen = json.loads((d / "11-screen.json").read_text()) if (d / "11-screen.json").exists() else {}
        if screen.get("screened_out"):
            rows.append({"id": cid, "label": manifest[cid]["label"], "score": None,
                         "verdict": "No-go", "basis": "failed must-have screen",
                         "why_proceed": [], "why_not": screen.get("reasons", []), "flags": []})
            continue
        if not (d / "result.json").exists():
            rows.append({"id": cid, "label": manifest[cid]["label"], "score": None,
                         "verdict": "Pending", "basis": "not scored yet", "why_proceed": [], "why_not": [], "flags": []})
            continue
        r = json.loads((d / "result.json").read_text())
        scores = {k: v["score"] for k, v in r["criteria"].items()}
        notes = []
        for adj in adjustments.get(cid, []):
            scores[adj["criterion"]] = adj["to"]
            notes.append(f"panel: {adj['criterion']} {adj['from']}→{adj['to']}")
        score = weighted(scores, rubric)
        if r["must_have_fail"]:
            verdict, basis = "No-go", f"must-have not met: {', '.join(r['must_have_fail'])}"
        else:
            verdict = "Go" if score >= cutoff else "No-go"
            basis = f"score {'≥' if verdict == 'Go' else '<'} cut-off {cutoff}"
        b = borderline.get(cid)
        if b and abs(score - cutoff) <= 5 and not r["must_have_fail"] and b.get("verdict") in ("Go", "No-go") and b["verdict"] != verdict:
            verdict, basis = b["verdict"], f"panel borderline call: {b.get('reason', '')}"
        o = overrides.get(cid)
        if o:
            verdict, basis = o["verdict"], f"recruiter override: {o.get('reason', '')}"
        flags = list(r.get("flags", [])) + notes
        if "unclear" in r["must_haves"].values():
            flags.append("a must-have is unclear from the CV")
        bg = [c for c in rubric["criteria"] if c["signal"] == "background"]
        if bg and bg[0]["id"] in r["criteria"]:
            note = r["criteria"][bg[0]["id"]].get("scorer_reason", "")
            if note:
                flags = [f"Background: {note}"] + flags
        rows.append({"id": cid, "label": manifest[cid]["label"], "score": score,
                     "verdict": verdict, "basis": basis, "why_proceed": r["why_proceed"],
                     "why_not": r["why_not"], "flags": flags})

    rows.sort(key=lambda x: (x["score"] is None, -(x["score"] or 0)))
    (run / ("final-draft.json" if draft else "final.json")).write_text(json.dumps({"cutoff": cutoff, "rows": rows}, indent=1, ensure_ascii=False))
    lines = [f"Cut-off: {cutoff}. Go = score at or above the cut-off with every must-have met.", "",
             "| ID | Candidate | Score | Go / No-go | Why proceed | Why not | Comments |",
             "|---|---|---|---|---|---|---|"]
    for x in rows:
        lines.append(f"| {x['id']} | {x['label']} | {x['score'] if x['score'] is not None else '—'} | "
                     f"**{x['verdict']}** ({x['basis']}) | "
                     f"{cell(x['why_proceed'])} | {cell(x['why_not'])} | {cell(x['flags'], 3)} |")
    out = "\n".join(lines) + "\n"
    if not draft:
        (run / "report.md").write_text(out)
    print(out)
    if draft:
        band = [x["id"] for x in rows if x["score"] is not None and abs(x["score"] - cutoff) <= 5]
        print(json.dumps({"borderline": band}))


if __name__ == "__main__":
    main()
