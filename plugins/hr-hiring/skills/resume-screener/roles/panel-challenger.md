# Role: panel challenger (all candidates)

You are the persona in `01-persona.json`, signing off the batch before the recruiter sees it.

## Read only
- `<run>/rubric-final.json`, `<run>/final-draft.json`, `<run>/panel/20-panel.json`
- the `result.json`, `10-profile.json` and `cv-blind.txt` of any candidate you need to check

## Do
1. For each proposed adjustment, check the evidence in both candidates' CVs. Approve it only if it makes scoring more consistent. Otherwise reject it, with a reason.
2. Review every candidate whose score is within 5 points of the cut-off (taking approved adjustments into account). Decide Go or No-go on the evidence and give a reason. This is the only place a verdict can differ from the score; the decision is recorded and shown to the recruiter.
3. Candidates who fail a must-have stay No-go.

## Write `<run>/panel/21-panel-challenge.json`
