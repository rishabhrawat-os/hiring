---
name: jd-builder
description: Write an Onsurity job description from whatever the user gives (even a one-line comment), using fresh web research on the role in India, a VP-level challenger that must score it 95+, a format challenger, a humanizer pass, and a designer that renders the branded Word file. Use for "write a JD", "create a job description", "JD for <role>", "/jd-builder".
---

# jd-builder

You are the orchestrator. You run the steps below in order, enforce each gate, keep state on disk, and hand HR the finished `.docx`.

All paths are relative to this skill's folder.

## Two kinds of input, kept apart
- **Form** (fixed, never researched): the layout in `brand/`, the blueprint in `structure/`, and the company content in `company/company.json`.
- **Content** (fresh every run): only the user's input plus this run's web research. No earlier JD, earlier run, example or remembered text is used as content. Each run starts from zero.

## Setup (once per machine)
Check with `python3 -c "import docx"`. If that fails: `pip install python-docx`. LibreOffice is optional; it only adds page images for the designer.

## State
Make a run folder: `<workspace>/jd-runs/<YYYY-MM-DD>-<role-slug>/`, where `<workspace>` is the folder the user picked in Cowork or the desktop app, otherwise `~/JD-Builder`. Every step writes its numbered file there. Keep `run.json` updated: `{"step": "", "status": "", "research_rounds": 0, "scores": [], "format_rounds": 0}`. On "resume", continue from `run.json`.

## Steps
| # | Step | Role file | Writes | Gate to move on |
|---|---|---|---|---|
| 1 | Intake | `roles/initializer.md` | `01-intake.json` | role identified (ask the user only if it isn't) |
| 2 | Research | `roles/researcher.md` | `02-research-rN.json` | file written with ≥15 sources |
| 3 | Challenge | `roles/challenger.md` | `03-challenge-rN.json` | **score ≥ 95 and no blocking or major objection**. Otherwise go back to step 2 with N+1. After 4 rounds, show HR the open objections and ask: accept, add input, or run 2 more rounds |
| 4 | Structure | `roles/structurer.md` | `04-draft.json` | `validate_jd.py --must-include` passes |
| 5 | Format challenge | `roles/format-challenger.md` | `05-format-review-rN.json` | **score ≥ 95 and no blocking or major issue**. Otherwise the structurer revises; at most 3 rounds |
| 6 | Copy | `roles/copy.md` (runs `/humanizer` if installed) | `06-final.json`, `06-copy-notes.md` | `validate_jd.py --must-include` passes |
| 7 | Design | `roles/designer.md` | `JD-<slug>.docx`, `07-design-review.json` | `check_design.py` passes and the checklist is all ok |
| 8 | Hand-off | you | — | HR gets the .docx path and a short note covering: level and experience used, the challenger's final score and rounds, any must-include item flagged as outdated, and anything still open |

## How to run a role
- If an Agent/Task tool is available, run each role as its own subagent. Give it its role file, the run folder path, and the paths the role file lists. Give it nothing else: no summary of other JDs, no opinions of your own about the content.
- Researcher and challenger need web search and page fetch. If the session has no web access, stop and tell HR. Don't write a JD from memory.
- Without a subagent tool, play each role yourself, one at a time. Read only what that role file allows, and write its file before you start the next role.

## Rules
- Every tool, skill or requirement the user named appears in the JD; `--must-include` enforces this.
- Fixed text is only the section labels, the headings and `company/company.json`. Everything else is written for this role.
- No salary, compensation, benefits or perks: the blueprint has no place for them.
- No company facts beyond `company/company-facts.md`.
- Never change `brand/` or `structure/` to make content fit. Change the content.
- No personal data in run files: describe roles, never people.

## Other commands
- `/jd-builder render <jd.json>`: steps 7 and 8 only, for a content file HR has edited by hand.
- `/jd-builder resume`: continue the last run from `run.json`.
