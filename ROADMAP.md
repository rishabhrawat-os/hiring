# Roadmap

## jd-builder

| Step | Scope | Status |
|---|---|---|
| 1. Form | Layout, fonts, blueprint, company content, renderer, design checks | Done |
| 2. Content pipeline | Initializer, researcher, VP challenger (pass ≥ 95), structurer, format challenger, copy pass with humanizer, designer | Done; first live run in this release |
| 3. Pilot | HR runs real roles across functions; tune limits and rubric from what they change by hand | Next |

Settled:
- Content comes only from the user's input and fresh research in each run. The blueprint PDFs gave layout and company details only.
- No salary, benefits or perks: the blueprint has no block for them.
- Market and default city come from `company/company.json` (currently India and Bengaluru); nothing in the skill assumes them.
- No em dashes, contrast framing or other AI writing patterns.

## resume-screener

| Step | Scope | Status |
|---|---|---|
| 1. Pipeline | Persona and rubric (challenger, 85 bar), recruiter approval, optional calibration, per candidate in parallel (extract + score, one challenger review), panel for borderline cases only, table, overrides, re-runs | Built |
| 2. Pilot | One live role, compared with the recruiter's own shortlist; tune anchors and the reconcile tolerance | Next |
