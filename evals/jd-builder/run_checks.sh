#!/usr/bin/env bash
# Validate, render and design-check the placeholder fixtures, and check the PDF
# importer still reads the blueprint PDFs. Prints ALL PASS or exits non-zero.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$HERE/../../plugins/hr-hiring/skills/jd-builder"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
fail=0
python3 "$HERE/make_fixtures.py" >/dev/null
for f in "$HERE"/fixtures/layout-*.json; do
  name="$(basename "$f" .json)"
  if ! python3 "$SKILL/scripts/validate_jd.py" "$f" >"$OUT/v.txt"; then echo "FAIL validate $name"; grep FAIL "$OUT/v.txt"; fail=1; continue; fi
  python3 "$SKILL/scripts/render_docx.py" "$f" "$OUT/$name.docx" >/dev/null
  if ! python3 "$SKILL/scripts/check_design.py" "$OUT/$name.docx" >"$OUT/d.txt"; then echo "FAIL design $name"; grep FAIL "$OUT/d.txt"; fail=1; continue; fi
  echo "ok   $name"
done
# The validator must reject AI writing patterns.
python3 - "$SKILL" "$HERE/fixtures/layout-min.json" "$OUT" <<'PY' || fail=1
import json, subprocess, sys
skill, src, out = sys.argv[1:]
cases = {"em dash": "We ship fast — every week.", "contrast": "You own the outcome, not the task.",
         "not just": "This is not just a job.", "question": "Ready to build?", "banned": "Join a fast-paced environment."}
bad = 0
for name, line in cases.items():
    d = json.load(open(src)); d["preferred"]["items"][0] = line
    p = f"{out}/{name.replace(' ', '_')}.json"; json.dump(d, open(p, "w"), ensure_ascii=False)
    r = subprocess.run(["python3", f"{skill}/scripts/validate_jd.py", p], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"FAIL validator let through: {name}"); bad = 1
    else:
        print(f"ok   rejects {name}")
sys.exit(bad)
PY
for n in 1 2 3; do
  python3 "$SKILL/scripts/extract_pdf_jd.py" "$HERE/fixtures/originals/onsurity-sde-$n-backend.pdf" "$OUT/x$n.json" >/dev/null 2>&1
  if cmp -s "$OUT/x$n.json" "$HERE/fixtures/extracted/sde-$n-backend.json"; then echo "ok   import sde-$n"; else echo "FAIL import sde-$n"; fail=1; fi
done
[ $fail -eq 0 ] && echo "ALL PASS" || exit 1
