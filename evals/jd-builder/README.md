# jd-builder evals

`run_checks.sh` is the pre-commit gate. It runs four checks:

1. Every gold example (`skills/jd-builder/examples/*.json`) and every fixture here passes `validate_jd.py`.
2. Each one renders to .docx.
3. Each rendered file passes `check_design.py`.
4. `extract_pdf_jd.py` reproduces the gold examples from the original PDFs byte for byte.

`fixtures/layout-non-engineering.json` is a layout test, not a real JD. It exercises the non-engineering variants: the TOOLS meta cell, OUR TOOLS, a people-manager track, the LEAD group, the TEAM level key, and "mistake" in the last Read-twice line.

Step 3 adds role briefs (engineering, marketing, sales, operations, data) with expected checks for the full research loop.
