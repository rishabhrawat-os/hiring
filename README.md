# Onsurity hiring skills

Claude skills for Onsurity's HR team, packaged as one plugin (`hr-hiring`).

| Skill | What it does | Status |
|---|---|---|
| `jd-builder` | Researches a role from whatever you tell it and writes the JD as a branded Word file | Live |
| `resume-screener` | Scores and ranks CVs against a JD, with a go/no-go for round one | Planned |

## Install (once per laptop)

You need Python 3 on the laptop (macOS: install from python.org if `python3` asks for developer tools). The skill also needs web access, for research.

**Claude desktop app / Cowork:** open the plugin settings, add the marketplace `rishabhrawat-os/hiring`, and install **hr-hiring**. If the repository is private, the GitHub account connected to Claude needs read access to it.

**Claude Code (terminal):**
```
/plugin marketplace add rishabhrawat-os/hiring
/plugin install hr-hiring@onsurity-hiring
```
Update with `/plugin marketplace update onsurity-hiring`.

On first use the skill installs `python-docx` for you (into your user folder, or a private virtual environment if your Python doesn't allow that).

## Use

Tell it the role in your own words, as much or as little as you have:

- "/hr-hiring:jd-builder performance marketing manager, Bengaluru, Google Ads and Meta"
- "Write a JD: senior Java backend engineer, Kafka and Kubernetes are a must"
- Or paste the hiring manager's notes.

Anything you name (a tool, skill or requirement) is guaranteed to appear in the JD. So is any experience range or city you state. Everything else (level, experience, responsibilities, tools, how the role is assessed) comes from fresh research on the role in India. A challenger playing the VP of that function has to score the research 95 or more before anything is written. The writing then goes through a format challenger and a humanizer pass. The JD never mentions salary.

You get a `.docx` with the fonts built in, plus a folder with every step's output in `~/JD-Builder/jd-runs/` (or your Cowork workspace).

Other commands: `/hr-hiring:jd-builder resume` continues an interrupted run; `/hr-hiring:jd-builder render <file.json>` re-renders after you edit the content file by hand.

## What every JD looks like

The house layout: a navy top bar, the title, a five-cell summary panel, a two-column grid of labelled sections, the navy "Non-negotiable" box, six assessment cards, and the "Read twice" panel. See `plugins/hr-hiring/skills/jd-builder/brand/design-spec.md`.

## Repo map

`STRUCTURE.md` lists every folder. `ARCHITECTURE.md` explains how the agents and files fit together.
