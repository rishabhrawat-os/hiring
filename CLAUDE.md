# hiring: maintainer notes

This repo ships the `hr-hiring` Claude plugin. HR installs it; you are maintaining it.

## Rules
- The skill folder (`plugins/hr-hiring/skills/jd-builder/`) must stay self-contained. Scripts read only files inside it, so it also works when uploaded as a standalone skill.
- `brand/tokens.json` and `structure/skeleton.json` are the sources of truth. The `.md` files next to them explain them. Change both together.
- Keep `SKILL.md` short: steps, gates and pointers. Detail goes in `roles/`, `structure/`, `brand/` and `voice/`, and is loaded only when a step needs it.
- No personal data in the repo: no CVs, candidate names or salaries of real people. Examples are published JDs only.
- British English in all JD content.

## Before you commit
`bash evals/jd-builder/run_checks.sh`. It validates the examples and the fixture, renders them, and design-checks the output. It must print `ALL PASS`.

## Changing the look
1. Edit `brand/tokens.json`, and the matching row in `brand/design-spec.md`.
2. Run the checks, then open a rendered .docx next to `brand/reference/*.png`.

## Adding a section or slot
Update `skeleton.json` (order, labels, limits), `jd.schema.json`, `render_docx.py`, `validate_jd.py`, `jd-structure.md`, and the three examples. Then run the checks.
