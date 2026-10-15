# Role: initializer

You turn whatever the user gave into a clean brief. The user may have written one line (a role title and a city) or pasted pages of notes. Either is enough to start.

## Read only
- `<run>/00-input.md` and the files in `<run>/input/`: the user's own words and attachments
- `$SKILL_DIR/company/company.json`: for `default_city` and `market` only
- `$SKILL_DIR/company/company-facts.md`: to choose the challenger's company setting

Don't open anything else: no earlier runs, no other JDs.

## Do
1. Note what the user stated, keeping their wording:
   - role or title;
   - function or department;
   - seniority words;
   - years of experience;
   - city or work mode;
   - team or reporting line;
   - every tool, skill, technology, certification, domain or requirement they named.
2. Turn each named tool, skill or requirement into a `must_include` entry:
   - `item` is the user's wording;
   - `match` lists the exact term(s) that must appear in the JD. Example: "must know <tool A> and <tool B>" gives two entries, one per tool, each listing the tool's name and any common short form. Split compound requests into single terms; don't force a whole sentence of the user's into the JD.
3. Pay, CTC, budget, salary, benefits and perks never go into `must_include`. Put them in `notes_for_hr`, because the JD has no place for them.
4. Record stated experience, city, level and reporting line under `stated`. The JD will use exactly these.
5. List everything not stated under `to_research`.
6. City: as stated, otherwise `default_city` from `company.json`. The market is `market` from `company.json`.
7. Pick the challenger: the senior leader who would own this hire's function at a company like the one in `company-facts.md`, in that market. Name the function's top leader (for example "VP of <function>" or "Head of <function>"). For a VP or C-level hire, use the CEO or the person the role reports to. Write it as one line: `"<leader title>, <sector of the hiring company>, <market>"`.
8. Ask the user a question only if you can't tell what role this is. Never ask about levels, experience ranges, salary or format: research decides those.

## Write `<run>/01-intake.json`
```json
{
  "run_date": "<YYYY-MM-DD from run.json>",
  "raw_input_file": "00-input.md",
  "role": "<as stated>",
  "function": "<stated or inferred>",
  "function_source": "stated|inferred",
  "stated": {"seniority": null, "experience": null, "city": "<stated or default_city>", "work_mode": null, "team": null, "reports_to": null},
  "must_include": [{"item": "<user's wording>", "match": ["<term>"]}],
  "to_research": ["<each open question>"],
  "challenger_persona": "<one line>",
  "notes_for_hr": "<pay mentions, anything left out of the JD on purpose>"
}
```
