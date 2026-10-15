# jd-builder evals (maintainers only)

Nothing in this folder is read by the skill.

`run_checks.sh` is the pre-commit gate. It:
1. Builds placeholder content (`make_fixtures.py`): every block at its minimum size, and every block filled up to the total word ceiling. The text is neutral filler, so it tests layout without suggesting any wording.
2. Validates, renders and design-checks both fixtures, and (with LibreOffice) checks the ceiling fixture renders to 7 pages or fewer.
3. Runs `writing_cases.json` through the validator:
   - plain English that must pass;
   - AI patterns, salary and US spelling that must fail;
   - user-named terms that must be exempt.
4. Checks the fixed text (company content, labels, headings) follows the same writing rules.
5. Checks `extract_pdf_jd.py` still reads the blueprint PDFs (`fixtures/originals/`) the same way (`fixtures/extracted/`).

Other tools:
- `greek_reference.py`: rebuilds the skill's `brand/reference/layout-page-*.png` from a blueprint PDF, with every word replaced by a bar.
- `extract_pdf_jd.py`: reads a PDF in the house layout into the content shape. Needs `pdfplumber`.
