# File formats

Every step writes JSON in these shapes. Scripts check them, so field names must match exactly.

## Run folder
```
<root>/screen-runs/<YYYY-MM-DD>-<role-slug>/
  run.json                     step, status, cutoff, rounds, recruiter decisions
  manifest.json                ID → original file name (local only)
  00-jd.txt, input/            the JD and the original files
  01-persona.json
  02-rubric-rN.json, 03-rubric-challenge-rN.json
  rubric-final.json            the rubric the recruiter approved (the only one scoring uses)
  candidates/C01/
    cv.txt                     extracted text
    cv-blind.txt               the same with name, contact and personal details removed
    10-profile.json            structured profile
    10-facts.json              tenure, stints, promotions, recency, gaps (facts.py)
    11-screen.json             must-have screen
    12-score-rN.json           scorer
    13-challenge-rN.json       challenger
    result.json                written by reconcile.py
    status.json
  panel/20-panel.json, panel/21-panel-challenge.json
  overrides.json               recruiter overrides
  final.json, report.md        written by build_table.py
  reasoning.md                 key reasoning for every decision, written by build_log.py (shared with the recruiter)
```

## 01-persona.json
```json
{"title": "<senior title in the same function>", "years": "<top of the role's range + about 5>", "function": "", "role_being_hired": {"title": "", "level": "", "experience": ""},
 "domain": "", "what_they_look_for": [""], "what_worries_them": [""]}
```

## Rubric (02-rubric-rN.json and rubric-final.json)
```json
{"role": "", "persona": "",
 "must_haves": [{"id": "M1", "requirement": "", "evidence_needed": ""}],
 "criteria": [{"id": "R1", "group": "role_fit|career|red_flags",
   "signal": "role_fit|stability|industry|breadth_depth|achievements|progression|background|recency|red_flags",
   "name": "", "weight": 20, "what_counts": "",
   "anchors": {"0": "", "5": "", "10": ""}, "zero_reason": ""}],
 "background_definition": "", "cutoff": 70, "notes": ""}
```
Rules (`check_rubric.py`):
- weights are whole numbers adding to 100;
- every career signal is present (weight 0 is allowed, with a `zero_reason`);
- role-fit criteria carry at least 50;
- background carries at most 10;
- every criterion has 0, 5 and 10 anchors;
- there is at least one must-have;
- the cut-off is between 0 and 100.

## 03-rubric-challenge-rN.json
```json
{"round": 1, "score": 0,
 "by_dimension": {"job_relevance": 0, "coverage": 0, "anchors": 0, "weights": 0, "fairness": 0},
 "objections": [{"id": "rc1-1", "severity": "blocking|major|minor", "criterion": "", "issue": "", "required_change": ""}]}
```
Maximums: job_relevance 25, coverage 20, anchors 20, weights 20, fairness 15. Pass at 85+ with no blocking objection.

## 10-profile.json
```json
{"candidate": "C01", "total_years": 0, "roles": [{"company": "", "title": "", "start": "YYYY-MM", "end": "YYYY-MM|present", "months": 0, "scope": "", "achievements": [""], "reason_for_short_stint": ""}],
 "promotions": [{"company": "", "from": "", "to": "", "when": ""}], "education": [{"institution": "", "degree": "", "year": ""}],
 "skills": [""], "industries": [""], "gaps": [{"from": "", "to": "", "months": 0, "explained": ""}], "inconsistencies": [""]}
```

## 11-screen.json
```json
{"candidate": "C01", "screened_out": false, "must_haves": [{"id": "M1", "met": true, "evidence": "<quote from cv-blind.txt>"}], "reasons": [""]}
```
`screened_out` is true only when a must-have is clearly not met: false with evidence, never "unclear".

## 12-score-rN.json and 13-challenge-rN.json
```json
{"candidate": "C01", "round": 1,
 "must_haves": [{"id": "M1", "met": true, "evidence": "<quote>"}],
 "criteria": [{"id": "R1", "score": 7, "evidence": ["<exact quote from cv-blind.txt>"], "reason": ""}],
 "why_proceed": [""], "why_not": [""], "flags": [""],
 "disputes": [{"id": "R1", "other_score": 7, "my_score": 5, "reason": ""}]}
```
- `disputes` appears in challenger files, and in scorer revisions when they reply.
- Every quote must appear in `cv-blind.txt`; `reconcile.py` checks this.

## panel/20-panel.json
```json
{"adjustments": [{"id": "p1", "candidate": "C03", "criterion": "R2", "from": 8, "to": 6, "reason": "same evidence scored 6 for C01 and C05"}],
 "notes": {"C01": ""}}
```

## panel/21-panel-challenge.json
```json
{"approve_adjustments": ["p1"], "reject_adjustments": [{"id": "", "reason": ""}],
 "borderline_reviews": [{"candidate": "C04", "verdict": "Go|No-go", "reason": ""}]}
```

## overrides.json
`[{"candidate": "C02", "verdict": "Go", "reason": "<recruiter's words>"}]`
