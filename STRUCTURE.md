# Structure

```
hiring/
├── README.md                       install + use, for HR
├── CLAUDE.md                       maintainer rules
├── ARCHITECTURE.md                 pipeline, state, design choices
├── STRUCTURE.md                    this file
├── ROADMAP.md                      what's built, what's next
├── .claude-plugin/marketplace.json the marketplace that lists hr-hiring
├── plugins/hr-hiring/
│   ├── .claude-plugin/plugin.json
│   └── skills/jd-builder/          self-contained skill
│       ├── SKILL.md                orchestrator: commands, steps, gates, state
│       ├── roles/                  one prompt per agent role
│       │   └── designer.md         makes the .docx match the house look (step 1)
│       ├── structure/
│       │   ├── skeleton.json       15 blocks: order, labels, fixed text, limits
│       │   ├── jd.schema.json      shape of a jd.json
│       │   └── jd-structure.md     what goes where, and how each slot is written
│       ├── brand/
│       │   ├── tokens.json         page, grid, colours, fonts, type scale
│       │   ├── design-spec.md      the same, explained
│       │   ├── fonts/              Archivo, Newsreader, IBM Plex Mono (OFL)
│       │   └── reference/          page images of the 3 original JDs
│       ├── company/
│       │   ├── company.json        About us, equal opportunity, footer: fixed text
│       │   ├── company-facts.md    the only company facts agents may use
│       │   └── engineering-stack.json
│       ├── voice/
│       │   ├── voice-guide.md      tone, punctuation, British spelling, humanizer use
│       │   └── banned-phrases.txt
│       ├── examples/
│       │   ├── sde-{1,2,3}-backend.json   gold content, extracted from the originals
│       │   └── originals/          the published PDFs
│       └── scripts/
│           ├── render_docx.py      jd.json → branded .docx (fonts embedded)
│           ├── validate_jd.py      skeleton, limits, voice, must-include
│           ├── check_design.py     reads the .docx back: fonts, colours, sizes, order
│           └── extract_pdf_jd.py   Onsurity-layout PDF → jd.json
└── evals/jd-builder/
    ├── README.md
    ├── run_checks.sh               run before every commit
    └── fixtures/                   layout test content (not real JDs)
```
