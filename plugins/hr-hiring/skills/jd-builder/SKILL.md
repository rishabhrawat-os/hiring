---
name: jd-builder
description: Build an Onsurity job description as a branded Word file. Researches the role for the Indian market, has a VP-level challenger push back until it's right, fits it to the house JD layout, humanizes and checks it. Also renders, imports or checks an existing JD. Use for "write a JD", "create a job description", "JD for <role>", "/jd-builder".
---

# jd-builder

You are the orchestrator. You run the steps in order, keep state on disk, and hand finished work to HR. Every JD has the same skeleton and look, whatever the role; only the content changes.

All paths below are relative to this skill's folder.

## Status
- **Live (step 1):** `render`, `import`, `check`, and the whole format layer: skeleton, schema, design tokens, fonts, company content, validators, and the designer role.
- **Step 2, not built yet:** the research loop (initializer, researcher, VP challenger, structurer, copy pass). If HR asks for a new JD before step 2 ships, say so and offer `render` from a hand-written JSON instead.

## Commands
| Say | Does |
|---|---|
| `/jd-builder` or "write a JD for …" | Full flow below (step 2) |
| `/jd-builder render <jd.json>` | Validate, render the .docx, design-check it |
| `/jd-builder import <jd.pdf>` | Turn an existing Onsurity-format PDF into jd.json, for a revision |
| `/jd-builder check <jd.docx>` | Design check of a rendered file |

## Setup (once per machine)
`python3 -c "import docx, pdfplumber"`. If that fails: `pip install python-docx pdfplumber`. LibreOffice is optional; it only enables page images for the visual check.

## Where things are
| Need | File |
|---|---|
| What goes where, limits, fixed vs slot | `structure/jd-structure.md` (`skeleton.json` is the machine copy) |
| Content shape | `structure/jd.schema.json` |
| Look: colours, fonts, sizes, grid | `brand/design-spec.md` (`tokens.json` is the machine copy) |
| How it should read | `voice/voice-guide.md`, `voice/banned-phrases.txt` |
| Fixed company text | `company/company.json`. Facts agents may use: `company/company-facts.md` |
| Engineering stack rows | `company/engineering-stack.json` |
| Gold examples | `examples/sde-{1,2,3}-backend.json` (+ `originals/` PDFs) |
| Role prompts | `roles/*.md` |

Load a file only when the current step needs it.

## State
One folder per JD: `<workspace>/jd-runs/<YYYY-MM-DD>-<role-slug>/`. In Cowork, `<workspace>` is the folder the user picked; otherwise it's `~/JD-Builder`. Each step writes one numbered file and updates `run.json` (`{"step": "...", "status": "...", "rounds": n, "scores": [...]}`). On "resume", read `run.json` and continue from the step it names.

## Full flow
| # | Step | Role | Writes | Gate |
|---|---|---|---|---|
| 1 | Intake | initializer *(step 2)* | `01-intake.json`: role, level, function, city, experience, track, HR's must-include list, domain | HR confirms the summary |
| 2 | Research | researcher *(step 2)* | `02-research-rN.json` with sources | — |
| 3 | Challenge | VP challenger *(step 2)* | `03-challenge-rN.json`: score /100, objections | score ≥ 95 and no blocking objection; max 4 rounds, then ask HR |
| 4 | Structure | structurer *(step 2)* | `04-draft.json` in the schema | `validate_jd.py` passes, incl. `--must-include 01-intake.json` |
| 5 | Format challenge | format checker *(step 2)* | `05-format-review.json` | skeleton rules and voice rules met |
| 6 | Copy | copy pass + `/humanizer` if installed | `06-final.json` | `validate_jd.py` passes again |
| 7 | Design | `roles/designer.md` | `JD-<slug>.docx`, `07-design-review.json` | `check_design.py` passes and the checklist is ok |
| 8 | Hand-off | you | — | Send HR the .docx and a 5-line summary: level, score, rounds, sources used, open notes |

Run roles 2–7 as subagents when the Agent/Task tool exists: give each its `roles/<name>.md` and the paths it needs, and nothing else. Without subagents, play each role yourself, one at a time, and write its file before you start the next.

## Rules
- Every tool, skill or spec HR names goes into the JD. `--must-include` enforces this.
- Fixed text (About us, equal opportunity, section labels and headings, trait titles, footer) is never rewritten. It comes from `company/` and `skeleton.json`.
- No company facts beyond `company/company-facts.md` and the intake.
- Indian market: comparable roles and pay norms in India; city from the intake (default Bengaluru).
- Never change `brand/` to make content fit. Cut the content instead.
- Nothing personal in a JD or in run files. Roles only, not people.

## render (live)
1. `python3 scripts/validate_jd.py <jd.json>`. Stop and show the FAIL lines if any.
2. `python3 scripts/render_docx.py <jd.json> <out>.docx`
3. `python3 scripts/check_design.py <out>.docx --png <out>-pages`. If page images were made, follow `roles/designer.md` step 4.
4. Give HR the .docx path.

## import (live)
`python3 scripts/extract_pdf_jd.py <in.pdf> <out.json>`, then `validate_jd.py` on the result. Only works on PDFs in the Onsurity layout.
