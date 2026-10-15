# What goes where

Every Onsurity JD has the same 15 blocks in the same order, whatever the role, function or level. `skeleton.json` is the machine version of this page, and `jd.schema.json` is the shape of the content file. Limits are in words.

Legend: **Fixed** = printed word for word from `company/` or `skeleton.json`. **Slot** = written by the research → challenge → copy loop for this role.

| # | Block | Label (gutter) | Heading | Fixed | Slot | Limits |
|---|---|---|---|---|---|---|
| 1 | Header | — | — | "ONSURITY" in the eyebrow | function, city, title, lead, punchline | lead 25–45, punchline 8–22 |
| 2 | Meta panel | — | — | labels LEVEL, TRACK, EXPERIENCE, LOCATION | the 5 values; 5th label from STACK / TOOLS / FOCUS / MARKETS / REPORTS TO | exactly 5 cells |
| 3 | About us | ABOUT US | Healthcare benefits shouldn't be a luxury | everything | — | — |
| 4 | The role | THE ROLE | What this job actually is | label, heading | lead + 3–5 paragraphs | lead 15–30; paragraphs 35–60 |
| 5 | The level | THE LEVEL | What {level} means here | keys SCOPE, AMBIGUITY, INFLUENCE, JUDGEMENT, CONSEQUENCE | lead, the 6 row texts, 6th key (SLOPE / MULTIPLIER / TEAM) | rows 6–20 |
| 6 | Your work | YOUR WORK | What you'll do (entry) / What you'll own | — | 3–4 groups × 3–5 bullets | bullets 12–35 |
| 7 | The bar | THE BAR | How we expect you to operate (in the navy box) | eyebrow NON-NEGOTIABLE, the 5 trait titles | intro, 5 trait texts | traits 18–40 |
| 8 | AI | AI | How we expect you to use AI | opener "AI-assisted development/work is the default here, not a novelty." | rest of the lead, 4–5 bullets | bullets 12–25 |
| 9 | Minimum | MINIMUM | Minimum qualifications | — | optional note, 10–14 items with a **bold lead** | items 8–30 |
| 10 | Preferred | PREFERRED | Preferred qualifications | — | 6–9 items | items 3–25 |
| 11 | Toolkit | OUR STACK / OUR TOOLS | What you'd work with | Engineering rows from `company/engineering-stack.json` | optional note; rows for other functions | 4–8 rows |
| 12 | Assessment | THE BAR, TESTED | What we'll assess | "Six dimensions." opener | the rest of the lead, 6 cards | card text 14–26 |
| 13 | Not for you | READ TWICE | This role is probably not for you if | last item (hospital admission) | 3–5 items before it | items 15–32 |
| 14 | Equal opportunity | EQUAL OPPORTUNITY | — | everything | — | — |
| 15 | Footer | — | — | ONSURITY TECHNOLOGIES, ONSURITY.COM | LEVEL · SPEC · CITY | upper case |

## How each slot is written (patterns from the originals)

- **Title**: "{Role}, {specialisation}". For example "Software Development Engineer III, Java" or "Growth Marketing Manager, B2B".
- **Lead**: says what is different about this level, honestly. "A hard senior role, deliberately." "Your first engineering job, at a company small enough that…" The **punchline** then states the bar in one breath.
- **The role**: the lead says who we're hiring and why. The paragraphs then cover:
  1. what you own and what "own" includes;
  2. the main skill or tool, and where the boundary of the work sits;
  3. why the problems are hard here (insurance partners, regulators, hospitals, finance; a member relying on it);
  4. the deal or the stakes.
- **The level**: each row is 1–2 short sentences that say what this level carries on that axis. Keep the keys and their order; only the sixth changes:
  - SLOPE: rate of learning, for 0–2 years;
  - MULTIPLIER: makes others better, for mid and senior individual contributors;
  - TEAM: the team works without you, for people managers.
- **Your work**: group labels are phases of the work. Engineering uses DESIGN, BUILD, RUN, then GROW (entry) or MULTIPLY (mid+). Other functions pick 3 phases in the same spirit plus GROW, MULTIPLY or LEAD. Every bullet starts with a verb, names a concrete thing, and often ends with why it matters.
- **The bar**: the five trait titles never change, because they are company values. Their texts change with the level. The SDE I texts are about learning; the SDE III texts are about consequence.
- **AI**: the opener is fixed. The bullets cover daily use with named tools, owning everything you ship, where AI is weak in this domain, and building the workflow. Senior levels add a bullet on AI in the product.
- **Minimum**: the experience range comes first, and education (or equivalent evidence) and communication come last. Every tool or skill HR named appears here, in Preferred or in the Toolkit. The bold lead is the skill; the rest is the evidence ("services you built and ran, not scripts").
- **Preferred**: one line each, things that make a candidate stronger but aren't required. Domain exposure (payments, health insurance, regulated data) goes here.
- **Toolkit**: lower-case keys, comma lists. The optional note sets the expectation for the level ("You won't know all of this on day one").
- **Assessment**: exactly six cards, which mirror the interview loop. The lead starts with "Six dimensions." and names what the level is judged on.
- **Read twice**: honest reasons to self-select out, each written "You want X. Here, Y." The last item is fixed. It reads "bug" for engineering and "mistake" for other functions.

## Staying role-neutral

The frame is the same for every role; only the slots change.

- Nothing in the skeleton assumes engineering. The engineering-only defaults are the STACK meta cell, the OUR STACK rows and DESIGN/BUILD/RUN, and each has a stated alternative.
- Seniority is never implied by age or by years alone. The Level rows describe scope and judgement; EXPERIENCE is a range that HR confirms.
- Banned words (`voice/banned-phrases.txt`) include age-coded and gender-coded terms.
