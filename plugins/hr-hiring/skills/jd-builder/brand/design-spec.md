# Onsurity JD design spec

Measured from the layout of the three Onsurity JD PDFs the user supplied as the blueprint (A4, exported from Chrome; kept in `evals/jd-builder/fixtures/originals/` for regression tests only). Only the layout, colours and type were taken; none of their wording. The values below live in `tokens.json`; `render_docx.py` and `check_design.py` both read them from there. This file explains the values; it doesn't override them.

## The look in one paragraph

A quiet editorial page. White paper, one navy accent, warm grey hairlines. A serif (Newsreader) for everything you read, a grotesque (Archivo) for everything you scan, and a monospace (IBM Plex Mono) for small upper-case labels. Every section sits on a two-column grid: a narrow gutter on the left holds a tracked mono label, and the content sits on the right. Two moments break the rhythm: the navy "Non-negotiable" box and the 3×2 grid of assessment cards. Nothing else is decorated. There are no icons, no images and no page numbers.

## Page and grid

| Item | Value |
|---|---|
| Paper | A4, 595.3 × 841.9 pt, white |
| Margins | top 42.7, bottom 42, left 39.7, right 39.6 pt |
| Content width | 516 pt |
| Label gutter | 116 pt (labels sit at x = 39.7) |
| Body column | 400 pt (text starts at x = 155.7) |
| Section divider | 0.7 pt hairline `#E7E7DE`, full width, about 16 pt above and 11 pt below |

## Colour

| Token | Hex | Used for |
|---|---|---|
| navy | `#113070` | top bar, "ONSURITY" in the eyebrow, the Non-negotiable box |
| ink | `#1A1F2E` | titles, headings, body text, bold lead-ins |
| slate | `#59637A` | lead paragraphs, section leads, card text, Read-twice items, equal-opportunity text |
| muted | `#8B93A5` | section labels, meta labels, stack keys, footer |
| link | `#2A55B5` | hyperlinks, The Level row keys |
| accent | `#4076E2` | Your Work group labels, bullet dashes |
| on_navy_text | `#BCCAEB` | body text and eyebrow inside the navy box |
| on_navy_heading | `#FFFFFF` | heading and trait titles inside the navy box |
| on_navy_rule | `#2C4C8F` | dividers inside the navy box |
| rule | `#E7E7DE` | all hairlines and table borders |
| rule_strong | `#CFCFC2` | eyebrow separators, Read-twice dashes |
| panel | `#FAFAF5` | meta panel and Read-twice panel fill |

## Type

| Fonts | Family in Word | File |
|---|---|---|
| Archivo Bold | Archivo (bold) | Archivo-700.ttf |
| Archivo SemiBold | Archivo SemiBold | Archivo-600.ttf |
| Newsreader | Newsreader (regular, italic) | Newsreader-400*.ttf, cut at optical size 13.2 to match the original line widths |
| Newsreader SemiBold | Newsreader SemiBold | Newsreader-600.ttf |
| IBM Plex Mono | IBM Plex Mono | IBMPlexMono-400.ttf |
| IBM Plex Mono Medium | IBM Plex Mono Medium | IBMPlexMono-500.ttf |

All fonts are embedded in every .docx, so nothing has to be installed. Licence: SIL OFL, `fonts/OFL.txt`.

