#!/usr/bin/env python3
"""Tests for the resume-screener scripts, on invented data built at runtime.
No real CVs or names are stored in the repo."""
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / "plugins/hr-hiring/skills/resume-screener"
PY = sys.executable
fails = 0


def run(script, *args):
    r = subprocess.run([PY, str(SKILL / "scripts" / script), *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def expect(name, cond, detail=""):
    global fails
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else f"\n     {detail[:400]}"))
    fails += 0 if cond else 1


CV_A = """Test Person A
test.a@example.com | +91 90000 00001
Experience
Analyst II, Example Insurance Co (2021-04 to present)
Built weekly claims dashboards in SQL and Power BI used by 40 managers.
Cut report preparation time from 3 days to 4 hours.
Promoted from Analyst I to Analyst II in 2023.
Analyst I, Example Health Pvt Ltd (2019-06 to 2021-03)
Wrote Python scripts to clean policy data.
Education
B.Sc. Statistics, Example University, 2019
"""
CV_B = """Test Person B
test.b@example.com
Experience
Sales Executive, Example Retail (2022-01 to present)
Handled walk-in customers and billing.
Education
B.Com, Example College, 2021
""" + "Filler line about retail operations and store opening checklists. " * 6

RUBRIC = {
    "role": "Data Analyst", "persona": "Head of Analytics",
    "must_haves": [{"id": "M1", "requirement": "SQL used at work", "evidence_needed": "a role that used SQL"}],
    "criteria": [
        {"id": "R1", "group": "role_fit", "signal": "role_fit", "name": "SQL and BI", "weight": 40, "what_counts": "x", "anchors": {"0": "a", "5": "b", "10": "c"}},
        {"id": "R2", "group": "role_fit", "signal": "role_fit", "name": "Python", "weight": 20, "what_counts": "x", "anchors": {"0": "a", "5": "b", "10": "c"}},
        {"id": "R3", "group": "career", "signal": "stability", "name": "Stability", "weight": 5, "what_counts": "x", "anchors": {"0": "a", "5": "b", "10": "c"}},
        {"id": "R4", "group": "career", "signal": "industry", "name": "Industry", "weight": 10, "what_counts": "x", "anchors": {"0": "a", "5": "b", "10": "c"}},
        {"id": "R5", "group": "career", "signal": "breadth_depth", "name": "Breadth", "weight": 5, "what_counts": "x", "anchors": {"0": "a", "5": "b", "10": "c"}},
        {"id": "R6", "group": "career", "signal": "achievements", "name": "Achievements", "weight": 10, "what_counts": "x", "anchors": {"0": "a", "5": "b", "10": "c"}},
        {"id": "R7", "group": "career", "signal": "progression", "name": "Progression", "weight": 5, "what_counts": "x", "anchors": {"0": "a", "5": "b", "10": "c"}},
        {"id": "R8", "group": "career", "signal": "background", "name": "Background", "weight": 5, "what_counts": "x", "anchors": {"0": "a", "5": "b", "10": "c"}},
        {"id": "R9", "group": "career", "signal": "recency", "name": "Recency", "weight": 0, "zero_reason": "covered by R1", "what_counts": "", "anchors": {"0": "a", "5": "b", "10": "c"}},
        {"id": "R10", "group": "red_flags", "signal": "red_flags", "name": "Red flags", "weight": 0, "zero_reason": "short CVs", "what_counts": "", "anchors": {"0": "a", "5": "b", "10": "c"}},
    ],
    "background_definition": "x", "cutoff": 60,
}


