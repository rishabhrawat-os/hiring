# Onsurity hiring skills

Claude skills for Onsurity's HR team, packaged as one plugin (`hr-hiring`).

| Skill | What it does | Status |
|---|---|---|
| `jd-builder` | Researches a role from whatever you tell it and writes the JD as a branded Word file | Live |
| `resume-screener` | Scores and ranks CVs against a JD, with a go/no-go for round one | Planned |

## Install (once per laptop)

Works in the Claude desktop app (Code tab), Cowork and Claude Code.

```
/plugin marketplace add rishabhrawat-os/hiring
/plugin install hr-hiring@onsurity-hiring
```

Get updates with `/plugin marketplace update onsurity-hiring`.

The Word files are built with Python. If Claude says `python-docx` is missing, let it run `pip install python-docx`. The skill needs web access for research.

## Use

Tell it the role in your own words, as much or as little as you have:

- "/jd-builder performance marketing manager, Bengaluru, Google Ads and Meta"
- "We need a senior Java backend engineer, Kafka and Kubernetes are a must"
- Or paste the hiring manager's notes.

Anything you name (a tool, skill or requirement) is guaranteed to be in the JD. Everything else, including level, experience range, responsibilities and tools, comes from fresh research on the role in India. A VP-level challenger has to score it 95+ before it is written up. The finished `.docx` carries its own fonts, so it looks the same on any laptop.

Other commands: `/jd-builder resume` continues an interrupted run; `/jd-builder render <file.json>` re-renders after you edit the content file by hand.

## What every JD looks like

The house layout: a navy top bar, the title, a five-cell summary panel, a two-column grid of labelled sections, the navy "Non-negotiable" box, six assessment cards, and the "Read twice" panel. See `plugins/hr-hiring/skills/jd-builder/brand/design-spec.md`.

## Repo map

`STRUCTURE.md` lists every folder. `ARCHITECTURE.md` explains how the agents and files fit together.
