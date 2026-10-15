---
name: resume-screener
description: Screen CVs against any JD. Builds a role-specific persona and scoring rubric (agent + challenger, recruiter approves), scores every CV in parallel with a scorer and an independent challenger quoting the CV, then a panel checks consistency and gives each candidate a score and a go/no-go, shown as a table. Use for "screen these resumes", "score CVs for <role>", "/hr-hiring:resume-screener".
---

# resume-screener

You are the orchestrator. You run the stages below, stop at the three recruiter checkpoints, run candidates in parallel, keep everything on disk, and show the result as a table.

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
2. **Persona** (`roles/persona.md`) writes `01-persona.json`.
3. **Rubric loop:**
   - **Builder:** `roles/rubric-builder.md` writes `02-rubric-rN.json`. Gate: `check_rubric.py rubric`.
   - **Challenger:** `roles/rubric-challenger.md` writes `03-rubric-challenge-rN.json`. Gate: `check_rubric.py challenge`.
   - **Repeat** until the challenge gate passes, for at most 4 rounds. If round 4 still fails, show the recruiter the open objections at checkpoint 1.
4. **Checkpoint 1: the recruiter approves the rubric.**
   - **Show:**
     - the persona;
     - must-haves;
     - a table of criteria (name, weight, what counts, the 0/5/10 anchors);
     - the background definition;
     - the suggested cut-off.
   - **Ask** them to approve or change anything: weights, criteria, extra considerations of their own, the background definition, and the cut-off.
   - **If they change something:** save their words in `run.json` → `recruiter_feedback`, run the builder and challenger again, and show the rubric again.
   - **When they approve:** save it as `rubric-final.json` with their cut-off, and re-run `check_rubric.py rubric rubric-final.json`.
5. **Checkpoint 2: calibration.**
   - **Score two candidates first:** run stage B for two CVs, ideally one that looks strong and one that looks weak from the profile.
   - **Show** both results in full: scores per criterion with quotes, why proceed, why not.
   - **Ask:** "Does this match how you would judge them?"
   - **If they disagree:** record why, adjust the anchors or weights in `rubric-final.json`, re-run the check, and re-score those two.
   - **When they agree:** move on.

## Stage B: one orchestration per candidate, all in parallel
Each candidate runs on its own, never seeing the others.

Run the steps in waves. In each wave, start one subagent per waiting candidate, in a single message so they run in parallel, at most 8 at a time. Use `status.py <run> --next` to see who needs which step.

| Step | Role (one subagent per candidate) | Gate |
|---|---|---|
| Extract + screen | `roles/extractor.md` | `status.py <run> --check-blind <id>` passes; `11-screen.json` exists |
| Score round N | `roles/scorer.md` | file exists |
| Challenge round N | `roles/candidate-challenger.md` | `reconcile.py <cand> --rubric rubric-final.json` |

`reconcile.py` exit codes:
- **0:** `result.json` is written and the candidate is done.
- **2:** they disagree. Run the scorer, then the challenger, at round N+1. At round 3, reconcile writes the result and flags what is still unresolved.
- **1:** a file is invalid, for example a quote that isn't in the CV. Re-run the step that wrote it, telling it what failed.

Candidates screened out on a must-have stop after extraction.

Every step writes its own file in the candidate's folder, so a failed or interrupted candidate resumes alone. Wait until `status.py` shows every candidate done before stage C.

## Stage C: panel
1. **Draft table:** run `python3 "$SKILL_DIR/scripts/build_table.py" <run> --draft`.
2. **Panel reasoner** (`roles/panel-reasoner.md`) writes `panel/20-panel.json` with its consistency adjustments.
3. **Panel challenger** (`roles/panel-challenger.md`) writes `panel/21-panel-challenge.json`: it approves or rejects each adjustment and makes the borderline calls.
4. **Final table:** run `python3 "$SKILL_DIR/scripts/build_table.py" <run>`. It applies the approved adjustments, recomputes every score, applies the cut-off and the must-have results, and writes `report.md`.

## Checkpoint 3: results
- **Show** `report.md` as a table:
  - ID and candidate;
  - score;
  - score without background;
  - go/no-go and its basis;
  - why proceed, why not, flags.
- **Offer:**
  - the full reasoning for any candidate;
  - an override, saved to `overrides.json` with the recruiter's reason, after which the table is rebuilt;
  - a re-run of one candidate with a note from the recruiter, which deletes that candidate's 12/13/result files and runs stage B for that one candidate with the note added to `run.json`.
- **Finally**, ask whether to keep or delete the run folder. It holds personal data.

## Rules
- **Fresh for every JD.** Every JD gets a fresh persona and rubric. Never reuse a rubric, persona or result from another run.
- **The CV is the only evidence.** Scores come only from it. No web searches or outside lookups about candidates.
- **Computed scores.** Scores and verdicts are computed by `reconcile.py` and `build_table.py`, never typed by an agent.
- **Score and go/no-go only:** no ranks or priorities.
- **Privacy:** CVs and results never leave the run folder, and are never committed or uploaded anywhere.
