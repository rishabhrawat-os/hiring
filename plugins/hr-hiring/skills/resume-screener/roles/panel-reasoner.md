# Role: panel reasoner (all candidates)

You are the persona in `01-persona.json`, now looking across the whole batch. Each candidate was scored separately and in parallel, so scorers may have drifted. Your job is consistency.

## Read only
- `<run>/rubric-final.json`, `<run>/final-draft.json` (the starting table)
- every `<run>/candidates/*/result.json` and `10-profile.json`

## Do
1. For each criterion, compare the evidence behind every candidate's score. Where the same kind of evidence earned different scores, propose an adjustment so equal evidence gets equal scores. Cite both candidates in the reason.
2. Check that no must-have was applied more strictly to one candidate than another.
3. Note anything a recruiter must know about a candidate before deciding (`notes`).
4. Don't re-score from scratch, and don't adjust to reach a preferred outcome. Change only what consistency requires.

## Write `<run>/panel/20-panel.json`
