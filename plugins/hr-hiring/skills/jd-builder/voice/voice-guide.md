# How an Onsurity JD sounds

Taken from the three SDE JDs. The copy pass follows this page, and `validate_jd.py` enforces the parts that can be checked mechanically.

## The voice

- **Second person, present tense, with contractions.** "You'll own a domain." "We're small enough that…" Not "The candidate will…".
- **Honest about difficulty.** "A hard senior role, deliberately." "We hold this bar and we don't lower it to fill the seat." Say what the job costs, not only what it offers.
- **Concrete nouns from our world**: claims, wallet, subscriptions, provider network, payments, a member in a hospital visit, insurance partners, regulators, month-end. Use the role's own equivalents for non-tech roles: pipeline, a broker's quote, a payroll cycle, a renewal.
- **Consequences, not adjectives.** "Missing them in production costs a member." Not "high-impact role".
- **Short sentences, then one longer one.** Most sentences are under 20 words. A two-word sentence is fine ("The deal is simple.").
- **Verb-first bullets.** Own, Write, Debug, Carry, Set, Review, Say no. Each bullet names a real thing and, often, why it matters.
- **Evidence over claims in qualifications.** "Production Node.js — services you built and ran, not scripts." The bold lead names the skill; the rest says what proof looks like.

## House punctuation and spelling

- **British English**: centre, judgement, defence, organise, optimise, programme (but "program" for code), specialise, memorised.
- **Spaced em dash for asides**: " — ". At most about 2 per 100 words; the originals run at about 1.6.
- **En dash in ranges**: 0–2 years, 3–5 years. Use "6+ years" for open ranges.
- **Curly apostrophes are fine; straight are fine. Be consistent within one JD.**
- **"·" (middle dot)** separates items in the meta panel and the footer.
- **No exclamation marks, no emoji, no ALL-CAPS words** outside labels.

## Contrasts: allowed, rationed

The originals use "not X, Y" contrasts on purpose ("Not years, not lines of code.", "fix the cause, not the symptom"). They are part of the voice. Keep to **one per section at most**, and only where both halves are concrete. A generic contrast ("not just a job, a mission") is slop: cut it.

## Never write

- Anything in `banned-phrases.txt` (job-ad clichés, AI tells, exclusionary words).
- Company claims that aren't in `company/`. Don't invent funding, customer counts, awards or perks.
- Salary, benefits or perks unless HR supplied them.
- Age, gender, "native speaker", "young team", "culture fit", or "digital native".
- Requirements that can't be tested in the interview loop on the Assessment cards.

## Using /humanizer

If the `humanizer` skill is installed, run it over each slot's text once the challenger has signed off. Give it this page as the style to keep: the house em dashes and rationed contrasts stay; generic contrasts, inflated words, stacked adjectives and one-line closers go. After humanizer, run `validate_jd.py` again, because humanizer must not push a slot outside its word limits.
