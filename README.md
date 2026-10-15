# Onsurity hiring skills

Claude skills for Onsurity's HR team, packaged as one plugin (`hr-hiring`).

| Skill | What it does | Status |
|---|---|---|
| `jd-builder` | Writes a job description in the Onsurity layout and gives you a branded Word file | Format, rendering and checks live. Research loop in progress |
| `resume-screener` | Scores and ranks CVs against a JD, with a go/no-go for round one | Planned |

## Install (once per laptop)

Works in the Claude desktop app (Code tab), Cowork and Claude Code.

```
/plugin marketplace add rishabhrawat-os/hiring
/plugin install hr-hiring@onsurity-hiring
```

Get updates with `/plugin marketplace update onsurity-hiring`.

The Word files are built with Python. If Claude says `python-docx` is missing, let it run `pip install python-docx pdfplumber`.

## Use

- **New JD:** "write a JD for a senior backend engineer, Java, 6+ years, Bengaluru", or just `/jd-builder`. *(The research loop ships in step 2; see `ROADMAP.md`.)*
- **Render a JD you already have as JSON:** `/jd-builder render path/to/jd.json`
- **Revise an old JD:** `/jd-builder import path/to/old-jd.pdf`, edit, then render.

The finished `.docx` carries its own fonts, so it looks the same on any laptop. Open it in Word to read, edit or export to PDF.

## What every JD looks like

The house layout taken from the SDE I/II/III JDs: a navy top bar, the title, a five-cell summary panel, a two-column grid of labelled sections, the navy "Non-negotiable" box, six assessment cards, and the "Read twice" panel. See `plugins/hr-hiring/skills/jd-builder/brand/design-spec.md`.

## Repo map

`STRUCTURE.md` lists every folder. `ARCHITECTURE.md` explains how the agents and files fit together.