| Role | Font | Size / line height | Tracking | Colour | Case |
|---|---|---|---|---|---|
| Top bar | rule | 3.7 pt thick | | navy | |
| Eyebrow (ONSURITY — FUNCTION — CITY) | Plex Mono Medium | 7.5 | +1.2 | navy, then muted; "——" in rule_strong | upper |
| Title | Archivo Bold | 25 / 27 | −0.75 | ink | as written; wraps at about 345 pt, usually onto 2 lines |
| Lead | Newsreader | 11 / 18 | | slate | max width 420 pt |
| Punchline (end of lead) | Archivo SemiBold | 10.5 | | ink | |
| Meta label | Plex Mono | 6.5 | +0.85 | muted | upper |
| Meta value | Archivo SemiBold | 9 / 13 | | ink | |
| Section label (gutter) | Plex Mono Medium | 7.5 | +1.05 | muted | upper |
| Section heading | Archivo SemiBold | 14 | | ink | sentence case |
| Section lead | Newsreader | 10.5 / 15 | | slate | |
| Body | Newsreader | 9.5 / 13.7, 7.5 pt between paragraphs | | ink | |
| Bold lead-in inside body | Archivo SemiBold | 9 | | ink | |
| Bold in About us | Newsreader SemiBold | 9.5 | | ink | |
| Level key | Plex Mono Medium | 8.2 | +0.8 | link | upper |
| Work group label | Plex Mono Medium | 8 | +1.0 | accent | upper |
| Bullet | "–" in Archivo SemiBold, accent; text indent 15 pt; 4.5 pt between bullets | | | | |
| Stack key / value | Plex Mono | 8.5 | | muted / ink | lower |
| Card title / text | Archivo SemiBold 9.5 / Newsreader 9, lh 13.8 | | | ink / slate | |
| Read-twice title / items | Archivo SemiBold 12 / Newsreader 9.5 | | | ink / slate; dash rule_strong | |
| Equal opportunity | Newsreader | 11.3 / 16 | | slate | |
| Footer | Plex Mono | 7.5 | +1.0 | muted | upper |

## Components, top to bottom

1. **Top bar**: navy, full width, 3.7 pt.
2. **Eyebrow**: `ONSURITY  ——  ENGINEERING  ——  BENGALURU`.
3. **Title**: the role title, in two lines at most.
4. **Lead + punchline**: one paragraph. The punchline is the last sentence(s), set in Archivo.
5. **Meta panel**: one row of five equal cells on a `panel` fill with a `rule` border. Each cell has a mono label over an Archivo value. The labels are LEVEL · TRACK · EXPERIENCE · LOCATION · STACK, and the fifth can be TOOLS, FOCUS, MARKETS or REPORTS TO.
6. **About us**: the only section without a divider above it.
7. **Labelled sections**: a divider, the gutter label, then a heading in the body column.
   - **The level**: six rows; a link-blue mono key with hairlines between rows.
   - **Your work**: 3–4 groups, each opened by a hairline and an accent mono label, then dash bullets.
   - **The bar**: a navy box with 18 pt padding. It holds the eyebrow "NON-NEGOTIABLE", a white heading, the intro, then five traits separated by `on_navy_rule` hairlines.
   - **Minimum**: two columns of dash bullets (215 / 185 pt). Each item opens with a bold lead phrase.
   - **Our stack / Our tools**: a mono key/value table with hairlines.
   - **The bar, tested**: a 3 × 2 grid of cards with a `rule` border and 12 pt padding.
   - **Read twice**: a `panel` box with a `rule` border; Archivo title; slate items with pale dashes.
   - **Equal opportunity**: one slate paragraph, slightly larger than the body.
8. **Footer**: a hairline, then `ONSURITY TECHNOLOGIES   LEVEL · SPEC · CITY   ONSURITY.COM`.

## Page flow

- Sections don't split across pages, except **Your work**, which may run long. A section that doesn't fit moves to the next page, as in the originals.
- Group labels stay with their first bullet; the footer stays with Equal opportunity.
- Expect 5–7 pages.

## What Word can't copy exactly

- **Box corners**: Word tables have square corners. The originals have about 4 pt rounded corners on the meta panel, the navy box, the cards and the Read-twice panel.
- **Bullet dashes**: these are a real "–" character, not the drawn 5 pt line in the originals. They read the same and stay editable.
- **Line breaks**: these can differ by a word here and there from the Chrome PDFs, because Word and Chrome justify text differently.
