# Architecture

## Idea

The content of a JD is researched; its form is fixed. The two are kept apart:

- **Form**: the skeleton (15 blocks), the design tokens, the fonts and the company text. It is data in the repo, measured from the published SDE JDs. Agents can't change it.
- **Content**: one `jd.json` per role, in a strict schema with word limits. Agents write it, challengers attack it, and scripts check it.

The `.docx` is a pure function of `jd.json` and the form: `render_docx.py`.

## jd-builder pipeline

```
HR brief
   │
   ▼
[1] Initializer ── 01-intake.json  (role, level, function, city, must-include list)
   │
   ▼
[2] Researcher ◄──────────────► [3] VP challenger
   02-research-rN.json            03-challenge-rN.json
   (sources, dated)               (score /100, blocking objections)
   loop until score ≥ 95 and no blocking objection, max 4 rounds, then ask HR
   │
   ▼
[4] Structurer ── 04-draft.json ── validate_jd.py (+ must-include)
   │
   ▼
[5] Format challenger ── 05-format-review.json (skeleton + voice rules)
   │
   ▼
[6] Copy pass + /humanizer ── 06-final.json ── validate_jd.py
   │
   ▼
[7] Designer ── render_docx.py → JD-<slug>.docx ── check_design.py (+ page images vs reference)
   │
   ▼
HR gets the .docx and a summary
```

- **Orchestrator** = the main session following `SKILL.md`. It owns the loop, the gates and `run.json`. Subagents can't spawn subagents, so the loop lives here.
- **Roles** = `roles/*.md`, one prompt each. Each role gets only its role file and the paths it needs. Without a subagent tool the orchestrator plays the roles in turn; the outputs are the same files.
- **Gates** are scripts where possible (`validate_jd.py`, `check_design.py`) and challenger scores where judgement is needed.

## State

`<workspace>/jd-runs/<date>-<slug>/`, one numbered file per step plus `run.json`. Each step reads earlier files and writes one new file. A run can be resumed, audited, or re-rendered without redoing research.

## Why these choices

| Choice | Why |
|---|---|
| Plugin marketplace in this repo | One install command per laptop; works in the desktop app, Cowork and the CLI; updates by `git push` |
| Skill folder self-contained | Also works if uploaded as a plain skill; scripts never reach outside it |
| python-docx renderer, not a template .docx | Every measurement lives in `tokens.json`; no hand-edited Word template drifting from the spec |
| Fonts embedded in the .docx | Looks identical on laptops without Archivo, Newsreader or IBM Plex Mono |
| Newsreader cut at optical size 13.2 | Matches the line widths of the Chrome-rendered originals |
| Two-column grid as borderless tables | Word has no CSS grid; tables give a fixed gutter and keep sections together |
| Word limits per slot | Keeps the page rhythm of the originals and stops padding |
| Banned-phrase list + British spelling check | Cheap, deterministic guard against AI-sounding text and US spelling |

## Known limits

- Word tables have square corners (the originals have about 4 pt radius).
- Line breaks can differ by a word from the Chrome PDFs.
- `extract_pdf_jd.py` only reads PDFs in this exact layout.
