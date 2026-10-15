#!/usr/bin/env python3
"""Write <run>/reasoning.md: one file with the key reasoning behind every
decision in the run, for anyone who wants to check why a candidate got
their score or verdict, or how the system weighs things.

It only gathers what the steps already recorded: persona, rubric and its
challenge, recruiter decisions, and for each candidate the must-have
calls, computed facts, per-criterion scores with the deciding reason,
scorer-challenger differences, panel changes and overrides. Long reasons
are shortened to their first sentence.

    python3 build_log.py <run>
"""
import json
import re
import sys
from pathlib import Path


def load(p, default=None):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else default


def short(s, n=220):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    first = re.split(r"(?<=[.])\s", s)[0].rstrip(";, ")
    s = first if len(first) >= 40 else s
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def latest(d, prefix):
    files = sorted(d.glob(f"{prefix}-r*.json"), key=lambda p: int(re.search(r"-r(\d+)\.json$", p.name).group(1)))
    return load(files[-1]) if files else None


def cell(s):
    return str(s).replace("|", "/").replace("\n", " ")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run = Path(sys.argv[1])
    rj = load(run / "run.json", {})
    persona = load(run / "01-persona.json", {})
    rubric = load(run / "rubric-final.json")
    final = load(run / "final.json") or load(run / "final-draft.json")
    manifest = {c["id"]: c for c in load(run / "manifest.json", {"candidates": []})["candidates"]}
    crit = {c["id"]: c for c in rubric["criteria"]}
    out = []
    w = out.append

    w(f"# Screening reasoning log: {persona.get('role_being_hired', {}).get('title') or rubric.get('role', '')}")
    w("")
    w(f"Run `{run.name}`, run date {rj.get('run_date', '')}. This file records the key decisions only. "
      "Every score is calculated by script from the criterion scores below; agents never type a total.")
    if rj.get("demo"):
        w("")
        w("> Demo run on invented CVs. Recruiter checkpoints were approved by the assistant, not a recruiter.")
    w("")

    w("## 1. Who judged")
    w("")
    w(f"- **Persona:** {persona.get('title', '')} ({persona.get('years', '')} years), hiring for "
      f"{persona.get('role_being_hired', {}).get('title', '')} ({persona.get('role_being_hired', {}).get('experience', '')}).")
    for k, label in (("what_they_look_for", "Looks for"), ("what_worries_them", "Worried by")):
        items = persona.get(k, [])[:4]
        if items:
            w(f"- **{label}:** " + "; ".join(short(i, 120) for i in items) + ".")
    if rj.get("recruiter_context"):
        w(f"- **Recruiter context:** {short(rj['recruiter_context'], 300)}")
    w("")

    w("## 2. Rubric")
    w("")
    w(f"**Cut-off: {rubric['cutoff']}.** Go = score at or above the cut-off with no must-have clearly failed.")
    w("")
    w("**Must-haves**")
    for m in rubric["must_haves"]:
        w(f"- {m['id']}: {short(m['requirement'], 160)}. Evidence needed: {short(m['evidence_needed'], 160)}")
    w("")
    w("| ID | Criterion | Signal | Weight | What earns a 10 |")
    w("|---|---|---|---|---|")
    for c in rubric["criteria"]:
        w(f"| {c['id']} | {cell(c['name'])} | {c['signal']} | {c['weight']} | {cell(short(c['anchors'].get('10', ''), 150))} |")
    w("")
    if rubric.get("background_definition"):
        w(f"- **Background (capped):** {short(rubric['background_definition'], 260)}")
    rounds = sorted(run.glob("03-rubric-challenge-r*.json"))
    for f in rounds:
        ch = load(f)
        heavy = [o for o in ch.get("objections", []) if o.get("severity") in ("blocking", "major")]
        w(f"- **Rubric challenge {f.stem.split('-')[-1]}:** {ch.get('score')}/100"
          + ("; blocking/major points: " + "; ".join(f"{o['id']} ({o['severity']}) {short(o.get('issue', ''), 110)}" for o in heavy) if heavy else "; no blocking or major points") + ".")
    for k in ("checkpoint1", "checkpoint2"):
        if rj.get(k):
            w(f"- **{k.replace('checkpoint', 'Checkpoint ')}:** {rj[k]}")
    w("")

    w("## 3. Candidates")
    w("")
    w("Score = sum of (weight × final criterion score) ÷ 10. A criterion's final score is the average of the scorer's and the challenger's, "
      "rounded to 0.5, after any approved panel adjustment. The points column is rounded for display.")
    w("")
    rows = {r["id"]: r for r in (final or {}).get("rows", [])}
    order = [r["id"] for r in (final or {}).get("rows", [])] or list(manifest)
    for cid in order:
        d = run / "candidates" / cid
        row = rows.get(cid, {})
        w(f"### {cid} · {manifest.get(cid, {}).get('label', '')} · "
          f"{row.get('score') if row.get('score') is not None else '—'} · {row.get('verdict', '')}")
        w("")
        if row.get("basis"):
            w(f"**Decision:** {row['verdict']}, because {row['basis']}.")
        screen = load(d / "11-screen.json", {})
        res = load(d / "result.json")
        facts = load(d / "10-facts.json")
        if facts:
            stints = facts.get("short_stints_last_5y", [])
            w(f"**Facts (calculated):** {facts.get('total_months_worked')} months worked across {facts.get('companies')} employer(s) "
              f"(average {facts.get('average_months_per_company')} months), {facts.get('promotions')} promotion(s), "
              f"{len(stints)} stint(s) under 12 months in the last 5 years"
              + (" (" + "; ".join(f"{s['company']}: {s['months']} months" + (f", reason given: {short(s['reason_given'], 80)}" if s.get('reason_given') else "") for s in stints) + ")" if stints else "")
              + (". Gaps (interview only, not scored): " + ", ".join(f"{g['months']} months after {g['after']}" for g in facts.get('gaps_for_interview_only', [])) if facts.get("gaps_for_interview_only") else "")
              + ".")
        w("")
        w("**Must-haves**")
        mh_src = (res or {}).get("must_haves") or {m["id"]: m.get("met") for m in screen.get("must_haves", [])}
        quotes = {m["id"]: m.get("evidence", "") for m in screen.get("must_haves", [])}
        for mid, met in mh_src.items():
            label = {True: "met", False: "not met", "unclear": "unclear"}.get(met, str(met))
            q = quotes.get(mid)
            w(f"- {mid}: {label}" + (f". Evidence: \"{short(q, 160)}\"" if q else ""))
        if screen.get("screened_out"):
            for r_ in screen.get("reasons", []):
                w(f"- Screened out: {short(r_, 260)}")
            w("")
            continue
        if not res:
            w("- Not scored yet.")
            w("")
            continue
        s = latest(d, "12-score") or {}
        c = latest(d, "13-challenge") or {}
        sc = {x["id"]: x for x in s.get("criteria", [])}
        cc = {x["id"]: x for x in c.get("criteria", [])}
        w("")
        w("| Criterion | Wt | Scorer | Challenger | Final | Points | Deciding reason |")
        w("|---|---|---|---|---|---|---|")
        for k, v in res["criteria"].items():
            fin = v["score"]
            for note in row.get("flags", []):
                m = re.match(rf"panel: {k} ([\d.]+)→([\d.]+)", note)
                if m:
                    fin = float(m.group(2))
            pts = round(crit[k]["weight"] * fin / 10, 1)
            w(f"| {k} {cell(crit[k]['name'])} | {crit[k]['weight']} | {sc.get(k, {}).get('score', '—')} | {cc.get(k, {}).get('score', '—')} | "
              f"{fin} | {pts} | {cell(short(v.get('scorer_reason', ''), 170))} |")
        disputes = c.get("disputes", [])
        if disputes:
            w("")
            w("**Challenger disputes**")
            for x in disputes:
                w(f"- {x.get('id')}: scorer {x.get('other_score')}, challenger {x.get('my_score')}. {short(x.get('reason', ''), 200)}")
        diffs = [f for f in res.get("flags", []) if "averaged" in f or f.startswith("must-have")]
        if diffs:
            w("")
            w("**Scorer and challenger differed:** " + "; ".join(diffs) + ".")
        w("")
        w("**Why proceed:** " + "; ".join(short(x, 160) for x in res.get("why_proceed", [])[:3]))
        w("")
        w("**Why not:** " + "; ".join(short(x, 160) for x in res.get("why_not", [])[:3]))
        other = [f for f in row.get("flags", []) if not ("averaged" in f or f.startswith(("must-have", "a must-have")))]
        if other:
            w("")
            w("**Comments:** " + "; ".join(short(x, 160) for x in other[:5]))
        w("")

    panel = load(run / "panel" / "20-panel.json")
    pch = load(run / "panel" / "21-panel-challenge.json")
    w("## 4. Panel")
    w("")
    if not panel:
        band = [r["id"] for r in (final or {}).get("rows", []) if r.get("score") is not None and abs(r["score"] - rubric["cutoff"]) <= 5]
        w("Skipped: no candidate was within 5 points of the cut-off." if not band else f"Not run yet for borderline candidates: {', '.join(band)}.")
    else:
        ok = set((pch or {}).get("approve_adjustments", []))
        for a_ in panel.get("adjustments", []):
            w(f"- {a_['id']} {a_['candidate']} {a_['criterion']} {a_['from']}→{a_['to']}: {'approved' if a_['id'] in ok else 'rejected'}. {short(a_.get('reason', ''), 200)}")
        for b in (pch or {}).get("borderline_reviews", []):
            w(f"- Borderline {b['candidate']}: {b['verdict']}. {short(b.get('reason', ''), 200)}")
    overrides = load(run / "overrides.json", [])
    if overrides:
        w("")
        w("## 5. Recruiter overrides")
        w("")
        for o in overrides:
            w(f"- {o['candidate']}: {o['verdict']}. {short(o.get('reason', ''), 200)}")
    (run / "reasoning.md").write_text("\n".join(out) + "\n")
    print(f"wrote {run / 'reasoning.md'}")


if __name__ == "__main__":
    main()