def score_doc(cid, rnd, scores, quote="Built weekly claims dashboards in SQL and Power BI used by 40 managers."):
    return {"candidate": cid, "round": rnd,
            "must_haves": [{"id": "M1", "met": True, "evidence": quote}],
            "criteria": [{"id": c["id"], "score": scores.get(c["id"], 5), "evidence": [quote], "reason": "r"} for c in RUBRIC["criteria"]],
            "why_proceed": ["p"], "why_not": ["n"], "flags": []}


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    src = t / "src"
    src.mkdir()
    (src / "jd.txt").write_text("Data Analyst. SQL, Python, Power BI. 2-4 years. Bengaluru. " * 5)
    (src / "a.txt").write_text(CV_A)
    import docx
    d = docx.Document()
    for line in CV_B.splitlines():
        d.add_paragraph(line)
    d.save(src / "b.docx")
    with zipfile.ZipFile(src / "batch.zip", "w") as z:
        z.writestr("c.txt", CV_A.replace("Person A", "Person C"))
        z.writestr("../escape.txt", "should be skipped")
    run_dir = t / "run"

    code, out = run("ingest.py", run_dir, "--jd", src / "jd.txt", src / "a.txt", src / "b.docx", src / "batch.zip")
    m = json.loads((run_dir / "manifest.json").read_text())
    expect("ingest: txt, docx and zip give 3 candidates", code == 0 and len(m["candidates"]) == 3, out)
    expect("ingest: unsafe zip path skipped", not (t / "escape.txt").exists() and not (run_dir / "input" / "escape.txt").exists())
    expect("ingest: docx text extracted", "Sales Executive" in (run_dir / "candidates/C02/cv.txt").read_text(), out)
    code, out = run("ingest.py", run_dir, "--jd", src / "jd.txt", src / "a.txt")
    expect("ingest: re-adding a file doesn't duplicate it", len(json.loads((run_dir / "manifest.json").read_text())["candidates"]) == 3, out)

    rf = run_dir / "rubric-final.json"
    rf.write_text(json.dumps(RUBRIC))
    code, out = run("check_rubric.py", "rubric", rf)
    expect("rubric: valid rubric passes", code == 0, out)
    bad = json.loads(json.dumps(RUBRIC))
    bad["criteria"][7]["weight"] = 15
    bad["criteria"][0]["weight"] = 30
    bad["criteria"] = [c for c in bad["criteria"] if c["signal"] != "progression"]
    p = t / "bad.json"
    p.write_text(json.dumps(bad))
    code, out = run("check_rubric.py", "rubric", p)
    expect("rubric: background over cap, missing signal, bad sum all caught",
           code == 1 and "cap is 10" in out and "progression" in out and "must be 100" in out, out)
    ch = {"round": 1, "score": 96, "by_dimension": {"job_relevance": 24, "coverage": 19, "anchors": 19, "weights": 20, "fairness": 14}, "objections": []}
    p.write_text(json.dumps(ch))
    expect("rubric challenge: 96 with no objections passes", run("check_rubric.py", "challenge", p)[0] == 0)
    p.write_text(json.dumps({**ch, "objections": [{"id": "x", "severity": "Major"}]}))
    expect("rubric challenge: bad severity fails", run("check_rubric.py", "challenge", p)[0] == 1)
    p.write_text(json.dumps({**ch, "score": 101, "by_dimension": {**ch["by_dimension"], "extra": 5}}))
    expect("rubric challenge: unknown dimension fails", run("check_rubric.py", "challenge", p)[0] == 1)

    c1 = run_dir / "candidates/C01"
    (c1 / "cv-blind.txt").write_text(CV_A)
    code, out = run("status.py", run_dir, "--check-blind", "C01")
    expect("blind check: email and phone caught", code == 1 and "email" in out and "phone" in out, out)
    (c1 / "cv-blind.txt").write_text("\n".join(CV_A.splitlines()[2:]))
    expect("blind check: clean text passes", run("status.py", run_dir, "--check-blind", "C01")[0] == 0)
    (c1 / "10-profile.json").write_text("{}")
    (c1 / "11-screen.json").write_text(json.dumps({"screened_out": False}))

    (c1 / "12-score-r1.json").write_text(json.dumps(score_doc("C01", 1, {"R1": 9})))
    (c1 / "13-challenge-r1.json").write_text(json.dumps(score_doc("C01", 1, {"R1": 6})))
    code, out = run("reconcile.py", c1, "--rubric", rf)
    expect("reconcile: gap of 3 asks for another round", code == 2 and "DISAGREE R1" in out, out)
    (c1 / "12-score-r2.json").write_text(json.dumps(score_doc("C01", 2, {"R1": 8}, quote="This line is not in the CV at all, invented")))
    (c1 / "13-challenge-r2.json").write_text(json.dumps(score_doc("C01", 2, {"R1": 7})))
    code, out = run("reconcile.py", c1, "--rubric", rf)
    expect("reconcile: invented quote rejected", code == 1 and "quote not found" in out, out)
    (c1 / "12-score-r2.json").write_text(json.dumps(score_doc("C01", 2, {"R1": 8})))
    code, out = run("reconcile.py", c1, "--rubric", rf)
    r = json.loads((c1 / "result.json").read_text()) if (c1 / "result.json").exists() else {}
    # R1 = 7.5 (mean of 8 and 7), others 5 -> (40*7.5 + 60*5)/100*10 = 60.0
    expect("reconcile: agreement writes result with computed score", code == 0 and r.get("score") == 60.0, out + json.dumps(r)[:200])

    for cid, s_, c_ in (("C02", 2, 2), ("C03", 9, 8)):
        cd = run_dir / "candidates" / cid
        (cd / "cv-blind.txt").write_text(CV_A)
        (cd / "10-profile.json").write_text("{}")
        (cd / "11-screen.json").write_text(json.dumps({"screened_out": False}))
        (cd / "12-score-r1.json").write_text(json.dumps(score_doc(cid, 1, {k["id"]: s_ for k in RUBRIC["criteria"]})))
        (cd / "13-challenge-r1.json").write_text(json.dumps(score_doc(cid, 1, {k["id"]: c_ for k in RUBRIC["criteria"]})))
        run("reconcile.py", cd, "--rubric", rf)
    code, out = run("status.py", run_dir, "--next")
    expect("status: all candidates done", code == 0 and json.loads(out) == {"done": ["C01", "C02", "C03"]}, out)

    code, out = run("build_table.py", run_dir, "--draft")
    expect("table: draft builds", code == 0 and "| C03 |" in out, out)
    (run_dir / "panel").mkdir()
    (run_dir / "panel/20-panel.json").write_text(json.dumps({"adjustments": [
        {"id": "p1", "candidate": "C01", "criterion": "R2", "from": 5, "to": 4, "reason": "consistency"},
        {"id": "p2", "candidate": "C03", "criterion": "R1", "from": 8.5, "to": 2, "reason": "rejected"}], "notes": {}}))
    (run_dir / "panel/21-panel-challenge.json").write_text(json.dumps({"approve_adjustments": ["p1"], "reject_adjustments": [{"id": "p2", "reason": "no"}],
        "borderline_reviews": [{"candidate": "C01", "verdict": "Go", "reason": "strong SQL evidence"}]}))
    code, out = run("build_table.py", run_dir)
    fin = json.loads((run_dir / "final.json").read_text())["rows"]
    row = {x["id"]: x for x in fin}
    # C01: R2 5->4 => 60 - 20*1/100*10 = 58.0, below cut-off 60 but within 5 -> panel borderline Go
    expect("table: approved adjustment applied, rejected one ignored", row["C01"]["score"] == 58.0 and row["C03"]["score"] == 85.0, json.dumps(row)[:300])
    expect("table: borderline call recorded", row["C01"]["verdict"] == "Go" and "borderline" in row["C01"]["basis"])
    expect("table: low score is No-go", row["C02"]["verdict"] == "No-go")
    (run_dir / "overrides.json").write_text(json.dumps([{"candidate": "C02", "verdict": "Go", "reason": "referral, test in interview"}]))
    run("build_table.py", run_dir)
    row = {x["id"]: x for x in json.loads((run_dir / "final.json").read_text())["rows"]}
    expect("table: recruiter override applied and labelled", row["C02"]["verdict"] == "Go" and "recruiter override" in row["C02"]["basis"])
    expect("table: report.md written", (run_dir / "report.md").read_text().count("| C0") == 3)

print("ALL PASS" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
