# Roadmap

## jd-builder

| Step | Scope | Status |
|---|---|---|
| 1. Format | Analyse the 3 SDE JDs. Skeleton, schema, design tokens, fonts, company content, voice rules, renderer, validators, designer role, gold examples | **Done** |
| 2. Research loop | Initializer (intake questions, must-include list, domain + level), researcher (India-first sources, dated, recency rules), VP challenger (persona per domain, 100-point rubric, pass at 95), structurer, format challenger, copy pass + humanizer | Next |
| 3. Evals + pilot | 5 role briefs across functions and levels (engineering, marketing, sales, operations, data); HR runs 2 real roles; tune limits and the rubric | — |

Decisions already made: the skill lives in this repo; anyone can run it in the Claude desktop app or Cowork; the challenger pass bar is 95; roles are India-based; the format comes from the SDE JDs.

Open questions for step 2:
- The level names Onsurity uses outside engineering (e.g. Associate, Manager, Senior Manager), and their experience ranges.
- Whether a salary band ever appears (no slot for it today).
- Whether the challenger should be allowed web search, or only critique the researcher's sources.

## resume-screener

Takes any jd.json (or an imported JD), scores CVs against it, ranks them, and gives a go/no-go for round one. It reuses the skeleton's Minimum, Preferred and Assessment blocks as the scoring frame. Not started.
