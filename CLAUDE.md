# hiring: maintainer notes

This repo ships the `hr-hiring` Claude plugin. HR installs it; you are maintaining it.

## Rules
- Each skill folder (`plugins/hr-hiring/skills/<skill>/`) must stay self-contained. Scripts read only files inside it, so it also works when uploaded as a standalone skill.
- `brand/tokens.json` and `structure/skeleton.json` are the sources of truth. The `.md` files next to them explain them. Change both together.
- Keep `SKILL.md` short: steps, gates and pointers. Detail goes in `roles/`, `structure/`, `brand/` and `voice/`, and is loaded only when a step needs it.
- No personal data in the repo: no CVs, candidate names or salaries of real people.
- Content and form never mix. No JD wording (examples, earlier runs, the blueprint PDFs) may be placed inside the skill folder or referenced by any role. The blueprint PDFs live in `evals/` for importer tests only.
- JD writing rules are in `voice/voice-guide.md`: plain, human, British/Indian spelling, no em dashes or contrast framing.

## Before you commit
`bash evals/jd-builder/run_checks.sh` and `python3 evals/resume-screener/test_scripts.py`. Both must print `ALL PASS`. The first builds placeholder fixtures at min and max size, validates, renders and design-checks them, tests that the validator rejects AI patterns, and checks the PDF importer. The second tests every resume-screener script on invented data.
- Never commit real CVs or screening results; tests build invented data at runtime.
- After changing anything in a skill folder, run `python3 tools/build_skill_zips.py` so `install/*.zip` matches; `run_checks.sh` fails otherwise.
- Skill descriptions stay at 200 characters or fewer, so the skills also upload to claude.ai.

## Changing the look
1. Edit `brand/tokens.json`, and the matching row in `brand/design-spec.md`.
2. Run the checks, then open a rendered .docx next to `brand/reference/*.png`.

## Adding a section or slot
Update `skeleton.json` (order, labels, purpose, limits), `jd.schema.json`, `render_docx.py`, `validate_jd.py`, `jd-structure.md`, the role files that fill it, and `evals/jd-builder/make_fixtures.py`. Then run the checks.
