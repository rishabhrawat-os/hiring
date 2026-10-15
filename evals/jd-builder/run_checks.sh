#!/usr/bin/env bash
# Validate, render and design-check every example and fixture. Prints ALL PASS or exits non-zero.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$HERE/../../plugins/hr-hiring/skills/jd-builder"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
fail=0
for f in "$SKILL"/examples/*.json "$HERE"/fixtures/*.json; do
  name="$(basename "$f" .json)"
  python3 "$SKILL/scripts/validate_jd.py" "$f" >/dev/null || { echo "FAIL validate $name"; python3 "$SKILL/scripts/validate_jd.py" "$f" | grep FAIL; fail=1; continue; }
  python3 "$SKILL/scripts/render_docx.py" "$f" "$OUT/$name.docx" >/dev/null
  python3 "$SKILL/scripts/check_design.py" "$OUT/$name.docx" >/dev/null || { echo "FAIL design $name"; python3 "$SKILL/scripts/check_design.py" "$OUT/$name.docx" | grep FAIL; fail=1; continue; }
  echo "ok   $name"
done
# Extraction must reproduce the gold examples exactly.
for n in 1 2 3; do
  python3 "$SKILL/scripts/extract_pdf_jd.py" "$SKILL/examples/originals/onsurity-sde-$n-backend.pdf" "$OUT/x$n.json" >/dev/null 2>&1
  cmp -s "$OUT/x$n.json" "$SKILL/examples/sde-$n-backend.json" && echo "ok   extract sde-$n" || { echo "FAIL extract sde-$n"; fail=1; }
done
[ $fail -eq 0 ] && echo "ALL PASS" || exit 1
