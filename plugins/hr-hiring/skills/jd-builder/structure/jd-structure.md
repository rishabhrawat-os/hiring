# The JD blueprint

Every Onsurity JD uses the same 15 blocks in the same order, for any role, function or level. This page says what each block is for and how much space it has. It says nothing about what to write: the content comes from the user's input and the research of that run. `skeleton.json` is the machine version, and `jd.schema.json` is the content file's shape.

**Fixed text** is limited to:
- company content, from `company/company.json`: About us, Equal opportunity, the footer ends;
- the section labels and headings listed below, which are the names of the blocks.

| # | Block | Gutter label | Heading | Component | Holds | Space |
|---|---|---|---|---|---|---|
| 1 | Header | — | — | top bar, eyebrow, title, lead | function, city, title, lead, then one factual sentence in bold sans naming the main outcome the role is accountable for | title 2–8 words; lead 25–45; outcome sentence 6–22 |
| 2 | Meta panel | — | — | 5-cell panel | LEVEL, TRACK, EXPERIENCE, LOCATION + one of STACK / TOOLS / FOCUS / MARKETS / REPORTS TO | 1–6 words per cell |
| 3 | About us | ABOUT US | (from company.json) | prose | company content | fixed |
| 4 | The role | THE ROLE | What this job actually is | opening line + paragraphs | what the job is, day to day, who it works with, why it matters | opening 12–30; 3–5 paragraphs of 30–65 |
| 5 | The level | THE LEVEL | What {level} means here | opening line + 6 key/value rows | the seniority expected, as six dimensions chosen by research | 6 rows, 6–22 words each; keys one upper-case word |
| 6 | Your work | YOUR WORK | What you'll do (entry) / What you'll own | labelled bullet groups | responsibilities in 3–4 groups | 3–5 bullets of 8–35 words per group; labels 1–2 upper-case words |
| 7 | The bar | THE BAR | How we expect you to operate (in the navy box, under "NON-NEGOTIABLE") | box with intro + 5 items | five behaviours the role can't succeed without | intro 8–25; titles 2–6 words; texts 15–40 |
| 8 | AI | AI | How we expect you to use AI | opening line + bullets | how AI is used in this role today | opening 10–30; 4–5 bullets of 8–28 |
| 9 | Minimum | MINIMUM | Minimum qualifications | 2-column bullets | must-haves; each item opens with a short **bold phrase** | 8–14 items of 6–30 words; optional note ≤40 |
| 10 | Preferred | PREFERRED | Preferred qualifications | bullets | nice-to-haves | 4–9 items of 3–25 |
| 11 | Toolkit | OUR STACK (engineering/data) or OUR TOOLS | What you'd work with | key/value rows | tools by category | 2–8 rows; optional note ≤35 |
| 12 | Assessment | THE BAR, TESTED | What we'll assess | opening line + 6 cards | what the hiring process will assess | opening 8–25; 6 cards, titles 1–4 words, texts 12–28 |
| 13 | Not for you | READ TWICE | This role is probably not for you if | panel bullets | honest reasons to self-select out; each completes the heading's sentence | 4–6 items of 8–32 |
| 14 | Equal opportunity | EQUAL OPPORTUNITY | — | prose | company content | fixed |
| 15 | Footer | — | — | one line | LEVEL · SPECIALISATION · CITY between the fixed ends | upper case |

## Rules that come from the layout

- The Level always has six rows and the assessment always has six cards, because the components are a six-row table and a 3×2 grid.
- The Bar always has five items: that is the size of the navy box.
- Minimum qualifications open each item with a bold phrase, because the two-column list is built to be scanned.
- No block may be left empty or padded to fill space. If research can't fill a block with something specific to this role, the challenger raises it.
- There is no salary, benefits or perks block, so a JD never states them.
- The whole JD stays under `limits.total_words` (1,700), which keeps it to about 7 pages.
