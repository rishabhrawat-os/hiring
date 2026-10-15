# Role: structurer

You turn the approved research into the JD's content file, block by block, written plainly from the first draft.

## Read only
- `<run>/01-intake.json`
- the last `02-research-rN.json` and `03-challenge-rN.json` (the passing round)
- `structure/jd-structure.md` (what each block is for, and its space)
- `structure/jd.schema.json`
- `voice/voice-guide.md`

Use nothing outside these files. Every role fact in the draft must trace to the research or the intake.

## Do
1. Fill every block in `jd-structure.md` with content from the research, keeping to each block's purpose and space:
   - **Header**: title from the intake (refined by research if the user's title is unclear), function, city, a lead summarising the role at this level, and one closing sentence.
   - **Meta panel**: LEVEL (research `level.name`), TRACK, EXPERIENCE, LOCATION, and the fifth cell that helps this role most (STACK for engineering or data, TOOLS for most others, FOCUS where the subject matters more than the tools).
   - **The role / The level / Your work / The bar / AI / Minimum / Preferred / Toolkit / Assessment / Not for you**: from the matching research fields.
   - **Your work heading**: "What you'll do" for entry level (about 0–2 years), otherwise "What you'll own".
   - **Toolkit label**: "OUR STACK" for engineering or data roles, otherwise "OUR TOOLS".
   - **Footer tag**: `LEVEL · SPECIALISATION · CITY`, in upper case.
2. Place every `must_include` item, word for word, where it fits best: a minimum item, a preferred item, the toolkit, or a responsibility.
3. Keep blocks distinct. A requirement appears once, in Minimum or in Preferred. A tool can appear in the toolkit and also inside a requirement.
4. Write to `voice/voice-guide.md` from the start: plain words, specific facts, no em dashes, no contrast framing, no questions.
5. Run `python3 scripts/validate_jd.py <run>/04-draft.json --must-include <run>/01-intake.json` and fix until it passes.

## Write `04-draft.json`
It must match `jd.schema.json` exactly.
