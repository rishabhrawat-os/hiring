# Architecture

## Idea

A JD has two parts that never mix:

- **Form**: the layout (`brand/`), the blueprint of 15 blocks (`structure/`) and the company content (`company/company.json`). These were taken from the JD PDFs the user supplied as a blueprint: the layout, colours, type and company details only, none of their wording. Agents can't change the form.
- **Content**: written fresh for every run from the user's input and that run's web research. No earlier JD, run or example is ever shown to an agent.

The `.docx` is a pure function of the content file and the form: `render_docx.py`.

## Pipeline

```
User input (one line or pages)
   │
   ▼
[1] Initializer ─ 01-intake.json   stated facts, must-include list, what to research, challenger persona
   │
   ▼
[2] Researcher ◄────────────► [3] Challenger (VP of the role's function)
   02-research-rN.json            03-challenge-rN.json
   fresh web search, ≥15 dated    own searches + source spot-checks,
   sources, India-first           score /100, objections
   loop until score ≥ 95 with no blocking/major objection (max 4 rounds, then ask HR)
   │
   ▼
[4] Structurer ─ 04-draft.json ─ validate_jd.py --must-include
   │
   ▼
[5] Format challenger ◄─► structurer   blueprint fit, faithful to research, human writing,
   05-format-review-rN.json             proofreading; score ≥ 95, max 3 rounds
   │
   ▼
[6] Copy pass + /humanizer ─ 06-final.json ─ validate_jd.py
   │
   ▼
[7] Designer ─ render_docx.py → JD-<slug>.docx ─ check_design.py + page images
   │
   ▼
HR gets the .docx and a short note
```

- **Orchestrator** = the main session following `SKILL.md`. It owns the loops, the gates and `run.json`. The loops live here because subagents can't start subagents.
- **Roles** = `roles/*.md`. Each role file lists exactly what that role may read. Roles run as separate subagents when the tool exists, so the challenger judges the research cold.
- **Gates**: scripts where a rule is mechanical (`validate_jd.py`, `check_design.py`), challenger scores where judgement is needed.

## Guards against generic or AI-sounding JDs

- Fresh research each run, at least 15 sources, most from the last 18 months, every claim tied to a source.
- An independent challenger that runs its own searches and opens cited pages.
- `validate_jd.py` fails any em dash, "not X, Y" or "not just" contrast, "rather than", rhetorical question, exclamation mark, staged reveal, banned phrase or US spelling.
- A format challenger that reads every line for triads, closers, filler and repetition.
- A humanizer pass, then validation again.

## State

`<workspace>/jd-runs/<date>-<slug>/`: one numbered file per step plus `run.json`. Runs can be resumed or audited. Runs are never inputs to other runs.

## Why these choices

| Choice | Why |
|---|---|
| Plugin marketplace in this repo | One install command per laptop; desktop app, Cowork and CLI; updates by `git push` |
| Self-contained skill folder | Works if uploaded as a plain skill; scripts never reach outside it |
| python-docx renderer driven by tokens.json | Every measurement in one file; no hand-edited Word template drifting from the spec |
| Fonts embedded in the .docx | Looks the same on laptops without Archivo, Newsreader or IBM Plex Mono |
| Space limits per block | Keeps the page layout intact |
| Placeholder fixtures for tests | Test the layout without putting example wording anywhere near the agents |

## Known limits

- Word tables have square corners (the blueprint PDFs have about 4 pt radius).
- Line breaks can differ from a browser-made PDF by a word.
