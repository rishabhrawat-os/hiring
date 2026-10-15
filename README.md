# Onsurity hiring skills

Claude skills for Onsurity's HR team, packaged as one plugin (`hr-hiring`).

| Skill | What it does | Status |
|---|---|---|
| `jd-builder` | Researches a role from whatever you tell it and writes the JD as a branded Word file | Live |
| `resume-screener` | Scores every CV against any JD and gives a go/no-go, with the reasons, in a table | Live |

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

## Screening CVs

Say "/hr-hiring:resume-screener" and give it a JD (file or pasted text) and the CVs (a folder, several files or a zip).

1. It builds a hiring-manager persona about 5 years more senior than the role, and a scoring rubric. The rubric covers:
   - role fit;
   - job stability, industry relevance, breadth and depth, achievements, promotions, recency and red flags;
   - company and college background, capped at 10 points.

   A challenger has to score the rubric 85 or more before you see it. This is a first-round screen, so the bar is "good enough to separate clear fits from clear misses".
2. **You approve the rubric**: change weights, add your own considerations, and set the cut-off.
3. **Optional check**: if you want, it scores two CVs first so you can check the judgement before the full batch.
4. Every CV is then scored separately and in parallel. A scorer and an independent challenger, each reviewing once, both quote the CV for every point, and invented quotes are rejected. Tenure, short stints, promotions and recency are calculated by a script from the CV's dates.
5. A panel reviews only the borderline candidates (within 5 points of your cut-off). If there are none, it is skipped.
6. **You get a table**: score, go/no-go, why proceed, why not, and comments (interview pointers and a one-line background note). You can override any decision or re-run one candidate with a note.

CVs and results stay in a local folder (`~/JD-Builder/screen-runs/` or your Cowork workspace). Nothing is uploaded or committed, and you can delete the run at the end.

## What every JD looks like

The house layout: a navy top bar, the title, a five-cell summary panel, a two-column grid of labelled sections, the navy "Non-negotiable" box, six assessment cards, and the "Read twice" panel. See `plugins/hr-hiring/skills/jd-builder/brand/design-spec.md`.

## Repo map

`STRUCTURE.md` lists every folder. `ARCHITECTURE.md` explains how the agents and files fit together.
