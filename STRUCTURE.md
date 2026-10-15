# Structure

```
hiring/
├── README.md                       install + use, for HR
├── CLAUDE.md                       maintainer rules
├── ARCHITECTURE.md                 pipeline, guards, state, design choices
├── STRUCTURE.md                    this file
├── ROADMAP.md                      what's built, what's next
├── .claude-plugin/marketplace.json the marketplace that lists hr-hiring
├── plugins/hr-hiring/
│   ├── .claude-plugin/plugin.json
│   └── skills/jd-builder/          self-contained skill (agents see only this folder)
│       ├── SKILL.md                orchestrator: steps, gates, state, rules
│       ├── roles/                  one prompt per agent, each lists what it may read
│       │   ├── initializer.md      user input → brief + must-include list
│       │   ├── researcher.md       fresh web research, sourced
│       │   ├── challenger.md       VP of the function; scores /100, pass ≥ 95
│       │   ├── structurer.md       research → content file in the blueprint
│       │   ├── format-challenger.md blueprint fit, human writing, proofreading
│       │   ├── copy.md             humanizer + proofread
│       │   └── designer.md         renders and checks the branded .docx
│       ├── structure/
│       │   ├── skeleton.json       15 blocks: order, labels, headings, purpose, space limits
│       │   ├── jd.schema.json      shape of the content file
│       │   └── jd-structure.md     the blueprint explained
│       ├── brand/
│       │   ├── tokens.json         page, grid, colours, fonts, type scale
│       │   ├── design-spec.md      the same, explained
│       │   ├── fonts/              Archivo, Newsreader, IBM Plex Mono (OFL)
│       │   └── reference/          layout page images, words replaced by bars
│       ├── company/
│       │   ├── company.json        About us, equal opportunity, footer: the fixed text
│       │   └── company-facts.md    the only company facts a JD may state
│       ├── voice/
│       │   ├── voice-guide.md      plain, human writing rules
│       │   └── banned-phrases.txt
│       └── scripts/
│           ├── render_docx.py      content file → branded .docx (fonts embedded)
│           ├── validate_jd.py      blueprint, space, AI patterns, spelling, must-include
│           ├── check_design.py     reads the .docx back: fonts, colours, sizes, order
│           └── check_gate.py       recomputes research, challenge and format gates
└── evals/jd-builder/               maintainer tests; never read by the skill
    ├── run_checks.sh               run before every commit
    ├── make_fixtures.py            placeholder content at min size and at the word ceiling
    ├── writing_cases.json          sentences the validator must pass / fail / exempt
    ├── greek_reference.py          builds the word-free reference images
    ├── extract_pdf_jd.py           reads a PDF in the house layout
    └── fixtures/
        ├── layout-min.json, layout-max.json
        ├── originals/              the blueprint PDFs
        └── extracted/              their extraction, for the importer test only
```
