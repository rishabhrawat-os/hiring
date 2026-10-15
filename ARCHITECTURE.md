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

# resume-screener

```
JD + CVs ─► ingest.py
Stage A (once per JD)
  persona + rubric builder (one agent) ─► rubric challenger (85 bar, check_rubric.py, max 2 rounds)
  CHECKPOINT 1: recruiter approves/edits rubric, background definition, cut-off
                (optional: score 2 CVs first to check the judgement)
Stage B (per candidate, parallel waves of up to 8 subagents)
  wave 1: extractor + scorer (one agent): blind CV, profile, facts.py, must-have screen, scores
  wave 2: challenger reviews once; reconcile.py checks quotes, averages, notes gaps > 2 points
  candidates/<id>/result.json  (score computed by the script)
Stage C (only if a candidate is within 5 points of the cut-off)
  panel reasoner (consistency for borderline cases) ─► panel challenger (approves, borderline calls)
  build_table.py ─► report.md
  CHECKPOINT 3: recruiter reviews the table, overrides, re-runs one candidate with a note
```

- **One orchestration per candidate.** Each candidate's steps run as separate subagents that see only that candidate's folder, so candidates are judged against the rubric and never against each other. Only the panel looks across the batch, and only for consistency.
- **Parallel by stage.** Subagents can't start subagents, so the orchestrator runs each stage as a wave: every candidate's extract-and-score at once, then every challenger. State on disk (`status.py --next`) tells it who needs what, so a failed candidate resumes alone.
- **Scores are computed, never typed.** `reconcile.py` averages the agreed criterion scores and applies the weights. `build_table.py` applies the panel adjustments that were approved, the cut-off, the must-haves and any overrides.
- **Evidence or nothing.** Every score quotes the blind CV, and quotes that aren't in it are rejected.
- **Bias controls:**
  - the CV is blinded before scoring;
  - background is capped at 10 points, defined by the recruiter, and shown as a one-line comment;
  - the rubric challenger scores fairness;
  - short stints are judged in context.

**Speed choices (first-round screen).** These replace the earlier, slower version:

| Was | Now | Why |
|---|---|---|
| Rubric pass bar 95, up to 4 rounds | 85, up to 2 rounds; only blocking objections hold it up | Good enough to separate clear fits from clear misses |
| Persona and rubric as two agents | One agent, two role files | Saves a hand-off |
| Extractor and scorer as two agents | One agent per candidate | Saves a wave |
| Scorer and challenger agree within 1 point, up to 3 rounds | One challenger review; gaps over 2 points are averaged and noted | Extra rounds rarely change a verdict |
| Calibration always on | Optional | — |
| Panel on every batch | Only for candidates within 5 points of the cut-off | Nobody else's verdict can change |
| Tenure and stints judged by agents | Calculated by `facts.py` | Deterministic |
