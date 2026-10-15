---
name: jd-builder
description: Write a job description in the company's house layout from whatever the user gives (even a one-line comment), using fresh web research on the role in the hiring market, a VP-level challenger that must score it 95+, a format challenger, a humanizer pass, and a designer that renders the branded Word file. Use for "write a JD", "create a job description", "JD for <role>", "/hr-hiring:jd-builder".
---

# jd-builder

You are the orchestrator. You run the steps below in order, enforce every gate, keep state on disk, and hand HR the finished `.docx`.

## Paths
`SKILL_DIR` is the absolute path of this folder: the base directory shown when the skill loaded, or `${CLAUDE_PLUGIN_ROOT}/skills/jd-builder`. Every path below starts with it. Pass `SKILL_DIR` and the run folder to every role, and write every command with absolute paths, e.g. `python3 "$SKILL_DIR/scripts/validate_jd.py" ...`.

## Form and content are kept apart
- **Form** (fixed): the layout (`brand/`), the blueprint (`structure/`) and the company content (`company/company.json`).
- **Content**: only the user's input plus this run's web research. No earlier JD, earlier run, example or remembered text is used. Every run starts from zero.

## Setup
- **Which Python.** Python packages (`python-docx`, `pypdf`) are installed automatically when Claude starts, by the plugin's `ensure_deps.py`. It writes the Python to use into `~/JD-Builder/python`. Read that file and use that interpreter wherever this skill says `python3`; if the file is missing, use `python3`.
- **If a script says a package is missing:** run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ensure_deps.py"` and use the interpreter it records. If the plugin root isn't available (the skill was uploaded on its own), run `python3 -m pip install --user python-docx pypdf`; if that is refused, `python3 -m venv ~/JD-Builder/.venv`, then `~/JD-Builder/.venv/bin/pip install python-docx pypdf`, and use `~/JD-Builder/.venv/bin/python`.

Web search and page fetch must be available. Without them, stop and tell HR: a JD can't be written from memory.

## State
- **Run folder:** `<root>/jd-runs/<YYYY-MM-DD>-<role-slug>/`. `<root>` is the Cowork workspace folder when running in Cowork; everywhere else it is `~/JD-Builder`. Never write into a code repository that happens to be open.
- **run.json:** keep it updated with:
  ```
  {"run_date", "step", "status", "research_round", "format_round",
   "scores": [], "approved_draft", "humanizer_used", "override": null}
  ```
- **Resume:** on "resume", continue from `run.json`.

## Steps
| # | Step | Role | Writes | Gate (run it; never trust a self-reported pass) |
|---|---|---|---|---|
| 0 | Save input | you | `00-input.md` (the user's words, verbatim) and `input/` (copies of attachments) | file exists |
| 1 | Intake | `roles/initializer.md` | `01-intake.json` | the role is identified; ask the user only if it isn't |
| 2 | Research | `roles/researcher.md` | `02-research-rN.json` | `check_gate.py research <file> --run-date <run_date>` (rounds 2+: add `--previous-challenge 03-challenge-r(N-1).json`) |
| 3 | Challenge | `roles/challenger.md` | `03-challenge-rN.json` | `check_gate.py challenge <file> --research <02 file>`. If it fails, go back to step 2 with N+1 |
| 4 | Structure | `roles/structurer.md` | `04-draft-r1.json` | `validate_jd.py <file> --intake 01-intake.json` |
| 5 | Format challenge | `roles/format-challenger.md` | `05-format-review-rN.json` | `check_gate.py format <file>`. If it fails, the structurer writes `04-draft-r(N+1).json` and the format challenger reviews again |
| 6 | Copy | `roles/copy.md` | `06-final.json`, `06-copy-notes.md` | `validate_jd.py 06-final.json --intake 01-intake.json`, then the format challenger's facts check, gated by `check_gate.py facts 05-facts-check.json --approved <approved_draft> --final 06-final.json --intake 01-intake.json` |
| 7 | Design | `roles/designer.md` | `JD-<slug>.docx`, `07-design-review.json` | `check_design.py` passes and every checklist item is ok or "not verified" |
| 8 | Hand-off | you | — | Give HR the .docx path and a short note: level and experience used (and whether research or the user set them), the challenger's final score and number of rounds, any must-include item flagged as outdated, whether humanizer ran, and anything open |

**Loop limits:**
- Research rounds: 4.
- Format rounds: 3.
- When a limit is reached, show HR the open objections or issues and offer three choices:
  1. add input, which is appended to `00-input.md`; then rerun from step 1;
  2. run 2 more rounds;
  3. override.
- An override is recorded in `run.json` as `{"step", "score", "by": "HR"}` and printed in the hand-off as "below the 95 bar (score N), approved by HR".
- Never move past a failed gate without an explicit override.

## How to run a role
- **With an Agent/Task tool**, run each role as its own subagent. Give it:
  - its role file;
  - `SKILL_DIR`;
  - the run folder;
  - for the initializer only, the path of `00-input.md` and `input/`.

  Give it nothing else: no summary of other JDs and none of your own opinions about the content.
- **Without a subagent tool**, play each role yourself, one at a time. Read only what that role file allows, and write its file before you start the next role.

## Rules
- User-named terms come first. Every tool, skill or requirement the user named appears in the JD, even where the writing rules would otherwise flag a word. The validator exempts them.
- Stated facts are kept. If the user stated an experience range, city or level, the JD uses it.
- No salary, pay, benefits or perks: the blueprint has no place for them. If the user mentions pay, note it for HR in the hand-off and leave it out of the JD.
- The only fixed text is the section labels, the headings and `company/company.json`.
- No company facts beyond `company/company-facts.md`.
- Never edit `brand/`, `structure/` or `scripts/` during a run. If something looks wrong there, report it in the hand-off.
- No personal data in run files: describe roles, never people.

## Other commands
- `/hr-hiring:jd-builder resume`: continue the last run.
- `/hr-hiring:jd-builder render <file.json>`: validate, render and design-check a content file HR edited by hand (steps 7–8).
