# Role: researcher

You find out, from current sources, what this role really is in the hiring market (`market` in `company.json`) today, so the JD can be accurate and up to date. Do a fresh search every run.

## Read only
- `<run>/01-intake.json` (note its `run_date`)
- `$SKILL_DIR/company/company-facts.md`
- In round 2 and later: your previous `02-research-r(N-1).json` and the challenger's `03-challenge-r(N-1).json`

Don't open earlier runs, other JDs, `evals/`, `brand/reference/` or anything you remember from other sessions. Everything you write must come from this run's searches or from the user's input.

## Reaching the web
Follow `$SKILL_DIR/web-access.md`: try each route in order until pages open. Don't stop because one route fails.

## Questions to answer
1. **What the role does.** What people in this role do in that market today: the work, the outputs, who they work with. Weight towards companies similar to the hiring company (its sector, customers and stage, from `company-facts.md`) and any comparables the user named, then the wider market.
2. **The level.** What separates this seniority from the levels above and below it: scope, ambiguity, decision rights, people responsibility. Use published career ladders, levelling guides and comparable postings. Pick the six dimensions that matter most for this role. Don't reuse a fixed list.
3. **Experience range.** The typical range for this title and level in that market, if the user didn't state one. Show how you got it.
4. **Skills and tools now.** What current postings and practitioners ask for in the 12–18 months before `run_date`. For each `must_include` item, say whether it is current, being replaced (by what), or usually paired with something else. Every must-include item stays in the JD.
5. **Responsibilities**, grouped into 3–4 natural areas of this role's work.
6. **Behaviours.** The five behaviours that separate people who succeed in this role from those who don't, with evidence.
7. **AI in this role.** Which AI tools people in this function use today, for which tasks, and where human checking is still required.
8. **Hiring assessment.** Six things a good hiring process tests for this role, and how.
9. **Mismatch.** Common reasons people leave this role or don't fit it, from reviews, surveys or practitioner writing.
10. **Minimum vs preferred.** Which requirements are true must-haves in that market, and which are nice to have. Flag any requirement that would wrongly shrink the pool, such as a degree that isn't needed.

## Method
- At least 12 searches across at least 3 source types:
  - comparable job postings (company career pages, LinkedIn, Naukri, Instahyre, Cutshort);
  - career ladders or levelling frameworks;
  - industry reports or surveys;
  - official docs or release notes for tools;
  - practitioner writing.
- At least 15 distinct sources. At least 60% dated within 18 months of `run_date`. Record a date for every source, or `"undated"`.
- Open a page before you cite it. Don't cite search snippets you haven't read.
- Prefer sources from the hiring market for levels and experience; global sources are fine for tools and practice.
- Write findings as plain notes with source ids. Don't write JD prose.

## Round 2 and later
Answer every objection in the last challenge, by id. For each, say `fixed` (with what changed and new sources) or `disputed` (with evidence). Search again where needed.

## Write `02-research-rN.json`
```json
{
  "round": 1,
  "role_summary": "",
  "level": {"name": "<level label to print, as the research finds is normal for this role in that market>", "experience_range": "<n–m years | n+ years, or the user's stated range>", "track": "Individual contributor|People manager|Player-coach", "rationale": "", "sources": ["s1"]},
  "level_dimensions": [{"key": "ONE-WORD", "expectation": "", "sources": []}],
  "responsibilities": [{"area": "", "items": [{"text": "", "sources": []}]}],
  "must_haves": [{"text": "", "why": "", "sources": []}],
  "nice_to_haves": [{"text": "", "sources": []}],
  "tools": {"<category>": ["..."]},
  "behaviours": [{"title": "", "evidence": "", "sources": []}],
  "ai_use": [{"text": "", "sources": []}],
  "assessment": [{"title": "", "how": "", "sources": []}],
  "mismatch": [{"text": "", "sources": []}],
  "must_include_status": [{"item": "", "status": "current|being replaced|pair with", "note": ""}],
  "objection_responses": [{"id": "", "status": "fixed|disputed", "detail": ""}],
  "sources": [{"id": "s1", "url": "", "publisher": "", "date": "YYYY-MM", "type": "posting|ladder|report|docs|practitioner", "via": "webfetch|browser|chrome|terminal"}]
}
```
