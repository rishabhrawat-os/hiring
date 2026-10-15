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
  if command -v soffice >/dev/null && command -v pdfinfo >/dev/null; then
    (cd "$OUT" && soffice --headless --convert-to pdf "$name.docx" >/dev/null 2>&1)
    pages=$(pdfinfo "$OUT/$name.pdf" | awk '/^Pages/ {print $2}')
    if [ "$pages" -gt 7 ]; then echo "FAIL $name renders to $pages pages (max 7)"; fail=1; continue; fi
    echo "ok   $name ($pages pages)"
  else
    echo "ok   $name (page count not checked: no LibreOffice)"
  fi
done
# The validator must accept plain English and reject AI patterns (writing_cases.json).
python3 - "$SKILL" "$HERE" "$OUT" <<'PY' || fail=1
import json, subprocess, sys, copy
skill, here, out = sys.argv[1:]
cases = json.load(open(f"{here}/writing_cases.json"))
base = json.load(open(f"{here}/fixtures/layout-min.json"))
def run(line, intake=None):
    d = copy.deepcopy(base); d["preferred"]["items"][0] = line
    json.dump(d, open(f"{out}/c.json", "w"), ensure_ascii=False)
    cmd = ["python3", f"{skill}/scripts/validate_jd.py", f"{out}/c.json"]
    if intake:
        json.dump(intake, open(f"{out}/i.json", "w")); cmd += ["--intake", f"{out}/i.json"]
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0
bad = 0
for line in cases["must_pass"]:
    if not run(line): print(f"FAIL false positive: {line}"); bad = 1
for line, why in cases["must_fail"]:
    if run(line): print(f"FAIL let through ({why}): {line}"); bad = 1
for line, term in cases["exempt_with_must_include"]:
    if not run(line, {"must_include": [term]}): print(f"FAIL user term blocked: {term}"); bad = 1
if not bad:
    n = len(cases["must_pass"]) + len(cases["must_fail"]) + len(cases["exempt_with_must_include"])
    print(f"ok   writing checks ({n} cases)")
sys.exit(bad)
PY
# Fixed text (company content, labels, headings) must also follow the writing rules.
python3 - "$SKILL" <<'PY' || fail=1
import json, re, sys
sys.path.insert(0, f"{sys.argv[1]}/scripts")
import validate_jd as v
co = json.load(open(f"{sys.argv[1]}/company/company.json"))
sk = json.load(open(f"{sys.argv[1]}/structure/skeleton.json"))
texts = co["about_us"]["paragraphs"] + [co["about_us"]["heading"], co["eeo"]["text"]]
for sec in sk["sections"].values():
    texts += [sec[k] for k in ("heading",) if k in sec] + list(sec.get("heading_options", {}))
    texts += list(sec.get("fixed", {}).values())
bad = 0
for t in texts:
    p = v.plain(t)
    for name, rx in v.AI_PATTERNS:
        if re.search(rx, p, re.I):
            print(f"FAIL fixed text has {name}: {p[:70]}"); bad = 1
if not bad:
    print("ok   fixed text follows the writing rules")
sys.exit(bad)
PY
for n in 1 2 3; do
  python3 "$HERE/extract_pdf_jd.py" "$HERE/fixtures/originals/onsurity-sde-$n-backend.pdf" "$OUT/x$n.json" >/dev/null 2>&1
  if cmp -s "$OUT/x$n.json" "$HERE/fixtures/extracted/sde-$n-backend.json"; then echo "ok   import sde-$n"; else echo "FAIL import sde-$n"; fail=1; fi
done
[ $fail -eq 0 ] && echo "ALL PASS" || exit 1
