---
name: resume-screener
description: Screen CVs against a JD: recruiter-approved rubric, each CV scored and checked, go/no-go table with reasons. Use for "screen these CVs" or /hr-hiring:resume-screener.
---

# resume-screener

You are the orchestrator. This is a first-round screen: aim for a quick, defensible go/no-go, not a precise score. You run the stages below, stop at the recruiter checkpoints, run candidates in parallel, keep everything on disk, and show the result as a table.

## Paths
`SKILL_DIR` is the absolute path of this folder: the base directory shown when the skill loaded, or `${CLAUDE_PLUGIN_ROOT}/skills/resume-screener`. Pass `SKILL_DIR` and the run folder to every role. Use absolute paths in every command. File shapes are in `structure/formats.md`.

## First use on this computer
If `~/JD-Builder/.welcome-shown` doesn't exist, show the user the guide in `${CLAUDE_PLUGIN_ROOT}/skills/help/GETTING-STARTED.md` (skip this if that file isn't there), then create `~/JD-Builder/.welcome-shown` and carry on with their request. Show it only once per computer.

## The user does no technical steps
The user is not technical. Never ask them to run a command, install anything, find a file or open a folder. Do it yourself, and if the computer asks for permission, tell them in one line to click **Allow**.
- **Python missing** (`python3 --version` fails): install it yourself.
  - macOS: run `xcode-select --install` and tell the user to click **Install** in the window that appears; wait, then continue.
  - Windows: `winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements`.
  - Linux: tell the user their IT team needs to install Python 3, because it needs an administrator.
  - Cowork and other cloud workspaces already have Python.
- **Opening results:** open finished files for the user (`open <file>` on macOS, `start "" "<file>"` on Windows, `xdg-open <file>` on Linux). In Cowork, link the file instead. In a claude.ai or desktop chat, copy it to the chat's outputs folder (for example `/mnt/user-data/outputs/`) and share it there so the user can download it.
- **Questions about files** ("where is my JD?", "open my results"): find the latest run folder and open or show the file.

## Setup
- **Which Python.** Python packages (`python-docx`, `pypdf`) are installed automatically when Claude starts, by the plugin's `ensure_deps.py`. It writes the Python to use into `~/JD-Builder/python`. Read that file and use that interpreter wherever this skill says `python3`; if the file is missing, use `python3`.
- **If a script says a package is missing:** run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ensure_deps.py"` and use the interpreter it records. If the plugin root isn't available (the skill was uploaded on its own), run `python3 -m pip install --user python-docx pypdf`; if that is refused, `python3 -m venv ~/JD-Builder/.venv`, then `~/JD-Builder/.venv/bin/pip install python-docx pypdf`, and use `~/JD-Builder/.venv/bin/python`. In a claude.ai or desktop chat, if pip cannot reach the internet, tell the user in one line to turn on **Code execution and file creation** and network access in Settings > Capabilities (on Team or Enterprise, their admin does this), then try again.
- **Fallback.** If extraction still yields no text for a CV (scanned PDF), the extractor reads the original file directly.

## Run folder
- **Location:** `<root>/screen-runs/<YYYY-MM-DD>-<role-slug>/`. `<root>` is the Cowork workspace folder when running in Cowork; everywhere else it is `~/JD-Builder`. Never put CVs or results inside a code repository.
- **run.json:** keep `step`, `status`, `cutoff`, `rubric_round` and `recruiter_feedback` up to date. On "resume", run `status.py <run>` and continue.

## Stage A: persona and rubric (once per JD)
1. **Ingest:**
   - ask the recruiter for the JD (a file or pasted text) and the CVs (a folder, several files, or a zip), and, optionally, anything the JD doesn't say that they want weighed (company or team context, industries they value, deal-breakers). Save their words in `run.json` → `recruiter_context`. Don't add context of your own;
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
- **Show** `report.md` as a table, and give the recruiter the path of `reasoning.md`: one file per run with the key reasoning for every decision (who judged, the rubric and its challenge, recruiter decisions, and for each candidate the must-have calls with quotes, calculated facts, each criterion's scorer/challenger/final score with the deciding reason, disputes, panel changes and overrides). It is for anyone who wants to check a decision or see what the system weighs. `build_table.py` writes it automatically.
  - ID and candidate;
  - score;
  - go/no-go and its basis;
  - why proceed and why not;
  - comments (interview pointers, a background note, any scorer–challenger gap).
- **Offer:**
  - to answer "why did <candidate> get this score?" from that candidate's section of `reasoning.md`, in plain words;
  - an override, saved to `overrides.json` with the recruiter's reason, after which the table is rebuilt;
  - a re-run of one candidate with a note, which deletes that candidate's 12/13/result files and runs stage B for them.
- **Finally**, ask whether to keep or delete the run folder. It holds personal data.

## Rules
- **Fresh for every JD.** Every JD gets a fresh persona and rubric. Never reuse a rubric, persona or result from another run.
- **The CV is the only evidence.** Scores come only from it. No web searches or outside lookups about candidates.
- **Computed scores.** Scores and verdicts are computed by `reconcile.py` and `build_table.py`, never typed by an agent.
- **Score and go/no-go only:** no ranks or priorities.
- **Privacy:** CVs and results never leave the run folder, and are never committed or uploaded anywhere.
