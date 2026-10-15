# Writing rules for JD content

These rules apply to every word written into a JD. They come from plain-language writing practice, not from any earlier JD. `validate_jd.py` fails a JD that breaks the checkable ones.

## Write like a person explaining the job to a friend

- Use plain words: "use", not "leverage"; "help", not "empower"; "build", not "spearhead".
- Address the reader as "you" and the company as "we", in present or future tense.
- Most sentences are under 20 words, and each says one thing.
- Be specific. Name the actual tools, tasks, teams and outputs that the research found for this role. If a sentence would fit any company's JD, rewrite it or delete it.
- State facts directly. Write "You will run the monthly payroll close", not "You will play a key role in ensuring payroll excellence".
- Describe responsibilities as work someone does, starting with a verb: "Run", "Write", "Review", "Plan", "Fix".
- Each requirement says what is needed and what level of it, for example "3+ years running paid search campaigns with monthly budgets above ₹10 lakh". Avoid vague adjectives such as "strong", "excellent" or "solid" unless they are followed by what they mean.

## Never use (validate_jd.py checks these)

- **Em dashes (—)**, or a hyphen or en dash used as a pause between words. Use a full stop, a comma or brackets instead. An en dash is allowed only in number ranges (3–5 years).
- **Contrast framing**: "X, not Y", "not just X", "not only X but Y", "isn't X, it's Y", "rather than", or sentences starting with "Not". Say what the thing is, and stop.
- **Rhetorical questions and exclamation marks.**
- **Staged reveals**: "Here's the thing:", "The result:", "The catch:".
- **Words and phrases in `banned-phrases.txt`**: job-ad clichés, AI-sounding words, and exclusionary or age- or gender-coded terms.
- **"Objectives"**, "key result areas", or mission-statement language.

## Also avoid (the format challenger checks these)

- Lists of three used for rhythm ("fast, focused and fearless"). A list should have as many items as the facts require.
- One-line closing sentences that sum up a paragraph ("That's the job.").
- Inflated stakes ("world-class", "game-changing", "mission-critical").
- The same sentence shape repeated across bullets.
- Bold or italics for emphasis inside sentences. The layout's bold lead phrase in Minimum qualifications is the only bold.

## Spelling and numbers

- British/Indian English spelling: organise, optimise, centre, behaviour, licence (noun), programme (but "program" for software).
- Indian number style for money: ₹10 lakh, ₹2 crore.
- Number ranges use an en dash with no spaces: 3–5 years.
- "+" for open ranges: 6+ years.

## Facts

- Company facts come only from `company/company.json`.
- Role facts come only from the user's input and the research of this run.
- No salary, compensation, benefits or perks: the layout has no place for them.
- Nothing about age, gender, marital status, religion, caste, region or native language.

## Using /humanizer

Once the challenger signs off, run the `humanizer` skill (if installed) over every slot's text, telling it to keep facts, names, numbers and word limits unchanged. Then run `validate_jd.py` again. If humanizer isn't installed, the copy pass applies this page by hand.
