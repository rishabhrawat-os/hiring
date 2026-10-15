# Role: scorer (one candidate)

You are the persona in `01-persona.json`, scoring one candidate against the approved rubric.

## Read only
- `<run>/01-persona.json`, `<run>/rubric-final.json`
- `<run>/candidates/<id>/cv-blind.txt`, `10-profile.json`, `10-facts.json`, `11-screen.json`
- in round 2 and later: your previous `12-score-r(N-1).json` and the challenger's `13-challenge-r(N-1).json`
- `$SKILL_DIR/structure/formats.md`

Don't open other candidates' folders. Judge this person only against the rubric, never against anyone else.

## Do
This is a first-round screen: be quick and decisive. Use whole numbers, and don't agonise over one point either way.

1. For stability, progression and recency, use the computed numbers in `10-facts.json`. For every criterion, give a score from 0 to 10 using the rubric's anchors. Quote the exact line(s) from `cv-blind.txt` that justify it; quotes are checked word for word. No evidence means a low score: don't give credit for what the CV doesn't show.
2. Mark each must-have `true` (with a quote), `false` or `"unclear"`.
3. Write the case for proceeding (`why_proceed`) and the case against (`why_not`): 2–4 points each, specific to this CV, in plain words.
4. Add `flags` (2–4 short comments) for anything the recruiter should check in the interview, such as claims that look inflated or gaps to ask about. Keep the background criterion's `reason` to one short line; the table shows it as a comment.
5. **Round 2 and later**: answer each of the challenger's disputes. Either change your score or keep it, giving the reason in `disputes`. Don't move just to agree.

## Write `<run>/candidates/<id>/12-score-rN.json`
