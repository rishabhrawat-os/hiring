---
name: resume-screener
description: Screen CVs against any JD. A fast first-round screen. Builds a role-specific persona and scoring rubric (agent + challenger, recruiter approves), scores every CV in parallel with a scorer and an independent challenger quoting the CV, has a panel review only the borderline cases, and gives each candidate a score and a go/no-go with comments, shown as a table. Use for "screen these resumes", "score CVs for <role>", "/hr-hiring:resume-screener".
---

# resume-screener

You are the orchestrator. This is a first-round screen: aim for a quick, defensible go/no-go, not a precise score. You run the stages below, stop at the recruiter checkpoints, run candidates in parallel, keep everything on disk, and show the result as a table.

## Paths
`SKILL_DIR` is the absolute path of this folder: the base directory shown when the skill loaded, or `${CLAUDE_PLUGIN_ROOT}/skills/resume-screener`. Pass `SKILL_DIR` and the run folder to every role. Use absolute paths in every command. File shapes are in `structure/formats.md`.

## Setup
- **Python packages.** PDF and Word CVs need `pypdf` and `python-docx`. Install them with `python3 -m pip install --user pypdf python-docx`; if that is refused, make a venv at `~/JD-Builder/.venv` and use its python.
- **Fallback.** If extraction still yields no text for a CV (scanned PDF), the extractor reads the original file directly.

## Run folder
- **Location:** `<root>/screen-runs/<YYYY-MM-DD>-<role-slug>/`. `<root>` is the Cowork workspace folder when running in Cowork; everywhere else it is `~/JD-Builder`. Never put CVs or results inside a code repository.
- **run.json:** keep `step`, `status`, `cutoff`, `rubric_round` and `recruiter_feedback` up to date. On "resume", run `status.py <run>` and continue.

## Stage A: persona and rubric (once per JD)
1. **Ingest:**
   - ask the recruiter for the JD (a file or pasted text) and the CVs (a folder, several files, or a zip);
   - run `python3 "$SKILL_DIR/scripts/ingest.py" <run> --jd <jd> <cv paths...>`.
2. **Persona and rubric:** one subagent with `roles/persona.md`, then `roles/rubric-builder.md`, writes `01-persona.json` and `02-rubric-r1.json`. Gate: `check_rubric.py rubric`.
3. **Rubric challenge:** `roles/rubric-challenger.md` writes `03-rubric-challenge-r1.json`. Gate: `check_rubric.py challenge`, which passes at **85 or more with no blocking objection**.
   - **If it fails:** run one more builder and challenger round.
   - **If round 2 also fails:** take it to checkpoint 1 with the open objections shown.
4. **Checkpoint 1: the recruiter approves the rubric.** Show:
   - the persona;
   - the must-haves;
   - the criteria table (name, weight, the 0/5/10 anchors);
   - the background definition;
   - the suggested cut-off;
   - any open challenger points.

   Ask them to approve or change it, and to set the cut-off. Save changes to `run.json` → `recruiter_feedback` and run one builder round. Save the approved rubric as `rubric-final.json` and re-run `check_rubric.py rubric` on it.

   **Optional calibration:** ask "Score 2 CVs first so you can check the judgement? (default: no)". If yes, run stage B for two CVs, show them, adjust the anchors if the recruiter disagrees, then continue.

## Stage B: one orchestration per candidate, all in parallel
Each candidate runs on its own, never seeing the others. Start one subagent per candidate in a single message so they run in parallel, at most 8 at a time. `status.py <run> --next` shows who needs which step.

| Wave | Subagent per candidate | Gate |
|---|---|---|
| 1 | **Extract + score:** `roles/extractor.md`, then `roles/scorer.md`, in the same subagent | `status.py <run> --check-blind <id>` passes. If `11-screen.json` says screened out, the candidate is done and stops here |
| 2 | **Challenge:** `roles/candidate-challenger.md` (one review, no back-and-forth) | `reconcile.py <cand> --rubric rubric-final.json` |

`reconcile.py`:
- **Agreement:** scores within 2 points count as agreed.
- **Wider gaps:** averaged and noted in the comments, so there are no extra rounds.
- **Exit 1:** a file is invalid, for example a quote that isn't in the CV. Re-run the step that wrote it, telling it what failed.

Wait until `status.py` shows every candidate done.

## Stage C: panel (only for borderline candidates)
1. Run `python3 "$SKILL_DIR/scripts/build_table.py" <run> --draft`. Its last line lists the borderline candidates: those within 5 points of the cut-off.
2. **If the list is empty, skip the panel**, because no verdict can change.
3. **Otherwise:**
   - `roles/panel-reasoner.md` (given the borderline list) writes `panel/20-panel.json`;
   - `roles/panel-challenger.md` writes `panel/21-panel-challenge.json`.
4. Run `python3 "$SKILL_DIR/scripts/build_table.py" <run>`. It computes the scores, applies the cut-off, the must-haves, the approved adjustments and any overrides, and writes `report.md`.

## Checkpoint 3: results
- **Show** `report.md` as a table:
  - ID and candidate;
  - score;
  - go/no-go and its basis;
  - why proceed and why not;
  - comments (interview pointers, a background note, any scorer–challenger gap).
- **Offer:**
  - the full reasoning for any candidate;
  - an override, saved to `overrides.json` with the recruiter's reason, after which the table is rebuilt;
  - a re-run of one candidate with a note, which deletes that candidate's 12/13/result files and runs stage B for them.
- **Finally**, ask whether to keep or delete the run folder. It holds personal data.

## Rules
- **Fresh for every JD.** Every JD gets a fresh persona and rubric. Never reuse a rubric, persona or result from another run.
- **The CV is the only evidence.** Scores come only from it. No web searches or outside lookups about candidates.
- **Computed scores.** Scores and verdicts are computed by `reconcile.py` and `build_table.py`, never typed by an agent.
- **Score and go/no-go only:** no ranks or priorities.
- **Privacy:** CVs and results never leave the run folder, and are never committed or uploaded anywhere.
