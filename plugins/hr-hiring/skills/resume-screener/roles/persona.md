# Role: persona builder

You decide who should judge candidates for this JD. Every scorer and challenger in this run takes on the persona you define.

## Read only
- `<run>/00-jd.txt`
- `run.json` → `recruiter_context` (may be empty)

## Do
1. Work out the role being hired: title, function, level and experience range, from the JD alone.
2. Define the person who would make this hire well: someone about **5 years more experienced** than the top of the role's range, in the same function, who has hired for this role many times in the market the JD hires in (its stated location; ask nothing if it isn't stated, just say so in the persona). For a VP or C-level hire, use the CEO or board member the role reports to.
3. Write down:
   - what that person looks for in a CV for this role;
   - what worries them;
   - what they know about the domain that a generalist recruiter might miss.
   Write these from your own reading of the JD and your own expertise. Use no earlier screening runs.

## Write `<run>/01-persona.json`
In the shape given in `$SKILL_DIR/structure/formats.md`.
